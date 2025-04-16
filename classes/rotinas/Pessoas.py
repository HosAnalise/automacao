from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.GerarDados import GeradorDados  
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components


class Pessoas:



    queries = {
            "tipoCadastro":   """
                                    SELECT
                                        TIPO_CADASTRO_PESSOA_ID
                                    FROM
                                        ERP.TIPO_CADASTRO_PESSOA
                                    WHERE TIPO_CADASTRO_PESSOA_ID <> 10
                                """,

                                   
    }
    
    @staticmethod
    def novaPessoa(init,query,staticValues = False):

        queries = query
        browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
        env_application_type = env_vars['WEB']

        try:
            hasComponent = WebDriverWait(browser,30).until(EC.presence_of_element_located((By.CSS_SELECTOR,"P6_FISICA_JURIDICA")))
            if not hasComponent:
                Components.btnClick(init,"#B88575101250151001")

            hasFrame = Components.has_frame(init,"[title='Cadastro de Pessoa']")


            tipoCadastro =  queries["Query_tipoCadastro"]
            tipoFisicaJuridica = GeradorDados.randomNumberDinamic(1,2)
            cpfCnpj = GeradorDados.gerar_cnpj() if tipoFisicaJuridica == 1 else GeradorDados.gerar_cpf()    

            if hasFrame:
                apexValues = staticValues if isinstance(staticValues,dict) else {
                    "P6_TIPO_CADASTRO_PESSOA_ID": tipoCadastro,
                    "P6_FISICA_JURIDICA": tipoFisicaJuridica,
                    "P6_CNPJ": cpfCnpj,   

                }


        except(TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))

#END novaPessoa(init,query,staticValues = False)       

        

