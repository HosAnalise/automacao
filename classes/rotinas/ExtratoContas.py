from datetime import datetime,timedelta
import random
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.GerarDados import GeradorDados  
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components



class ExtratoContas:

    url = "exibir-extrato-das-contas"
    filterSelector = "#P76_CONTAS"
    filters = [
        "P76_CONTAS",
        "P76_DATA_INICIAL",
        "P76_DATA_FINAL",
        "P76_SITUACAO",
        "P76_VALOR_MIN",
        "P76_VALOR_MAX",
        "P76_NUMERO_DOCUMENTO",
        "P76_CATEGORIAS",
        "P76_CENTRO_CUSTO",
        "P76_ORIGEM"
    ]
    queries = {
                "queryModelodocumentoFiscal":   """
                                                        SELECT 
                                                            MODELO.DOCUMENTO_FISCAL_MODELO_ID
                                                        FROM 
                                                            ERP.DOCUMENTO_FISCAL_MODELO MODELO
                                                """,    

                "queryContaId": """
                                    SELECT CONTA.CONTA_ID  
                                    FROM ERP.CONTA
                                    JOIN ERP.CONTA_ESPECIFICACAO ON CONTA.CONTA_ID = CONTA_ESPECIFICACAO.CONTA_ID
                                    LEFT JOIN ERP.LOJA ON LOJA.LOJA_ID = CONTA_ESPECIFICACAO.LOJA_ID
                                    WHERE CONTA_ESPECIFICACAO.GRUPO_LOJA_ID = 1501
                                        AND CONTA.TIPO_CONTA_ID IN (1, 2)
                                        AND (CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IN (1) OR CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IS NULL)
                                        AND (CONTA.CONTA_ID IN (0) OR CONTA_ESPECIFICACAO.STATUS IN (1))
                                """,
                "queryContaDestinoId": """
                                    SELECT CONTA.CONTA_ID  
                                    FROM ERP.CONTA
                                    JOIN ERP.CONTA_ESPECIFICACAO ON CONTA.CONTA_ID = CONTA_ESPECIFICACAO.CONTA_ID
                                    LEFT JOIN ERP.LOJA ON LOJA.LOJA_ID = CONTA_ESPECIFICACAO.LOJA_ID
                                    WHERE CONTA_ESPECIFICACAO.GRUPO_LOJA_ID = 1501
                                        AND CONTA.TIPO_CONTA_ID IN (1, 2)
                                        AND (CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IN (1) OR CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IS NULL)
                                        AND (CONTA.CONTA_ID IN (0) OR CONTA_ESPECIFICACAO.STATUS IN (1))
                                """,                
                
                "queryFornecedorId": """
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

                "queryCategoriaFinanceira": """
                    SELECT CF.CATEGORIA_FINANCEIRA_ID  
                    FROM ERP.CATEGORIA_FINANCEIRA CF
                    LEFT JOIN ERP.CATEGORIA_FINANCEIRA_ESPECIFICACAO CFE ON CF.CATEGORIA_FINANCEIRA_ID = CFE.CATEGORIA_FINANCEIRA_ID
                    LEFT JOIN ERP.CATEGORIA_FINANCEIRA CF_PAI ON CFE.CATEGORIA_FINANCEIRA_PAI_ID = CF_PAI.CATEGORIA_FINANCEIRA_ID
                    WHERE CF.CLASSIFICACAO_CATEGORIA_FINANCEIRA_ID = 1
                        AND CFE.CATEGORIA_FINANCEIRA_PAI_ID IS NOT NULL
                        AND CFE.GRUPO_LOJA_ID = 1501
                        AND (CFE.CATEGORIA_FINANCEIRA_ID IN (0) OR CFE.STATUS = 1)
                """,


                "queryFormaPagamento": """
                    SELECT FORMA_PAGAMENTO_ID FROM ERP.FORMA_PAGAMENTO
                    WHERE
                        status = 1
                        and (grupo_loja_id = 1501 or grupo_loja_id is null)
                        AND VISIVEL = 1        
                """,


                "queryTipoChave": """
                    SELECT TIPO_CHAVE_PIX_ID 
                    FROM ERP.TIPO_CHAVE_PIX
                """,

                "queryBanco": """
                    SELECT BANCO_ID FROM ERP.BANCO
                """,
                "queryCentroCusto": """
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

                "queryCobradorId": """
                    SELECT 
                        PESSOA.PESSOA_ID
                    FROM 
                        ERP.PESSOA
                    LEFT JOIN 
                        ERP.PESSOA_CADASTRO ON PESSOA_CADASTRO.PESSOA_ID = PESSOA.PESSOA_ID
                    WHERE
                        PESSOA.GRUPO_LOJA_ID = 1501
                        AND PESSOA.STATUS = 1
                        AND (
                            PESSOA_CADASTRO.TIPO_CADASTRO_PESSOA_ID = 5
                            OR 
                            (PESSOA_CADASTRO.TIPO_CADASTRO_PESSOA_ID = 2
                            AND EXISTS (
                                SELECT 1
                                FROM ERP.PESSOA_FORNECEDOR
                                WHERE PESSOA_FORNECEDOR.PESSOA_ID = PESSOA.PESSOA_ID
                                AND NVL(PESSOA_FORNECEDOR.COBRADOR, 0) = 1
                            ))
                        )

                """,



                "queryEmpresa": """
                        SELECT LOJA_ID FROM ERP.LOJA WHERE GRUPO_LOJA_ID = 1501
                    """,
                
                "queryCliente" : """
                    SELECT
                        PESSOA.PESSOA_ID       
                    FROM 
                        ERP.PESSOA
                    WHERE 
                        GRUPO_LOJA_ID = 1501
                        AND STATUS = 1
                """
            }

    
