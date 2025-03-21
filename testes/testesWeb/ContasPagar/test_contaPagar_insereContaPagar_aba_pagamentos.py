from datetime import datetime,timedelta
import random
import time
import lorem
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.GerarDados import GeradorDados  
from scripts.FuncoesUteis import FuncoesUteis
from scripts.ApexUtil import Apex
from selenium.webdriver.common.action_chains import ActionChains


def test_contasPagar_insereConta_aba_pagamentos(init,query):
    

        
  
       

    randomContaId,randomFornecedorId,randomCategoriaFinanceiraId,randomEmpresaId,randomPagamentoId,randomChavePixId,randomBancoId,randomCentroCustoId,randomModeloDocumentoID = query
    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
    getEnv = env_vars
    env_application_type = getEnv.get("WEB")
    
    random_value = round(random.uniform(1, 9999), 2)
    randomStr = FuncoesUteis.formatBrCurrency(random_value)
    randomValue = FuncoesUteis.stringToFloat(randomStr)
    randomText = lorem.paragraph()
    randomNumber = GeradorDados.randomNumberDinamic(0,2)
    randomDay = GeradorDados.randomNumberDinamic(1,30)
    descontoCondicionalValue = 0
  

    today = datetime.today()
    randomDay = GeradorDados.randomNumberDinamic(0, 30)
    randomDate = today + timedelta(days=randomDay)
    finalDate = randomDate.strftime("%d/%m/%Y")

    bigText700 = GeradorDados.gerar_texto(700)




