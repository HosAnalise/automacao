from datetime import datetime
import locale
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import random
from classes.utils.ApexUtil import Apex


class FuncoesUteis:
    """
    Classe contendo funções utilitárias para automação de testes.
    """

    @staticmethod
    def has_alert(init):
        """
        Verifica se há um alerta de erro na página.
        
        Parâmetros:
            init (tuple): Tupla contendo os objetos necessários para a execução do teste.
        
        Retorna:
            bool: True se o alerta for encontrado, False caso contrário.
        """
        browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init

        try:
            alert = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#t_Alert_Notification"))
            )
            if alert:
                content = alert.text
                Log_manager.add_log(
                    application_type="Web", level="ERROR", 
                    message=f"Erro encontrado: {content}", routine="ContaPagar", error_details=""
                )
                return True
        except (TimeoutException, NoSuchElementException) as e:
            Log_manager.add_log(
                application_type="Web", level="INFO", 
                message="Alerta não encontrado", routine="ContaPagar", error_details=str(e)
            )
            return False

    @staticmethod
    def stringToFloat(element):
        """
        Converte uma string de número formatado para um float.
        
        Parâmetros:
            element (str): String contendo o número a ser convertido.
        
        Retorna:
            float: Número convertido ou None se a conversão falhar.
        """
        if not isinstance(element, str):
            return None  
        
        try:
            return float(element.strip().replace('.', '').replace(',', '.'))
        except ValueError:
            return None  

    @staticmethod
    def formatBrCurrency(value):
        """
        Formata um número para o padrão de moeda brasileiro.
        
        Parâmetros:
            value (int, float): Valor numérico a ser formatado.
        
        Retorna:
            str: Valor formatado como moeda brasileira.
        
        Lança:
            ValueError: Se o valor não for um número.
        """
        if not isinstance(value, (int, float)):
            raise ValueError("O valor deve ser um número (int ou float).")

        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")  
        return locale.currency(value, grouping=True, symbol=False)  

    @staticmethod
    def has_alert_sucess(init):
        """
        Verifica se há um alerta de sucesso na página.
        
        Parâmetros:
            init (tuple): Tupla contendo os objetos necessários para a execução do teste.
        
        Retorna:
            bool: True se o alerta de sucesso for encontrado, False caso contrário.
        """
        browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init

        try:
            alert = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#t_Alert_Success"))
            )
            if alert:
                content = alert.text    
                Log_manager.add_log(
                    application_type="Web", level="INFO", 
                    message=f"Alerta de sucesso encontrado: {content}", routine="ContaPagar", error_details=""
                )
                return True
        except (TimeoutException, NoSuchElementException) as e:
            Log_manager.add_log(
                application_type="Web", level="INFO", 
                message="Alerta de sucesso não encontrado", routine="ContaPagar", error_details=str(e)
            )
            return False

    @staticmethod
    def has_form(init):
        """
        Verifica se há um erro de formulário na página.
        
        Parâmetros:
            init (tuple): Tupla contendo os objetos necessários para a execução do teste.
        
        Retorna:
            bool: True se um erro de formulário for encontrado, False caso contrário.
        """
        browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init

        try:
            formError = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".a-Form-error"))
            )
            if formError:
                content = formError.text
                Log_manager.add_log(
                    application_type='Web', level="ERROR", 
                    message=f"Erro de formulário encontrado: {content}", routine="ContaPagar", error_details=""
                )
                return True
        except (TimeoutException, NoSuchElementException) as e:
            Log_manager.add_log(
                application_type='Web', level="INFO", 
                message="Erro de formulário não encontrado", routine="ContaPagar", error_details=str(e)
            )  
            return False 

# Realiza as queries necessarias para preencher as lovs com valor aleatorio recebe um dicinario py. Exemplo: 'queries  = {"nomeDaQuery":"""Select * from dual"""}'    
    @staticmethod
    def getQueryResults(init, queries, limit=10, random_choice=True):
        browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
        start = time.time()

        def obter_valor(lista):
            if random_choice:
                return random.choice(lista) if lista else None
            return lista if lista else []

        def executar_query(cursor, query):
            cursor.execute(query)
            return [row[0] for row in cursor.fetchmany(limit)]  

        try:
            with oracle_db_connection.cursor() as cursor:
                results = {}

                for key, query in queries.items():
                    results[key] = executar_query(cursor, query)

                queryResults = {f"Query_{key}": obter_valor(result) for key, result in results.items()}
                
                return queryResults
        
        except Exception as e:
            return {"error": str(e)}


    

        except Exception as e:
            Log_manager.add_log(application_type =env_application_type,level= "Error", message = f"Erro na excução das queries ", routine="", error_details =f"{e}" )

        finally:
            endTime = time.time()
            executionTime = endTime - start

            minutos = int(executionTime // 60)
            segundos = int(executionTime % 60)
            milissegundos = int((executionTime % 1) * 1000)

            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"Tempo de execução das queries: {minutos} min {segundos} s {milissegundos} ms",
                routine="",
                error_details=''
            )
            
