import time
import random
from sqlalchemy import false, true
import webdriver_manager
from classes.rotinas.ConciliacaoBancaria import ConciliacaoBancaria
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components
from classes.rotinas.ExtratoContas import ExtratoContas
from classes.utils.GerarDados import GeradorDados  
from classes.utils.ApexUtil import Apex
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException
import pytest

@pytest.mark.dockerConciliacaoBancaria
def test_insere_regra_conciliacao(init):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']

    try:
        
        FuncoesUteis.goToPage(init,ConciliacaoBancaria.url)

        FuncoesUteis.showHideFilter(init, ConciliacaoBancaria.filterSelector)

        Components.btnClick(init, "#regrasConciliacao_tab")

        dictConfig = { #deixar None significa que será utilizado um valor aleatorio para cada campo na geração dos dicionarios
        #{ Campos que sempre serão preenchidos
        "descricaoRegra" : None, #string
        "status" : None, #Varia entre 1 = "Ativo" ; 0 = "Inativo"
        "tipoLancamento" : None, #Varia entre 1 = "Entrada" ; 2 = "Saida"
        "conta1" : None, #Se for usar, necessario o numero da conta especifica
        "tipoSelecao" : None, #Varia entre 1 = "Conter" ; 2 = "For igual a"
        "descricaoLancamento" : None, #string 
        "salvar" : 0, #0 = "Não Salvar" ; 1 = "Salvar"
        #}
        "tipoTratamento" : None, #1 = "Lançamento de Conta a Receber"(Se quiser utilizar, colocar tipoLancamento = 1); 2 = "Lançamento de Transferência"; 4 = "Lançamento de Conta a Pagar"(Se quiser utilizar, colocar tipoLancamento = 2); 5 = "Ignorar Lançamento"
        "conta2" : None, #(Apenas caso tipoTratamento for 2). Se for usar, necessario o numero da conta especifica
        "formaTransferencia" : None, #(Apenas caso tipoTratamento for 2). Varia entre 1 e 5
        "cliente" : None, #(Apenas caso tipoTratamento for 1 ou 4). Se for usar, necessario o numero do cliente especifico
        "categFinanceira" : None, #(Apenas caso tipoTratamento for 1 ou 4). Se for usar, necessario o numero da categoria especifica
        "utilizarDescricao" : None, #varia entre 1 = "Desmarcar Checkbox" ; 0 = "Deixar Marcada"
        "descricaoTratamento" : None #string
        }

        ConciliacaoBancaria.criarRegraConciliacao(init, dictConfig)


    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine=f"{ConciliacaoBancaria.rotina} - test_insere_regra_conciliacao", error_details=str(e))

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
            routine=f"{ConciliacaoBancaria.rotina} - test_insere_regra_conciliacao",
            error_details=''
        )

        Log_manager.insert_logs_for_execution()

        browser.quit()