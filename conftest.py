from collections import namedtuple
from datetime import datetime
import json
import os
import socket
import tempfile
from xml.dom.minidom import Attr
from pydantic import BaseModel
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException,ElementNotInteractableException, ElementClickInterceptedException,ElementClickInterceptedException,WebDriverException,NoSuchWindowException,NoSuchWindowException,NoAlertPresentException,MoveTargetOutOfBoundsException,JavascriptException,SessionNotCreatedException,InvalidCookieDomainException,UnexpectedAlertPresentException
import pytest
from classes.utils.LogManager import LogManager
from dotenv import dotenv_values
import oracledb
from PIL import Image
import numpy as np
import time
from sqlalchemy import create_engine
from selenium.webdriver.chrome.options import Options
import traceback
import sys
from classes.utils.Email import EmailModel, EmailComposer,EmailSender
from classes.utils.Components import Components






def pytest_addoption(parser):
    parser.addoption(
        "--browser", action="store", default="chrome", help="Escolha o navegador (chrome, firefox, edge)"
    )
    parser.addoption(
        "--user", action="store", default="teste", help="Escolha o usuário para login"
    )
    parser.addoption(
        "--ambiente", action="store", default="NONE", help="escolha um ambiente"
    )
    parser.addoption(
        "--insertOrEdit", action="store", default="Insert", help="Escolha inserção ou edição"
    )
    parser.addoption(
        "--headless", action="store", default="Yes", help="Escolha se o navegador de testes estará visivel (Yes or No)"
    )
    parser.addoption(
        "--daysToDelete", action="store", default="7", help="logs com mais de x dias serão deletados"
    )
    parser.addoption(
        "--urlToUse", action="store", default="URL_ERP", help="Url do login"
    )
    parser.addoption(
        "--collection",
        action="store",
        default="web_logs",
        help="Nome da coleção de logs a ser testada (padrão: web_logs)",
    )
  

@pytest.fixture
def collection_name(request):
    """Fixture que obtém o valor da opção --collection."""
    return request.config.getoption("--collection")

@pytest.fixture
def days_to_delete(request):
    """Fixture que obtém o valor da opção --daysToDelete."""
    return int(request.config.getoption("--daysToDelete"))

def timestampFormat():
    timestamp = datetime.now().strftime("%d-%m-%Y %H-%M-%S-%f")
    return timestamp


def getEnv():
    env_vars = dotenv_values(".env") 
    return env_vars

@pytest.fixture
def env_vars():
    return getEnv()




@pytest.fixture()
def db_connection(env_vars, request):
    getEnv = env_vars
    connection_str = getEnv.get("DATABASES")
    
    if not connection_str:
        pytest.fail("A variável 'DATABASES' não foi definida nas variáveis de ambiente.")
    
    try:
        connection = json.loads(connection_str)
    except json.JSONDecodeError:
        pytest.fail("Erro ao decodificar a string de conexão JSON.")
    
    db_conn = getEnv.get(f'{connection.get(request.param)}')
    if not db_conn:
        pytest.fail(f"Configuração para o banco de dados '{request.param}' não encontrada.")
    
    conn = None
    try:
        engine = create_engine(db_conn)
        conn = engine.connect()
        print(f"Conexão com o banco de dados '{request.param}' estabelecida com sucesso!")
        yield conn  # Retorna a conexão para o teste
    except oracledb.Error as err:
        pytest.fail(f"Erro ao conectar ao banco de dados: {err}")
    finally:
        if conn:
            conn.close()  # Garante que a conexão seja fechada após o teste
            print(f"Conexão com o banco de dados '{request.param}' fechada.")



def get_driver(browser_name, options):
    """Factory function to create the appropriate WebDriver instance."""
    if browser_name.lower() == "chrome":
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    elif browser_name.lower() == "firefox":
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
    elif browser_name.lower() == "edge":
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
    else:
        raise ValueError(f"Browser '{browser_name}' not supported.")
    return driver

