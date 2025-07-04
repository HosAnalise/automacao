import time
import pytest
from classes.rotinas.CadastroPessoas import Pessoas
from classes.utils.Components import Components
from classes.utils.FuncoesUteis import FuncoesUteis
from faker import Faker
fake = Faker(locale='pt_BR')

# --- Payloads para Testes de Segurança ---
XSS_PAYLOAD_BASIC = "<script>alert('XSS')</script>"
XSS_PAYLOAD_IMG = "<img src=x onerror=alert('XSS')>"
SQL_INJECTION_PAYLOAD_SIMPLE = "' OR '1'='1"
# SQL_INJECTION_PAYLOAD_DROP = "'; DROP TABLE Pessoas; --"

@pytest.mark.parametrize("infoPessoa, devePassar, fisicaJuridica, cenario", [
    # ==== CENÁRIOS EXISTENTES ====
    (
        Pessoas.Pessoa(
            P6_NOME=fake.name(),
            P6_CPF="04227167078",
            P6_RG=fake.rg().replace('.', '').replace('-', ''),
            P6_E_PACIENTE='0',
            P6_GENERO='F',
            P6_APELIDO='Pessoa Física Válida',
            P6_DATA_NASCIMENTO='01/01/2000',
            P6_ENVIAR_PARA_REGISTRO='0',
            P6_STATUS='1'
        ), True, True, "Pessoa Física - Criação com sucesso"
    ),
    (
        Pessoas.Pessoa(
            P6_NOME=fake.name(),
            P6_CPF=fake.cpf().replace('.', '').replace('-', ''),
            P6_RG=fake.rg().replace('.', '').replace('-', ''),
            P6_E_PACIENTE='0',
            P6_GENERO='F',
            P6_APELIDO='Pessoa Física Válida',
            P6_DATA_NASCIMENTO='01/01/2000',
            P6_ENVIAR_PARA_REGISTRO='0',
            P6_STATUS='1'
        ), True, True, "Pessoa Física Paciente - Criação com sucesso"
    ),
    (
        Pessoas.Pessoa(
            P6_NOME=fake.text(max_nb_chars=1000),
            P6_CPF=fake.cpf().replace('.', '').replace('-', ''),
            P6_RG=fake.rg().replace('.', '').replace('-', ''),
            P6_E_PACIENTE='0',
            P6_GENERO='F',
            P6_APELIDO='Pessoa Física Válida',
            P6_DATA_NASCIMENTO='01/01/2000',
            P6_ENVIAR_PARA_REGISTRO='0',
            P6_STATUS='1'
        ), False, True, "Pessoa Física - Nome tamanho inválido"
    ),
    (
        Pessoas.Pessoa(
            P6_NOME=fake.name(),
            P6_CPF='abcdefghisjk',
            P6_RG='abcdefghisjk',
            P6_E_PACIENTE='0',
            P6_GENERO='O',
            P6_APELIDO=fake.text(max_nb_chars=1000),
            P6_DATA_NASCIMENTO='23/06/2025',
            P6_ENVIAR_PARA_REGISTRO='0',
            P6_STATUS='0'
        ), False, True, "Pessoa Física - Dados inválidos (letras em CPF/RG, texto longo)"
    ),
    (
        Pessoas.Pessoa(
            P6_NOME=fake.name(),
            P6_CPF=fake.cpf().replace('.', '').replace('-', ''),
            P6_RG=fake.rg().replace('.', '').replace('-', ''),
            P6_E_PACIENTE='0',
            P6_GENERO='M',
            P6_APELIDO='Apelido Teste',
            P6_DATA_NASCIMENTO='31/02/2026', # Data inválida
            P6_ENVIAR_PARA_REGISTRO='1',
            P6_STATUS='0'
        ), False, True, "Pessoa Física - Data de nascimento inválida"
    ),
    (
        Pessoas.Pessoa(
            P6_CPF=fake.cpf().replace('.', '').replace('-', ''),
            P6_RG=fake.rg().replace('.', '').replace('-', ''),
            P6_E_PACIENTE='0',
            P6_GENERO='M',
            P6_APELIDO='Apelido Teste',
            P6_DATA_NASCIMENTO='31/02/2000', # Data inválida
            P6_ENVIAR_PARA_REGISTRO='1',
            P6_STATUS='0'
        ), False, True, "Pessoa Física - Sem nome"
    ),
    (
        Pessoas.Pessoa(
            P6_FISICA_JURIDICA='2',  # Pessoa Jurídica
            P6_CNPJ=fake.cnpj().replace('.', '').replace('/', '').replace('-', ''),
            P6_RAZAO_SOCIAL=fake.company(),
            P6_FANTASIA=fake.company_suffix(),
            P6_APELIDO='Pessoa Jurídica Válida',
            P6_ENVIAR_PARA_REGISTRO='0',
            P6_IE=str(fake.random_number(digits=9)),
            P6_STATUS='1',
            P6_ISENTA_IE='0',
            P6_UF_INSCRICAO_ESTADUAL=fake.estado_sigla()
        ), True, False, "Pessoa Jurídica - Criação com sucesso"
    ),
    (
        Pessoas.Pessoa(
            P6_FISICA_JURIDICA="2",  # Pessoa Jurídica
            P6_CNPJ='abcdefghijklmn',
            P6_RAZAO_SOCIAL=fake.text(max_nb_chars=1000),
            P6_FANTASIA=fake.text(max_nb_chars=1000),
            P6_APELIDO=fake.text(max_nb_chars=1000),
            P6_ENVIAR_PARA_REGISTRO='0',
            P6_IE='letrasnaIE',
            P6_STATUS='1',
            P6_ISENTA_IE='0',
            P6_UF_INSCRICAO_ESTADUAL='XX'
        ), False, False, "Pessoa Jurídica - Dados inválidos (letras, UF inválida)"
    ),

    # ==== NOVOS CENÁRIOS DE SEGURANÇA ====
    (
        Pessoas.Pessoa(
            P6_CPF=fake.cpf().replace('.', '').replace('-', ''),
            P6_RG=fake.rg().replace('.', '').replace('-', ''),
            P6_APELIDO=XSS_PAYLOAD_BASIC, # Tentativa de XSS
            P6_DATA_NASCIMENTO='01/01/2000'
        ), False, True, "Pessoa Física - Tentativa de XSS no apelido"
    ),
    # (
    #     Pessoas.Pessoa(
    #         P6_CNPJ=fake.cnpj().replace('.', '').replace('/', '').replace('-', ''),
    #         P6_RAZAO_SOCIAL=SQL_INJECTION_PAYLOAD_SIMPLE, # Tentativa de SQL Injection
    #         P6_FANTASIA=SQL_INJECTION_PAYLOAD_DROP # Tentativa de SQL Injection destrutiva
    #     ), False, False, "Pessoa Jurídica - Tentativa de SQL Injection"
    # ),

    # ==== NOVOS CENÁRIOS DE VALIDAÇÃO E CASOS EXTREMOS ====
    (
        Pessoas.Pessoa(
            P6_CPF='', # CPF Vazio
            P6_APELIDO='CPF Obrigatório',
            P6_DATA_NASCIMENTO='01/01/2000'
        ), False, True, "Pessoa Física - Campo obrigatório (CPF) vazio"
    ),
    (
        Pessoas.Pessoa(
            P6_CNPJ='', # CNPJ Vazio
            P6_RAZAO_SOCIAL='Razão Social Obrigatória'
        ), False, False, "Pessoa Jurídica - Campo obrigatório (CNPJ) vazio"
    ),
    (
        Pessoas.Pessoa(
            P6_CPF=fake.cpf().replace('.', '').replace('-', ''),
            P6_APELIDO='   Apelido com espaços   ', # Espaços no início e fim
            P6_DATA_NASCIMENTO='01/01/2000'
        ), True, True, "Pessoa Física - Input com espaços extras (deve ser tratado pelo sistema)"
    ),
    (
        Pessoas.Pessoa(
            P6_CPF=fake.cpf().replace('.', '').replace('-', ''),
            P6_APELIDO='José da Silva (José) 😊', # Caracteres Unicode e emoji
            P6_DATA_NASCIMENTO='01/01/2000'
        ), True, True, "Pessoa Física - Suporte a caracteres Unicode"
    ),
])
@pytest.mark.dockerCadastroPessoas
def test_insere_nova_pessoa(init, infoPessoa, devePassar, fisicaJuridica, cenario):
    """
    Testa a inserção de novas pessoas (físicas e jurídicas) com diferentes cenários.
    
    Cenário testado: {}
    """.format(cenario)
    
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, selenium_exceptions, error_logger = init
    env_application_type = env_vars['APPLICATION_TYPE']
    
    Log_manager.add_log(level="INFO", message=f"Iniciando teste para o cenário: '{cenario}'",application_type=env_application_type, routine=Pessoas.rotina)

    try:
        FuncoesUteis.goToPage(init=init, url=Pessoas.url)
        FuncoesUteis.showHideFilter(init=init, seletor=Pessoas.filterSelector)
        Components.btnClick(init=init, seletor="#B88575101250151001") # Botão "Novo"
        Components.has_frame(init=init, seletor="[title='Cadastro de Pessoa']")

        if fisicaJuridica:
            resultado = Pessoas.insereDadosGeraisFisico(
                init=init,
                dadosPessoa=infoPessoa
            )
        else:
            resultado = Pessoas.insereDadosGeraisJuridico(
                init=init,
                dadosPessoa=infoPessoa
            )
        
        # O resultado pode ser o objeto da pessoa ou False em caso de falha esperada na UI.
        if resultado is not False:
            # Se a função retornou um objeto, extraímos os dados para log.
            dados_retornados = resultado.model_dump(exclude_none=True)
            print(f"Dados retornados: {dados_retornados}, Tipo: {type(dados_retornados)}")
        else:
            dados_retornados = None
            print("Função de inserção retornou False.")
        
        # Validação do resultado do teste
        if devePassar:
            assert resultado is not False, f"O cenário '{cenario}' deveria ter passado, mas falhou."
        else:
            assert resultado is False, f"O cenário '{cenario}' deveria ter falhado, mas passou."

    except selenium_exceptions as e:
        logs = error_logger(exc=e, block=f"{Pessoas.rotina} - {cenario}")
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message=f"{logs.time} - {logs.message}",
            routine=f"{Pessoas.rotina} - {cenario}",
            error_details=f"{logs.error} - {logs.type_error} - {logs.function_error}- {logs.file} - {str(logs.row)}"
        )
        pytest.fail(f"O teste falhou devido a uma exceção do Selenium no cenário '{cenario}': {e}")
    except AssertionError as e:
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message=f"Falha na asserção: {e}",
            routine=f"{Pessoas.rotina} - {cenario}",
            error_details=str(e)
        )
        pytest.fail(f"Falha na asserção no cenário '{cenario}': {e}")
    except Exception as e:
        logs = error_logger(exc=e, block=f"{Pessoas.rotina} - {cenario}")
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message=f"Uma exceção inesperada ocorreu: {logs.message}",
            routine=f"{Pessoas.rotina} - {cenario}",
            error_details=f"{logs.error} - {logs.type_error} - {logs.function_error}- {logs.file} - {str(logs.row)}"
        )
        pytest.fail(f"Uma exceção inesperada ocorreu no cenário '{cenario}': {e}")

    finally:
        endTime = time.time()
        executionTime = endTime - starTime
        minutos, segundos = divmod(executionTime, 60)
        
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Tempo de execução do cenário '{cenario}': {int(minutos)}m {segundos:.2f}s",
            routine=f"{Pessoas.rotina} - test_insere_nova_pessoa",
            error_details=''
        )
        
        # Garante que o navegador seja fechado mesmo se as asserções falharem
        try:
            browser.quit()
        except Exception as e:
            Log_manager.add_log(
                application_type=env_application_type,
                level="WARNING",
                message=f"Falha ao fechar o navegador no final do cenário '{cenario}': {e}",
                routine=f"{Pessoas.rotina} - test_insere_nova_pessoa",
                error_details=str(e)
            )
        
        # Inserir logs no final de cada parametrização para análise individual
        Log_manager.insert_logs_for_execution(logName=f"{Pessoas.rotina} - {cenario}")