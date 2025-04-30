import time
from classes.rotinas.ContasReceber import ContaReceber
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.GerarDados import GeradorDados  
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components






import pytest

@pytest.mark.dockercontaReceber
def test_contaReceber_excluiContaReceber(init):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']


    try:
        FuncoesUteis.goToPage(init,ContaReceber.url)
        query = FuncoesUteis.getQueryResults(init,ContaReceber.queries)
        filters = {
        "P84_SELETOR_LOJA":query["Query_queryEmpresa"],
            "P84_TIPO_PERIODO":"VENCIMENTO",
            "P84_DATA_INICIAL":"24/03/2025",
            "P84_DATA_FINAL":"28/03/2025",
            "P84_NUMERO_DOCUMENTO":"",
            "P84_NUMERO_PEDIDO":"",
            "P84_CONTA":"",
            "P84_CENTRO_CUSTO":"",
            "P84_CATEGORIA":"",
            "P84_CLIENTE":"",
            "P84_VALOR_INICIAL":"",
            "P84_VALOR_FINAL":"",
            "P84_ORIGEM":"",
            "P84_CONVENIO":"",
            "P84_NR_CONTA":"",
            "P84_RECEBIDO_EM":"",
            "P84_TIPO_COBRANCA":"",
            "P84_COBRADOR":"",
            "P84_CONTEM_BOLETO":""
        }
        FuncoesUteis.aplyFilter(init,filters)
        ContaReceber.editaContaReceber(init)
        ContaReceber.excluiContaReceber(init)
        ContaReceber.salvaContaReceber(init)
        
            
    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
        screenshot_path = screenshots
        if screenshot_path:
            success = browser.save_screenshot(screenshot_path)
            if success:
                Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="ContaReceber", application_type=env_application_type, error_details=str(e))
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
            message="Conta editada",
            routine="ContaPagar",
            error_details=''
        )

        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Tempo de execução do teste: {minutos} min {segundos} s {milissegundos} ms",
            routine="ContaPagar",
            error_details=''
        )

        Log_manager.insert_logs_for_execution("ContaReceber")

        browser.quit()



       