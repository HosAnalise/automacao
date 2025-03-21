from datetime import datetime,timedelta
import random
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.GerarDados import GeradorDados  
from scripts.ApexUtil import Apex
from scripts.FuncoesUteis import FuncoesUteis

@pytest.mark.parametrize("browser, login", [("chrome", "teste")], indirect=True)
def test_extratoContas_gerarRelatorio(init,query):
       
    randomQueries =  query
    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

    getEnv = env_vars
    env_application_type = getEnv.get("WEB")
    
    random_value = round(random.uniform(1, 999999), 2)
    randomValue = FuncoesUteis.formatBrCurrency(random_value)
    randomNumber = GeradorDados.randomNumberDinamic(0,3)
    randomDay = GeradorDados.randomNumberDinamic(1,30)

    today = datetime.today()
    randomDay = GeradorDados.randomNumberDinamic(0, 30)
    randomDate = today + timedelta(days=randomDay)
    finalDate = randomDate.strftime("%d/%m/%Y")
    todaystr = today.strftime("%d/%m/%Y")




    try:
        defaultContent = browser.current_window_handle
        Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Jenela atual encontrada : {defaultContent}",
                        routine="ExtratoDeContas",
                        error_details=''
                    )



        btnGerarRelatorio = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B131918532644441921")))
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão btnGerarRelatorio encontrado ",
            routine="ExtratoDeContas",
            error_details=''
        )
        btnGerarRelatorio.click()
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão btnGerarRelatorio clicado ",
            routine="ExtratoDeContas",
            error_details=''
        )

        try:
            has_frame = WebDriverWait(browser,30).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"[title='Gerar Relatório Extrato de Contas']")))
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Trocando para o iframe: Gerar Relatório Extrato de Contas",
                routine="ExtratoDeContas",
                error_details=''
            )
        except(TimeoutException,Exception,NoSuchElementException) as e :
            has_frame = None
            Log_manager.add_log(
                application_type=env_application_type,
                level="ERROR",
                message="Troca para o iframe: Gerar Relatório Extrato de Contas. Falhou",
                routine="ExtratoDeContas",
                error_details=str(e)
            )

        if has_frame:

            btnGerarPdf = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".t-Cards-item.gerarPDF")))
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Botão btnGerarPdf encontrado ",
                routine="ExtratoDeContas",
                error_details=''
            )
            btnGerarPdf.click()
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Botão btnGerarPdf clicado ",
                routine="ExtratoDeContas",
                error_details=''
            )

            all_windows = browser.window_handles
            Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Jenelas encontradas : {all_windows}",
                        routine="ExtratoDeContas",
                        error_details=''
                    )


            for window in all_windows:
                if window != defaultContent:
                    browser.switch_to.window(window)
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Troca pra jenela {window}",
                        routine="ExtratoDeContas",
                        error_details=''
                    )
                    break
                else:
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="ERROR",
                        message=f"Troca pra jenela {window} mal sucedida",
                        routine="ExtratoDeContas",
                        error_details=''
                    )        

    except TimeoutException as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro: Tempo limite excedido ao acessar a página",
            routine="ExtratoDeContas",
            error_details=str(e)
        )
        screenshot_path = screenshots
        
        # Verifica se o screenshot foi tirado corretamente
        if screenshot_path:
            sucess  = browser.save_screenshot(screenshot_path)
            if sucess:            
                Log_manager.add_log(
                    level="INFO", 
                    message=f"Screenshot salvo em: {screenshot_path}", 
                    routine="Login",application_type='WEB', 
                    error_details=str(e)
            )
        else:
            Log_manager.add_log(
                level="ERROR", 
                message="Falha ao salvar screenshot", 
                routine="Login",application_type='WEB', 
                error_details=str(e)
            )

    except NoSuchElementException as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro: Elemento não encontrado na página",
            routine="ExtratoDeContas",
            error_details=str(e)
        )
        screenshot_path = screenshots
        
        # Verifica se o screenshot foi tirado corretamente
        if screenshot_path:
            sucess  = browser.save_screenshot(screenshot_path)
            if sucess:  
                Log_manager.add_log(
                    level="INFO", 
                    message=f"Screenshot salvo em: {screenshot_path}", 
                    routine="Login",application_type='WEB', 
                    error_details=str(e)
            )
        else:
            Log_manager.add_log(
                level="ERROR", 
                message="Falha ao salvar screenshot", 
                routine="Login",application_type='WEB', 
                error_details=str(e)
            )

    except Exception as e:  # Captura qualquer outro erro inesperado
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro desconhecido ao acessar a página",
            routine="ExtratoDeContas",
            error_details=str(e)
        )
        screenshot_path = screenshots
        
        # Verifica se o screenshot foi tirado corretamente
        if screenshot_path:
            sucess  = browser.save_screenshot(screenshot_path)
            if sucess:  
                Log_manager.add_log(
                    level="INFO", 
                    message=f"Screenshot salvo em: {screenshot_path}", 
                    routine="Login",application_type='WEB', 
                    error_details=str(e)
            )
        else:
            Log_manager.add_log(
                level="ERROR", 
                message="Falha ao salvar screenshot", 
                routine="Login",application_type='WEB', 
                error_details=str(e)
            )



    
         

