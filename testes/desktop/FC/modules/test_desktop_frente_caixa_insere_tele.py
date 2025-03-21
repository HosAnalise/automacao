import pytest
import random
import time
from PIL import ImageGrab
from pywinauto.keyboard import send_keys

def test_desktop_inserir_tele_entrega(log_manager,env_vars, timestampFormat,   compare_images_advanced, has_connection):
    if has_connection:
            
        getEnv = env_vars
        env_application_type = getEnv.get("DESKTOP")
        screenshoot_path = getEnv.get('SCREENSHOT_PATH')
        timestamp = timestampFormat
        delivery = random.randint(0, 5)  


        try:
                    
            left, top, right, bottom = 1864, 218, 1894, 248  # Coordenadas do campo frete
            region = (left, top, right, bottom)

            # Capturar screenshot antes da inserção
            before_insert_screenshot_path = f"{screenshoot_path}\\before_insert_delivery_{timestamp}.png"
            before_insert_screenshot = ImageGrab.grab(bbox=region)
            before_insert_screenshot.save(before_insert_screenshot_path)

            time.sleep(2)
            send_keys("{F5}")
            time.sleep(2)


            # Simular pressionamento de tecla "DOWN" delivery vezes
            for _ in range(delivery):
                send_keys("{DOWN}")

            time.sleep(1)
            send_keys("{ENTER}")
            time.sleep(2)   
            # Capturar screenshot após a inserção
            after_insert_screenshot_path = f"{screenshoot_path}\\after_insert_delivery_{timestamp}.png"
            after_insert_screenshot = ImageGrab.grab(bbox=region)
            after_insert_screenshot.save(after_insert_screenshot_path)


        

            # Comparar imagens
            difference = compare_images_advanced(before_insert_screenshot_path, after_insert_screenshot_path)

            if difference < 1.5:  # Define um limite de tolerância de 1.5%
                log_manager.add_log(
                    application_type=env_application_type,
                    level="ERROR",
                    routine="Insere Venda",
                    message=f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference:.2f}% Tele entrega não adicionada",
                    error_details="",
                )
                pytest.fail(f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference:.2f}% Tele entrega não adicionada")
            else:
                log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    routine="Insere Venda",
                    message=f"Mudança detectada! Diferença de {difference:.2f}%. Tele entrega adicionada",
                    error_details="",
                )
                return True
                
        
        except (OSError, Exception) as e:
            log_manager.add_log(
                application_type=env_application_type,
                level="ERROR",
                message="Erro ao inserir tele",
                routine="Insere Venda",
                error_details=str(e),
            )
