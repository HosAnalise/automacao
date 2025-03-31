import time
from classes.rotinas.ContasPagar import ContasPagar
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



def test_FiltroLateralAbreEZeroRegistros(init):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']

    for i in range(2):

        if i == 0: #contas a pagar
            rotina = "Contas a Pagar"
            page = ContasPagar.url
            seletor = "P46_TIPO_PERIODO"

        else:
            rotina = "Contas a Receber"
            page = ContaReceber.url
            seletor = "P84_TIPO_PERIODO"

        try:
            FuncoesUteis.goToPage(init, page)

            try:

                WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"#{seletor}")))

                Log_manager.add_log(
                    level="INFO",
                    message=f"O Filtro Lateral da Página {rotina} Esta Vindo Aberto.",
                    routine=rotina,
                    error_details=""
                )
            except:
                Log_manager.add_log(
                    level="INFO",
                    message=f"O Filtro Lateral da Página {rotina} Esta Vindo Fechado.",
                    routine=rotina,
                    error_details=""
                )

            try:
                WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#.fa.fa-edit")))

                Log_manager.add_log(
                    level="INFO",
                    message=f"A Página {rotina} Não Está Trazendo Nenhum Registro Automaticamente.",
                    routine=rotina,
                    error_details=""
                )
            except:
                Log_manager.add_log(
                    level="INFO",
                    message=f"A Página {rotina} Está Trazendo Registros Automaticamente.",
                    routine=rotina,
                    error_details=""
                )



        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="ContaPagar", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))

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

    Log_manager.insert_logs_for_execution()

    browser.quit()