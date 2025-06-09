import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from classes.rotinas import ContasPagar
from classes.rotinas.ConciliacaoBancaria import ConciliacaoBancaria
from classes.rotinas.ContasReceber import ContaReceber
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components

@pytest.mark.dockerConciliacaoBancaria
def test_conciliacaoBancaria_insere_lancamento_contaExistente(init):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']

    queries = {
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

    queryContaReceber = FuncoesUteis.getQueryResults(init, queries)

    seletoresQuery = {
        "P85_CONTA_ID" : queryContaReceber["Query_queryContaId"],
        "P85_CATEGORIA_FINANCEIRA" : queryContaReceber["Query_queryCategoriaFinanceira"],
        "P85_LOJA" : queryContaReceber["Query_queryEmpresa"],
        "P85_PESSOA_CLIENTE_ID" : queryContaReceber["Query_queryCliente"]
    }

    seletoresAleatorio = {
        "P85_DATA_VENCIMENTO" : "date",
        "P85_VALOR" : (float, 35, 60),
        "P85_NUMERO_PEDIDO" : (str, 10, 20),
        "P85_NUMERO_DOCUMENTO" : (str, 10, 20) 
    }

    try:
        FuncoesUteis.goToPage(init, ContaReceber.url)
        time.sleep(2)
        FuncoesUteis.guaranteeShowHideFilter(init, "#P84_TIPO_PERIODO", False)

        campos = FuncoesUteis.geraValoresRandom(init, seletoresAleatorio)

        dictConta = campos | seletoresQuery

        ContaReceber.insereContaReceber(init, '', dictConta)

        dictPesquisa = FuncoesUteis.recuperaValores(init, seletoresAleatorio)
        
        ContaReceber.salvaContaReceber(init)

        FuncoesUteis.goToPage(init, ConciliacaoBancaria.url)
        time.sleep(1)

        ConciliacaoBancaria.clickOpcoesLancamento(init)

        filtros = {
            "P157_DATA_INICIAL": dictPesquisa["P85_DATA_VENCIMENTO"],
            "P157_DATA_FINAL": dictPesquisa["P85_DATA_VENCIMENTO"],
            "P157_NUMERO_DOCUMENTO": dictPesquisa["P85_NUMERO_DOCUMENTO"],
            "P157_NUMERO_PEDIDO": dictPesquisa["P85_NUMERO_PEDIDO"],
            "P157_VALOR_MIN": dictPesquisa["P85_VALOR"],
            "P157_VALOR_MAX": dictPesquisa["P85_VALOR"]
        }

        ConciliacaoBancaria.incluiRecebimentoContaExistente(init, filtros)

    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine=f"{ConciliacaoBancaria.rotina} - test_conciliacaoBancaria_insere_lancamento_contaExistente", error_details=str(e))

    finally:
        endTime = time.time()
        executionTime = endTime - starTime

        minutos = int(executionTime // 60)
        segundos = int(executionTime % 60)
        milissegundos = int((executionTime % 1) * 1000)

        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Tempo de execução do teste: {minutos} min {segundos} s {milissegundos} ms",
            routine=f"{ConciliacaoBancaria.rotina} - test_conciliacaoBancaria_insere_lancamento_contaExistente",
            error_details=''
        )

        Log_manager.insert_logs_for_execution()

        browser.quit()