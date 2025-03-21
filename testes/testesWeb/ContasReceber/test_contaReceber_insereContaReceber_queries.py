from datetime import datetime,timedelta
import random
import time



def test_contaReceber_insereConta_queries(init):
       
    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
    getEnv = env_vars
    env_application_type = getEnv.get("WEB")
    start = time.time()
    
    def obter_valor_aleatorio(lista):
        if lista:
            return random.choice(lista)
        return None  # ou algum valor padrão, caso necessário


    
    queries = {
    "queryModelodocumentoFiscal":   """
                                            SELECT 
                                                MODELO.DOCUMENTO_FISCAL_MODELO_ID
                                            FROM 
                                                ERP.DOCUMENTO_FISCAL_MODELO MODELO
                                    """,    

    "queryContaId": """
                        SELECT CONTA.CONTA_ID  
                        FROM ERP.CONTA
                        JOIN ERP.CONTA_ESPECIFICACAO ON CONTA.CONTA_ID = CONTA_ESPECIFICACAO.CONTA_ID
                        LEFT JOIN ERP.LOJA ON LOJA.LOJA_ID = CONTA_ESPECIFICACAO.LOJA_ID
                        WHERE CONTA_ESPECIFICACAO.GRUPO_LOJA_ID = 1501
                            AND CONTA.TIPO_CONTA_ID IN (1, 2)
                            AND (CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IN (1) OR CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IS NULL)
                            AND (CONTA.CONTA_ID IN (0) OR CONTA_ESPECIFICACAO.STATUS IN (1))
                    """,
    
    "queryFornecedorId": """
                            SELECT PESSOA_ID 
                            FROM ERP.PESSOA 
                            WHERE GRUPO_LOJA_ID = 1501
                                AND EXISTS (
                                    SELECT 1 
                                    FROM ERP.PESSOA_CADASTRO 
                                    WHERE PESSOA_CADASTRO.PESSOA_ID = PESSOA.PESSOA_ID 
                                        AND PESSOA_CADASTRO.TIPO_CADASTRO_PESSOA_ID = 2
                                )
                                AND STATUS = 1
                        """,

    "queryCategoriaFinanceira": """
        SELECT CF.CATEGORIA_FINANCEIRA_ID  
        FROM ERP.CATEGORIA_FINANCEIRA CF
        LEFT JOIN ERP.CATEGORIA_FINANCEIRA_ESPECIFICACAO CFE ON CF.CATEGORIA_FINANCEIRA_ID = CFE.CATEGORIA_FINANCEIRA_ID
        LEFT JOIN ERP.CATEGORIA_FINANCEIRA CF_PAI ON CFE.CATEGORIA_FINANCEIRA_PAI_ID = CF_PAI.CATEGORIA_FINANCEIRA_ID
        WHERE CF.CLASSIFICACAO_CATEGORIA_FINANCEIRA_ID = 1
            AND CFE.CATEGORIA_FINANCEIRA_PAI_ID IS NOT NULL
            AND CFE.GRUPO_LOJA_ID = 1501
            AND (CFE.CATEGORIA_FINANCEIRA_ID IN (0) OR CFE.STATUS = 1)
    """,


    "queryFormaPagamento": """
        SELECT FORMA_PAGAMENTO_ID FROM ERP.FORMA_PAGAMENTO
        WHERE
            status = 1
            and (grupo_loja_id = 1501 or grupo_loja_id is null)
            AND VISIVEL = 1        
    """,


    "queryTipoChave": """
        SELECT TIPO_CHAVE_PIX_ID 
        FROM ERP.TIPO_CHAVE_PIX
    """,

    "queryBanco": """
        SELECT BANCO_ID FROM ERP.BANCO
    """,
    "queryCentroCusto": """
        SELECT 
            CC.CENTRO_CUSTO_ID  
        FROM 
            ERP.CENTRO_CUSTO CC
        LEFT JOIN 
            ERP.CENTRO_CUSTO_ESPECIFICACAO CCE ON CC.CENTRO_CUSTO_ID = CCE.CENTRO_CUSTO_ID
        LEFT JOIN   
            ERP.CENTRO_CUSTO CC_PAI ON CCE.CENTRO_CUSTO_PAI_ID = CC_PAI.CENTRO_CUSTO_ID
        WHERE 
            CCE.GRUPO_LOJA_ID = 1501
            AND CCE.CENTRO_CUSTO_PAI_ID IS NOT NULL 
            AND (
                CCE.CENTRO_CUSTO_ID IN (0)
                OR CCE.STATUS IN (1)
            )

    """,

    "queryCobradorId": """
        SELECT 
            PESSOA.PESSOA_ID
        FROM 
            ERP.PESSOA
        LEFT JOIN 
            ERP.PESSOA_CADASTRO ON PESSOA_CADASTRO.PESSOA_ID = PESSOA.PESSOA_ID
        WHERE
            PESSOA.GRUPO_LOJA_ID = 1501
            AND PESSOA.STATUS = 1
            AND (
                PESSOA_CADASTRO.TIPO_CADASTRO_PESSOA_ID = 5
                OR 
                (PESSOA_CADASTRO.TIPO_CADASTRO_PESSOA_ID = 2
                AND EXISTS (
                    SELECT 1
                    FROM ERP.PESSOA_FORNECEDOR
                    WHERE PESSOA_FORNECEDOR.PESSOA_ID = PESSOA.PESSOA_ID
                    AND NVL(PESSOA_FORNECEDOR.COBRADOR, 0) = 1
                ))
            )

    """,



    "queryEmpresa": """
            SELECT LOJA_ID FROM ERP.LOJA WHERE GRUPO_LOJA_ID = 1501
        """,
    
    "queryCliente" : """
        SELECT
            PESSOA.PESSOA_ID       
        FROM 
            ERP.PESSOA
        WHERE 
            GRUPO_LOJA_ID = 1501
            AND STATUS = 1
    """
    }

      
    


    def executar_query(cursor, query):
        cursor.execute(query)
        queryValues = [row[0] for row in cursor.fetchmany(20)]
        return queryValues if queryValues else []
    


    try:
        with oracle_db_connection.cursor() as cursor:
            results = {}
            randomValues = {}  

            for key,query in queries.items():
                results[key] = executar_query(cursor,query) 

            for key, result in results.items():
                randomValues[f"Random_{key}"] = obter_valor_aleatorio(result)                
           
            return randomValues


  

    except Exception as e:
        Log_manager.add_log(application_type =env_application_type,level= "Error", message = f"Erro na excução das queries ", routine="ContaPagar", error_details =f"{e}" )

    finally:
        endTime = time.time()
        executionTime = endTime - start

        minutos = int(executionTime // 60)
        segundos = int(executionTime % 60)
        milissegundos = int((executionTime % 1) * 1000)

        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Tempo de execução das queries: {minutos} min {segundos} s {milissegundos} ms",
            routine="ContaPagar",
            error_details=''
        )