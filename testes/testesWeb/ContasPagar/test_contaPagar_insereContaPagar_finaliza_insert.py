from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.FuncoesUteis import FuncoesUteis

def test_insere_conta_pagar_finaliza_insert(init):
        
    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
    getEnv = env_vars
    env_application_type = getEnv.get("WEB")
#________________________________________________________________
# Parte que finaliza o processo de nova conta a pagar

    try:

        # Captura o botão de salvar e clica
        salvarConta =  WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[name='salvarSair']")))
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão salvar do nova conta a pagar encontrado",
            routine="ContaPagar",
            error_details=''
        ) 

        browser.execute_script("arguments[0].scrollIntoView(true);", salvarConta)
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Scroll até Botão salvar do nova conta a pagar",
            routine="ContaPagar",
            error_details=''
        )

        salvarConta.click()
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão salvar do nova conta a pagar clicado",
            routine="ContaPagar",
            error_details=''
        ) 

        has_alert = FuncoesUteis.has_alert(init)
        has_alert_sucess = FuncoesUteis.has_alert_sucess(init)       

        if has_alert_sucess:
            # Captura o botão de Voltar a Contas a Pagar e clica
            voltarContaPagar =  WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#B103339792839912425"))) 
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão voltar a contas a pagar encontrado", routine="ContaPagar", error_details ="" )

            voltarContaPagar.click()
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão voltar a contas a pagar clicado", routine="ContaPagar", error_details ="" )


        if has_alert:
            Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Alert de erro encontrado",
            routine="ContaPagar",
            error_details=''
        )
            



    except TimeoutException as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro: Tempo limite excedido ao acessar a página",
            routine="ContaPagar",
            error_details=str(e)
        )

    except NoSuchElementException as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro: Elemento não encontrado na página",
            routine="ContaPagar",
            error_details=str(e)
        )

    except Exception as e:  # Captura qualquer outro erro inesperado
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro desconhecido ao acessar a página",
            routine="ContaPagar",
            error_details=str(e)
        )    
