from testes.testesWeb.ContasPagar.test_contaPagar_insereContaPagar_queries import test_contaPagar_insereConta_queries
from testes.testesWeb.ContasPagar.test_contaPagar_insereContaPagar import test_contasPagar_insereConta
from testes.testesWeb.ContasPagar.test_contaPagar_insereContaPagar_aba_detalhes import test_contasPagar_insereConta_aba_detalhes
from testes.testesWeb.ContasPagar.test_contaPagar_insereContaPagar_aba_repeticao import test_contasPagar_insereConta_aba_repeticao
from testes.testesWeb.ContasPagar.test_contaPagar_insereContaPagar_aba_pagamentos import test_contasPagar_insereConta_aba_pagamentos
from testes.testesWeb.ContasPagar.test_contaPagar_insereContaPagar_aba_intrucao_pagamento import test_contasPagar_insereConta_aba_intrucao_pagamento
from testes.testesWeb.ContasPagar.test_contaPagar_insereContaPagar_aba_despesas import test_contasPagar_insereConta_aba_despesas
from testes.testesWeb.ContasPagar.test_contaPagar_EditaContaPagar import test_contaPagar_insereConta_edita
from testes.testesWeb.ContasPagar.test_contaPagar_insereContaPagar_finaliza_insert import test_insere_conta_pagar_finaliza_insert
from testes.testesWeb.ContasPagar.test_contaPagar_ExcluiContaPagar import test_contaPagar_insereConta_exclui
import pytest
import time






@pytest.mark.parametrize("insertOrEdit", ["Insert"])  # Default para Insert
def test_module_contasPagar(init, request, insertOrEdit):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    getEnv = env_vars
    env_application_type = getEnv.get("WEB")

    try:
        # Verifica o valor de 'insertOrEdit', podendo ser alterado pelo pytest ou pela linha de comando
        insertOrEdit = request.config.getoption("insertOrEdit", default=insertOrEdit)  # Valor de "Insert" se não passar pela linha de comando

        if insertOrEdit == 'Insert':
            query = test_contaPagar_insereConta_queries(init)
            test_contasPagar_insereConta(init, query)
            # test_contasPagar_insereConta_aba_detalhes(init, query)
            test_contasPagar_insereConta_aba_repeticao(init)
            # test_contasPagar_insereConta_aba_pagamentos(init,query)
            # test_contasPagar_insereConta_aba_intrucao_pagamento(init, query)
            # test_contasPagar_insereConta_aba_despesas(init)
            # test_insere_conta_pagar_finaliza_insert(init)
        
        elif insertOrEdit == "Edit":
            test_contaPagar_insereConta_edita(init)

        elif insertOrEdit == "Delete":    
           test_contaPagar_insereConta_exclui(init)

    except Exception as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="Error",
            message="Erro na execução do módulo de contas a pagar",
            routine="ContaPagar",
            error_details=str(e)
        )
    
    finally:
        screenshot_path = screenshots
        
        # Verifica se o screenshot foi tirado corretamente
        if screenshot_path:
            Log_manager.add_log(
                    level="INFO", 
                    message=f"Screenshot salvo em: {screenshot_path}", 
                    routine="Login",application_type='WEB', 
                    error_details=''
            )
        else:
            Log_manager.add_log(
                level="ERROR", 
                message="Falha ao salvar screenshot", 
                routine="Login",application_type='WEB', 
                error_details=''
            )
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

        Log_manager.insert_logs_for_execution()






