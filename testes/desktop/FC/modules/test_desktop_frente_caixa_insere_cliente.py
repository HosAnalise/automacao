import random
import time
import pytest
from pywinauto.keyboard import send_keys
from PIL import ImageGrab
from pywinauto.timings import TimeoutError
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.application import AppStartError


def test_desktop_inserir_cliente(log_manager, env_vars, timestampFormat, compare_images_advanced,has_connection,client_credit = "CREDIARIO"):

    if has_connection:

        timestamp = timestampFormat
        getEnv = env_vars
        screenshoot_path = getEnv.get('SCREENSHOT_PATH')
        env_application_type = getEnv.get('DESKTOP')
        userFc = getEnv.get('FC_USER', '').split(",")
    

        if not userFc:
            raise ValueError("Lista de usuários (FC_USER) está vazia no .env")

        client = random.choice(userFc)

        try:
            left, top, right, bottom = 1623, 96, 1914, 156  # Ajuste conforme necessário
            region = (left, top, right, bottom)

            before_insert_screenshot_path = f"{screenshoot_path}\\before_insert_cliente_{timestamp}.png"
            before_insert_screenshot = ImageGrab.grab(bbox=region)
            before_insert_screenshot.save(before_insert_screenshot_path)

            time.sleep(2)
            send_keys("{F4}")
            time.sleep(2)
            send_keys(f"{client}")
            time.sleep(2)
        
            for _ in range(2):
                send_keys("{ENTER}")
                time.sleep(2)


            if client_credit == "CREDIARIO":
                time.sleep(2)
                send_keys("{ENTER}")
                time.sleep(2)
            else:
                send_keys("{TAB}")
                time.sleep(2)
                send_keys("{ENTER}")
                time.sleep(2)
                
            for _ in range(2):
                send_keys("{ESC}")
                time.sleep(2)



            after_insert_screenshot_path = f"{screenshoot_path}\\after_insert_cliente_{timestamp}.png"
            after_insert_screenshot = ImageGrab.grab(bbox=region)
            after_insert_screenshot.save(after_insert_screenshot_path)

            difference = compare_images_advanced(before_insert_screenshot_path, after_insert_screenshot_path)

            if difference < 1.5:  # Define um limite de tolerância de 1.5%
                    log_manager.add_log(
                        application_type=env_application_type, 
                        level="ERROR",
                        message=f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference:.2f}% Cliente não inserido",
                        routine="Insere Venda", 
                        error_details=''
                    )
                    assert  f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference:.2f}% Cliente não inserido"
                    pytest.fail(f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference:.2f}% Cliente não inserido")
            else:
                log_manager.add_log(
                    application_type=env_application_type, 
                    level="INFO",
                    message=f"Mudança detectada! Diferença de {difference:.2f}% Cliente Inserido",
                    routine="Insere Venda", 
                    error_details=''
                )
                assert   f"Mudança detectada! Diferença de {difference:.2f}% Cliente Inserido"

                return True

        except (TimeoutError, ElementNotFoundError, AppStartError, OSError) as e:
            log_manager.add_log(
                application_type=env_application_type, 
                level="ERROR",
                message="Erro ao inserir cliente",
                routine="Insere Venda", 
                error_details=str(e)
            )
            raise  # Propaga a exceção para depuração
