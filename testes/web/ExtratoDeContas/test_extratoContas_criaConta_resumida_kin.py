from tabnanny import check
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.rotinas.ExtratoContas import ExtratoContas
from classes.utils.Components import Components
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.rotinas.ContasPagar import ContasPagar
from classes.rotinas.ContasReceber import ContaReceber, ContasReceber


@pytest.mark.parametrize("conta, devePassar", [
    (
        ContaReceber.ContaResumida(
            P199_VALOR='66.59'
        ),
        True
    )
    ,
    (
        ContasPagar.ContaResumida(
            P194_NUMERO_DOCUMENTO='doc123321'
        ),
        True
    )
])
@pytest.mark.dockerExtratoContas
def test_extratoContas_criaConta_resumida(init, conta, devePassar):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']

    try:
        FuncoesUteis.goToPage(init, ExtratoContas.url)
        
        FuncoesUteis.showHideFilter(init, ExtratoContas.filterSelector)

        funcionou = ExtratoContas.novaContaResumida(init, conta)

        if devePassar:
            if funcionou is False:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="WARNING",
                    message="Teste devia retornar um objeto, porém retornou False.",
                    routine=f"{ExtratoContas.rotina} - test_extratoContas_criaConta_resumida",
                    error_details=""
                )
            assert funcionou is not False

        else:
            if funcionou is not False:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="WARNING",
                    message="Teste devia retornar False, porém retornou objeto.",
                    routine=ExtratoContas.rotina,
                    error_details=""
                )
            assert funcionou is False

    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine=f"{ExtratoContas.rotina} - test_extratoContas_criaConta_resumida", error_details=str(e))

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
            routine=f"{ExtratoContas.rotina} - test_extratoContas_criaConta_resumida",
            error_details=''
        )

        Log_manager.insert_logs_for_execution()

        browser.quit()