#insere uma conta a receber resumida
    @staticmethod
    def contaReceberResumido(init, query, values):
        randomQueries = query
        browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        random_value = round(random.uniform(1, 999999), 2)
        randomValue = FuncoesUteis.formatBrCurrency(random_value)
        randomNumber = GeradorDados.randomNumberDinamic(0, 4)
        randomDay = GeradorDados.randomNumberDinamic(1, 30)

        today = datetime.today()
        randomDay = GeradorDados.randomNumberDinamic(0, 30)
        randomDate = today + timedelta(days=randomDay)
        finalDate = randomDate.strftime("%d/%m/%Y")
        todaystr = today.strftime("%d/%m/%Y")
        descricaoText500 = GeradorDados.gerar_texto(500)
        descricaoText700 = GeradorDados.gerar_texto(700)

        try:
            if not values:
                btnNovaContaReceber = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#B89274598958096047")))
                btnText = btnNovaContaReceber.text
                Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"Botão {btnText} encontrado", routine="", error_details='')
                btnNovaContaReceber.click()
                Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"Botão {btnText} clicado", routine="", error_details='')

            seletor = "[title='Cadastro de Contas a Receber Resumido']"
            has_frame = Components.has_frame(init, seletor)

            if has_frame:
                WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#P199_CONTA_ID")))
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="Elemento no iframe encontrado", routine="", error_details='')
               
                descricaoText500 = GeradorDados.gerar_texto(500)
                descricaoText700 = GeradorDados.gerar_texto(700)

                contaidValue = randomQueries['Query_queryContaId'] if randomNumber != 0 else descricaoText700
                valorValue = randomValue if randomNumber != 0 else descricaoText700
                formaRecebiementoValue = randomQueries['Query_queryFormaPagamento'] if randomNumber != 0 else descricaoText700
                clienteValue = randomQueries['Query_queryCliente'] if randomNumber != 0 else descricaoText700
                dataEmissaoValue = todaystr if randomNumber != 0 else descricaoText700
                dataRecebimentoValue = finalDate if randomNumber != 0 else descricaoText700
                categoriaFinanceiraValue = randomQueries['Query_queryCategoriaFinanceira'] if randomNumber != 0 else descricaoText700
                descricaoValue = descricaoText500 if randomNumber != 0 else descricaoText700



                apexValues = values if values else {
                    "P199_CONTA_ID": contaidValue,
                    "P199_VALOR":valorValue,
                    "P199_FORMA_RECEBIMENTO":formaRecebiementoValue,
                    "P199_PESSOA_ID":clienteValue,
                    "P199_DATA_EMISSAO":dataEmissaoValue,
                    "P199_DATA_RECEBIMENTO":dataRecebimentoValue,
                    "P199_CATEGORIA_FINANCEIRA_ID":categoriaFinanceiraValue,
                    "P199_DESCRICAO":descricaoValue
                }

                apexGetValue = {}

                # Preenche dinamicamente os campos
                for seletor, value in apexValues.items():
                    Apex.setValue(browser, seletor, value)
                    time.sleep(0.5)
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"{seletor} teve o valor {value} inserido", routine="", error_details='')

                    apexGetValue[seletor] = Apex.getValue(browser, seletor)
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"{seletor} teve o valor {apexGetValue[seletor]} encontrado", routine="", error_details='')

                # Comparando valores
                campos = {seletor: (apexGetValue[seletor], value) for seletor, value in apexValues.items()}
                FuncoesUteis.compareValues(init, campos)

                # Clicando no botão para salvar
                btnSaveExtratoContasResumido = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#save")))
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="o botão btnSaveExtratoContasResumido foi encontrado", routine="", error_details='')
                btnSaveExtratoContasResumido.click()
                Log_manager.add_log(application_type=env_application_type, level="INFO", message="o botão btnSaveExtratoContasResumido foi clicado", routine="", error_details='')

                Components.has_alert(init)
                Components.has_alert_sucess(init)

                browser.switch_to.default_content()

                if not values:
                    icon = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".a-Icon.icon-irr-no-results")))
                    if icon:
                        Log_manager.add_log(application_type=env_application_type, level="INFO", message="o ícone inicial foi encontrado, transação ocorreu corretamente", routine="", error_details='')

        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))

