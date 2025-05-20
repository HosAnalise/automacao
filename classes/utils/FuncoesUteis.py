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
from classes.utils.GerarDados import GeradorDados
from classes.utils.Components import Components
import random
from classes.utils.ApexUtil import Apex
from classes.utils.LogManager import LogManager
from conftest import env_vars
from typing import Any
from pydantic import BaseModel

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
                    message=(
                        f"Valor incorreto - {chave}: {v1} (esperado, tipo {type(v1).__name__}) "
                        f"≠ {v2} (atual, tipo {type(v2).__name__})"
                    ),
                    routine="",
                    error_details=""
                )

            return False
        

# Redireciona para uma pagina especifica
    @staticmethod
    def goToPage(init:tuple,url:str):
        """
        Redireciona pra pagina especifica

        :param init: Tupla contendo os objetos necessários:
                     (browser, login, Log_manager, get_ambiente, env_vars,
                      seletor_ambiente, screenshots, oracle_db_connection).
        :param url: str Url pra onde deseja ir              

        """
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
        :param seletor: Seletor CSS para verificar a visibilidade atual do filtro, necessita do '#', porém não é obrigatorio passar, pois possui validação interna.
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

        if not seletor.startswith("#"):
            seletor = f"#{seletor}"
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"O seletor foi corrigido automaticamente para '{seletor}', adicionando '#' ao inicio.",
                routine="guaranteeShowHideFilter",
                error_details=""
            )

        try:
            # Verifica se o filtro lateral já está aberto
            try:
                WebDriverWait(browser,5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, seletor)))  
                elemento = True
            except:
                elemento = False

            if elemento:
                open = True
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

    @staticmethod
    def recuperaValores(init:tuple, seletores:set)->dict:
        """
        Recebe um conjunto de seletores e retorna um dicionario com os campos e valores encontrados nos seletores correspondentes.

        :params init :
            Tupla contendo os objetos necessários para a automação:

            - browser: Instância do WebDriver do Selenium.
            - login: Objeto de login (não utilizado diretamente nesta função).
            - Log_manager: Gerenciador de logs para registrar eventos e erros.
            - get_ambiente: Função ou objeto para obter informações do ambiente.
            - env_vars: Dicionário contendo variáveis do ambiente.
            - seletor_ambiente: Seletor de ambiente (não utilizado diretamente nesta função).
            - screenshots: Caminho para salvar capturas de tela em caso de erro.
            - oracle_db_connection: Conexão com o banco de dados Oracle (não utilizada nesta função).

        :params seletores :
            - Conjunto de seletores que serão utilizados para localizar e retornar os campos na página.

            - Ex. de Envio: seletores = {"P76_CONTA_ORIGEM", "P76_CONTA_DESTINO"}

        :return camposFiltros:
            - Dicionário contendo os campos e valores dos seletores especificados.
        """
        
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        valoresDict = {}
        for seletor in seletores:
            WebDriverWait(browser, 15).until(
                lambda driver: driver.execute_script(
                    f"return typeof apex.item('{seletor}') !== 'undefined' && apex.item('{seletor}') !== null"
                )
            )
            valoresDict[seletor] = Apex.getValue(browser, seletor)
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"Capturado valor do seletor {seletor}: {valoresDict[seletor]}",
                routine="",
                error_details=''
            )

        return valoresDict
#END recuperaValores(init, dict)

    @staticmethod
    def scrollIntoView(init:tuple, seletor:str, clica:bool = False):
        """
        Recebe um seletor, é arrastado a tela até o seletor estiver em vista.

        :params init :
            Tupla contendo os objetos necessários para a automação:

            - browser: Instância do WebDriver do Selenium.
            - login: Objeto de login (não utilizado diretamente nesta função).
            - Log_manager: Gerenciador de logs para registrar eventos e erros.
            - get_ambiente: Função ou objeto para obter informações do ambiente.
            - env_vars: Dicionário contendo variáveis do ambiente.
            - seletor_ambiente: Seletor de ambiente (não utilizado diretamente nesta função).
            - screenshots: Caminho para salvar capturas de tela em caso de erro.
            - oracle_db_connection: Conexão com o banco de dados Oracle (não utilizada nesta função).

        :params seletor :
            - String de seletor utilizado para dar scroll até acha-lo. Deve ser passado sem o '#'.

        :params clica :
            - Booleano que indica se o elemento deve ser clicado após o scroll.
        """
        
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        campo = WebDriverWait(browser,30).until(EC.presence_of_element_located((By.CSS_SELECTOR, f"#{seletor}")))
        browser.execute_script("arguments[0].scrollIntoView(true);", campo)
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Scroll até o seletor {seletor} realizado com sucesso.",
            routine="",
            error_details=''
        )

        Components.btnClick(init, f"#{seletor}") if clica else None
