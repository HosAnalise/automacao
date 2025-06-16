from tabnanny import check
import time
import pytest
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.Components import Components
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.rotinas.ContasReceber import ContaReceber
from classes.rotinas.Pessoas import Pessoas

@pytest.mark.parametrize("novaPessoa, devePassar", [
    (
        Pessoas.Pessoa( #documento não utilizar, caso passar CNPJ, deve ser valido para teste funcionar, dependentes as vezes o campo de nome não aparece.
            tipoPessoa='2', P6_ISENTA_IE= 'N',
            endereco=Pessoas.Endereco(P6_BAIRRO="bairrozao"),
            contato=Pessoas.Contato(P6_NOME_CONTATO="o tal do contato")
        ),
        True
    )
])
@pytest.mark.dockerCheques
def test_contaReceber_novoCliente(init, novaPessoa, devePassar):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, screenshots, oracle_db_connection = init
    env_application_type = env_vars['WEB']

    try:
        FuncoesUteis.goToPage(init, ContaReceber.url)

        FuncoesUteis.showHideFilter(init, ContaReceber.filterSelector)

        Components.btnClick(init, "#B392477272658547904") #nova conta

        funcionou = True if ContaReceber.criaNovoCliente(init, novaPessoa) else False

        if devePassar:
            if funcionou is False:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="WARNING",
                    message="Teste devia retornar um objeto, porém retornou False.",
                    routine=f"{ContaReceber.rotina} - test_contaReceber_novoCliente",
                    error_details=""
                )
            assert funcionou is not False

        else:
            if funcionou:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="WARNING",
                    message="Teste devia retornar False, porém retornou objeto.",
                    routine=f"{ContaReceber.rotina} - test_contaReceber_novoCliente",
                    error_details=""
                )
            assert funcionou is False

    except (TimeoutException, NoSuchElementException, Exception) as e:
        Log_manager.add_log(application_type=env_application_type, level="ERROR", message=str(e), routine=f"{ContaReceber.rotina} - test_contaReceber_novoCliente", error_details=str(e))
        
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
            routine=f"{ContaReceber.rotina} - test_contaReceber_novoCliente",
            error_details=''
        )

        Log_manager.insert_logs_for_execution()

        browser.quit()