def get_browser_options(browser_name,headless):
    
    options = None
    if browser_name.lower() == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")  # Navegação anônima
        options.add_argument("--no-sandbox")  # Desabilita o sandbox para melhorar a performance
        options.add_argument("--disable-dev-shm-usage")  # Uso de memória compartilhada
        options.add_argument("--disable-gpu") 
        if headless == "Yes":
            options.add_argument("--headless=new")  

        user_data_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={user_data_dir}")

    elif browser_name.lower() == "firefox":
        options = webdriver.FirefoxOptions()
        options.set_preference("dom.webnotifications.enabled", False)  # Desabilita notificações
    elif browser_name.lower() == "edge":
        options = webdriver.EdgeOptions()
    return options


# def pytest_generate_tests(metafunc):
#     config = metafunc.fixturenames and metafunc.config.pluginmanager.getplugin("pytestconfig").getoption("config")
#     browsers_to_test = []
#     for browser_name, enabled in config["browsers"].items():
#         if enabled.lower() == "true":
#             browsers_to_test.append(browser_name)

#     if "browser" in metafunc.fixturenames:
#         metafunc.parametrize("browser", browsers_to_test, indirect=True)


@pytest.fixture()
def selenium_exceptions():
        
    return (
        NoSuchElementException,
        TimeoutException,
        StaleElementReferenceException,
        ElementNotInteractableException,
        ElementClickInterceptedException,
        ElementClickInterceptedException,
        WebDriverException,
        NoSuchWindowException,
        NoSuchWindowException,
        NoAlertPresentException,
        MoveTargetOutOfBoundsException,
        JavascriptException,
        SessionNotCreatedException,
        InvalidCookieDomainException,
        UnexpectedAlertPresentException

    )
         

@pytest.fixture()
def browser(request):
    envValue = getEnv()
    mode = envValue.get('MODE', '').upper()

    if mode == "LOCAL":

        # Pegando o valor do parâmetro da linha de comando
        browser_name = request.config.getoption("browser")
        headless = request.config.getoption("headless")
        
        options = get_browser_options(browser_name,headless)
        driver = get_driver(browser_name, options)

        driver.implicitly_wait(10)

        # Melhorar o tempo de espera inicial do navegador
        try:
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            pytest.exit("Erro crítico: navegador não inicializou corretamente.")

        yield driver

        driver.quit()
    
    elif mode == "SELENOID":
        browser = envValue.get("BROWSER",'chrome')
        version = envValue.get('VERSION', '128.0')
        remote_url = envValue.get('SELENOID_URL')
        remote_url = "http://localhost:4444/wd/hub"



        options = Options()
        options.set_capability("browserName", browser)
        options.set_capability("browserVersion", version)
        options.set_capability("selenoid:options", {
            "enableVNC": True,
            "enableVideo": False,
            "videoName": "test.mp4",
            "videoCodec": "mpeg4"
        })

        driver = webdriver.Remote(
            command_executor=remote_url,
            options=options
        )

        yield driver

        driver.quit()




@pytest.fixture()
def get_ambiente(request):
    # Recuperando o nome do ambiente da linha de comando
    ambienteConfig = request.config.getoption("ambiente")
    
    # Obtendo a variável de ambiente correspondente ao nome do ambiente
    env_var = getEnv()
    ambienteValoresStr = env_var.get(f"{ambienteConfig.upper()}_VALORES_AMBIENTE")
    
    if ambienteValoresStr:
        # Convertendo a string JSON de volta para um dicionário
        ambienteValores = json.loads(ambienteValoresStr)
        
        # Extraindo os valores específicos
        nivel_acesso = ambienteValores.get("nivelAcesso")
        ambiente = ambienteValores.get("ambiente")
        rede = ambienteValores.get("rede")
        loja = ambienteValores.get("loja")
        
        # Retornando as variáveis de forma individual
        return nivel_acesso, ambiente,rede,loja
    pytest.fail(f"Variáveis de ambiente para {ambienteConfig} não encontradas.")






