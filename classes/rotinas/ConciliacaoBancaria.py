import random

from calendar import c
import faker
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from sqlalchemy import false
from sqlalchemy import true
from classes.utils.GerarDados import GeradorDados  
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components
from classes.rotinas.ExtratoContas import ExtratoContas
from classes.rotinas.ContasReceber import ContaReceber
from time import sleep
from classes.rotinas.ContasReceber import ContaReceber
from time import sleep
import random
from faker import Faker as fake


class ConciliacaoBancaria:
    url="conciliacao-bancaria"
    filterSelector = "#P154_FILTRO_CONTA"
    filters = [
        "P154_FILTRO_CONTA",
        "P154_FILTRO_PERIODO_POR",
        "P154_DATA_INICIAL",
        "P154_DATA_FINAL",
        "P154_FILTRO_SITUACAO"
    ]

    camposRegra = {
        "P268_DESCRICAO_REGRA",
        "P268_TIPO_LANCAMENTO",
        "P268_CONTA",
        "P268_TIPO_SELECAO",
        "P268_DESCRICAO_LANCAMENTO_BANCARIO",
        "P268_TIPO_TRATAMENTO",
        "P268_TRANSFERENCIA_CONTA_ORIGEM_ID",
        "P268_TRANSFERENCIA_CONTA_DESTINO_ID",
        "P268_TRANSFERENCIA_FORMA_TRANSFERENCIA_ID",
	    "P268_TRANSFERENCIA_UTILIZAR_DESCRICAO_LANCAMENTO",
        "P268_CONTA_PAGAR_PESSOA_ID",
        "P268_TRANSFERENCIA_DESCRICAO",
        "P268_CONTA_PAGAR_CATEGORIA_FINANCEIRA_ID",
        "P268_CONTA_PAGAR_UTILIZAR_DESCRICAO_LANCAMENTO",
        "P268_CONTA_PAGAR_DESCRICAO"
    }

    @staticmethod
    def insereConciliacao(init:tuple,pathArquivo:str):
        """
        Realiza o processo de conciliação bancária automatizada.
        
        Esta função interage com a interface da aplicação web para importar um arquivo OFX
        e confirmar a conciliação bancária. O progresso é registrado em logs.
        
        
        :param init: tuple
            Tupla contendo os objetos necessários para a automação:
            - browser: Instância do WebDriver do Selenium.
            - login: Objeto de login (não utilizado diretamente nesta função).
            - Log_manager: Gerenciador de logs para registrar eventos e erros.
            - get_ambiente: Função ou objeto para obter informações do ambiente.
            - env_vars: Dicionário contendo variáveis do ambiente.
            - seletor_ambiente: Seletor de ambiente (não utilizado diretamente nesta função).
            - screenshots: Caminho para salvar capturas de tela em caso de erro.
            - oracle_db_connection: Conexão com o banco de dados Oracle (não utilizada nesta função).
        
        ##    
        Fluxo da Função:
        1. Aguarda e clica no botão "Nova Conciliação".
        2. Verifica se há um frame para importação do extrato.
        3. Envia um arquivo OFX para o input de upload.
        4. Aguarda e clica no botão "Importar Extrato".
        5. Aguarda e clica no botão de confirmação, se presente.
        6. Em caso de erro, captura logs e salva um screenshot.
        7. Retorna ao contexto principal do navegador.
        
        :raises:
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
                filePath = (rf"{pathArquivo}")
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
    def inluiRecebimentoContaExistente(init:tuple,filter:dict):
        """
        Automatiza a inclusão de um recebimento em uma conta existente no sistema web.

       
        :param init:
         (tuple): Contém os objetos e configurações necessárias para a automação.
        :param filter:
         (dict): Filtros a serem aplicados para localizar os lançamentos desejados.

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
    def criarNovaContaReceber(init:tuple,values:dict):
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
    def criarNovaTransferencia(init:tuple,query:dict):
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
    def associarRecebimentoExistente(init:tuple,filters:dict,contaReceber:str|bool = False):
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
    def associarTransferenciaExistente(init:tuple,filters:dict|bool=False,contaReceber:str|bool=False):
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
    def ingnorarLancamento(init:tuple):

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
    def conciliarLancamento(init:tuple):
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
        
