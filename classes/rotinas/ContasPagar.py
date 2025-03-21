from datetime import datetime,timedelta
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.GerarDados import GeradorDados  
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components


class ContasPagar:

    url="contas-a-pagar"
    filterSelector ="P46_SELETOR_LOJA"
    queries ={
        "queryContaId" : """
                SELECT CONTA.CONTA_ID  
                FROM ERP.CONTA
                JOIN ERP.CONTA_ESPECIFICACAO ON CONTA.CONTA_ID = CONTA_ESPECIFICACAO.CONTA_ID
                LEFT JOIN ERP.LOJA ON LOJA.LOJA_ID = CONTA_ESPECIFICACAO.LOJA_ID
                WHERE CONTA_ESPECIFICACAO.GRUPO_LOJA_ID = 1501
                    AND CONTA.TIPO_CONTA_ID IN (1, 2)
                    AND (CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IN (1) OR CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IS NULL)
                    AND (CONTA.CONTA_ID IN (0) OR CONTA_ESPECIFICACAO.STATUS IN (1))
            """,            
        "queryFornecedorId" : """
                SELECT PESSOA_ID 
                FROM ERP.PESSOA 
                WHERE GRUPO_LOJA_ID = 1501
                    AND EXISTS (
                        SELECT 1 
                        FROM ERP.PESSOA_CADASTRO 
                        WHERE PESSOA_CADASTRO.PESSOA_ID = PESSOA.PESSOA_ID 
                            AND PESSOA_CADASTRO.TIPO_CADASTRO_PESSOA_ID = 2
                    )
                    AND STATUS = 1
            """,
        "queryCategoriaFinanceira" : """
                SELECT CF.CATEGORIA_FINANCEIRA_ID  
                FROM ERP.CATEGORIA_FINANCEIRA CF
                LEFT JOIN ERP.CATEGORIA_FINANCEIRA_ESPECIFICACAO CFE ON CF.CATEGORIA_FINANCEIRA_ID = CFE.CATEGORIA_FINANCEIRA_ID
                LEFT JOIN ERP.CATEGORIA_FINANCEIRA CF_PAI ON CFE.CATEGORIA_FINANCEIRA_PAI_ID = CF_PAI.CATEGORIA_FINANCEIRA_ID
                WHERE CF.CLASSIFICACAO_CATEGORIA_FINANCEIRA_ID = 1
                    AND CFE.CATEGORIA_FINANCEIRA_PAI_ID IS NOT NULL
                    AND CFE.GRUPO_LOJA_ID = 1501
                    AND (CFE.CATEGORIA_FINANCEIRA_ID IN (0) OR CFE.STATUS = 1)
            """,
        "queryEmpresa" : """
                SELECT LOJA_ID FROM ERP.LOJA WHERE GRUPO_LOJA_ID = 1501
            """,
        "queryFormaPagamento" : """
                SELECT FORMA_PAGAMENTO_ID FROM ERP.FORMA_PAGAMENTO
                WHERE
                    status = 1
                    and (grupo_loja_id = 1501 or grupo_loja_id is null)
                    AND VISIVEL = 1        
            """,

        "queryTipoChave" : """
                SELECT TIPO_CHAVE_PIX_ID 
                FROM ERP.TIPO_CHAVE_PIX
            """,

        "queryBanco" : """
                SELECT BANCO_ID FROM ERP.BANCO
            """,
        "queryCentroCusto" : """
                SELECT 
                    CC.CENTRO_CUSTO_ID  
                FROM 
                    ERP.CENTRO_CUSTO CC
                LEFT JOIN 
                    ERP.CENTRO_CUSTO_ESPECIFICACAO CCE ON CC.CENTRO_CUSTO_ID = CCE.CENTRO_CUSTO_ID
                LEFT JOIN   
                    ERP.CENTRO_CUSTO CC_PAI ON CCE.CENTRO_CUSTO_PAI_ID = CC_PAI.CENTRO_CUSTO_ID
                WHERE 
                    CCE.GRUPO_LOJA_ID = 1501
                    AND CCE.CENTRO_CUSTO_PAI_ID IS NOT NULL 
                    AND (
                        CCE.CENTRO_CUSTO_ID IN (0)
                        OR CCE.STATUS IN (1)
                    )

                """,
        "queryModelodocumentoFiscal" : """
                SELECT 
                    MODELO.DOCUMENTO_FISCAL_MODELO_ID
                FROM 
                    ERP.DOCUMENTO_FISCAL_MODELO MODELO
            """
    }



    @staticmethod
    def insereContaPagar(init,query):
        randomContaId,randomFornecedorId,randomCategoriaFinanceiraId,randomEmpresaId,randomPagamentoId,randomChavePixId,randomBancoId,randomCentroCustoId,randomModeloDocumentoID = query
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
        
        random_value = round(random.uniform(1, 999999), 2)
        randomValue = FuncoesUteis.formatBrCurrency(random_value)
        randomText = GeradorDados.gerar_texto(50)
        randomNumber = GeradorDados.randomNumberDinamic(0,4)
        randomDay = GeradorDados.randomNumberDinamic(1,30)

        today = datetime.today()
        randomDay = GeradorDados.randomNumberDinamic(0, 30)
        randomDate = today + timedelta(days=randomDay)
        finalDate = randomDate.strftime("%d/%m/%Y")

        
        try:
           
            btnNovaContaPagar = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#B129961237978758786")))
            btnNovaContaPagar.click()

            WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_VALOR")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo: valorOriginal encontrado", routine="ContaPagar", error_details ="" )

            if randomNumber != 0:
                Apex.setValue(browser,"P47_VALOR",randomValue)
                valorOriginalValue = Apex.getValue(browser,"P47_VALOR")
                if valorOriginalValue == str(randomValue):
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: valorOriginal teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
            else:
                Apex.setValue(browser,"P47_VALOR",randomText)
                valorOriginalValue = Apex.getValue(browser,"P47_VALOR")
                if valorOriginalValue == randomText:
                    Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: valorOriginal teve o valor inserido incorretamente valor: {valorOriginalValue}", routine="ContaPagar", error_details ="" )


            naConta = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_CONTA_ID")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: naConta encontrado", routine="ContaPagar", error_details ="" )

            if randomNumber != 0:
                Apex.setValue(browser,"P47_CONTA_ID",randomContaId)
                naContaValue = Apex.getValue(browser,"P47_CONTA_ID")
                if naContaValue == randomContaId:
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: naConta teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
            else:
                Apex.setValue(browser,"P47_CONTA_ID",randomText)
                naContaValue = Apex.getValue(browser,"P47_CONTA_ID")
                if naContaValue == randomText:
                    Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: naConta teve o valor inserido incorretamente valor: {naContaValue}", routine="ContaPagar", error_details ="" )        
        

            # Captura pessoa favorecido/fornecedor e insre valores
            WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_PESSOA_FAVORECIDO_ID")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: pessoaFavorecido encontrado", routine="ContaPagar", error_details ="" )


            if randomNumber != 0:
                Apex.setValue(browser,"P47_PESSOA_FAVORECIDO_ID",randomFornecedorId)
                pessoaFavorecidoValue = Apex.getValue(browser,"P47_PESSOA_FAVORECIDO_ID")
                if pessoaFavorecidoValue == randomFornecedorId:
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: pessoaFavorecido teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
            else:
                Apex.setValue(browser,"P47_PESSOA_FAVORECIDO_ID",randomText)
                pessoaFavorecidoValue = Apex.getValue(browser,"P47_PESSOA_FAVORECIDO_ID")
                
                if pessoaFavorecidoValue == randomText:
                    Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: pessoaFavorecido teve o valor inserido incorretamente valor: {pessoaFavorecidoValue}", routine="ContaPagar", error_details ="" )



        
            # Captura o campo de data de vencimento e insere valores
            vencimentoConta = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_DATA_VENCIMENTO")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: vencimentoConta encontrado", routine="ContaPagar", error_details ="" )


            if randomNumber != 0:
                Apex.setValue(browser,"P47_DATA_VENCIMENTO",finalDate)
                vencimentoContaValue = Apex.getValue(browser,"P47_DATA_VENCIMENTO")
                if vencimentoContaValue == finalDate:
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: vencimentoConta teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )

            else:
                Apex.setValue(browser,"P47_DATA_VENCIMENTO",randomText)
                vencimentoContaValue = Apex.getValue(browser,"P47_DATA_VENCIMENTO")
                if vencimentoContaValue == randomText:
                    Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: vencimentoConta teve o valor inserido incorretamente valor: {vencimentoContaValue}", routine="ContaPagar", error_details ="" )
            
        

            # Escolhe uma data de previsão de pagamento e insere valores
            previsaoPagamentoConta = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_DATA_PREVISAO_PAGAMENTO")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: previsaoPagamentoConta encontrado", routine="ContaPagar", error_details ="" )


            if randomNumber != 0:
                Apex.setValue(browser,"P47_DATA_PREVISAO_PAGAMENTO",finalDate)
                previsaoPagamentoContaValue = Apex.getValue(browser,"P47_DATA_PREVISAO_PAGAMENTO")
                if previsaoPagamentoContaValue == finalDate:
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: previsaoPagamentoConta teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )

            else:
                Apex.setValue(browser,"P47_DATA_PREVISAO_PAGAMENTO",randomText)
                previsaoPagamentoContaValue = Apex.getValue(browser,"P47_DATA_PREVISAO_PAGAMENTO")
                if previsaoPagamentoContaValue == randomText:
                    Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: previsaoPagamentoConta teve o valor inserido incorretamente valor: {previsaoPagamentoContaValue}", routine="ContaPagar", error_details ="" )

        

            # Captura o campo de categoria financeira e insere valores
            categoriaFinanceira = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_CATEGORIA_FINANCEIRA")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: categoriaFinanceira encontrado", routine="ContaPagar", error_details ="" )
            
            time.sleep(3)

            if randomNumber != 0:
                Apex.setValue(browser,"P47_CATEGORIA_FINANCEIRA",randomCategoriaFinanceiraId)
                categoriaFinanceiraValue = Apex.getValue(browser,"P47_CATEGORIA_FINANCEIRA")
                if categoriaFinanceiraValue == randomCategoriaFinanceiraId:
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: categoriaFinanceira teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )

            else:
                Apex.setValue(browser,"P47_CATEGORIA_FINANCEIRA",randomText)
                categoriaFinanceiraValue = Apex.getValue(browser,"P47_CATEGORIA_FINANCEIRA")
                if categoriaFinanceiraValue == randomText:    
                    Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: previsaoPagamentoConta teve o valor inserido incorretamente valor: {categoriaFinanceiraValue}", routine="ContaPagar", error_details ="" )
    
        

            # Captura o campo de empresa e insere valores
            empresa = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_LOJA"))) 
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: empresa encontrado", routine="ContaPagar", error_details ="" )


            if randomNumber != 0:
                Apex.setValue(browser,"P47_LOJA",randomEmpresaId)
                empresaValue = Apex.getValue(browser,"P47_LOJA")
                if empresaValue ==randomEmpresaId:
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: empresa teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
            else:
                Apex.setValue(browser,"P47_LOJA",randomText)
                empresaValue = Apex.getValue(browser,"P47_LOJA")
                if empresaValue == randomText:
                    Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: empresa teve o valor inserido incorretamente valor: {empresaValue}", routine="ContaPagar", error_details ="" )        
        
            
            # captura o campo descricao e insere valores

            descricao = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_DESCRICAO"))) 
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: descricao encontrado", routine="ContaPagar", error_details ="" )

            bigText500 = GeradorDados.gerar_texto(500)

            if randomNumber != 0:
                Apex.setValue(browser,"P47_DESCRICAO",randomText)
                descricaoValue = Apex.getValue(browser,"P47_DESCRICAO")
                if descricaoValue == randomText:
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: descricao teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
            else:
                Apex.setValue(browser,"P47_DESCRICAO",bigText500)
                descricaoValue = Apex.getValue(browser,"P47_DESCRICAO")
                if descricaoValue == randomText:
                    Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: descricao teve o valor inserido incorretamente valor: {descricaoValue}", routine="ContaPagar", error_details ="" )




        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))

