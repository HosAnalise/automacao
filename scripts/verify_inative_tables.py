import os
import sys
from sqlalchemy import create_engine, text, inspect, exc,func
from sqlalchemy.engine import Engine
import traceback


# --- CONFIGURAÇÃO CENTRAL DE BANCOS DE DADOS ---
# Adicionar um novo banco de dados aqui é tudo que você precisa fazer para estender o script.
DB_DIALECTS = {
    'firebird': {
        'url': "firebird+fdb://{user}:{password}@{host}:{port}/{database}",
        'activity_query': """
            SELECT TRIM(R.RDB$RELATION_NAME)
            FROM RDB$RELATIONS R
            LEFT JOIN MON$IO_STATS S ON R.RDB$RELATION_ID = S.MON$STAT_ID
            WHERE R.RDB$SYSTEM_FLAG = 0 AND R.RDB$VIEW_BLR IS NULL
              AND (S.MON$PAGE_READS > 0 OR S.MON$PAGE_WRITES > 0);
        """,
        'system_schemas': ['RDB$', 'SEC$']
    },
    'postgresql': {
        'url': "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
        'activity_query': """
            SELECT schemaname || '.' || relname AS full_table_name
            FROM pg_stat_user_tables
            WHERE seq_scan > 0 OR idx_scan > 0 OR n_tup_ins > 0 OR
                  n_tup_upd > 0 OR n_tup_del > 0;
        """,
        'system_schemas': ('pg_catalog', 'information_schema')
    },
    'oracle': {
        'url': "oracle+cx_oracle://{user}:{password}@{host}:{port}/?service_name={database}",
        'activity_query': """
            SELECT owner || '.' || object_name AS full_table_name
            FROM ALL_OBJECTS
            WHERE object_type = 'TABLE'
            AND owner NOT IN ('SYS', 'SYSTEM')
            AND (last_ddl_time > SYSDATE - 30 OR created > SYSDATE - 30); -- Exemplo: Atividade nos últimos 30 dias
        """,
        'system_schemas': ('SYS', 'SYSTEM')
    }
}