#END contaReceberResumido()   




    #insere uma nova transferencia 
    @staticmethod
    def novaTransferencia(init,query,contaDestino = True,staticValues=False):
        randomQueries =  query
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
        
        Query_value = round(random.uniform(1, 999999), 2)
        randomValue = FuncoesUteis.formatBrCurrency(Query_value)
        randomNumber = GeradorDados.randomNumberDinamic(0,3)

        today = datetime.today()
        todaystr = today.strftime("%d/%m/%Y")
        try:
            btnNovaTransferencia = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#novaTransferencia")))
            btnText = btnNovaTransferencia.text
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado",
                    routine="",
                    error_details=''
                )
            btnNovaTransferencia.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} clicado",
                    routine="",
                    error_details=''
                )
            seletor = "[title='Cadastro de Transferência']"
            has_frame = Components.has_frame(init,seletor)

            if has_frame:
                WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P78_CONTA_ORIGEM_ID")))
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message="Elemento no iframe encontrado",
                    routine="",
                    error_details=''
                )
                descricaoText500 = GeradorDados.gerar_texto(500)
                descricaoText700 = GeradorDados.gerar_texto(700)

                documento = GeradorDados.gerar_cpf() if randomValue != 0 else GeradorDados.gerar_chave_aleatoria()
                formaTransferenciaValue = randomQueries['Query_queryCliente'] if randomNumber != 0 else descricaoText700
                valorTransferenciaValue = randomValue if randomNumber != 0 else descricaoText700
                contaOrigemIdValue = randomQueries['Query_queryContaId'] if randomNumber != 0 else descricaoText700
                contaDestinoIdValue = staticValues["P78_CONTA_DESTINO_ID"] if isinstance(staticValues,dict) else randomQueries['Query_queryContaDestinoId'] if randomNumber != 0 else descricaoText700
                formaPagamentoValue = randomQueries['Query_queryFormaPagamento'] if randomNumber != 0 else descricaoText700
                descricaoText =  descricaoText500 if randomNumber != 0 else descricaoText700
                dataValue = todaystr if randomNumber != 0 else descricaoText700
                text = "Transferência entre Contas"

                apexValues = staticValues if isinstance(staticValues,dict) else{
                    "P78_CONTA_ORIGEM_ID":contaOrigemIdValue,
                    "P78_DATA_TRANSFERENCIA":dataValue,
                    "P78_FORMA_TRANSFERENCIA":formaTransferenciaValue,
                    "P78_NUMERO_DOCUMENTO": documento,
                    "P78_VALOR_TRANSFERENCIA":valorTransferenciaValue,
                    "P78_FORMA_PAGAMENTO":formaPagamentoValue,
                    "P78_DESCRICAO":descricaoText
                }
                apexGetValue = {}   

                for seletor,value in apexValues.items():
                    if not contaDestino and seletor == "P78_VALOR_TRANSFERENCIA":
                       
                        Log_manager.add_log(
                            application_type=env_application_type, 
                            level="INFO", 
                            message=f"Seletor {seletor} foi ignorado, pois contaDestino é False", 
                            routine="", 
                            error_details=""
                        )
                    else:    
                        WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,f"#{seletor}")))
                        Apex.setValue(browser,seletor,value)
                        Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                                message=f"{seletor} teve o valor {value} inserido", 
                                                routine="", error_details="")

                        apexGetValue[seletor] = Apex.getValue(browser,seletor)     
                        Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                                message=f"{seletor} teve o valor {apexGetValue[seletor]} encontrado", 
                                                routine="", error_details="")
                    
                if contaDestino:

                    Apex.setValue(browser,"P78_CONTA_DESTINO_ID",contaDestinoIdValue)
                    contaDestinoValue =  Apex.getValue(browser,"P78_CONTA_DESTINO_ID")

                origem =   Apex.getValue(browser,"P78_ORIGEM") 

                campos = {
                        "contaOrigemId" : (apexGetValue["P78_CONTA_ORIGEM_ID"],contaOrigemIdValue),
                        "contaDestinoId" : (contaDestinoValue,contaDestinoIdValue),
                        "dataTransferencia": (apexGetValue["P78_DATA_TRANSFERENCIA"],dataValue),
                        "formaTransferencia":(apexGetValue["P78_FORMA_TRANSFERENCIA"],formaTransferenciaValue),
                        "numeroDocumento":(apexGetValue["P78_NUMERO_DOCUMENTO"],documento),
                        "valorTransferencia" : (apexGetValue["P78_VALOR_TRANSFERENCIA"],randomValue),
                        "formaPagamento": (apexGetValue["P78_FORMA_PAGAMENTO"],formaPagamentoValue),
                        "origem":(origem,text),
                        "descricao": (apexGetValue["P78_DESCRICAO"],descricaoText)
                }
                
                FuncoesUteis.compareValues(init,campos)

                btnSaveCadastroTransferenciaResumido = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B89271388586096015")))
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="o botão btnSaveCadastroTransferenciaResumido foi encontrado",
                        routine="",
                        error_details=''
                    )
                
                btnSaveCadastroTransferenciaResumido.click()
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="o botão btnSaveCadastroTransferenciaResumido foi clicado",
                        routine="",
                        error_details=''
                    )
                
                Components.has_alert(init)
                Components.has_alert_sucess(init),

                browser.switch_to.default_content()
              

                icon = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".a-Icon.icon-irr-no-results")))
                if icon:
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="o icone inicial foi encontrado transação ocorreu corretamente",
                        routine="",
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

