import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.GerarDados import GeradorDados  
from scripts.ApexUtil import Apex
from scripts.FuncoesUteis import FuncoesUteis
from scripts.Components import Components



def test_contasReceber_insereConta_aba_repeticao(init):
         
    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
    getEnv = env_vars
    env_application_type = getEnv.get("WEB")
    
    randomDay = GeradorDados.randomNumberDinamic(1,30)
    randomMonth = GeradorDados.randomNumberDinamic(1,12)
    randonDayOfTheWeek = GeradorDados.randomNumberDinamic(1,7)
    randomWeeks = GeradorDados.randomNumberDinamic(0,998)
#_________________________________________________________________
# inicio da aba repetição de nova conta a pagar
    try:

        abaRepeticao = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#R221082137306428338_tab"))) 
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: aba Repeticao encontrado", routine="ContaReceber", error_details ="" )        

        browser.execute_script("arguments[0].scrollIntoView(true);", abaRepeticao)        
        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Scrol até aba Repeticao", routine="ContaReceber", error_details ="" )        

        if abaRepeticao:
            abaRepeticao.click()
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: aba Repeticao clicado", routine="ContaReceber", error_details ="" )        


        try:
            has_repeat = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#listaRepeticao")))
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Listas de repetição encontrada, já há repetição incluida", routine="ContaReceber", error_details ="" )
        except  (TimeoutException, NoSuchElementException, Exception) as e:
            has_repeat = 0
            Log_manager.add_log(
                application_type=env_application_type,
                level="ERROR",
                message="Lista de repetições não encontrada",
                routine="ContaReceber",
                error_details=str(e)
            )
            
        if has_repeat == 0: 

            btnRepeticao = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[name='repeticao']"))) 
            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: btnRepeticao encontrado", routine="ContaReceber", error_details ="" )

            if btnRepeticao:

                btnRepeticao.click()
                Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo: btnRepeticao clicado", routine="ContaReceber", error_details ="" )
                
                FuncoesUteis.has_alert(init)
                FuncoesUteis.has_alert_sucess(init)

                seletor = "#contaReceberRepeticao"
                has_frame = Components.has_frame(init,seletor)

                if has_frame:

                    randomZeroOrOne = GeradorDados.randomNumberDinamic(0,1)                                           

                    if randomZeroOrOne == 0:
                        Apex.setValue(browser,"P91_OPCAO_FERIADO","A")
                        opcaoFeriadoValue = Apex.getValue(browser,"P91_OPCAO_FERIADO_0")
                        if opcaoFeriadoValue == "A":
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo P91_OPCAO_FERIADO: Opção feriados teve o valor : Antecipar inserido corretamente", routine="ContaReceber", error_details ="" )

                    elif randomZeroOrOne == 1 :
                        Apex.setValue(browser,"P91_OPCAO_FERIADO","P")  
                        opcaoFeriadoValue = Apex.getValue(browser,"P91_OPCAO_FERIADO_1")
                        if opcaoFeriadoValue == "P":
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo P91_OPCAO_FERIADO: Opção feriados teve o valor : Postergar Sábados e Doomingos inserido corretamente", routine="ContaReceber", error_details ="" )
                

                    if randomZeroOrOne == 0:
                        Apex.setValue(browser,"P91_OPCAO_COMPETENCIA","O")
                        opcaoCompetencia = Apex.getValue(browser,"P91_OPCAO_COMPETENCIA")
                        if opcaoCompetencia == "O":
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo P91_OPCAO_COMPETENCIA: Opção Competencia teve o valor: Ajustar Data Emissão/Competência conforme periodicidade da repetição  inserido corretamente", routine="ContaReceber", error_details ="" )
                    elif randomZeroOrOne == 1:
                        Apex.setValue(browser,"P91_OPCAO_COMPETENCIA","R")     
                        opcaoCompetencia = Apex.getValue(browser,"P91_OPCAO_COMPETENCIA")
                        if opcaoCompetencia == "R":
                            Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Campo P91_OPCAO_COMPETENCIA: Opção Competencia teve o valor: Manter mesmo dia Data Emissão/Competência da conta original nas repetições inserido corretamente", routine="ContaReceber", error_details ="" )


                    randomPeriodo = GeradorDados.randomNumberDinamic(0, 2)

                    # Mapeia os valores possíveis
                    periodo_map = {
                        0: "M",
                        1: "S",
                        2: "E"
                    }

                    # Define o valor correspondente
                    valor_selecionado = periodo_map[randomPeriodo].strip().upper()        
                    Apex.setValue(browser, "P91_SELECAO_PERIODO", valor_selecionado)  


                    selecaoPeriodoValue = Apex.getValue(browser, "P91_SELECAO_PERIODO")
                    time.sleep(2)
                    
                    if selecaoPeriodoValue:
                        selecaoPeriodoValue = selecaoPeriodoValue[0].strip().upper()
                        selecaoPeriodoValue = str(selecaoPeriodoValue)

                    if selecaoPeriodoValue == valor_selecionado:
                        Log_manager.add_log(
                            application_type=env_application_type,
                            level="INFO",
                            message=f"Campo P91_OPCAO_COMPETENCIA: Seleção período teve o valor inserido corretamente valor selecionado {valor_selecionado}",
                            routine="ContaReceber",
                            error_details="")
                    else:
                        Log_manager.add_log(
                            application_type=env_application_type,
                            level="ERROR",
                            message="Falha ao definir o valor do campo : Seleção período",
                            routine="ContaReceber",
                            error_details=f"Esperado: {valor_selecionado}, Obtido: {selecaoPeriodoValue}" )


                    if selecaoPeriodoValue == "M":
                        WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P91_DIA")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P91_DIA encontrado", routine="ContaReceber", error_details ="" )

                        Apex.setValue(browser, "P91_DIA", randomDay)
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P91_DIA:Todo dia teve o valor inserido corretamente", routine="ContaReceber", error_details ="" )
                        time.sleep(1)

                        WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P91_QUANTIDADE_MES")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P91_QUANTIDADE_MES encontrado", routine="ContaReceber", error_details ="" )

                        Apex.setValue(browser, "P91_QUANTIDADE_MES", randomMonth)
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P91_QUANTIDADE_MES: Repetir por teve o valor inserido corretamente", routine="ContaReceber", error_details ="" )
                        
                        btnNovaSimulacao = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B119202079299682336")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação encontrado", routine="ContaReceber", error_details ="" )

                        btnNovaSimulacao.click()
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação clicado", routine="ContaReceber", error_details ="" )

                    elif selecaoPeriodoValue == "S":
                        WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P91_DIA_SEMANA")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P91_DIA_SEMANA encontrado", routine="ContaReceber", error_details ="" )

                        Apex.setValue(browser, "P91_DIA_SEMANA", randonDayOfTheWeek)
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P91_DIA_SEMANA:Repetir:todo(a) teve o valor inserido corretamente", routine="ContaReceber", error_details ="" )
                        time.sleep(1)

                        WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P91_QUANTIDADE_SEMANA")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P91_QUANTIDADE_SEMANA encontrado", routine="ContaReceber", error_details ="" )
                        
                        Apex.setValue(browser, "P91_QUANTIDADE_SEMANA", randomWeeks)
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P91_QUANTIDADE_SEMANA:por teve o valor inserido corretamente", routine="ContaReceber", error_details ="" )
                        
                        btnNovaSimulacao = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B119200508165682334")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação encontrado", routine="ContaReceber", error_details ="" )

                        btnNovaSimulacao.click()
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação clicado", routine="ContaReceber", error_details ="" )
                    
                    elif selecaoPeriodoValue == "E":
                        WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P91_A_CADA_DIA")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P91_A_CADA_DIA encontrado", routine="ContaReceber", error_details ="" )

                        Apex.setValue(browser, "P91_A_CADA_DIA", randomWeeks)
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P91_A_CADA_DIA :Repetir a cada teve o valor inserido corretamente", routine="ContaReceber", error_details ="" )
                        time.sleep(1)

                        WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#P91_QUANTIDADE_VEZ")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "P91_QUANTIDADE_VEZ encontrado", routine="ContaReceber", error_details ="" )

                        Apex.setValue(browser, "P91_QUANTIDADE_VEZ", randomWeeks)
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Campo P91_QUANTIDADE_VEZ :por teve o valor inserido corretamente", routine="ContaReceber", error_details ="" )
                        
                        btnNovaSimulacao = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B119203509952682337")))
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação encontrado", routine="ContaReceber", error_details ="" )

                        btnNovaSimulacao.click()
                        Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão nova simulação clicado", routine="ContaReceber", error_details ="" )

                        FuncoesUteis.has_form(init)           


                    WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#simulacao")))
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Tabela Criada Simulação realizada", routine="ContaReceber", error_details ="" )


                    btnSaveIframeRepeticaoPagamento = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B119206935067682339"))) 
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão salvar da aba geração de repetições encontrado", routine="ContaReceber", error_details ="" )

                    # browser.execute_script("arguments[0].scrollIntoView(true);", btnSaveIframeRepeticaoPagamento)        
                    # Log_manager.add_log(application_type =env_application_type,level= "INFO", message = f"Scrol até aba Repeticao", routine="ContaReceber", error_details ="" ) 
            
                    btnSaveIframeRepeticaoPagamento.click()
                    Log_manager.add_log(application_type =env_application_type,level= "INFO", message = "Botão salvar da aba geração de repetições clicado", routine="ContaReceber", error_details ="" )

            else:
                Log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Campo: btnRepeticao não encontrado", routine="ContaReceber", error_details ="" )
                

            FuncoesUteis.has_alert(init)
        
    except TimeoutException as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro: Tempo limite excedido ao acessar a página",
            routine="ContaPagar",
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
            routine="ContaPagar",
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
            routine="ContaPagar",
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
        browser.switch_to.default_content()