#_________________________________________________________________
# inicio da aba pagamento de nova conta a pagar  
    try:
        valorOriginalValue = Apex.getValue(browser,"P47_VALOR")

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

        if randomNumber in (0, 2):


            lancaDescontoCondicional = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#B107285263114283801"))) 
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão lança denconto condicional encontrado", routine="ContaPagar", error_details ="" )

            
            lancaDescontoCondicional.click()
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão lança denconto condicional clicado", routine="ContaPagar", error_details ="" )

            WebDriverWait(browser, 30).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "[title='Lançamento Desconto Condicional']"))) 
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Trocando para iframe Lançamento Desconto Condicional ", routine="ContaPagar", error_details ="" )

            descontoCondicional = GeradorDados.randomNumberDinamic(1, 100)
            if randomNumber == 0:
                Apex.setValue(browser,"P220_DESCONTO",descontoCondicional)
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f" Desconto Condicional inserido {descontoCondicional} ", routine="ContaPagar", error_details ="" )

                Apex.setValue(browser,"P220_OBSERVACAO",randomText)
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Texto de observação inserido", routine="ContaPagar", error_details ="" )


            else:
                Apex.setValue(browser,"P220_DESCONTO",randomValue)
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f" Desconto Condicional inserido {randomValue} ", routine="ContaPagar", error_details ="" )

                Apex.setValue(browser,"P220_OBSERVACAO",bigText700)   
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Texto 700 caracteres inserido", routine="ContaPagar", error_details ="" )

            btnSaveIframeDescontoCondicional = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B107285890923283807")))    
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão Save denconto condicional encontrado", routine="ContaPagar", error_details ="" )

            descontoCondicionalValue = FuncoesUteis.stringToFloat(Apex.getValue(browser,"P220_DESCONTO"))
            


            btnSaveIframeDescontoCondicional.click()
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão Save denconto condicional clicado", routine="ContaPagar", error_details ="" )
            
            valorOriginalFormatado = FuncoesUteis.stringToFloat(valorOriginalValue)
            novoValor = abs(valorOriginalFormatado - descontoCondicional)

            has_alert = FuncoesUteis.has_alert(init)
            if has_alert:

                
                    Apex.setValue(browser,"P220_DESCONTO",novoValor)
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f" Desconto Condicional inserido {novoValor} ", routine="ContaPagar", error_details ="" )
                    btnSaveIframeDescontoCondicional.click()
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão Save denconto condicional clicado", routine="ContaPagar", error_details ="" )
            
            browser.switch_to.default_content()
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Voltando para o conteudo principal", routine="ContaPagar", error_details ="" )

        elif randomNumber in (1,2):
            

            novoPagamento = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B264204626044900605")))    
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão novo pagamento encontrado", routine="ContaPagar", error_details ="" )

            novoPagamento.click()
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão novo pagamento clicado", routine="ContaPagar", error_details ="" )
            
            
            WebDriverWait(browser, 30).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "#Pagamentos")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Trocando para iframe Pagamentos ", routine="ContaPagar", error_details ="" )
            
            valorPagamentoDividido = round((valorOriginalFormatado/3),2)
            valorDescontoDividido = round((randomValue/4),2)
            valorDescontoDividido = FuncoesUteis.formatBrCurrency(valorDescontoDividido)
            print(f'Valor do desconto a ser inserido {valorDescontoDividido}')


            if randomNumber == 0:
                Apex.setValue(browser,"P70_CONTA_ID",randomContaId)
                Apex.setValue(browser,"P70_FORMA_PAGAMENTO",randomPagamentoId)
                Apex.setValue(browser,"P70_DATA_PAGAMENTO",finalDate)
                Apex.setValue(browser,"P70_VALOR_PAGAMENTO",valorPagamentoDividido)
                Apex.setValue(browser,"P70_DESCONTO",valorDescontoDividido)
                Apex.setValue(browser,"P70_JUROS",randomValue)
                Apex.setValue(browser,"P70_MULTA",randomValue)
                Apex.setValue(browser,"P70_ACRESCIMOS",randomValue)     
                Apex.setValue(browser,"P70_OBSERVACAO",randomText)   


            else:
                Apex.setValue(browser,"P70_CONTA_ID",randomText)
                Apex.setValue(browser,"P70_FORMA_PAGAMENTO",randomText)
                Apex.setValue(browser,"P70_DATA_PAGAMENTO",randomText)
                Apex.setValue(browser,"P70_VALOR_PAGAMENTO",randomText)
                Apex.setValue(browser,"P70_DESCONTO",randomText)
                Apex.setValue(browser,"P70_JUROS",randomText)
                Apex.setValue(browser,"P70_MULTA",randomText)
                Apex.setValue(browser,"P70_ACRESCIMOS",randomText)
                

            descontoEditavel  = Apex.getValue(browser,"P70_DESCONTO")
            print(f"Valor desconto apos ser inserido {descontoEditavel}")
            descontoEditavelFloat = FuncoesUteis.stringToFloat(descontoEditavel)  
            print(f"Valor desconto apos ser inserido Float {descontoEditavelFloat}")

            time.sleep(1)

            jurosEditavel = Apex.getValue(browser,"P70_JUROS")
            jurosEditavelFloat = FuncoesUteis.stringToFloat(jurosEditavel)

            multaEditavel = Apex.getValue(browser,"P70_MULTA")
            multaEditavelFloat = FuncoesUteis.stringToFloat(multaEditavel)

            acrescimosEditavel = Apex.getValue(browser,"P70_ACRESCIMOS")
            acrescimosEditavelFloat = FuncoesUteis.stringToFloat(acrescimosEditavel)

            despesas = Apex.getValue(browser,"P70_DESPESAS")
            despesasFloat = FuncoesUteis.stringToFloat(despesas)
            
            valorPagamento = Apex.getValue(browser,"P70_VALOR_PAGAMENTO")
            valorPagamentoFloat = FuncoesUteis.stringToFloat(valorPagamento)

            time.sleep(1)
            
            descontoDisplay  = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P70_DESCONTO_CONTA_DISPLAY > span")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P70_DESCONTO_CONTA_DISPLAY  Display de desconto achado", routine="ContaPagar", error_details ="" )
            descontoDisplay =  descontoDisplay.text      
            
            
            jurosDisplay = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P70_JUROS_CONTA_DISPLAY > span")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P70_JUROS_CONTA_DISPLAY  Display de desconto achado", routine="ContaPagar", error_details ="" )
            jurosDisplay = jurosDisplay.text      
            
            multaDisplay = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P70_MULTA_CONTA_DISPLAY > span")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P70_MULTA_CONTA_DISPLAY  Display de desconto achado", routine="ContaPagar", error_details ="" )
            multaDisplay = multaDisplay.text

            acrescimosDisplay = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P70_VALOR_ACRESCIMOS_DISPLAY > span")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P70_VALOR_ACRESCIMOS_DISPLAY  Display de desconto achado", routine="ContaPagar", error_details ="" )
            acrescimosDisplay = acrescimosDisplay.text
        
            despesasDisplay = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P70_VALOR_DESPESA_DISPLAY > span")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P70_VALOR_DESPESA_DISPLAY  Display de desconto achado", routine="ContaPagar", error_details ="" )
            despesasDisplay = despesasDisplay.text
        
            saldoPagarDisplay = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P70_SALDO_DISPLAY > span")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P70_SALDO_DISPLAY  Display de desconto achado", routine="ContaPagar", error_details ="" )
            saldoPagarDisplay = saldoPagarDisplay.text
        
            valorOriginalDisplay = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P70_VALOR_DISPLAY")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P70_VALOR_DISPLAY  Display de desconto achado", routine="ContaPagar", error_details ="" )
            valorOriginalDisplay = valorOriginalDisplay.text
        
            valorTotal = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P70_VALOR_TOTAL_DISPLAY > span")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P70_VALOR_DISPLAY  Display de desconto achado", routine="ContaPagar", error_details ="" )
            valorTotal = valorTotal.text
        
        
            valorTotalFloat = FuncoesUteis.stringToFloat(valorTotal)
            valorOriginalDisplayFloat = FuncoesUteis.stringToFloat(valorOriginalDisplay)
            descontoDisplayFloat = FuncoesUteis.stringToFloat(descontoDisplay)

            jurosDisplayFloat = FuncoesUteis.stringToFloat(jurosDisplay)
            multaDisplayFloat = FuncoesUteis.stringToFloat(multaDisplay)
            acrescimosDisplayFloat = FuncoesUteis.stringToFloat(acrescimosDisplay)
            despesasDisplayFloat = FuncoesUteis.stringToFloat(despesasDisplay)
            saldoPagarDisplayFloat = FuncoesUteis.stringToFloat(saldoPagarDisplay)


        valorSomado =  round(abs(valorOriginalDisplayFloat - descontoDisplayFloat + jurosDisplayFloat + multaDisplayFloat + acrescimosDisplayFloat),2)

    
        # Dicionário para armazenar comparações
        valores = {
            "Desconto": ((descontoEditavelFloat + descontoCondicionalValue), descontoDisplayFloat),
            "Juros": (jurosEditavelFloat, jurosDisplayFloat),
            "Multa": (multaEditavelFloat, multaDisplayFloat),
            "Acréscimos": (acrescimosEditavelFloat, acrescimosDisplayFloat),
            "Despesas": (despesasFloat, despesasDisplayFloat),
            "Valor Total": (valorTotalFloat, valorSomado),
            "Valor Pagamento": (valorPagamentoFloat, saldoPagarDisplayFloat),
            "Valor Original": (valorOriginalValue,valorOriginalDisplayFloat)
        }

        # Verifica quais valores são diferentes
        valoresDiferentes = {chave: (v1, v2) for chave, (v1, v2) in valores.items() if v1 != v2}

        if not valoresDiferentes:
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Todos valores foram inseridos corretamente ", routine="ContaPagar", error_details ="" )

        else:
            Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = " Valores foram inseridos incorretamente  ", routine="ContaPagar", error_details ="" )

            for chave, (v1, v2) in valoresDiferentes.items():
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f" valores incorretos: - {chave}: {v1} (esperado) ≠ {v2} (atual)", routine="ContaPagar", error_details ="" )



        btnSaveIframePagamentos =  WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#btn_salvar"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão save do iframe Pagamentos encontrado", routine="ContaPagar", error_details ="" )

        btnSaveIframePagamentos.click()
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão save do iframe Pagamentos clicado", routine="ContaPagar", error_details ="" )



        browser.switch_to.default_content()
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Voltando para o conteudo principal", routine="ContaPagar", error_details ="" )
        
        has_alert = FuncoesUteis.has_alert(init)
            

        

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