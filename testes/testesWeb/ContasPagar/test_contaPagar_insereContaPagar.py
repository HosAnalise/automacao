from datetime import datetime,timedelta
import random
import time
import lorem
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.GerarDados import GeradorDados  
from scripts.FuncoesUteis import FuncoesUteis
from scripts.ApexUtil import Apex

@pytest.mark.suiteContaPagar
@pytest.mark.parametrize("browser, login", [("chrome", "teste")], indirect=True)
def test_contasPagar_insereConta(init,query):
       
    randomContaId,randomFornecedorId,randomCategoriaFinanceiraId,randomEmpresaId,randomPagamentoId,randomChavePixId,randomBancoId,randomCentroCustoId,randomModeloDocumentoID = query
    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

    getEnv = env_vars
    url_erp = getEnv.get('URL_ERP')
    env_application_type = getEnv.get("WEB")
    
    random_value = round(random.uniform(1, 999999), 2)
    randomValue = FuncoesUteis.formatBrCurrency(random_value)
    randomText = lorem.paragraph()
    randomNumber = GeradorDados.randomNumberDinamic(0,4)
    randomDay = GeradorDados.randomNumberDinamic(1,30)

    today = datetime.today()
    randomDay = GeradorDados.randomNumberDinamic(0, 30)
    randomDate = today + timedelta(days=randomDay)
    finalDate = randomDate.strftime("%d/%m/%Y")




    if not url_erp:
        pytest.fail("Erro crítico: 'URL_ERP' não encontrada no ambiente de variáveis. sim")   

    # Redireciona para a página de contas a pagar
    browser.get(f"{url_erp}contas-a-pagar")




    
    try:
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#P46_SELETOR_LOJA")))
        script ="$('button#t_Button_rightControlButton > span').click()"
        browser.execute_script(script)

        btnNovaContaPagar = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#B129961237978758786")))
        btnNovaContaPagar.click()



        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_VALOR")))
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo: valorOriginal encontrado", routine="ContaPagar", error_details ="" )

        if randomNumber != 0:
            Apex.setValue(browser,"P47_VALOR",randomValue)
            valorOriginalValue = Apex.getValue(browser,"P47_VALOR")
            if valorOriginalValue == str(randomValue):
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: valorOriginal teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P47_VALOR",randomText)
            valorOriginalValue = Apex.getValue(browser,"P47_VALOR")
            if valorOriginalValue == randomText:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: valorOriginal teve o valor inserido incorretamente valor: {valorOriginalValue}", routine="ContaPagar", error_details ="" )


        naConta = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_CONTA_ID")))
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: naConta encontrado", routine="ContaPagar", error_details ="" )

        if randomNumber != 0:
            Apex.setValue(browser,"P47_CONTA_ID",randomContaId)
            naContaValue = Apex.getValue(browser,"P47_CONTA_ID")
            if naContaValue == randomContaId:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: naConta teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P47_CONTA_ID",randomText)
            naContaValue = Apex.getValue(browser,"P47_CONTA_ID")
            if naContaValue == randomText:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: naConta teve o valor inserido incorretamente valor: {naContaValue}", routine="ContaPagar", error_details ="" )        
    

        # Captura pessoa favorecido/fornecedor e insre valores
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_PESSOA_FAVORECIDO_ID")))
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: pessoaFavorecido encontrado", routine="ContaPagar", error_details ="" )


        if randomNumber != 0:
            Apex.setValue(browser,"P47_PESSOA_FAVORECIDO_ID",randomFornecedorId)
            pessoaFavorecidoValue = Apex.getValue(browser,"P47_PESSOA_FAVORECIDO_ID")
            if pessoaFavorecidoValue == randomFornecedorId:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: pessoaFavorecido teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P47_PESSOA_FAVORECIDO_ID",randomText)
            pessoaFavorecidoValue = Apex.getValue(browser,"P47_PESSOA_FAVORECIDO_ID")
            
            if pessoaFavorecidoValue == randomText:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: pessoaFavorecido teve o valor inserido incorretamente valor: {pessoaFavorecidoValue}", routine="ContaPagar", error_details ="" )



       
        # Captura o campo de data de vencimento e insere valores
        vencimentoConta = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_DATA_VENCIMENTO")))
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: vencimentoConta encontrado", routine="ContaPagar", error_details ="" )


        if randomNumber != 0:
            Apex.setValue(browser,"P47_DATA_VENCIMENTO",finalDate)
            vencimentoContaValue = Apex.getValue(browser,"P47_DATA_VENCIMENTO")
            if vencimentoContaValue == finalDate:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: vencimentoConta teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )

        else:
            Apex.setValue(browser,"P47_DATA_VENCIMENTO",randomText)
            vencimentoContaValue = Apex.getValue(browser,"P47_DATA_VENCIMENTO")
            if vencimentoContaValue == randomText:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: vencimentoConta teve o valor inserido incorretamente valor: {vencimentoContaValue}", routine="ContaPagar", error_details ="" )
        
    

        # Escolhe uma data de previsão de pagamento e insere valores
        previsaoPagamentoConta = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_DATA_PREVISAO_PAGAMENTO")))
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: previsaoPagamentoConta encontrado", routine="ContaPagar", error_details ="" )


        if randomNumber != 0:
            Apex.setValue(browser,"P47_DATA_PREVISAO_PAGAMENTO",finalDate)
            previsaoPagamentoContaValue = Apex.getValue(browser,"P47_DATA_PREVISAO_PAGAMENTO")
            if previsaoPagamentoContaValue == finalDate:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: previsaoPagamentoConta teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )

        else:
            Apex.setValue(browser,"P47_DATA_PREVISAO_PAGAMENTO",randomText)
            previsaoPagamentoContaValue = Apex.getValue(browser,"P47_DATA_PREVISAO_PAGAMENTO")
            if previsaoPagamentoContaValue == randomText:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: previsaoPagamentoConta teve o valor inserido incorretamente valor: {previsaoPagamentoContaValue}", routine="ContaPagar", error_details ="" )

    

        # Captura o campo de categoria financeira e insere valores
        categoriaFinanceira = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_CATEGORIA_FINANCEIRA")))
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: categoriaFinanceira encontrado", routine="ContaPagar", error_details ="" )
        
        time.sleep(3)

        if randomNumber != 0:
            Apex.setValue(browser,"P47_CATEGORIA_FINANCEIRA",randomCategoriaFinanceiraId)
            categoriaFinanceiraValue = Apex.getValue(browser,"P47_CATEGORIA_FINANCEIRA")
            if categoriaFinanceiraValue == randomCategoriaFinanceiraId:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: categoriaFinanceira teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )

        else:
            Apex.setValue(browser,"P47_CATEGORIA_FINANCEIRA",randomText)
            categoriaFinanceiraValue = Apex.getValue(browser,"P47_CATEGORIA_FINANCEIRA")
            if categoriaFinanceiraValue == randomText:    
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: previsaoPagamentoConta teve o valor inserido incorretamente valor: {categoriaFinanceiraValue}", routine="ContaPagar", error_details ="" )
 
    

        # Captura o campo de empresa e insere valores
        empresa = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_LOJA"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: empresa encontrado", routine="ContaPagar", error_details ="" )


        if randomNumber != 0:
            Apex.setValue(browser,"P47_LOJA",randomEmpresaId)
            empresaValue = Apex.getValue(browser,"P47_LOJA")
            if empresaValue ==randomEmpresaId:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: empresa teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P47_LOJA",randomText)
            empresaValue = Apex.getValue(browser,"P47_LOJA")
            if empresaValue == randomText:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: empresa teve o valor inserido incorretamente valor: {empresaValue}", routine="ContaPagar", error_details ="" )        
    
        
        # captura o campo descricao e insere valores

        descricao = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#P47_DESCRICAO"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: descricao encontrado", routine="ContaPagar", error_details ="" )

        bigText500 = GeradorDados.gerar_texto(500)

        if randomNumber != 0:
            Apex.setValue(browser,"P47_DESCRICAO",randomText)
            descricaoValue = Apex.getValue(browser,"P47_DESCRICAO")
            if descricaoValue == randomText:
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: descricao teve o valor inserido corretamente", routine="ContaPagar", error_details ="" )
        else:
            Apex.setValue(browser,"P47_DESCRICAO",bigText500)
            descricaoValue = Apex.getValue(browser,"P47_DESCRICAO")
            if descricaoValue == randomText:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: descricao teve o valor inserido incorretamente valor: {descricaoValue}", routine="ContaPagar", error_details ="" )






        





 


     


     


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




    



