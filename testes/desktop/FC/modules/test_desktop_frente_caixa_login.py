import pytest
import time
from pywinauto.application import Application
from pywinauto.timings import wait_until, TimeoutError
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.application import AppStartError

def test_desktop_realizar_login(log_manager,env_vars,has_connection):

    if has_connection:

        getEnv = env_vars
        appPath = getEnv.get('PATH_HOS_FRENTE_CAIXA')
        user = getEnv.get('PDV_EMAIL')
        password = getEnv.get('PDV_PASSWORD')
        env_application_type = getEnv.get('DESKTOP')
    
        try:
            # Iniciar o aplicativo
            app = Application(backend="uia").start(f"{appPath}")

            log_manager.add_log(
                application_type=env_application_type,
                level="DEBUG",
                message="App Hos frente de caixa iniciado",
                routine="Insere Venda", 
                error_details=''
            )

            # Aguardar SplashScreen carregar
            main_window = app.window(title="SplashScreen")
            main_window.wait("ready", timeout=120)  # Espera a tela carregar completamente
            if main_window.exists():
                main_window.set_focus()
                time.sleep(2)
                log_manager.add_log(
                    application_type=env_application_type, 
                    level="DEBUG",
                    message="Página inicial carregada", 
                    routine="Insere Venda", 
                    error_details=''
                )
            else:
                log_manager.add_log(
                    application_type=env_application_type, 
                    level="ERROR",
                    message=f"Main Window não encontrada: {main_window}",
                    routine="Insere Venda",   
                    error_details=''
                )
                pytest.fail(f"Main Window não encontrada: {main_window}")

            # Interagir com os campos de autenticação
            user_field = main_window.child_window(auto_id="TxtUsuario", control_type="Edit")
            password_field = main_window.child_window(auto_id="TxtSenha", control_type="Edit")
            login_button = main_window.child_window(auto_id="BtnEntrar", control_type="Button")

            user_field.wait("visible", timeout=60)
            password_field.wait("visible", timeout=60)
            user_field.set_text(user)
            password_field.set_text(password)
            login_button.click()

            # Esperar a janela principal abrir após login
            wait_until(timeout=120, retry_interval=1, func=lambda: app.window(title_re="HOS - Frente de Caixa.*").exists())
            log_manager.add_log(
                application_type=env_application_type, 
                level="DEBUG",
                message="Login realizado com sucesso", 
                routine="Insere Venda", 
                error_details=''
            )

            # Capturar a referência da janela principal após login
            principal_window = app.window(title_re="HOS - Frente de Caixa.*")
            principal_window.wait("visible", timeout=120)

            if principal_window.exists():
                principal_window.set_focus()
                time.sleep(5)  # Aguarda um pouco para garantir que o foco foi dado
                log_manager.add_log(
                    application_type=env_application_type, 
                    level="DEBUG",
                    message=f"Janela encontrada: {principal_window}", 
                    routine="Insere Venda", 
                    error_details=''
                )
            else:
                log_manager.add_log(
                    application_type=env_application_type, 
                    level="ERROR",
                    message="Janela Principal não carregada", 
                    routine="Insere Venda", 
                    error_details=''
                )
                pytest.fail("Janela Principal não carregada")
                
            return app  # Retorna o objeto 'app' para outros usos

        except (TimeoutError, ElementNotFoundError, AppStartError, OSError, Exception) as e:
            log_manager.add_log(
                application_type=env_application_type, 
                level="ERROR",
                message="Erro ao realizar login",
                routine="Insere Venda", 
                error_details=str(e)
            )
            raise  # Levanta a exceção para tratamento posterior, se necessário
