import random
import time
import pytest
from pywinauto.application import Application
from pywinauto.timings import wait_until, TimeoutError
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.application import AppStartError
from pywinauto.keyboard import send_keys
from PIL import ImageGrab, Image
import numpy as np


   # Função para comparar imagens
def compare_images_advanced(image1_path, image2_path):
    img1 = Image.open(image1_path).convert("L")  # Converte para escala de cinza
    img2 = Image.open(image2_path).convert("L")

    # Converter para array numpy
    arr1 = np.array(img1)
    arr2 = np.array(img2)

    # Calcular diferença absoluta e porcentagem de diferença
    diff = np.abs(arr1 - arr2)
    diff_percentage = (np.sum(diff) / diff.size) / 255 * 100

    return diff_percentage



@pytest.mark.suiteDesktopFrenteCaixa
@pytest.mark.suiteFCInsereVenda
def test_desktop_insere_venda(env_vars, log_manager,timestampFormat):
    timestamp = timestampFormat
    getEnv = env_vars
    screenshoot_path = getEnv.get('SCREENSHOT_PATH')
    appPath = getEnv.get('PATH_HOS_FRENTE_CAIXA')
    user = getEnv.get('PDV_EMAIL')
    password = getEnv.get('PDV_SENHA')
    env_application_type = getEnv.get('DESKTOP')
    product_list  = getEnv.get('PRODUCT_LIST').split(",")
    product = random.choice(product_list)
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
            
        left, top, right, bottom = 349, 95, 1469, 120  # Coordenadas fornecidas

        # Definir a região específica da captura
        region = (left, top, right, bottom)

        # 1. Capturar screenshot antes da inserção
        before_insert_screenshot_path = f"{screenshoot_path}\\before_insert_1_{timestamp}.png"
        before_insert_screenshot = ImageGrab.grab(bbox=region)
        before_insert_screenshot.save(before_insert_screenshot_path)





        left2, top2, right2, bottom2 = 1617, 259, 1920, 934  # Coordenadas fornecidas
        # Definir a região específica da captura
        region2 = (left2, top2, right2, bottom2)

        # 1. Capturar screenshot antes da inserção
        before_insert_screenshot_path2 = f"{screenshoot_path}\\before_insert_2_{timestamp}.png"
        before_insert_screenshot2 = ImageGrab.grab(bbox=region2)
        before_insert_screenshot2.save(before_insert_screenshot_path2)

        time.sleep(5)

        send_keys(f"{product}")

        time.sleep(5)



        # 3. Capturar screenshot após a inserção
        after_insert_screenshot_path = f"{screenshoot_path}\\after_insert_1{timestamp}.png"
        after_insert_screenshot = ImageGrab.grab(bbox=region)
        after_insert_screenshot.save(after_insert_screenshot_path)


        difference = compare_images_advanced(before_insert_screenshot_path, after_insert_screenshot_path)



        if difference < 1.5:  # Define um limite de tolerância de 3% (ajuste conforme necessário)
            log_manager.add_log(
                                application_type=env_application_type, 
                                level="ERROR",
                                message="",
                                routine=f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference:.2f}% Produto não inserido", 
                                error_details=''
                                )        
        else:
            log_manager.add_log(
                                application_type=env_application_type, 
                                level="INFO",
                                message="",
                                routine=f"mudança detectada! Diferença{difference:.2f}% Produto Inserido", 
                                error_details=''
                                )        
            
            send_keys("{ENTER}")

            time.sleep(5)

            send_keys("{ENTER}")

            time.sleep(5)

            send_keys("{ENTER}")

            time.sleep(5)

            send_keys("{ENTER}")

            time.sleep(5)



        # 1. Capturar screenshot antes da inserção
        after_insert_screenshot_path2 = f"{screenshoot_path}\\after_insert_2{timestamp}.png"
        after_insert_screenshot2 = ImageGrab.grab(bbox=region2)
        after_insert_screenshot2.save(after_insert_screenshot_path2)

        difference2 = compare_images_advanced(before_insert_screenshot_path2, after_insert_screenshot_path2)






        if difference2 < 1.5:  
            log_manager.add_log(
                                application_type=env_application_type, 
                                level="ERROR",
                                message="",
                                routine=f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference2:.2f}% Produto não adicionado ao carrinho", 
                                error_details=''
                                )        
        else:
            log_manager.add_log(
                                application_type=env_application_type, 
                                level="INFO",
                                message="",
                                routine=f"mudança detectada! Diferença{difference2:.2f}% Produto adicionado ao carrinho", 
                                error_details=''
                                )

            time.sleep(5)        

            send_keys("{END}")

            time.sleep(5)

            left3, top3, right3, bottom3 = 674, 394, 794, 424  # Coordenadas fornecidas

            # Definir a região específica da captura
            region3= (left3, top3, right3, bottom3)

            # 1. Capturar screenshot antes da inserção
            before_insert_screenshot_path3 = f"{screenshoot_path}\\before_insert_3_{timestamp}.png"
            before_insert_screenshot3 = ImageGrab.grab(bbox=region3)
            before_insert_screenshot3.save(before_insert_screenshot_path3)


            time.sleep(5)

            send_keys("{TAB}")

            time.sleep(0.5)


            send_keys("{TAB}")

            time.sleep(0.5)


               # 1. Capturar screenshot antes da inserção
            after_insert_screenshot_path3 = f"{screenshoot_path}\\after_insert_3{timestamp}.png"
            after_insert_screenshot3 = ImageGrab.grab(bbox=region3)
            after_insert_screenshot3.save(after_insert_screenshot_path3)

            difference3 = compare_images_advanced(before_insert_screenshot_path3, after_insert_screenshot_path3)
            if difference3 < 1.5:  # Define um limite de tolerância de 3% (ajuste conforme necessário)
                log_manager.add_log(
                                    application_type=env_application_type, 
                                    level="ERROR",
                                    message="",
                                    routine=f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference3:.2f}% Metodo de pagamento Pix não selecionado corretamente", 
                                    error_details=''
                                    )        
            else:
                log_manager.add_log(
                                    application_type=env_application_type, 
                                    level="INFO",
                                    message="",
                                    routine=f"mudança detectada! Diferença{difference3:.2f}% Metodo de pagamento Pix selecionado corretamente", 
                                    error_details=''
                                    )        


                send_keys("{ENTER}")

                time.sleep(1)   

                send_keys("{ENTER}")

                time.sleep(5)

                send_keys("{ENTER}")

                time.sleep(5)

                send_keys("{TAB}")

                time.sleep(0.5)

                send_keys("{TAB}")

                time.sleep(0.5)

                send_keys("{ENTER}")

                time.sleep(5)

                send_keys("{ESC}")

                time.sleep(5)

                send_keys("{ESC}")


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
        
        


      








    