def _send_login_failure_notification(env_vars, browser, log_manager,error:str = None):
    """ Envia uma notificação por e-mail quando o login falha.    """

    screenshot_path = ".assets/login_failure.png"  
    try:
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        browser.save_screenshot(screenshot_path)
        log_manager.add_log(level="INFO", message=f"Screenshot de falha salva em '{screenshot_path}'", routine="Login")
    except Exception as e:
        screenshot_path = None 
        log_manager.add_log(level="ERROR", message="Falha crítica ao salvar screenshot.", routine="Login", error_details=str(e))

    EMAIL_REMETENTE = env_vars.get('EMAIL_REMETENTE')
    SENHA_REMETENTE = env_vars.get('SENHA_REMETENTE')

    if not EMAIL_REMETENTE or not SENHA_REMETENTE:
        raise ValueError("As variáveis de ambiente EMAIL_REMETENTE e SENHA_REMETENTE não foram definidas.")

    email_list = log_manager.get_logs_not_async(collection='emails')

    servidor_gmail = {
        "host": "smtp.gmail.com",
        "port": 587,
        "email": EMAIL_REMETENTE,
        "senha": SENHA_REMETENTE
    }
    enviador = EmailSender(**servidor_gmail)   
    
    for email in email_list:
        try:
            
            dados_email = EmailModel(
                                    destinatario=email['email'],
                                    assunto="Falha no Login do Gestão",
                                    corpo=f"Olá, houve falha no login do sistema,Erro:{error}. Em anexo uma imagem contendo print do erro ocorrido. Favor verificar com urgência. Esse e-mail foi gerado via automação",
                                    caminho_imagem=screenshot_path,
                                    nome_arquivo_anexo="login_failure.png"
                                    )
        except Exception as e:
            print(f"Erro na validação dos dados do e-mail: {e}")
            exit()

        print("Montando a mensagem...")
        compositor = EmailComposer(remetente=EMAIL_REMETENTE, data=dados_email)
        mensagem_pronta = compositor.build_message()   

        print("Enviando o e-mail...")
        enviador.send(mensagem_pronta)



LOGIN_TIMEOUT = 10  # Tempo de espera para elementos na página de login
POST_LOGIN_TIMEOUT = 30 # Tempo de espera para o carregamento da página após o login
ERROR_ALERT_TIMEOUT = 5 # Tempo curto para verificar se uma mensagem de erro apareceu


@pytest.fixture()
def login(browser, request, log_manager,selenium_exceptions):
    """
    Realiza o login no sistema, valida o sucesso ou falha, e retorna o WebDriver autenticado.
    """
    user = request.config.getoption("user")
    url_key = request.config.getoption("urlToUse")
    env_vars = getEnv()

    erp_url = env_vars.get(url_key, '')
    email = env_vars.get(f"{user.upper()}_EMAIL", '')
    password = env_vars.get(f"{user.upper()}_PASSWORD", '')

    email_field_selector = env_vars.get('EMAIL_FIELD', '')
    password_field_selector = env_vars.get('PASSWORD_FIELD', '')
    btn_login_selector = env_vars.get('BTN_LOGIN', '')
    error_message_selector = Components.ERROR_MESSAGE_SELECTOR

    if not all([erp_url, email, password, email_field_selector, password_field_selector, btn_login_selector]):
        pytest.exit("Erro crítico: Variáveis de ambiente ou seletores essenciais para o login não foram encontrados.")
        
    try:
        browser.get(f"{erp_url}login")
        log_manager.add_log(level="INFO", message="Página de login carregada.", routine="Login")
        
        wait = WebDriverWait(browser, LOGIN_TIMEOUT)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, email_field_selector))).send_keys(email)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, password_field_selector))).send_keys(password)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, btn_login_selector))).click()
        log_manager.add_log(level="INFO", message="Formulário de login preenchido e enviado.", routine="Login")
        return browser
    except selenium_exceptions as e:
        log_manager.add_log(level="ERROR", message="Timeout ao tentar preencher o formulário de login.", routine="Login", error_details=str(e))
        _send_login_failure_notification(env_vars, browser, log_manager,error=str(e))
        pytest.fail("Falha crítica: Não foi possível interagir com a página de login. Verifique os seletores ou a disponibilidade da página.")
    except Exception as e: 
        log_manager.add_log(level="ERROR", message="Erro inesperado durante a interação com o login.", routine="Login", error_details=str(e))
        _send_login_failure_notification(env_vars, browser, log_manager,error=str(e))
        pytest.fail(f"Erro inesperado no Selenium durante o login: {e}")
        
    try:
        error_alert = WebDriverWait(browser, ERROR_ALERT_TIMEOUT).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, error_message_selector))
        )
        error_text = error_alert.text.strip() if error_alert else "Alerta de erro encontrado, mas sem texto."
        if "Credenciais de Log-in Inválidas" in error_text:
            pass
        else:
            log_manager.add_log(level="ERROR", message=f"Falha no login. Mensagem de erro exibida: '{error_text}'", routine="Login")
            _send_login_failure_notification(env_vars, browser, log_manager,error=error_text)
            pytest.fail(f"Login falhou. Motivo: {error_text}")

    except TimeoutException:
       
        log_manager.add_log(level="INFO", message="Nenhum alerta de erro imediato encontrado. Verificando redirecionamento de sucesso...", routine="Login")
        try:
            WebDriverWait(browser, POST_LOGIN_TIMEOUT).until(EC.url_changes(f"{erp_url}login"))
            log_manager.add_log(level="INFO", message="Login realizado com sucesso! URL alterada.", routine="Login")
        except TimeoutException:
            log_manager.add_log(level="ERROR", message="Falha no login: A página não redirecionou após a tentativa.", routine="Login")
            _send_login_failure_notification(env_vars, browser, log_manager,error="A página não redirecionou após a tentativa.")
            pytest.fail("Login falhou. A URL não mudou após a submissão das credenciais.")

    return browser
        
    


