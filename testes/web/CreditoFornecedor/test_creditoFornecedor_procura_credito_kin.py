import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from classes.rotinas import ContasPagar, CreditoFornecedor
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.rotinas.CreditoFornecedor import CreditoFornecedor

@pytest.mark.dockerCreditoFornecedor
def test_creditoFornecedor_procura_credito(init):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']

    valores = CreditoFornecedor.Credito()

    try:
        FuncoesUteis.goToPage(init, CreditoFornecedor.url)

        CreditoFornecedor.procuraCreditoFornecedor(init)

    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine=f"{CreditoFornecedor.rotina} - test_creditoFornecedor_procura_credito", error_details=str(e))
        
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
            routine=f"{CreditoFornecedor.rotina} - test_creditoFornecedor_procura_credito",
            error_details=''
        )

        Log_manager.insert_logs_for_execution()

        browser.quit()