#END insereContaPagar(init,query)

    @staticmethod
    def detalhesContaPagar(init,query):
        randomContaId,randomFornecedorId,randomCategoriaFinanceiraId,randomEmpresaId,randomPagamentoId,randomChavePixId,randomBancoId,randomCentroCustoId,randomModeloDocumentoID = query
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
        
        random_value = round(random.uniform(1, 999999), 2)
        randomValue = FuncoesUteis.formatBrCurrency(random_value)
        randomText = GeradorDados.gerar_texto(50)
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

        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))

#END detalhesContaPagar(init,query)


    @staticmethod
    def repeticaoContaPagar(init):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
        
        randomDay = GeradorDados.randomNumberDinamic(1,30)
        randomMonth = GeradorDados.randomNumberDinamic(1,12)
        randonDayOfTheWeek = GeradorDados.randomNumberDinamic(1,7)
        randomWeeks = GeradorDados.randomNumberDinamic(0,998)
    #_________________________________________________________________
    # inicio da aba repetição de nova conta a pagar
        try:

            abaRepeticao = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#R102440341243643834_tab"))) 
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo: abaRepeticao encontrada", routine="ContaPagar", error_details ="" )        

            browser.execute_script("arguments[0].scrollIntoView(true);", abaRepeticao)        
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Scroll até abaRepeticao", routine="ContaPagar", error_details ="" )        


            abaRepeticao.click()
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo: abaRepeticao clicado", routine="ContaPagar", error_details ="" )        

            try:
                has_repeat = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#listaRepeticao")))
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Listas de repetição encontrada, já há repetição incluida", routine="ContaPagar", error_details ="" )
            except  (TimeoutException, NoSuchElementException, Exception) as e:
                has_repeat = 0
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="ERROR",
                    message="Lista de repetições não encontrada",
                    routine="ContaPagar",
                    error_details=str(e)
                )

            if has_repeat == 0:    

                btnRepeticao = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#btn_repeticao"))) 
                btnRepeticao.click()
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: btnRepeticao clicado", routine="ContaPagar", error_details ="" )

                FuncoesUteis.has_alert(init)

                
                seletor = "[title='Geração de Repetições']"
                has_frame = Components.has_frame(init,seletor)
                if has_frame:
                    randomZeroOrOne = GeradorDados.randomNumberDinamic(0,1)


                    if randomZeroOrOne == 0:
                        Apex.setValue(browser,"P71_OPCAO_FERIADO","A")
                        opcaoFeriadoValue = Apex.getValue(browser,"P71_OPCAO_FERIADO_0")
                        if opcaoFeriadoValue == "A":
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo P71_OPCAO_FERIADO: Opção feriados teve o valor : Antecipar inserido corretamente", routine="ContaPagar", error_details ="" )

                    elif randomZeroOrOne == 1 :
                        Apex.setValue(browser,"P71_OPCAO_FERIADO","P")  
                        opcaoFeriadoValue = Apex.getValue(browser,"P71_OPCAO_FERIADO_1")
                        if opcaoFeriadoValue == "P":
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo P71_OPCAO_FERIADO: Opção feriados teve o valor : Postergar Sábados e Doomingos inserido corretamente", routine="ContaPagar", error_details ="" )
                

                    if randomZeroOrOne == 0:
                        Apex.setValue(browser,"P71_OPCAO_COMPETENCIA","O")
                        opcaoCompetencia = Apex.getValue(browser,"P71_OPCAO_COMPETENCIA")
                        if opcaoCompetencia == "O":
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo P71_OPCAO_COMPETENCIA: Opção Competencia teve o valor: Ajustar Data Emissão/Competência conforme periodicidade da repetição  inserido corretamente", routine="ContaPagar", error_details ="" )
                    elif randomZeroOrOne == 1:
                        Apex.setValue(browser,"P71_OPCAO_COMPETENCIA","R")     
                        opcaoCompetencia = Apex.getValue(browser,"P71_OPCAO_COMPETENCIA")
                        if opcaoCompetencia == "R":
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo P71_OPCAO_COMPETENCIA: Opção Competencia teve o valor: Manter mesmo dia Data Emissão/Competência da conta original nas repetições inserido corretamente", routine="ContaPagar", error_details ="" )


                    randomPeriodo = GeradorDados.randomNumberDinamic(0, 2)

                    # Mapeia os valores possíveis
                    periodo_map = {
                        0: "M",
                        1: "S",
                        2: "E"
                    }

                    # Define o valor correspondente
                    valor_selecionado = periodo_map[randomPeriodo].strip().upper()        
                    Apex.setValue(browser, "P71_SELECAO_PERIODO", valor_selecionado)  


                    selecaoPeriodoValue = Apex.getValue(browser, "P71_SELECAO_PERIODO")
                    time.sleep(2)
                    
                    if selecaoPeriodoValue:
                        selecaoPeriodoValue = selecaoPeriodoValue[0].strip().upper()
                        selecaoPeriodoValue = str(selecaoPeriodoValue)

                    if selecaoPeriodoValue == valor_selecionado:
                        Log_manager.add_log(
                            application_type=env_application_type,
                            level="INFO",
                            message=f"Campo P71_OPCAO_COMPETENCIA: Seleção período teve o valor inserido corretamente valor selecionado {valor_selecionado}",
                            routine="ContaPagar",
                            error_details="")
                    else:
                        Log_manager.add_log(
                            application_type=env_application_type,
                            level="ERROR",
                            message="Falha ao definir o valor do campo : Seleção período",
                            routine="ContaPagar",
                            error_details=f"Esperado: {valor_selecionado}, Obtido: {selecaoPeriodoValue}" )


                    if selecaoPeriodoValue == "M":
                        WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P71_DIA")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P71_DIA encontrado", routine="ContaPagar", error_details ="" )

                        Apex.setValue(browser, "P71_DIA", randomDay)
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P71_DIA:Todo dia teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
                        time.sleep(1)

                        WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P71_QUANTIDADE_MES")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P71_QUANTIDADE_MES encontrado", routine="ContaPagar", error_details ="" )

                        Apex.setValue(browser, "P71_QUANTIDADE_MES", randomMonth)
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P71_QUANTIDADE_MES: Repetir por teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
                        
                        btnNovaSimulacao = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B117755939196395627")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação encontrado", routine="ContaPagar", error_details ="" )

                        btnNovaSimulacao.click()
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação clicado", routine="ContaPagar", error_details ="" )

                    elif selecaoPeriodoValue == "S":
                        WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P71_DIA_SEMANA")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P71_DIA_SEMANA encontrado", routine="ContaPagar", error_details ="" )

                        Apex.setValue(browser, "P71_DIA_SEMANA", randonDayOfTheWeek)
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P71_DIA_SEMANA:Repetir:todo(a) teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
                        time.sleep(1)

                        WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P71_QUANTIDADE_SEMANA")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P71_QUANTIDADE_SEMANA encontrado", routine="ContaPagar", error_details ="" )
                        
                        Apex.setValue(browser, "P71_QUANTIDADE_SEMANA", randomWeeks)
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P71_QUANTIDADE_SEMANA:por teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
                        
                        btnNovaSimulacao = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B117756094566395628")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação encontrado", routine="ContaPagar", error_details ="" )

                        btnNovaSimulacao.click()
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação clicado", routine="ContaPagar", error_details ="" )
                    
                    elif selecaoPeriodoValue == "E":
                        WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P71_A_CADA_DIA")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P71_A_CADA_DIA encontrado", routine="ContaPagar", error_details ="" )

                        Apex.setValue(browser, "P71_A_CADA_DIA", randomWeeks)
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P71_A_CADA_DIA:Repetir a cada teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
                        time.sleep(1)

                        WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P71_QUANTIDADE_VEZ")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P71_QUANTIDADE_VEZ encontrado", routine="ContaPagar", error_details ="" )

                        Apex.setValue(browser, "P71_QUANTIDADE_VEZ", randomWeeks)
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P71_QUANTIDADE_VEZ:por teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
                        
                        btnNovaSimulacao = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B117756106145395629")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação encontrado", routine="ContaPagar", error_details ="" )

                        btnNovaSimulacao.click()
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação clicado", routine="ContaPagar", error_details ="" )
            

                    try:

                        formError = WebDriverWait(browser,10).until(EC.visibility_of_element_located((By.CSS_SELECTOR,".a-Form-error")))
                    
                        if formError:
                            content = formError.text
                            Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Mais de um valor inserido no campo P71_OPCAO_FERIADO, error:{content}", routine="ContaPagar", error_details ="" )

                    except (TimeoutException, NoSuchElementException, Exception) as e :
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "formError não encontrado campo P71_OPCAO_FERIADO preenchido apenas com um valor", routine="ContaPagar", error_details =f"{e}" )   


                    WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".a-IRR-table")))
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Tabela Criada Simulação realizada", routine="ContaPagar", error_details ="" )


                    btnSaveIframeRepeticaoPagamento = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B112188062181997438"))) 
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão salvar da aba geração de repetições encontrado", routine="ContaPagar", error_details ="" )
            
                    btnSaveIframeRepeticaoPagamento.click()
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão salvar da aba geração de repetições clicado", routine="ContaPagar", error_details ="" )


                    FuncoesUteis.has_alert(init)

                

            
        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))

        finally:    
            browser.switch_to.default_content()

