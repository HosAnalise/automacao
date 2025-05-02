import time
import pytest
from pywinauto.application import Application
from pywinauto.timings import wait_until, TimeoutError
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.application import AppStartError
from pywinauto.keyboard import send_keys



@pytest.mark.suiteDesktopFrenteCaixa
@pytest.mark.suiteFCInsereVenda

def test_desktop_insere_venda_com_cliente(env_vars, log_manager):
    getEnv = env_vars
    appPath = getEnv.get('PATH_HOS_FRENTE_CAIXA')
    user = getEnv.get('PDV_EMAIL')
    password = getEnv.get('PDV_SENHA')
    env_application_type = getEnv.get('DESKTOP')
    execution_id = log_manager._generate_execution_id()

    try:
        # Iniciar o aplicativo
        app = Application(backend="uia").start(f"{appPath}")
        log_manager.add_log(application_type=env_application_type,
                            level="INFO",
                            message="App Hos frente de caixa iniciado",
                            routine="Inserção de venda", 
                            error_details=''
                            )

        # Aguardar SplashScreen carregar
        main_window = app.window(title="SplashScreen")
        main_window.wait("ready", timeout=30)  # Espera a tela carregar completamente
        if main_window.exists():
            log_manager.add_log(application_type=env_application_type, 
                                level="INFO",
                                message="Página inicial carregada",
                                routine="Inserção de venda",
                                error_details=''
                                )
        else:
            log_manager.add_log(application_type=env_application_type, 
                                level="ERROR",
                                message=f"Main Window não encontrada",
                                routine="Inserção de venda", 
                                error_details=''
                                )


        # Interagir com os campos de autenticação
        user_field = main_window.child_window(auto_id="TxtUsuario", control_type="Edit")
        password_field = main_window.child_window(auto_id="TxtSenha", control_type="Edit")
        login_button = main_window.child_window(auto_id="BtnEntrar", control_type="Button")

        user_field.wait("visible", timeout=30)
        password_field.wait("visible", timeout=30)
        user_field.set_text(user)
        password_field.set_text(password)
        login_button.click()

        # Esperar a janela principal abrir após login
        wait_until(timeout=30, retry_interval=1, func=lambda: app.window(title_re="HOS - Frente de Caixa.*").exists())
        log_manager.add_log(application_type=env_application_type, 
                            level="INFO",
                            message="Login realizado com sucesso", 
                            routine="Inserção de venda", 
                            error_details=''
                            )

        # Capturar a referência da janela principal após login
        principal_window = app.window(title_re="HOS - Frente de Caixa.*")
        principal_window.wait("visible", timeout=30)

        if principal_window.exists():
            log_manager.add_log(application_type=env_application_type, 
                                level="INFO",
                                message=f"janela encontrada{principal_window}", 
                                routine="Inserção de venda", 
                                error_details=''
                                )
        else:
            log_manager.add_log(application_type=env_application_type, 
                                level="ERROR",
                                message=f"Janela Principal não carregada", 
                                routine="Inserção de venda", 
                                error_details=''
                                )
    


        product_field = principal_window.child_window(auto_id="txtProduto", control_type="Edit")
        product_field.wait("visible", timeout=30)
        if product_field.exists():
            try:
                send_keys("FRALDA{ENTER}")

                time.sleep(5)
                # Encontrar todos os itens com o auto_id "ListViewItemProduto"
                todos_os_controles = principal_window.descendants()
                item_field = [controle for controle in todos_os_controles if controle.element_info.automation_id == "ListViewItemProduto"]
                if item_field:
                    send_keys("{ENTER}")  # Pressiona ENTER para abrir a janela
                    time.sleep(2)  # Pequena pausa para garantir que a janela comece a abrir

                    # Espera a nova janela aparecer
                    release_window = app.window(title_re="Lançamento de Lotes.*")  # Regex para qualquer variação no título

                    if release_window.wait("exists enabled visible", timeout=30):  # Aguarda a janela realmente aparecer
                        btn_confirm = release_window.child_window(auto_id="BtnConfirmar")

                        if btn_confirm.wait("exists enabled visible", timeout=10):  # Aguarda o botão estar pronto
                            btn_confirm.click()  
                        else:
                             log_manager.add_log(application_type=env_application_type,
                                                 level="ERROR",
                                                 message=f"Botão confirmar não encontrado: {btn_confirm}",
                                                 routine="Inserção de venda", 
                                                 error_details=str(e)
                                                )

                    else:
                        log_manager.add_log(application_type=env_application_type, 
                                            level="ERROR",
                                            message=f"janela de lançamento de lotes não renderizou: {release_window}",
                                            routine="Inserção de venda", 
                                            error_details=str(e)
                                            )
                        send_keys("{ENTER}")  # Se a janela não apareceu, tenta pressionar ENTER novamente    
                     
                else:
                    log_manager.add_log(application_type=env_application_type, 
                                        level="ERROR",
                                        message=f"Item não encontrado: {item_field}", 
                                        routine="Inserção de venda", 
                                        error_details='')
            except (TimeoutError, ElementNotFoundError, AppStartError) as e:
                log_manager.add_log(application_type=env_application_type, 
                                    level="ERROR",
                                    message=f"Erro ao executar o script: {str(e)}",
                                    routine="Inserção de venda", 
                                    error_details=str(e)
                                    )
        else:
            log_manager.add_log(application_type=env_application_type,
                                level="ERROR",
                                message=f"Campo de produto não encontrado: {product_field}",
                                routine="Inserção de venda",
                                error_details=''
                                )


        client_field = principal_window.child_window(auto_id="lblNomeConsumidor")    
        client_field.wait('visible',timeout=30)
        if client_field.exists():
            # principal_window.print_control_identifiers()

            send_keys("{F4}")
            time.sleep(5)
            send_keys("JOAO{ENTER}")
            
            client_list_items = principal_window.child_window(class_name="listBox").descendants(class_name="listBoxItem")

            if client_list_items:
                print(f"Total de itens encontrados: {len(client_list_items)}")
                
                # Escolhe o primeiro item (ou um específico)
                selected_item = client_list_items[0]  # Altere o índice conforme necessário
                
                selected_item.wait("exists ready visible", timeout=10)
                selected_item.click_input()  # Usa click_input() para garantir clique real
                
                send_keys("{ENTER}")  # Pressiona ENTER após selecionar
            else:
                log_manager.add_log(application_type=env_application_type, 
                                    level="ERROR",
                                    message="Nenhum item encontrado na lista de clientes",
                                    routine="Inserção de venda")

               

        else:
            log_manager.add_log(application_type=env_application_type, level="ERROR",
                                message="Campo do cliente não encontrado", routine="Inserção de venda", error_details='')

        # Finalizar venda
        send_keys("{END}")
        time.sleep(5)
        send_keys("199900")
        time.sleep(5)  
        send_keys("{ENTER}")
        time.sleep(5)  
        send_keys("{ENTER}")
        time.sleep(5)  
        send_keys("{ESC}")
        time.sleep(5)

       

    except (TimeoutError, ElementNotFoundError, AppStartError) as e:
        log_manager.add_log(application_type=env_application_type, level="ERROR",
                            message=f"Erro ao executar o script: {str(e)}",
                            routine="Inserção de venda", error_details=str(e))
    finally:
        log_manager.insert_logs_for_execution(execution_id)
        app.kill()