#END conciliarLancamento(init)

    @staticmethod
    def processaConciliacaoAutomatica(init:tuple,yesNot:bool):
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
    def desconciliaLancamento(init:tuple,especifico:str|bool=False):
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
        
#END desconciliaLancamento(init,especifico)

    @staticmethod
    def criarRegraConciliacao(init:tuple, dictConfigRecebido:dict):
        """
        Cria uma nova regra de conciliação bancária.

        Método recebe um dicionario com os campos preenchidos com valores especificos
        ou None, nesse caso o método irá gerar valores válidos e aleatórios para os campos, respeitando a lógica da rotina.

        :params init :
            Tupla contendo os objetos necessários para a automação:

            - browser: Instância do WebDriver do Selenium.
            - login: Objeto de login (não utilizado diretamente nesta função).
            - Log_manager: Gerenciador de logs para registrar eventos e erros.
            - get_ambiente: Função ou objeto para obter informações do ambiente.
            - env_vars: Dicionário contendo variáveis do ambiente.
            - seletor_ambiente: Seletor de ambiente (não utilizado diretamente nesta função).
            - screenshots: Caminho para salvar capturas de tela em caso de erro.
            - oracle_db_connection: Conexão com o banco de dados Oracle (não utilizada nesta função).
        
        :params dictConfigRecebido :
            - Dicionário contendo as configurações recebidas para a criação da regra de conciliação bancária.
        """
        #deve ser chamada apenas quando estiver na aba "Regras da Conciliação Bancária" e com o filtro lateral fechado.

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        try:

            query = { "conta1": """
                                SELECT CONTA.CONTA_ID
                                FROM ERP.CONTA
                                JOIN ERP.CONTA_ESPECIFICACAO ON CONTA.CONTA_ID = CONTA_ESPECIFICACAO.CONTA_ID
                                LEFT JOIN ERP.LOJA ON LOJA.LOJA_ID = CONTA_ESPECIFICACAO.LOJA_ID
                                WHERE CONTA_ESPECIFICACAO.GRUPO_LOJA_ID = 1501
                                    AND CONTA.TIPO_CONTA_ID IN (1, 2)
                                    AND (CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IN (1) OR CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IS NULL)
                                    AND (CONTA.CONTA_ID IN (0) OR CONTA_ESPECIFICACAO.STATUS IN (1))
                            """,
            "conta2": """
                                        SELECT CONTA.CONTA_ID
                                        FROM ERP.CONTA
                                        JOIN ERP.CONTA_ESPECIFICACAO ON CONTA.CONTA_ID = CONTA_ESPECIFICACAO.CONTA_ID
                                        LEFT JOIN ERP.LOJA ON LOJA.LOJA_ID = CONTA_ESPECIFICACAO.LOJA_ID
                                        WHERE CONTA_ESPECIFICACAO.GRUPO_LOJA_ID = 1501
                                            AND CONTA.TIPO_CONTA_ID IN (1, 2)
                                            AND (CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IN (1) OR CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IS NULL)
                                            AND (CONTA.CONTA_ID IN (0) OR CONTA_ESPECIFICACAO.STATUS IN (1))
                                    """}

            queryConta = FuncoesUteis.getQueryResults(init, query)

            queryContaReceber = FuncoesUteis.getQueryResults(init, ContaReceber.queries)



            #gera configurações aleatorias para o dicionario de configurações default, os campos gerados fora de dicionarios influenciam na criação de outros campos
            if dictConfigRecebido["tipoLancamento"] is None:
                tipoLancamento = random.randint(1, 2)
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"tipoLancamento gerado aleatóriamente: {tipoLancamento}",
                    routine="",
                    error_details=""
                )
            else:
                tipoLancamento = dictConfigRecebido["tipoLancamento"]
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"tipoLancamento recebido: {tipoLancamento}",
                    routine="",
                    error_details=""
                )

            if dictConfigRecebido["tipoTratamento"] is None:
                tipoTratamento = random.choice([1, 2, 5]) if tipoLancamento == 1 else random.choice([2, 4, 5])
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"tipoTratamento gerado aleatóriamente: {tipoTratamento}",
                    routine="",
                    error_details=""
                )
            else:
                tipoTratamento = dictConfigRecebido["tipoTratamento"]
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"tipoTratamento recebido: {tipoTratamento}",
                    routine="",
                    error_details=""
                )
            
            if tipoTratamento in [1,4]: #Conta a Receber / Pagar
                dictConfigEspecificDefault = { #apenas os campos que aparecem dependendo do tipo de tratamento, será mergado com a dictConfigTelaDefault depois para gerar o dictConfigDefault
                "cliente" : queryContaReceber["Query_queryCliente"],
                "categFinanceira" : queryContaReceber["Query_queryCategoriaFinanceira"],
                "utilizarDescricao" : random.randint(0, 1)
                }
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"cliente gerado aleatóriamente: {dictConfigEspecificDefault['cliente']} | categFinanceira gerada aleatóriamente: {dictConfigEspecificDefault['categFinanceira']} | utilizarDescricao gerada aleatóriamente: {dictConfigEspecificDefault['utilizarDescricao']}",
                    routine="",
                    error_details=""
                )

            elif tipoTratamento == 2: #Transferencia
                dictConfigEspecificDefault = {
                "conta2" : queryConta["Query_conta2"],
                "formaTransferencia" : random.randint(1, 5),
                "utilizarDescricao" : random.randint(0, 1)
                }
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"conta2 gerada aleatóriamente: {dictConfigEspecificDefault['conta2']} | formaTransferencia gerada aleatóriamente: {dictConfigEspecificDefault['formaTransferencia']} | utilizarDescricao gerada aleatóriamente: {dictConfigEspecificDefault['utilizarDescricao']}",
                    routine="",
                    error_details=""
                )

            try:
                if dictConfigEspecificDefault["utilizarDescricao"] == 1 or dictConfigRecebido["utilizarDescricao"] == 1:
                    dictConfigEspecificDefault["descricaoTratamento"] = GeradorDados.simpleRandString(init, 20, 36, "descricaoTratamento")

                else:
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"utilizarDescricao não será utilizado, logo não terá descricaoTratamento",
                        routine="",
                        error_details=""
                    )
            except:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"dictConfigEspecificDefault não foi criado, logo não terá descricaoTratamento",
                    routine="",
                    error_details=""
                )

            dictConfigTelaDefault = { #apenas os campos que apararecem ao abrir na tela
            "descricaoRegra" : GeradorDados.simpleRandString(init, 20, 36, "descricaoRegra"),
            "status" : random.randint(1, 2),
            "tipoLancamento" : tipoLancamento,
            "conta1" : queryConta["Query_conta1"],
            "tipoSelecao" : random.randint(1, 2),
            "descricaoLancamento" : GeradorDados.simpleRandString(init, 20, 36, "descricaoLancamento"),
            "tipoTratamento" : tipoTratamento,
            "salvar" : 0
            }

            try:
                """
                #recebe os valores default e os valores aleatorios, vai receber 2 dicionarios, um com os campos que tem em tela, e outros que são dependentes
                caso a dictConfigEspecificDefault não existir, o dicionario default será apenas do dictConfigTelaDefault
                """
                dictConfigDefault = dictConfigTelaDefault | dictConfigEspecificDefault 
            except NameError:
                dictConfigDefault = dictConfigTelaDefault

            # é construido com base nos valores defaults, porém pode ser sobreescrito por possiveis valores inseridos manualmente quando metodo for chamado
            dictConfigFinal = {}

            # Primeiro: adiciona tudo da dictConfigRecebido, desde que o valor seja diferente de None
            for key, value in dictConfigRecebido.items():
                if value is not None:
                    dictConfigFinal[key] = value

            # Segundo: adiciona valores do default apenas se a key já não existir na dictConfigFinal
            for key, value in dictConfigDefault.items():
                if key not in dictConfigFinal:
                    dictConfigFinal[key] = value


            dicionarioEscrito = { #dicionario incompleto, apenas as informações que aparecem quando o "Tipo de Tratamento" for "Ignorar Lançamento" / Default e seletores iguais
            "P268_DESCRICAO_REGRA" : dictConfigFinal["descricaoRegra"],
            "P268_DESCRICAO_LANCAMENTO_BANCARIO" : dictConfigFinal["descricaoLancamento"]
            }

            dicionarioPopup = { #dicionario incompleto, apenas as informações que aparecem quando o "Tipo de Tratamento" for "Ignorar Lançamento" / Default
                "P268_TIPO_LANCAMENTO" : dictConfigFinal["tipoLancamento"], 
                "P268_CONTA" : dictConfigFinal["conta1"],
                "P268_TIPO_SELECAO" : dictConfigFinal["tipoSelecao"],
                "P268_TIPO_TRATAMENTO" : dictConfigFinal["tipoTratamento"],
                "P268_STATUS" : dictConfigFinal["status"]
            }

            #adicionando aos dicionarios dependendo de certos valores e seletores{
            if dicionarioPopup["P268_TIPO_TRATAMENTO"] == 2: #Lançamento de Transferência
                dicionarioPopup["P268_TRANSFERENCIA_UTILIZAR_DESCRICAO_LANCAMENTO"] = dictConfigFinal["utilizarDescricao"]
                dicionarioPopup["P268_TRANSFERENCIA_FORMA_TRANSFERENCIA_ID"] = dictConfigFinal["formaTransferencia"]

                if(dicionarioPopup["P268_TIPO_LANCAMENTO"] == 1): #Entrada
                    dicionarioPopup["P268_TRANSFERENCIA_CONTA_ORIGEM_ID"] = dictConfigFinal["conta2"]

                else: #Saida
                    dicionarioPopup["P268_TRANSFERENCIA_CONTA_DESTINO_ID"] = dictConfigFinal["conta2"]

                if dicionarioPopup["P268_TRANSFERENCIA_UTILIZAR_DESCRICAO_LANCAMENTO"] == 1:
                    dicionarioEscrito["P268_TRANSFERENCIA_DESCRICAO"] = dictConfigFinal["descricaoTratamento"]


            elif dicionarioPopup["P268_TIPO_TRATAMENTO"] == 1 or dicionarioPopup["P268_TIPO_TRATAMENTO"] == 4: #Lançamento de Conta a Receber ou Conta a Pagar

                if dicionarioPopup["P268_TIPO_LANCAMENTO"] == 1: #Entrada -> Conta a Receber
                    dicionarioPopup["P268_CONTA_RECEBER_UTILIZAR_DESCRICAO_LANCAMENTO"] = dictConfigFinal["utilizarDescricao"]
                    dicionarioPopup["P268_CONTA_RECEBER_PESSOA_ID"] = dictConfigFinal["cliente"]
                    dicionarioPopup["P268_CONTA_RECEBER_CATEGORIA_FINANCEIRA_ID"] = dictConfigFinal["categFinanceira"]

                    if dicionarioPopup["P268_CONTA_RECEBER_UTILIZAR_DESCRICAO_LANCAMENTO"] == 1:
                        dicionarioEscrito["P268_CONTA_RECEBER_DESCRICAO"] = dictConfigFinal["descricaoTratamento"]

                elif dicionarioPopup["P268_TIPO_LANCAMENTO"] == 2: #Saida -> Conta a Pagar
                    dicionarioPopup["P268_CONTA_PAGAR_UTILIZAR_DESCRICAO_LANCAMENTO"] = dictConfigFinal["utilizarDescricao"]
                    dicionarioPopup["P268_CONTA_PAGAR_PESSOA_ID"] = dictConfigFinal["cliente"]
                    dicionarioPopup["P268_CONTA_PAGAR_CATEGORIA_FINANCEIRA_ID"] = dictConfigFinal["categFinanceira"]

                    if dicionarioPopup["P268_CONTA_PAGAR_UTILIZAR_DESCRICAO_LANCAMENTO"] == 1:
                        dicionarioEscrito["P268_CONTA_PAGAR_DESCRICAO"] = dictConfigFinal["descricaoTratamento"]
            # }


            Components.btnClick(init, "#adicionaRegra")
            
            hasFrame = Components.has_frame(init,"[title='Cadastro de Regra para Conciliação Bancária']")
            if hasFrame:

                dictCompareOne = {
                    "P268_TIPO_LANCAMENTO" : dicionarioPopup["P268_TIPO_LANCAMENTO"]
                }
                del dicionarioPopup["P268_TIPO_LANCAMENTO"]

                tipoLancamento = FuncoesUteis.prepareToCompareValues(init, dictCompareOne)
                sleep(2)
                FuncoesUteis.compareValues(init, tipoLancamento)

                dictCompareOne = {
                    "P268_TIPO_TRATAMENTO" : dicionarioPopup["P268_TIPO_TRATAMENTO"]
                }
                del dicionarioPopup["P268_TIPO_TRATAMENTO"]

                tipoTratamento = FuncoesUteis.prepareToCompareValues(init, dictCompareOne)
                FuncoesUteis.compareValues(init, tipoTratamento)

                if dicionarioPopup.get("P268_TRANSFERENCIA_UTILIZAR_DESCRICAO_LANCAMENTO") or dicionarioPopup.get("P268_CONTA_RECEBER_UTILIZAR_DESCRICAO_LANCAMENTO") or dicionarioPopup.get("P268_CONTA_PAGAR_UTILIZAR_DESCRICAO_LANCAMENTO"):
                    campos = [
                    "P268_TRANSFERENCIA_UTILIZAR_DESCRICAO_LANCAMENTO",
                    "P268_CONTA_RECEBER_UTILIZAR_DESCRICAO_LANCAMENTO",
                    "P268_CONTA_PAGAR_UTILIZAR_DESCRICAO_LANCAMENTO"
                    ]

                    for seletor in campos:
                        if seletor in dicionarioPopup:
                            Apex.setValue(browser, seletor, 0)
                            
                            Log_manager.add_log(
                                application_type=env_application_type,
                                level="INFO",
                                message=f"Desmarcado a checkbox {seletor}",
                                routine="",
                                error_details=""
                            )
                            del dicionarioPopup[seletor]

                            break
                        else:
                            Log_manager.add_log(
                                application_type=env_application_type,
                                level="INFO",
                                message=f"Não encontrado nenhum seletor no dicionario",
                                routine="",
                                error_details=""
                            )

                campos = FuncoesUteis.prepareToCompareValues(init, dicionarioPopup)
                FuncoesUteis.compareValues(init, campos)


                campos = FuncoesUteis.prepareToCompareValues(init, dicionarioEscrito, True)
                FuncoesUteis.compareValues(init, campos)
                    
                camposEscritos = {}
                for seletor,value in dicionarioEscrito.items():

                    try:
                        element = browser.find_element(By.CSS_SELECTOR, f"#{seletor}")
                        size_value = element.get_attribute("size")
                        camposEscritos[seletor] = int(size_value)

                        Log_manager.add_log(
                            application_type=env_application_type,
                            level="INFO",
                            message=f"Campo {seletor} encontrado com valor {size_value}",
                            routine="",
                            error_details=""
                        )

                    except Exception as e:
                        Log_manager.add_log(
                            application_type=env_application_type,
                            level="ERROR",
                            message=f"Erro ao buscar o campo {seletor}: {str(e)}",
                            routine="",
                            error_details=str(e)
                        )
                        continue

                for key, value in camposEscritos.items():
                    try:
                        valorCampo = Apex.getValue(browser, key)
                        tamanho = len(valorCampo)
                        if tamanho > value:
                            Log_manager.add_log(
                                application_type=env_application_type,
                                level="INFO",
                                message=f"Valor do campo {key} recebeu {valorCampo} de tamanho({tamanho}), é maior que o permitido ({value})",
                                routine="",
                                error_details=""
                            )
                        else:
                            Log_manager.add_log(
                                application_type=env_application_type,
                                level="INFO",
                                message=f"Valor do campo {key} recebeu {valorCampo} de tamanho({tamanho}), dentro do permitido ({value})",
                                routine="",
                                error_details=""
                            )
                    except Exception as e:
                        Log_manager.add_log(
                            application_type=env_application_type,
                            level="ERROR",
                            message=f"Erro ao verificar o valor do campo {key}: {str(e)}",
                            routine="",
                            error_details=str(e)
                        )

                botaoFinal = "#B170903369717813403" if dictConfigFinal["salvar"] else "#B170903131900813401"
                Components.btnClick(init, botaoFinal)


                browser.switch_to.default_content()

        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))

