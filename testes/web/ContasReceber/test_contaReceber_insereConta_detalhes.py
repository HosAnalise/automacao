import time
from classes.rotinas.ContasReceber import ContaReceber
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.GerarDados import GeradorDados  
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components
import pytest
from classes.utils.decorators import com_visual

@com_visual()
@pytest.mark.dockercontaReceber
def test_contaReceber_insereConta_detalhes(init,validator=None):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['APPLICATION_TYPE']

    try:

        FuncoesUteis.goToPage(init,ContaReceber.url)
        query = FuncoesUteis.getQueryResults(init,ContaReceber.queries)
        FuncoesUteis.showHideFilter(init,ContaReceber.filterSelector)
        insereContaReceber = ContaReceber.insereContaReceber(init,query)
        ContaReceber.detalhesContaReceber(init,query)
        ContaReceber.salvaContaReceber(init)
        if insereContaReceber == 1:
            ContaReceber.recebimentoContaReceber(init,query)
            
    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine=f"{ContaReceber.rotina} - test_contaReceber_insereConta_detalhes", error_details=str(e))
        
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
            routine=f"{ContaReceber.rotina} - test_contaReceber_insereConta_detalhes",
            error_details=''
        )

        Log_manager.insert_logs_for_execution("ContaPagar")

        if validator:
            validator.check_window("Após inserção")


        browser.quit()