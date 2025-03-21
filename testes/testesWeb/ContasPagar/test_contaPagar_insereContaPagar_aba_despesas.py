import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.GerarDados import GeradorDados  
from scripts.ApexUtil import Apex
from scripts.FuncoesUteis import FuncoesUteis

def test_contasPagar_insereConta_aba_despesas(init):
    

  
       
        
    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
    getEnv = env_vars
    env_application_type = getEnv.get("WEB")
    
    random_value = round(random.uniform(1, 999999), 2)
    randomValue = FuncoesUteis.formatBrCurrency(random_value)
    randomText = GeradorDados.gerar_texto(30)
    bigText700 = GeradorDados.gerar_texto(700)
    





    try:#_________________________________________________________________
# inicio da aba despesas  
 
        abaDespesas = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#despesas_tab")))
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Aba despesas encontrada",
            routine="ContaPagar",
            error_details=''
        )
        browser.execute_script("arguments[0].scrollIntoView(true);", abaDespesas)
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Scroll até a aba de despesas",
            routine="ContaPagar",
            error_details=''
        )

        abaDespesas.click()
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Aba de despesas clicada",
            routine="ContaPagar",
            error_details=''
        )

        btnNovaDespesa = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#despesa")))
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão nova despesa encontrado",
            routine="ContaPagar",
            error_details=''
        )
        btnNovaDespesa.click()
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão nova despesa encontrado",
            routine="ContaPagar",
            error_details=''
        )


        WebDriverWait(browser,30).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"[title='Conta Pagar X Despesas']")))
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Mudando para o iframe Conta Pagar X Despesas",
            routine="ContaPagar",
            error_details=''
        )

        smallOrbig = GeradorDados.randomNumberDinamic(0,1)

        if smallOrbig == 0:
            Apex.setValue(browser,"P139_MOTIVO",randomText) 
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"Valor P139_MOTIVO setado para: {randomText}",
                routine="ContaPagar",
                error_details=''
            )
        else:
            Apex.setValue(browser,"P139_MOTIVO",bigText700) 
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"Valor P139_MOTIVO setado para: {bigText700}",
                routine="ContaPagar",
                error_details=''
            )

        

        textOrNumber = GeradorDados.randomNumberDinamic(0,1)
        if textOrNumber == 0:
            Apex.setValue(browser,"P139_DESPESA",randomValue)
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"Valor P139_DESPESA setado para: {randomValue}",
                routine="ContaPagar",
                error_details=''
            ) 
        else:
            Apex.setValue(browser,"P139_DESPESA",randomText)
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"Valor P139_DESPESA setado para: {randomText}",
                routine="ContaPagar",
                error_details=''
            ) 

        btnSaveIframeDespesas = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B22200413557968720")))
        Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Botão Save do iframe encontrado",
                routine="ContaPagar",
                error_details=''
            )
        btnSaveIframeDespesas.click()
        Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Botão Save do iframe clicado",
                routine="ContaPagar",
                error_details=''
            )
        
        has_alert = FuncoesUteis.has_alert(init)


        browser.switch_to.default_content()
        Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Voltando pro contexto principal",
                routine="ContaPagar",
                error_details=''
            )
        


        # WebDriverWait(browser,30).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"[title='Excluir']")))   

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