#End RandomQueries(init,queries)

    @staticmethod
    def timestampFormat():
        """
        Retorna um timestamp formatado.
        
        Retorna:
            str: Timestamp no formato 'dd-mm-yyyy HH-MM-SS-ffffff'.
        """
        return datetime.now().strftime("%d-%m-%Y %H-%M-%S-%f")

    @staticmethod
    def compareValues(init, obj):
        """
        Compara pares de valores em um dicionário e registra logs de sucesso ou erro.

        Args:
            init (tuple): Variáveis do ambiente extraídas no início.
            obj (dict): Dicionário onde cada chave mapeia para uma tupla (valor_esperado, valor_atual).

        Returns:
            bool: True se todos os valores forem iguais, False se houver diferenças.
        """
        
        browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
        env_application_type = env_vars.get("WEB")

        if not isinstance(obj, dict):
            Log_manager.add_log(
                application_type=env_application_type,
                level="ERROR",
                message="compareValues - O objeto passado não é um dicionário válido.",
                routine="",
                error_details=""
            )
            return False

        valoresDiferentes = {chave: (v1, v2) for chave, (v1, v2) in obj.items() if v1 != v2}

        if not valoresDiferentes:
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Todos valores foram inseridos corretamente.",
                routine="",
                error_details=""
            )
            return True
        else:
            Log_manager.add_log(
                application_type=env_application_type,
                level="ERROR",
                message="Alguns valores foram inseridos incorretamente.",
                routine="",
                error_details=""
            )
            
            for chave, (v1, v2) in valoresDiferentes.items():
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Valor incorreto - {chave}: {v1} (esperado) ≠ {v2} (atual)",
                    routine="",
                    error_details=""
                )

            return False
        

# Redireciona para uma pagina especifica
    @staticmethod
    def goToPage(init,url):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        url_erp = getEnv.get('URL_ERP')
       
        if not url_erp:
            pytest.fail("Erro crítico: 'URL_ERP' não encontrada no ambiente de variáveis")   

        browser.get(f"{url_erp}{url}")    
#END goToPage(init,url)


# Metodo que aplica filtros essa função recebe um dicionario py. Exemplo : "var = {seletor:value}", use o id do page item e o valor que deseja inserir nos filtros
    @staticmethod
    def aplyFilter(init,apexValues):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")        
        isDictAndNotNull =  isinstance(apexValues, dict) and apexValues
        try:

            if isDictAndNotNull:

                apexGetValue = {}   

                for seletor,value in apexValues.items():
                    Apex.setValue(browser,seletor,value)
                    Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                            message=f"{seletor} teve o valor {value} inserido", 
                                            routine="", error_details="")

                    apexGetValue[seletor] = Apex.getValue(browser,seletor)     
                    Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                            message=f"{seletor} teve o valor {apexGetValue[seletor]} encontrado", 
                                            routine="", error_details="") 
                   

                btnAplicaFiltros = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".t-Button.t-Button--hot.t-Button--simple.t-Button--stretch")))
                btnText = btnAplicaFiltros.text
                
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} encontrado",
                        routine="",
                        error_details=''
                    )
                btnAplicaFiltros.click()
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} clicado",
                        routine="",
                        error_details=''
                    )
                

    
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
#END aplyFilter(init,apexValues)


#Oculta ou mostra barra de filtros
    @staticmethod
    def showHideFilter(init,seletor,showHide):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")  

        try:

            if showHide:
                WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, seletor)))
                script ="$('button#t_Button_rightControlButton > span').click()"
                browser.execute_script(script)
            else:
                script ="$('button#t_Button_rightControlButton > span').click()"
                browser.execute_script(script)   
    
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
#END showHideFilter(init,seletor,showHide)




#Limpa Filtros 
    @staticmethod
    def clearFilter(init,apexValues):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")        
        isDictAndNotNull =  isinstance(apexValues, dict) and apexValues
        
        try:

            if isDictAndNotNull:                   
                apexGetValueBefore = {}   

                for seletor,value in apexValues.items():
                    
                    apexGetValueBefore[seletor] = Apex.getValue(browser,seletor)     
                    Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                            message=f"{seletor} teve o valor {apexGetValueBefore[seletor]} encontrado", 
                                            routine="", error_details="") 

                btnLimpaFiltros = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#filtrosRegion > div.t-Region-bodyWrap > div.t-Region-buttons.t-Region-buttons--bottom > div.t-Region-buttons-right > button:nth-child(2) > span")))
                btnText = btnLimpaFiltros.text
                
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} encontrado",
                        routine="",
                        error_details=''
                    )
                btnLimpaFiltros.click()
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} clicado",
                        routine="",
                        error_details=''
                    )
                

                apexGetValueAfter = {}   

                for seletor,value in apexValues.items():
                    
                    apexGetValueAfter[seletor] = Apex.getValue(browser,seletor)     
                    Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                            message=f"{seletor} teve o valor {apexGetValueAfter[seletor]} encontrado", 
                                            routine="", error_details="")

                valuesBeforeAfter = {chave: (apexGetValueBefore[chave], apexGetValueAfter[chave]) for chave in apexGetValueBefore}
                FuncoesUteis.compareValues(init, valuesBeforeAfter)

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
#END aplyFilter(init,apexValues)
