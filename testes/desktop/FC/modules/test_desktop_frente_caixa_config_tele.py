import time
import requests
import random
import pytest
from pywinauto.keyboard import send_keys
from pywinauto.mouse import click
from pywinauto.timings import TimeoutError
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.application import AppStartError
from PIL import ImageGrab


# Dicionário de faixas de CEPs por estado no Brasil
ceps = {
    "AC": (69900, 69999),
    "AL": (57000, 57999),
    "AM": (69000, 69299),
    "AP": (68900, 68999),
    "BA": (40000, 48999),
    "CE": (60000, 63999),
    "DF": (70000, 73699),
    "ES": (29000, 29999),
    "GO": (72800, 76799),
    "MA": (65000, 65999),
    "MG": (30000, 39999),
    "MS": (79000, 79999),
    "MT": (78000, 78899),
    "PA": (66000, 68899),
    "PB": (58000, 58999),
    "PE": (50000, 56999),
    "PI": (64000, 64999),
    "PR": (80000, 87999),
    "RJ": (20000, 28999),
    "RN": (59000, 59999),
    "RR": (69300, 69399),
    "RS": (90000, 99999),
    "SC": (88000, 89999),
    "SE": (49000, 49999),
    "SP": (10000, 19999),
    "TO": (77000, 77999),
}

def generate_cep(state=None):
    """Gera um CEP real baseado nos prefixos de Estados brasileiros."""
    if state and state.upper() in ceps:
        prefix = ceps[state.upper()]
    else:
        prefix = random.choice(list(ceps.values()))  

    cep = random.randint(prefix[0] * 1000, prefix[1] * 1000 + 999)  # Garante 8 dígitos
    return f"{str(cep)[:5]}-{str(cep)[5:]}"  # Formata corretamente como XXXXX-XXX

print(generate_cep())


def get_random_real_cep():
    
    # Gera um CEP aleatório dentro de um intervalo válido (exemplo: São Paulo)
    random_cep = generate_cep()

    try:
        # Faz a consulta na API do ViaCEP com timeout de 10 segundos
        response = requests.get(f"https://opencep.com/v1/{random_cep}.json", timeout=10)

        # Verifica se o CEP existe
        if response.status_code == 200:
            data = response.json()
            if "erro" not in data:
                return data  # Retorna o CEP válido encontrado
    except requests.exceptions.Timeout:
        print("O tempo de conexão com o servidor excedeu o limite!")
    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro na requisição: {e}")

    return get_random_real_cep()  # Tenta novamente se o CEP não existir ou ocorreu erro




def generate_cellphone():
    ddd = random.randint(11, 99)  # Gera um DDD entre 11 e 99
    number = f"9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    return f"({ddd}) {number}"

def generate_telephone():
    ddd = random.randint(11, 99)
    number = f"{random.randint(2000, 5999)}-{random.randint(1000, 9999)}"
    return f"({ddd}) {number}"

