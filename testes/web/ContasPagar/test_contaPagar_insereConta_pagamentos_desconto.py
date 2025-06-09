import time
from classes.rotinas.ContasPagar import ContasPagar
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.FuncoesUteis import FuncoesUteis
import pytest

@pytest.mark.dockerContaPagar
def test_contaPagar_insereConta_pagamentos_desconto(init):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']

    try:
        FuncoesUteis.goToPage(init,ContasPagar.url)
        query = FuncoesUteis.getQueryResults(init,ContasPagar.queries)
        
        FuncoesUteis.showHideFilter(init,ContasPagar.filterSelector)
        ContasPagar.insereContaPagar(init,query)
        ContasPagar.pagamentosContaPagar(init)
        ContasPagar.lancarDescontoCondicional(init)
        ContasPagar.finalizaInsertContaPagar(init)   
        

    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine=f"{ContasPagar.rotina} - test_contaPagar_insereConta_pagamentos_desconto", error_details=str(e))

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
            routine=f"{ContasPagar.rotina} - test_contaPagar_insereConta_pagamentos_desconto",
            error_details=''
        )

        Log_manager.insert_logs_for_execution("ContaPagar")

        browser.quit()