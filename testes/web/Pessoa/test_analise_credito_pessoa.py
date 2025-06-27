import time
import pytest
from classes.rotinas.Pessoas import Pessoas
from classes.utils.Components import Components
from classes.utils.FuncoesUteis import FuncoesUteis
from faker import Faker
fake = Faker(locale='pt_BR')

@pytest.mark.parametrize("infoPessoa, devePassar, fisicaJuridica", [
    (
        Pessoas.Pessoa(
            P6_CPF=12345678901,
            P6_RG=123456789,
            P6_E_PACIENTE='0',
            P6_GENERO='F',
            P6_APELIDO='teste',
            P6_DATA_NASCIMENTO='01/01/2000',
            P6_ENVIAR_PARA_REGISTRO='0',
            P6_STATUS='1'
        ), True,True
    )
    ,
    (
        Pessoas.Pessoa(
            P6_CPF='abcdefghisjk',
            P6_RG='abcdefghisjk',
            P6_E_PACIENTE='0',
            P6_GENERO='O',
            P6_APELIDO=fake.text(max_nb_chars=1000),
            P6_DATA_NASCIMENTO='23/06/2025',
            P6_ENVIAR_PARA_REGISTRO='0',
            P6_STATUS='0'
        ), False,True
    )
    ,
    (
        Pessoas.Pessoa(
            P6_CPF='abcdefghisjk',
            P6_RG='abcdefghisjk',
            P6_E_PACIENTE='0',
            P6_GENERO='O',
            P6_APELIDO='teste',
            P6_DATA_NASCIMENTO='31/06/2026',
            P6_ENVIAR_PARA_REGISTRO='1',
            P6_STATUS='0'
        ), False,True
    ),
    (
        Pessoas.Pessoa(
            P6_CNPJ=fake.cnpj(),
            P6_RAZAO_SOCIAL=fake.company(),
            P6_FANTASIA=fake.company_suffix(),
            P6_APELIDO='teste',
            P6_ENVIAR_PARA_REGISTRO='0',
            P6_IE=fake.random_number(),
            P6_STATUS='1',
            P6_ISENTA_IE='0',
            P6_UF_INSCRICAO_ESTADUAL=fake.estado_sigla()
        ), True,False
),
(
        Pessoas.Pessoa(
            P6_CNPJ=fake.name_nonbinary(),
            P6_RAZAO_SOCIAL=fake.text(max_nb_chars=1000),
            P6_FANTASIA=fake.text(max_nb_chars=1000),
            P6_APELIDO=fake.text(max_nb_chars=1000),
            P6_ENVIAR_PARA_REGISTRO='0',
            P6_IE=fake.random_number(digits=100),
            P6_STATUS='1',
            P6_ISENTA_IE='0',
            P6_UF_INSCRICAO_ESTADUAL='xx'
            
        ), False,False
),

    
])
@pytest.mark.dockerPessoas
def test_insere_nova_pessoa(init, infoPessoa, devePassar,fisicaJuridica):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, selenium_exceptions, error_logger = init
    env_application_type = env_vars['APPLICATION_TYPE']

    try:
        FuncoesUteis.goToPage(init=init,url= Pessoas.url)

        FuncoesUteis.showHideFilter(init=init, seletor=Pessoas.filterSelector)

        Components.btnClick(init=init, seletor="#B88575101250151001")

        Components.has_frame(init=init,seletor="[title='Cadastro de Pessoa']")

        Pessoas.novaAnaliseCredito(init=init)

        if pessoa is not False:
            pessoa = pessoa.model_dump(exclude_none=True)

        

       



        if devePassar:
            if Pessoas.analisePropria(init=init,obj=pessoa) is False:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="WARNING",
                    message="Teste devia retornar um objeto, porém retornou False.",
                    routine=f"{Pessoas.rotina} - test_insere_nova_pessoa",
                    error_details=""
                )
            assert pessoa is not False

        else:
            if Pessoas.analisePropria(init=init,obj=pessoa) is not False:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="WARNING",
                    message="Teste devia retornar False, porém retornou objeto.",
                    routine=f"{Pessoas.rotina} - test_insere_nova_pessoa",
                    error_details=""
                )
            assert pessoa is False

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
            routine=f"{Pessoas.rotina} - test_insere_nova_pessoa",
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
                routine=f"{Pessoas.rotina} - test_insere_nova_pessoa",
                error_details=str(e)
            )