from datetime import datetime,timedelta
import time
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
    filterSelector = "P154_FILTRO_CONTA"

    @staticmethod
    def insereConciliacao(init):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")
           
        try:
            
            btnNovaConciliacao = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#B43105716282300150")))
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Botão btnNovaConciliacao encontrado ",
                routine="ConciliacaoBancaria",
                error_details=''
            )
            btnNovaConciliacao.click()
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Botão btnNovaConciliacao clicado ",
                routine="ConciliacaoBancaria",
                error_details=''
            )

            seletor = "[title='Importar Extrato']"
            has_frame = Components.has_frame(init,seletor)

            if has_frame:
                filePath = (r"C:\Users\Hos_Gabriel\Desktop\Automatização web\config\teste.ofx")
                WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".apex-item-filedrop-action.a-Button a-Button--hot")))
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

                if not FuncoesUteis.has_alert(init) and FuncoesUteis.has_alert_sucess(init):
                    browser.switch_to.default_content()
                else:
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="Erro",
                        message="Alert encontrado",
                        routine="ExtratoDeContas",
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