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
def test_extratoContas_novaContaReceber(init,query):
       
    randomQueries =  query
    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

    getEnv = env_vars
    url_erp = getEnv.get('URL_ERP')
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
    
        btnNovaContaReceber = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#B89274598958096047")))
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão Nova Conta a Receber encontrado",
            routine="ExtratoDeContas",
            error_details=''
        )
        btnNovaContaReceber.click()
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão Nova Conta a Receber clicado",
            routine="ExtratoDeContas",
            error_details=''
        )


        try:
            has_frame = WebDriverWait(browser,30).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"[title='Cadastro de Contas a Receber Resumido']")))
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Trocando para o iframe: Cadastro de Contas a Receber Resumido",
                routine="ExtratoDeContas",
                error_details=''
            )
        except(TimeoutException,Exception,NoSuchElementException) as e :
            has_frame = None
            Log_manager.add_log(
                application_type=env_application_type,
                level="ERROR",
                message="Troca para o iframe: Cadastro de Contas a Receber Resumido. Falhou",
                routine="ExtratoDeContas",
                error_details=str(e)
            )

        if has_frame:
            WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P199_CONTA_ID")))
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Elemento no iframe encontrado",
                routine="ExtratoDeContas",
                error_details=''
            )
            descricaoText500 = GeradorDados.gerar_texto(500)
            descricaoText700 = GeradorDados.gerar_texto(700)
            
            Apex.setValue(browser,"P199_CONTA_ID",randomQueries['Random_queryContaId'] if randomNumber != 0 else descricaoText700)
            Apex.setValue(browser,"P199_VALOR",randomValue if randomNumber != 0 else descricaoText700)
            Apex.setValue(browser,"P199_FORMA_RECEBIMENTO",randomQueries['Random_queryFormaPagamento'] if randomNumber != 0 else descricaoText700)
            Apex.setValue(browser,"P199_PESSOA_ID",randomQueries['Random_queryCliente'] if randomNumber != 0 else descricaoText700)
            Apex.setValue(browser,"P199_DATA_EMISSAO",todaystr if randomNumber != 0 else descricaoText700)
            Apex.setValue(browser,"P199_DATA_RECEBIMENTO",finalDate if randomNumber != 0 else descricaoText700)
            Apex.setValue(browser,"P199_CATEGORIA_FINANCEIRA_ID",randomQueries['Random_queryCategoriaFinanceira'] if randomNumber != 0 else descricaoText700)
            Apex.setValue(browser, "P199_DESCRICAO", descricaoText500 if randomNumber != 0 else descricaoText700)

            contaid =  Apex.getValue(browser,"P199_CONTA_ID")
            valor =  Apex.getValue(browser,"P199_VALOR")
            formaRecebiemento = Apex.getValue(browser,"P199_FORMA_RECEBIMENTO")
            cliente  =  Apex.getValue(browser,"P199_PESSOA_ID")
            dataEmissao = Apex.getValue(browser,"P199_DATA_EMISSAO")
            dataRecebimento = Apex.getValue(browser,"P199_DATA_RECEBIMENTO")
            categoriaFinanceira = Apex.getValue(browser,"P199_CATEGORIA_FINANCEIRA_ID")
            descricao = Apex.getValue(browser,"P199_DESCRICAO")




            campos = {
                    "contaid" : (contaid,randomQueries['Random_queryContaId']),
                    "valor" : (valor,randomValue),
                    "formaRecebiemento": (formaRecebiemento,randomQueries['Random_queryFormaPagamento']),
                    "cliente":(cliente,randomQueries['Random_queryCliente']),
                    "dataEmissao": (dataEmissao,todaystr),
                    "dataRecebimento": (dataRecebimento,finalDate),
                    "categoriaFinanceira": (categoriaFinanceira,randomQueries['Random_queryCategoriaFinanceira']),
                    "descricao": (descricao,descricaoText500 )
            }

            valoresDiferentes = {chave: (v1, v2) for chave, (v1, v2) in campos.items() if v1 != v2}

            if not valoresDiferentes:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Todos valores foram inseridos corretamente ", routine="ExtratoDeContas", error_details ="" )

            else:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = " Valores foram inseridos incorretamente  ", routine="ExtratoDeContas", error_details ="" )

                for chave, (v1, v2) in valoresDiferentes.items():
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f" valores incorretos: - {chave}: {v1} (esperado) ≠ {v2} (atual)", routine="ExtratoDeContas", error_details ="" )

            btnSaveContaReceberResumido = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#save")))
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message="o botão btnSaveContaReceberResumido foi encontrado",
                    routine="ExtratoDeContas",
                    error_details=''
                )
            btnSaveContaReceberResumido.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message="o botão btnSaveContaReceberResumido foi clicado",
                    routine="ExtratoDeContas",
                    error_details=''
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

            icon = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".a-Icon.icon-irr-no-results")))
            if icon:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message="o icone inicial foi encontrado transação ocorreu corretamente",
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




    



    