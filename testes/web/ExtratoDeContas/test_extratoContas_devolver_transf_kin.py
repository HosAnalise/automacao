import time
import random
import webdriver_manager
from classes.rotinas.ExtratoContas import ExtratoContas
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.GerarDados import GeradorDados  
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components
from classes.rotinas.ContasReceber import ContaReceber
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException


def test_DevolverTransferencia(init):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']

    try:
        FuncoesUteis.goToPage(init, "configurações-gerais")

        conta = Apex.getValue(browser, "P107_CONTA_RECEBIMENTO_PIX_VENDA")


        FuncoesUteis.goToPage(init, "exibir-extrato-das-contas")

        #fazendo a transferencia
        contaOrigem = "5290"
        data = GeradorDados.simpleRandDate(init)
        valorTransf = f"{random.uniform(10, 230):.2f}".replace(".", ",")
        numDoc = GeradorDados.simpleRandString(init, 5, 8)
        desc = GeradorDados.simpleRandString(init, 7, 15)

        contaTransf = {
            "P78_CONTA_ORIGEM_ID" : contaOrigem,
            "P78_CONTA_DESTINO_ID" : conta,
            "P78_DATA_TRANSFERENCIA" : data,
            "P78_VALOR_TRANSFERENCIA" : valorTransf,
            "P78_NUMERO_DOCUMENTO" : numDoc,
            "P78_DESCRICAO" : desc
        }
        for chave, valor in contaTransf.items():
            print(f"{chave}: {valor}")


        contaTransfPre = { #usado para comparar com a transferencia devolvida
            "P78_CONTA_ORIGEM_ID" : conta,
            "P78_CONTA_DESTINO_ID" : contaOrigem, #trocado para fazer a comparação com a transferencia devolvida
            "P78_DATA_TRANSFERENCIA" : data,
            "P78_VALOR_TRANSFERENCIA" : valorTransf,
            "P78_NUMERO_DOCUMENTO" : numDoc,
            "P78_DESCRICAO" : f"DEVOLVIDO - {desc}"
        }

        filtros = {
            "P76_CONTAS" : conta,
            "P76_DATA_INICIAL" : data,
            "P76_DATA_FINAL" : data, #garante que o periodo é apenas um dia
            #"P76_VALOR_MIN" : valorTransf, #retirados pois não está achando a transferencia quando usando o valor
            #"P76_VALOR_MAX" : valorTransf, #posso depender do numDoc para filtrar, a chance de repetir a string é de 0,000000000000018%
            "P76_NUMERO_DOCUMENTO" : numDoc
        }

        time.sleep(1)
        FuncoesUteis.guaranteeShowHideFilter(init, ExtratoContas.filterSelector, 0) #depois, substituir por ExtratoContas.filterSelector

        Components.btnClick(init, "#novaTransferencia")
        WebDriverWait(browser, 30).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "[title='Cadastro de Transferência']")))

        FuncoesUteis.setFilters(init, contaTransf)
        Components.btnClick(init, "#B5886099528185118")

        browser.switch_to.default_content()

        FuncoesUteis.guaranteeShowHideFilter(init, ExtratoContas.filterSelector, 1)
        FuncoesUteis.setFilters(init, filtros)
        Components.btnClick(init, "#filtrar")

        ExtratoContas.editaExtratoConta(init)
        WebDriverWait(browser, 30).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "[title='Cadastro de Transferência']")))


        Components.btnClick(init, "#btnDevolver")
        time.sleep(1)
        browser.switch_to.default_content()

        browser.execute_script("$('.js-confirmBtn.ui-button.ui-corner-all.ui-widget.ui-button--hot').click()")
        
        FuncoesUteis.guaranteeShowHideFilter(init, ExtratoContas.filterSelector, 1)

        FuncoesUteis.setFilters(init, filtros)
        Apex.setValue(browser, "P76_ORIGEM", "4")
        Components.btnClick(init, "#filtrar")

        ExtratoContas.editaExtratoConta(init)
        WebDriverWait(browser, 30).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "[title='Cadastro de Transferência']")))

        contaTransfDevolvida = {}
        for key, value in contaTransfPre.items():
            contaTransfDevolvida[key] = Apex.getValue(browser, key)

        camposBefAfter = {seletor: (contaTransfPre[seletor], value) for seletor, value in contaTransfDevolvida.items()}

        FuncoesUteis.compareValues(init, camposBefAfter) #verifica se as contas estão invertidas e a data, valor e num de doc estão iguais

        if contaTransfDevolvida["P78_DESCRICAO"] != f"DEVOLVIDO - {contaTransf['P78_DESCRICAO']}": #verifica se o campo descrição está igual, porem com 'DEVOLVIDO - ' antes
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Descrição Incorreta, Valor Obtido = {contaTransfDevolvida['P78_DESCRICAO']}, Valor Original = {contaTransf['P78_DESCRICAO']}",
                    routine="",
                    error_details=""
                )

        else:
            Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Descrição Correta, Valor Obtido = {contaTransfDevolvida['P78_DESCRICAO']}, Valor Original = {contaTransf['P78_DESCRICAO']}",
                    routine="",
                    error_details=""
                )

    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="", error_details=str(e))
        screenshot_path = screenshots
        if screenshot_path:
            success = browser.save_screenshot(screenshot_path)
            if success:
                Log_manager.add_log(level="INFO", message=f"Screenshot salvo em: {screenshot_path}", routine="ExtratoDeContas", application_type=env_application_type, error_details=str(e))
            else:
                Log_manager.add_log(level="ERROR", message="Falha ao salvar screenshot", routine="ExtratoDeContas", application_type=env_application_type, error_details=str(e))

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
            routine="ExtratoDeContas",
            error_details=''
        )

        Log_manager.insert_logs_for_execution()

        browser.quit()
