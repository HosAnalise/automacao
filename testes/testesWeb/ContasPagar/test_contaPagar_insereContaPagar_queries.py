from datetime import datetime,timedelta
import random
import time
import lorem
import re
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains


def test_contaPagar_insereConta_queries(init):
       
    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
    getEnv = env_vars
    env_application_type = getEnv.get("WEB")
    
    


    try:
        cursor = oracle_db_connection.cursor()    

        queryContaId = """
            SELECT CONTA.CONTA_ID  
            FROM ERP.CONTA
            JOIN ERP.CONTA_ESPECIFICACAO ON CONTA.CONTA_ID = CONTA_ESPECIFICACAO.CONTA_ID
            LEFT JOIN ERP.LOJA ON LOJA.LOJA_ID = CONTA_ESPECIFICACAO.LOJA_ID
            WHERE CONTA_ESPECIFICACAO.GRUPO_LOJA_ID = 1501
                AND CONTA.TIPO_CONTA_ID IN (1, 2)
                AND (CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IN (1) OR CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IS NULL)
                AND (CONTA.CONTA_ID IN (0) OR CONTA_ESPECIFICACAO.STATUS IN (1))
        """
        
        queryFornecedorId = """
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
        """

        queryCategoriaFinanceira = """
            SELECT CF.CATEGORIA_FINANCEIRA_ID  
            FROM ERP.CATEGORIA_FINANCEIRA CF
            LEFT JOIN ERP.CATEGORIA_FINANCEIRA_ESPECIFICACAO CFE ON CF.CATEGORIA_FINANCEIRA_ID = CFE.CATEGORIA_FINANCEIRA_ID
            LEFT JOIN ERP.CATEGORIA_FINANCEIRA CF_PAI ON CFE.CATEGORIA_FINANCEIRA_PAI_ID = CF_PAI.CATEGORIA_FINANCEIRA_ID
            WHERE CF.CLASSIFICACAO_CATEGORIA_FINANCEIRA_ID = 1
                AND CFE.CATEGORIA_FINANCEIRA_PAI_ID IS NOT NULL
                AND CFE.GRUPO_LOJA_ID = 1501
                AND (CFE.CATEGORIA_FINANCEIRA_ID IN (0) OR CFE.STATUS = 1)
        """

        queryEmpresa = """
            SELECT LOJA_ID FROM ERP.LOJA WHERE GRUPO_LOJA_ID = 1501
        """

        queryFormaPagamento = """
            SELECT FORMA_PAGAMENTO_ID FROM ERP.FORMA_PAGAMENTO
            WHERE
                status = 1
                and (grupo_loja_id = 1501 or grupo_loja_id is null)
                AND VISIVEL = 1        
        """


        queryTipoChave = """
            SELECT TIPO_CHAVE_PIX_ID 
            FROM ERP.TIPO_CHAVE_PIX
        """

        queryBanco = """
            SELECT BANCO_ID FROM ERP.BANCO
        """
        queryCentroCusto = """
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

            """
        queryModelodocumentoFiscal = """
            SELECT 
                 MODELO.DOCUMENTO_FISCAL_MODELO_ID
            FROM 
                ERP.DOCUMENTO_FISCAL_MODELO MODELO
        """


        def executar_query(cursor, query):
            cursor.execute(query)
            queryValues = [row[0] for row in cursor.fetchall()]
            return queryValues if queryValues else []
                       

        # Executando as queries e armazenando os resultados
       
        resultContaId = executar_query(cursor, queryContaId)

       
        resultFornecedorId = executar_query(cursor, queryFornecedorId)

       
        resultCategoriaFinanceira = executar_query(cursor, queryCategoriaFinanceira)

       
        resultEmpresaId = executar_query(cursor, queryEmpresa)

       
        resultFormaPagamentoId = executar_query(cursor, queryFormaPagamento)

       
        resultTipoChaveId = executar_query(cursor, queryTipoChave)

       
        resultBancoId = executar_query(cursor, queryBanco)

       
        resultCentroCustoId = executar_query(cursor, queryCentroCusto)

       
        resultModeloDocumentoFiscalId = executar_query(cursor, queryModelodocumentoFiscal)

   

        # Pegando valores aleatórios das listas retornadas
        

        if resultContaId :
            randomContaId = random.choice(resultContaId)

        if resultFornecedorId :
            randomFornecedorId = random.choice(resultFornecedorId)


        if resultCategoriaFinanceira :
            randomCategoriaFinanceiraId = random.choice(resultCategoriaFinanceira)


        if resultEmpresaId :
            randomEmpresaId = random.choice(resultEmpresaId)


        if resultFormaPagamentoId :
            randomPagamentoId = random.choice(resultFormaPagamentoId)
    

        if resultTipoChaveId :
            randomChavePixId = random.choice(resultTipoChaveId) 


        if resultBancoId :
            randomBancoId = random.choice(resultBancoId)  
 

        if resultCentroCustoId :
            randomCentroCustoId = random.choice(resultCentroCustoId)      

        if resultModeloDocumentoFiscalId :
            randomModeloDocumentoID = random.choice(resultModeloDocumentoFiscalId)
                   

        cursor.close()

        return randomContaId,randomFornecedorId,randomCategoriaFinanceiraId,randomEmpresaId,randomPagamentoId,randomChavePixId,randomBancoId,randomCentroCustoId,randomModeloDocumentoID

    except Exception as e:
        Log_manager.add_log(application_type =env_application_type,level= "Error", message = f"Erro na excução das queries ", routine="ContaPagar", error_details =f"{e}" )
        