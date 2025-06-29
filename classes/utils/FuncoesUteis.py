from datetime import datetime
import locale
from multiprocessing.spawn import prepare
import socket
import time
import pytest
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import random
from classes.utils.ApexUtil import Apex
from classes.utils.LogManager import LogManager
from conftest import env_vars

from classes.utils.decorators import com_visual


Log_manager = LogManager()
class FuncoesUteis:
    """
    Classe contendo funções utilitárias para automação de testes.
    """

   

    @staticmethod
    def stringToFloat(element:str) -> float|None:
        """
        Converte uma string de número formatado para um float.
        
        :param element:
            String contendo o número a ser convertido.
        
        :return:
            float: Número convertido ou None se a conversão falhar.
        """
       
        
        try:
            return float(element.strip().replace('.', '').replace(',', '.'))
        except ValueError:
            return None  

    @staticmethod
    def formatBrCurrency(value: int | float) -> str:
        """
        Formata um número para o padrão de moeda brasileiro.

        :param value: Valor numérico a ser formatado (int ou float).
        :return: Valor formatado como moeda brasileira, sem símbolo (ex: 1.234,56).
        :raises ValueError: Se o valor não for numérico.
        """
        if not isinstance(value, (int, float)):
            raise ValueError("O valor deve ser numérico (int ou float).")

        try:
            locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
        except locale.Error:
            # Fallback comum no Windows
            try:
                locale.setlocale(locale.LC_ALL, "Portuguese_Brazil.1252")
            except locale.Error:
                raise RuntimeError("Locale brasileiro não está instalado no sistema.")

        return locale.currency(value, grouping=True, symbol=False)

    
# Realiza as queries necessarias para preencher as lovs com valor aleatorio recebe um dicinario py. Exemplo: 'queries  = {"nomeDaQuery":"""Select * from dual"""}'    
    @staticmethod
    def getQueryResults(init:tuple, queries:dict, limit:int=10, random_choice:bool=True)-> dict:
        """
        Retorna o resultado de uma query, ou se o usurio quiser apenas um valor aleatorio dessa query.

        :param init: Tupla contendo os objetos necessários:
                     (browser, login, Log_manager, get_ambiente, env_vars,
                      seletor_ambiente, screenshots, oracle_db_connection).
        :param queries: Dict contendo todas as queries a serem realizadas. 
        :param limit: int limita os resultados das queryes 
        :param random_choice: bool permite o usuario escolher se a query vem com o valor total ou apenas um valor aleatorio
        :return: Retorna um dicionario {"Query_nomeQuery": valor}

        """
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
            Log_manager.add_log(application_type =env_application_type,level= "Error", message = f"Erro na excução das queries ", routine="", error_details =f"{e}" )
            return {"error": str(e)}
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
        
        :return     str: Timestamp no formato 'dd-mm-yyyy HH-MM-SS-ffffff'.
        """
        return datetime.now().strftime("%d-%m-%Y %H-%M-%S-%f")

    @staticmethod
    def compareValues(init:tuple, obj:dict) -> bool:
        """
        Compara pares de valores em um dicionário e registra logs de sucesso ou erro.

      
            :param init: (tuple): Variáveis do ambiente extraídas no início.
            :param obj: (dict): Dicionário onde cada chave mapeia para uma tupla (valor_esperado, valor_atual).

        :return:
            bool: True se todos os valores forem iguais, False se houver diferenças.Também cria logs que mostram os valores com diferenças
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
    def goToPage(init:tuple,url:str,validator=None):
        """
        Redireciona pra pagina especifica

        :param init: Tupla contendo os objetos necessários:
                     (browser, login, Log_manager, get_ambiente, env_vars,
                      seletor_ambiente, screenshots, oracle_db_connection).
        :param url: str Url pra onde deseja ir              

        """
        browser = init[0]

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        url_erp = getEnv.get('URL_ERP')
       
        if not url_erp:
            pytest.fail("Erro crítico: 'URL_ERP' não encontrada no ambiente de variáveis")   

        browser.get(f"{url_erp}{url}")    
