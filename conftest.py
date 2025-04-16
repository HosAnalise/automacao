from datetime import datetime
import json
import os
import socket
import tempfile
from annotated_types import UpperCase
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pytest
from classes.utils.LogManager import LogManager
from dotenv import dotenv_values
import oracledb
from PIL import Image
import numpy as np
import time
from sqlalchemy import create_engine
from selenium.webdriver.chrome.options import Options





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
def screenshots(env_vars,browser):
        
        timestamp = timestampFormat()

        # Diretório para salvar os screenshots
        env_screenshot = env_vars.get('SCREENSHOT_PATH')

        if env_screenshot:
            screenshot_dir = f"{env_screenshot}"
            os.makedirs(screenshot_dir, exist_ok=True)  # Criar a pasta se não existir

            # Caminho do arquivo de screenshot
            screenshot_path = os.path.join(screenshot_dir, f"screenshot_web_{timestamp}.png")

            return screenshot_path 
  





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

        return driver
    
    elif mode == "SELENOID":
        browser = envValue.get("BROWSER")
        version = envValue.get('VERSION')
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

        return webdriver.Remote(
            command_executor=remote_url,
            options=options
        )




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





@pytest.fixture()
def login(browser, request):  
    """Realiza o login no sistema e retorna o WebDriver já autenticado."""
    user = request.config.getoption("user")  # Pegando o valor do parâmetro de usuário via CLI
    url = request.config.getoption("urlToUse")
    env_vars = getEnv()
    log_manager = LogManager()
    erp_url = env_vars.get(f'{url}', '')
    emailField = env_vars.get('EMAIL_FIELD', '')
    passwordField = env_vars.get('PASSWORD_FIELD', '')
    btnLogin = env_vars.get('BTN_LOGIN', '')

    if not erp_url:
        pytest.exit("Erro crítico: ERP_URL não encontrada no .env")

    email = env_vars.get(f"{user.upper()}_EMAIL", '')
    senha = env_vars.get(f"{user.upper()}_PASSWORD", '')

    if not email or not senha:
        pytest.exit(f"Erro crítico: dados de login não encontrados para o usuário {user}.")

    try:
        browser.get(f"{erp_url}login")
        log_manager.add_log(level="INFO", message="Página login carregada", routine="Login", error_details='',application_type='WEB',
)

        # Realizando login
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, emailField))).send_keys(email)
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, passwordField))).send_keys(senha)
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, btnLogin))).click()

        WebDriverWait(browser, 10).until(EC.url_changes(f"{erp_url}login"))
    except (TimeoutException, NoSuchElementException) as e:
        log_manager.add_log(level="ERROR", message="Erro ao interagir com a página de login", routine="Login", error_details=str(e))
        pytest.exit("Erro crítico: encerrando testes devido ao erro de login.")
        
    
    return browser


@pytest.fixture()
def seletor_ambiente(browser, login, log_manager, env_vars, get_ambiente,screenshots):


    execution_id = log_manager._generate_execution_id()
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
        iframe = WebDriverWait(browser, 10).until(
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
        screenshot_path = screenshots(env_vars, browser)
        
        # Verifica se o screenshot foi tirado corretamente
        if screenshot_path:
            log_manager.add_log(
                level="INFO", 
                message=f"Screenshot salvo em: {screenshot_path}", 
                routine="Login",application_type='WEB', 
                error_details=e.msg if hasattr(e, "msg") else str(e)
            )
        else:
           log_manager.add_log(
            level="ERROR", 
            message="Falha ao salvar screenshot", 
            routine="Login",application_type='WEB', 
            error_details=e.msg if hasattr(e, "msg") else str(e)
            )
                
        error_message = f"Erro durante a escolha do ambiente:TimeOutException ou NoSuchElementException {str(e)}"
        log_manager.add_log(
            level="ERROR", 
            message=error_message, 
            routine="Login",application_type='WEB', 
            error_details=e.msg if hasattr(e, "msg") else str(e)
        )
        ambienteNaoSalvo = None
        

    finally:
        log_manager.insert_logs_for_execution(execution_id)
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




@pytest.fixture()
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








@pytest.fixture()
def init(browser,login,log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection):
    return browser,login,log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection











