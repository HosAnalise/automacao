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



class ContaReceber:
    url="contas-a-receber"
    filterSelector="#P84_SELETOR_LOJA"
    filters =[
        "P84_SELETOR_LOJA",
        "P84_TIPO_PERIODO",
        "P84_DATA_INICIAL",
        "P84_DATA_FINAL",
        "P84_SITUACAO",
        "P84_NUMERO_DOCUMENTO",
        "P84_NUMERO_PEDIDO",
        "P84_CONTA",
        "P84_CENTRO_CUSTO",
        "P84_CATEGORIA",
        "P84_CLIENTE",
        "P84_VALOR_INICIAL",
        "P84_VALOR_FINAL",
        "P84_ORIGEM",
        "P84_VENDA_ORIGEM",
        "P84_CONVENIO",
        "P84_NR_CONTA",
        "P84_RECEBIDO_EM",
        "P84_TIPO_COBRANCA",
        "P84_COBRADOR",
        "P84_CONTEM_BOLETO"
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

      


    
    @staticmethod
    def insereContaReceber(init,query,staticValues = False):
        """
        Função para inserir uma conta a receber no sistema.

        Parâmetros:
        init: Uma lista contendo objetos necessários para a execução da automação. 
            Os itens desta lista incluem o navegador (browser), o login, o gerenciador de logs (Log_manager), 
            a função para obter ambiente (get_ambiente), variáveis de ambiente (env_vars), 
            seletor de ambiente, caminho para screenshots e conexão com o banco de dados Oracle.
        
        query: Dicionário contendo consultas aleatórias utilizadas para preencher campos da conta a receber.

        Retorna:
        recebidovalue: O valor do recebimento inserido ou calculado durante a execução.
        """

        try:

            browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
            randomQueries =  query
            getEnv = env_vars
            env_application_type = getEnv.get("WEB")
            
            urlContain = "conta-a-receber"
            has_contaReceber = Components.url_contains(init,urlContain)
           

            if not has_contaReceber:
                Components.btnClick(init,"#B392477272658547904")
                
            has_receipt = Apex.getValue(browser,"P85_RECEBIDO") 
                        
            randomValue = round(random.uniform(1, 999999), 2)
            randomText = GeradorDados.gerar_texto(20)
            randomNumber = GeradorDados.randomNumberDinamic(0,4)


            today = datetime.today()
            randomDayVencimento = GeradorDados.randomNumberDinamic(1,30)
            randomDatePrevisao = today + timedelta(days=randomDayVencimento)
            randomDayPrevisao = GeradorDados.randomNumberDinamic(0, 30)
            randomDatePrevisao = today + timedelta(days=randomDayPrevisao)
            dataVencimento = randomDatePrevisao.strftime("%d/%m/%Y")
            dataPrevisao =  randomDatePrevisao.strftime("%d/%m/%Y")

            zeroOrOne = GeradorDados.randomNumberDinamic(0,1)
            bigText500 = GeradorDados.gerar_texto(500)



            recebidovalue = has_receipt if has_contaReceber  else 0 if randomNumber != 0 else zeroOrOne if randomNumber == 4 else 1
            valorValue = randomValue if randomNumber != 0 else randomText
            contaIdValue = randomQueries["Query_queryContaId"] if randomNumber != 0 else randomText
            pessoaClienteId = randomQueries["Query_queryCliente"] if randomNumber != 0 else randomText
            dataVencimentoValue = dataVencimento if randomNumber != 0 else randomText
            dataPrevisaoRecebimento = dataPrevisao if randomNumber != 0 else randomText
            categoriaFinanceiraValue  = randomQueries["Query_queryCategoriaFinanceira"]
            lojaIdValue = randomQueries["Query_queryEmpresa"] if randomNumber != 0 else randomText
            descricaoValue = randomText if randomNumber != 0 else bigText500


            apexValues = staticValues if isinstance(staticValues,dict) else {
                "P85_RECEBIDO":recebidovalue,
                "P85_VALOR" : valorValue,
                "P85_CONTA_ID":contaIdValue,
                "P85_PESSOA_CLIENTE_ID":pessoaClienteId,
                "P85_DATA_VENCIMENTO":dataVencimentoValue,
                "P85_DATA_PREVISAO_RECEBIMENTO":dataPrevisaoRecebimento,
                "P85_CATEGORIA_FINANCEIRA":categoriaFinanceiraValue,
                "P85_LOJA": lojaIdValue ,
                "P85_DESCRICAO":descricaoValue
            }

           
            for seletor, value in apexValues.items():
                WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"#{seletor}")))
                Apex.setValue(browser,seletor,value)
                Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                                message=f"{seletor} teve o valor {value} inserido", 
                                                routine="ContaReceber", error_details="")
                
                
            campos = FuncoesUteis.prepareToCompareValues(init,apexValues)
            FuncoesUteis.compareValues(init,campos)



            

        except TimeoutException as e:
            Log_manager.add_log(
                application_type=env_application_type,
                level="ERROR",
                message="Erro: Tempo limite excedido ao acessar a página",
                routine="ContaReceber",
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
                routine="ContaReceber",
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
                routine="ContaReceber",
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

        finally:
            return recebidovalue        
#END insereContaReceber(init,query)




    @staticmethod
    def detalhesContaReceber(init,query,staticValues = False):
        """
        Função para preencher os detalhes de uma conta a receber no sistema.

        Parâmetros:
        init: Lista contendo objetos necessários para a execução da automação. 
            Os itens dessa lista incluem o navegador (browser), login, gerenciador de logs (Log_manager), 
            função para obter o ambiente (get_ambiente), variáveis de ambiente (env_vars), 
            seletor de ambiente, caminho para salvar screenshots e conexão com o banco de dados Oracle.
        
        query: Dicionário contendo consultas aleatórias que são usadas para preencher os campos da conta a receber.

       
        """
        randomQueries = query
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
        
        Query_value = round(random.uniform(1, 999999), 2)
        randomValue = FuncoesUteis.formatBrCurrency(Query_value)
        randomText = GeradorDados.gerar_texto(20)
        randomNumber = GeradorDados.randomNumberDinamic(0,4)
        randomDay = GeradorDados.randomNumberDinamic(1,30)
    
        today = datetime.today()
        todayStr = today.strftime("%d/%m/%Y")
        randomDay = GeradorDados.randomNumberDinamic(0, 30)
        randomDate = today + timedelta(days=randomDay)
        finalDate = randomDate.strftime("%d/%m/%Y")
        sevenDaysAgo = today - timedelta(days=7)
        sevenDaysAgoStr = sevenDaysAgo.strftime("%d/%m/%Y")

        bigText700 = GeradorDados.gerar_texto(700)
        bigText500 = GeradorDados.gerar_texto(700)

    




        try:

            cobrador = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#P85_COBRADOR")))
            browser.execute_script("arguments[0].scrollIntoView(true);", cobrador)
            
            dataEmissao = todayStr if randomNumber != 0 else finalDate
            dataRegistro = sevenDaysAgoStr if randomNumber != 0 else todayStr if randomNumber == 4 else finalDate
            centroLucro = randomQueries["Query_queryCentroCusto"] if randomNumber != 0 else randomText
            numeroPedido = GeradorDados.randomNumberDinamic(100000,999999) if randomNumber != 0 else randomText
            tipoDocumento = randomQueries["Query_queryModelodocumentoFiscal"] if randomNumber != 0 else randomText
            numeroDocumento = GeradorDados.gerar_cpf() if randomNumber != 0 else GeradorDados.gerar_cnpj() if randomNumber == 4 else randomText 
            chaveNfe = GeradorDados.gerar_chave_nfe() if randomNumber != 0 else bigText500
            tipoCobranca = GeradorDados.randomNumberDinamic(1,2) if randomNumber != 0 else randomText
            cobrador = randomQueries["Query_queryCobradorId"] if randomNumber != 0 else randomText
            observacao = randomText if randomNumber != 0 else bigText700


            apexValues = staticValues if isinstance(staticValues,dict) else {
                "P85_DATA_EMISSAO":dataEmissao,
                "P85_DATA_REGISTRO":dataRegistro,
                "P85_CENTRO_DE_CUSTO":centroLucro,
                "P85_NUMERO_PEDIDO":numeroPedido,
                "P85_DOCUMENTO_FISCAL_MODELO_ID":tipoDocumento,
                "P85_NUMERO_DOCUMENTO":numeroDocumento,
                "P85_CHAVE_NFE":chaveNfe,
                "P85_TIPO_COBRANCA":tipoCobranca,
                "P85_COBRADOR":cobrador,
                "P85_OBSERVACAO":observacao,
            }
            

            campos = FuncoesUteis.prepareToCompareValues(init,apexValues)
            FuncoesUteis.compareValues(init,campos)
                
                





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
#END detalhesContaReceber(init,query)


    @staticmethod
    def repeticaoContaReceber(init):
        """
        Função para automatizar a criação de uma repetição de conta a receber em uma aplicação web utilizando Selenium.

        Esta função realiza as seguintes ações:
        1. Acessa a aba de repetição de nova conta a pagar e a interage.
        2. Verifica se já existe uma repetição cadastrada.
        3. Caso não exista, preenche os campos para gerar uma nova repetição, escolhendo valores aleatórios para a periodicidade e outras configurações.
        4. Realiza validações para garantir que os valores inseridos nos campos estão corretos.
        5. Caso ocorra algum erro (ex: tempo de espera excedido ou elemento não encontrado), a função captura e registra o erro, além de salvar uma captura de tela do erro.

        Parâmetros:
        - init (tuple): Tupla contendo os seguintes objetos necessários para o funcionamento da função:
            1. browser (WebDriver): Instância do Selenium WebDriver.
            2. login (str): Credenciais de login (não utilizado diretamente na função).
            3. Log_manager (LogManager): Instância para registrar logs.
            4. get_ambiente (function): Função para obter o ambiente.
            5. env_vars (dict): Dicionário contendo as variáveis de ambiente.
            6. seletor_ambiente (str): Seletor para identificar o ambiente (não utilizado diretamente na função).
            7. screenshots (str): Caminho onde as capturas de tela serão salvas.
            8. oracle_db_connection (object): Conexão com o banco de dados Oracle (não utilizado diretamente na função).

        
        Exceções:
        - TimeoutException: Lançada quando o tempo de espera para encontrar um elemento excede o limite.
        - NoSuchElementException: Lançada quando o elemento esperado não é encontrado na página.
        - Exception: Captura qualquer outro erro inesperado.
        """

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

            abaRepeticao = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#R221082137306428338_tab"))) 
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: aba Repeticao encontrado", routine="ContaReceber", error_details ="" )        

            browser.execute_script("arguments[0].scrollIntoView(true);", abaRepeticao)        
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Scrol até aba Repeticao", routine="ContaReceber", error_details ="" )        

            if abaRepeticao:
                abaRepeticao.click()
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: aba Repeticao clicado", routine="ContaReceber", error_details ="" )        


            try:
                has_repeat = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#listaRepeticao")))
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Listas de repetição encontrada, já há repetição incluida", routine="ContaReceber", error_details ="" )
            except  (TimeoutException, NoSuchElementException, Exception) as e:
                has_repeat = 0
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="ERROR",
                    message="Lista de repetições não encontrada",
                    routine="ContaReceber",
                    error_details=str(e)
                )
                
            if has_repeat == 0: 

                btnRepeticao = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[name='repeticao']"))) 
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: btnRepeticao encontrado", routine="ContaReceber", error_details ="" )

                if btnRepeticao:

                    btnRepeticao.click()
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: btnRepeticao clicado", routine="ContaReceber", error_details ="" )
                    
                    Components.has_alert(init)
                    Components.has_alert_sucess(init)

                    seletor = "#contaReceberRepeticao"
                    has_frame = Components.has_frame(init,seletor)

                    if has_frame:

                        randomZeroOrOne = GeradorDados.randomNumberDinamic(0,1)                                           

                        if randomZeroOrOne == 0:
                            Apex.setValue(browser,"P91_OPCAO_FERIADO","A")
                            opcaoFeriadoValue = Apex.getValue(browser,"P91_OPCAO_FERIADO_0")
                            if opcaoFeriadoValue == "A":
                                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo P91_OPCAO_FERIADO: Opção feriados teve o valor : Antecipar inserido corretamente", routine="ContaReceber", error_details ="" )

                        elif randomZeroOrOne == 1 :
                            Apex.setValue(browser,"P91_OPCAO_FERIADO","P")  
                            opcaoFeriadoValue = Apex.getValue(browser,"P91_OPCAO_FERIADO_1")
                            if opcaoFeriadoValue == "P":
                                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo P91_OPCAO_FERIADO: Opção feriados teve o valor : Postergar Sábados e Doomingos inserido corretamente", routine="ContaReceber", error_details ="" )
                    

                        if randomZeroOrOne == 0:
                            Apex.setValue(browser,"P91_OPCAO_COMPETENCIA","O")
                            opcaoCompetencia = Apex.getValue(browser,"P91_OPCAO_COMPETENCIA")
                            if opcaoCompetencia == "O":
                                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo P91_OPCAO_COMPETENCIA: Opção Competencia teve o valor: Ajustar Data Emissão/Competência conforme periodicidade da repetição  inserido corretamente", routine="ContaReceber", error_details ="" )
                        elif randomZeroOrOne == 1:
                            Apex.setValue(browser,"P91_OPCAO_COMPETENCIA","R")     
                            opcaoCompetencia = Apex.getValue(browser,"P91_OPCAO_COMPETENCIA")
                            if opcaoCompetencia == "R":
                                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo P91_OPCAO_COMPETENCIA: Opção Competencia teve o valor: Manter mesmo dia Data Emissão/Competência da conta original nas repetições inserido corretamente", routine="ContaReceber", error_details ="" )


                        randomPeriodo = GeradorDados.randomNumberDinamic(0, 2)

                        # Mapeia os valores possíveis
                        periodo_map = {
                            0: "M",
                            1: "S",
                            2: "E"
                        }

                        # Define o valor correspondente
                        valor_selecionado = periodo_map[randomPeriodo].strip().upper()        
                        Apex.setValue(browser, "P91_SELECAO_PERIODO", valor_selecionado)  


                        selecaoPeriodoValue = Apex.getValue(browser, "P91_SELECAO_PERIODO")
                        time.sleep(2)
                        
                        if selecaoPeriodoValue:
                            selecaoPeriodoValue = selecaoPeriodoValue[0].strip().upper()
                            selecaoPeriodoValue = str(selecaoPeriodoValue)

                        if selecaoPeriodoValue == valor_selecionado:
                            Log_manager.add_log(
                                application_type=env_application_type,
                                level="INFO",
                                message=f"Campo P91_OPCAO_COMPETENCIA: Seleção período teve o valor inserido corretamente valor selecionado {valor_selecionado}",
                                routine="ContaReceber",
                                error_details="")
                        else:
                            Log_manager.add_log(
                                application_type=env_application_type,
                                level="ERROR",
                                message="Falha ao definir o valor do campo : Seleção período",
                                routine="ContaReceber",
                                error_details=f"Esperado: {valor_selecionado}, Obtido: {selecaoPeriodoValue}" )


                        if selecaoPeriodoValue == "M":
                            WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P91_DIA")))
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P91_DIA encontrado", routine="ContaReceber", error_details ="" )

                            Apex.setValue(browser, "P91_DIA", randomDay)
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P91_DIA:Todo dia teve o valor inserido corretamente", routine="ContaReceber", error_details ="" )
                            time.sleep(1)

                            WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P91_QUANTIDADE_MES")))
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P91_QUANTIDADE_MES encontrado", routine="ContaReceber", error_details ="" )

                            Apex.setValue(browser, "P91_QUANTIDADE_MES", randomMonth)
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P91_QUANTIDADE_MES: Repetir por teve o valor inserido corretamente", routine="ContaReceber", error_details ="" )
                            
                            btnNovaSimulacao = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B119202079299682336")))
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação encontrado", routine="ContaReceber", error_details ="" )

                            btnNovaSimulacao.click()
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação clicado", routine="ContaReceber", error_details ="" )

                        elif selecaoPeriodoValue == "S":
                            WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P91_DIA_SEMANA")))
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P91_DIA_SEMANA encontrado", routine="ContaReceber", error_details ="" )

                            Apex.setValue(browser, "P91_DIA_SEMANA", randonDayOfTheWeek)
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P91_DIA_SEMANA:Repetir:todo(a) teve o valor inserido corretamente", routine="ContaReceber", error_details ="" )
                            time.sleep(1)

                            WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P91_QUANTIDADE_SEMANA")))
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P91_QUANTIDADE_SEMANA encontrado", routine="ContaReceber", error_details ="" )
                            
                            Apex.setValue(browser, "P91_QUANTIDADE_SEMANA", randomWeeks)
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P91_QUANTIDADE_SEMANA:por teve o valor inserido corretamente", routine="ContaReceber", error_details ="" )
                            
                            btnNovaSimulacao = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B119200508165682334")))
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação encontrado", routine="ContaReceber", error_details ="" )

                            btnNovaSimulacao.click()
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação clicado", routine="ContaReceber", error_details ="" )
                        
                        elif selecaoPeriodoValue == "E":
                            WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P91_A_CADA_DIA")))
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P91_A_CADA_DIA encontrado", routine="ContaReceber", error_details ="" )

                            Apex.setValue(browser, "P91_A_CADA_DIA", randomWeeks)
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P91_A_CADA_DIA :Repetir a cada teve o valor inserido corretamente", routine="ContaReceber", error_details ="" )
                            time.sleep(1)

                            WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P91_QUANTIDADE_VEZ")))
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P91_QUANTIDADE_VEZ encontrado", routine="ContaReceber", error_details ="" )

                            Apex.setValue(browser, "P91_QUANTIDADE_VEZ", randomWeeks)
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P91_QUANTIDADE_VEZ :por teve o valor inserido corretamente", routine="ContaReceber", error_details ="" )
                            
                            btnNovaSimulacao = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B119203509952682337")))
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação encontrado", routine="ContaReceber", error_details ="" )

                            btnNovaSimulacao.click()
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação clicado", routine="ContaReceber", error_details ="" )

                        Components.has_spin(init)
                        Components.has_form(init)           


                        WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#simulacao")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Tabela Criada Simulação realizada", routine="ContaReceber", error_details ="" )


                        btnSaveIframeRepeticaoPagamento = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B119206935067682339"))) 
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão salvar da aba geração de repetições encontrado", routine="ContaReceber", error_details ="" )

                        # browser.execute_script("arguments[0].scrollIntoView(true);", btnSaveIframeRepeticaoPagamento)        
                        # Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Scrol até aba Repeticao", routine="ContaReceber", error_details ="" ) 
                
                        btnSaveIframeRepeticaoPagamento.click()
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão salvar da aba geração de repetições clicado", routine="ContaReceber", error_details ="" )

                else:
                    Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: btnRepeticao não encontrado", routine="ContaReceber", error_details ="" )
                    

                Components.has_alert(init)
            
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
        finally:    
            browser.switch_to.default_content()
