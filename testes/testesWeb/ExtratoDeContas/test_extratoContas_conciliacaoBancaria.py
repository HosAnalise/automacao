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
def test_extratoContas_conciliacaoBancaria(init,query):
       
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
        btnConciliacaoBancaria = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B120530734977149415")))
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão btnConciliacaoBancaria encontrado ",
            routine="ExtratoDeContas",
            error_details=''
        )
        btnConciliacaoBancaria.click()
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão btnConciliacaoBancaria clicado ",
            routine="ExtratoDeContas",
            error_details=''
        )

    
        WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P194_CONTA_ID")))
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Elemento no iframe encontrado",
            routine="ExtratoDeContas",
            error_details=''
        )




        # Quando criar a rotina de conciliação bancaria importar a função pra cá

        



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



    
         

