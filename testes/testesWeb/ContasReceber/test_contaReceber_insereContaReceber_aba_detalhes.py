from datetime import datetime,timedelta
import random
import lorem
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.GerarDados import GeradorDados  
from scripts.ApexUtil import Apex
from scripts.FuncoesUteis import FuncoesUteis


def test_contasReceber_insereConta_aba_detalhes(init,query):        
    
    randomQueries = query
    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
    getEnv = env_vars
    env_application_type = getEnv.get("WEB")
    
    random_value = round(random.uniform(1, 999999), 2)
    randomValue = FuncoesUteis.formatBrCurrency(random_value)
    randomText = lorem.paragraph()
    randomNumber = GeradorDados.randomNumberDinamic(0,4)
    randomDay = GeradorDados.randomNumberDinamic(1,30)
 
    today = datetime.today()
    randomDay = GeradorDados.randomNumberDinamic(0, 30)
    randomDate = today + timedelta(days=randomDay)
    finalDate = randomDate.strftime("%d/%m/%Y")

    bigText700 = GeradorDados.gerar_texto(700)
    bigText500 = GeradorDados.gerar_texto(700)

   




    try:

        apexValues = {}





        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P85_DATA_EMISSAO")))
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: dataEmissao encontrado", routine="ContaPagar", error_details ="" )


        if randomNumber != 0:
            Apex.setValue(browser,"P85_DATA_EMISSAO",finalDate)
            dataEmissaoValue = Apex.getValue(browser,"P85_DATA_EMISSAO")
            if dataEmissaoValue == finalDate:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: dataEmissao teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P85_DATA_EMISSAO",randomText)
            dataEmissaoValue = Apex.getValue(browser,"P85_DATA_EMISSAO")
            if dataEmissaoValue == randomText:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: dataEmissao teve o valor inserido incorretamente valor: {dataEmissaoValue}", routine="ContaPagar", error_details ="" )

        # Escolhe uma data de registro de pagamento e insere valores
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P85_DATA_REGISTRO")))
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: dataRegistro encontrado", routine="ContaPagar", error_details ="" )


        if randomNumber != 0:
            Apex.setValue(browser,"P85_DATA_REGISTRO",finalDate)
            dataRegistroValue = Apex.getValue(browser,"P85_DATA_REGISTRO")
            if dataRegistroValue == finalDate:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: dataRegistro teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P85_DATA_REGISTRO",randomText)  
            dataRegistroValue = Apex.getValue(browser,"P85_DATA_REGISTRO")
            if dataRegistroValue == randomText:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: dataRegistro teve o valor inserido incorretamente valor: {dataRegistroValue}", routine="ContaPagar", error_details ="" )

        # Captura o campo centro custo e insere valores
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P85_CENTRO_DE_CUSTO"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: centro de lucro encontrado", routine="ContaPagar", error_details ="" )

        
        if randomNumber != 0:
            Apex.setValue(browser,"P85_CENTRO_DE_CUSTO",randomValue)
            centroCustoValue = Apex.getValue(browser,"P85_CENTRO_DE_CUSTO")
            if centroCustoValue == randomValue:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: centro de lucro teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P85_CENTRO_DE_CUSTO",randomValue)
            centroCustoValue = Apex.getValue(browser,"P85_CENTRO_DE_CUSTO")
            if centroCustoValue == randomText:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: centro de lucro teve o valor inserido incorretamente valor: {centroCustoValue}", routine="ContaPagar", error_details ="" )

        # Captura o campo tipo do documento e insere valores

        tipoDocumento = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P85_DOCUMENTO_FISCAL_MODELO_ID"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: tipoDocumento encontrado", routine="ContaPagar", error_details ="" )
        browser.execute_script("arguments[0].scrollIntoView(true);", tipoDocumento)



        if randomNumber != 0:
            Apex.setValue(browser,"P85_DOCUMENTO_FISCAL_MODELO_ID",randomQueries["Random_queryModelodocumentoFiscal"])
            tipoDocumentoValue = Apex.getValue(browser,"P85_DOCUMENTO_FISCAL_MODELO_ID")
            if tipoDocumentoValue == randomQueries["Random_queryModelodocumentoFiscal"]:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: tipoDocumento teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )

        else:
            Apex.setValue(browser,"P85_DOCUMENTO_FISCAL_MODELO_ID",randomText)
            tipoDocumentoValue = Apex.getValue(browser,"P85_DOCUMENTO_FISCAL_MODELO_ID")
            if tipoDocumentoValue == randomText:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: tipoDocumento teve o valor inserido incorretamente valor: {tipoDocumentoValue}", routine="ContaPagar", error_details ="" )



        # Captura o campo chave da NF-e e insere valores
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P85_CHAVE_NFE"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: chaveNFe encontrado", routine="ContaPagar", error_details ="" )

        randomChaveNfe = GeradorDados.gerar_chave_nfe()


        if randomNumber != 0:
            Apex.setValue(browser,"P85_CHAVE_NFE",randomChaveNfe)
            chaveNFeValue = Apex.getValue(browser,"P85_CHAVE_NFE")
            if chaveNFeValue == randomChaveNfe:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: chaveNFe teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )

        else:
            Apex.setValue(browser,"P85_CHAVE_NFE",bigText500)
            chaveNFeValue = Apex.getValue(browser,"P85_CHAVE_NFE")
            if chaveNFeValue == bigText500:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: chaveNFe teve o valor inserido incorretamente valor: {chaveNFeValue}", routine="ContaPagar", error_details ="" )
            

        # Captura o campo Nº pedido de compra e insere valores
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P85_NUMERO_PEDIDO"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: numero pedido venda encontrado", routine="ContaPagar", error_details ="" )
        randomNumeroPedidoCompra = GeradorDados.randomNumberDinamic(00000000000,9999999999)


        if randomNumber != 0:
            Apex.setValue(browser,"P85_NUMERO_PEDIDO",randomNumeroPedidoCompra)
            numeroPedidoCompraValue = Apex.getValue(browser,"P85_NUMERO_PEDIDO")
            if numeroPedidoCompraValue == randomNumeroPedidoCompra:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: numero pedido venda teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P85_NUMERO_PEDIDO",bigText500)
            numeroPedidoCompraValue = Apex.getValue(browser,"P85_NUMERO_PEDIDO")
            if numeroPedidoCompraValue == bigText500:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: numero pedido venda teve o valor inserido incorretamente valor: {numeroPedidoCompraValue}", routine="ContaPagar", error_details ="" )




        # Captura o campo Tipo documento e insere valores
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P85_NUMERO_DOCUMENTO"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: numeroDocumento encontrado", routine="ContaPagar", error_details ="" )
        randomNumeroDocumento = GeradorDados.randomNumberDinamic(00000000000,9999999999)


        if randomNumber != 0:
            Apex.setValue(browser,"P85_NUMERO_DOCUMENTO",randomNumeroDocumento)
            numeroDocumentoValue = Apex.getValue(browser,"P85_NUMERO_DOCUMENTO")
            if numeroDocumentoValue == randomNumeroDocumento:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: numeroDocumento teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P85_NUMERO_DOCUMENTO",bigText500)      
            numeroDocumentoValue = Apex.getValue(browser,"P85_NUMERO_DOCUMENTO")
            if numeroDocumentoValue == bigText500:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: numeroDocumento teve o valor inserido incorretamente valor: {numeroDocumentoValue}", routine="ContaPagar", error_details ="" )
     
               
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P85_TIPO_COBRANCA")))
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: codigoBarras encontrado", routine="ContaPagar", error_details ="" ) 

        if randomNumber != 0:
            Apex.setValue(browser,"P85_TIPO_COBRANCA",1)
            tipoCobrancaValue = Apex.getValue(browser,"P85_TIPO_COBRANCA")
            if tipoCobrancaValue == '1':
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: tipo cobrança teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P85_TIPO_COBRANCA",2) 
            tipoCobrancaValue = Apex.getValue(browser,"P85_TIPO_COBRANCA")
            if tipoCobrancaValue == '2':
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: tipo cobrança teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )     

        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P85_COBRADOR")))
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: tipo cobrança encontrado", routine="ContaPagar", error_details ="" ) 

        if randomNumber != 0:
            Apex.setValue(browser,"P85_COBRADOR",randomQueries["Random_queryCobradorId"])
            tipoCobrancaValue = Apex.getValue(browser,"P85_COBRADOR")
            if tipoCobrancaValue == '1':
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: cobrador teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P85_COBRADOR",bigText500) 
            tipoCobrancaValue = Apex.getValue(browser,"P85_COBRADOR")
            if tipoCobrancaValue == '2':
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: cobrador teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )           



        observacoes = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P85_OBSERVACAO"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: observacoes encontrado", routine="ContaPagar", error_details ="" )


        # Role até o elemento para garantir visibilidade
        browser.execute_script("arguments[0].scrollIntoView(true);", observacoes)

        # Clique no elemento
        if randomNumber != 0:
            Apex.setValue(browser,"P85_OBSERVACAO",bigText500)
            observacoesValue = Apex.getValue(browser,"P85_OBSERVACAO")
            if observacoesValue == bigText500:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: observacoes teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P85_OBSERVACAO",bigText700)     
            observacoesValue = Apex.getValue(browser,"P85_OBSERVACAO")
            if observacoesValue == bigText700:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: observacoes teve o valor inserido incorretamente valor: {observacoesValue}", routine="ContaPagar", error_details ="" )

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