import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from classes.rotinas import ContasPagar, CreditoFornecedor
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.rotinas.CreditoFornecedor import CreditoFornecedor

@pytest.mark.parametrize("infoCredito, devePassar", [
    (
        CreditoFornecedor.Credito(
            P169_VALOR='114,88',
            P169_OBSERVACAO='esse vai funfa',
            P169_DATA='26/05/2025',
            P169_NUMERO_NOTA_SAIDA='2288445'
        ), True
    )
    ,
    (
        CreditoFornecedor.Credito(

        ), True
    )
    ,
    (
        CreditoFornecedor.Credito(
            P169_VALOR='ahga',
            P169_OBSERVACAO='teste legalzao 123!!',
            P169_DATA='datazona',
            P169_NUMERO_NOTA_SAIDA='num!eroslocouca',
            P169_NUMERO_NOTA_ENTRADA= 'testeb@omdia'
        ), False
    ),
])
@pytest.mark.dockerCreditoFornecedor
def test_creditoFornecedor_insere_credito(init, infoCredito, devePassar):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']

    try:
        FuncoesUteis.goToPage(init, CreditoFornecedor.url)
        
        FuncoesUteis.showHideFilter(init, CreditoFornecedor.filterSelector)

        funcionou = CreditoFornecedor.insereCreditoFornecedor(init, infoCredito)

        if devePassar:
            if funcionou is False:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="WARNING",
                    message="Teste devia retornar um objeto, porém retornou False.",
                    routine=f"{CreditoFornecedor.rotina} - test_creditoFornecedor_insere_credito",
                    error_details=""
                )
            assert funcionou is not False

        else:
            if funcionou is not False:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="WARNING",
                    message="Teste devia retornar False, porém retornou objeto.",
                    routine=f"{CreditoFornecedor.rotina} - test_creditoFornecedor_insere_credito",
                    error_details=""
                )
            assert funcionou is False

    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine=f"{CreditoFornecedor.rotina} - test_creditoFornecedor_insere_credito", error_details=str(e))
        
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
            routine=f"{CreditoFornecedor.rotina} - test_creditoFornecedor_insere_credito",
            error_details=''
        )

        Log_manager.insert_logs_for_execution()

        browser.quit()