#END criarRegraConciliacao(init, dictConfigRecebido)

    @staticmethod
    def criarContaReceberResumido(init:tuple, dictRecebido:dict = None, procuraConta:bool = True) -> dict:
        """
        Clica na Opção de Lançamento "Criar Nova Conta a Receber" e
        cria uma Conta a Receber resumida via conciliação bancária.

        :params init :
            Tupla contendo os objetos necessários para a automação:

            - browser: Instância do WebDriver do Selenium.
            - login: Objeto de login (não utilizado diretamente nesta função).
            - Log_manager: Gerenciador de logs para registrar eventos e erros.
            - get_ambiente: Função ou objeto para obter informações do ambiente.
            - env_vars: Dicionário contendo variáveis do ambiente.
            - seletor_ambiente: Seletor de ambiente (não utilizado diretamente nesta função).
            - screenshots: Caminho para salvar capturas de tela em caso de erro.
            - oracle_db_connection: Conexão com o banco de dados Oracle (não utilizada nesta função).

        :params dictRecebido :
            - Dicionário opcional contendo os campos e valores a serem preenchidos na Conta a Receber Resumida.

            - Caso não seja passado, o método irá gerar valores válidos e aleatórios para os campos, respeitando a lógica da rotina.
        
        :params procuraConta :
            - Booleano que define se o método ira procurar pela Conta a Receber criada,
            verificando se os valores colocados nos campos estão sendo colocados corretamente na criação.

            - True = Procura a conta criada.
            - False = Não procura a conta criada.

        :return camposFiltros:
            - Dicionário contendo os campos e valores da Conta a Receber criada necessarias pra procura-lá.
        """
        
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        queryContaReceber = FuncoesUteis.getQueryResults(init, ContaReceber.queries)
        
        if dictRecebido is None:
            dictContaReceber = {
                "P199_PESSOA_ID" : queryContaReceber["Query_queryCliente"],
                "P199_DATA_EMISSAO" : GeradorDados.simpleRandDate(init),
                "P199_CATEGORIA_FINANCEIRA_ID" : queryContaReceber["Query_queryCategoriaFinanceira"]
            }

            contaReceberDescricao = {
                "P199_DESCRICAO" : GeradorDados.simpleRandString(init, 20, 36, "P199_DESCRICAO")
            }
        else:
            cliente = dictRecebido["cliente"] if dictRecebido["cliente"] is not None else queryContaReceber["Query_queryCliente"]
            dataEmissao = dictRecebido["dataEmissao"] if dictRecebido["dataEmissao"] is not None else GeradorDados.simpleRandDate(init)
            categFinanceira = dictRecebido["categFinanceira"] if dictRecebido["categFinanceira"] is not None else queryContaReceber["Query_queryCategoriaFinanceira"]
            descricaoConta = dictRecebido["descricao"] if dictRecebido["descricao"] is not None else GeradorDados.simpleRandString(init, 20, 36, "P199_DESCRICAO")

            dictContaReceber = {
                "P199_PESSOA_ID" : cliente,
                "P199_DATA_EMISSAO" : dataEmissao,
                "P199_CATEGORIA_FINANCEIRA_ID" : categFinanceira
            }

            contaReceberDescricao = {
                "P199_DESCRICAO" : descricaoConta
            }

        Components.btnClick(init, 'p[acao="novoLancamento"]')

        hasFrame = Components.has_frame(init,"[title='Cadastro de Contas a Receber Resumido']")
        if hasFrame:
            
            campos = FuncoesUteis.prepareToCompareValues(init, dictContaReceber)
            FuncoesUteis.compareValues(init, campos)

            campos = FuncoesUteis.prepareToCompareValues(init, contaReceberDescricao)
            FuncoesUteis.compareValues(init, campos)

            for seletor, value in contaReceberDescricao.items():

                element = browser.find_element(By.CSS_SELECTOR, f"#{seletor}")
                tamMax = element.get_attribute("maxlength")

                tamanhoEscrito = len(contaReceberDescricao[seletor])

                valorCampo = Apex.getValue(browser, seletor)
                tamanhoEncontrado = len(valorCampo)

                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Campo {seletor} escrito com tamanho = {tamanhoEscrito}, encontrado com tamanho = {tamanhoEncontrado}",
                    routine="",
                    error_details=""
                )

            mapeamentoFiltro = {
                "P199_CONTA_ID": "P84_CONTA",
                "P199_VALOR": "P84_VALOR_INICIAL",
                "P199_PESSOA_ID": "P84_CLIENTE",
                "P199_DATA_EMISSAO": "P84_DATA_INICIAL",
                "P199_CATEGORIA_FINANCEIRA_ID": "P84_CATEGORIA"
            }
            
            valoresInseridos = [
                Apex.getValue(browser, "P199_CONTA_ID"),
                Apex.getValue(browser, "P199_VALOR"),
                "Dinheiro", # Apex.getValue(browser, "P199_FORMA_RECEBIMENTO"),
                Apex.getValue(browser, "P199_PESSOA_ID"),
                Apex.getValue(browser, "P199_DATA_EMISSAO"),
                Apex.getValue(browser, "P199_DATA_RECEBIMENTO"),
                Apex.getValue(browser, "P199_CATEGORIA_FINANCEIRA_ID"),
                Apex.getValue(browser, "P199_DESCRICAO")
            ]

            valorFinal = Apex.getValue(browser, "P199_VALOR")
            dataFinal = Apex.getValue(browser, "P199_DATA_EMISSAO")

            camposFiltros = {}
            for seletor, seletorFinal in mapeamentoFiltro.items():

                camposFiltros[seletorFinal] = Apex.getValue(browser, seletor)
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Inserido o valor do campo {seletor} para o seletor {seletorFinal}",
                    routine="",
                    error_details=""
                )
            
            camposFiltros["P84_VALOR_FINAL"] = valorFinal
            camposFiltros["P84_DATA_FINAL"] = dataFinal
            camposFiltros["P84_TIPO_PERIODO"] = "EMISSAO"

            Components.btnClick(init, "#save")

            if not Components.has_alert(init) and int(tamanhoEncontrado) > int(tamMax):
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="ERROR",
                    message=f"Campo {seletor} não respeitou o tamanho máximo permitido ({tamMax})",
                    routine="",
                    error_details=""
                )

            if procuraConta: #verifica se a conta foi criada corretamente

                camposFiltros["P84_SITUACAO"] = "recebida"

                FuncoesUteis.goToPage(init,ContaReceber.url)

                FuncoesUteis.setFilters(init, camposFiltros)

                Components.btnClick(init, "#filtrar")

                ContaReceber.editaContaReceber(init)

                valoresNaConta = [
                    Apex.getValue(browser, "P85_CONTA_ID"),
                    Apex.getValue(browser, "P85_VALOR"),
                    None, #P199_FORMA_RECEBIMENTO
                    Apex.getValue(browser, "P85_PESSOA_CLIENTE_ID"),
                    Apex.getValue(browser, "P85_DATA_EMISSAO"),
                    Apex.getValue(browser, "P85_DATA_PREVISAO_RECEBIMENTO"),
                    Apex.getValue(browser, "P85_CATEGORIA_FINANCEIRA"),
                    Apex.getValue(browser, "P85_DESCRICAO")
                ]

                sleep(1)

                Components.btnClick(init, "#recebimento_tab")

                sleep(1)

                formaPagamento = browser.find_element(By.CSS_SELECTOR, 'td[headers="C5662823473090224"]').text

                valoresNaConta[2] = formaPagamento

                compareInsertContaBase = {#dicionario segue o padrão : "(nome da informação)-(nome do seletor da conta a receber resumida) : (valor na conta), (valor inserido)"
                    "Conta-P199_CONTA_ID": None,
                    "Valor-P199_VALOR": None,
                    "FormaRecebimento-P199_FORMA_RECEBIMENTO": None,
                    "Cliente-P199_PESSOA_ID": None,
                    "DataEmissao-P199_DATA_EMISSAO": None,
                    "DataRecebimento-P199_DATA_RECEBIMENTO": None,
                    "CategoriaFinanceira-P199_CATEGORIA_FINANCEIRA_ID": None,
                    "Descricao-P199_DESCRICAO": None,
                    "FormaRecebimento-P199_FORMA_RECEBIMENTO": None
                }
                compareInsertConta = {
                    key: (valoresInseridos[i], valoresNaConta[i])
                    for i, key in enumerate(compareInsertContaBase)
                }

                FuncoesUteis.compareValues(init, compareInsertConta)

            print(f"CAMPOSFILTROS============\n{camposFiltros}")
            print(f"COMPAREINSERTCONTA========\n{compareInsertConta}")

            return camposFiltros

