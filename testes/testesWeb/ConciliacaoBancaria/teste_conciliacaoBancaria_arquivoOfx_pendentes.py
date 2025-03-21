from datetime import datetime, timedelta
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.Components import Components
from scripts.GerarDados import GeradorDados  
from scripts.ApexUtil import Apex
from scripts.FuncoesUteis import FuncoesUteis
from testes.testesWeb.Classes.ExtratoContas import ExtratoContas

@pytest.mark.parametrize("browser, login", [("chrome", "teste")], indirect=True)
def test_conciliacaoBancaria_arquivoOfx_pendentes(init,query):
       
    browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
    randomQuery = query


    getEnv = env_vars
    env_application_type = getEnv.get("WEB")
    randomValue = GeradorDados.randomNumberDinamic(0,7)
    today = datetime.today()
    randomDay = GeradorDados.randomNumberDinamic(0, 30)
    randomDate = today + timedelta(days=randomDay)
    finalDate = randomDate.strftime("%d/%m/%Y")
    


    try:
        span = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"d.fa.fa-times-circle.iconGrey")))
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão span encontrado",
            routine="ConciliacaoBancaria",
            error_details=''
        )
        spanClass = span.get_attribute("class")

        print(f"spanClass: {spanClass}")

        while spanClass == "fa fa-spinner fa-anim-spin":
            pass
        
        span.click()
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Botão span clicado ",
            routine="ConciliacaoBancaria",
            error_details=''
        )

        formasDeConciliacao = {
            0 : "[title='Selecione um lançamento para conciliar']",
            1 : "[acao='novoLancamentoExistente']",
            2 : "[acao='novoLancamento']",
            3 : "[acao='novoLancamentoTransferencia']",
            4 : "[acao='associarLancamento']",
            5 : "[acao='associarLancamentoTransferencia']",
            6 : "[acao='ignorarLancamento']",
            7 : "[acao='naoCorrespondentes']",
        }

        for key, value in formasDeConciliacao.items():

            if randomValue == key and randomValue != 0:
                btnClicado = WebDriverWait(browser,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,value)))                
                btnText = btnClicado.text                
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado ",
                    routine="ConciliacaoBancaria",
                    error_details=''
                )
                btnClicado.click()
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} clicado ",
                    routine="ConciliacaoBancaria",
                    error_details=''
                )
                if randomValue == 1:
                    
                    seletor = "[title='Incluir Lançamento em Conta Existente']"
                    has_frame = Components.has_frame(init,seletor)

                    if has_frame:
                        WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#P157_QUITAR_SALDO")))

                        randomCpf = GeradorDados.gerar_cpf()
                        randomNumeroPedido = GeradorDados.gerar_chave_aleatoria()
                        valor1 = GeradorDados.randomNumberDinamic(1, 99999)
                        valor2 = GeradorDados.randomNumberDinamic(1, 99999)
                        randomValorMin, randomValorMax = sorted([valor1, valor2])
                        randomValorMin = FuncoesUteis.formatBrCurrency(randomValorMin)
                        randomValorMax = FuncoesUteis.formatBrCurrency(randomValorMax)
                        randomOneTwo = GeradorDados.randomNumberDinamic(0,2)
                        queryempresa = randomQuery["Random_queryEmpresa"] if randomOneTwo == 0  else -1
                        queryContas = randomQuery["Random_queryContaId"] if randomOneTwo == 0  else -1
                        queryCategorias = randomQuery["Random_queryCategoriaFinanceira"] if randomOneTwo == 0  else -1
                        queryCliente = randomQuery["Random_queryCliente"] if randomOneTwo == 0  else -1


                        pageitens = {
                            "P157_QUITAR_SALDO": queryempresa,
                            "P157_TIPO_PERIODO": 0,
                            "P157_DATA_INICIAL": today,
                            "P157_DATA_FINAL": finalDate,
                            "P157_NUMERO_DOCUMENTO": randomCpf,
                            "P157_NUMERO_PEDIDO": randomNumeroPedido,
                            "P157_CONTAS": queryContas,
                            "P157_CATEGORIAS":queryCategorias ,
                            "P157_CLIENTE": queryCliente,
                            "P157_VALOR_MIN": randomValorMin,
                            "P157_VALOR_MAX": randomValorMax,
                        }

                        for key,value in pageitens.items():
                            Apex.setValue(browser,key,value)
                            pageitensValues = {}
                            pageitensValues[key] = Apex.getValue(browser,key)

                        

                        has_insert = {
                            "P157_QUITAR_SALDO": (queryempresa, pageitensValues["P157_QUITAR_SALDO"]),
                            "P157_TIPO_PERIODO": (0,pageitensValues["P157_TIPO_PERIODO"]),
                            "P157_DATA_INICIAL": (today,pageitensValues["P157_DATA_INICIAL"]),
                            "P157_DATA_FINAL": (finalDate,pageitensValues["P157_DATA_FINAL"]),
                            "P157_NUMERO_DOCUMENTO": (randomCpf,pageitensValues["P157_NUMERO_DOCUMENTO"]),
                            "P157_NUMERO_PEDIDO": (randomNumeroPedido,pageitensValues["P157_NUMERO_PEDIDO"]),
                            "P157_CONTAS": (queryContas,pageitensValues["P157_CONTAS"]),
                            "P157_CATEGORIAS":(queryCategorias,pageitensValues["P157_CATEGORIAS"]) ,
                            "P157_CLIENTE": (queryCliente,pageitensValues["P157_CLIENTE"]),
                            "P157_VALOR_MIN": (randomValorMin,pageitensValues["P157_VALOR_MIN"]),
                            "P157_VALOR_MAX": (randomValorMax,pageitensValues["P157_VALOR_MAX"]),
                        }
                        

                        FuncoesUteis.compareValues(init,has_insert)

                        btnFilter = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B111432143494655101")))
                        btnText = btnFilter.text                
                        Log_manager.add_log(
                            application_type=env_application_type,
                            level="INFO",
                            message=f"Botão {btnText} encontrado ",
                            routine="ConciliacaoBancaria",
                            error_details=''
                        )
                        btnFilter.click()
                        Log_manager.add_log(
                            application_type=env_application_type,
                            level="INFO",
                            message=f"Botão {btnText} clicado ",
                            routine="ConciliacaoBancaria",
                            error_details=''
                        )


                        has_table = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,".a-IRR-noDataMsg-text")))

                        if not has_table:
                            checkBoxes = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".selecaoConta.form-check-input")))
                            checkBoxesId = checkBoxes.get_attribute("value")
                            Log_manager.add_log(
                            application_type=env_application_type,
                            level="INFO",
                            message=f"Checkbox com id: {checkBoxesId}, encontrado",
                            routine="ConciliacaoBancaria",
                            error_details=''
                            )
                            checkBoxes.click()
                            Log_manager.add_log(
                                application_type=env_application_type,
                                level="INFO",
                                message=f"Checkbox com id: {checkBoxesId}, clicado",
                                routine="ConciliacaoBancaria",
                                error_details=''
                            )

                            btnConciliar = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#conciliarButton")))
                            btnText = btnConciliar.text                
                            Log_manager.add_log(
                                application_type=env_application_type,
                                level="INFO",
                                message=f"Botão {btnText} encontrado ",
                                routine="ConciliacaoBancaria",
                                error_details=''
                            )
                            btnConciliar.click()
                            Log_manager.add_log(
                                application_type=env_application_type,
                                level="INFO",
                                message=f"Botão {btnText} clicado ",
                                routine="ConciliacaoBancaria",
                                error_details=''
                            )

                            conciliado = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,".subTitlePrincipal")))
                            conciliadoText = conciliado.text

                            if conciliadoText == "Lançamento Conciliado":
                                Log_manager.add_log(
                                application_type=env_application_type,
                                level="INFO",
                                message=f"Lançamento Conciliado com sucesso! via {key}",
                                routine="ConciliacaoBancaria",
                                error_details=''
                            )
                elif randomValue == 2:
                    ExtratoContas.contaReceber(init,query)      
                elif randomValue == 3:
                    ExtratoContas.novaTransferencia(init,query,False)    



                          





                        
                            
                        
                        







                    





    except TimeoutException as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message="Erro: Tempo limite excedido ao acessar a página",
            routine="ConciliacaoBancaria",
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
            routine="ConciliacaoBancaria",
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
            routine="ConciliacaoBancaria",
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