#END repeticaoContaReceber(init)            

    def recebimentoContaReceber(init,query,staticValues = False):
        """
        Função que simula a operação de recebimento de uma conta a receber na aplicação.
        Interage com a interface do usuário, preenche campos com dados dinâmicos e registra logs
        detalhados para monitoramento e depuração de erros. Além disso, captura screenshots quando necessário.
        
        Parâmetros:
        init (tuple): Tupla contendo objetos e variáveis necessárias para o processo, como o navegador (browser),
                    login, Log_manager, ambiente de execução, e outros componentes de configuração.
        query (dict): Dicionário que contém informações relacionadas à consulta da conta a receber, 
                    incluindo identificadores e parâmetros específicos da conta.
        
       
        """

        randomQuery = query

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")    
    
        randomValue = round(random.uniform(1, 100), 2)
        randomText = GeradorDados.gerar_texto(50)
        randomNumber = GeradorDados.randomNumberDinamic(0,5)
        randomDay = GeradorDados.randomNumberDinamic(1,30)

        today = datetime.today()
        todayStr = today.strftime("%d/%m/%Y")
        randomDay = GeradorDados.randomNumberDinamic(0, 30)
        randomDate = today + timedelta(days=randomDay)
        finalDateStr = randomDate.strftime("%d/%m/%Y")

        try:

            valorOriginalValue = FuncoesUteis.stringToFloat(Apex.getValue(browser,"P85_VALOR"))
            clienteOriginalValue  = FuncoesUteis.stringToFloat(Apex.getValue(browser,"P85_PESSOA_CLIENTE_ID"))
            numeroDocumentoOriginalValue = FuncoesUteis.stringToFloat(Apex.getValue(browser,"P85_NUMERO_DOCUMENTO"))

            seletor = "#contaReceberRecebimento"
            has_frame = Components.has_frame(init,seletor)

            if not has_frame:               

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
            else:
                has_repeat = True        

            if has_repeat:
                if not has_frame:
                    seletor = "#contaReceberRecebimento"
                    has_frame = Components.has_frame(init,seletor)


                if has_frame:         
                    
                    valorDescontoDividido = round((randomValue/4),2)
                    valorDescontoDividido = FuncoesUteis.formatBrCurrency(valorDescontoDividido)
                    randomContaId = randomQuery["Query_queryContaId"] if randomNumber != 0 else randomText
                    randomPagamentoId = randomQuery["Query_queryFormaPagamento"] if randomNumber != 0 else randomText
                    finalDate = todayStr if randomNumber in (0,1,2,3) else finalDateStr if randomNumber == 4 else randomText
                    valorOriginalPagamento = valorOriginalValue/3
                    valorDescontoDividido = valorDescontoDividido  if randomNumber != 0 else randomText
                    randomValue = randomValue  if randomNumber != 0 else randomText
                    randomText =randomText  if randomNumber != 0 else randomValue

                    apexValues = staticValues if isinstance(staticValues,dict) else{
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
                        clienteId = FuncoesUteis.stringToFloat(Apex.getValue(browser,"P87_PESSOA_ID") )

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

                    Components.has_alert(init)            
                
                    

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
        finally:
            browser.switch_to.default_content()
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Voltando para o conteudo principal", routine="ContaReceber", error_details ="" )
                            
#END recebimentoContaReceber(init,query) 

    @staticmethod
    def jurosMultasContaReceber(init,staticValues = False):
        """
        Função responsável por acessar a aba de Juros e Multas de uma conta a receber,
        inserir valores aleatórios nos campos correspondentes e validar se os valores
        foram corretamente inseridos. Todos os eventos são registrados em logs para 
        rastreamento e análise de falhas.

        Parâmetros:
        - init (tuple): Tupla contendo os seguintes objetos e variáveis do ambiente:
            - browser (WebDriver): Instância do WebDriver utilizada para automação.
            - login: Dados de login (não utilizados diretamente nesta função).
            - Log_manager: Gerenciador de logs para registrar as operações.
            - get_ambiente: Função para obter informações sobre o ambiente.
            - env_vars (dict): Dicionário contendo variáveis do ambiente.
            - seletor_ambiente: Seletor do ambiente (não utilizado diretamente).
            - screenshots (str): Caminho para salvar capturas de tela em caso de erro.
            - oracle_db_connection: Conexão com o banco de dados Oracle (não utilizada diretamente).

        Retorno:
        - None: A função apenas executa as ações no sistema e gera logs.
        """
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        try:

            abaJurosMultas = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"[aria-controls='R55917550016747726']")))
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

            apexValues = staticValues if isinstance(staticValues,dict) else {
                "P85_JUROS_CONTA_RECEBER":jurosDiaValor,
                "P85_MULTA_CONTA_RECEBER":multaValor,
                "P85_JUROS_MES_CONTA_RECEBER":jurosMesValor
            }

            print(f"valores apex {apexValues}")
           
            campos = FuncoesUteis.prepareToCompareValues(init,apexValues,True)
            FuncoesUteis.compareValues(init,campos)


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
#END jurosMultasContaReceber(init)


    @staticmethod
    def editaContaReceber(init,callback = False):
        """
        Função responsável por acessar e clicar no botão de edição de uma conta a receber.

        Parâmetros:
        - init (tuple): Tupla contendo os seguintes elementos do ambiente:
            - browser (WebDriver): Instância do WebDriver utilizada para automação.
            - login: Dados de login (não utilizados diretamente nesta função).
            - Log_manager: Gerenciador de logs para registrar as operações.
            - get_ambiente: Função para obter informações sobre o ambiente.
            - env_vars (dict): Dicionário contendo variáveis do ambiente.
            - seletor_ambiente: Seletor do ambiente (não utilizado diretamente).
            - screenshots (str): Caminho para salvar capturas de tela em caso de erro.
            - oracle_db_connection: Conexão com o banco de dados Oracle (não utilizada diretamente).

        Retorno:
        - None: A função apenas executa as ações no sistema e gera logs.
        """

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
            if callback:
                callback()
         

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
#END editaContaReceber(init)                       


    
    @staticmethod
    def totalizadoresContaReceber(init,query):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB") 


        try:     
            queries = query

            totalizadores = {

                "#a_Collapsible1_containerTotalizadores_content tr > #atrasada":0,
                "#a_Collapsible1_containerTotalizadores_content tr > #devolvidoParcial":1,
                "#a_Collapsible1_containerTotalizadores_content tr > #recebida":2,
                "#a_Collapsible1_containerTotalizadores_content tr > #vencehoje":3,
                "#a_Collapsible1_containerTotalizadores_content tr > #venceamanha":4,
                "#a_Collapsible1_containerTotalizadores_content tr > #avencer":5,
                "#a_Collapsible1_containerTotalizadores_content tr > #recebidoparcial":6
            }


            for key in totalizadores.items():
                totalizador = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,f"#{key}")))
                
                if totalizador:
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Totalizador {key} encontrado", 
                                        routine="ContaReceber", error_details ="" 
                    )
                else:
                    Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Totalizador {key} não encontrado", 
                                        routine="ContaReceber", error_details ="" 
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
#END totalizadoresContaReceber(init,query)        


    @staticmethod
    def salvaContaReceber(init):
        """
        Função responsável por salvar uma conta a receber.

        Parâmetros:
        - init (tuple): Tupla contendo os seguintes elementos do ambiente:
            - browser (WebDriver): Instância do WebDriver utilizada para automação.
            - login: Dados de login (não utilizados diretamente nesta função).
            - Log_manager: Gerenciador de logs para registrar as operações.
            - get_ambiente: Função para obter informações sobre o ambiente.
            - env_vars (dict): Dicionário contendo variáveis do ambiente.
            - seletor_ambiente: Seletor do ambiente (não utilizado diretamente).
            - screenshots (str): Caminho para salvar capturas de tela em caso de erro.
            - oracle_db_connection: Conexão com o banco de dados Oracle (não utilizada diretamente).

        
        """
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB") 

        try:

            btnSaveContaReceber = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#B118650201045784509"))) 
            btnText = btnSaveContaReceber.text
            Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"Botão {btnText} encontrado", routine="", error_details='')

            browser.execute_script("arguments[0].scrollIntoView(true);", btnSaveContaReceber)
            Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"Scroll até {btnText}", routine="", error_details='')

            btnSaveContaReceber.click()
            Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"Botão {btnText} clicado", routine="", error_details='')

            Components.has_spin(init)
            Components.has_alert(init)
            Components.has_alert_sucess(init)

        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))    



