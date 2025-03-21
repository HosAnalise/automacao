from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.GerarDados import GeradorDados  
from scripts.ApexUtil import Apex
from scripts.FuncoesUteis import FuncoesUteis


def test_contasReceber_insereConta_aba_juros_multas(init):


    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
    getEnv = env_vars
    env_application_type = getEnv.get("WEB")

    try:

        abaJurosMultas = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"R55917550016747726_tab")))
        Log_manager.add_log(application_type =env_application_type,
                            level= "INFO",
                            message = "Aba de Juros e multas encontrada",
                            routine="ContaReceber", 
                            error_details ="" 
                            )
        
        abaJurosMultas.click()
        Log_manager.add_log(application_type =env_application_type,
                            level= "INFO",
                            message = "Aba de Juros e multas clicada",
                            routine="ContaReceber", 
                            error_details ="" 
                            )
        randomValue = GeradorDados.randomNumberDinamic(0,4)
        randomText = GeradorDados.gerar_texto(200)

        jurosDiaValor = FuncoesUteis.formatBrCurrency(GeradorDados.randomNumberDinamic(1,100)) if randomValue != 0 else randomText
        multaValor = FuncoesUteis.formatBrCurrency(GeradorDados.randomNumberDinamic(1,100)) if randomValue != 0 else randomText
        jurosMesValor = FuncoesUteis.formatBrCurrency(GeradorDados.randomNumberDinamic(1,100)) if randomValue != 0 else randomText

        apexValues = {
            "P85_JUROS_CONTA_RECEBER":jurosDiaValor,
            "P85_MULTA_CONTA_RECEBER":multaValor,
            "P85_JUROS_MES_CONTA_RECEBER":jurosMesValor
        }

        apexGetValue = {}
        for seletor, value in apexValues.items():
            Apex.setValue(browser,seletor,value)
            Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                            message=f"{seletor} teve o valor {value} inserido", 
                                            routine="ContaReceber", error_details="")
            
            apexGetValue[seletor] = FuncoesUteis.formatBrCurrency(Apex.getValue(browser,seletor))
            Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                            message=f"{seletor} teve o valor {apexGetValue[seletor]} encontrado", 
                                            routine="ContaReceber", error_details="")
            
        itens = {
            "JurosDia" : (jurosDiaValor,apexGetValue["P85_JUROS_CONTA_RECEBER"].replace('%','').strip()),
            "Multa" : (multaValor,apexGetValue["P85_MULTA_CONTA_RECEBER"].replace('%','').strip()),
            "JurosMes":(jurosMesValor,apexGetValue["P85_JUROS_MES_CONTA_RECEBER"].replace('%','').strip())
        }

        FuncoesUteis.compareValues(init,itens)

    except TimeoutException as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro: Tempo limite excedido ao acessar a página",
            routine="ContaPagar",
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
            routine="ContaPagar",
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
            routine="ContaPagar",
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
        


    
   

    