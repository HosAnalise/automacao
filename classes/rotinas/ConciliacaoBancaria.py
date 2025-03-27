
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.GerarDados import GeradorDados  
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components
from classes.rotinas.ExtratoContas import ExtratoContas



class ConciliacaoBancaria:
    url="conciliacao-bancaria"
    filterSelector = "#P154_FILTRO_CONTA"

    @staticmethod
    def insereConciliacao(init):
        """
        Realiza o processo de conciliação bancária automatizada.
        
        Esta função interage com a interface da aplicação web para importar um arquivo OFX
        e confirmar a conciliação bancária. O progresso é registrado em logs.
        
        Parâmetros:
        init : tuple
            Tupla contendo os objetos necessários para a automação:
            - browser: Instância do WebDriver do Selenium.
            - login: Objeto de login (não utilizado diretamente nesta função).
            - Log_manager: Gerenciador de logs para registrar eventos e erros.
            - get_ambiente: Função ou objeto para obter informações do ambiente.
            - env_vars: Dicionário contendo variáveis do ambiente.
            - seletor_ambiente: Seletor de ambiente (não utilizado diretamente nesta função).
            - screenshots: Caminho para salvar capturas de tela em caso de erro.
            - oracle_db_connection: Conexão com o banco de dados Oracle (não utilizada nesta função).
        
        Fluxo da Função:
        1. Aguarda e clica no botão "Nova Conciliação".
        2. Verifica se há um frame para importação do extrato.
        3. Envia um arquivo OFX para o input de upload.
        4. Aguarda e clica no botão "Importar Extrato".
        5. Aguarda e clica no botão de confirmação, se presente.
        6. Em caso de erro, captura logs e salva um screenshot.
        7. Retorna ao contexto principal do navegador.
        
        Exceções Tratadas:
        - TimeoutException: Se algum elemento não for encontrado dentro do tempo limite.
        - NoSuchElementException: Se algum elemento esperado não existir na página.
        - Exception: Captura outros erros inesperados.
        
        """
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
           
        try:

            btnNovaConciliacao = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B43105716282300150")))
            btnText = btnNovaConciliacao.text
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"Botão {btnText} encontrado ",
                routine="ConciliacaoBancaria",
                error_details=''
            )
            btnNovaConciliacao.click()
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"Botão {btnText} clicado ",
                routine="ConciliacaoBancaria",
                error_details=''
            )

            seletor = "[title='Importar Extrato']"
            has_frame = Components.has_frame(init,seletor)

            if has_frame:
                filePath = (r"C:\Users\Hos_Gabriel\Desktop\Automatização web\assets\teste0,50.ofx")
                WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".apex-item-filedrop-action.a-Button.a-Button--hot")))
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

#END insereConciliacao(init)

    @staticmethod
    def inluiRecebimentoContaExistente(init,filter):
        """
        Automatiza a inclusão de um recebimento em uma conta existente no sistema web.

        Parâmetros:
        - init (tuple): Contém os objetos e configurações necessárias para a automação.
        - filter (dict): Filtros a serem aplicados para localizar os lançamentos desejados.

        Fluxo da Função:
        1. Aguarda e clica no botão "Incluir Recebimento".
        2. Verifica se há um frame para a inclusão do lançamento.
        3. Se houver filtros aplica os filtros fornecidos.
        4. Localiza os checkboxes disponíveis e seleciona um aleatoriamente.
        5. Clica no botão "Conciliar".
        6. Verifica a presença de alertas na página.
        7. Aguarda a presença do botão "Desconciliar Lançamento" para confirmar a conclusão.
        8. Em caso de erro, captura e salva um screenshot.

        Tratamento de Erros:
        - TimeoutException: Caso algum elemento demore a aparecer.
        - NoSuchElementException: Caso um elemento esperado não seja encontrado.
        - Exception: Captura qualquer outro erro inesperado e registra nos logs.

        Registros de Logs:
        - Identificação e clique nos botões.
        - Número de checkboxes encontrados.
        - Seleção de um checkbox aleatório.
        - Ocorrência de erros e salvamento de screenshots, se necessário.
        """

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        try:

            btnInlcuirRecebimento = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[acao='novoLancamentoExistente']")))
            btnText = btnInlcuirRecebimento.text
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado",
                    routine="",
                    error_details=''
                )
            
            btnInlcuirRecebimento.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} clicado",
                    routine="",
                    error_details=''
                )
            
            seletor ="[title='Incluir Lançamento em Conta Existente']"
            has_frame = Components.has_frame(init,seletor)


            if has_frame:
                
                if filter:
                    FuncoesUteis.aplyFilter(init,filter)

                checkBoxes = WebDriverWait(browser,30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,".selecaoConta.form-check-input")))

                checkBoxesLen = len(checkBoxes)
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="Info",
                    message=f"{checkBoxesLen} checkBoxes encontrados",
                    routine="ConciliacaoBancaria",
                    error_details=str(e)
                )

                randomCheckbox = GeradorDados.randomNumberDinamic(0,checkBoxesLen-1)

                checkBoxes[randomCheckbox].click()
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="Info",
                    message=f"{randomCheckbox} checkBox clicado",
                    routine="ConciliacaoBancaria",
                    error_details=str(e)
                )


                btnConciliar = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#conciliarButton")))
                btnText = btnConciliar.text
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} encontrado",
                        routine="",
                        error_details=''
                    )
                
                btnConciliar.click()
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} clicado",
                        routine="",
                        error_details=''
                    )
                FuncoesUteis.has_alert(init)

                WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[acao='desconciliarLancamento']")))
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão desconciliarLancamento encontrado",
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

