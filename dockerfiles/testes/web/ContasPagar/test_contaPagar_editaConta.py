import time
from classes.rotinas.ContasPagar import ContasPagar
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.Components import Components
from classes.utils.FuncoesUteis import FuncoesUteis
import pytest

@pytest.mark.dockerContaPagar
def test_contaPagar_insereConta_despesas(init):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']


    try:
        FuncoesUteis.goToPage(init,ContasPagar.url)
        query = FuncoesUteis.getQueryResults(init,ContasPagar.queries)
        values = [
            '-1',
            'VENCIMENTO',
            '10/03/2025',
            '02/04/2025',
            ',venceHoje,venceAmanha,aVencer,atrasada,pagoParcialmente,agrupada',
            '',
            '',
            '',
            '-1',
            '-1',
            '-1',
            '0',
            '-1',
            '-1',
            '-1',
            '',
            '',
            '-1'
        ]      

        filterValues = FuncoesUteis.combine_lists_to_dict(ContasPagar.filters,values)
        FuncoesUteis.setFilters(init,filterValues)
        seletor = "#filtrar"
        Components.btnClick(init,seletor)
        ContasPagar.editaContaPagar(init,lambda: ContasPagar.excluiContaPagar(init))
        ContasPagar.finalizaInsertContaPagar(init)   
        
        
            
    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
        screenshot_path = screenshots
        if screenshot_path:
            success = browser.save_screenshot(screenshot_path)
            if success:
                Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="ContaPagar", application_type=env_application_type, error_details=str(e))
            else:
                Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))

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
            routine="ContaPagar",
            error_details=''
        )

        Log_manager.insert_logs_for_execution("ContaPagar")

        browser.quit()



       