#END novaTransferencia()


#Nova conta a pagar resumida 
    @staticmethod
    def contaPagarResumida(init,query):
        randomQuery = query
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
        
        Query_value = round(random.uniform(1, 9999), 2)
        randomValue = FuncoesUteis.formatBrCurrency(Query_value)
        randomNumber = GeradorDados.randomNumberDinamic(0,5)

        today = datetime.today()
        randomDay = GeradorDados.randomNumberDinamic(0, 30)
        randomDate = today + timedelta(days=randomDay)
        finalDate = randomDate.strftime("%d/%m/%Y")
        todaystr = today.strftime("%d/%m/%Y") 
        randomText = GeradorDados.gerar_texto(30)

        try:
            btnNovaContaPagar = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B89271014725096012")))
            btnText = btnNovaContaPagar.text
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado",
                    routine="",
                    error_details=''
                )
            btnNovaContaPagar.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} clicado",
                    routine="",
                    error_details=''
                )
            seletor = "[title='Cadastro de Contas a Pagar Resumido']"
            has_frame = Components.has_frame(init,seletor)

            if has_frame:
                WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P194_CONTA_ID")))

                contaId = randomQuery["Query_queryContaId"] if randomNumber != 0 else randomText
                valor = randomValue if randomNumber != 0 else randomText
                formaPagamento = randomQuery["Query_queryFormaPagamento"] if randomNumber != 0 else randomText
                fornecedorId = randomQuery["Query_queryFornecedorId"] if randomNumber != 0 else randomText
                dataEmissao = todaystr if randomNumber != 0 else finalDate 
                categoriaFinanceira = randomQuery["Query_queryCategoriaFinanceira"] if randomNumber != 0 else randomText
                conferido = GeradorDados.randomNumberDinamic(0,1) if randomNumber != 0 else 3 
                descricao = randomText if randomNumber != 0 else GeradorDados.gerar_texto(500)
                numeroDocumento = GeradorDados.gerar_cpf() if randomNumber != 0 else GeradorDados.gerar_texto(500)               

                
                apexValues = {
                    "P194_CONTA_ID":contaId,
                    "P194_VALOR":valor,
                    "P194_FORMA_PAGAMENTO":formaPagamento,
                    "P194_PESSOA_ID":fornecedorId,
                    "P194_DATA_EMISSAO":dataEmissao,
                    "P194_DATA_PAGAMENTO":dataEmissao,
                    "P194_CATEGORIA_FINANCEIRA_ID":categoriaFinanceira,
                    "P194_CONFERIDO":conferido,
                    "P194_DESCRICAO":descricao,
                    "P194_NUMERO_DOCUMENTO": numeroDocumento
                }

                apexGetValue = {}   

                for seletor,value in apexValues.items():
                    WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,f"#{seletor}")))
                    Apex.setValue(browser,seletor,value)
                    Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                            message=f"{seletor} teve o valor {value} inserido", 
                                            routine="", error_details="")

                    apexGetValue[seletor] = Apex.getValue(browser,seletor)     
                    Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                            message=f"{seletor} teve o valor {apexGetValue[seletor]} encontrado", 
                                            routine="", error_details="")



                campos = {
                        "contaO"
                        "rigemId" : (apexGetValue["P194_CONTA_ID"],contaId),
                        "valorContaPagar" : (apexGetValue["P78_VALOR_ContaPagar"],randomValue),
                        "formaPagamento":(apexGetValue["P194_FORMA_PAGAMENTO"],formaPagamento),
                        "FavorecidoFornecedor":(apexGetValue["P194_PESSOA_ID"],fornecedorId),
                        "dataEmissao": (apexGetValue["P194_DATA_EMISSAO"],dataEmissao),
                        "dataPagamento": (apexGetValue["P194_DATA_PAGAMENTO"],dataEmissao),
                        "categoriaFinanceira":(apexGetValue["P194_CATEGORIA_FINANCEIRA_ID"],categoriaFinanceira),
                        "conferido":(apexGetValue["P194_CONFERIDO"],conferido),
                        "descricao": (apexGetValue["P194_DESCRICAO"],descricao),
                        "numeroDocumento":(apexGetValue["P194_NUMERO_DOCUMENTO"],numeroDocumento),
                        
                }
                
                FuncoesUteis.compareValues(init,campos)

                
                browser.switch_to.default_content()
              

                icon = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,".a-Icon.icon-irr-no-results")))
                if icon:
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="o icone inicial foi encontrado transação ocorreu corretamente",
                        routine="",
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