#END incluiRecebimentoContaExistente(init,filter)

    @staticmethod
    def criarNovaContaReceber(init,values):
        """
        Cria uma nova conta a receber na aplicação web.
        
        Parâmetros:
        init (tuple): Contém as instâncias do browser, login, gerenciador de logs, ambiente, etc.
        values (dict): Dicionário com os valores necessários para a criação da conta.

        Fluxo:
        1. Aguarda e encontra o botão 'Nova Conta a Receber'.
        2. Clica no botão.
        3. Chama a função 'contaReceberResumido' para processar a conta.
        4. Captura logs em cada etapa do processo.
        5. Em caso de erro, captura logs e realiza um screenshot para análise.
        
        Tratamento de Erros:
        - Captura TimeoutException, NoSuchElementException e outras exceções.
        - Salva logs de erro e tenta capturar um screenshot para análise.
        """
        query =''
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
           
        try:

            btnNovaContaReceber = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[acao='novoLancamento']")))
            btnText = btnNovaContaReceber.text
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado",
                    routine="",
                    error_details=''
                )
            
            btnNovaContaReceber.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} clicado",
                    routine="",
                    error_details=''
                )
            
            ExtratoContas.contaReceberResumido(init,query,values)

            
        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))
#END criarNovaContaReceber(init,values)

    @staticmethod
    def criarNovaTransferencia(init,query):
        """
        Cria uma nova transferência financeira na aplicação.
        
        Parâmetros:
            init (tuple): Contém variáveis essenciais para execução da automação, incluindo:
                - browser: Instância do WebDriver Selenium.
                - login: Gerenciador de autenticação.
                - Log_manager: Classe responsável pelo gerenciamento de logs.
                - get_ambiente: Função que obtém o ambiente atual.
                - env_vars: Dicionário contendo variáveis de ambiente.
                - seletor_ambiente: Identificador do ambiente de execução.
                - screenshots: Caminho para salvar capturas de tela.
                - oracle_db_connection: Conexão com o banco de dados Oracle.
            query (dict): Query SQL a ser utilizada na função de nova transferência.

        Fluxo:
            1. Identifica e clica no botão de "Nova Transferência".
            2. Registra logs informando a localização e clique do botão.
            3. Chama a função `novaTransferencia` da classe `ExtratoContas`.
            4. Captura e registra erros, se houverem, salvando screenshots em caso de falha.
        
        Tratamento de Erros:
            - Captura TimeoutException, NoSuchElementException e exceções genéricas.
            - Registra logs de erro e salva uma captura de tela caso ocorra falha.
        """
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
           
        try:       
            btnNovaContaReceber = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[acao='novoLancamentoTransferencia']")))
            btnText = btnNovaContaReceber.text
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado",
                    routine="",
                    error_details=''
                )
            
            btnNovaContaReceber.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} clicado",
                    routine="",
                    error_details=''
                )
            ExtratoContas.novaTransferencia(init,query,False)
            

            
        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))