@pytest.fixture()
def seletor_ambiente(browser, login, log_manager, env_vars, get_ambiente):


    nivel_acesso, ambiente, rede, loja = get_ambiente



    # Verificação se algum valor é igual a "1"
    if nivel_acesso == "1" and ambiente == "1" and rede == "1" and loja == "1":
        log_manager.add_log(
            level="DEBUG",
            message=f"VALORES PADRÃO DETECTADOS - Nivel Acesso: {nivel_acesso}, Ambiente: {ambiente}, Rede: {rede}, Loja: {loja}",
            routine="Login",application_type='WEB'
        )
        print("Valores padrão detectados, interrompendo o teste.")  # Informando que os valores são padrão e o teste será interrompido
        return  # Interrompe o teste quando os valores são "1"

    # Se os valores não são "1", prossegue com o teste normal
    log_manager.add_log(
        level="DEBUG",
        message=f"Nivel Acesso: {nivel_acesso}, Ambiente: {ambiente}, Rede: {rede}, Loja: {loja}",
        routine="Login",application_type='WEB'
    )

    # Verificando se a URL_ERP está no ambiente
    if 'URL_ERP' not in env_vars:
        pytest.fail("Erro crítico: 'URL_ERP' não encontrada no ambiente de variáveis.")
    
    # Caso tudo esteja ok, execute a navegação
    env_item = env_vars['URL_ERP']
    browser.get(f"{env_item}home")

    try:
        seletorAmbiente = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".t-Button.t-Button--icon.t-Button--header.t-Button--navBar"))
        )
        seletorAmbiente.click()
        log_manager.add_log(level="INFO", message="Botão Alterar local de trabalho clicado", routine="Login",application_type='WEB')

        # Primeiro, aguarde o iframe ficar disponível e depois mude para ele
        WebDriverWait(browser, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[title="Alterar Local de Trabalho"]'))
        )
        log_manager.add_log(level="INFO", message="Trocado para iframe Alterar Local de Trabalho", routine="Login",application_type='WEB')

        time.sleep(2)

        script = f'apex.item("P9_NIVEL_ACESSO_ID").setValue({nivel_acesso});'
        browser.execute_script(script)
        log_manager.add_log(level="INFO", message="Valor Nível Acesso Setado", routine="Login",application_type='WEB')

        script1 = f'apex.item("P9_AMBIENTE").setValue({ambiente});'
        browser.execute_script(script1)
        log_manager.add_log(level="INFO", message="Valor Ambiente Setado", routine="Login",application_type='WEB')

        time.sleep(2)

        if nivel_acesso == '6':
            nivelAcesso = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#P9_LOJA_ID_HOS"))
            )
            if nivelAcesso.is_displayed():
                log_manager.add_log(level="INFO", message="Loja disponivel para adicionar valores", routine="Login",application_type='WEB')
                script3 = f'apex.item("P9_LOJA_ID_HOS").setValue({loja});'
                browser.execute_script(script3)
                log_manager.add_log(level="INFO", message="Valor Loja Setado", routine="Login",application_type='WEB')
        elif nivel_acesso == '5':
            script2 = f'apex.item("P9_REDE_ID_HOS").setValue({rede});'
            browser.execute_script(script2)
            log_manager.add_log(level="INFO", message="Valor Rede Setado", routine="Login",application_type='WEB')

        time.sleep(3)
        salvarAmbiente = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#salvar"))
        )
        salvarAmbiente.click()
        log_manager.add_log(level="INFO", message="Botão Salvar ambiente clicado", routine="Login",application_type='WEB')

        # Verifica se há erro de ambiente não salvo
        try:
            ambienteNaoSalvo = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#t_Alert_Notification"))
            )
            if ambienteNaoSalvo.is_displayed():
                log_manager.add_log(level="ERROR", message="Dados Não Encontrados, Preencha os Campos Necessários", routine="Login",application_type='WEB')
                salvarAmbiente = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#salvar"))
                )
                salvarAmbienteValor = salvarAmbiente.get_attribute('disabled')
                if salvarAmbienteValor is not None:
                    script5 = f'apex.item("P9_LOJA_ID_HOS_HIDDENVALUE").setValue({loja});'
                    browser.execute_script(script5)
                    log_manager.add_log(level="INFO", message="Valor Loja Setado", routine="Login",application_type='WEB')
                    salvarAmbiente.click()
                    log_manager.add_log(level="INFO", message="Botão Salvar ambiente clicado", routine="Login",application_type='WEB')
        except TimeoutException:
            log_manager.add_log(level="INFO", message="Nenhum erro de ambiente encontrado", routine="Login",application_type='WEB')

    except (TimeoutException, NoSuchElementException) as e:
        # # Diretório para salvar os screenshots
        # screenshot_dir = f"{env_screenshot}"
        # os.makedirs(screenshot_dir, exist_ok=True)  # Criar a pasta se não existir

        # # Criar timestamp no formato dd-mm-yyyy_hh-mm-ss-ms

        # # Caminho do arquivo de screenshot
        # screenshot_path = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")

        # # Salvar o screenshot
        # browser.save_screenshot(screenshot_path)
         # Chama a fixture 'screenshots' para tirar a captura de tela
        # screenshot_path = screenshots(env_vars, browser)
        
        # Verifica se o screenshot foi tirado corretamente
        # if screenshot_path:
        #     log_manager.add_log(
        #         level="INFO", 
        #         message=f"Screenshot salvo em: {screenshot_path}", 
        #         routine="Login",application_type='WEB', 
        #         error_details=e.msg if hasattr(e, "msg") else str(e)
        #     )
        # else:
        #    log_manager.add_log(
        #     level="ERROR", 
        #     message="Falha ao salvar screenshot", 
        #     routine="Login",application_type='WEB', 
        #     error_details=e.msg if hasattr(e, "msg") else str(e)
        #     )
                
        error_message = f"Erro durante a escolha do ambiente:TimeOutException ou NoSuchElementException {str(e)}"
        log_manager.add_log(
            level="ERROR", 
            message=error_message, 
            routine="Login",application_type='WEB', 
            error_details=e.msg if hasattr(e, "msg") else str(e)
        )
        ambienteNaoSalvo = None
        

    finally:
        log_manager.insert_logs_for_execution()
        return browser


