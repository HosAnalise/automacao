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


def test_contasPagar_insereConta_aba_detalhes(init,query):


        
    
    
    randomContaId,randomFornecedorId,randomCategoriaFinanceiraId,randomEmpresaId,randomPagamentoId,randomChavePixId,randomBancoId,randomCentroCustoId,randomModeloDocumentoID = query
    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
    getEnv = env_vars
    env_application_type = getEnv.get("WEB")
    
    random_value = round(random.uniform(1, 999999), 2)
    randomValue = FuncoesUteis.formatBrCurrency(random_value)
    randomText = lorem.paragraph()
    randomNumber = GeradorDados.randomNumberDinamic(0,1)
    randomDay = GeradorDados.randomNumberDinamic(1,30)
 
    today = datetime.today()
    randomDay = GeradorDados.randomNumberDinamic(0, 30)
    randomDate = today + timedelta(days=randomDay)
    finalDate = randomDate.strftime("%d/%m/%Y")

    bigText700 = GeradorDados.gerar_texto(700)
    bigText500 = GeradorDados.gerar_texto(700)





    try:
        dataEmissao = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_DATA_EMISSAO")))
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: dataEmissao encontrado", routine="ContaPagar", error_details ="" )


        if randomNumber == 0:
            Apex.setValue(browser,"P47_DATA_EMISSAO",finalDate)
            dataEmissaoValue = Apex.getValue(browser,"P47_DATA_EMISSAO")
            if dataEmissaoValue == finalDate:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: dataEmissao teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P47_DATA_EMISSAO",randomText)
            dataEmissaoValue = Apex.getValue(browser,"P47_DATA_EMISSAO")
            if dataEmissaoValue == randomText:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: dataEmissao teve o valor inserido incorretamente valor: {dataEmissaoValue}", routine="ContaPagar", error_details ="" )

        # Escolhe uma data de registro de pagamento e insere valores
        dataRegistro = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_DATA_REGISTRO")))
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: dataRegistro encontrado", routine="ContaPagar", error_details ="" )


        if randomNumber == 0:
            Apex.setValue(browser,"P47_DATA_REGISTRO",finalDate)
            dataRegistroValue = Apex.getValue(browser,"P47_DATA_REGISTRO")
            if dataRegistroValue == finalDate:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: dataRegistro teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P47_DATA_REGISTRO",randomText)  
            dataRegistroValue = Apex.getValue(browser,"P47_DATA_REGISTRO")
            if dataRegistroValue == randomText:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: dataRegistro teve o valor inserido incorretamente valor: {dataRegistroValue}", routine="ContaPagar", error_details ="" )
              
     


        # Captura o campo centro custo e insere valores

        centroCusto = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_CENTRO_DE_CUSTO"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: centroCusto encontrado", routine="ContaPagar", error_details ="" )

        
        if randomNumber == 0:
            Apex.setValue(browser,"P47_CENTRO_DE_CUSTO",randomCentroCustoId)
            centroCustoValue = Apex.getValue(browser,"P47_CENTRO_DE_CUSTO")
            if centroCustoValue == randomCentroCustoId:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: centroCusto teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P47_CENTRO_DE_CUSTO",randomValue)
            centroCustoValue = Apex.getValue(browser,"P47_CENTRO_DE_CUSTO")
            if centroCustoValue == randomText:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: centroCusto teve o valor inserido incorretamente valor: {centroCustoValue}", routine="ContaPagar", error_details ="" )


        # Captura o campo conferido e insere valores

        conferido = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_CONFERIDO"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: conferido encontrado", routine="ContaPagar", error_details ="" )


        # Role até o elemento para garantir visibilidade
        browser.execute_script("arguments[0].scrollIntoView(true);", conferido)

        # Clique no elemento
        if randomNumber == 0:
            Apex.setValue(browser,"P47_CONFERIDO","1")
        else:
            Apex.setValue(browser,"P47_CONFERIDO",randomText)               


        # Captura o campo tipo do documento e insere valores

        tipoDocumento = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_DOCUMENTO_FISCAL_MODELO_ID"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: tipoDocumento encontrado", routine="ContaPagar", error_details ="" )


        if randomNumber == 0:
            Apex.setValue(browser,"P47_DOCUMENTO_FISCAL_MODELO_ID",randomModeloDocumentoID)
            tipoDocumentoValue = Apex.getValue(browser,"P47_DOCUMENTO_FISCAL_MODELO_ID")
            if tipoDocumentoValue == randomModeloDocumentoID:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: tipoDocumento teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )

        else:
            Apex.setValue(browser,"P47_DOCUMENTO_FISCAL_MODELO_ID",randomText)
            tipoDocumentoValue = Apex.getValue(browser,"P47_DOCUMENTO_FISCAL_MODELO_ID")
            if tipoDocumentoValue == randomText:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: tipoDocumento teve o valor inserido incorretamente valor: {tipoDocumentoValue}", routine="ContaPagar", error_details ="" )



        # Captura o campo chave da NF-e e insere valores
        chaveNFe = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_CHAVE_NFE"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: chaveNFe encontrado", routine="ContaPagar", error_details ="" )

        randomChaveNfe = GeradorDados.gerar_chave_nfe()


        if randomNumber == 0:
            Apex.setValue(browser,"P47_CHAVE_NFE",randomChaveNfe)
            chaveNFeValue = Apex.getValue(browser,"P47_CHAVE_NFE")
            if chaveNFeValue == randomChaveNfe:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: chaveNFe teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )

        else:
            Apex.setValue(browser,"P47_CHAVE_NFE",bigText500)
            chaveNFeValue = Apex.getValue(browser,"P47_CHAVE_NFE")
            if chaveNFeValue == bigText500:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: chaveNFe teve o valor inserido incorretamente valor: {chaveNFeValue}", routine="ContaPagar", error_details ="" )
            

        # Captura o campo Nº pedido de compra e insere valores
        numeroPedidoCompra = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_NUMERO_PEDIDO"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: numeroPedidoCompra encontrado", routine="ContaPagar", error_details ="" )
        randomNumeroPedidoCompra = GeradorDados.randomNumberDinamic(00000000000,9999999999)


        if randomNumber == 0:
            Apex.setValue(browser,"P47_NUMERO_PEDIDO",randomNumeroPedidoCompra)
            numeroPedidoCompraValue = Apex.getValue(browser,"P47_NUMERO_PEDIDO")
            if numeroPedidoCompraValue == randomNumeroPedidoCompra:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: numeroPedidoCompra teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P47_NUMERO_PEDIDO",bigText500)
            numeroPedidoCompraValue = Apex.getValue(browser,"P47_NUMERO_PEDIDO")
            if numeroPedidoCompraValue == bigText500:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: numeroPedidoCompra teve o valor inserido incorretamente valor: {numeroPedidoCompraValue}", routine="ContaPagar", error_details ="" )




        # Captura o campo Tipo documento e insere valores
        numeroDocumento = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_NUMERO_DOCUMENTO"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: numeroDocumento encontrado", routine="ContaPagar", error_details ="" )
        randomNumeroDocumento = GeradorDados.randomNumberDinamic(00000000000,9999999999)


        if randomNumber == 0:
            Apex.setValue(browser,"P47_NUMERO_DOCUMENTO",randomNumeroDocumento)
            numeroDocumentoValue = Apex.getValue(browser,"P47_NUMERO_DOCUMENTO")
            if numeroDocumentoValue == randomNumeroDocumento:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: numeroDocumento teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P47_NUMERO_DOCUMENTO",bigText500)      
            numeroDocumentoValue = Apex.getValue(browser,"P47_NUMERO_DOCUMENTO")
            if numeroDocumentoValue == bigText500:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: numeroDocumento teve o valor inserido incorretamente valor: {numeroDocumentoValue}", routine="ContaPagar", error_details ="" )



        # Captura o campo Tipo documento e insere valores
        numeroTitulo = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_NUMERO_TITULO"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: numeroTitulo encontrado", routine="ContaPagar", error_details ="" )
        randomNumeroTitulo = GeradorDados.randomNumberDinamic(00000000000,9999999999)

        if randomNumber == 0:
            Apex.setValue(browser,"P47_NUMERO_TITULO",randomNumeroTitulo)
            numeroTituloValue = Apex.getValue(browser,"P47_NUMERO_TITULO")
            if numeroTituloValue == randomNumeroTitulo:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: numeroTitulo teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P47_NUMERO_TITULO",bigText500)   
            numeroTituloValue = Apex.getValue(browser,"P47_NUMERO_TITULO")
            if numeroTituloValue == bigText500:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: numeroTitulo teve o valor inserido incorretamente valor: {numeroTituloValue}", routine="ContaPagar", error_details ="" )       
               
        # Captura o campo Tipo documento e insere valores
        codigoBarras = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_CODIGO_BARRAS")))
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: codigoBarras encontrado", routine="ContaPagar", error_details ="" )
        randomCodigoBarras = GeradorDados.randomNumberDinamic(00000000000,9999999999)

 

        if randomNumber == 0:
            Apex.setValue(browser,"P47_CODIGO_BARRAS",randomCodigoBarras)
            codigoBarrasValue = Apex.getValue(browser,"P47_CODIGO_BARRAS")
            if codigoBarrasValue == randomCodigoBarras:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: codigoBarras teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P47_CODIGO_BARRAS",bigText500) 
            codigoBarrasValue = Apex.getValue(browser,"P47_CODIGO_BARRAS")
            if codigoBarrasValue == bigText500:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: codigoBarras teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )        



        observacoes = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_OBSERVACAO"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: observacoes encontrado", routine="ContaPagar", error_details ="" )


        # Role até o elemento para garantir visibilidade
        browser.execute_script("arguments[0].scrollIntoView(true);", observacoes)

        # Clique no elemento
        if randomNumber == 0:
            Apex.setValue(browser,"P47_OBSERVACAO",bigText500)
            observacoesValue = Apex.getValue(browser,"P47_OBSERVACAO")
            if observacoesValue == bigText500:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: observacoes teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P47_OBSERVACAO",bigText700)     
            observacoesValue = Apex.getValue(browser,"P47_OBSERVACAO")
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