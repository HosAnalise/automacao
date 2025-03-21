from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.FuncoesUteis import FuncoesUteis
import pytest




def test_contaPagar_insereConta_exclui(init):

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


        # Aguarda a aba estar visível
        abaPagamento = WebDriverWait(browser, 30).until(
            EC.visibility_of_element_located((By.ID, "pagamento_tab"))
        )
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de pagamento encontrada", routine="ContaPagar", error_details ="" )


        # Garante que o elemento está na tela
        browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", abaPagamento)
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Scroll até Aba de pagamento ", routine="ContaPagar", error_details ="" )


        # Aguarda até que o elemento esteja clicável
        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, "pagamento_tab")))
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de pagamento clicavel", routine="ContaPagar", error_details ="" )


        # Tenta clicar normalmente, se falhar, usa JavaScript para forçar o clique
        try:
            abaPagamento.click()
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de pagamento clicada via py", routine="ContaPagar", error_details ="" )

        except:
            browser.execute_script("arguments[0].click();", abaPagamento)
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Aba de pagamento clicada via js", routine="ContaPagar", error_details ="" )


        while True:
            try:
                delete_icons = WebDriverWait(browser, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".excluirPagamento"))
                )

                if not delete_icons:
                    break  # Sai do loop se não houver mais ícones para excluir

                delete_icons[0].click()  # Sempre clicamos no primeiro disponível

                confirm_btn = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".js-confirmBtn"))
                )
                confirm_btn.click()


            except TimeoutException:
                break  
        btnDelete = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[name='excluirConta']")))   
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão excluir Conta Pagar encontrado", routine="ContaPagar", error_details ="" )
 
        btnDelete.click()
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão excluir Conta Pagar clicado", routine="ContaPagar", error_details ="" )

        btnConfirmDelete = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".js-confirmBtn")))   
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão confirmar exclusão Conta Pagar encontrado", routine="ContaPagar", error_details ="" )
 
        btnConfirmDelete.click()
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão confirmar exclusão Conta Pagar clicado", routine="ContaPagar", error_details ="" )

        has_alert = FuncoesUteis.has_alert(init)



        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Conta a pagar {dataId} foi excluida", routine="ContaPagar", error_details ="" )





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

