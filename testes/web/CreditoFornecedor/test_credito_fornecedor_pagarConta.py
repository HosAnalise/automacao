import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import pytest

@pytest.mark.suiteCreditoFornecedor
@pytest.mark.parametrize("browser, login", [("chrome", "teste")], indirect=True)
def test_reembolso_credito_fornecedor(init):
    browser, login, log_manager, get_ambiente,env_vars,seletor_ambiente,screenshots,sql_connect = init
    
    execution_id = log_manager._generate_execution_id()

    if 'URL_ERP' not in env_vars:
        pytest.fail("Erro crítico: 'URL_ERP' não encontrada no ambiente de variáveis.")

    env_item = env_vars['URL_ERP']

    browser.get(f"{env_item}listagem-de-cr%C3%A9dito-de-devolu%C3%A7%C3%A3o-de-fornecedor")

    assert "Listagem de Crédito De Devolução de Fornecedor" in browser.title, "Página de reembolso não carregou corretamente"   
    

    try:
        # Acessar página de reembolso
        browser.get(f"{env_item}listagem-de-cr%C3%A9dito-de-devolu%C3%A7%C3%A3o-de-fornecedor")
        log_manager.add_log(level= "INFO", message = "Página de reembolso de crédito carregada", routine="CreditoFornecedor", error_details ='' )

        # Selecionar crédito de fornecedor
        creditoFornecedor = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".t-Button.t-Button--stretch.t-Button--hot.detalheCredito")))
        creditoFornecedor.click()
        log_manager.add_log(level= "INFO", message ="Crédito Fornecedor selecionado", routine="CreditoFornecedor", error_details ='' )

        # Captura botão de ações
        buttonAcoes = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[title='Ações']")))
        valorDataIdInicio = buttonAcoes.get_attribute("data-id")
        buttonAcoes.click()

        # Aguarda o iframe e troca para ele
        iframe = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[title="Tipo de Utilização"]')))
        browser.switch_to.frame(iframe)

         # Executa JavaScript para selecionar a opção de reembolso
        script = "document.querySelector('#R54526807905668028_cards > li:nth-child(1) > div > a > div.t-Card-titleWrap > h3').click()"
        browser.execute_script(script)
        browser.switch_to.default_content()

        # Troca para outro iframe e preenche a conta
        iframe2 = WebDriverWait(browser, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[title="Crédito Fornecedor - Operação"]')))

        

    except:
        log_manager.add_log(level= "INFO", message ="Crédito Fornecedor selecionado", routine="CreditoFornecedor", error_details ='' )


