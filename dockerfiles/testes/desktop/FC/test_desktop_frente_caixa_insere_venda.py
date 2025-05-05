import time
import pytest
from pywinauto.application import Application
from pywinauto.timings import wait_until, TimeoutError
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.application import AppStartError
from pywinauto.keyboard import send_keys

@pytest.mark.suiteDesktopFrenteCaixa
@pytest.mark.suiteFCInsereVenda
def test_desktop_insere_venda(env_vars, log_manager):
    getEnv = env_vars
    appPath = getEnv.get('PATH_HOS_FRENTE_CAIXA')
    user = getEnv.get('PDV_EMAIL')
    password = getEnv.get('PDV_SENHA')
    env_application_type = getEnv.get('DESKTOP')
    execution_id = log_manager._generate_execution_id()

    try:
        # Iniciar o aplicativo
        app = Application(backend="uia").start(f"{appPath}")
        log_manager.add_log(
                            application_type=env_application_type,
                            level="DEBUG",
                            message="App Hos frente de caixa iniciado",
                            routine="Inserção de venda", 
                            error_details=''
                            )

        # Aguardar SplashScreen carregar
        main_window = app.window(title="SplashScreen")
        main_window.wait("ready", timeout=60)  # Espera a tela carregar completamente
        if main_window.exists():
            log_manager.add_log(
                                application_type=env_application_type, 
                                level="DEBUG",
                                message="Página inicial carregada",
                                routine="Inserção de venda",
                                error_details=''
                                )
        else:
            log_manager.add_log(
                                application_type=env_application_type, 
                                level="ERROR",
                                message=f"Main Window não encontrada: {main_window}",
                                routine="Inserção de venda",   
                                error_details=''
                                )


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
        wait_until(timeout=60, retry_interval=1, func=lambda: app.window(title_re="HOS - Frente de Caixa.*").exists())
        log_manager.add_log(
                            application_type=env_application_type, 
                            level="DEBUG",
                            message="Login realizado com sucesso", 
                            routine="Inserção de venda", 
                            error_details=''
                            )

        # Capturar a referência da janela principal após login
        principal_window = app.window(title_re="HOS - Frente de Caixa.*")
        principal_window.wait("visible", timeout=60)

        if principal_window.exists():
            principal_window.set_focus()
            log_manager.add_log(
                                application_type=env_application_type, 
                                level="DEBUG",
                                message=f"janela encontrada{principal_window}", 
                                routine="Inserção de venda", 
                                error_details=''
                                )
        else:
            log_manager.add_log(
                                application_type=env_application_type, 
                                level="ERROR",
                                message=f"Janela Principal não carregada", 
                                routine="Inserção de venda", 
                                error_details=''
                                )
    


        product_field = principal_window.child_window(auto_id="txtProduto", control_type="Edit")
        product_field.wait("enabled visible", timeout=60)
        if product_field.exists():

            log_manager.add_log(
                                application_type=env_application_type,
                                level="DEBUG",
                                message=f"Campo de produto encontrado: {product_field}",
                                routine="Inserção de venda",
                                error_details=''
                                )

            try:
                time.sleep(2)
                send_keys("FRALDA{ENTER}")
                

                time.sleep(10)
                
                
                
                # Encontrar todos os itens com o auto_id "ListViewItemProduto"

                
                
                all_itens = principal_window.descendants()
                

                log_manager.add_log(
                                        application_type=env_application_type,
                                        level="DEBUG",
                                        message=f"Descentedants encontrados: {all_itens}",
                                        routine="Inserção de venda",
                                        error_details=''

                                    )
                # Filtra apenas os itens que possuem o auto_id "ListViewItemProduto"
                item_field = [item for item in all_itens if  item.element_info.automation_id == "ListViewItemProduto"]

                log_manager.add_log(
                                        application_type=env_application_type,
                                        level="DEBUG",
                                        message=f"Lista encontrada: {item_field}",
                                        routine="Inserção de venda",
                                        error_details=''

                                    )

                if item_field:
                   
                    log_manager.add_log(
                        application_type=env_application_type,
                        level="DEBUG",
                        message=f"Produto encontrado: {item_field[0].element_info.name}",
                        routine="Inserção de venda",
                        error_details=''

                    )
                   
                    send_keys("{ENTER}")
                    time.sleep(2)  # Pequena pausa para garantir que a ação seja processada                     

                    # Espera a nova janela aparecer
                    release_window = app.window(title_re="Lançamento de Lotes.*")  # Regex para qualquer variação no título

                    if release_window.wait("exists enabled visible", timeout=60):  # Aguarda a janela realmente aparecer
                        btn_confirm = release_window.child_window(auto_id="BtnConfirmar")

                        if btn_confirm.wait("exists enabled visible", timeout=10):  # Aguarda o botão estar pronto
                            btn_confirm.click()  
                        else:
                             log_manager.add_log(
                                                application_type=env_application_type,
                                                 level="ERROR",
                                                 message=f"Botão confirmar não encontrado: {btn_confirm}",
                                                 routine="Inserção de venda", 
                                                 error_details=''
                                                )

                    else:
                        log_manager.add_log(
                                            application_type=env_application_type, 
                                            level="ERROR",
                                            message=f"janela de lançamento de lotes não renderizou: {release_window}",
                                            routine="Inserção de venda", 
                                            error_details=''
                                            )
                        send_keys("{ENTER}")  # Se a janela não apareceu, tenta pressionar ENTER novamente    
                     
                else:
                    log_manager.add_log(
                                        application_type=env_application_type, 
                                        level="ERROR",
                                        message=f"Lista de itens não encontrada: {item_field}", 
                                        routine="Inserção de venda", 
                                        error_details=''
                                        )
            except (TimeoutError, ElementNotFoundError, AppStartError,OSError,Exception) as e:
                log_manager.add_log(
                                    application_type=env_application_type, 
                                    level="ERROR",
                                    message=f"Erro ao executar o script: {str(e)}",
                                    routine="Inserção de venda", 
                                    error_details=str(e)
                                    )
        else:
            log_manager.add_log(
                                application_type=env_application_type,
                                level="ERROR",
                                message=f"Campo de produto não encontrado: {product_field}",
                                routine="Inserção de venda",
                                error_details=''
                                )
            


            
        cart_item = principal_window.child_window(auto_id="Produto1", control_type="Edit")
        cart_item.wait('exists enabled visible', timeout=60)

        if cart_item.exists():
            log_manager.add_log(
                        application_type=env_application_type,
                        level="DEBUG",
                        message=f"Item do carrinho encontrado{cart_item}",
                        routine="Inserção de venda",
                        error_details=''

                    )

            # Finalizar venda
            time.sleep(5)
            send_keys("{END}")
            time.sleep(5)
            send_keys("199900")
            time.sleep(3)  
            send_keys("{ENTER}")
            time.sleep(3)  
            send_keys("{ENTER}")
            time.sleep(3)  
            send_keys("{ESC}")
            time.sleep(3)
        else:

            # Finalizar venda
            time.sleep(5)
            send_keys("{END}")
            time.sleep(5)
            send_keys("199900")
            time.sleep(3)  
            send_keys("{ENTER}")
            time.sleep(3)  
            send_keys("{ENTER}")
            time.sleep(3)  
            send_keys("{ESC}")
            time.sleep(3)
            

        

       

    except (TimeoutError, ElementNotFoundError, AppStartError,OSError,Exception) as e:
        log_manager.add_log(
                            application_type=env_application_type, 
                            level="ERROR",
                            message="Erro ao executar o script",
                            routine="Inserção de venda", 
                            error_details=str(e)
                            )
    finally:
        log_manager.insert_logs_for_execution(execution_id)
        app.kill()