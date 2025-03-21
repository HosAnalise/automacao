import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


@pytest.mark.suiteCreditoFornecedor
@pytest.mark.parametrize("browser, login", [("chrome", "teste")], indirect=True)
def test_reembolso_credito_fornecedor(init):

    browser, login, log_manager, get_ambiente,env_vars,seletor_ambiente,screenshots = init
    
    execution_id = log_manager._generate_execution_id()
    screenshots_path,screenshot = screenshots

    if 'URL_ERP' not in env_vars:
        pytest.fail("Erro crítico: 'URL_ERP' não encontrada no ambiente de variáveis.")

    url_erp = env_vars['URL_ERP']
        
    env_application_type = env_vars['WEB']


    browser.get(f"{url_erp}listagem-de-cr%C3%A9dito-de-devolu%C3%A7%C3%A3o-de-fornecedor")

    assert "Listagem de Crédito De Devolução de Fornecedor" in browser.title, "Página de reembolso não carregou corretamente"   
    

    try:
        # Acessar página de reembolso
        browser.get(f"{url_erp}listagem-de-cr%C3%A9dito-de-devolu%C3%A7%C3%A3o-de-fornecedor")
        log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Página de reembolso de crédito carregada", routine="CreditoFornecedor", error_details ='' )

        # Selecionar crédito de fornecedor
        creditoFornecedor = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".t-Button.t-Button--stretch.t-Button--hot.detalheCredito")))
        creditoFornecedor.click()
        log_manager.add_log(application_type =env_application_type,level= "INFO", message ="Crédito Fornecedor selecionado", routine="CreditoFornecedor", error_details ='' )

        # Captura botão de ações
        buttonAcoes = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[title='Ações']")))
        valorDataIdInicio = buttonAcoes.get_attribute("data-id")
        buttonAcoes.click()

        # Aguarda o iframe e troca para ele
        iframe = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[title="Tipo de Utilização"]')))
        browser.switch_to.frame(iframe)

        # Executa JavaScript para selecionar a opção de reembolso
        script = "document.querySelector('#R54526807905668028_cards > li:nth-child(4) > div > a > div.t-Card-titleWrap > h3').click()"
        browser.execute_script(script)
        browser.switch_to.default_content()

        # Troca para outro iframe e preenche a conta
        iframe2 = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[title="Cadastro de Contas a Receber Resumido"]')))
        browser.switch_to.frame(iframe2)

        conta = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "P199_CONTA_ID_lov_btn")))
        conta.click()
        time.sleep(1)
        browser.execute_script("apex.item('P199_CONTA_ID').setValue('5290')")

        # Salvar
        salvar = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "save")))
        salvar.click()
        browser.switch_to.default_content()

        # Pressiona ESC para fechar pop-ups
        iframe3 = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[title="Tipo de Utilização"]')))
        browser.switch_to.frame(iframe3)
        time.sleep(2)
        ActionChains(browser).send_keys(Keys.ESCAPE).perform()
        browser.switch_to.default_content()

       
    except (TimeoutException, NoSuchElementException, Exception) as e:
        log_manager.add_log(application_type =env_application_type,level= "ERROR", message= f"Erro durante o reembolso: {str(e)}", routine="CreditoFornecedor", error_details ='' )
        screenshot
        pytest.fail(f"Erro no teste: {str(e)}")


    try:
        # Injetar o script corrigido
        script = """
        $('#irrListagem').on('apexafterrefresh', function() {
            $(this).attr('data-refresh-detectado', 'true');
        });
        """
        browser.execute_script(script)
        # Aguardar até que o atributo seja alterado
        while True:
            atributo = browser.execute_script("return $('#irrListagem').attr('data-refresh-detectado');")
            if atributo == "true":
                print("Evento apexafterrefresh detectado!")
                break
            time.sleep(1)

        # Verificar sucesso
        buttonAcoesFinal = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[title='Ações']")))
        valorDataIdFinal = buttonAcoesFinal.get_attribute("data-id")

        if valorDataIdInicio == valorDataIdFinal:
            log_manager.add_log(application_type =env_application_type,level= "ERROR", message= "Reembolso não realizado", routine="CreditoFornecedor",  error_details=f"id Credito fornecedor não reembolsado {valorDataIdInicio}")
        else:
            log_manager.add_log(application_type =env_application_type,level= "INFO", message= "Reembolso realizado com sucesso", routine="CreditoFornecedor", error_details = '' )
    
    except (TimeoutException,  Exception) as e:
        buttonAcoesFinal = None
        log_manager.add_log(application_type =env_application_type,level= "ERROR", message= f"Erro durante o reembolso: {str(e)}", routine="CreditoFornecedor", error_details ='' )
        screenshot
        pytest.fail(f"Erro no teste: {str(e)}")
    except NoSuchElementException as e:
        log_manager.add_log(application_type =env_application_type,level= "INFO", message= f"Reembolso realizado com sucesso: {str(e)}", routine="CreditoFornecedor", error_details ='' )
        screenshot
        pytest.fail(f"Erro no teste: {str(e)}")    

    finally:
        # Exibe os últimos logs da rotina
        # LogManager.get_logs(routine="CreditoFornecedor", limit=5)
        log_manager.insert_logs_for_execution(execution_id)
