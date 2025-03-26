
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.GerarDados import GeradorDados  
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components
from classes.rotinas.ExtratoContas import ExtratoContas



class ConciliacaoBancaria:
    url="conciliacao-bancaria"
    filterSelector = "#P154_FILTRO_CONTA"

    @staticmethod
    def insereConciliacao(init):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
           
        try:

            btnNovaConciliacao = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B43105716282300150")))
            btnText = btnNovaConciliacao.text
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"Botão {btnText} encontrado ",
                routine="ConciliacaoBancaria",
                error_details=''
            )
            btnNovaConciliacao.click()
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message=f"Botão {btnText} clicado ",
                routine="ConciliacaoBancaria",
                error_details=''
            )

            seletor = "[title='Importar Extrato']"
            has_frame = Components.has_frame(init,seletor)

            if has_frame:
                filePath = (r"C:\Users\Hos_Gabriel\Desktop\Automatização web\assets\teste0,50.ofx")
                WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".apex-item-filedrop-action.a-Button.a-Button--hot")))
                dropZone = WebDriverWait(browser,30).until(EC.presence_of_element_located((By.CSS_SELECTOR,"#P156_ARQUIVO_OFX")))
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message="input do arquivo Ofx encontrado",
                    routine="ExtratoDeContas",
                    error_details=''
                )
                dropZone.send_keys(filePath)
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message="Aquivo Ofx dropado no input do arquivo Ofx",
                    routine="ExtratoDeContas",
                    error_details=''
                )

                btnImportaExtrato = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#importarExtrato")))
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message="Botão btnImportaExtrato encontrado ",
                    routine="ConciliacaoBancaria",
                    error_details=''
                )
                btnImportaExtrato.click()
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message="Botão btnImportaExtrato clicado ",
                    routine="ConciliacaoBancaria",
                    error_details=''
                )

                try:

                    btnConfirm = WebDriverWait(browser,20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".js-confirmBtn")))
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="Botão btnConfirm encontrado ",
                        routine="ConciliacaoBancaria",
                        error_details=''
                    )

                    btnConfirm.click()
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="Botão btnConfirm clicado ",
                        routine="ConciliacaoBancaria",
                        error_details=''
                    )

                except (TimeoutException,Exception,NoSuchElementException) as e:
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="ERROR",
                        message="Erro: Tempo limite excedido ao acessar a página",
                        routine="ConciliacaoBancaria",
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
        finally:
                browser.switch_to.default_content()

#END insereConciliacao(init)

    @staticmethod
    def inluiRecebimentoContaExistente(init,filter):

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        try:

            btnInlcuirRecebimento = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[acao='novoLancamentoExistente']")))
            btnText = btnInlcuirRecebimento.text
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado",
                    routine="",
                    error_details=''
                )
            
            btnInlcuirRecebimento.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} clicado",
                    routine="",
                    error_details=''
                )
            
            seletor ="[title='Incluir Lançamento em Conta Existente']"
            has_frame = Components.has_frame(init,seletor)


            if has_frame:

                FuncoesUteis.aplyFilter(init,filter)

                checkBoxes = WebDriverWait(browser,30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,".selecaoConta.form-check-input")))

                checkBoxesLen = len(checkBoxes)
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="Info",
                    message=f"{checkBoxesLen} checkBoxes encontrados",
                    routine="ConciliacaoBancaria",
                    error_details=str(e)
                )

                randomCheckbox = GeradorDados.randomNumberDinamic(0,checkBoxesLen-1)

                checkBoxes[randomCheckbox].click()
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="Info",
                    message=f"{randomCheckbox} checkBox clicado",
                    routine="ConciliacaoBancaria",
                    error_details=str(e)
                )


                btnConciliar = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#conciliarButton")))
                btnText = btnConciliar.text
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} encontrado",
                        routine="",
                        error_details=''
                    )
                
                btnConciliar.click()
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} clicado",
                        routine="",
                        error_details=''
                    )
                FuncoesUteis.has_alert(init)

                WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[acao='desconciliarLancamento']")))
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão desconciliarLancamento encontrado",
                        routine="",
                        error_details=''
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

#END incluiRecebimentoContaExistente(init,filter)

    @staticmethod
    def criarNovaContaReceber(init,values):
        query =''
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
           
        try:

            btnNovaContaReceber = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[acao='novoLancamento']")))
            btnText = btnNovaContaReceber.text
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado",
                    routine="",
                    error_details=''
                )
            
            btnNovaContaReceber.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} clicado",
                    routine="",
                    error_details=''
                )
            
            ExtratoContas.contaReceberResumido(init,query,values)

            
        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))
#END criarNovaContaReceber(init,values)

    @staticmethod
    def criarNovaTransferencia(init,query):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
           
        try:       
            btnNovaContaReceber = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[acao='novoLancamentoTransferencia']")))
            btnText = btnNovaContaReceber.text
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado",
                    routine="",
                    error_details=''
                )
            
            btnNovaContaReceber.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} clicado",
                    routine="",
                    error_details=''
                )
            ExtratoContas.novaTransferencia(init,query,False)
            

            
        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
            screenshot_path = screenshots
            if screenshot_path:
                success = browser.save_screenshot(screenshot_path)
                if success:
                    Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="", application_type=env_application_type, error_details=str(e))
                else:
                    Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="", application_type=env_application_type, error_details=str(e))
