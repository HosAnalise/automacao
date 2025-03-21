import pytest
import random
import time
from pywinauto.keyboard import send_keys
from PIL import ImageGrab
from pywinauto.timings import TimeoutError
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.application import AppStartError


def test_desktop_inserir_produto(log_manager, env_vars,  timestampFormat, compare_images_advanced,has_connection,amount = 1, controlled = False):    
    if has_connection:
        
        timestamp = timestampFormat
        getEnv = env_vars
        screenshoot_path = getEnv.get('SCREENSHOT_PATH')
        env_application_type = getEnv.get('DESKTOP')
        product_list = getEnv.get('PRODUCT_LIST').split(",")
        controlled_product_list =  getEnv.get('CONTROLLED_PRODUCT_LIST').split(",")

        try:

            left, top, right, bottom = 349, 95, 1469, 120  # Coordenadas do campo produto
            # Definir a região específica da captura
            region = (left, top, right, bottom)

            # Capturar screenshot antes da inserção
            before_insert_screenshot_path = f"{screenshoot_path}\\before_insert_produto_{timestamp}.png"
            before_insert_screenshot = ImageGrab.grab(bbox=region)
            before_insert_screenshot.save(before_insert_screenshot_path)

            if controlled:
                product = random.choice(controlled_product_list)
            
            else:
                product = random.choice(product_list)   
                
            time.sleep(2)
            send_keys(f"{product}")
            time.sleep(2)    

            
            # Capturar screenshot após a inserção
            after_insert_screenshot_path = f"{screenshoot_path}\\after_insert_produto_{timestamp}.png"
            after_insert_screenshot = ImageGrab.grab(bbox=region)
            after_insert_screenshot.save(after_insert_screenshot_path)
            for _ in range(2):
                send_keys("{ENTER}")
                time.sleep(2)   

            # Comparar as imagens para verificar se houve mudança
            difference = compare_images_advanced(before_insert_screenshot_path, after_insert_screenshot_path)

            if difference < 1.5:  # Define um limite de tolerância de 1.5%
                log_manager.add_log(
                    application_type=env_application_type, 
                    level="ERROR",
                    routine="Insere Venda",
                    message=f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference:.2f}% Produto não inserido", 
                    error_details=''
                )
                assert difference < 1.5, f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference:.2f}% Produto não inserido" 
                pytest.fail(f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference:.2f}% Produto não inserido")
            else:
                log_manager.add_log(
                    application_type=env_application_type, 
                    level="INFO",
                    routine="Insere Venda",
                    message=f"Mudança detectada! Diferença de {difference:.2f}% Produto Inserido", 
                    error_details=''
                )
                assert  f"Mudança detectada! Diferença de {difference:.2f}% Produto Inserido"
                
                for _ in range(4): 
                    send_keys("{ENTER}")
                    time.sleep(2)

                if amount > 1:
                    send_keys("{INSERT}")
                    time.sleep(2)
                    send_keys(f"{amount}{{ENTER}}")
                    time.sleep(2) 
                    if amount > 200:
                        send_keys("{ENTER}")
                        time.sleep(2)          
                
                assert  f"Mudança detectada! Diferença de {difference:.2f}% Produto Inserido"

        except (TimeoutError, ElementNotFoundError, AppStartError, OSError, Exception) as e:
            log_manager.add_log(
                application_type=env_application_type, 
                level="ERROR",
                message="Erro ao finalizar inserção do produto",
                routine="Insere Venda", 
                error_details=str(e)
            )
            raise  # Levanta a exceção para tratamento posterior, se necessário








