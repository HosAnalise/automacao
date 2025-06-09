from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class Components:

    rotina = "Components"

    @staticmethod
    def has_alert_success(init: tuple) -> bool:
        """
        Verifica se há um alerta de sucesso na página.

        :param init: Tupla contendo os objetos necessários:
            (browser, login, Log_manager, get_ambiente, env_vars,
            seletor_ambiente, screenshots, oracle_db_connection)
        :return: True se o alerta de sucesso for encontrado, False caso contrário.
        """
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        try:
            alert = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#t_Alert_Success"))
            )
            content = alert.text.strip() if alert else ""
            Log_manager.add_log(
                application_type="Web",
                level="INFO",
                message=f"Alerta de sucesso encontrado: {content}",
                routine=f"{Components.rotina} - has_alert_success",
                error_details=""
            )
            return True

        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(
                application_type="Web",
                level="INFO",
                message="Alerta de sucesso não encontrado",
                routine=f"{Components.rotina} - has_alert_success",
                error_details=str(e)
            )
            return False
# verifica se há um alert de sucesso, captura seu texto e insere o log com seu conteudo.       
#END has_alert_success(init)


    @staticmethod
    def has_form(init:tuple) -> bool:
        """
        Verifica se há um form na página.

        :param init: Tupla contendo os objetos necessários:
            (browser, login, Log_manager, get_ambiente, env_vars,
            seletor_ambiente, screenshots, oracle_db_connection)
        :return: True se o alerta de sucesso for encontrado, False caso contrário.
        """

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        try:

            formError = WebDriverWait(browser,10).until(EC.visibility_of_element_located((By.CSS_SELECTOR,".a-Form-error")))
        
            if formError:
                content = formError.text
                Log_manager.add_log(application_type ='Web',level= "ERROR", message = f"FormError encontrado , error:{content}", routine=f"{Components.rotina} - has_form", error_details ="" )
                return True

        except (TimeoutException, NoSuchElementException, Exception) as e :
            Log_manager.add_log(application_type ='Web',level= "INFO", message = "FormError não encontrado", routine=f"{Components.rotina} - has_form", error_details =f"{e}" )  
            return False 
#END has_form(init)


    @staticmethod
    def has_frame(init:tuple, seletor:str)->bool:
        """
        Verifica se há um iframe na página.

        :param init: Tupla contendo os objetos necessários:
            (browser, login, Log_manager, get_ambiente, env_vars,
            seletor_ambiente, screenshots, oracle_db_connection)
        :return: True se o alerta de sucesso for encontrado, False caso contrário.
        """
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
                routine=f"{Components.rotina} - has_frame",
                error_details=""
            )
            return True  

        except (TimeoutException, NoSuchElementException) as e:
            Log_manager.add_log(
                application_type=env_application_type,
                level="ERROR",
                message=f"Falha ao trocar para o iframe: {iframe_name or 'desconhecido'}",
                routine=f"{Components.rotina} - has_frame",
                error_details=str(e)
            )
            return False     
#END has_frame(init, seletor)


    @staticmethod
    def has_alert(init:tuple)->bool:
        """
        Verifica se há um alerta na página.

        :param init: Tupla contendo os objetos necessários:
            (browser, login, Log_manager, get_ambiente, env_vars,
            seletor_ambiente, screenshots, oracle_db_connection)
        :return: True se o alerta de sucesso for encontrado, False caso contrário.
        """
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        try:

            alert = WebDriverWait(browser,10).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#t_Alert_Notification")))
            if alert:
                content = alert.text    
                Log_manager.add_log(application_type ="Web",level= "ERROR", message = f" error:{content}", routine=f"{Components.rotina} - has_alert", error_details ="" )
                return True
    

        except (TimeoutException, NoSuchElementException, Exception) as e :
            Log_manager.add_log(application_type ="Web",level= "INFO", message = "Alert não encontrado", routine=f"{Components.rotina} - has_alert", error_details =f"{e}" )   
            return False
#END has_alert(init)


    @staticmethod
    def has_spin(init:tuple)->bool:
        """
        Verifica se há um spin de carregamento na página.

        :param init: Tupla contendo os objetos necessários:
            (browser, login, Log_manager, get_ambiente, env_vars,
            seletor_ambiente, screenshots, oracle_db_connection)
        :return: True se o alerta de sucesso for encontrado, False caso contrário.
        """

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        env_application_type = env_vars.get("WEB")  

        try:

            spin = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,".u-Processing-spinner")))
            Log_manager.add_log(application_type=env_application_type, level="INFO", message="Loading...", routine=f"{Components.rotina} - has_spin", error_details='')


            has = WebDriverWait(browser,30).until(EC.staleness_of(spin))
            Log_manager.add_log(application_type=env_application_type, level="INFO", message="fim do Loading...", routine=f"{Components.rotina} - has_spin", error_details='')
            return has
    

        except (TimeoutException, NoSuchElementException, Exception) as e :
            Log_manager.add_log(application_type ="Web",level= "INFO", message = "Alert não encontrado", routine=f"{Components.rotina} - has_spin", error_details =f"{e}" )   
            return False
#END has_spin(init)


    @staticmethod
    def url_contains(init:tuple,url:str)->bool:
        """
        Verifica se a url contem o trecho passado por parametro.

        :param init: Tupla contendo os objetos necessários:
            (browser, login, Log_manager, get_ambiente, env_vars,
            seletor_ambiente, screenshots, oracle_db_connection)
        :param url: trecho da url a ser verificada .             
        :return: True se o alerta de sucesso for encontrado, False caso contrário.
        """
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        env_application_type = env_vars.get("WEB")
            
        try:
            WebDriverWait(browser,10).until(EC.url_contains(url))
            Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"O trecho {url} esta presente na url da pagina atual", routine=f"{Components.rotina} - url_contains", error_details='')
            return True
        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine=f"{Components.rotina} - url_contains", error_details=str(e))
            return False
#END url_contains(init, url)


    @staticmethod
    def btnClick(init:tuple,seletor:str)->bool:
        """
        Executa o click de um botão na pagina e gera logs de sucesso e falha caso haja.

        :param init: Tupla contendo os objetos necessários:
            (browser, login, Log_manager, get_ambiente, env_vars,
            seletor_ambiente, screenshots, oracle_db_connection)
        :param seletor: seletor css que ira identificar o botão a ser clicado na pagina.              
        :return: True se o alerta de sucesso for encontrado, False caso contrário.
        """
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        env_application_type = env_vars.get("WEB")
            
        try:
            btnClick = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,seletor)))
            btnText = btnClick.text
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado",
                    routine=f"{Components.rotina} - btnClick",
                    error_details=''
                )
            
            btnClick.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} clicado",
                    routine=f"{Components.rotina} - btnClick",
                    error_details=''
                )
            return True
        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine=f"{Components.rotina} - btnClick", error_details=str(e))
            return False
#END btnClick(init, seletor)