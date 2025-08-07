import time
from matplotlib.pylab import f
import pytest
from classes.rotinas.MetasPorRegiao import MetasPorRegiao
from classes.utils.Components import Components
from classes.utils.FuncoesUteis import FuncoesUteis
from faker import Faker
fake = Faker(locale='pt_BR')

# --- Payloads para Testes de Segurança ---
XSS_PAYLOAD_BASIC = "<script>alert('XSS')</script>"
XSS_PAYLOAD_IMG = "<img src=x onerror=alert('XSS')>"
SQL_INJECTION_PAYLOAD_SIMPLE = "' OR '1'='1"
valor_metas_lojas = "20"  # Exemplo de valor para o campo de lojas

@pytest.mark.parametrize("meta_data, devePassar, valor_metas_lojas, cenario", [
    # ==== CENÁRIOS DE SUCESSO ====
    (
        MetasPorRegiao.Metas(
            P311_DESCRICAO="Meta Teste Válida (Ativa)",
            P311_SELETOR_LOJA=["2381", "3625"],
            P311_STATUS="1" # 1 = Ativo
        ), True, valor_metas_lojas, "Criação de meta com status ativo e lojas selecionadas - Criação com sucesso"
    ),
        (
            MetasPorRegiao.Metas(
            P311_DESCRICAO="Meta Teste Válida (Inativa)",
            P311_SELETOR_LOJA=["3605"],
            P311_STATUS="0" # 0 = Inativo
        ), True,  valor_metas_lojas, "Criação de meta com status inativo - Criação com sucesso"
    ),
    (
        MetasPorRegiao.Metas(
            P311_DESCRICAO="Meta com descrição longa para testar o limite de caracteres que é permitido pelo sistema e que funciona corretamente.",
            P311_SELETOR_LOJA=["2381"],
            P311_STATUS="1"
        ), True, valor_metas_lojas, "Criação de meta com descrição longa - Criação com sucesso"
    ),
    (
        MetasPorRegiao.Metas(
            P311_DESCRICAO="Meta com Acentos e Caracteres Especiais: (R$), %, @, é &, ç, ñ,ô, ü",
            P311_SELETOR_LOJA=["2381", "3625", "3605"],
            P311_STATUS="1"
        ), True, valor_metas_lojas, "Criação de meta com caracteres especiais - Criação com sucesso"
    ),
    (
        MetasPorRegiao.Metas(
            P311_DESCRICAO="Meta para todas as lojas",
            P311_SELETOR_LOJA=[""], # Nenhuma loja específica, aplica-se a todas
            P311_STATUS="1"
        ), False, valor_metas_lojas, "Criação de meta para todas as lojas - Criação com sucesso"
    ),

    # ==== CENÁRIOS DE FALHA (VALIDAÇÃO DE CAMPOS) ====
    (
        MetasPorRegiao.Metas(
            P311_DESCRICAO="", # Descrição vazia
            P311_SELETOR_LOJA=["2381"],
            P311_STATUS="1"
        ), False, valor_metas_lojas, "Tentativa de criar meta com descrição vazia - Deve falhar"
    ),
    (
        MetasPorRegiao.Metas(
            P311_DESCRICAO="Meta sem status",
            P311_SELETOR_LOJA=["2381"],
            P311_STATUS="" # Status vazio
        ), True, valor_metas_lojas, "Tentativa de criar meta sem status - Deve Passar (mas não é recomendado)"
    ),
    (
        MetasPorRegiao.Metas(
            P311_DESCRICAO="Meta com status inválido",
            P311_SELETOR_LOJA=["2381"],
            P311_STATUS="3" # Status inválido
        ), False, valor_metas_lojas, "Tentativa de criar meta com status inválido - Deve falhar"
    ),
     
    (
        MetasPorRegiao.Metas(
            P311_DESCRICAO="Meta com dados nulos",
            P311_SELETOR_LOJA=[""],
            P311_STATUS=""
        ), False, valor_metas_lojas, "Tentativa de criar meta com dados nulos - Deve falhar"
    ),


    # ==== CENÁRIOS DE SEGURANÇA ====
    (
        MetasPorRegiao.Metas(
            P311_DESCRICAO=XSS_PAYLOAD_BASIC, # Tentativa de XSS
            P311_SELETOR_LOJA=["2381"],
            P311_STATUS="1"
        ), False, valor_metas_lojas, "Tentativa de Cross-Site Scripting (XSS) no campo de descrição - Deve falhar"
    ),
    (
        MetasPorRegiao.Metas(
            P311_DESCRICAO=XSS_PAYLOAD_IMG, # Tentativa de XSS com tag de imagem
            P311_SELETOR_LOJA=["2381"],
            P311_STATUS="1"
        ), False, valor_metas_lojas, "Tentativa de Cross-Site Scripting (XSS) com imagem - Deve falhar"
    ),
    (
        MetasPorRegiao.Metas(
            P311_DESCRICAO=SQL_INJECTION_PAYLOAD_SIMPLE, # Tentativa de SQL Injection
            P311_SELETOR_LOJA=["2381"],
            P311_STATUS="1"
        ), False, valor_metas_lojas, "Tentativa de SQL Injection no campo de descrição - Deve falhar"
    ),

    # ==== CENÁRIOS DE CASOS EXTREMOS E CARGA ====
    (
        MetasPorRegiao.Metas(
            P311_DESCRICAO=fake.text(max_nb_chars=1000), # Descrição muito longa
            P311_SELETOR_LOJA=["2381"],
            P311_STATUS="1"
        ), False, valor_metas_lojas, "Tentativa de criar meta com descrição excedendo o limite máximo de caracteres - Deve falhar"
    ),
    (
        MetasPorRegiao.Metas(
            P311_DESCRICAO="Meta de Teste com muitas lojas",
            P311_SELETOR_LOJA=[str(i) for i in range(1000)], # Lista de lojas muito grande
            P311_STATUS="1"
        ), True, valor_metas_lojas, "Criação de meta com um número muito grande de lojas - Teste de carga"
    ),
    (
        MetasPorRegiao.Metas(
            P311_DESCRICAO="   Meta com espaços   ", # Espaços em branco no início e no fim
            P311_SELETOR_LOJA=["2381"],
            P311_STATUS="1"
        ), True, valor_metas_lojas, "Criação de meta com espaços em branco que devem ser tratados (trim) - Deve passar"
    ),
])
@pytest.mark.dockerMetasPorRegiao # Marcador corrigido
def test_criar_e_editar_meta_por_regiao(init, meta_data, devePassar, valor_metas_lojas, cenario):
    """
    Testa o ciclo completo de criação e edição de 'Metas por Região'.
    - Para cenários de sucesso, cria a meta, a localiza, edita e valida o resultado.
    - Para cenários de falha, valida que a criação é bloqueada e uma mensagem de erro é exibida.
    """
    start_time = time.time()
    _, _, Log_manager, _, env_vars, _, selenium_exceptions, error_logger = init
    env_application_type = env_vars['APPLICATION_TYPE']
    rotina_nome = f"{MetasPorRegiao.rotina} - {cenario}"
    
    Log_manager.add_log(level="INFO", application_type=env_application_type, message=f"Iniciando teste: '{cenario}'", routine=rotina_nome)

    try:
        # --- PASSO 1: TENTATIVA DE CRIAÇÃO (COMUM A TODOS OS CENÁRIOS) ---
        FuncoesUteis.goToPage(init=init, url=MetasPorRegiao.url)
        MetasPorRegiao.criarMeta(init=init)

        # A função criarMetaComissao retorna False em caso de erro de preenchimento
        resultado_criacao = MetasPorRegiao.criarMetaComissao(init=init, meta=meta_data)

        MetasPorRegiao.selecionarLojasRegioes(init=init)

        valorMetasLojas = MetasPorRegiao.insereValorMetaLojasRegioes(init=init, value_to_insert= valor_metas_lojas)

        MetasPorRegiao.cadastrarMeta(init=init)

        has_alert = Components.has_alert(init=init)

        # --- PASSO 2: VERIFICAÇÃO CONDICIONAL ---
        if devePassar:
            # Para cenários de sucesso, esperamos que a criação tenha funcionado
            assert resultado_criacao , "Erro inesperado: A etapa de criação da meta falhou."
            assert not has_alert, "Alerta inesperado após a criação da meta."
            assert valorMetasLojas, "Falha ao inserir valores nas lojas."

            Log_manager.add_log(level="INFO",application_type=env_application_type, message="Meta criada com sucesso.", routine=rotina_nome)

        else:
            # Para cenários de falha, esperamos que a criação tenha falhado
            assert resultado_criacao is False, "A etapa de criação da meta deveria ter falhado, mas passou."
            assert not valorMetasLojas, "Falha ao inserir valores nas lojas, mas deveria ter falhado."
            assert has_alert,  "Alerta esperado não foi exibido."
            Log_manager.add_log(level="INFO",application_type=env_application_type, message="Meta não criada como esperado. Prosseguindo para validação de erro.", routine=rotina_nome)
    
    except selenium_exceptions as e:
        logs = error_logger(exc=e, block=rotina_nome)
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=f"{logs.time} - {logs.message}", routine=rotina_nome, error_details=f"{logs.error} - {logs.type_error} - {logs.function_error} - {logs.file} - {logs.row}")
        pytest.fail(f"O teste falhou devido a uma exceção do Selenium no cenário '{cenario}': {e}")
    
    finally:
        # Este bloco é executado mesmo se o teste falhar, ideal para registrar o tempo
        end_time = time.time()
        execution_time = end_time - start_time
        minutos, segundos = divmod(execution_time, 60)

        Log_manager.add_log(level="INFO", application_type=env_application_type, message=f"Finalizando teste: '{cenario}'", routine=rotina_nome)

        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Tempo de execução: {int(minutos)}m {segundos:.2f}s",
            routine=rotina_nome
        )
        # Recomendo fortemente mover o browser.quit() para a fixture 'init'
        
        Log_manager.insert_logs_for_execution(logName=f"{MetasPorRegiao.rotina} - test_criar_e_editar_meta_por_regiao")



