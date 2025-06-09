import time
import pytest
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.rotinas.ExtratoContas import ExtratoContas
import pytest

@pytest.mark.dockerExtratoContas
def test_extratoContas_gerarRelatorio(init):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']
    getEnv = env_vars

    try:
        FuncoesUteis.goToPage(init, "exibir-extrato-das-contas")
        FuncoesUteis.showHideFilter(init,ExtratoContas.filterSelector)
        ExtratoContas.gerarRelatorio(init,"PDF")


    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine=f"{ExtratoContas.rotina} - test_extratoContas_gerarRelatorio", error_details=str(e))
        
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
            routine=f"{ExtratoContas.rotina} - test_extratoContas_gerarRelatorio",
            error_details=''
        )

    Log_manager.insert_logs_for_execution("ExtratoContas")

    browser.quit()