#END criarNovaTransferencia(init)



    @staticmethod
    def associarRecebimentoExistente(init,filters,contaReceber):
        """
        Associa um recebimento existente a um lançamento na aplicação web.
        
        1. Localiza e clica no botão "Associar Lançamento".
        2. Aplica filtros, caso fornecidos.
        3. Seleciona o checkbox correspondente ao lançamento.
        4. Confirma a associação clicando no botão "Conciliar".
        5. Registra logs das ações realizadas.
        6. Em caso de erro, captura uma tela e a salva.
        
        Parâmetros:
        - init (tupla): Contém instâncias necessárias para execução do método.
        - browser (WebDriver): Instância do navegador.
        - login (str): Informações de login.
        - Log_manager (object): Gerenciador de logs.
        - get_ambiente (object): Função para obter o ambiente.
        - env_vars (dict): Variáveis de ambiente.
        - seletor_ambiente (str): Seletor de ambiente.
        - screenshots (str): Caminho para salvar capturas de tela.
        - oracle_db_connection (object): Conexão com o banco de dados Oracle.
        
        - filters (dict, opcional): Filtros a serem aplicados na busca do lançamento.
        - contaReceber (str, opcional): Código da conta a receber para associar.

        Fluxo:
        1. **Clique no botão de associar lançamento**:
            - Aguarda até o botão de associar o lançamento estar clicável.
            - Registra o clique do botão nos logs.
            
        2. **Verificação do modal de associação**:
            - Verifica se o modal "Associar a Lançamento Existente" foi aberto corretamente.
            
        3. **Aplicação de filtros**:
            - Se `filters` for fornecido, clica na aba de filtros e aplica os filtros.
            - Aguarda a exibição do relatório de contas a receber.
            
        4. **Seleção do checkbox**:
            - Se o relatório de contas a receber foi exibido, seleciona o checkbox correspondente à conta.
            - Caso contrário, registra erro nos logs.
            
        5. **Clique no botão de conciliar**:
            - Localiza e clica no botão "Conciliar" para confirmar a associação.
            - Registra as ações no log.
            
        6. **Tratamento de erros e captura de tela**:
            - Se ocorrer algum erro, registra a exceção nos logs.
            - Caso ocorra erro ao salvar a captura de tela, registra o erro nos logs.
            
        7. **Restaurar contexto do navegador**:
            - Retorna ao contexto principal da página ao final do processo.
        """
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        contaReceber = contaReceber if contaReceber else False
           
        try:       
            seletor ="[acao='associarLancamento']"
            Components.btnClick(init,seletor)
            
            seletor = "[title='Associar a Lançamento Existente']"
            Components.has_frame(init,seletor)

            if isinstance(filters,dict):
                btnFilter = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#SR_filtros_tab")))
                btnText = btnFilter.text
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} encontrado",
                        routine="",
                        error_details=''
                    )
                
                btnFilter.click()
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} clicado",
                        routine="",
                        error_details=''
                    )
                FuncoesUteis.aplyFilter(init,filters)


                Components.has_spin(init)
                has_report = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#reportContasReceber")))
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="Report encontrado com com filtros aplicados",
                        routine="",
                        error_details=''
                    )


            else:
                has_report = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#reportContasReceber")))
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="Report encontrado sem filtros aplicados",
                        routine="",
                        error_details=''
                    )

            
            if has_report:
                seletorCheckbox = f"[value='{contaReceber}']" if contaReceber and isinstance(filters,dict) else ".selecaoConta.form-check-input"
                checkBox = WebDriverWait(browser,30).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,seletorCheckbox)))
                checkBox[0].click()
            else:
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="ERROR",
                        message="Report não encontrado",
                        routine="",
                        error_details=''
                    )
             

            btnConciliar = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#conciliarButton")))
            btnText = btnConciliar.text
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado",
                    routine="",
                    error_details=''
                )
            
            btnConciliar.click()
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
        finally:
            browser.switch_to.default_content()
