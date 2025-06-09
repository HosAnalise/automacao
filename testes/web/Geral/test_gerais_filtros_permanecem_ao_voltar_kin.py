import time
from classes.rotinas.ExtratoContas import ExtratoContas
from classes.rotinas.ContasPagar import ContasPagar
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



def test_geral_filtrosPermanecemAoVoltar(init):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']

    for i in range(2):

        if i == 0:
            rotina = "Contas a Pagar"
            page = ContasPagar.url
            voltar = '#B103339792839912425' 
            filters = {
                "P46_SELETOR_LOJA": "2381",
                    "P46_TIPO_PERIODO": "REGISTRO",
                    "P46_DATA_INICIAL": "25/03/2025",
                    "P46_DATA_FINAL": "25/03/2025",
                    "P46_SITUACAO" : "atrasada,pagoParcialmente",
                    "P46_NUMERO_DOCUMENTO": "776248",
                    "P46_NUMERO_PEDIDO": "546879",
                    "P46_NUMERO_TITULO": "1346987",
                    "P46_CONTA": "6030",
                    "P46_CENTRO_CUSTO": "2856",
                    "P46_CATEGORIA": "33105",
                    "P46_FORNECEDOR": "1685318",
                    "P46_TIPO_ORIGEM": "1",
                    "P46_CODIGO_BARRAS": "0",
                    "P46_CONFERIDO": "0",
                    "P46_VALOR_INICIAL": "569,44",
                    "P46_VALOR_FINAL": "569,44",
                    "P46_EFETUADO_EM": "1"
                }


        elif i == 1:
            rotina = "Contas a Receber"
            page = ContaReceber.url
            voltar = '#B118649869079784509'
            valorCobrador = "3187232"
            filters = {
                "P84_SELETOR_LOJA": "2381",
                    "P84_TIPO_PERIODO": "REGISTRO",
                    "P84_DATA_INICIAL": "26/03/2025",
                    "P84_DATA_FINAL": "26/03/2025",
                    "P84_SITUACAO" : "recebidoparcial",
                    "P84_NUMERO_DOCUMENTO": "655987",
                    "P84_NUMERO_PEDIDO": "264875",
                    "P84_CONTA": "5290",
                    "P84_CENTRO_CUSTO": "3228",
                    "P84_CATEGORIA": "33087",
                    "P84_CLIENTE": "3784774",
                    "P84_VALOR_INICIAL": "269,58",
                    "P84_VALOR_FINAL": "269,58",
                    "P84_ORIGEM": "1",
                    #"P84_VENDA_ORIGEM": "1", não funcionando, erro 'is not defined'
                    "P84_CONVENIO": "-1",
                    "P84_NR_CONTA": "",
                    "P84_RECEBIDO_EM": "3",
                    "P84_TIPO_COBRANCA": "2",
                    "P84_COBRADOR": valorCobrador,
                    "P84_CONTEM_BOLETO": "0"
                }


        # else:
        #     rotina = "Extrato de Contas"
        #     page = ExtratoContas.url
        #     voltar = '#B116404984751394426'
        #     filters = {
        #         "P76_CONTAS",
        #         "P76_DATA_INICIAL",
        #         "P76_DATA_FINAL",
        #         "P76_SITUACAO",
        #         "P76_VALOR_MIN",
        #         "P76_VALOR_MAX",
        #         "P76_NUMERO_DOCUMENTO",
        #         "P76_CATEGORIAS",
        #         "P76_CENTRO_CUSTO",
        #         "P76_ORIGEM"
        #     }


        try:
            btnSalvar = ".t-Button.t-Button--hot.t-Button--simple.t-Button--stretch"

            FuncoesUteis.goToPage(init, page)
            seletor = ContasPagar.filterSelector if i == 0 else ContaReceber.filterSelector

            FuncoesUteis.guaranteeShowHideFilter(init, seletor, 1)
            FuncoesUteis.setFilters(init, filters)
            if i == 1:
                time.sleep(1)
                Apex.setValue(browser, "P84_COBRADOR", valorCobrador)
            Components.btnClick(init, btnSalvar)

            filtersPosApply = {}
            for key,value in filters.items():
                filtersPosApply[key] = Apex.getValue(browser,key)

            print(filtersPosApply)

            filtersBefAfter = {seletor: (filters[seletor], value) for seletor, value in filtersPosApply.items()}

            FuncoesUteis.compareValues(init, filtersBefAfter)


            if i == 0:
                ContasPagar.editaContaPagar(init)
            else:
                ContaReceber.editaContaReceber(init)

            click = WebDriverWait(browser,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,voltar)))
            browser.execute_script("arguments[0].scrollIntoView(true);", click)
            Components.btnClick(init,voltar)

            time.sleep(2)
            browser.execute_script("confirm()")
            print("confirm Clicado")

            try:
                alert = browser.switch_to.alert
                print(f"Alert encontrado: {alert.text}")
                alert.accept()  # Ou alert.dismiss() se preferir cancelar o alert
                print("Alert tratado com sucesso.")
                Log_manager.add_log(
                    level="INFO",
                    message=f"Foi Tratado o Alert {alert.text}",
                    routine=rotina,
                    error_details=""
                )
            except NoAlertPresentException:
                print("Nenhum alert presente.")

            filtersVolta = {}
            FuncoesUteis.guaranteeShowHideFilter(init, seletor, 1)

            for key, value in filters.items():
                try:
                    print(f"Processando chave: {key}")
                    filtersVolta[key] = Apex.getValue(browser, key)
                    print(f"Valor obtido para {key}: {filtersVolta[key]}")
                except Exception as e:
                    print(f"Erro ao processar chave {key}: {e}")
                    Log_manager.add_log(
                        application_type=env_application_type,
                        level="ERROR",
                        message=f"Erro ao obter valor para {key}: {e}",
                        routine="ContaPagar",
                        error_details=str(e)
                    )


            filtersBefAfter = {seletor: (filtersPosApply[seletor], value) for seletor, value in filtersVolta.items()}

            FuncoesUteis.compareValues(init, filtersBefAfter)


        except (TimeoutException, NoSuchElementException, Exception) as e:
            Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine="Testes Gerais - test_geral_filtrosPermanecemAoVoltar", error_details=str(e))
            
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
                routine="Testes Gerais - test_geral_filtrosPermanecemAoVoltar",
                error_details=''
            )

    Log_manager.insert_logs_for_execution()

    browser.quit()