#END salvaContaReceber(init)

    @staticmethod
    def excluiContaReceber(init):
        """
        Função responsável por excluir uma conta a receber.

        Parâmetros:
        - init (tuple): Tupla contendo os seguintes elementos do ambiente:
            - browser (WebDriver): Instância do WebDriver utilizada para automação.
            - login: Dados de login (não utilizados diretamente nesta função).
            - Log_manager: Gerenciador de logs para registrar as operações.
            - get_ambiente: Função para obter informações sobre o ambiente.
            - env_vars (dict): Dicionário contendo variáveis do ambiente.
            - seletor_ambiente: Seletor do ambiente (não utilizado diretamente).
            - screenshots (str): Caminho para salvar capturas de tela em caso de erro.
            - oracle_db_connection: Conexão com o banco de dados Oracle (não utilizada diretamente).
        """
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB") 

        try:

            # Aguarda a aba estar visível
            abaRecebimento = WebDriverWait(browser, 30).until(
                EC.visibility_of_element_located((By.ID, "recebimento_tab"))
            )
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de Recebimento encontrada", routine="ContaReceber", error_details ="" )


            # Garante que o elemento está na tela
            browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", abaRecebimento)
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Scroll até Aba de Recebimento ", routine="ContaReceber", error_details ="" )


            # Aguarda até que o elemento esteja clicável
            WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#recebimento_tab")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de Recebimento clicavel", routine="ContaReceber", error_details ="" )


            abaRecebimento.click()
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de Recebimento clicada", routine="ContaReceber", error_details ="" )
            
            try:
                has_receipt = WebDriverWait(browser,30).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,".fa.fa-trash-o")))
            except (TimeoutException, NoSuchElementException, Exception) as e:
                Log_manager.add_log(application_type=env_application_type, level="ERROR", message="Não há recebimento atrelado a conta", routine="", error_details=str(e))
               
                has_receipt = False

            if has_receipt:
                while len(has_receipt) > 0:  # Continuar enquanto houver botões de exclusão na lista
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message="Botão de exclusão de recebimentos encontrado", routine="ContaReceber", error_details="")
                    
                    # Clicar no primeiro botão de exclusão encontrado
                    has_receipt[0].click()
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message="Botão de exclusão de recebimentos clicado", routine="ContaReceber", error_details="")
                    
                    # Esperar um pouco para garantir que o item seja removido ou que a página seja atualizada
                    WebDriverWait(browser, 10).until(EC.staleness_of(has_receipt[0]))  # Espera até o botão se tornar obsoleto
                    
                    # Recarregar a lista de botões de exclusão (pois a página pode ter mudado após a exclusão)
                    has_receipt = WebDriverWait(browser, 30).until(
                        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".fa.fa-trash-o"))
                    )

                btnDeleteRecebimentoConfirm = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".js-confirmBtn.ui-button.ui-corner-all.ui-widget.ui-button--hot"))) 
                btnText = btnDeleteRecebimentoConfirm.text
                Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"Botão {btnText} encontrado", routine="", error_details='')

                browser.execute_script("arguments[0].scrollIntoView(true);", btnDeleteRecebimentoConfirm)
                Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"Scroll até {btnText}", routine="", error_details='')

                btnDeleteRecebimentoConfirm.click()
                Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"Botão {btnText} clicado", routine="", error_details='')    
            else:
                btnDeleteContaReceber = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#B118650674994784509"))) 
                btnText = btnDeleteContaReceber.text
                Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"Botão {btnText} encontrado", routine="", error_details='')

                browser.execute_script("arguments[0].scrollIntoView(true);", btnDeleteContaReceber)
                Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"Scroll até {btnText}", routine="", error_details='')

                btnDeleteContaReceber.click()
                Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"Botão {btnText} clicado", routine="", error_details='')

                has_alert = Components.has_alert(init)
                
                if not has_alert:

                    btnDeleteContaReceberConfirm = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".js-confirmBtn.ui-button.ui-corner-all.ui-widget.ui-button--hot"))) 
                    btnText = btnDeleteContaReceberConfirm.text
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"Botão {btnText} encontrado", routine="", error_details='')

                    browser.execute_script("arguments[0].scrollIntoView(true);", btnDeleteContaReceberConfirm)
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"Scroll até {btnText}", routine="", error_details='')

                    btnDeleteContaReceberConfirm.click()
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message=f"Botão {btnText} clicado", routine="", error_details='')
                    
                    Components.url_contains(init,ContaReceber.url)

        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))    
        