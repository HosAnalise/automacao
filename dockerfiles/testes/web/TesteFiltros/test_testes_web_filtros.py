import json
import pytest
from datetime import datetime 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_filtros(init):

    def apexSetvalue(browser,page,element,value):
        browser.execute_script(f"apex.item('P{page}_{element}').setValue('{value}')")  
        
    def apexGetValue(browser,page,element):
         return browser.execute_script(f"return apex.item('P{page}_{element}').getValue()")       



    browser,login,log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots = init
    
    execution_id = log_manager._generate_execution_id()

    getEnv = env_vars   

    url_erp = getEnv.get('URL_ERP')

    if not url_erp:
        pytest.fail("Erro crítico: 'URL_ERP' não encontrada no ambiente de variáveis.")

        
    env_application_type = getEnv.get('WEB')

    page_str = getEnv.get('FILTERED_PAGE')

    page = json.loads(page_str) 

    today = datetime.today()

    first_day = today.replace(day=1)

    today_str = today.strftime("%d/%m/%Y")
    first_day_str = first_day.strftime("%d/%m/%Y")


    try:

        for pageKey, pageValue in page.items():

            
                browser.get(f"{url_erp}{pageValue}")

            
                try:
                    waitBtn = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".a-Button.a-IRR-button.a-IRR-button--actions.js-menuButton")))
                except:
                    continue

                if pageKey != "154":
                    script ="$('button#t_Button_rightControlButton > span').click()"
                    browser.execute_script(script)
                    log_manager.add_log(application_type =env_application_type,level= "INFO", message =f"Botão filtro selecionado tela {pageValue}", routine="testeFiltro", error_details ='' )

                apexSetvalue(browser,pageKey,"DATA_INICIAL", first_day_str)
                dataInicialValueStart = apexGetValue(browser,pageKey,"DATA_INICIAL")

                if dataInicialValueStart:
                    log_manager.add_log(application_type =env_application_type,level= "DEBUG", message =f"Data inicial preenchida: {dataInicialValueStart}", routine="testeFiltro", error_details ='' )

            
                apexSetvalue(browser,pageKey,"DATA_FINAL", today_str)
                dataFinalValueStart = apexGetValue(browser,pageKey,"DATA_FINAL")


                if dataFinalValueStart:
                    log_manager.add_log(application_type =env_application_type,level= "DEBUG", message =f"Data final preenchida: {dataFinalValueStart}", routine="testeFiltro", error_details ='' )            


                filter = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".t-Button.t-Button--hot.t-Button--simple.t-Button--stretch")))
                browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", filter)
                filter.click()
                log_manager.add_log(application_type =env_application_type,level= "INFO", message =f"Botão filtrar clickado tela {pageValue}", routine="testeFiltro", error_details ='' )            


                editContaPagar = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.fa.fa-edit')))
                log_manager.add_log(application_type =env_application_type,level= "INFO", message =f"Botão editar encontrado{pageValue}", routine="testeFiltro", error_details ='' )            

                
                rows = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))

                if rows:

                    dataArr = []

                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME,"td")
                        data = [cell.text for cell in cells if cell.text.strip() != '']
                        if data:
                            dataArr.append(data)

                    

                    
                if dataArr:
                    log_manager.add_log(application_type =env_application_type,level= "DEBUG", message =f"Dados da tabela da page {pageValue} coletados {dataArr}", routine="testeFiltro", error_details ='' )            
            
            
                editContaPagar.click()
                log_manager.add_log(application_type =env_application_type,level= "INFO", message =f"Botão editContaPagar clickado tela {pageValue}", routine="testeFiltro", error_details ='' )            



                breadCrumb = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".t-Breadcrumb-label")))
                returnContaPagar = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[name='voltar']")))

                if breadCrumb and returnContaPagar:
                    browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", returnContaPagar)
                    returnContaPagarClick = True
                    returnContaPagar.click()
                    log_manager.add_log(application_type =env_application_type,level= "INFO", message =f"Botão Voltar clickado tela {pageValue}", routine="testeFiltro", error_details ='' )            
                else:
                    breadCrumb.click()
                    log_manager.add_log(application_type =env_application_type,level= "INFO", message =f"BreadCrumb clickada tela {pageValue}", routine="testeFiltro", error_details ='' )            
                    


                editContaPagar = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.fa.fa-edit')))
                log_manager.add_log(application_type =env_application_type,level= "INFO", message =f"Botão editContaPagar encontrado{pageValue}", routine="testeFiltro", error_details ='' )            

            
                rows = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))

                if rows:

                    dataArr2 = []

                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME,"td")
                        data = [cell.text for cell in cells if cell.text.strip() != '']
                        if data:
                            dataArr2.append(data)

                if dataArr2:            
                    log_manager.add_log(application_type =env_application_type,level= "DEBUG", message =f"Dados da tabela da page {pageValue} coletados {dataArr2}", routine="testeFiltro", error_details ='' )
                
                dataInicialValueReturn = apexGetValue(browser,pageKey,"DATA_INICIAL")
                dataFinalValueReturn = apexGetValue(browser,pageKey,"DATA_FINAL")

                if dataArr ==  dataArr2 or (dataInicialValueStart == dataInicialValueReturn and dataFinalValueStart == dataFinalValueReturn):
                    log_manager.add_log(application_type =env_application_type,level= "INFO", message =f"Filtros estavam ativos no retorno da pagina usando o botão voltar para page {pageValue}", routine="testeFiltro", error_details ='' )
                else:
                    log_manager.add_log(application_type =env_application_type,level= "ERROR", message =f"Filtros não estavam ativos no retorno da pagina {pageValue}", routine="testeFiltro", error_details ='' )


                if returnContaPagarClick:
                    editContaPagar = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.fa.fa-edit')))
                    editContaPagar.click()
                    log_manager.add_log(application_type =env_application_type,level= "INFO", message =f"Botão editar clickado{pageValue}", routine="testeFiltro", error_details ='' )            

                    breadCrumb = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".t-Breadcrumb-label")))
                    breadCrumb.click()
                    log_manager.add_log(application_type =env_application_type,level= "INFO", message =f"BreadCrumb clickada{pageValue}", routine="testeFiltro", error_details ='' )            
                   

                    editContaPagar = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.fa.fa-edit')))
                    log_manager.add_log(application_type =env_application_type,level= "INFO", message =f"Botão editar encontrado{pageValue}", routine="testeFiltro", error_details ='' )            

                    rows = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))

                    if rows:

                        dataArr3 = []

                        for row in rows:
                            cells = row.find_elements(By.TAG_NAME,"td")
                            data = [cell.text for cell in cells if cell.text.strip() != '']
                            if data:
                                dataArr3.append(data)
                    if dataArr3:            
                        log_manager.add_log(application_type =env_application_type,level= "DEBUG", message =f"Dados da tabela da page {pageValue} coletados {dataArr3}", routine="testeFiltro", error_details ='' )    

                    dataInicialValueBreadCrumb = apexGetValue(browser,pageKey,"DATA_INICIAL")
                    dataFinalValueBreadCrumb = apexGetValue(browser,pageKey,"DATA_FINAL")

                    if dataArr ==  dataArr3 or (dataInicialValueStart == dataInicialValueBreadCrumb and dataFinalValueStart == dataFinalValueBreadCrumb):
                        log_manager.add_log(application_type =env_application_type,level= "INFO", message =f"Filtros estavam ativos no retorno da pagina {pageValue} usando a breadCrumb", routine="testeFiltro", error_details ='' )
                    else:
                        log_manager.add_log(application_type =env_application_type,level= "ERROR", message =f"Filtros não estavam ativos no retorno da pagina {pageValue}", routine="testeFiltro", error_details ='' )

    
    except (TimeoutException, NoSuchElementException, Exception) as  e:   
        log_manager.add_log(application_type =env_application_type,level= "ERROR", message = f"Erro ao acessar página de {pageValue}", routine="testeFiltro", error_details =str(e) )




    finally:
        log_manager.insert_logs_for_execution(execution_id)
    



      
