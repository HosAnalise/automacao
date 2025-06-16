from tabnanny import check
import time
import pytest
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.Components import Components
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.rotinas.ContasReceber import ContaReceber

@pytest.mark.parametrize("infoConta, devePassar", [
    (
        ContaReceber.Conta(
            P85_LOJA='2381'
        ),
        True
    )
    
])
@pytest.mark.dockerContaReceber
def test_contaReceber_botao_empresa(init, infoConta, devePassar):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']

    try:
        FuncoesUteis.goToPage(init, ContaReceber.url)

        FuncoesUteis.showHideFilter(init, ContaReceber.filterSelector)

        Components.btnClick(init, "#B392477272658547904") #nova conta

        if ContaReceber.preencheCamposConta(init, infoConta):
            funcionou = ContaReceber.testaBtnEmpresa(init)

            if devePassar:
                if funcionou is False:
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="WARNING",
                        message="Teste devia retornar True, porém retornou False.",
                        routine=f"{ContaReceber.rotina} - test_contaReceber_botao_empresa",
                        error_details=""
                    )
                assert funcionou is not False

            else:
                if funcionou is not False:
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="WARNING",
                        message="Teste devia retornar False, porém retornou True.",
                        routine=f"{ContaReceber.rotina} - test_contaReceber_botao_empresa",
                        error_details=""
                    )
                assert funcionou is False

    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine=f"{ContaReceber.rotina} - test_contaReceber_botao_empresa", error_details=str(e))
        
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
            routine=f"{ContaReceber.rotina} - test_contaReceber_botao_empresa",
            error_details=''
        )

        Log_manager.insert_logs_for_execution()

        browser.quit()