#END associarRecebimentoExistente(init,filters,contaReceber)
    
    
    @staticmethod
    def associarTransferenciaExistente(init,filters,contaReceber):
        """
        Associa uma transferência existente a um lançamento na aplicação web.
        
        1. Localiza e clica no botão de "Associar Lançamento Transferência".
        2. Aplica filtros, caso fornecidos.
        3. Seleciona o checkbox correspondente à conta a receber.
        4. Confirma a associação clicando no botão "Conciliar".
        5. Registra logs das ações realizadas.
        6. Em caso de erro, captura uma tela e a salva.
        
        Parâmetros:
        - init (tupla): Contém instâncias necessárias para execução do método.
        - browser (WebDriver): Instância do navegador.
        - login (str): Informações de login.
        - Log_manager (object): Gerenciador de logs.
        - get_ambiente (object): Função para obter o ambiente.
        - env_vars (dict): Variáveis de ambiente.
        - seletor_ambiente (str): Seletor de ambiente.
        - screenshots (str): Caminho para salvar capturas de tela.
        - oracle_db_connection (object): Conexão com o banco de dados Oracle.
        
        - filters (dict, opcional): Filtros a serem aplicados na busca da transferência.
        - contaReceber (str, opcional): Código da conta a receber para associar.

        Fluxo:
        1. **Clique no botão de associar transferência**:
            - Aguarda até o botão de associar a transferência estar clicável.
            - Registra o clique do botão nos logs.
            
        2. **Verificação do modal de associação**:
            - Verifica se o modal "Associar a Transferência Existente" foi aberto corretamente.
            
        3. **Aplicação de filtros**:
            - Se `filters` for fornecido, clica na aba de filtros e aplica os filtros.
            - Aguarda a exibição dos resultados filtrados.
            
        4. **Seleção do checkbox**:
            - Identifica o checkbox correspondente à conta a receber.
            - Se os filtros forem aplicados, seleciona o checkbox do lançamento filtrado.
            - Caso contrário, seleciona o primeiro checkbox disponível.
            - Registra logs sobre a seleção do checkbox.
            
        5. **Clique no botão de conciliar**:
            - Localiza e clica no botão "Conciliar" para confirmar a associação.
            - Registra as ações no log.
            
        6. **Tratamento de erros e captura de tela**:
            - Se ocorrer algum erro, registra a exceção nos logs.
            - Caso ocorra erro ao salvar a captura de tela, registra o erro nos logs.
            
        7. **Restaurar contexto do navegador**:
            - Retorna ao contexto principal da página ao final do processo.
        """
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
           
        try: 
            seletor = "[acao='associarLancamentoTransferencia']"
            Components.btnClick(init,seletor)

            seletor = "[title='Associar a uma Transferência Existente']"
            Components.has_frame(init,seletor)

            if isinstance(filters,dict):
                seletor = "#SR_filtros_tab"
                Components.btnClick(init,seletor)
                FuncoesUteis.aplyFilter(init,filters)

                Components.has_spin(init)
                has_check = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,".selecaoConta.form-check-input")))
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="Resultados encontrado com filtros aplicados",
                        routine="",
                        error_details=''
                )

            else:
                has_check = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,".selecaoConta.form-check-input")))
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="Resultados encontrado sem filtros aplicados",
                        routine="",
                        error_details=''
                )

            
            if has_check:
                seletorCheckbox = f"[value='{contaReceber}']" if contaReceber and isinstance(filters,dict) else ".selecaoConta.form-check-input"
                checkBox = WebDriverWait(browser,30).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,seletorCheckbox)))
                checkBox[0].click()
            else:
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="ERROR",
                        message="Report não encontrado",
                        routine="",
                        error_details=''
                    )
             
            seletor = "#conciliarButton"
            Components.btnClick(init,seletor)



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
#END associarTransferemciaExistente(init,filters,contaReceber)

    @staticmethod
    def ingnorarLancamento(init):

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
           
        try: 
            lancamentoBancarioId = Apex.getValue(browser,"P159_LANCAMENTO_BANCARIO_ID")

            seletor = "[acao='ignorarLancamento']"
            Components.btnClick(init,seletor)

            seletor = "#SR_ignoradosReport_tab"
            Components.btnClick(init,seletor)


            lancamentoIgnorado = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,f"[lancamentobancarioid={lancamentoBancarioId}]")))
            
            if lancamentoIgnorado :
                Log_manager.add_log(application_type=env_application_type,
                                    level="ERROR",
                                    message="Lançamento bancario ignorado com sucesso",
                                    routine="",
                                    error_details="")
            else:
                Log_manager.add_log(application_type=env_application_type,
                                    level="ERROR",
                                    message="Lançamento bancario não ignorado",
                                    routine="",
                                    error_details="")
                    




        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))
        
