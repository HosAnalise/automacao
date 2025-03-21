import pytest
import json
import random
import time
from pywinauto.keyboard import send_keys
from pywinauto.mouse import click
from PIL import ImageGrab
from pywinauto.timings import TimeoutError
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.application import AppStartError

def test_desktop_finalizar_venda(log_manager, env_vars, timestampFormat, compare_images_advanced,has_connection, payment_methods="DINHEIRO",has_client=False):
    
    if has_connection:

        timestamp = timestampFormat
        getEnv = env_vars
        payment_method_str = getEnv.get("PAYMENT_METHODS")
        payment_method = json.loads(payment_method_str)
        screenshoot_path = getEnv.get('SCREENSHOT_PATH')
        env_application_type = getEnv.get('DESKTOP')
        random_number = random.randint(100000,999999)
        days = random.randint(1,31)
        gift_card = 150397956815
        

        try:

            left, top, right, bottom = 1617, 259, 1920, 934  # Ajuste as coordenadas conforme sua tela
            # Definir a região específica da captura
            region = (left, top, right, bottom)

            # Capturar screenshot antes da inserção
            before_insert_screenshot_path = f"{screenshoot_path}\\before_finaliza_venda_{timestamp}.png"
            before_insert_screenshot = ImageGrab.grab(bbox=region)
            before_insert_screenshot.save(before_insert_screenshot_path)

            time.sleep(2)
            if payment_methods == "CONVENIO":
                # Clica na posição específica
                click(coords=(1860, 177))


                
            time.sleep(2)
            send_keys("{END}")
            time.sleep(4)

            left1, top1, right1, bottom1 = 824, 319, 1453, 688  # Ajuste as coordenadas conforme sua tela

            # Definir a região específica da captura
            region1 = (left1, top1, right1, bottom1)

            # Capturar screenshot antes da inserção
            before_insert_screenshot_path1 = f"{screenshoot_path}\\before_finaliza_venda_1{timestamp}.png"
            before_insert_screenshot1 = ImageGrab.grab(bbox=region)
            before_insert_screenshot1.save(before_insert_screenshot_path1)

            if payment_methods == "DINHEIRO":
                for _ in range(payment_method["DINHEIRO"]):  # Pressiona TAB 'valor' vezes para CARTAO
                    send_keys("{TAB}")
                send_keys("{ENTER}")
                send_keys("{ENTER}")
            elif payment_methods == "CARTAO":
                for _ in range(payment_method["CARTAO"]):  # Pressiona TAB 'valor' vezes para CARTAO
                    send_keys("{TAB}")
                time.sleep(2)
                send_keys("{ENTER}")
                time.sleep(3)
                send_keys("{ENTER}")
                time.sleep(3)
                send_keys("{ENTER}")
                time.sleep(3)
                send_keys(f"{random_number}")
                time.sleep(3)
                send_keys("{ENTER}")
                time.sleep(3)
                send_keys(f"{random_number}")
                time.sleep(3)
                send_keys("{ENTER}")
            elif payment_methods == "PIX":
                for _ in range(payment_method["PIX"]):  # Pressiona TAB 'valor' vezes para PIX
                    send_keys("{TAB}")
                for _ in range(3):   
                    send_keys("{ENTER}")
                    time.sleep(3)
            
                send_keys("{TAB}")
                time.sleep(1)
                send_keys("{TAB}")
                time.sleep(1)
                send_keys("{ENTER}")
            elif payment_methods == "CHEQUE":
                for _ in range(payment_method["CHEQUE"]):  # Pressiona TAB 'valor' vezes para CHEQUE
                    send_keys("{TAB}")
                time.sleep(1)    
                send_keys("{ENTER}")
                time.sleep(1)
                send_keys("{ENTER}")
                time.sleep(2)
                send_keys(f"{random_number}{{ENTER}}")
                time.sleep(1)
                send_keys(f"{random_number}{{ENTER}}")
                time.sleep(1)
                send_keys(f"{random_number}{{ENTER}}")
                time.sleep(1)
                send_keys(f"{random_number}{{ENTER}}")
                time.sleep(1)
                send_keys(f"{random_number}{{ENTER}}")
                time.sleep(1)
                send_keys(f"{random_number}{{ENTER}}")
                time.sleep(1)
                send_keys("{ENTER}")
                time.sleep(2)
                for _ in range(9):
                    send_keys("{ENTER}")
                    time.sleep(0.5)
                
            elif payment_methods == "CHEQUE_PRE":
                for _ in range(payment_method["CHEQUE_PRE"]):  # Pressiona TAB 'valor' vezes para CHEQUE PRE
                    send_keys("{TAB}")
                time.sleep(1)    
                send_keys("{ENTER}")
                time.sleep(3)
                send_keys("{ENTER}")
                time.sleep(2)
                send_keys(f"{random_number}{{ENTER}}")
                time.sleep(1)
                send_keys(f"{random_number}{{ENTER}}")
                time.sleep(1)
                send_keys(f"{random_number}{{ENTER}}")
                time.sleep(1)
                send_keys(f"{random_number}{{ENTER}}")
                time.sleep(1)
                send_keys(f"{random_number}{{ENTER}}")
                time.sleep(1)
                send_keys(f"{random_number}{{ENTER}}")
                time.sleep(1)
                send_keys("{ENTER}")
                time.sleep(2)
                for _ in range(7):
                    send_keys("{ENTER}")
                    time.sleep(0.5)

                send_keys(f"{days}{{ENTER}}")

                for _ in range(2):
                    send_keys("{ENTER}")
                    time.sleep(0.5) 
            
            elif payment_methods == "CRT_PRESENTE":
                for _ in range(payment_method["CRT_PRESENTE"]):  # Pressiona TAB 'valor' vezes para CRT_PRESENTE
                    send_keys("{TAB}")
                time.sleep(1)
                send_keys("{ENTER}")
                time.sleep(1)
                send_keys("{TAB}")
                time.sleep(1.5)
                send_keys("{ENTER}")
                time.sleep(1)
                send_keys(f"{gift_card}{{ENTER}}")        
                time.sleep(1.5)
                send_keys("{ENTER}")

                
            elif payment_methods == "DEPOSITO":
                for _ in range(payment_method["DEPOSITO"]):  # Pressiona TAB 'valor' vezes para DEPOSITO
                    send_keys("{TAB}")
                send_keys("{ENTER}")
                time.sleep(1)
                send_keys("{ENTER}")
            elif payment_methods == "TRANSFERENCIA":
                for _ in range(payment_method["TRANSFERENCIA"]):  # Pressiona TAB 'valor' vezes para TRANSFERENCIA
                    send_keys("{TAB}")
                send_keys("{ENTER}")
                time.sleep(1)
                send_keys("{ENTER}")
            elif payment_methods == "BOLETO" and has_client:
                for _ in range(payment_method["BOLETO"]):  # Pressiona TAB 'valor' vezes para BOLETO
                    send_keys("{TAB}")
                send_keys("{ENTER}")
                time.sleep(2)
                send_keys("{ENTER}")
                time.sleep(1)
                send_keys("{ENTER}")
                time.sleep(1)
                send_keys(f"{days}{{ENTER}}")
                for _ in range(4):
                    send_keys("{ENTER}")
                    time.sleep(1.5)
            elif payment_methods == "CREDIARIO" and has_client:
                for _ in range(payment_method["CREDIARIO"]):  # Pressiona TAB 'valor' vezes para CREDIARIO
                    send_keys("{TAB}")
                for _ in range(5):    
                    send_keys("{ENTER}")
                    time.sleep(2)
            elif payment_methods == "CONVENIO" and has_client:
                for _ in range(payment_method["CONVENIO"]):
                    send_keys("{TAB}")
                    time.sleep(1)
                for _ in range(5):
                    send_keys("{ENTER}")
                    time.sleep(1)                         

            time.sleep(5)
            send_keys("{TAB}")
            time.sleep(5)
            send_keys("{ENTER}")
            time.sleep(5)
            for _ in range(5):
                send_keys("{ESC}")
                time.sleep(5)
            send_keys('%{F4}')    
            time.sleep(5)

            # Capturar screenshot após a inserção
            after_insert_screenshot_path1 = f"{screenshoot_path}\\after_finaliza_venda_{timestamp}.png"
            after_insert_screenshot1 = ImageGrab.grab(bbox=region1)
            after_insert_screenshot1.save(after_insert_screenshot_path1)


            # Capturar screenshot após a inserção
            after_insert_screenshot_path = f"{screenshoot_path}\\after_finaliza_venda_{timestamp}.png"
            after_insert_screenshot = ImageGrab.grab(bbox=region)
            after_insert_screenshot.save(after_insert_screenshot_path)

            # Comparar as imagens para verificar se houve mudança
            difference = compare_images_advanced(before_insert_screenshot_path, after_insert_screenshot_path)

            if difference < 1.5:  # Define um limite de tolerância de 1.5%
                log_manager.add_log(
                    application_type=env_application_type, 
                    level="ERROR",
                    message=f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference:.2f}% venda não finalizada: {payment_methods}",
                    routine="Insere Venda", 
                    error_details=''
                )
                assert difference < 1.5, f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference:.2f}% venda não finalizada"
                pytest.fail(f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference:.2f}% venda não finalizada: {payment_methods}")

            else:
                log_manager.add_log(
                    application_type=env_application_type, 
                    level="INFO",
                    message=f"Mudança detectada! Diferença de {difference:.2f}% Venda finalizada",
                    routine="Insere Venda", 
                    error_details=''
                )
                


            difference2 = compare_images_advanced(before_insert_screenshot_path1, after_insert_screenshot_path1)

            if difference2 < 1.5:  # Define um limite de tolerância de 1.5%
                log_manager.add_log(
                    application_type=env_application_type, 
                    level="ERROR",
                    message=f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference2:.2f}% venda não finalizada: {payment_methods}",
                    routine="Insere Venda", 
                    error_details=''
                )
                assert  f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference2:.2f}% venda não finalizada"
                pytest.fail(f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference2:.2f}% venda não finalizada: {payment_methods}")
            else:
                log_manager.add_log(
                    application_type=env_application_type, 
                    level="INFO",
                    message=f"Mudança detectada! Diferença de {difference2:.2f}% Venda finalizada",
                    routine="Insere Venda", 
                    error_details=''
                )
                assert  f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference2:.2f}% venda não finalizada"
            
        except (TimeoutError, ElementNotFoundError, AppStartError, OSError, Exception) as e:
            log_manager.add_log(
                application_type=env_application_type, 
                level="ERROR",
                message="Erro ao finalizar venda",
                routine="Insere Venda", 
                error_details=str(e)
            )
            raise  # Levanta a exceção para tratamento posterior, se necessário
