# conftest.py
from email.mime import application
import os
import random
import time
import pytest
from pywinauto import Application
from dotenv import dotenv_values, load_dotenv
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from classes.utils.LogManager import LogManager

env_application_type = os.getenv("APPLICATION_TYPE")
load_dotenv(r"C:\Users\GabrielSiqueiraHOSSi\Desktop\Automacao\.env.desktop")


# Modelo de configuração centralizado
class AppConfig(BaseModel):
    login_path: str
    username: str
    password: str

    @classmethod
    def from_env(cls):
        return cls(
            login_path=os.getenv("LOGINPATH"),
            username=os.getenv("USER"),
            password=os.getenv("PASSWORD")
        )


@pytest.fixture(scope="session")
def config() -> AppConfig:
    return AppConfig.from_env()


@pytest.fixture(scope="function")
def app(config: AppConfig):
    app_instance = Application(backend="uia").start(config.login_path)
    yield app_instance
    app_instance.kill()


@pytest.fixture(scope="function")
def login(app, config: AppConfig):
    # Aguarda a janela de login
    login_window = app.window(title="HOS - Farma Splash")
    login_window.wait("visible", timeout=30)

    # Interage com os campos
    user_field = login_window.child_window(auto_id="TxtUsuario", control_type="Edit").wait("exists enabled visible ready", timeout=15)
    user_field.set_text(config.username)

    pass_field = login_window.child_window(auto_id="TxtSenha", control_type="Edit")
    pass_field.set_text(config.password)

    btn_login = login_window.child_window(auto_id="BtnEntrar", control_type="Button")
    btn_login.click()

    yield  True




def getEnv():
    env_vars = dotenv_values(".env.desktop") 
    return env_vars

@pytest.fixture
def env_vars():
    return getEnv()

@pytest.fixture
def alchemy_connection():
    """
    Conecta ao banco de dados usando SQLAlchemy e retorna a conexão.
    """
    try:
        engine = create_engine("firebird+fdb://SYSDBA:masterkey@server-farma/C:/caminho/para/cadastro.fdb")
        connection = engine.connect()
        return connection
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None    

@pytest.fixture(scope="function")
def getQueryResults(log_manager):
    Log_manager=log_manager

    def querys(queries:dict, limit:int=10, random_choice:bool=True)-> dict:
        """
        Retorna o resultado de uma query, ou se o usurio quiser apenas um valor aleatorio dessa query.

        :param init: Tupla contendo os objetos necessários:
                        (browser, login, Log_manager, get_ambiente, env_vars,
                        seletor_ambiente, screenshots, oracle_db_connection).
        :param queries: Dict contendo todas as queries a serem realizadas. 
        :param limit: int limita os resultados das queryes 
        :param random_choice: bool permite o usuario escolher se a query vem com o valor total ou apenas um valor aleatorio
        :return: Retorna um dicionario {"Query_nomeQuery": valor}

        """
        def executar_query(connection, query):
            result = connection.execute(text(query))
            return [row[0] for row in result.fetchmany(limit)]
    
        start = time.time()
        conn = alchemy_connection()

        def obter_valor(lista):
            if random_choice:
                return random.choice(lista) if lista else None
            return lista if lista else []

        try:
            results = {}

            for key, query in queries.items():
                results[key] = executar_query(conn, query)

            queryResults = {key: obter_valor(result) for key, result in results.items()}
            return queryResults

        except Exception as e:
            Log_manager.add_log(application_type=env_application_type, level="Error", message="Erro na execução das queries", routine="", error_details=str(e))
            return {"error": str(e)}
        
        finally:
            conn.close()
            endTime = time.time()
            Log_manager.add_log(
                application_type=app,
                level="INFO",
                message=f"Tempo de execução das queries: {int((endTime-start)//60)} min {int((endTime-start)%60)} s {int(((endTime-start)%1)*1000)} ms",
                routine="",
                error_details=''
            )

    return querys

@pytest.fixture
def log_manager():
    return LogManager()