#END scrollIntoView(init, seletor)

    @staticmethod
    def geraValoresRandom(init:tuple, dictRecebido:dict[str, type | tuple[type, int, int]]) -> dict[str, Any]:
        """
        Recebe um dicionário contendo Seletores como chave e Types como valores, é possivel mandar uma tupla como valor, que 
        sobrepõem o range default, passando (type, valor minimo e maximo).

        Retorna um dicionário com os mesmos seletores e valores gerados aleatoriamente para cada tipo especificado.

        Types Recebiveis (range default):
            - str: String aleatória entre 5 e 30 caracteres alfanuméricos.
            - int: Número inteiro aleatório entre 5 e 30.
            - float: Número decimal aleatório entre 5 e 30 com duas casas decimais.
            - bool: Valor booleano aleatório (True ou False).
            - "date": Data aleatória no formato 'dd/mm/yyyy', não é possivel passar configuração por parametro.

        :params init :
            Tupla contendo os objetos necessários para a automação:

            - browser: Instância do WebDriver do Selenium.
            - login: Objeto de login (não utilizado diretamente nesta função).
            - Log_manager: Gerenciador de logs para registrar eventos e erros.
            - get_ambiente: Função ou objeto para obter informações do ambiente.
            - env_vars: Dicionário contendo variáveis do ambiente.
            - seletor_ambiente: Seletor de ambiente (não utilizado diretamente nesta função).
            - screenshots: Caminho para salvar capturas de tela em caso de erro.
            - oracle_db_connection: Conexão com o banco de dados Oracle (não utilizada nesta função).
        
        :params dictRecebido :
            - Dicionário contendo seletores como chave e tipos como valores.

        Exemplos de dictRecebido e Returns:
            - "P85_DATA_VENCIMENTO": "date" = data aleatoria "04/08/2021"
            - "P85_VALOR": float = float aleatorio "1234,56"
            - "P84_ORIGEM": (int, 30, 50) = int aleatorio entre 30 e 50 "39"
        """

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        resultados = {}

        for seletor, config in dictRecebido.items():
            if isinstance(config, tuple):
                tipo, x, y = config
            else:
                tipo, x, y = config, None, None

            tipo_str = tipo if isinstance(tipo, str) else tipo.__name__.lower()

            if tipo_str == "str":
                valor = GeradorDados.simpleRandString(init, x if x is not None else 10, y if y is not None else 50, seletor)
                # método já cria logs

            elif tipo_str == "int":
                valor = random.randint(x if x is not None else 5, y if y is not None else 30)
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Gerado o int aleatório : {valor} | Variável {seletor}",
                        routine="",
                        error_details=""
                    )

            elif tipo_str == "float":
                parte_inteira = random.randint(x if x is not None else 5, y if y is not None else 30)
                valor = (f"{parte_inteira},{random.randint(0, 99):02d}")
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Gerado o float aleatório : {valor} | Variável {seletor}",
                        routine="",
                        error_details=""
                    )

            elif tipo_str == "bool":
                valor = random.choice([True, False])
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Gerado boolean {valor} para o seletor {seletor}",
                        routine="",
                        error_details=""
                    )

            elif tipo_str == "date":
                valor = GeradorDados.simpleRandDate(init, seletor)
                # método já cria logs

            else:
                raise ValueError(f"Tipo não suportado: {tipo}")

            resultados[seletor] = valor

        return resultados
#END geraValoresRandom(init, dictRecebido)

    @staticmethod
    def objToDictObrigatorio(init:tuple, objRecebido:BaseModel, camposObrigatorios:dict) -> dict:
        """
        Recebe um objeto e um dicionario, compara os valores do objeto com o dicionario, criando um novo dicionario.
        Caso o objeto possua valor nos campos obrigatórios, tais valores serão utilizados no dicionário, caso contrário, será utilizado os valores recebidos no dicionário.
        Retorna o dicionário criado para manipulação.

        :param init:
            Tupla com parâmetros do ambiente.

        :param objRecebido:
            Objeto Pydantic a ser convertido em dicionário.

        :param camposObrigatorios:
            Dicionário com os campos obrigatórios como chaves, e os valores aleatórios como valores.

        :return:
            Dicionário resultante com campos preenchidos a partir do objeto e/ou campos obrigatórios.
        """

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        dictObjeto = objRecebido.model_dump(exclude_none=True)
        for chave, valor in camposObrigatorios.items():
            if dictObjeto.get(chave) is None:
                dictObjeto[chave] = valor

                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Valor no seletor '{chave}' não encontrado no objeto recebido. Valor default utilizado: '{valor}'.",
                    routine="objToDictObrigatorio",
                    error_details=""
                )
                
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Dicionário final criado com {len(dictObjeto)} campos.",
            routine="objToDictObrigatorio",
            error_details=""
        )
        
        return dictObjeto
#END objToDictObrigatorio(init, objRecebido, cmaposObrigatorios)

    @staticmethod
    def mapearObjeto(init:tuple, objRecebido:BaseModel, mapa:dict[str, str | list[str]]) -> dict[str, str]:
        """
        Recebe um objeto BaseModel e um dicionário de mapeamento de chaves.
        Retorna um novo dicionario, com as chaves alteradas e valores recebidos pelo objeto.
        Um seletor só estara no dicionário final caso o mesmo esteja tanto no Objeto quanto no dicionario de mapeamento.

        :param init:
            Tupla com parâmetros do ambiente.

        :param objRecebido:
            Objeto Pydantic contendo os seletores de origem e valores a serem mapeados.

        :param mapa:
            Dicionário com os nomes dos campos de origem (objeto) como chave e os nomes desejados como valor.

        :return:
            Dicionário com os nomes mapeados e respectivos valores do objeto original.
        """

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        dictObjeto = objRecebido.model_dump(exclude_none=True)
        dictFinal = {}

        for chaveObjeto, chaveFinal in mapa.items():
            if chaveObjeto in dictObjeto:
                valor = dictObjeto[chaveObjeto]
                if isinstance(chaveFinal, list):
                    for chave in chaveFinal:
                        dictFinal[chave] = valor
                else:
                    dictFinal[chaveFinal] = valor
            else:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Campo '{chaveObjeto}' não encontrado no objeto recebido. Ignorado no mapeamento.",
                    routine="mapearObjeto",
                    error_details=""
                )
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Mapeamento concluído com sucesso. Total de {len(dictFinal)} campos mapeados.",
            routine="mapearObjeto",
            error_details=""
        )

        return dictFinal
#END mapearObjeto(init, objRecebido, mapa)