# END contaPagarResumida(init)


# Nova conciliação bancaria
    @staticmethod
    def conciliacaoBancaria(init):
        randomQuery = randomQuery(init)
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
        

        try:
            btnConciliacaoBancaria = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B120530734977149415")))
            btnText = btnConciliacaoBancaria.text

            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado",
                    routine="",
                    error_details=''
                )
            btnConciliacaoBancaria.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} clicado",
                    routine="",
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

# END conciliacaoBancaria(init)               


# Gerar Relatoria de extrato de contas
    @staticmethod
    def gerarRelatorio(init,pdfOrExcel):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")            


        try:    

            btnGerarRelatorio = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B131918532644441921")))
            btnText = btnGerarRelatorio.text
            
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado",
                    routine="",
                    error_details=''
                )
            btnGerarRelatorio.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} clicado",
                    routine="",
                    error_details=''
                )
            
            seletor = "[title='Gerar Relatório Extrato de Contas']"
            has_frame = Components.has_frame(init,seletor)

            if has_frame:
                btnGerarPdf = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".t-Cards-item.gerarPDF")))
                btnGerarExcel = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".t-Cards-item.gerarXLSX")))

                if pdfOrExcel:
                    btnText = btnGerarPdf.text
                    
                    Log_manager.add_log(
                            application_type=env_application_type,
                            level="INFO",
                            message=f"Botão {btnText} encontrado",
                            routine="",
                            error_details=''
                        )
                    btnGerarPdf.click()
                    Log_manager.add_log(
                            application_type=env_application_type,
                            level="INFO",
                            message=f"Botão {btnText} clicado",
                            routine="",
                            error_details=''
                        )
                else:
                    btnText = btnGerarExcel.text
                    
                    Log_manager.add_log(
                            application_type=env_application_type,
                            level="INFO",
                            message=f"Botão {btnText} encontrado",
                            routine="",
                            error_details=''
                        )
                    btnGerarExcel.click()
                    Log_manager.add_log(
                            application_type=env_application_type,
                            level="INFO",
                            message=f"Botão {btnText} clicado",
                            routine="",
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

#END geraRelatorio(init,pdfOrExcel)


#Realiza multiplas ações em varios extratos diferentes

    @staticmethod
    def multipleActions(init,conciliaDesconcilia,checkAll):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
        
      

        try:

            if checkAll:
                btnMultiplosCheckBoxes = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".form-check-input.checkAll")))
                btnText = btnMultiplosCheckBoxes.text
                
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} encontrado",
                        routine="",
                        error_details=''
                    )
                btnMultiplosCheckBoxes.click()
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} clicado",
                        routine="",
                        error_details=''
                    )
            else:
                btnCheckBox = WebDriverWait(browser,30).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,".form-check-input")))  
                checkBoxLength = len(btnCheckBox)

                if checkBoxLength > 2:
                    randomIndex, randomIndex2 = random.sample(range(checkBoxLength), 2)
                    btnCheckBox[randomIndex].click()
                    btnCheckBox[randomIndex2].click()
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="CheckBoxes Clicados",
                        routine="",
                        error_details=''
                    )
                else:
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="Não há checkboxes suficientes para clicar",
                        routine="",
                        error_details=''
                    )
            
            if btnMultiplosCheckBoxes:
                btnMultiplasAcoes = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".fa.fa-clipboard-edit.fa-2x")))
                btnText = btnMultiplasAcoes.text
                
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} encontrado",
                        routine="",
                        error_details=''
                    )
                btnMultiplasAcoes.click()
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} clicado",
                        routine="",
                        error_details=''
                    )
            
                seletor = "[title='Ações Múltiplos Itens']"
                has_frame = Components.has_frame(init,seletor)

                if has_frame:
                    btnConciliarItens = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".t-Cards-item.conciliar")))
                    btnDesconciliarItens = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".t-Cards-item.desconciliar")))

                    if conciliaDesconcilia:
                        btnText = btnConciliarItens.text
                        
                        Log_manager.add_log(
                                application_type=env_application_type,
                                level="INFO",
                                message=f"Botão {btnText} encontrado",
                                routine="",
                                error_details=''
                            )
                        btnConciliarItens.click()
                        Log_manager.add_log(
                                application_type=env_application_type,
                                level="INFO",
                                message=f"Botão {btnText} clicado",
                                routine="",
                                error_details=''
                            )
                        WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,".conciliacao.conciliado")))
                        Log_manager.add_log(
                                application_type=env_application_type,
                                level="INFO",
                                message="Campo Conciliado encontrado",
                                routine="",
                                error_details=''
                            )
                        

                    else:
                        btnText = btnDesconciliarItens.text
                        
                        Log_manager.add_log(
                                application_type=env_application_type,
                                level="INFO",
                                message=f"Botão {btnText} encontrado",
                                routine="",
                                error_details=''
                            )
                        btnDesconciliarItens.click()
                        Log_manager.add_log(
                                application_type=env_application_type,
                                level="INFO",
                                message=f"Botão {btnText} clicado",
                                routine="",
                                error_details=''
                            )
                        WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,".conciliacao.nao-conciliado")))
                        Log_manager.add_log(
                                application_type=env_application_type,
                                level="INFO",
                                message="Campo Não Conciliado encontrado",
                                routine="",
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

#END multipleActions(init,conciliaDesconcilia)

# Icone de mais informações
    @staticmethod
    def moreInfo(init):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
        
      

        try:
            btnMaisInformacoes = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".fa.fa-info-circle-o.icon-color")))
            btnText = btnMaisInformacoes.text
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado",
                    routine="",
                    error_details=''
                )
            
            # Garante que o elemento está na tela
            browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", btnMaisInformacoes)
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Scroll até {btnText} ", routine="", error_details ="" )
            
            btnMaisInformacoes.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} clicado",
                    routine="",
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
    
