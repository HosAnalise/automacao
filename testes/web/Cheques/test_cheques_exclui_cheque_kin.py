from tabnanny import check
import time
from turtle import Turtle
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.Components import Components
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.rotinas.Cheques import Cheques

#===================================================================================================
# TESTE NÃO COMPLETO, NÃO FOI POSSIVEL ACHAR UM CHEQUE QUE DÊ PARA EXCLUIR, LÓGICA É PARA FUNCIONAR
#===================================================================================================

@pytest.mark.parametrize("cheque, devePassar",[
    (   
        Cheques.Cheque(
            P130_NUMERO_CHEQUE='567856'
        ),
        True
    )
])
@pytest.mark.dockerCheques
def test_cheques_exclui_cheque(init, cheque, devePassar):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']

    try:
        FuncoesUteis.goToPage(init, Cheques.url)
        
        FuncoesUteis.showHideFilter(init, Cheques.filterSelector)

        Cheques.procuraCheque(init, cheque)

        Components.btnClick(init, ".fa.fa-edit.icon-color.edit")

        if Components.has_frame(init, "iframe[src*='cheque']"):
            Components.btnClick(init, "#B16326626606607180")

            browser.switch_to.default_content()
            Components.btnClick(init, ".js-confirmBtn.ui-button.ui-corner-all.ui-widget.ui-button--hot")

            funcionou = True if not Components.has_alert else False

            if devePassar:
                if funcionou is False:
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="WARNING",
                        message="Teste devia retornar True, porém retornou False.",
                        routine=f"{Cheques.rotina} - test_cheques_exclui_cheque",
                        error_details=""
                    )
                assert funcionou is not False

            else:
                if funcionou is not False:
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="WARNING",
                        message="Teste devia retornar False, porém retornou True.",
                        routine=f"{Cheques.rotina} - test_cheques_exclui_cheque",
                        error_details=""
                    )
                assert funcionou is False

    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine=f"{Cheques.rotina} - test_cheques_exclui_cheque", error_details=str(e))

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
            routine=f"{Cheques.rotina} - test_cheques_exclui_cheque",
            error_details=''
        )

        Log_manager.insert_logs_for_execution()

        browser.quit()