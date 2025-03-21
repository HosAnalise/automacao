from datetime import datetime,timedelta
import random
import time
import lorem
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.GerarDados import GeradorDados  
from scripts.ApexUtil import Apex
from scripts.FuncoesUteis import FuncoesUteis
from scripts.Components import Components

@pytest.mark.suiteContaPagar
@pytest.mark.parametrize("browser, login", [("chrome", "teste")], indirect=True)
def test_conciliacaoBancaria_extratosBancarios_novaConciliacao(init,query):
       
    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

    getEnv = env_vars
    url_erp = getEnv.get('URL_ERP')
    env_application_type = getEnv.get("WEB")
    
  



    if not url_erp:
        pytest.fail("Erro crítico: 'URL_ERP' não encontrada no ambiente de variáveis. sim")   

    # Redireciona para a página de contas a pagar
    browser.get(f"{url_erp}conciliacao-bancaria")


  


    
    try:
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#P154_FILTRO_CONTA")))
        script ="$('button#t_Button_rightControlButton > span').click()"
        browser.execute_script(script)

        btnNovaConciliacao = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B43105716282300150")))
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão btnNovaConciliacao encontrado ",
            routine="ConciliacaoBancaria",
            error_details=''
        )
        btnNovaConciliacao.click()
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão btnNovaConciliacao clicado ",
            routine="ConciliacaoBancaria",
            error_details=''
        )

        seletor = "[title='Importar Extrato']"
        has_frame = Components.has_frame(init,seletor)
        print(f"valor do hasFrame {has_frame}")





        if has_frame:
            filePath = (r"C:\Users\Hos_Gabriel\Desktop\Automatização web\config\teste.ofx")
            WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".apex-item-filedrop-action.a-Button a-Button--hot")))
            dropZone = WebDriverWait(browser,30).until(EC.presence_of_element_located((By.CSS_SELECTOR,"#P156_ARQUIVO_OFX")))
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="input do arquivo Ofx encontrado",
                routine="ExtratoDeContas",
                error_details=''
            )
            dropZone.send_keys(filePath)
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Aquivo Ofx dropado no input do arquivo Ofx",
                routine="ExtratoDeContas",
                error_details=''
            )

            btnImportaExtrato = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#importarExtrato")))
            Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão btnImportaExtrato encontrado ",
            routine="ConciliacaoBancaria",
            error_details=''
            )
            btnImportaExtrato.click()
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Botão btnImportaExtrato clicado ",
                routine="ConciliacaoBancaria",
                error_details=''
            )

            try:

                btnConfirm = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".js-confirmBtn")))
                Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Botão btnConfirm encontrado ",
                routine="ConciliacaoBancaria",
                error_details=''
                )
                btnConfirm.click()
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message="Botão btnConfirm clicado ",
                    routine="ConciliacaoBancaria",
                    error_details=''
                )

            except (TimeoutException,Exception,NoSuchElementException) as e:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="ERROR",
                    message="Erro: Tempo limite excedido ao acessar a página",
                    routine="ConciliacaoBancaria",
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

            if not FuncoesUteis.has_alert(init) and FuncoesUteis.has_alert_sucess(init):
                browser.switch_to.default_content()
            else:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="Erro",
                    message="Alert encontrado",
                    routine="ExtratoDeContas",
                    error_details=''  
                ) 





    except TimeoutException as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro: Tempo limite excedido ao acessar a página",
            routine="ConciliacaoBancaria",
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
            routine="ConciliacaoBancaria",
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
            routine="ConciliacaoBancaria",
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