# END moreInfo(init)


    @staticmethod
    def zerarFiltros(init,showHide,apexValues):

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")      
      
        try:

            seletor = "#P76_CONTAS" if showHide  else ""
            FuncoesUteis.showHideFilter(init,seletor,showHide)

            if apexValues and isinstance(apexValues,dict):                

                FuncoesUteis.aplyFilter(init,apexValues)

                has_edit = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".fa.fa-edit.icon-color.edit")))

                if has_edit:
                    btnZerarFiltros = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B17322433979317014")))
                    btnText = btnZerarFiltros.text
                    Log_manager.add_log(
                            application_type=env_application_type,
                            level="INFO",
                            message=f"Botão {btnText} encontrado",
                            routine="",
                            error_details=''
                        )
                    
                    btnZerarFiltros.click()
                    Log_manager.add_log(
                            application_type=env_application_type,
                            level="INFO",
                            message=f"Botão {btnText} clicado",
                            routine="",
                            error_details=''
                        )
                    
                    apexGetValues = {
                    0:"P76_SITUACAO",
                    1:"P76_VALOR_MIN",
                    2:"P76_VALOR_MAX",
                    3:"P76_CATEGORIAS",
                    4:"P76_CENTRO_CUSTO",
                    5:"P76_ORIGEM"

                    }

                    for key,seletor in apexGetValues.items():
                        WebDriverWait(browser,30).until(EC.presence_of_element_located((By.CSS_SELECTOR,f"#{seletor}")))
                        value = Apex.getValue(browser,seletor)
                        Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                                message=f"{seletor} teve o valor {value} encontrado", 
                                                routine="", error_details="")
                        if not value or value == ['0']:
                            Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                                message=f"{seletor} foi zerado", 
                                                routine="", error_details="")              

        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))