@pytest.fixture
def log_manager():
    return LogManager()


@pytest.fixture
def compare_images_advanced():
    def _compare(image1_path, image2_path):
        img1 = Image.open(image1_path).convert("L")  # Converte para escala de cinza
        img2 = Image.open(image2_path).convert("L")

        # Converter para array numpy
        arr1 = np.array(img1)
        arr2 = np.array(img2)

        # Calcular diferença absoluta e porcentagem de diferença
        diff = np.abs(arr1 - arr2)
        diff_percentage = (np.sum(diff) / diff.size) / 255 * 100

        return diff_percentage

    return _compare




def has_connection():

    def _has_connection_socket():

        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
        


    def _has_connection_requests():
    
        try:
            response = requests.get("https://www.google.com", timeout=3)
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.ConnectionError:
            return False    
        
    return _has_connection_socket() and _has_connection_requests()





        

@pytest.fixture()
def oracle_db_connection(env_vars):

    getEnv = env_vars
    # Carrega as variáveis de ambiente
    user = getEnv.get("ORACLE_USER")
    password = getEnv.get("ORACLE_PASSWORD")
    host = getEnv.get("ORACLE_HOST")
    port = getEnv.get("ORACLE_PORT")
    service_name = getEnv.get("ORACLE_SERVICE_NAME")

    if not all([user, password, host, port, service_name]):
        pytest.fail("Uma ou mais variáveis de conexão do Oracle não foram definidas no .env.")

    # Cria o DSN (Data Source Name)
    dsn = oracledb.makedsn(host, port, service_name)

    # Tenta conectar ao banco de dados
    conn = None
    try:
        conn = oracledb.connect(user=user, password=password, dsn=dsn)
        print(f"✅ Conexão com o banco de dados Oracle '{service_name}' estabelecida com sucesso!")
        yield conn  # Retorna a conexão para o teste

    except oracledb.Error as err:
        pytest.fail(f"❌ Erro ao conectar ao banco de dados Oracle: {err}")

    finally:
        if conn:
            conn.close()
            print(f"🔌 Conexão com o banco de dados Oracle '{service_name}' fechada.")



