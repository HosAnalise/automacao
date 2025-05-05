from pywinauto.keyboard import send_keys
from pywinauto.mouse import click
from PIL import ImageGrab
from pywinauto.timings import TimeoutError
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.application import AppStartError
import time
import pytest






def test_desktop_config_controlados(log_manager, env_vars, timestampFormat, compare_images_advanced,has_connection,controlled =  False, has_client = False):
 
    if has_connection:

        if controlled:

            getEnv = env_vars
            screenshoot_path = getEnv.get('SCREENSHOT_PATH')
            env_application_type = getEnv.get('DESKTOP') 
            prescription_number = getEnv.get('PRESCRIPTION_NUMBER')
            key_press = 11
            timestamp = timestampFormat

            try:                     
                    send_keys("{END}")
                    time.sleep(2)
                    send_keys("{F2}")
                    time.sleep(5)
                    send_keys("{ENTER}")

                    left, top, right, bottom = 1269, 308, 1389, 333  # campo de inserção de numero da receita
                
                    # Definir a região específica da captura
                    region = (left, top, right, bottom)

                    # Capturar screenshot antes da inserção
                    before_insert_screenshot_path = f"{screenshoot_path}\\before_insere_receita_{timestamp}.png"
                    before_insert_screenshot = ImageGrab.grab(bbox=region)
                    before_insert_screenshot.save(before_insert_screenshot_path)


                    time.sleep(3)
                    for _ in range(10):
                        send_keys("{BACKSPACE}")  # Alternativa para Backspace
                    send_keys(f"{prescription_number}")  # Insere o novo valor
                    time.sleep(1)
                

                    # Capturar screenshot antes da inserção
                    after_insert_screenshot_path = f"{screenshoot_path}\\after_insere_receita_{timestamp}.png"
                    after_insert_screenshot = ImageGrab.grab(bbox=region)
                    after_insert_screenshot.save(after_insert_screenshot_path)


                    difference = compare_images_advanced(before_insert_screenshot_path, after_insert_screenshot_path)

                    if difference < 1.5: # Define um limite de tolerância de 1.5%

                        log_manager.add_log(
                            application_type=env_application_type,
                            level="ERROR",
                            message= f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference:.2f}% Numero da receita não adicionado",
                            routine="Insere Venda",
                            error_details="")
                        
                        pytest.fail(f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference:.2f}% Numero da receita não adicionado")
                    else:    

                        log_manager.add_log(
                            application_type=env_application_type,
                            level="INFO",
                            message=f"Mudança detectada! Diferença de {difference:.2f}%. Numero da receita adicionado",
                            routine="Insere Venda",
                            error_details="")
                        

                    time.sleep(3)
                    send_keys("{ENTER}")
                    time.sleep(2)
                    for _ in range(3):
                        send_keys("{ENTER}")
                        time.sleep(1)

                    
                    left1, top1, right1, bottom1 = 609, 434, 1063, 459  # campo de inserção prescritor da receita
                    # Definir a região específica da captura
                    region1 = (left1, top1, right1, bottom1)

                    # Capturar screenshot antes da inserção
                    before_insert_screenshot_path1 = f"{screenshoot_path}\\before_insere_prescritor_{timestamp}.png"
                    before_insert_screenshot1 = ImageGrab.grab(bbox=region1)
                    before_insert_screenshot1.save(before_insert_screenshot_path1)    

                    send_keys("TESTE{ENTER}")
                    time.sleep(2)
                    send_keys("{ENTER}")
                    time.sleep(1)


                    # Capturar screenshot antes da inserção
                    after_insert_screenshot_path1 = f"{screenshoot_path}\\after_insere_prescritor_{timestamp}.png"
                    after_insert_screenshot1 = ImageGrab.grab(bbox=region1)
                    after_insert_screenshot1.save(after_insert_screenshot_path1)


                    difference1 = compare_images_advanced(before_insert_screenshot_path1, after_insert_screenshot_path1)

                    if difference1 < 1.5:  # Define um limite de tolerância de 1.5%
                        log_manager.add_log(
                            application_type=env_application_type,
                            level="ERROR",
                            message= f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference1:.2f}% Numero da receita não adicionado",
                            routine="Insere Venda",
                            error_details="")
                        pytest.fail(f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference1:.2f}% Numero da receita não adicionado")
                    else:    
                        log_manager.add_log(
                            application_type=env_application_type,
                            level="INFO",
                            message=f"Mudança detectada! Diferença de {difference1:.2f}%. Numero da receita adicionado",
                            routine="Insere Venda",
                            error_details="")

                    if not has_client:    
                        send_keys("TESTE_TESTE2{ENTER}")
                        time.sleep(2)
                        key_press = 10
                    for _ in range(key_press):
                        send_keys("{ENTER}")
                        time.sleep(1)
                    time.sleep(2)    
                    click(coords=(1302,636))    
                    time.sleep(2)
                    send_keys("{ENTER}")
                    time.sleep(1)
                    send_keys("{ESC}")

            except (TimeoutError, ElementNotFoundError, AppStartError, OSError, Exception) as e:
                log_manager.add_log(
                    application_type=env_application_type, 
                    level="ERROR",
                    message="Erro ao finalizar Configuração de Controlados",
                    routine="Insere Venda", 
                    error_details=str(e)
                )
                raise  # Levanta a exceção para tratamento posterior, se necessário

        