def test_desktop_config_tele(log_manager,env_vars,timestampFormat,compare_images_advanced,has_connection ,has_client= False, has_delivery= False,payment_method = "CONVENIO"):

    if has_connection:    
        
        if has_delivery:

            timestamp = timestampFormat
            getEnv = env_vars
            env_application_type = getEnv.get('DESKTOP')
            screenshoot_path = getEnv.get('SCREENSHOT_PATH')
            random_telephone = generate_telephone()
            random_cep = '95700024'
            random_number = random.randint(1, 999)
            random_cellphone = generate_cellphone()

            try:


                    time.sleep(2)
                    if payment_method == "CONVENIO":
                        # Clica na posição específica
                        click(coords=(1860, 177))



                    if has_client:

                        time.sleep(7)
                        send_keys("{END}")
                        for _ in range(19):
                            time.sleep(1.5)
                            send_keys("{ENTER}")
                        time.sleep(4)                    

                    else:

                        time.sleep(7)
                        send_keys("{END}")
                        time.sleep(5)
                        for _ in range(6):
                            send_keys("{ENTER}")
                            time.sleep(1)

                        left, top, right, bottom = 1017, 511, 1129, 536  # Ajuste as coordenadas conforme sua tela
                        # Definir a região específica da captura
                        region = (left, top, right, bottom)

                        # Capturar screenshot antes da inserção
                        before_insert_screenshot_path = f"{screenshoot_path}\\before_insere_cep_{timestamp}.png"
                        before_insert_screenshot = ImageGrab.grab(bbox=region)
                        before_insert_screenshot.save(before_insert_screenshot_path)

                        send_keys(f"{random_cep}{{ENTER}}")
                        time.sleep(1)
                        # Capturar screenshot antes da inserção
                        after_insert_screenshot_path = f"{screenshoot_path}\\after_insere_cep_{timestamp}.png"
                        after_insert_screenshot = ImageGrab.grab(bbox=region)
                        after_insert_screenshot.save(after_insert_screenshot_path)

                        difference = compare_images_advanced(before_insert_screenshot_path, after_insert_screenshot_path)

                        if difference < 1.5:  # Define um limite de tolerância de 1.5%
                            log_manager.add_log(
                                application_type=env_application_type,
                                level="ERROR",
                                message= f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference:.2f}% Cep não adicionado",
                                routine="Insere Venda",
                                error_details="")
                            pytest.fail(f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference:.2f}% Cep não adicionado")
                        else:    
                            log_manager.add_log(
                                application_type=env_application_type,
                                level="INFO",
                                message=f"Mudança detectada! Diferença de {difference:.2f}%. Cep adicionado",
                                routine="Insere Venda",
                                error_details="")
                            
                        
                            for _ in range(7):
                                send_keys("{ENTER}")
                                time.sleep(1)

                                
                            left1, top1, right1, bottom1 = 1164, 544, 1254, 569  # Ajuste as coordenadas conforme sua tela
                            # Definir a região específica da captura
                            region1 = (left1, top1, right1, bottom1)

                            # Capturar screenshot antes da inserção
                            before_insert_screenshot_path1 = f"{screenshoot_path}\\before_finaliza_venda_{timestamp}.png"
                            before_insert_screenshot1 = ImageGrab.grab(bbox=region1)
                            before_insert_screenshot1.save(before_insert_screenshot_path1)



                            send_keys(f"{random_number}{{ENTER}}")
                            time.sleep(1)


                            # Capturar screenshot antes da inserção
                            after_insert_screenshot_path1 = f"{screenshoot_path}\\after_insere_cep_{timestamp}.png"
                            after_insert_screenshot1 = ImageGrab.grab(bbox=region1)
                            after_insert_screenshot1.save(after_insert_screenshot_path1)


                            difference1 = compare_images_advanced(before_insert_screenshot_path1, after_insert_screenshot_path1)

                            if difference1 < 1.5:  # Define um limite de tolerância de 1.5%
                                log_manager.add_log(
                                    application_type=env_application_type,
                                    level="ERROR",
                                    message= f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference1:.2f}% número não adicionado",
                                    routine="Insere Venda",
                                    error_details="")
                                pytest.fail(f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference1:.2f}% número não adicionado")
                            else:    
                                log_manager.add_log(
                                    application_type=env_application_type,
                                    level="INFO",
                                    message=f"Mudança detectada! Diferença de {difference1:.2f}%. número adicionado",
                                    routine="Insere Venda",
                                    error_details="")

                            


                            left2, top2, right2, bottom2 = 784, 676, 924, 701  # Ajuste as coordenadas conforme sua tela
                            # Definir a região específica da captura
                            region2 = (left2, top2, right2, bottom2)

                            # Capturar screenshot antes da inserção
                            before_insert_screenshot_path2 = f"{screenshoot_path}\\before_finaliza_venda_{timestamp}.png"
                            before_insert_screenshot2 = ImageGrab.grab(bbox=region2)
                            before_insert_screenshot2.save(before_insert_screenshot_path2)

                            send_keys(f"{random_telephone}{{ENTER}}")
                            time.sleep(1)

                            # Capturar screenshot antes da inserção
                            after_insert_screenshot_path2 = f"{screenshoot_path}\\after_insere_cep_{timestamp}.png"
                            after_insert_screenshot2 = ImageGrab.grab(bbox=region2)
                            after_insert_screenshot2.save(after_insert_screenshot_path2)


                            difference2 = compare_images_advanced(before_insert_screenshot_path2, after_insert_screenshot_path2)

                            if difference2 < 1.5:  # Define um limite de tolerância de 1.5%
                                log_manager.add_log(
                                    application_type=env_application_type,
                                    level="ERROR",
                                    message= f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference2:.2f}% number telephone não adicionado",
                                    routine="Insere Venda",
                                    error_details="")
                                pytest.fail(f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference2:.2f}% number telephone não adicionado")
                            else:
                                log_manager.add_log(
                                    application_type=env_application_type,
                                    level="INFO",
                                    message=f"Mudança detectada! Diferença de {difference2:.2f}%. number telephone adicionado",
                                    routine="Insere Venda",
                                    error_details="")

                                for _ in range(2):
                                    send_keys("{ENTER}")
                                time.sleep(1)

                            left3, top3, right3, bottom3 = 982, 676, 1122, 701  # Ajuste as coordenadas conforme sua tela
                            # Definir a região específica da captura
                            region3 = (left3, top3, right3, bottom3)

                            # Capturar screenshot antes da inserção
                            before_insert_screenshot_path3 = f"{screenshoot_path}\\before_finaliza_venda_{timestamp}.png"
                            before_insert_screenshot3 = ImageGrab.grab(bbox=region3)
                            before_insert_screenshot3.save(before_insert_screenshot_path3)
                            
                            send_keys(f"{random_cellphone}{{ENTER}}")
                            time.sleep(1)
                            # Capturar screenshot antes da inserção
                            after_insert_screenshot_path3 = f"{screenshoot_path}\\after_insere_cep_{timestamp}.png"
                            after_insert_screenshot3 = ImageGrab.grab(bbox=region3)
                            after_insert_screenshot3.save(after_insert_screenshot_path3)

                            difference3 = compare_images_advanced(before_insert_screenshot_path3, after_insert_screenshot_path3)    

                            if difference3 < 1.5:  # Define um limite de tolerância de 1.5%
                                log_manager.add_log(
                                    application_type=env_application_type,
                                    level="ERROR",
                                    message= f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference3:.2f}% number cellphone não adicionado",
                                    routine="Insere Venda",
                                    error_details="")
                                pytest.fail(f"Erro: Nenhuma mudança detectada! Diferença de apenas {difference3:.2f}% number cellphone não adicionado")
                            else:
                                log_manager.add_log(
                                    application_type=env_application_type,
                                    level="INFO",
                                    message=f"Mudança detectada! Diferença de {difference3:.2f}%. number cellphone adicionado",
                                    routine="Insere Venda",
                                    error_details="")
                                
                                for _ in range(2):
                                    send_keys("{ENTER}")
                                time.sleep(4)    
            except (TimeoutError, ElementNotFoundError, AppStartError, OSError, Exception) as e:
                    log_manager.add_log(
                        application_type=env_application_type, 
                        level="ERROR",
                        message="Erro ao finalizar Configuração de tele entrega",
                        routine="Insere Venda", 
                        error_details=str(e)
                    )
                    raise  # Levanta a exceção para tratamento posterior, se necessário


                            

            