#END repeticaoContaPagar(init)

    def pagamentosContaPagar(init,query):
        randomContaId,randomFornecedorId,randomCategoriaFinanceiraId,randomEmpresaId,randomPagamentoId,randomChavePixId,randomBancoId,randomCentroCustoId,randomModeloDocumentoID = query
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
        
        random_value = round(random.uniform(1, 9999), 2)
        randomStr = FuncoesUteis.formatBrCurrency(random_value)
        randomValue = FuncoesUteis.stringToFloat(randomStr)
        randomText = GeradorDados.gerar_texto(50)
        randomNumber = GeradorDados.randomNumberDinamic(0,2)
        randomDay = GeradorDados.randomNumberDinamic(1,30)
        descontoCondicionalValue = 0
    

        today = datetime.today()
        randomDay = GeradorDados.randomNumberDinamic(0, 30)
        randomDate = today + timedelta(days=randomDay)
        finalDate = randomDate.strftime("%d/%m/%Y")

        bigText700 = GeradorDados.gerar_texto(700)




    #_________________________________________________________________
    # inicio da aba pagamento de nova conta a pagar  
        try:
            valorOriginalValue = Apex.getValue(browser,"P47_VALOR")

            # Aguarda a aba estar visível
            abaPagamento = WebDriverWait(browser, 30).until(
                EC.visibility_of_element_located((By.ID, "pagamento_tab"))
            )
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de pagamento encontrada", routine="ContaPagar", error_details ="" )


            # Garante que o elemento está na tela
            browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", abaPagamento)
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Scroll até Aba de pagamento ", routine="ContaPagar", error_details ="" )


            # Aguarda até que o elemento esteja clicável
            WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, "pagamento_tab")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de pagamento clicavel", routine="ContaPagar", error_details ="" )


            # Tenta clicar normalmente, se falhar, usa JavaScript para forçar o clique
            try:
                abaPagamento.click()
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de pagamento clicada via py", routine="ContaPagar", error_details ="" )

            except:
                browser.execute_script("arguments[0].click();", abaPagamento)
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de pagamento clicada via js", routine="ContaPagar", error_details ="" )

            if randomNumber in (0, 2):


                lancaDescontoCondicional = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#B107285263114283801"))) 
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão lança denconto condicional encontrado", routine="ContaPagar", error_details ="" )

                
                lancaDescontoCondicional.click()
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão lança denconto condicional clicado", routine="ContaPagar", error_details ="" )

                WebDriverWait(browser, 30).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "[title='Lançamento Desconto Condicional']"))) 
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Trocando para iframe Lançamento Desconto Condicional ", routine="ContaPagar", error_details ="" )

                descontoCondicional = GeradorDados.randomNumberDinamic(1, 100)
                if randomNumber == 0:
                    Apex.setValue(browser,"P220_DESCONTO",descontoCondicional)
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f" Desconto Condicional inserido {descontoCondicional} ", routine="ContaPagar", error_details ="" )

                    Apex.setValue(browser,"P220_OBSERVACAO",randomText)
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Texto de observação inserido", routine="ContaPagar", error_details ="" )


                else:
                    Apex.setValue(browser,"P220_DESCONTO",randomValue)
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f" Desconto Condicional inserido {randomValue} ", routine="ContaPagar", error_details ="" )

                    Apex.setValue(browser,"P220_OBSERVACAO",bigText700)   
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Texto 700 caracteres inserido", routine="ContaPagar", error_details ="" )

                btnSaveIframeDescontoCondicional = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B107285890923283807")))    
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão Save denconto condicional encontrado", routine="ContaPagar", error_details ="" )

                descontoCondicionalValue = FuncoesUteis.stringToFloat(Apex.getValue(browser,"P220_DESCONTO"))
                


                btnSaveIframeDescontoCondicional.click()
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão Save denconto condicional clicado", routine="ContaPagar", error_details ="" )
                
                valorOriginalFormatado = FuncoesUteis.stringToFloat(valorOriginalValue)
                novoValor = abs(valorOriginalFormatado - descontoCondicional)

                has_alert = FuncoesUteis.has_alert(init)
                if has_alert:

                    
                        Apex.setValue(browser,"P220_DESCONTO",novoValor)
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f" Desconto Condicional inserido {novoValor} ", routine="ContaPagar", error_details ="" )
                        btnSaveIframeDescontoCondicional.click()
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão Save denconto condicional clicado", routine="ContaPagar", error_details ="" )
                
                browser.switch_to.default_content()
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Voltando para o conteudo principal", routine="ContaPagar", error_details ="" )

            elif randomNumber in (1,2):
                

                novoPagamento = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B264204626044900605")))    
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão novo pagamento encontrado", routine="ContaPagar", error_details ="" )

                novoPagamento.click()
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão novo pagamento clicado", routine="ContaPagar", error_details ="" )
                
                
                WebDriverWait(browser, 30).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "#Pagamentos")))
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Trocando para iframe Pagamentos ", routine="ContaPagar", error_details ="" )
                
                valorPagamentoDividido = round((valorOriginalFormatado/3),2)
                valorDescontoDividido = round((randomValue/4),2)
                valorDescontoDividido = FuncoesUteis.formatBrCurrency(valorDescontoDividido)
                print(f'Valor do desconto a ser inserido {valorDescontoDividido}')


                if randomNumber == 0:
                    Apex.setValue(browser,"P70_CONTA_ID",randomContaId)
                    Apex.setValue(browser,"P70_FORMA_PAGAMENTO",randomPagamentoId)
                    Apex.setValue(browser,"P70_DATA_PAGAMENTO",finalDate)
                    Apex.setValue(browser,"P70_VALOR_PAGAMENTO",valorPagamentoDividido)
                    Apex.setValue(browser,"P70_DESCONTO",valorDescontoDividido)
                    Apex.setValue(browser,"P70_JUROS",randomValue)
                    Apex.setValue(browser,"P70_MULTA",randomValue)
                    Apex.setValue(browser,"P70_ACRESCIMOS",randomValue)     
                    Apex.setValue(browser,"P70_OBSERVACAO",randomText)   


                else:
                    Apex.setValue(browser,"P70_CONTA_ID",randomText)
                    Apex.setValue(browser,"P70_FORMA_PAGAMENTO",randomText)
                    Apex.setValue(browser,"P70_DATA_PAGAMENTO",randomText)
                    Apex.setValue(browser,"P70_VALOR_PAGAMENTO",randomText)
                    Apex.setValue(browser,"P70_DESCONTO",randomText)
                    Apex.setValue(browser,"P70_JUROS",randomText)
                    Apex.setValue(browser,"P70_MULTA",randomText)
                    Apex.setValue(browser,"P70_ACRESCIMOS",randomText)
                    

                descontoEditavel  = Apex.getValue(browser,"P70_DESCONTO")
                print(f"Valor desconto apos ser inserido {descontoEditavel}")
                descontoEditavelFloat = FuncoesUteis.stringToFloat(descontoEditavel)  
                print(f"Valor desconto apos ser inserido Float {descontoEditavelFloat}")

                time.sleep(1)

                jurosEditavel = Apex.getValue(browser,"P70_JUROS")
                jurosEditavelFloat = FuncoesUteis.stringToFloat(jurosEditavel)

                multaEditavel = Apex.getValue(browser,"P70_MULTA")
                multaEditavelFloat = FuncoesUteis.stringToFloat(multaEditavel)

                acrescimosEditavel = Apex.getValue(browser,"P70_ACRESCIMOS")
                acrescimosEditavelFloat = FuncoesUteis.stringToFloat(acrescimosEditavel)

                despesas = Apex.getValue(browser,"P70_DESPESAS")
                despesasFloat = FuncoesUteis.stringToFloat(despesas)
                
                valorPagamento = Apex.getValue(browser,"P70_VALOR_PAGAMENTO")
                valorPagamentoFloat = FuncoesUteis.stringToFloat(valorPagamento)

                time.sleep(1)
                
                descontoDisplay  = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P70_DESCONTO_CONTA_DISPLAY > span")))
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P70_DESCONTO_CONTA_DISPLAY  Display de desconto achado", routine="ContaPagar", error_details ="" )
                descontoDisplay =  descontoDisplay.text      
                
                
                jurosDisplay = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P70_JUROS_CONTA_DISPLAY > span")))
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P70_JUROS_CONTA_DISPLAY  Display de desconto achado", routine="ContaPagar", error_details ="" )
                jurosDisplay = jurosDisplay.text      
                
                multaDisplay = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P70_MULTA_CONTA_DISPLAY > span")))
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P70_MULTA_CONTA_DISPLAY  Display de desconto achado", routine="ContaPagar", error_details ="" )
                multaDisplay = multaDisplay.text

                acrescimosDisplay = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P70_VALOR_ACRESCIMOS_DISPLAY > span")))
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P70_VALOR_ACRESCIMOS_DISPLAY  Display de desconto achado", routine="ContaPagar", error_details ="" )
                acrescimosDisplay = acrescimosDisplay.text
            
                despesasDisplay = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P70_VALOR_DESPESA_DISPLAY > span")))
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P70_VALOR_DESPESA_DISPLAY  Display de desconto achado", routine="ContaPagar", error_details ="" )
                despesasDisplay = despesasDisplay.text
            
                saldoPagarDisplay = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P70_SALDO_DISPLAY > span")))
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P70_SALDO_DISPLAY  Display de desconto achado", routine="ContaPagar", error_details ="" )
                saldoPagarDisplay = saldoPagarDisplay.text
            
                valorOriginalDisplay = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P70_VALOR_DISPLAY")))
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P70_VALOR_DISPLAY  Display de desconto achado", routine="ContaPagar", error_details ="" )
                valorOriginalDisplay = valorOriginalDisplay.text
            
                valorTotal = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P70_VALOR_TOTAL_DISPLAY > span")))
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P70_VALOR_DISPLAY  Display de desconto achado", routine="ContaPagar", error_details ="" )
                valorTotal = valorTotal.text
            
            
                valorTotalFloat = FuncoesUteis.stringToFloat(valorTotal)
                valorOriginalDisplayFloat = FuncoesUteis.stringToFloat(valorOriginalDisplay)
                descontoDisplayFloat = FuncoesUteis.stringToFloat(descontoDisplay)

                jurosDisplayFloat = FuncoesUteis.stringToFloat(jurosDisplay)
                multaDisplayFloat = FuncoesUteis.stringToFloat(multaDisplay)
                acrescimosDisplayFloat = FuncoesUteis.stringToFloat(acrescimosDisplay)
                despesasDisplayFloat = FuncoesUteis.stringToFloat(despesasDisplay)
                saldoPagarDisplayFloat = FuncoesUteis.stringToFloat(saldoPagarDisplay)


            valorSomado =  round(abs(valorOriginalDisplayFloat - descontoDisplayFloat + jurosDisplayFloat + multaDisplayFloat + acrescimosDisplayFloat),2)

        
            # Dicionário para armazenar comparações
            valores = {
                "Desconto": ((descontoEditavelFloat + descontoCondicionalValue), descontoDisplayFloat),
                "Juros": (jurosEditavelFloat, jurosDisplayFloat),
                "Multa": (multaEditavelFloat, multaDisplayFloat),
                "Acréscimos": (acrescimosEditavelFloat, acrescimosDisplayFloat),
                "Despesas": (despesasFloat, despesasDisplayFloat),
                "Valor Total": (valorTotalFloat, valorSomado),
                "Valor Pagamento": (valorPagamentoFloat, saldoPagarDisplayFloat),
                "Valor Original": (valorOriginalValue,valorOriginalDisplayFloat)
            }

            # Verifica quais valores são diferentes
            valoresDiferentes = {chave: (v1, v2) for chave, (v1, v2) in valores.items() if v1 != v2}

            if not valoresDiferentes:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Todos valores foram inseridos corretamente ", routine="ContaPagar", error_details ="" )

            else:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = " Valores foram inseridos incorretamente  ", routine="ContaPagar", error_details ="" )

                for chave, (v1, v2) in valoresDiferentes.items():
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f" valores incorretos: - {chave}: {v1} (esperado) ≠ {v2} (atual)", routine="ContaPagar", error_details ="" )



            btnSaveIframePagamentos =  WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#btn_salvar"))) 
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão save do iframe Pagamentos encontrado", routine="ContaPagar", error_details ="" )

            btnSaveIframePagamentos.click()
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão save do iframe Pagamentos clicado", routine="ContaPagar", error_details ="" )



            browser.switch_to.default_content()
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Voltando para o conteudo principal", routine="ContaPagar", error_details ="" )
            
            has_alert = FuncoesUteis.has_alert(init)
                

            

        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))

