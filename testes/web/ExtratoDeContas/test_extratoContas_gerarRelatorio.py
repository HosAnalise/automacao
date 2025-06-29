import time
import pytest
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.rotinas.ExtratoContas import ExtratoContas

@pytest.mark.docker
def test_gerarRelatorio(init):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']
    getEnv = env_vars

  

    try:
        FuncoesUteis.goToPage(init, "exibir-extrato-das-contas")
        FuncoesUteis.showHideFilter(init,ExtratoContas.filterSelector)
        ExtratoContas.gerarRelatorio(init,"PDF")


        


    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
        screenshot_path = screenshots
        if screenshot_path:
            success = browser.save_screenshot(screenshot_path)
            if success:
                Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="ExtratoContas", application_type=env_application_type, error_details=str(e))
            else:
                Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="ExtratoContas", application_type=env_application_type, error_details=str(e))

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
            routine="ExtratoContas",
            error_details=''
        )

    Log_manager.insert_logs_for_execution("ExtratoContas")

    browser.quit()