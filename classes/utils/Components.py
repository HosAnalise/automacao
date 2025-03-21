from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class Components:
    @staticmethod
    def has_alert_sucess(init):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        try:

            alert = WebDriverWait(browser,10).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#t_Alert_Success")))
            if alert:
                content = alert.text    
                Log_manager.add_log(application_type ="Web",level= "INFO", message = f" Alert de sucesso encontrado! :{content}", routine="", error_details ="" )
                return True
    

        except (TimeoutException, NoSuchElementException, Exception) as e :
            Log_manager.add_log(application_type ="Web",level= "INFO", message = f"Alert de sucesso não encontrado", routine="", error_details =f"{e}" )   
            return False
# verifica se há um alert de sucesso, captura seu texto e insere o log com seu conteudo.       

    @staticmethod
    def has_form(init):

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        try:

            formError = WebDriverWait(browser,10).until(EC.visibility_of_element_located((By.CSS_SELECTOR,".a-Form-error")))
        
            if formError:
                content = formError.text
                Log_manager.add_log(application_type ='Web',level= "ERROR", message = f"FormError encontrado , error:{content}", routine="", error_details ="" )
                return True

        except (TimeoutException, NoSuchElementException, Exception) as e :
            Log_manager.add_log(application_type ='Web',level= "INFO", message = "FormError não encontrado", routine="", error_details =f"{e}" )  
            return False 
        


    @staticmethod
    def has_frame(init, seletor):
        browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
        
        env_application_type = env_vars.get("WEB")  
        iframe_name = None  

        try:
            # Aguardar até que o iframe esteja disponível e alternar para ele
            iframe_element = WebDriverWait(browser, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, seletor))
            )

            iframe_name = iframe_element.get_attribute("title") if iframe_element else "desconhecido"

            browser.switch_to.frame(iframe_element)

            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"Trocando para o iframe: {iframe_name}",
                routine="",
                error_details=""
            )
            return True  

        except (TimeoutException, NoSuchElementException) as e:
            Log_manager.add_log(
                application_type=env_application_type,
                level="ERROR",
                message=f"Falha ao trocar para o iframe: {iframe_name or 'desconhecido'}",
                routine="",
                error_details=str(e)
            )
            return False     
        
        
    @staticmethod
    def has_alert(init):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        try:

            alert = WebDriverWait(browser,10).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#t_Alert_Notification")))
            if alert:
                content = alert.text    
                Log_manager.add_log(application_type ="Web",level= "ERROR", message = f" error:{content}", routine="ContaPagar", error_details ="" )
                return True
    

        except (TimeoutException, NoSuchElementException, Exception) as e :
            Log_manager.add_log(application_type ="Web",level= "INFO", message = "Alert não encontrado", routine="ContaPagar", error_details =f"{e}" )   
            return False