#END pagamentosContaPagar(init,query)               

    @staticmethod
    def instrucaoPagamentoContaPagar(init,query):
        randomContaId,randomFornecedorId,randomCategoriaFinanceiraId,randomEmpresaId,randomPagamentoId,randomChavePixId,randomBancoId,randomCentroCustoId,randomModeloDocumentoID = query
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
        
        random_value = round(random.uniform(1, 999999), 2)
        randomValue = FuncoesUteis.formatBrCurrency(random_value)
        randomText = GeradorDados.gerar_texto(20)

        bigText700 = GeradorDados.gerar_texto(700)


        try:

            abaInstrucaoPagamento = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#R108405262283655634_tab")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba instrução de pagamento encontrada", routine="ContaPagar", error_details ="" )

            browser.execute_script("arguments[0].scrollIntoView(true);", abaInstrucaoPagamento)
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Sroll até Aba instrução de pagamento", routine="ContaPagar", error_details ="" )


            # Clica na aba de instrução de pagamento
            abaInstrucaoPagamento.click()
            Log_manager.add_log(application_type=env_application_type, level="INFO", message="Aba instrução de pagamento clicada", routine="ContaPagar", error_details="")

            # Gera um número aleatório para forma de pagamento
            formaPagamento = GeradorDados.randomNumberDinamic(0, 2)

            # Gera um número aleatório para DDA
            randomDda = GeradorDados.randomNumberDinamic(0, 2)
            if randomDda == 0:
                Apex.setValue(browser, "P47_DDA", "1")
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="DDA definido (DDA)", routine="ContaPagar", error_details="")

            if formaPagamento == 0:
                Apex.setValue(browser, "P47_FORMA_INSTRUCAO_PAGAMENTO_ID", 2)
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="Forma de pagamento definida como 2 (Boleto)", routine="ContaPagar", error_details="")

            elif formaPagamento == 1:
                Apex.setValue(browser, "P47_FORMA_INSTRUCAO_PAGAMENTO_ID", 3)
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="Forma de pagamento definida como 3 (PIX)", routine="ContaPagar", error_details="")
                
                # Aguarda o campo de tipo de chave PIX estar clicável
                WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#P47_PIX_TIPO_CHAVE_ID")))
                Apex.setValue(browser, "P47_PIX_TIPO_CHAVE_ID", randomChavePixId)
                Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"Tipo de chave PIX definido como {randomChavePixId}", routine="ContaPagar", error_details="")
                
                if randomChavePixId == 1:
                    cpfCnpj = GeradorDados.randomNumberDinamic(0, 1)
                    if cpfCnpj == 0:
                        Apex.setValue(browser, "P47_PIX_CHAVE", GeradorDados.gerar_cpf())
                        Log_manager.add_log(application_type=env_application_type, level="INFO", message="Chave PIX definida como CPF", routine="ContaPagar", error_details="")
                    else:
                        Apex.setValue(browser, "P47_PIX_CHAVE", GeradorDados.gerar_cnpj())
                        Log_manager.add_log(application_type=env_application_type, level="INFO", message="Chave PIX definida como CNPJ", routine="ContaPagar", error_details="")
                elif randomChavePixId == 2:
                    Apex.setValue(browser, "P47_PIX_CHAVE", GeradorDados.gerar_numero_celular())
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message="Chave PIX definida como número de celular", routine="ContaPagar", error_details="")
                elif randomChavePixId == 3:
                    Apex.setValue(browser, "P47_PIX_CHAVE", GeradorDados.gerar_email())
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message="Chave PIX definida como email", routine="ContaPagar", error_details="")
                elif randomChavePixId in (4, 5, 6):
                    Apex.setValue(browser, "P47_PIX_CHAVE", GeradorDados.gerar_chave_aleatoria())
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message="Chave PIX definida como chave aleatória", routine="ContaPagar", error_details="")

            elif formaPagamento == 2:
                Apex.setValue(browser, "P47_FORMA_INSTRUCAO_PAGAMENTO_ID", 4)
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="Forma de pagamento definida como 4 (TED)", routine="ContaPagar", error_details="")
                
                contaDestino = GeradorDados.randomNumberDinamic(0, 2)
                if contaDestino == 0:
                    Apex.setValue(browser, "P47_TED_CONTA_DESTINO_ID", 1)
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message="Conta destino definida como 1 (Corrente)", routine="ContaPagar", error_details="")
                elif contaDestino == 1:
                    Apex.setValue(browser, "P47_TED_CONTA_DESTINO_ID", 2)
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message="Conta destino definida como 2 (Poupança)", routine="ContaPagar", error_details="")
                elif contaDestino == 2:
                    Apex.setValue(browser, "P47_TED_CONTA_DESTINO_ID", 3)
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message="Conta destino definida como 3 (Pagamento)", routine="ContaPagar", error_details="")
                
                digitoConta = GeradorDados.randomNumberDinamic(0, 9)
                numeroAgencia = GeradorDados.randomNumberDinamic(0000, 9999)
                numeroConta = GeradorDados.randomNumberDinamic(0000000000, 999999999)
                nomeFavorcido = GeradorDados.gerar_nome()
                textOrNumber = GeradorDados.randomNumberDinamic(0, 1)

                if textOrNumber == 0:
                    Apex.setValue(browser, "P47_TED_BANCO_ID", randomBancoId)
                    Apex.setValue(browser, "P47_TED_AGENCIA", numeroAgencia)
                    Apex.setValue(browser, "P47_TED_CONTA", numeroConta)
                    Apex.setValue(browser, "P47_TED_CONTA_DIGITO", digitoConta)
                    Apex.setValue(browser, "P47_TED_NOME_FAVORECIDO", nomeFavorcido)
                    Apex.setValue(browser, "P47_INSTRUCAO_OBSERVACAO", randomText)
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message="Informações da conta TED preenchidas corretamente", routine="ContaPagar", error_details="")
                else:
                    Apex.setValue(browser, "P47_TED_BANCO_ID", randomBancoId)
                    Apex.setValue(browser, "P47_TED_AGENCIA", randomText)
                    Apex.setValue(browser, "P47_TED_CONTA", randomText)
                    Apex.setValue(browser, "P47_TED_CONTA_DIGITO", randomText)
                    Apex.setValue(browser, "P47_TED_NOME_FAVORECIDO", randomValue)
                    Apex.setValue(browser, "P47_INSTRUCAO_OBSERVACAO", bigText700)
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message="Informações de conta TED com texto aleatório preenchidas", routine="ContaPagar", error_details="")

                cpfCnpj2 = GeradorDados.randomNumberDinamic(0, 1)
                if cpfCnpj2 == 0:
                    Apex.setValue(browser, "P47_TED_DOCUMENTO_FAVORECIDO", GeradorDados.gerar_cpf())
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message="Documento do favorecido definido como CPF", routine="ContaPagar", error_details="")
                else:
                    Apex.setValue(browser, "P47_TED_DOCUMENTO_FAVORECIDO", GeradorDados.gerar_cnpj())
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message="Documento do favorecido definido como CNPJ", routine="ContaPagar", error_details="")
        
        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))