#END ignorarLancamento(init)

    @staticmethod
    def conciliarLancamento(init):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
           
        try: 
            lancamentoBancarioId = Apex.getValue(browser,"P159_LANCAMENTO_BANCARIO_ID")

            seletor = "[acao='conciliarLancamento']"
            Components.btnClick(init,seletor)

            seletor = "#SR_R217176266746131119_tab"
            Components.btnClick(init,seletor)

            seletor = "#SR_conciliadosReport_tab"
            Components.btnClick(init,seletor)
            


            lancamentoConciliado = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,f"[lancamentobancarioid={lancamentoBancarioId}]")))
            
            if lancamentoConciliado :
                Log_manager.add_log(application_type=env_application_type,
                                    level="ERROR",
                                    message="Lançamento bancario ignorado com sucesso",
                                    routine="",
                                    error_details="")
            else:
                Log_manager.add_log(application_type=env_application_type,
                                    level="ERROR",
                                    message="Lançamento bancario não ignorado",
                                    routine="",
                                    error_details="")
                    




        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))
        
        

        

    @staticmethod
    def processaConciliacaoAutomatica(init,yesNot):
        """
        Descrição:
        Este método processa a conciliação automática de lançamentos financeiros na aplicação web. Dependendo do parâmetro yesNot, ele pode confirmar ou cancelar a conciliação automática.

        Parâmetros:
        init: Tupla contendo as instâncias necessárias para execução do método, incluindo browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots e oracle_db_connection.

        yesNot (bool): Define se a conciliação automática deve ser confirmada (True) ou cancelada (False).

        Fluxo de Execução:
        Confirmação da conciliação automática (yesNot=True)

        Aguarda até que o botão de confirmação da conciliação automática esteja disponível e interage com ele.

        Registra logs da localização e clique no botão.

        Aguarda o carregamento da interface com os resultados conciliados.

        Navegação até a aba de conciliações automáticas

        Acessa a aba que exibe os lançamentos conciliados automaticamente.

        Registra logs indicando a ação realizada.

        Verificação de resultados

        Verifica se há conciliações automáticas disponíveis na aba.

        Caso não haja resultados, registra essa informação nos logs.

        Se houver conciliações disponíveis, também registra a ocorrência nos logs.

        Cancelamento da conciliação automática (yesNot=False)

        Aguarda até que o botão de recusa da conciliação automática esteja disponível e interage com ele.

        Registra logs da localização e clique no botão.

        Tratamento de exceções e capturas de tela

        Captura e registra qualquer erro ocorrido durante o processo.

        Caso ocorra um erro, tira um screenshot e salva na pasta configurada.

        Tratamento de Erros:
        Em caso de TimeoutException ou NoSuchElementException, o erro é registrado nos logs.

        Se a captura de tela falhar, um erro adicional é registrado nos logs.
        """


        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
           
        try:       
            if yesNot:

                seletor = ".js-confirmBtn.ui-button.ui-corner-all.ui-widget.ui-button--hot"
                Components.btnClick(init,seletor)
              
                Components.has_spin(init)
                

                seletor  = "#SR_R217176266746131119_tab"
                Components.btnClick(init,seletor)

                
                seletor = "#SR_R217176266746131119_tab"
                Components.btnClick(init,seletor)
                
                has_notResults = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".a-Icon.icon-irr-no-results")))

                if has_notResults:
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="Não há conciliações automaticas disponiveis na aba de conciliações automaticas",
                        routine="",
                        error_details=''
                    )
                else:
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="Há conciliações automaticas disponiveis na aba de conciliações automaticas",
                        routine="",
                        error_details=''
                    )
            else:
                seletor = ".ui-button.ui-corner-all.ui-widget"
                Components.btnClick(init,seletor)

                            
        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))

#END processaConciliacaoAutomatica(init,yesNot) 

    @staticmethod
    def desconciliaLancamento(init,especifico):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
           
        try: 
            seletor = especifico if especifico else ".buttonsConciliacao"

            desconciliaLancamento= WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,seletor)))
            desconciliaLancamentoId = desconciliaLancamento.get_attribute("lancamentoid")

            seletor = "[acao='desconciliarLancamento']"

            Components.btnClick(init,seletor)

            seletor = "#SR_pendentesReport_tab"
            Components.btnClick(init,seletor)

            lancamentoDesconciliado = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,f"[lancamentobancarioid={desconciliaLancamentoId}]")))
            
            if lancamentoDesconciliado :
                Log_manager.add_log(application_type=env_application_type,
                                    level="ERROR",
                                    message="Lançamento bancario desconciliado com sucesso",
                                    routine="",
                                    error_details="")
            else:
                Log_manager.add_log(application_type=env_application_type,
                                    level="ERROR",
                                    message="Lançamento bancario não desconciliado",
                                    routine="",
                                    error_details="")


        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))
        
        