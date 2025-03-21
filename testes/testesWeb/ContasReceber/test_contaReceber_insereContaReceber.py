from datetime import datetime,timedelta
import random
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.GerarDados import GeradorDados  
from scripts.FuncoesUteis import FuncoesUteis
from scripts.ApexUtil import Apex

@pytest.mark.parametrize("browser, login", [("chrome", "teste")], indirect=True)
def test_contasReceber_insereConta(init,query):
       
    randomQueries =  query
    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

    getEnv = env_vars
    url_erp = getEnv.get('URL_ERP')
    env_application_type = getEnv.get("WEB")
    
    randomValue = round(random.uniform(1, 999999), 2)
    randomText = GeradorDados.gerar_texto(100)
    randomNumber = GeradorDados.randomNumberDinamic(0,4)


    today = datetime.today()
    randomDayVencimento = GeradorDados.randomNumberDinamic(1,30)
    randomDatePrevisao = today + timedelta(days=randomDayVencimento)
    randomDayPrevisao = GeradorDados.randomNumberDinamic(0, 30)
    randomDatePrevisao = today + timedelta(days=randomDayPrevisao)
    dataVencimento = randomDatePrevisao.strftime("%d/%m/%Y")
    dataPrevisao =  randomDatePrevisao.strftime("%d/%m/%Y")




    if not url_erp:
        pytest.fail("Erro crítico: 'URL_ERP' não encontrada no ambiente de variáveis")   

    # Redireciona para a página de contas a pagar
    browser.get(f"{url_erp}contas-a-receber")
    
    try:
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#P84_SELETOR_LOJA")))
        script ="$('button#t_Button_rightControlButton > span').click()"
        browser.execute_script(script)

        btnNovaContaReceber = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#B392477272658547904")))
        btnNovaContaReceber.click()

        zeroOrOne = GeradorDados.randomNumberDinamic(0,1)
        bigText500 = GeradorDados.gerar_texto(500)

        recebidovalue = zeroOrOne if randomNumber != 0 else randomText
        valorValue = randomValue if randomNumber != 0 else randomText
        contaIdValue = randomQueries["Random_queryContaId"] if randomNumber != 0 else randomText
        pessoaClienteId = randomQueries["Random_queryCliente"] if randomNumber != 0 else randomText
        dataVencimentoValue = dataVencimento if randomNumber != 0 else randomText
        dataPrevisaoRecebimento = dataPrevisao if randomNumber != 0 else randomText
        categoriaFinanceiraValue  = randomQueries["Random_queryCategoriaFinanceira"]
        lojaIdValue = randomQueries["Random_queryEmpresa"] if randomNumber != 0 else randomText
        descricaoValue = randomText if randomNumber != 0 else bigText500


        apexValues = {
            "P85_RECEBIDO":recebidovalue,
            "P85_VALOR" : valorValue,
            "P85_CONTA_ID":contaIdValue,
            "P85_PESSOA_CLIENTE_ID":pessoaClienteId,
            "P85_DATA_VENCIMENTO":dataVencimentoValue,
            "P85_DATA_PREVISAO_RECEBIMENTO":dataPrevisaoRecebimento,
            "P85_CATEGORIA_FINANCEIRA":categoriaFinanceiraValue,
            "P85_LOJA": lojaIdValue ,
            "P85_DESCRICAO":descricaoValue
        }

        apexGetValue = {}
        for seletor, value in apexValues.items():
            Apex.setValue(browser,seletor,value)
            Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                            message=f"{seletor} teve o valor {value} inserido", 
                                            routine="ContaReceber", error_details="")
            time.sleep(1)
            
            apexGetValue[seletor] = FuncoesUteis.stringToFloat(Apex.getValue(browser,seletor))
            Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                            message=f"{seletor} teve o valor {apexGetValue[seletor]} encontrado", 
                                            routine="ContaReceber", error_details="")
            
        apexSpecificValue = {
            "P85_DATA_VENCIMENTO":dataVencimentoValue,
            "P85_DATA_PREVISAO_RECEBIMENTO":dataPrevisaoRecebimento,
            "P85_DESCRICAO":descricaoValue
        }    

        apexGetSpecificValue = {}
        for seletor, value in apexSpecificValue.items():                       
            apexGetSpecificValue[seletor] = Apex.getValue(browser,seletor)
            Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                            message=f"{seletor} teve o valor {apexGetValue[seletor]} encontrado", 
                                            routine="ContaReceber", error_details="")


            
        apexCompareValues = {
            "Recebimento":(recebidovalue,apexGetValue["P85_RECEBIDO"]),
            "Valor":(valorValue,apexGetValue["P85_VALOR"]),
            "Conta":(contaIdValue,apexGetValue["P85_CONTA_ID"]),
            "Cliente":(pessoaClienteId,apexGetValue["P85_PESSOA_CLIENTE_ID"]),
            "DataVencimento":(dataVencimentoValue,apexGetSpecificValue["P85_DATA_VENCIMENTO"]),
            "DataPrevisaoRecebimento":(dataPrevisaoRecebimento,apexGetSpecificValue["P85_DATA_PREVISAO_RECEBIMENTO"]),
            "CategoriaFinanceira":(categoriaFinanceiraValue,apexGetValue["P85_CATEGORIA_FINANCEIRA"]),
            "Empresa":(lojaIdValue,apexGetValue["P85_LOJA"]),
            "Descricao":(descricaoValue,apexGetSpecificValue["P85_DESCRICAO"])


        }

        FuncoesUteis.compareValues(init,apexCompareValues)



        

    except TimeoutException as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro: Tempo limite excedido ao acessar a página",
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

    except NoSuchElementException as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro: Elemento não encontrado na página",
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

    except Exception as e:  # Captura qualquer outro erro inesperado
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro desconhecido ao acessar a página",
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




    



