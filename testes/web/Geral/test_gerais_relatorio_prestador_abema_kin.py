import time
from classes.rotinas import Abema
from classes.rotinas.Abema import AbemaRelatorioPrestador as ARP
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
from time import sleep


def test_abema_gerarRelatorioPrestador(init):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']
    getEnv = env_vars

    filters = {
        "P56_COMPETENCIA_FOLHA_1" : "01/2025",
        "P56_COMPETENCIA_FOLHA_FIM_1" : "01/2025",
        "prestadorempresa_saved_reports" : "82523067444671710"
    }
    url = getEnv.get("URL_ERP")
    print(f"{url}relatório-prestador")

    try:
        FuncoesUteis.goToPage(init, "relatório-prestador")

        FuncoesUteis.guaranteeShowHideFilter(init, ARP.filterSelector, 1)

        FuncoesUteis.setFilters(init, filters)

        Components.btnClick(init, "#B82287259769324517")

        Components.btnClick(init, "#botaorelatorio")

        print(f"{FuncoesUteis.getURL(init)}")



    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine=f"{ARP.rotina} - test_abema_gerarRelatorioPrestador", error_details=str(e))
        
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
            routine=f"{ARP.rotina} - test_abema_gerarRelatorioPrestador",
            error_details=''
        )

    Log_manager.insert_logs_for_execution()

    browser.quit()