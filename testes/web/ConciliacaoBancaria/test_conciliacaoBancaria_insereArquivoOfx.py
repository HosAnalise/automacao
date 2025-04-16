import time
from classes.rotinas.ConciliacaoBancaria import ConciliacaoBancaria
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components


def test_contaPagar_insereArquivoOfx(init):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']


    try:
        FuncoesUteis.goToPage(init,ConciliacaoBancaria.url)
        Components.has_spin(init)
        FuncoesUteis.showHideFilter(init,ConciliacaoBancaria.filterSelector,False)
        ConciliacaoBancaria.insereConciliacao(init)
        Components.has_alert(init)
                    
    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
        screenshot_path = screenshots
        if screenshot_path:
            success = browser.save_screenshot(screenshot_path)
            if success:
                Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="ConciliacaoBancaria", application_type=env_application_type, error_details=str(e))
            else:
                Log_manager.add_log(level="INFO", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))

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
            routine="ContaPagar",
            error_details=''
        )

        Log_manager.insert_logs_for_execution("ConciliacaoBancaria")

        browser.quit()



       