#END goToPage(init,url)


# Metodo que aplica filtros essa função recebe um dicionario py. Exemplo : "var = {seletor:value}", use o id do page item e o valor que deseja inserir nos filtros
    @staticmethod
    def aplyFilter(init:tuple,apexValues:dict):
        """
        Aplica valores a componentes apex baseados em um dicionario {seletor:valor} e aplica os filtro na pagina.

        :param init: Tupla contendo os objetos necessários:
                     browser, login, Log_manager, get_ambiente, env_vars,
                      seletor_ambiente, screenshots, oracle_db_connection.

        :param apexValues: dict com itens de pagina apex {seletor:item}         

        """
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")        
        isDictAndNotNull =  isinstance(apexValues, dict) and apexValues
        if isDictAndNotNull:
            try:

            
                for seletor,value in apexValues.items():
                    Apex.setValue(browser,seletor,value)
                    Log_manager.add_log(application_type=env_application_type, level="INFO", 
                                            message=f"{seletor} teve o valor {value} inserido", 
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
    def showHideFilter(init:tuple,seletor:str|bool=False):
        

        """
        Mostra ou esconde o filtro lateral na página com base no seletor.

        Se um seletor for passado, o filtro será fechado (verificando a presença do seletor).
        Se nenhum seletor for passado, o filtro será aberto.

        :param init: Tupla contendo os objetos necessários:
                     (browser, login, Log_manager, get_ambiente, env_vars,
                      seletor_ambiente, screenshots, oracle_db_connection).
        :param seletor: Seletor CSS (str) usado para validar presença do filtro antes de ocultar.
                        Se não for passado, o filtro será exibido.
        """
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")  

        try:

            if seletor:
                try:
                    WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, seletor)))
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Elemento {seletor} encontrado",
                        routine="",
                        error_details=''
                    )
                
                except (TimeoutException,NoSuchElementException,Exception) as e:
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="ERROR",
                        message=f"Erro ao localizar seletor {seletor}. Err : {e}",
                        routine="",
                        error_details=str(e)
                    )
            
            messageFilter = "Filtro Lateral fechado" if seletor else "Filtro Lateral aberto"  
            script ="$('button#t_Button_rightControlButton > span').click()"
            browser.execute_script(script)  
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=messageFilter,
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

        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))
#END showHideFilter(init,seletor)




#Limpa Filtros 
    @staticmethod
    def clearFilter(init:tuple,apexValues:dict):
        """
        Limpa os filtros da página e compara os valores antes e depois da limpeza.

        :param init: Tupla contendo os objetos necessários:
                     browser, login, Log_manager, get_ambiente, env_vars,
                      seletor_ambiente, screenshots, oracle_db_connection.

        :param apexValues: Dicionário onde as chaves são os seletores Apex dos filtros
                           e os valores são os valores esperados podem ser vazios.
        """
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
#END clearFilter(init,apexValues)

    @staticmethod
    def setFilters(init: tuple, apexValues: dict):
        """
        Seta os valores nos campos Apex informados no dicionário.

        :param init: Tupla contendo os objetos necessários:
                    (browser, login, Log_manager, get_ambiente, env_vars,
                    seletor_ambiente, screenshots, oracle_db_connection).
        :param apexValues: Dicionário onde:
                        - Chaves são os seletores Apex dos campos.
                        - Valores são os valores a serem inseridos.
        """
        (browser, login, Log_manager, get_ambiente,
        env_vars, seletor_ambiente, screenshots, oracle_db_connection) = init

        env_application_type = env_vars.get("WEB", "Web")

        if not isinstance(apexValues, dict) or not apexValues:
            Log_manager.add_log(
                application_type=env_application_type,
                level="WARNING",
                message="Nenhum filtro foi passado para preenchimento.",
                routine="",
                error_details=""
            )
            return

        for selector, value in apexValues.items():
            try:
                Apex.setValue(browser, selector, value)
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Valor '{value}' setado com sucesso no seletor '{selector}'.",
                    routine="",
                    error_details=""
                )
            except Exception as e:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="ERROR",
                    message=f"Erro ao setar valor no seletor '{selector}'.",
                    routine="",
                    error_details=str(e)
                )

    #END setFilters(init,apexValues)

    
    @staticmethod
    def combine_lists_to_dict(keys_list:list, values_list:list)->dict:
        """
        Combina duas Lists e transforma em um Dict

        :param keys_list: lista com as chaves que vão compor o dict.
        :param values_list: lista com os valores que vão compor o dict.

        :return: Retorna um dicionario no formato {keys_list : values_list}
        """

       
        return dict(zip(keys_list, values_list))

