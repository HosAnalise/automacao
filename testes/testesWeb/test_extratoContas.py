    
import datetime
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scripts.GerarDados import GeradorDados
from testes.testesWeb.Classes.ExtratoContas import ExtratoContas
from scripts.FuncoesUteis import FuncoesUteis

def test_extratoContas(init):    
        starTime = time.time()

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
        
      

        try:
        
            query = FuncoesUteis.getQueryResults(init,ExtratoContas.queries,10,True)
            print("valor da query:", query)
            FuncoesUteis.goToPage(init,ExtratoContas.url)
            FuncoesUteis.showHideFilter(init,ExtratoContas.seletorFiltro,True)    
            ExtratoContas.contaReceberResumido(init,query)
            ExtratoContas.contaReceberResumido(init,query)
            ExtratoContas.novaTransferencia(init,query,True)
            today = datetime.today()
            todaystr = today.strftime("%d/%m/%Y") 
            randomSituacao = GeradorDados.randomNumberDinamic(0,2)
            valorMin = GeradorDados.randomNumberDinamic(0,100) 
            valorMax = GeradorDados.randomNumberDinamic(100,9999) 
            contaId = query["Query_queryBanco"] 
            categorias = query["Query_queryCategoriaFinanceira"] 
            centroCusto =  query["Query_queryCentroCusto"] 
            origem = query["Query_queryOrigem"] 
            
            apexValues = {
                "P76_CONTAS": contaId,
                "P76_DATA_INICIAL": todaystr,
                "P76_DATA_FINAL":todaystr,
                "P76_SITUACAO":randomSituacao,
                "P76_VALOR_MIN": valorMin,
                "P76_VALOR_MAX": valorMax,
                "P76_CATEGORIAS": categorias,
                "P76_CENTRO_CUSTO": centroCusto,
                "P76_ORIGEM": origem
            }

            FuncoesUteis.aplyFilter(init,apexValues)

            
        except TimeoutException as e:
            Log_manager.add_log(
                application_type=env_application_type,
                level="ERROR",
                message="Erro: Tempo limite excedido ao acessar a página",
                routine="",
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
                        routine="",
                        application_type=env_application_type, 
                        error_details=str(e)
                )
            else:
                Log_manager.add_log(
                    level="ERROR", 
                    message="Falha ao salvar screenshot", 
                    routine="",
                    application_type=env_application_type, 
                    error_details=str(e)
                )

        except NoSuchElementException as e:
            Log_manager.add_log(
                application_type=env_application_type,
                level="ERROR",
                message="Erro: Elemento não encontrado na página",
                routine="",
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
                        routine="",
                        application_type=env_application_type, 
                        error_details=str(e)
                )
            else:
                Log_manager.add_log(
                    level="ERROR", 
                    message="Falha ao salvar screenshot", 
                    routine="",
                    application_type=env_application_type, 
                    error_details=str(e)
                )

        except Exception as e:  # Captura qualquer outro erro inesperado
            Log_manager.add_log(
                application_type=env_application_type,
                level="ERROR",
                message="Erro desconhecido ao acessar a página",
                routine="",
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
                        routine="",
                        application_type=env_application_type, 
                        error_details=str(e)
                )
            else:
                Log_manager.add_log(
                    level="ERROR", 
                    message="Falha ao salvar screenshot", 
                    routine="",
                    application_type=env_application_type, 
                    error_details=str(e)
                )

        finally:
            endTime = time.time()
            executionTime = endTime - starTime

            minutos = int(executionTime // 60)
            segundos = int(executionTime % 60)
            milissegundos = int((executionTime % 1) * 1000)

            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"Tempo de execução do teste: {minutos} min {segundos} s {milissegundos} ms",
                routine="ContaReceber",
                error_details=''
            )

            Log_manager.insert_logs_for_execution()