def get_table_row_counts_firebird(engine, system_tables_to_ignore: list):
    """
    Obtém a contagem de registros para cada tabela do banco de dados.

    Args:
        engine: A engine do SQLAlchemy.
        system_tables_to_ignore: Uma lista de prefixos de tabelas de sistema a serem ignoradas.

    Returns:
        Um dicionário com {nome_da_tabela: contagem_de_registros}.
    """
    print("Iniciando contagem de registros... (Pode ser lento em bancos grandes)")
    all_counts = {}
    inspector = inspect(engine)

    # Para Firebird (e outros bancos sem schemas), obtemos as tabelas diretamente
    # A chamada get_table_names() sem argumentos funciona para este caso.
    for table_name in inspector.get_table_names():
        # Verifica se a tabela deve ser ignorada (tabelas de sistema)
        if any(table_name.upper().startswith(prefix) for prefix in system_tables_to_ignore):
            print(f"   - Ignorando tabela do sistema: {table_name}")
            continue

        try:
            # Usando func.count() é a forma mais portável do SQLAlchemy
            # para contar registros.
            query = text(f'SELECT COUNT(*) FROM "{table_name.upper().replace('"', '')}"')
            with engine.connect() as connection:
                result = connection.execute(query).scalar_one()
                all_counts[table_name] = result

        except Exception as e:
            print(f"   - [AVISO] Não foi possível contar registros da tabela '{table_name}'. Erro: {e}")
            all_counts[table_name] = 'ERRO'

    print("Contagem de registros finalizada.")
    return all_counts

def get_table_row_counts(engine: Engine, system_schemas: tuple) -> dict[str, int]:
    """
    Conta os registros de todas as tabelas de usuário.

    Args:
        engine: A instância do SQLAlchemy Engine para se conectar ao banco.
        system_schemas: Uma tupla de prefixos de esquema de sistema a serem ignorados.

    Returns:
        Um dicionário mapeando nome da tabela para contagem de linhas.
    """
    print("\nIniciando contagem de registros... (Pode ser lento em bancos grandes)")
    counts = {}
    inspector = inspect(engine)
    
    for schema in inspector.get_schema_names():
        if schema.startswith(system_schemas):
            continue
        for table_name in inspector.get_table_names(schema=schema):
            # Usamos aspas para lidar com nomes de tabelas e esquemas que podem ser palavras-chave
            full_table_name = f'"{schema}"."{table_name}"' if schema else f'"{table_name}"'
            query = text(f'SELECT COUNT(*) FROM {full_table_name}')
            
            try:
                with engine.connect() as connection:
                    result = connection.execute(query).scalar_one()
                    # Usamos o nome simples da tabela como chave para consistência
                    counts[table_name.strip()] = result
            except exc.SQLAlchemyError as e:
                print(f"  - [AVISO] Não foi possível contar '{table_name}': {e.orig}")
                counts[table_name.strip()] = -1  # Marcar como erro
                traceback.print_exc()  # Isso vai imprimir o histórico completo do erro
                print("--------------------------")
    
    print("Contagem finalizada.")
    return counts

def get_active_tables(engine: Engine, query: str) -> set[str]:
    """
    Executa uma consulta específica do dialeto para obter uma lista de tabelas ativas.

    Args:
        engine: A instância do SQLAlchemy Engine.
        query: A string de consulta SQL para obter nomes de tabelas ativas.

    Returns:
        Um conjunto (set) com os nomes das tabelas ativas.
    """
    print("\nVerificando estatísticas de atividade do banco de dados...")
    with engine.connect() as connection:
        result = connection.execute(text(query))
        # Usamos um set para buscas rápidas e para remover duplicatas automaticamente
        active_tables = {row[0].strip() for row in result}
    print("Verificação de atividade finalizada.")
    return active_tables

def analyze_tables(row_counts: dict[str, int], active_tables: set[str]) -> dict:
    """
    Analisa os dados coletados e classifica as tabelas.

    Args:
        row_counts: Dicionário de contagem de linhas por tabela.
        active_tables: Conjunto de tabelas com atividade registrada.

    Returns:
        Um dicionário contendo as listas de tabelas classificadas.
    """
    analysis = {
        "candidates_for_removal": [],
        "investigate_immediately": [],
        "impossible_to_count": []
    }
    all_user_tables = row_counts.keys()

    for table in all_user_tables:
        
        if isinstance(row_counts[table], str):
            analysis["impossible_to_count"].append(
                f"{table} (Motivo: Erro ao contar registros)"
            )
            
        count = row_counts[table]
        # Normalizamos o nome da tabela para a verificação (ex: remover aspas)
        is_active = table in active_tables
        
        
        if count == 0 and not is_active:
            analysis["candidates_for_removal"].append(
                f"{table} (Motivo: Vazia e sem atividade de leitura/escrita registrada)"
            )
        elif count > 0 and not is_active:
            analysis["candidates_for_removal"].append(
                f"{table} (Motivo: Contém {count} registros, mas sem atividade recente)"
            )
        elif count == 0 and is_active:
            analysis["investigate_immediately"].append(
                f"{table} (Motivo: Está vazia, mas a aplicação AINDA tenta ler/escrever nela!)"
            )
    return analysis

def print_report(analysis: dict):
    """
    Imprime o relatório final da análise de forma organizada.

    Args:
        analysis: O dicionário de resultados da função analyze_tables.
    """
    print("\n--- Veredito Final ---")
    
    candidates = analysis["candidates_for_removal"]
    investigate = analysis["investigate_immediately"]
    impossible_to_count = analysis["impossible_to_count"]

    if impossible_to_count:
        print("\n⚠️ Atenção - Tabelas com Erro ao Contar Registros:")
        for item in impossible_to_count:
            print(f"  - {item}")

    if candidates:
        print("\n🚨 RISCO MÉDIO/ALTO - Candidatas à Remoção/Arquivamento:")
        for candidate in candidates:
            print(f"  - {candidate}")
    
    if investigate:
        print("\n🔥🔥🔥 ALERTA VERMELHO - Investigar Imediatamente (NÃO REMOVER):")
        for item in investigate:
            print(f"  - {item}")
            
    if not candidates and not investigate and not impossible_to_count:
        print("\n✨ Nenhuma candidata óbvia para remoção ou investigação crítica foi encontrada.")
        
    print("\nLembre-se: Sempre valide com a equipe e verifique o código-fonte antes de qualquer ação de `DROP TABLE`!")

def main(dialect_name: str):
    """
    Função principal que orquestra a análise híbrida de tabelas.

    Args:
        dialect_name: A chave do dialeto a ser usado (ex: 'firebird', 'postgresql').
    """
    print("🐍 Python Like a Pro - Detetive Híbrido de Tabelas 🕵️‍♂️")
    print("-" * 65)

    if dialect_name.lower() not in DB_DIALECTS:
        print(f"[ERRO] Dialeto '{dialect_name}' não configurado. Opções válidas: {list(DB_DIALECTS.keys())}")
        sys.exit(1)

    config = DB_DIALECTS[dialect_name]
    
    # Carrega credenciais do ambiente
    try:
        db_user = os.environ[f'{dialect_name.upper()}_USER']
        db_password = os.environ[f'{dialect_name.upper()}_PASSWORD']
        db_host = os.environ[f'{dialect_name.upper()}_HOST']
        db_port = os.environ[f'{dialect_name.upper()}_PORT']
        db_name = os.environ[f'{dialect_name.upper()}_DATABASE']
    except KeyError as e:
        print(f"[ERRO] Variável de ambiente não definida: {e}. Certifique-se de configurar todas as credenciais.")
        traceback.print_exc()  # Isso vai imprimir o histórico completo do erro
        print("--------------------------")
        sys.exit(1)

    db_url = config['url'].format(
        user=db_user, password=db_password, host=db_host, port=db_port, database=db_name
    )

    try:
        engine = create_engine(db_url)
        # Testa a conexão
        with engine.connect() as connection:
            print(f"Conexão com '{dialect_name}' bem-sucedida!")


        # Passo 1: Obter contagem de registros

        row_counts= get_table_row_counts_firebird(engine, config['system_schemas']) if dialect_name.lower() == 'firebird' else get_table_row_counts(engine, config['system_schemas'])
   
        
        # Passo 2: Obter tabelas com atividade registrada
        active_tables = get_active_tables(engine, config['activity_query'])

        # Passo 3: Analisar os resultados
        final_analysis = analyze_tables(row_counts, active_tables)

        # Passo 4: Apresentar o relatório
        print_report(final_analysis)

    except exc.SQLAlchemyError as e:
        print(f"\n[ERRO FATAL] Ocorreu um erro ao conectar ou consultar o banco de dados.")
        print(f"Detalhes: {e}")
        traceback.print_exc()  # Isso vai imprimir o histórico completo do erro
        print("--------------------------")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERRO INESPERADO] Ocorreu um erro não previsto: {e}")
        traceback.print_exc()  # Isso vai imprimir o histórico completo do erro
        print("--------------------------")
        sys.exit(1)


if __name__ == "__main__":
    # Para usar, simplesmente troque o nome do dialeto aqui!
    # Ex: main(dialect_name='postgresql')
            main(dialect_name='firebird')