#END instrucaoPagamentoContaPagar(init,query)

    @staticmethod
    def despesasContaPagar(init):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
        
        random_value = round(random.uniform(1, 999999), 2)
        randomValue = FuncoesUteis.formatBrCurrency(random_value)
        randomText = GeradorDados.gerar_texto(30)
        bigText700 = GeradorDados.gerar_texto(700)
    
        try:
    
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
            



        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))

#END despesasContaPagar(init)

    @staticmethod
    def editaContaPagar(init):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")    
        dataId = "data id não encontrado"  





        try:
           
            edit = WebDriverWait(browser,120).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".fa.fa-edit")))
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Conta a pagar editavel encontrada",
                routine="ContaPagar",
                error_details=''
            )

            dataId = edit.get_attribute("data-id")
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Conta a pagar data-id capturado",
                routine="ContaPagar",
                error_details=''
            )

            edit.click()
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Conta a pagar editavel clicada. Inicio da edição da conta!",
                routine="ContaPagar",
                error_details=''
            )
         

        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))


        finally:
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"Conta a pagar {dataId} editada",
                routine="ContaPagar",
                error_details=''
            )    
#END editaContaPagar(init)

    @staticmethod
    def excluiContaPagar(init):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")    
        dataId = "data id não encontrado"  
       

        try:                  

            # Aguarda a aba estar visível
            abaPagamento = WebDriverWait(browser, 30).until(
                EC.visibility_of_element_located((By.ID, "pagamento_tab"))
            )
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de pagamento encontrada", routine="ContaPagar", error_details ="" )


            # Garante que o elemento está na tela
            browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", abaPagamento)
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Scroll até Aba de pagamento ", routine="ContaPagar", error_details ="" )


            # Aguarda até que o elemento esteja clicável
            WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, "pagamento_tab")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de pagamento clicavel", routine="ContaPagar", error_details ="" )

            abaPagamento.click()
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de pagamento clicada via py", routine="ContaPagar", error_details ="" )

            while True:
                try:
                    delete_icons = WebDriverWait(browser, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".excluirPagamento"))
                    )

                    if not delete_icons:
                        break  # Sai do loop se não houver mais ícones para excluir

                    delete_icons[0].click()  # Sempre clicamos no primeiro disponível

                    confirm_btn = WebDriverWait(browser, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".js-confirmBtn"))
                    )
                    confirm_btn.click()


                except TimeoutException:
                    break  
            btnDelete = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[name='excluirConta']")))   
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão excluir Conta Pagar encontrado", routine="ContaPagar", error_details ="" )
    
            btnDelete.click()
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão excluir Conta Pagar clicado", routine="ContaPagar", error_details ="" )

            btnConfirmDelete = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".js-confirmBtn")))   
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão confirmar exclusão Conta Pagar encontrado", routine="ContaPagar", error_details ="" )
    
            btnConfirmDelete.click()
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão confirmar exclusão Conta Pagar clicado", routine="ContaPagar", error_details ="" )

            FuncoesUteis.has_alert(init)

            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Conta a pagar {dataId} foi excluida", routine="ContaPagar", error_details ="" )


        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))

#END excluiContaPagar(init)

    @staticmethod
    def finalizaInsertContaPagar(init):
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

            FuncoesUteis.has_alert(init)
            has_alert_sucess = FuncoesUteis.has_alert_sucess(init)       

            if has_alert_sucess:
                # Captura o botão de Voltar a Contas a Pagar e clica
                voltarContaPagar =  WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#B103339792839912425"))) 
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão voltar a contas a pagar encontrado", routine="ContaPagar", error_details ="" )

                voltarContaPagar.click()
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão voltar a contas a pagar clicado", routine="ContaPagar", error_details ="" )

        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))


            


            

