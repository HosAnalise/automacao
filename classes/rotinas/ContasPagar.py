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
    filterSelector ="#P46_SELETOR_LOJA"
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
        """
        Insere dados em diversos campos da tela de "conta a pagar" .
        Preenche os campos do formulário com valores dinâmicos gerados aleatoriamente ou obtidos de uma consulta (`query`).
        Realiza logs detalhados do processo e captura uma screenshot em caso de erro.

        Parâmetros:
        - init (tuple): Tupla contendo objetos e variáveis necessários para a execução da função. Inclui:
            - browser: Instância do navegador controlado pelo Selenium.
            - login: Dados de login (não utilizados diretamente na função).
            - Log_manager: Gerenciador de logs para registrar eventos e erros.
            - get_ambiente: Função que pode obter o ambiente de execução (não utilizada diretamente aqui).
            - env_vars: Variáveis de ambiente que contêm informações sobre o ambiente de execução, como o tipo de aplicação web.
            - seletor_ambiente: Possível seletor de ambiente (não utilizado diretamente).
            - screenshots: Caminho para salvar screenshots em caso de erro.
            - oracle_db_connection: Conexão com o banco de dados Oracle (não utilizada diretamente na função).
            
        - query (dict): Dicionário contendo dados necessários para preencher os campos da conta a pagar, como IDs de conta, fornecedor, categoria financeira, etc.
        
        Processos:
        1. Geração de valores aleatórios para preencher os campos:
        - Valor (no formato de moeda brasileira).
        - Texto aleatório.
        - Número aleatório para determinar a inserção correta ou incorreta.
        - Data aleatória baseada na data atual.
        
        2. Preenchimento dos campos da tela com os valores gerados:
        - Valor original.
        - Conta.
        - Pessoa favorecida.
        - Data de vencimento.
        - Data de previsão de pagamento.
        - Categoria financeira.
        - Empresa.
        - Descrição.

        3. Verificação se os valores inseridos correspondem aos valores esperados, com logs para sucesso e erro.

        4. Caso ocorra uma falha (exceções como TimeoutException, NoSuchElementException, ou outros erros), um log de erro é registrado e uma captura de tela é salva no caminho especificado.

        Exceções:
        - Em caso de falha ao interagir com os elementos (TimeoutException, NoSuchElementException, ou qualquer outra exceção genérica), a função registra um log de erro e tenta salvar uma captura de tela.

        Logs:
        - Logs de sucesso são gerados quando os campos são preenchidos corretamente.
        - Logs de erro são gerados quando os valores inseridos não correspondem aos valores esperados ou quando ocorrem exceções.
        - O caminho da screenshot é registrado em caso de falha.

        Exemplo de uso:
        init = (browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection)
        query = {
            'Query_queryContaId': '123',
            'Query_queryFornecedorId': '456',
            'Query_queryCategoriaFinanceira': '789',
            'Query_queryEmpresa': '001'
        }

        insereContaPagar(init, query)
        """
        queries = query
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
            urlContain = "conta-a-pagar"
            has_contaPagar = Components.url_contains(init,urlContain)

            if not has_contaPagar:
           
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
                Apex.setValue(browser,"P47_CONTA_ID",queries['Query_queryContaId'])
                naContaValue = Apex.getValue(browser,"P47_CONTA_ID")
                if naContaValue == queries['Query_queryContaId']:
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
                Apex.setValue(browser,"P47_PESSOA_FAVORECIDO_ID",queries["Query_queryFornecedorId"])
                pessoaFavorecidoValue = Apex.getValue(browser,"P47_PESSOA_FAVORECIDO_ID")
                if pessoaFavorecidoValue == queries["Query_queryFornecedorId"]:
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
                Apex.setValue(browser,"P47_CATEGORIA_FINANCEIRA",queries["Query_queryCategoriaFinanceira"])
                categoriaFinanceiraValue = Apex.getValue(browser,"P47_CATEGORIA_FINANCEIRA")
                if categoriaFinanceiraValue == queries["Query_queryCategoriaFinanceira"]:
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
                Apex.setValue(browser,"P47_LOJA",queries["Query_queryEmpresa"])
                empresaValue = Apex.getValue(browser,"P47_LOJA")
                if empresaValue ==queries["Query_queryEmpresa"]:
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
        """
        Preenche os campos aba detalhes de contas a pagar e realiza validações. 

        Parâmetros:
        init (tuple): Tupla contendo os seguintes itens:
            - browser: objeto Selenium WebDriver para interação com o navegador.
            - login: informações de login (não utilizado diretamente na função).
            - Log_manager: gerenciador de logs para registrar informações e erros.
            - get_ambiente: função para obter o ambiente (não utilizada diretamente).
            - env_vars: variáveis de ambiente.
            - seletor_ambiente: seletor de ambiente (não utilizado diretamente).
            - screenshots: caminho onde as capturas de tela podem ser salvas.
            - oracle_db_connection: conexão com o banco de dados Oracle (não utilizada diretamente).
        
        query (dict): Dicionário contendo os seguintes valores:
            - Query_queryCentroCusto: valor para o campo "Centro de Custo".
            - Query_queryModelodocumentoFiscal: valor para o campo "Modelo do Documento Fiscal".

        Retorno:
        Nenhum. A função preenche campos na interface e gera logs conforme o andamento do processo.

        Fluxo:
        1. A função preenche os campos de data, centro de custo, modelo do documento fiscal, chave NFe, número do pedido, 
        número do documento, título e código de barras.
        2. Para cada campo, a função valida se o valor foi inserido corretamente e registra logs.
        3. Caso haja erro durante o preenchimento, uma captura de tela é tirada e o erro é registrado no log.

        Exceções Tratadas:
        - TimeoutException: Quando o tempo para encontrar um elemento expira.
        - NoSuchElementException: Quando o elemento não é encontrado no DOM.
        - Exception: Qualquer outra exceção que ocorrer.

        Logs:
        - INFO: Registrado quando um campo é preenchido corretamente.
        - ERROR: Registrado quando ocorre um erro no preenchimento.
        """
        queries = query
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
                Apex.setValue(browser,"P47_CENTRO_DE_CUSTO",queries["Query_queryCentroCusto"])
                centroCustoValue = Apex.getValue(browser,"P47_CENTRO_DE_CUSTO")
                if centroCustoValue == queries["Query_queryCentroCusto"]:
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
                Apex.setValue(browser,"P47_DOCUMENTO_FISCAL_MODELO_ID",queries["Query_queryModelodocumentoFiscal"])
                tipoDocumentoValue = Apex.getValue(browser,"P47_DOCUMENTO_FISCAL_MODELO_ID")
                if tipoDocumentoValue == queries["Query_queryModelodocumentoFiscal"]:
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
        """
        Função responsável por automatizar a aba repetição de uma conta a pagar.
        
        A função realiza as seguintes ações:
        1. Navega até a aba de repetição de conta a pagar.
        2. Verifica se já existem repetições cadastradas. Caso não existam, cria uma nova repetição.
        3. Configura as opções de repetição, como feriados, competência, período e dias de repetição.
        4. Realiza a simulação das repetições e salva a configuração.
        5. Captura logs de sucesso e erro durante o processo e tira screenshots em caso de falha.

        Parâmetros:
        - init (tuple): Parâmetro que contém a seguinte estrutura:
            1. browser: Instância do navegador WebDriver do Selenium.
            2. login: Informações de login para autenticação.
            3. Log_manager: Instância do gerenciador de logs para registrar mensagens.
            4. get_ambiente: Função que retorna o ambiente de configuração.
            5. env_vars: Variáveis de ambiente contendo configurações do sistema.
            6. seletor_ambiente: Seletor utilizado para identificar o ambiente de execução.
            7. screenshots: Caminho para salvar screenshots de erro.
            8. oracle_db_connection: Conexão com o banco de dados Oracle (não utilizada diretamente aqui, mas pode ser usada em outras partes do código).
        
        Fluxo:
        1. A função navega até a aba de repetição de contas a pagar no sistema.
        2. Verifica se já existem repetições cadastradas. Se não, cria uma nova repetição.
        3. A função configura os campos de feriados, competência, período e dias de repetição com valores aleatórios, usando a classe `GeradorDados`.
        4. Simula a configuração da repetição e salva a configuração.
        5. Se ocorrer um erro (como elementos não encontrados ou falha na execução), a função captura a exceção, registra no log e salva uma captura de tela.
        6. Por fim, a função retorna o controle ao conteúdo principal da página.

        Exceções:
        - TimeoutException: Lançada quando um elemento não é encontrado dentro do tempo limite.
        - NoSuchElementException: Lançada quando um elemento não existe na página.
        - Exception: Captura qualquer outra exceção que ocorra durante o processo.
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

                Components.has_alert(init)

                
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


                    Components.has_alert(init)

                

            
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
    @staticmethod
    def pagamentosContaPagar(init,query):
      
        """
        Função para realizar o pagamento de uma conta a pagar, aplicando possíveis descontos condicionais, juros, multas e verificando se os valores inseridos estão corretos.

        Parâmetros:
        - init (tuple): Tupla contendo as seguintes variáveis:
            - browser: Instância do navegador WebDriver.
            - login: Objeto responsável pelo login no sistema.
            - Log_manager: Gerenciador de logs para armazenar e exibir informações.
            - get_ambiente: Função para obter variáveis de ambiente.
            - env_vars: Variáveis de ambiente da aplicação.
            - seletor_ambiente: Função para identificar o ambiente atual da aplicação.
            - screenshots: Caminho para salvar capturas de tela de erros.
            - oracle_db_connection: Conexão com o banco de dados Oracle.
        
        - query (dict): Dicionário contendo as consultas SQL ou variáveis que precisam ser usadas, como:
            - "Query_queryContaId": ID da conta a ser paga.
        
        Fluxo de operação:
        1. Obtém o valor original da conta a pagar.
        2. Acessa a aba de pagamento no sistema, esperando que ela seja visível e clicando nela.
        3. Se o número aleatório for 0 ou 2, realiza o lançamento de um desconto condicional, inserindo o valor e a observação, e clicando para salvar.
        4. Se o número aleatório for 1 ou 2, realiza o pagamento da conta, inserindo valores como desconto, juros, multa, acréscimos e despesas. Também valida se os valores inseridos correspondem aos esperados.
        5. Verifica se há alertas ou erros no processo e salva as informações no log.
        6. No final, o botão de salvar do iframe de pagamento é clicado para confirmar o pagamento.

        Exceções tratadas:
        - TimeoutException: Caso o tempo de espera por um elemento seja excedido.
        - NoSuchElementException: Caso um elemento não seja encontrado.
        - Exception: Para capturar outras exceções gerais.

        Logs:
        - A função gera logs detalhados durante cada etapa do processo, informando o que está sendo realizado e os valores manipulados.
        - Se houver erros durante a execução, um log de erro será gerado, junto com uma captura de tela do erro (se configurado).

        Retorno:
        - Não retorna nenhum valor diretamente. A função realiza a interação com a interface do usuário e gera logs.

        """
        queries = query
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

                has_alert = Components.has_alert(init)
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
                    Apex.setValue(browser,"P70_CONTA_ID",queries["Query_queryContaId"])
                    Apex.setValue(browser,"P70_FORMA_PAGAMENTO",queries["Query_queryContaId"])
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
                descontoEditavelFloat = FuncoesUteis.stringToFloat(descontoEditavel)  

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
            
            has_alert = Components.has_alert(init)
                

            

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
        """
        Função responsável por preencher e submeter os dados de uma instrução de pagamento no sistema de conta a pagar.

        Parâmetros:
        - init (tuple): Tupla contendo as seguintes variáveis de inicialização:
            - browser: O driver do Selenium para interagir com o navegador.
            - login: Informações de login do sistema (não utilizado diretamente na função).
            - Log_manager: Objeto responsável por gerenciar logs durante a execução do script.
            - get_ambiente: Função para obter o ambiente de execução.
            - env_vars: Dicionário de variáveis de ambiente contendo configurações do sistema.
            - seletor_ambiente: Função para selecionar o ambiente de execução (não utilizado diretamente na função).
            - screenshots: Caminho onde as capturas de tela podem ser salvas em caso de erro.
            - oracle_db_connection: Conexão com o banco de dados Oracle (não utilizado diretamente na função).

        - query (dict): Dicionário contendo consultas pré-definidas que serão usadas para preencher campos no formulário:
            - "Query_queryTipoChave": Tipo de chave para o PIX.
            - "Query_queryBanco": Banco para a conta TED.

        Fluxo da função:
        1. Aguarda até que a aba de instrução de pagamento esteja clicável.
        2. Realiza a rolagem da página para tornar a aba visível e clica nela.
        3. Gera valores aleatórios para preencher campos, como forma de pagamento, chave PIX, banco, entre outros.
        4. Preenche os campos do formulário conforme a forma de pagamento selecionada:
            - Boleto (2)
            - PIX (3)
            - TED (4)
        5. Registra logs durante todo o processo, indicando o status das ações realizadas.
        6. Em caso de erro (TimeoutException, NoSuchElementException, ou outros), a função captura o erro, registra o log e, se possível, salva uma captura de tela.

        Exceções Tratadas:
        - TimeoutException: Quando um elemento não está disponível no tempo estipulado.
        - NoSuchElementException: Quando um elemento não é encontrado.
        - Exception: Exceções gerais que podem ocorrer durante a execução do processo.

        Logs:
        - A função gera logs detalhados para cada etapa do processo, incluindo o sucesso ou falha de cada ação e as informações geradas.

        Parâmetros internos usados:
        - `env_application_type`: Tipo de ambiente de execução (WEB).
        - `random_value`: Valor aleatório gerado para ser utilizado como número monetário.
        - `randomText`: Texto aleatório gerado para ser usado em observações.
        - `bigText700`: Texto aleatório de tamanho grande gerado para observações.

        A função também realiza ações específicas para cada forma de pagamento, como preencher o campo para DDA, escolher uma chave para PIX ou fornecer informações para TED.

        Exemplo de uso:
        - `instrucaoPagamentoContaPagar(init, query)`: Onde `init` é a tupla com os dados de inicialização e `query` é o dicionário com as consultas necessárias.
        """
        queries = query
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
        
        random_value = round(random.uniform(1, 999999), 2)
        randomValue = FuncoesUteis.formatBrCurrency(random_value)
        randomText = GeradorDados.gerar_texto(20)

        bigText700 = GeradorDados.gerar_texto(700)
        randomChavePixId = queries["Query_queryTipoChave"]


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
                    Apex.setValue(browser, "P47_TED_BANCO_ID", queries["Query_queryBanco"])
                    Apex.setValue(browser, "P47_TED_AGENCIA", numeroAgencia)
                    Apex.setValue(browser, "P47_TED_CONTA", numeroConta)
                    Apex.setValue(browser, "P47_TED_CONTA_DIGITO", digitoConta)
                    Apex.setValue(browser, "P47_TED_NOME_FAVORECIDO", nomeFavorcido)
                    Apex.setValue(browser, "P47_INSTRUCAO_OBSERVACAO", randomText)
                    Log_manager.add_log(application_type=env_application_type, level="INFO", message="Informações da conta TED preenchidas corretamente", routine="ContaPagar", error_details="")
                else:
                    Apex.setValue(browser, "P47_TED_BANCO_ID", queries["Query_queryBanco"])
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
        """
        Função responsável por automatizar o processo de inserção de despesas em uma conta a pagar. Ela navega pela aba de despesas,
        preenche campos com valores aleatórios e, em seguida, salva a nova despesa. Durante todo o processo, logs detalhados são 
        registrados e, em caso de erro, uma captura de tela é gerada para análise.

        Parâmetros:
            init (tuple): Tupla contendo as variáveis de inicialização necessárias:
                - browser: Instância do navegador controlado pelo Selenium.
                - login: Informações de login (não utilizadas diretamente nesta função).
                - Log_manager: Objeto responsável pela gestão de logs.
                - get_ambiente: Função ou objeto para recuperar o ambiente de execução.
                - env_vars: Variáveis de ambiente, incluindo o tipo de aplicação (WEB).
                - seletor_ambiente: Seletor para identificar o ambiente.
                - screenshots: Caminho ou diretório para salvar capturas de tela.
                - oracle_db_connection: Conexão com o banco de dados Oracle (não utilizada diretamente nesta função).

        Fluxo:
            1. A função aguarda até que a aba de despesas esteja visível e clicável.
            2. Realiza o scroll até a aba de despesas e clica nela.
            3. Espera até que o botão para adicionar uma nova despesa seja clicável e, então, clica nele.
            4. Alterna para o iframe específico de "Conta Pagar X Despesas".
            5. Preenche os campos de "Motivo" e "Despesa" com valores aleatórios gerados.
            6. Clica no botão "Save" para salvar a despesa.
            7. Retorna para o contexto principal da página.

        Valores Aleatórios Gerados:
            - `random_value`: Valor numérico aleatório para o campo "Despesa".
            - `randomValue`: Valor formatado em moeda brasileira (para o campo "Despesa").
            - `randomText`: Texto aleatório com 30 caracteres (para o campo "Motivo").
            - `bigText700`: Texto aleatório com 700 caracteres (para o campo "Motivo", caso uma condição aleatória seja atendida).

        Exceções tratadas:
            - TimeoutException: Caso o tempo de espera para encontrar um elemento expire.
            - NoSuchElementException: Caso um elemento não seja encontrado na página.
            - Exception: Qualquer outro erro inesperado durante a execução.

        Ações de Log:
            - O Log_manager é utilizado para registrar os seguintes eventos:
                - "Aba despesas encontrada"
                - "Scroll até a aba de despesas"
                - "Aba de despesas clicada"
                - "Botão nova despesa encontrado"
                - "Mudando para o iframe Conta Pagar X Despesas"
                - Logs de erro e sucesso, conforme o andamento da execução.

        Captura de Tela:
            - Caso ocorra uma exceção durante a execução, uma captura de tela é salva no diretório configurado, 
            caso a opção de salvar screenshots esteja ativada.

        Finalização:
            - Após a tentativa de inserir a despesa, a função retorna para o contexto principal da página e registra um log de sucesso ou erro.
        """
    
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

            smallOrbig = GeradorDados.randomNumberDinamic(0,4)

            if smallOrbig != 0:
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

            

            if smallOrbig != 0:
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
            
            has_alert = Components.has_alert(init)


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
        """
        Função responsável por automatizar a edição de uma conta a pagar em uma aplicação web. Ela localiza o ícone de edição
        da conta, captura o `data-id` associado a essa conta, e inicia o processo de edição, enquanto gera logs detalhados 
        para monitoramento e captura de erros.

        Parâmetros:
            init (tuple): Tupla contendo as variáveis de inicialização necessárias:
                - browser: Instância do navegador controlado pelo Selenium.
                - login: Informações de login (não utilizadas diretamente nesta função).
                - Log_manager: Objeto responsável pela gestão de logs.
                - get_ambiente: Função ou objeto para recuperar o ambiente de execução.
                - env_vars: Variáveis de ambiente, incluindo o tipo de aplicação (WEB).
                - seletor_ambiente: Seletor para identificar o ambiente.
                - screenshots: Caminho ou diretório para salvar capturas de tela.
                - oracle_db_connection: Conexão com o banco de dados Oracle (não utilizada diretamente nesta função).

        Fluxo:
            1. A função aguarda até que o ícone de edição da conta a pagar esteja visível e clicável.
            2. Quando o ícone é encontrado, o `data-id` do elemento é capturado.
            3. A função clica no ícone de edição para iniciar o processo de edição da conta a pagar.
            4. Durante a execução, eventos importantes são registrados no log.

        Exceções tratadas:
            - TimeoutException: Caso o tempo de espera para encontrar o ícone de edição expire.
            - NoSuchElementException: Caso o ícone de edição não seja encontrado na página.
            - Exception: Qualquer outro erro inesperado durante a execução.

        Ações de Log:
            - O Log_manager é utilizado para registrar os seguintes eventos:
                - "Conta a pagar editável encontrada"
                - "Conta a pagar data-id capturado"
                - "Conta a pagar editável clicada. Início da edição da conta"
                - Logs de erro e sucesso, conforme o andamento da execução.

        Captura de Tela:
            - Caso ocorra uma exceção durante a execução, uma captura de tela é salva no diretório configurado, 
            caso a opção de salvar screenshots esteja ativada.

        Finalização:
            - Após a tentativa de edição, um log final é gerado, indicando se a conta foi editada com sucesso ou se ocorreu algum erro.
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
        """
        Realiza a exclusão de uma conta a pagar na aplicação web.

        Parâmetros:
            init (tuple): Variáveis de inicialização contendo:
                - browser: A instância do Selenium WebDriver para controle do navegador.
                - login: Detalhes do login para a aplicação.
                - Log_manager: Gerenciador de logs para registrar as ações e erros.
                - get_ambiente: Função para obter o ambiente de execução.
                - env_vars: Variáveis de ambiente, como o tipo de aplicação (WEB).
                - seletor_ambiente: Informações sobre o ambiente de execução.
                - screenshots: Caminho para salvar screenshots em caso de erro.
                - oracle_db_connection: Conexão com o banco de dados Oracle.

        Fluxo da Função:
            1. A função localiza e clica na aba de pagamento.
            2. Em seguida, busca e clica nos ícones de exclusão de pagamento, confirmando a exclusão.
            3. Depois, a função localiza e clica no botão para excluir a conta a pagar e confirma a exclusão.
            4. Registra logs para todas as ações, incluindo sucesso e erros.
            5. Caso algum erro ocorra, registra o erro e tenta salvar uma screenshot.

        Logs:
            - INFO: Mensagens que indicam progresso ou sucesso nas etapas.
            - ERROR: Mensagens que indicam erros ou falhas durante a execução.

        Exceções tratadas:
            - TimeoutException: Caso algum elemento não seja encontrado dentro do tempo esperado.
            - NoSuchElementException: Caso um elemento não seja encontrado.
            - Exception: Para qualquer outro erro inesperado.
        """
       
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

            Components.has_alert(init)

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
        """
        Finaliza o processo de inserção de uma nova conta a pagar.

        Parâmetros:
            init (tuple): Variáveis de inicialização contendo:
                - browser: A instância do Selenium WebDriver para controle do navegador.
                - login: Detalhes do login para a aplicação.
                - Log_manager: Gerenciador de logs para registrar as ações e erros.
                - get_ambiente: Função para obter o ambiente de execução.
                - env_vars: Variáveis de ambiente, como o tipo de aplicação (WEB).
                - seletor_ambiente: Informações sobre o ambiente de execução.
                - screenshots: Caminho para salvar screenshots em caso de erro.
                - oracle_db_connection: Conexão com o banco de dados Oracle.

        Fluxo da Função:
            1. Localiza e clica no botão de salvar a nova conta a pagar.
            2. Aguarda por alertas de sucesso e trata caso haja um.
            3. Localiza e clica no botão para voltar para a tela de contas a pagar.
            4. Registra logs para todas as ações e erros durante o processo.
            5. Caso algum erro ocorra, registra o erro e tenta salvar uma screenshot.

        Logs:
            - INFO: Mensagens que indicam progresso ou sucesso nas etapas.
            - ERROR: Mensagens que indicam erros ou falhas durante a execução.

        Exceções tratadas:
            - TimeoutException: Caso algum elemento não seja encontrado dentro do tempo esperado.
            - NoSuchElementException: Caso um elemento não seja encontrado.
            - Exception: Para qualquer outro erro inesperado.
        """
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

            Components.has_alert(init)
            has_alert_sucess = Components.has_alert_sucess(init)       

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