#END combine_lists_to_dict(keys_set, values_set)
   
    @staticmethod
    def has_connection() -> bool:
        """
        Verifica se há conexão com a internet utilizando dois métodos:
        1. Tentativa de conexão via socket (DNS do Google).
        2. Requisição HTTP para o Google.com.

        :return: True se ambos os testes forem bem-sucedidos, False caso contrário.
        """
        
        def check_socket_connection() -> bool:
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                return True
            except OSError:
                return False

        def check_http_connection() -> bool:
            try:
                response = requests.get("https://www.google.com", timeout=3)
                return response.status_code == 200
            except (requests.RequestException, Exception):
                return False

        return check_socket_connection() and check_http_connection()
# END has_connection()


    @staticmethod
    def setValue(init:tuple,seletor:str,value:str|int):
        """
        Insere um valor em um campo localizado pelo seletor CSS.

        :param init: Tupla contendo os objetos necessários:
                    (browser, login, Log_manager, get_ambiente, env_vars,
                    seletor_ambiente, screenshots, oracle_db_connection).
        :param seletor: Seletor CSS do campo que receberá o valor.
        :param value: Valor a ser inserido no campo.
        """


        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        item = None
        item = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,seletor)))
        textItem = item.text
        item.send_keys(value)
        Log_manager.add_log(
                application_type="WEB",
                level="INFO",
                message=f"Valor {value}, inserido no {textItem}",
                routine="",
                error_details=""
            )

    
       

        
    @staticmethod
    def prepareToCompareValues(init:tuple,apexValues:dict,sendKeys:bool = False):
        """
        Prepara valores em campos APEX e retorna um dicionário com os valores esperados e encontrados.
        :param init: Tupla contendo:
            (browser, login, Log_manager, get_ambiente, env_vars,
            seletor_ambiente, screenshots, oracle_db_connection).
        :param apexValues: Dicionário com seletores como chaves e valores a serem inseridos.
        :param sendKeys: Se True, usa FuncoesUteis.setValue (com send_keys); caso contrário usa Apex.setValue.
        :return: Dicionário {seletor: (valor_encontrado, valor_esperado)}
        """
        browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
        apexGetValue = {}

        for seletor, value in apexValues.items():
            send = lambda: Apex.setValue(browser, seletor, value) if not sendKeys else FuncoesUteis.setValue(init, f"#{seletor}", value)
            try:
                send()

                WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"#{seletor}")))
                apexGetValue[seletor] = Apex.getValue(browser, seletor)

                Log_manager.add_log(
                    application_type='WEB',
                    level="INFO",
                    message=f"{seletor} teve o valor {apexGetValue[seletor]} encontrado",
                    routine="ContaReceber",
                    error_details=""
                )

            except (TimeoutException, NoSuchElementException) as e:
                Log_manager.add_log(
                    application_type='WEB',
                    level="ERROR",
                    message=f"Erro ao manipular {seletor}: {str(e)}",
                    routine="ContaReceber",
                    error_details=str(e)
                )

            except Exception as e:
                Log_manager.add_log(
                    application_type='WEB',
                    level="ERROR",
                    message=f"Erro inesperado em {seletor}: {str(e)}",
                    routine="ContaReceber",
                    error_details=str(e)
                )

            finally:
                if screenshots:
                    screenshot_path = f"{screenshots}/{seletor}.png"
                    if browser.save_screenshot(screenshot_path):
                        Log_manager.add_log(
                            application_type='WEB',
                            level="INFO",
                            message=f"Screenshot salvo em: {screenshot_path}",
                            routine="ContaReceber",
                            error_details=""
                        )
                    else:
                        Log_manager.add_log(
                            application_type='WEB',
                            level="ERROR",
                            message=f"Falha ao salvar screenshot em {screenshot_path}",
                            routine="ContaReceber",
                            error_details=""
                        )

        campos = {seletor: (apexGetValue.get(seletor, None), value) for seletor, value in apexValues.items()}
        return campos
    


    