#END criarNovaTransferencia(init)



    @staticmethod
    def associarRecebimentoExistente(init,filters,contaReceber):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        contaReceber = contaReceber if contaReceber else False
           
        try:       
            btnAssociarRecebimento = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"[acao='associarLancamento']")))
            btnText = btnAssociarRecebimento.text
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado",
                    routine="",
                    error_details=''
                )
            
            btnAssociarRecebimento.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} clicado",
                    routine="",
                    error_details=''
                )
            
            seletor = "[title='Associar a Lançamento Existente']"
            Components.has_frame(init,seletor)

            if isinstance(filters,dict):
                btnFilter = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#SR_filtros_tab")))
                btnText = btnFilter.text
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} encontrado",
                        routine="",
                        error_details=''
                    )
                
                btnFilter.click()
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} clicado",
                        routine="",
                        error_details=''
                    )
                FuncoesUteis.aplyFilter(init,filters)


                Components.has_spin(init)
                has_report = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#reportContasReceber")))
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="Report encontrado com com filtros aplicados",
                        routine="",
                        error_details=''
                    )


            else:
                has_report = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#reportContasReceber")))
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="Report encontrado sem filtros aplicados",
                        routine="",
                        error_details=''
                    )

            
            if has_report:
                seletorCheckbox = f"[value='{contaReceber}']" if contaReceber and isinstance(filters,dict) else ".selecaoConta.form-check-input"
                checkBox = WebDriverWait(browser,30).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,seletorCheckbox)))
                checkBox[0].click()
            else:
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="ERROR",
                        message="Report não encontrado",
                        routine="",
                        error_details=''
                    )
             

            btnConciliar = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#conciliarButton")))
            btnText = btnConciliar.text
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado",
                    routine="",
                    error_details=''
                )
            
            btnConciliar.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} clicado",
                    routine="",
                    error_details=''
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
        finally:
            browser.switch_to.default_content()
#END associarRecebimentoExistente(init,filters,contaReceber)
    
    
    @staticmethod
    def associarTransferenciaExistente(init,filters,contaReceber):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
           
        try: 
            seletor = "[acao='associarLancamentoTransferencia']"
            Components.btnClick(init,seletor)

            seletor = "[title='Associar a uma Transferência Existente']"
            Components.has_frame(init,seletor)

            if isinstance(filters,dict):
                seletor = "#SR_filtros_tab"
                Components.btnClick(init,seletor)
                FuncoesUteis.aplyFilter(init,filters)

                Components.has_spin(init)
                has_check = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,".selecaoConta.form-check-input")))
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="Resultados encontrado com filtros aplicados",
                        routine="",
                        error_details=''
                )

            else:
                has_check = WebDriverWait(browser,30).until(EC.visibility_of_element_located((By.CSS_SELECTOR,".selecaoConta.form-check-input")))
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="Resultados encontrado sem filtros aplicados",
                        routine="",
                        error_details=''
                )

            
            if has_check:
                seletorCheckbox = f"[value='{contaReceber}']" if contaReceber and isinstance(filters,dict) else ".selecaoConta.form-check-input"
                checkBox = WebDriverWait(browser,30).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,seletorCheckbox)))
                checkBox[0].click()
            else:
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="ERROR",
                        message="Report não encontrado",
                        routine="",
                        error_details=''
                    )
             

            btnConciliar = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#conciliarButton")))
            btnText = btnConciliar.text
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} encontrado",
                    routine="",
                    error_details=''
                )
            
            btnConciliar.click()
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Botão {btnText} clicado",
                    routine="",
                    error_details=''
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
        finally:
            browser.switch_to.default_content()          


    @staticmethod
    def processaConciliacaoAutomatica(init,yesNot):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
           
        try:       
            if yesNot:
                btnConciliarAutomatico = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".js-confirmBtn.ui-button.ui-corner-all.ui-widget.ui-button--hot")))
                btnText = btnConciliarAutomatico.text
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} encontrado",
                        routine="",
                        error_details=''
                    )
                
                btnConciliarAutomatico.click()
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} clicado",
                        routine="",
                        error_details=''
                    )
                
                Components.has_spin(init)

                btnConciliados = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#SR_R217176266746131119_tab")))
                btnText = btnConciliados.text
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} encontrado",
                        routine="",
                        error_details=''
                    )
                
                btnConciliados.click()
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} clicado",
                        routine="",
                        error_details=''
                    )
                
                btnConciliadosAutomaticamente = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#SR_R217176266746131119_tab")))
                btnText = btnConciliadosAutomaticamente.text
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} encontrado",
                        routine="",
                        error_details=''
                    )
                
                btnConciliadosAutomaticamente.click()
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} clicado",
                        routine="",
                        error_details=''
                    )
                
                has_notResults = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".a-Icon.icon-irr-no-results")))

                if has_notResults:
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="Não há conciliações automaticas disponiveis na aba de conciliações automaticas",
                        routine="",
                        error_details=''
                    )
                else:
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message="Há conciliações automaticas disponiveis na aba de conciliações automaticas",
                        routine="",
                        error_details=''
                    )
            else:
                btnNaoConciliarAutomatico = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".ui-button.ui-corner-all.ui-widget")))
                btnText = btnNaoConciliarAutomatico.text
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} encontrado",
                        routine="",
                        error_details=''
                    )
                
                btnNaoConciliarAutomatico.click()
                Log_manager.add_log(
                        application_type=env_application_type,
                        level="INFO",
                        message=f"Botão {btnText} clicado",
                        routine="",
                        error_details=''
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

#END processaConciliacaoAutomatica(init,yesNot) 

