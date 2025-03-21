from datetime import datetime,timedelta
import random
import time
import lorem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.GerarDados import GeradorDados  
from scripts.FuncoesUteis import FuncoesUteis
from scripts.ApexUtil import Apex
from scripts.Components import Components


def test_contasReceber_insereConta_aba_Recebimentos(init,query):        
  
       
    randomQuery = query

    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
    getEnv = env_vars
    env_application_type = getEnv.get("WEB")    
   
    randomValue = round(random.uniform(1, 100), 2)
    randomText = lorem.paragraph()
    randomNumber = GeradorDados.randomNumberDinamic(0,5)
    randomDay = GeradorDados.randomNumberDinamic(1,30)

    today = datetime.today()
    todayStr = today.strftime("%d/%m/%Y")
    randomDay = GeradorDados.randomNumberDinamic(0, 30)
    randomDate = today + timedelta(days=randomDay)
    finalDateStr = randomDate.strftime("%d/%m/%Y")
#_________________________________________________________________
# inicio da aba Recebimento de nova conta a pagar  
    try:

        valorOriginalValue = FuncoesUteis.stringToFloat(Apex.getValue(browser,"P85_VALOR"))
        clienteOriginalValue  = FuncoesUteis.stringToFloat(Apex.getValue(browser,"P85_PESSOA_CLIENTE_ID"))
        numeroDocumentoOriginalValue = FuncoesUteis.stringToFloat(Apex.getValue(browser,"P85_NUMERO_DOCUMENTO"))

        # Aguarda a aba estar visível
        abaRecebimento = WebDriverWait(browser, 30).until(
            EC.visibility_of_element_located((By.ID, "recebimento_tab"))
        )
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de Recebimento encontrada", routine="ContaReceber", error_details ="" )


        # Garante que o elemento está na tela
        browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", abaRecebimento)
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Scroll até Aba de Recebimento ", routine="ContaReceber", error_details ="" )


        # Aguarda até que o elemento esteja clicável
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#recebimento_tab")))
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de Recebimento clicavel", routine="ContaReceber", error_details ="" )


        abaRecebimento.click()
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de Recebimento clicada", routine="ContaReceber", error_details ="" )
    
        try:
            novoRecebimento = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B118674634687784523")))    
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão novo Recebimento encontrado", routine="ContaReceber", error_details ="" )

            novoRecebimento.click()
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão novo Recebimento clicado", routine="ContaReceber", error_details ="" )
            has_repeat = True
        except  (TimeoutException, NoSuchElementException, Exception) as e:
            has_repeat = False
            Log_manager.add_log(
                application_type=env_application_type,
                level="ERROR",
                message="Botão novo recebimento não encontrado",
                routine="ContaReceber",
                error_details=str(e)
            )  

        if has_repeat:
            seletor = "#contaReceberRecebimento"
            has_frame = Components.has_frame(init,seletor)


            if has_frame:         
                
                valorDescontoDividido = round((randomValue/4),2)
                valorDescontoDividido = FuncoesUteis.formatBrCurrency(valorDescontoDividido)
                randomContaId = randomQuery["Random_queryContaId"] if randomNumber != 0 else randomText
                randomPagamentoId = randomQuery["Random_queryFormaPagamento"] if randomNumber != 0 else randomText
                finalDate = todayStr if randomNumber in (0,1,2,3) else finalDateStr if randomNumber == 4 else randomText
                valorOriginalPagamento = valorOriginalValue/3
                valorDescontoDividido = valorDescontoDividido  if randomNumber != 0 else randomText
                randomValue = randomValue  if randomNumber != 0 else randomText
                randomText =randomText  if randomNumber != 0 else randomValue

                apexValues = {
                    "P87_CONTA_ID":randomContaId,
                    "P87_FORMA_PAGAMENTO":randomPagamentoId,
                    "P87_DATA_RECEBIMENTO":finalDate,
                    "P87_VALOR_RECEBIMENTO":valorOriginalPagamento,
                    "P87_DESCONTO":valorDescontoDividido,
                    "P87_JUROS":randomValue,
                    "P87_MULTA":randomValue,
                    "P87_TAXAS":randomValue,
                    "P87_ACRESCIMOS":randomValue,
                    "P87_OBSERVACAO":randomText,
                }

                apexGetValue = {}   

                for seletor,value in apexValues.items():
                    Apex.setValue(browser,seletor,value)
                    Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                            message=f"{seletor} teve o valor {value} inserido", 
                                            routine="ContaReceber", error_details="")

                    apexGetValue[seletor] =  FuncoesUteis.stringToFloat(Apex.getValue(browser,seletor))     
                    Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                            message=f"{seletor} teve o valor {apexGetValue[seletor]} encontrado", 
                                            routine="ContaReceber", error_details="")
                    clienteId = FuncoesUteis.stringToFloat(Apex.getValue(browser,"P87_PESSOA_ID")

)
                apexValuesDisplay = {
                    9:  "#P87_NUMERO_DOCUMENTO_DISPLAY",
                    6:  "#P87_VALOR_DISPLAY",
                    0:  "#P87_DESCONTO_CONTA_DISPLAY > span" ,
                    4:  "#P87_TAXAS_CONTA_DISPLAY > span",
                    1:  "#P87_JUROS_CONTA_DISPLAY > span",
                    2:  "#P87_MULTA_CONTA_DISPLAY > span",
                    3:  "#P87_ACRESCIMOS_CONTA_DISPLAY > span",
                    7:  "#P87_VALOR_TOTAL_DISPLAY > span",
                    5:  "#P87_SALDO_DISPLAY > span"
                }

                displayValuesText = {}
                valorFloat = {}

                for key, selector in apexValuesDisplay.items():
                    try:
                        element = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                        displayValuesText[key] = element.text  
                        Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                            message=f"{selector} Display encontrado com valor: {displayValuesText[key]}", 
                                            routine="ContaReceber", error_details="")
                        valorFloat[key] = FuncoesUteis.stringToFloat(displayValuesText[key])
                    except Exception as e:
                        Log_manager.add_log(application_type=env_application_type, level="ERROR", 
                                            message=f"Erro ao encontrar {selector}", 
                                            routine="ContaReceber", error_details=str(e))

                valorSomado =  round(abs(valorFloat[6] - valorFloat[0] + valorFloat[1] + valorFloat[2] + valorFloat[3]),2)         

            
                valores = {
                    "Desconto": ((apexGetValue["P87_DESCONTO"]), valorFloat[0]),
                    "Juros": (apexGetValue["P87_JUROS"], valorFloat[1]),
                    "Multa": (apexGetValue["P87_MULTA"], valorFloat[2]),
                    "Acréscimos": (apexGetValue["P87_ACRESCIMOS"], valorFloat[3]),
                    "Taxas": (apexGetValue["P87_TAXAS"], valorFloat[4]),
                    "Valor Total": (valorFloat[7], valorSomado),
                    "Valor Original": (valorOriginalValue,valorFloat[6]),
                    "Cliente" : (clienteOriginalValue,clienteId),
                    "Documento": (numeroDocumentoOriginalValue,valorFloat[9])
                }


                FuncoesUteis.compareValues(init,valores)

                btnSaveIframeRecebimentos =  WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#btn_salvar"))) 
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão save do iframe Recebimentos encontrado", routine="ContaReceber", error_details ="" )

                btnSaveIframeRecebimentos.click()
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão save do iframe Recebimentos clicado", routine="ContaReceber", error_details ="" )

                FuncoesUteis.has_alert(init)            
               
                browser.switch_to.default_content()
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Voltando para o conteudo principal", routine="ContaReceber", error_details ="" )
                

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