# END setValue(init,seletor,value)

    @staticmethod
    def guaranteeShowHideFilter(init:tuple,seletor:str,showHide:bool):
        """
        Garante que o filtro lateral esteja visível ou oculto, de acordo com `showHide`.
        
        :param init: Tupla com parâmetros do ambiente.
        :param seletor: Seletor CSS para verificar a visibilidade atual do filtro.
        :param showHide: True para abrir o filtro, False para fechar.
        """

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")  

        if showHide:
            openClose = [
                "Abrir",
                "Aberto"
            ]
        else:
            openClose = [
                "Fechar",
                "Fechado"
            ]

        try:
            # Verifica se o filtro lateral já está aberto
            elemento = WebDriverWait(browser,10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, seletor)))  
            if elemento:
                open = 1
                status = "Aberto"
            else:
                open = False
                status = "Fechado"

            #Ou o filtro deve ficar aberto, porém não está. Ou o filtro deve ficar fechado porém está aberto
            if (showHide and not open) or (not showHide and open):
                script = "$('button#t_Button_rightControlButton > span').click()"
                browser.execute_script(script)

                Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"Foi Escolhido {openClose[0]} o Filtro Lateral, e Ele Estava {status}. Logo, foi {openClose[1]}",
                routine="",
                error_details=''
                )
            else:
                Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"Foi Escolhido {openClose[0]} o Filtro Lateral, Porém Já Estava {status}.",
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
#END guaranteeShowHideFilter(init,seletor,showHide)

    @staticmethod
    def getURL(init:tuple)->str:
        """
        Recupera a url da Window atual.
        
        :param init: Tupla com parâmetros do ambiente.

        :return: str retorna a url da pagina atual
        """
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        url = None  # Inicializa a variável URL

        try:
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Iniciando a captura da URL da nova janela.",
                routine="Prestador/Empresa",
                error_details=''
            )

            # Salve o ID da janela original
            originalWindow = browser.current_window_handle
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"ID da janela original salvo: {originalWindow}",
                routine="Prestador/Empresa",
                error_details=''
            )

            # Aguarde até que uma nova janela seja aberta
            WebDriverWait(browser, 20).until(lambda d: len(d.window_handles) > 1)

            # Obtenha todos os IDs das janelas
            allWindows = browser.window_handles
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"IDs das janelas obtidos: {allWindows}",
                routine="Prestador/Empresa",
                error_details=''
            )

            # Mude o foco para a nova janela (que não é a original)
            for window in allWindows:
                if window != originalWindow:
                    browser.switch_to.window(window)
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Foco alterado para a nova janela: {window}",
                        routine="Prestador/Empresa",
                        error_details=''
                    )
                    break

            # Aguarde até que a URL esteja disponível
            url = WebDriverWait(browser, 20).until(lambda d: d.current_url if d.current_url != "" else False)
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"URL capturada: {url}",
                routine="Prestador/Empresa",
                error_details=''
            )
            
            return url

        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))
#END getURL(init)




    @staticmethod
    def compareValuesDesktop(obj:dict) -> bool:
        """
        Compara pares de valores em um dicionário e registra logs de sucesso ou erro.

        :param obj: (dict): Dicionário onde cada chave mapeia para uma tupla (valor_esperado, valor_atual).

        :return:
            bool: True se todos os valores forem iguais, False se houver diferenças.Também cria logs que mostram os valores com diferenças
        """
        
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


    