#END criarContaReceberResumido(init, procuraConta)

    @staticmethod
    def clickOpcoesLancamento(init:tuple, filtros:dict = None):
        """
        Procura por um OFX pela data, espera o botão da "Situação" terminar de carregar
        e clica para abrir as opções de lançamento.

        :params init :
            Tupla contendo os objetos necessários para a automação:

            - browser: Instância do WebDriver do Selenium.
            - login: Objeto de login (não utilizado diretamente nesta função).
            - Log_manager: Gerenciador de logs para registrar eventos e erros.
            - get_ambiente: Função ou objeto para obter informações do ambiente.
            - env_vars: Dicionário contendo variáveis do ambiente.
            - seletor_ambiente: Seletor de ambiente (não utilizado diretamente nesta função).
            - screenshots: Caminho para salvar capturas de tela em caso de erro.
            - oracle_db_connection: Conexão com o banco de dados Oracle (não utilizada nesta função).

        :params data :
            Dicionário opcional contendo os dados necessários para a busca do OFX, caso não seja passado será utilizado um default.
        """

        if filtros is None:
            filtros = {
            "P154_DATA_INICIAL" : "12/01/2025",
            "P154_DATA_FINAL" : "12/01/2025"
            }

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        FuncoesUteis.aplyFilter(init, filtros)
        Components.btnClick(init, ".fa.fa-edit")
        sleep(1)
        browser.execute_script("$('.ui-button.ui-corner-all.ui-widget').click()") 

        spin = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,".fa.fa-spinner.fa-anim-spin")))
        Log_manager.add_log(application_type=env_application_type, level="INFO", message="Loading...", routine="", error_details='')

        if spin:

            var = WebDriverWait(browser,90).until(EC.staleness_of(spin))
            Log_manager.add_log(application_type=env_application_type, level="INFO", message="fim do Loading...", routine="", error_details='')

        if var:

            try:
                element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".d.fa.fa-times-circle.iconGrey")))
                btn = ".d.fa.fa-times-circle.iconGrey"
            except:
                try:
                    element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".fa.fa-check-circle.iconGreen")))
                    btn = ".fa.fa-check-circle.iconGreen"
                except:
                    element = None

            if element:
                browser.execute_script("""
                    arguments[0].scrollIntoView({behavior: 'auto', block: 'nearest', inline: 'center'});
                """, element)
                Components.btnClick(init, btn)
            else:
                print("Nenhum dos elementos foi encontrado.")

        else:
            Log_manager.insert_logs_for_execution()
            browser.quit()
#END clickOpcoesLancamento(init, data)