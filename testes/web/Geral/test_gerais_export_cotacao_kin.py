import time
from classes.rotinas.PortalCotacoes import PortalCotacoes
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.GerarDados import GeradorDados  
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components
from classes.rotinas.ContasReceber import ContaReceber
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException


def test_ExportarCotacao(init):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']

    filters = {
        "P1_DATA_INICIO": "05/01/2025",
        "P1_DATA_FIM" : "05/01/2025"
    }
    
    try:
        time.sleep(2)

        Components.btnClick(init, "#cotacoesFinalizadas_tab")

        FuncoesUteis.guaranteeShowHideFilter(init, "#P1_DATA_INICIO", 1)
        FuncoesUteis.setFilters(init, filters)

        Components.btnClick(init, "#btnFiltrar")

        Components.btnClick(init, ".fa.fa-edit")

        PortalCotacoes.exportCotacao(init)
        time.sleep(3)


    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
        screenshot_path = screenshots
        if screenshot_path:
            success = browser.save_screenshot(screenshot_path)
            if success:
                Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="Cotações", application_type=env_application_type, error_details=str(e))
            else:
                Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="Cotações", application_type=env_application_type, error_details=str(e))

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
            routine="Cotações",
            error_details=''
        )

    Log_manager.insert_logs_for_execution()

    browser.quit()