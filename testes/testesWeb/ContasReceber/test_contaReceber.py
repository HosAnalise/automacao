from testes.testesWeb.ContasReceber.test_contaReceber_insereContaReceber import test_contasReceber_insereConta
from testes.testesWeb.ContasReceber.test_contaReceber_insereContaReceber_aba_repeticao import test_contasReceber_insereConta_aba_repeticao
from testes.testesWeb.ContasReceber.test_contaReceber_insereContaReceber_aba_detalhes import test_contasReceber_insereConta_aba_detalhes
from testes.testesWeb.ContasReceber.test_contaReceber_insereContaReceber_aba_recebimentos import test_contasReceber_insereConta_aba_Recebimentos
from testes.testesWeb.ContasReceber.test_contaReceber_insereContaReceber_queries import test_contaReceber_insereConta_queries
from testes.testesWeb.ContasReceber.test_contaReceber_insereContaReceber_aba_juros_multas import test_contasReceber_insereConta_aba_juros_multas
import pytest
import time


@pytest.mark.parametrize("insertOrEdit", ["Insert"])  # Default para Insert
def test_module_contasReceber(init, request, insertOrEdit):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    getEnv = env_vars
    env_application_type = getEnv.get("WEB")

    try:
        # Verifica o valor de 'insertOrEdit', podendo ser alterado pelo pytest ou pela linha de comando
        insertOrEdit = request.config.getoption("insertOrEdit", default=insertOrEdit)  # Valor de "Insert" se não passar pela linha de comando

        if insertOrEdit == 'Insert':
            query = test_contaReceber_insereConta_queries(init)
            test_contasReceber_insereConta(init,query)
            test_contasReceber_insereConta_aba_detalhes(init,query)
            test_contasReceber_insereConta_aba_repeticao(init)
            test_contasReceber_insereConta_aba_Recebimentos(init,query)
            test_contasReceber_insereConta_aba_juros_multas(init)
            


    except Exception as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="Error",
            message="Erro na execução do módulo de contas a Receber",
            routine="ContaReceber",
            error_details=str(e)
        )

        screenshot_path = screenshots
        
        # Verifica se o screenshot foi tirado corretamente
        if screenshot_path:
            sucess  = browser.save_screenshot(screenshot_path)
            if sucess:
                Log_manager.add_log(
                    level="INFO", 
                    message=f"Screenshot salvo em: {screenshot_path}", 
                    routine="Login",application_type='WEB', 
                    error_details=str(e)
                )
        else:
            Log_manager.add_log(
                level="ERROR", 
                message="Falha ao salvar screenshot", 
                routine="Login",application_type='WEB', 
                error_details=str(e)
            )

    
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
            routine="ContaReceber",
            error_details=''
        )

        Log_manager.insert_logs_for_execution()