#END finalizaInsertContaPagar(init)

    @staticmethod
    def excluiDespesa(init,deleteAllOrOnlyOne):
        """
        Exclui despesas da aplicação, com a possibilidade de excluir todas ou apenas uma despesa específica.

        Parâmetros:
            init (tuple): Variáveis de inicialização contendo:
                - browser: A instância do Selenium WebDriver para controle do navegador.
                - login: Detalhes do login para a aplicação.
                - Log_manager: Gerenciador de logs para registrar as ações e erros.
                - get_ambiente: Função para obter o ambiente de execução.
                - env_vars: Variáveis de ambiente, como o tipo de aplicação (WEB).
                - seletor_ambiente: Informações sobre o ambiente de execução.
                - screenshots: Caminho para salvar screenshots em caso de erro.
                - oracle_db_connection: Conexão com o banco de dados Oracle.

            deleteAllOrOnlyOne (bool or int): Determina se todas as despesas serão excluídas ou apenas uma.
                - Se `True`, todas as despesas serão excluídas.
                - Se `False`, apenas a primeira despesa será excluída.
                - Se um inteiro for passado, ele define o índice da despesa a ser excluída (índice baseado em zero).

        Fluxo da Função:
            1. Localiza e clica na aba de despesas.
            2. Aguarda até que os ícones de exclusão de despesa estejam presentes.
            3. Dependendo do valor de `deleteAllOrOnlyOne`, executa a exclusão de todas ou uma despesa específica.
            4. Registra logs para todas as ações e erros durante o processo.
            5. Caso algum erro ocorra, registra o erro e tenta salvar uma screenshot.

        Logs:
            - INFO: Mensagens que indicam progresso ou sucesso nas etapas.
            - ERROR: Mensagens que indicam erros ou falhas durante a execução.

        Exceções tratadas:
            - TimeoutException: Caso algum elemento não seja encontrado dentro do tempo esperado.
            - NoSuchElementException: Caso um elemento não seja encontrado.
            - Exception: Para qualquer outro erro inesperado.
        """
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")    
        dataId = "data id não encontrado"  
       

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
          
            trashicon = WebDriverWait(browser, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".fa.fa-trash-o.icon-red.remove"))
            )


            if not trashicon:
                Log_manager.add_log(application_type=env_application_type, level ="ERROR", message="Nenhuma despesa encontrada para excluir", routine ="ContaPagar", TypeError= '')
                return

            if deleteAllOrOnlyOne is True:
                while trashicon:
                    try:
                        trashicon[0].click()
                        confirm_btn = WebDriverWait(browser, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, ".js-confirmBtn"))
                        )
                        confirm_btn.click()

                        Components.has_spin(init)
                        
                        trashicon = WebDriverWait(browser, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".fa-trash-o.icon-red.remove"))
                        )

                    except TimeoutException:
                        Log_manager.add_log(env_application_type, "ERROR", "Botão de confirmação não encontrado", "ContaPagar", '')
                        break  
            else:
                try:
                    index = int(deleteAllOrOnlyOne) if isinstance(deleteAllOrOnlyOne, int) else 0
                    if 0 <= index < len(trashicon):
                        trashicon[index].click()
                        confirm_btn = WebDriverWait(browser, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, ".js-confirmBtn"))
                        )
                        confirm_btn.click()
                    else:
                        Log_manager.add_log(env_application_type, "ERROR", "Índice fora do intervalo", "ContaPagar", '')

                except ValueError:
                    Log_manager.add_log(env_application_type, "ERROR", "Parâmetro inválido para deleteAllOrOnlyOne", "ContaPagar", '')

        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))

#END excluiDespesa(init)            


            