#END zerarFiltros(init,showHide,apexValues)                



    @staticmethod
    def conciliarDesconciliar(init,conciliaDesconcilia):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")      
      
        try:
            has_edit = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".fa.fa-edit.icon-color.edit")))
            if has_edit:

                seletor = ".conciliacao.nao-conciliado" if conciliaDesconcilia  else ".conciliacao.conciliado"
                seletorTeste =  ".conciliacao.conciliado" if conciliaDesconcilia else ".conciliacao.nao-conciliado"
                

                btnConciliar = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,seletor)))
                btnText = btnConciliar.text
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} encontrado",
                        routine="",
                        error_details=''
                    )
                
                actions = ActionChains(browser)
                actions.double_click(btnConciliar).perform()
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} clicado",
                        routine="",
                        error_details=''
                    )
                
                btnDesconciliar = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,seletorTeste)))
                btnText = btnDesconciliar.text

                if btnText == "Conciliado":
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} encontrado, conciliação/Desconciliacao realizada com sucesso",
                        routine="",
                        error_details=''
                    )

        
        except TimeoutException as e:
            Log_manager.add_log(
                application_type=env_application_type,
            level="ERROR",
            message="Erro: Tempo limite excedido ao acessar a página",
            routine="",
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
                        routine="",
                        application_type=env_application_type, 
                        error_details=str(e)
                )
            else:
                Log_manager.add_log(
                    level="ERROR", 
                    message="Falha ao salvar screenshot", 
                    routine="",
                    application_type=env_application_type, 
                    error_details=str(e)
                )

        except NoSuchElementException as e:
            Log_manager.add_log(
                application_type=env_application_type,
                level="ERROR",
                message="Erro: Elemento não encontrado na página",
                routine="",
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
                        routine="",
                        application_type=env_application_type, 
                        error_details=str(e)
                )
            else:
                Log_manager.add_log(
                    level="ERROR", 
                    message="Falha ao salvar screenshot", 
                    routine="",
                    application_type=env_application_type, 
                    error_details=str(e)
                )

        except Exception as e:  # Captura qualquer outro erro inesperado
            Log_manager.add_log(
                application_type=env_application_type,
                level="ERROR",
                message="Erro desconhecido ao acessar a página",
                routine="",
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
                        routine="",
                        application_type=env_application_type, 
                        error_details=str(e)
                )
            else:
                Log_manager.add_log(
                    level="ERROR", 
                    message="Falha ao salvar screenshot", 
                    routine="",
                    application_type=env_application_type, 
                    error_details=str(e)
                )
#END conciliarDesconciliar(init,conciliaDesconcilia)

    @staticmethod
    def editaExtratoConta(init):
        
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")    
        dataId = "data id não encontrado"  
        try:
           
            edit = WebDriverWait(browser,120).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".fa.fa-edit")))
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Extrato de Conta editavel encontrada",
                routine="ContaPagar",
                error_details=''
            )

            dataId = edit.get_attribute("data-id")
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Extrato de Conta data-id capturado",
                routine="ContaPagar",
                error_details=''
            )

            edit.click()
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Extrato de Conta editavel clicada. Inicio da edição da conta!",
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
                message=f"Extrato de Conta {dataId} editada",
                routine="ContaPagar",
                error_details=''
            )    
#END editaExtratoConta(init)