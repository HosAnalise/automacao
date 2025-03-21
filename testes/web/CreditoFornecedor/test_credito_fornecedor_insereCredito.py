from datetime import datetime
import random
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import lorem
import pytest

@pytest.mark.parametrize("browser, login", [("chrome", "teste")], indirect=True)
def test_insere_credito_fornecedor(init):

    browser, login, log_manager, get_ambiente,env_vars,seletor_ambiente,screenshots= init

    execution_id = log_manager._generate_execution_id()

    if 'URL_ERP' not in env_vars:
        pytest.fail("Erro crítico: 'URL_ERP' não encontrada no ambiente de variáveis.")

    env_url = env_vars['URL_ERP']

    env_forncedor = env_vars['FORNECEDORES'].split(',')

    env_credito_fornecedor_origem = env_vars['CREDITO_FORNECEDOR_ORIGEM'].split(',')

    env_documento_fiscal_saida = env_vars['DOCUMENTO_FISCAL_SAIDA'].split(',')

    env_documento_fiscal_entrada = env_vars['DOCUMENTO_FISCAL_ENTRADA'].split(',')

    env_application_type = env_vars['WEB']
    
    log_manager.add_log(application_type =env_application_type,level="DEBUG", message=f"Valores carregados do env url:{env_url}, fornecedor:{env_forncedor}, credito fornecedor:{env_credito_fornecedor_origem}, documento fisacal saida:{env_documento_fiscal_saida}, documento fiscal entrada:{env_documento_fiscal_entrada}", routine="CreditoFornecedor", error_details='')

    browser.get(f"{env_url}listagem-de-cr%C3%A9dito-de-devolu%C3%A7%C3%A3o-de-fornecedor")

    assert "Listagem de Crédito De Devolução de Fornecedor" in browser.title, "Página de reembolso não carregou corretamente"

    try:

 

        # Aguarda até a página de crédito de fornecedor ser carregada
        browser.get(f"{env_url}listagem-de-cr%C3%A9dito-de-devolu%C3%A7%C3%A3o-de-fornecedor")
        log_manager.add_log(application_type =env_application_type,level="INFO", message="Página de crédito fornecedor carregada", routine="CreditoFornecedor", error_details='')

        # Clica no botão de novo crédito
        novoCredito = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "B79642276909633610")))
        novoCredito.click()
        log_manager.add_log(application_type =env_application_type,level="INFO", message="Botão novo crédito clicado", routine="CreditoFornecedor", error_details='')

        # Aguarda o iframe e troca para ele
        iframe = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[title="Crédito"]')))
        browser.switch_to.frame(iframe)
        log_manager.add_log(application_type =env_application_type,level="INFO", message="Mudando para iframe de novo crédito", routine="CreditoFornecedor", error_details='')

        # Gera valores aleatórios
        numero = random.uniform(1000, 9999)
        numero_formatado = "{:,.2f}".format(numero).replace(",", "X").replace(".", ",").replace("X", ".")
        loremEpsum = lorem.paragraph()  # Remove quebras de linha
        data_hoje = datetime.today().strftime('%d/%m/%Y')  # Confirme se esse formato é aceito no Apex

  
        fornecedor_sorteado = random.choice(env_forncedor)
        valor_sorteado_credito = random.choice(env_credito_fornecedor_origem)
        documento_fiscal_saida_sorteado = random.choice(env_documento_fiscal_saida)
        documento_fical_entrada_sorteado = random.choice(env_documento_fiscal_entrada)

        # Espera 2 segundos antes de iniciar as inserções
        time.sleep(2)

        # Enviando valores para os campos no Apex
        browser.execute_script(f"apex.item('P169_DATA|input').setValue('{data_hoje}')")
        browser.execute_script(f"apex.item('P169_CREDITO_FORNECEDOR_ORIGEM_ID').setValue('{valor_sorteado_credito}')")
        browser.execute_script(f"apex.item('P169_PESSOA_FORNECEDOR_ID').setValue('{fornecedor_sorteado}')")
        browser.execute_script("apex.item('P169_DOC_SAIDA_OPCAO').setValue('1')")
        browser.execute_script("apex.item('P169_DOC_ENTRADA_OPCAO').setValue('1')")

        time.sleep(1)

        browser.execute_script(f"apex.item('P169_NUMERO_NOTA_SAIDA').setValue('{documento_fiscal_saida_sorteado}')")
        browser.execute_script(f"apex.item('P169_NUMERO_NOTA_ENTRADA').setValue('{documento_fical_entrada_sorteado}')")
        browser.execute_script("apex.item('P169_LOJA_ID').setValue('2381')")
        browser.execute_script(f"apex.item('P169_VALOR').setValue('{numero_formatado}')")
        browser.execute_script(f"apex.item('P169_OBSERVACAO').setValue('{loremEpsum}')")

        # Clica no botão de salvar
        salvar = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "salvar")))
        salvar.click()

        log_manager.add_log(application_type =env_application_type,level="INFO", message="Botão Salvar crédito clicado", routine="CreditoFornecedor", error_details='')

        browser.switch_to.default_content()

    except (TimeoutException, NoSuchElementException) as e:
        log_manager.add_log(application_type =env_application_type,level="INFO", message="Erro ao interagir com a página de reembolso de crédito:", routine="CreditoFornecedor", error_details=str(e))
        screenshots

    try:
        # Injetar o script corrigido
        script = """
        $('#cardFornecedor').on('apexafterrefresh', function() {
            $(this).attr('data-refresh-detectado', 'true');
        });
        """
        browser.execute_script(script)
        # Aguardar até que o atributo seja alterado
        while True:
            atributo = browser.execute_script("return $('#cardFornecedor').attr('data-refresh-detectado');")
            if atributo == "true":
                print("Evento apexafterrefresh detectado!")
                break

            
            

    except (TimeoutException, NoSuchElementException, WebDriverException) as e:
        log_manager.add_log(application_type =env_application_type,level="ERROR", message=f"Erro ao executar o script no navegador: {str(e)}", routine="CreditoFornecedor", error_details=str(e))
        screenshots
        
    finally:
        log_manager.add_log(application_type =env_application_type,level="INFO", message="Crédito Fornecedor inserido", routine="CreditoFornecedor", error_details='')
        # Fechar o navegador
        log_manager.insert_logs_for_execution(execution_id)
