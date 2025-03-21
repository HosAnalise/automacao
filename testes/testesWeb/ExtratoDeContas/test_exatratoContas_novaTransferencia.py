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

@pytest.mark.parametrize("browser, login", [("chrome", "teste")], indirect=True)
def test_extratoContas_novaTransferencia(init,query):
       
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
        btnNovaTransferencia = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#novaTransferencia")))
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão btnNovaTransferencia encontrado ",
            routine="ExtratoDeContas",
            error_details=''
        )
        btnNovaTransferencia.click()
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão btnNovaTransferencia clicado ",
            routine="ExtratoDeContas",
            error_details=''
        )

        try:
            has_frame = WebDriverWait(browser,30).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"[title='Cadastro de Transferência']")))
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Trocando para o iframe: Cadastro de Transferência",
                routine="ExtratoDeContas",
                error_details=''
            )
        except(TimeoutException,Exception,NoSuchElementException) as e :
            has_frame = None
            Log_manager.add_log(
                application_type=env_application_type,
                level="ERROR",
                message="Troca para o iframe: Cadastro de Transferência. Falhou",
                routine="ExtratoDeContas",
                error_details=str(e)
            )

        if has_frame:
            WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P78_CONTA_ORIGEM_ID")))
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Elemento no iframe encontrado",
                routine="ExtratoDeContas",
                error_details=''
            )
            descricaoText500 = GeradorDados.gerar_texto(500)
            descricaoText700 = GeradorDados.gerar_texto(700)
            documento = GeradorDados.gerar_cpf() if randomValue != 0 else GeradorDados.gerar_chave_aleatoria()
            formaTransferenciaValue = randomQueries['Random_queryCliente'] if randomNumber != 0 else descricaoText700
            valorTransferenciaValue = randomValue if randomNumber != 0 else descricaoText700
            contaOrigemIdValue = randomQueries['Random_queryContaId'] if randomNumber != 0 else descricaoText700
            contaDestinoIdValue = randomQueries['Random_queryContaDestinoId'] if randomNumber != 0 else descricaoText700
            formaPagamentoValue = randomQueries['Random_queryFormaPagamento'] if randomNumber != 0 else descricaoText700
            descricaoText =  descricaoText500 if randomNumber != 0 else descricaoText700
            text = "Transferência entre Contas"

            Apex.setValue(browser,"P78_CONTA_ORIGEM_ID",contaOrigemIdValue)
            Apex.setValue(browser,"P78_CONTA_DESTINO_ID",contaDestinoIdValue)
            Apex.setValue(browser,"P78_DATA_TRANSFERENCIA",todaystr if randomNumber != 0 else descricaoText700)
            Apex.setValue(browser,"P78_FORMA_TRANSFERENCIA",formaTransferenciaValue)
            Apex.setValue(browser, "P78_NUMERO_DOCUMENTO", documento)
            Apex.setValue(browser,"P78_VALOR_TRANSFERENCIA",valorTransferenciaValue)
            Apex.setValue(browser,"P78_FORMA_PAGAMENTO",formaPagamentoValue)
            Apex.setValue(browser, "P78_DESCRICAO",descricaoText)

            
           
            contaOrigemId =  Apex.getValue(browser,"P78_CONTA_ORIGEM_ID")
            contaDestinoId =  Apex.getValue(browser,"P78_CONTA_DESTINO_ID")
            dataTransferencia = Apex.getValue(browser,"P78_DATA_TRANSFERENCIA")
            formaTransferencia  =  Apex.getValue(browser,"P78_FORMA_TRANSFERENCIA")
            numeroDocumento = Apex.getValue(browser,"P194_NUMERO_DOCUMENTO")
            valorTransferencia =  Apex.getValue(browser,"P78_VALOR_TRANSFERENCIA")
            formaPagamento = Apex.getValue(browser,"P78_FORMA_PAGAMENTO")
            descricao = Apex.getValue(browser,"P78_DESCRICAO")
            origem = Apex.getValue(browser,"P78_ORIGEM")



            campos = {
                    "contaOrigemId" : (contaOrigemId,contaOrigemIdValue),
                    "contaDestinoId" : (contaDestinoId,contaDestinoIdValue),
                    "dataTransferencia": (dataTransferencia,todaystr),
                    "formaTransferencia":(formaTransferencia,formaTransferenciaValue),
                    "numeroDocumento":(numeroDocumento,documento),
                    "valorTransferencia" : (valorTransferencia,randomValue),
                    "formaPagamento": (formaPagamento,formaPagamentoValue),
                    "origem":(origem,text),
                    "descricao": (descricao,descricaoText)
            }



            valoresDiferentes = {chave: (v1, v2) for chave, (v1, v2) in campos.items() if v1 != v2}

            if not valoresDiferentes:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Todos valores foram inseridos corretamente ", routine="ExtratoDeContas", error_details ="" )

            else:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = " Valores foram inseridos incorretamente  ", routine="ExtratoDeContas", error_details ="" )

                for chave, (v1, v2) in valoresDiferentes.items():
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f" valores incorretos: - {chave}: {v1} (esperado) ≠ {v2} (atual)", routine="ExtratoDeContas", error_details ="" )



            btnSaveCadastroTransferenciaResumido = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B89271388586096015")))
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message="o botão btnSaveCadastroTransferenciaResumido foi encontrado",
                    routine="ExtratoDeContas",
                    error_details=''
                )
            btnSaveCadastroTransferenciaResumido.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message="o botão btnSaveCadastroTransferenciaResumido foi clicado",
                    routine="ExtratoDeContas",
                    error_details=''
                )
            
            if not FuncoesUteis.has_alert(init) and FuncoesUteis.has_alert_sucess(init):
                browser.switch_to.default_content()
            else:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="ERROR",
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



