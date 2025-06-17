from tabnanny import check
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.Components import Components
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.rotinas.Cheques import Cheques

@pytest.mark.parametrize("infoEmitente, infoCheque, devePassar", [
    (
        Cheques.Emitente(
            tipoEmissao='0',
            P130_CPF_CNPJ='123.456.789-11'
        ), 
        Cheques.Cheque(
            P130_LOJA='2381',
            P130_AGENCIA='3660',
            P130_BANCO_ID='8',
            P130_BOM_PARA='18/09/2025',
            P130_CMC7='352136546543213543641313543651',
            P130_CONTA='6679',
            P130_DATA_EMISSAO='25/05/2025',
            P130_DIGITO_AGENCIA='X40',
            P130_DIGITO_CONTA='9',
            P130_LOCALIZACAO='7210',
            P130_NUMERO_CHEQUE='27958',
            P130_NUMERO_SERIE='12345',
            P130_OBSERVACAO='esse teste é auto !!!',
            P130_VALOR='27,59'
        ),
        True
    )
    # ,
    # (
    #     Cheques.Emitente(
    #         tipoEmissao='1'
    #     ), 
    #     Cheques.Cheque(
    #         P130_CMC7='193570284659132847105948372610',
    #         P130_BOM_PARA='03/02/2026',
    #         P130_VALOR='66,11',
    #         P130_OBSERVACAO='robotização',
    #         P130_NUMERO_CHEQUE='22299'
    #     ),
    #     True
    # )
    # ,
    # (
    #     Cheques.Emitente(
    #         tipoEmissao='2'
    #     ),
    #     Cheques.Cheque(

    #     ),
    #     True
    # ),
])
@pytest.mark.dockerCheques
def test_cheques_criar_cheque(init, infoEmitente, infoCheque, devePassar):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']

    try:
        FuncoesUteis.goToPage(init, Cheques.url)
        
        FuncoesUteis.showHideFilter(init, Cheques.filterSelector)

        funcionou = Cheques.criaChequeCompleto(init, infoEmitente, infoCheque)

        if devePassar:
            if funcionou is False:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="WARNING",
                    message="Teste devia retornar um objeto, porém retornou False.",
                    routine=f"{Cheques.rotina} - test_cheques_criar_cheque",
                    error_details=""
                )
            assert funcionou is not False

        else:
            if funcionou is not False:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="WARNING",
                    message="Teste devia retornar False, porém retornou objeto.",
                    routine=Cheques.rotina,
                    error_details=""
                )
            assert funcionou is False

    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine=f"{Cheques.rotina} - test_cheques_criar_cheque", error_details=str(e))

    finally:
        endTime = time.time()
        executionTime = endTime - starTime

        minutos = int(executionTime // 60)
        segundos = int(executionTime % 60)
        milissegundos = int((executionTime % 1) * 1000)

        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Tempo de execução do teste: {minutos} min {segundos} s {milissegundos} ms",
            routine=f"{Cheques.rotina} - test_cheques_criar_cheque",
            error_details=''
        )

        Log_manager.insert_logs_for_execution()

        browser.quit()