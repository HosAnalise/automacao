from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.GerarDados import GeradorDados  
from testes.testesWeb.ContasPagar.test_contaPagar_insereContaPagar_queries import test_contaPagar_insereConta_queries
from testes.testesWeb.ContasPagar.test_contaPagar_insereContaPagar_aba_detalhes import test_contasPagar_insereConta_aba_detalhes
from testes.testesWeb.ContasPagar.test_contaPagar_insereContaPagar_aba_repeticao import test_contasPagar_insereConta_aba_repeticao
from testes.testesWeb.ContasPagar.test_contaPagar_insereContaPagar_aba_pagamentos import test_contasPagar_insereConta_aba_pagamentos
from testes.testesWeb.ContasPagar.test_contaPagar_insereContaPagar_aba_intrucao_pagamento import test_contasPagar_insereConta_aba_intrucao_pagamento
from testes.testesWeb.ContasPagar.test_contaPagar_insereContaPagar_aba_despesas import test_contasPagar_insereConta_aba_despesas
from testes.testesWeb.ContasPagar.test_contaPagar_insereContaPagar_finaliza_insert import test_insere_conta_pagar_finaliza_insert
import pytest
import time




def test_contaPagar_insereConta_edita(init):

    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
    getEnv = env_vars
    env_application_type = getEnv.get("WEB")    
    dataId = "data id não encontrado"  
    url_erp = getEnv.get('URL_ERP')

    if not url_erp:
        pytest.fail("Erro crítico: 'URL_ERP' não encontrada no ambiente de variáveis. sim")   

    # Redireciona para a página de contas a pagar
    browser.get(f"{url_erp}contas-a-pagar")





    try:
        query = test_contaPagar_insereConta_queries(init)

        btnFilter = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#filtrar")))
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Conta a pagar botão filtrar encontrado",
            routine="ContaPagar",
            error_details=''
        )

        btnFilter.click()
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Conta a pagar botão filtrar clicado",
            routine="ContaPagar",
            error_details=''
        )


        edit = WebDriverWait(browser,120).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".fa.fa-edit")))
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Conta a pagar editavel encontrada",
            routine="ContaPagar",
            error_details=''
        )

        dataId = edit.get_attribute("data-id")
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Conta a pagar data-id capturado",
            routine="ContaPagar",
            error_details=''
        )

        edit.click()
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Conta a pagar editavel clicada. Inicio da edição da conta!",
            routine="ContaPagar",
            error_details=''
        )

        if GeradorDados.randomNumberDinamic(0, 1) == 0:
            test_contasPagar_insereConta_aba_detalhes(init, query)

        if GeradorDados.randomNumberDinamic(0, 1) == 0:
            
            test_contasPagar_insereConta_aba_repeticao(init)

        if GeradorDados.randomNumberDinamic(0, 1) == 0:    
            test_contasPagar_insereConta_aba_pagamentos(init,query)
       
        if GeradorDados.randomNumberDinamic(0, 1) == 0:    
            test_contasPagar_insereConta_aba_intrucao_pagamento(init, query)

        if GeradorDados.randomNumberDinamic(0, 1) == 0:    
            test_contasPagar_insereConta_aba_despesas(init)    
            
        test_insere_conta_pagar_finaliza_insert(init)    


    except TimeoutException as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro: Tempo limite excedido ao acessar a página",
            routine="ContaPagar",
            error_details=str(e)
        )

    except NoSuchElementException as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro: Elemento não encontrado na página",
            routine="ContaPagar",
            error_details=str(e)
        )

    except Exception as e:  # Captura qualquer outro erro inesperado
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro desconhecido ao acessar a página",
            routine="ContaPagar",
            error_details=str(e)
        )

    finally:
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Conta a pagar {dataId} editada",
            routine="ContaPagar",
            error_details=''
        )    


    