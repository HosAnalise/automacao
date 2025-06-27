import time
import pytest
from classes.rotinas.Pessoas import Pessoas
from classes.utils.Components import Components
from classes.utils.FuncoesUteis import FuncoesUteis
from faker import Faker
fake = Faker(locale='pt_BR')

@pytest.mark.parametrize("endereco, devePassar", [
    (   # Endereco com CEP valido
        Pessoas.Endereco(
            P6_TIPO_ENDERECO_ID='1',
            P6_CEP='95700028',
            P6_NUMERO='123',
            P6_COMPLEMENTO='Apto 101',
            P6_CORRESPONDENCIA='0',
            P6_BOLETO_ENDERECO='1'            
        ), True
    )
    ,
    (   # Endereco com Cep invalido
        Pessoas.Endereco(
            P6_TIPO_ENDERECO_ID='1',
            P6_CEP=fake.postcode(),
            P6_NUMERO='123',
            P6_COMPLEMENTO='Apto 101',
            P6_CORRESPONDENCIA='0',
            P6_BOLETO_ENDERECO='0'            
        ), False
    )
    ,
    (
        # Endereco sem Cep 
        Pessoas.Endereco(
            P6_TIPO_ENDERECO_ID='1',
            P6_ESTADO_ID='23',
            P6_CIDADE_ID = '4688',
            P6_ENDERECO ='Rua testes',
            P6_NUMERO='123',
            P6_COMPLEMENTO='Apto 101',
            P6_CORRESPONDENCIA='1',
            P6_BOLETO_ENDERECO='0'            
        ), True
    ),
    (
        # Endereco com Cep invalido
        Pessoas.Endereco(
            P6_TIPO_ENDERECO_ID='1',
            P6_CEP='ABCDESFD',
            P6_NUMERO='123',
            P6_COMPLEMENTO='Apto 101',
            P6_CORRESPONDENCIA='0',
            P6_BOLETO_ENDERECO='0'            
        ), False
),
    
])
@pytest.mark.dockerPessoas
def test_insere_endereco(init, endereco, devePassar):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, selenium_exceptions, error_logger = init
    env_application_type = env_vars['APPLICATION_TYPE']

    try:
        FuncoesUteis.goToPage(init=init,url= Pessoas.url)

        FuncoesUteis.showHideFilter(init=init, seletor=Pessoas.filterSelector)

        Components.btnClick(init=init, seletor="#B88575101250151001")

        Components.has_frame(init=init,seletor="[title='Cadastro de Pessoa']")

        endereco = Pessoas.insereEndereco(init=init,enderecoPessoa=endereco)

       
        if endereco is not False:
            endereco = endereco.model_dump(exclude_none=True)

        if devePassar:
            if endereco is False:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="WARNING",
                    message="Teste devia retornar um objeto, porém retornou False.",
                    routine=f"{Pessoas.rotina} - test_insere_endereco",
                    error_details=""
                )
            assert endereco is not False

        else:
            if endereco is not False:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="WARNING",
                    message="Teste devia retornar False, porém retornou objeto.",
                    routine=f"{Pessoas.rotina} - test_insere_endereco",
                    error_details=""
                )
            assert endereco is False

    except selenium_exceptions as e:
        logs = error_logger(exc=e,block=f"{Pessoas.rotina} - test_insere_nova_pessoa")
        Log_manager.add_log(
                            application_type=env_application_type, 
                            level="ERROR", 
                            message=f"{logs.time} - {logs.message}", 
                            routine=f"{Pessoas.rotina} - test_insere_nova_pessoa - {logs.function_error}- {logs.file} - {str(logs.row)}", 
                            error_details=f"{logs.error} - {logs.type_error} "
                            )
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
            routine=f"{Pessoas.rotina} - test_insere_endereco",
            error_details=''
        )

        Log_manager.insert_logs_for_execution(logName=Pessoas.rotina)

        try:
            browser.quit()
        except Exception as e:
            Log_manager.add_log(
                application_type=env_application_type,
                level="WARNING",
                message=f"Falha ao fechar o navegador: {e}",
                routine=f"{Pessoas.rotina} - test_insere_endereco",
                error_details=str(e)
            )