class TracebackLog(BaseModel):
    time: str
    error: str
    type_error: str
    function_error: str
    file: str
    row: int
    message: str

def log_erro_completo(exc: Exception, block: str = None) -> TracebackLog:
        """
        Retorna um objeto com informações detalhadas sobre a exceção capturada.
        :param exc: Exceção capturada no except
        :param block: (Opcional) Nome do contexto onde ocorreu o erro
        :return: TracebackLog
        """
        exc_type, _, exc_tb = sys.exc_info()
        tb = traceback.extract_tb(exc_tb)

        if not tb:
            return TracebackLog(
                time=timestampFormat(),
                error=f"Ocorreu uma exceção{f' no bloco: {block}' if block else ''}",
                type_error=type(exc).__name__,
                function_error="Desconhecida",
                file="Desconhecido",
                row=-1,
                message=str(exc)
            )

        erro_final = tb[-1]

        return TracebackLog(
            time=datetime.now().isoformat(),
            erro=f"Ocorreu uma exceção{f' no bloco: {block}' if block else ''}",
            type_error=type(exc).__name__,
            function_error=erro_final.name,
            file=erro_final.filename,
            row=erro_final.lineno,
            message=str(exc)
        )    

@pytest.fixture
def error_logger():
    return log_erro_completo



class TestContext:
    def __init__(self,browser,log_manager,env_vars,login,selenium_exceptions,error_logger):
        self.browser = browser
        self.log = log_manager
        self.env = env_vars
        self.login = login
        self.exceptions = selenium_exceptions
        self.catch_errors = error_logger
    
@pytest.fixture(scope='session')
def context(request):
    browser = browser
    log = log_manager()
    env = env_vars()
    login = login
    exceptions = selenium_exceptions()
    catch_errors = error_logger()



@pytest.fixture()
def init(browser,login,log_manager,get_ambiente,env_vars,seletor_ambiente,selenium_exceptions,error_logger):
    """

    
    """
    return browser,login,log_manager,get_ambiente,env_vars,seletor_ambiente,selenium_exceptions,error_logger



@pytest.fixture()
def context(browser,login,log_manager,get_ambiente,env_vars,seletor_ambiente,selenium_exceptions,oracle_db_connection):
    Init = namedtuple("Init", [
        "browser", "login", "log_manager", "get_ambiente",
        "env_vars", "seletor_ambiente", "screenshots", "oracle_db_connection"
    ])
    
    # Retornando a estrutura organizada com os valores recebidos como argumentos da fixture
    return Init(browser, login, log_manager, get_ambiente, env_vars, seletor_ambiente, selenium_exceptions, oracle_db_connection)







