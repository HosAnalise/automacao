import time
import pytest
from classes.rotinas.CadastroPessoas import Pessoas
from classes.utils.Components import Components
from classes.utils.FuncoesUteis import FuncoesUteis
from faker import Faker
fake = Faker(locale='pt_BR')

# --- Objeto de Pessoa Gerado Dinamicamente (Pré-condição) ---
# A base para o teste está perfeita.
dados_pessoa_validos = Pessoas.Pessoa(
    P6_CPF=fake.cpf(),
    P6_RG=fake.rg(),
    P6_NOME=fake.name(),
    P6_E_PACIENTE='0',
    P6_GENERO='F',
    P6_APELIDO=fake.first_name(),
    P6_DATA_NASCIMENTO=fake.date_of_birth(minimum_age=30, maximum_age=90).strftime('%d/%m/%Y'), # Idade maior para ter dependentes
    P6_ENVIAR_PARA_REGISTRO='0',
    P6_STATUS='1'
)

# --- Cenários de Teste para DEPENDENTES (Totalmente Reescritos) ---
@pytest.mark.parametrize("dadosPessoa, dependentePessoa, devePassar, salvar, cenario", [
    # Cenário 1: Caminho feliz com dependente válido
    (
        dados_pessoa_validos,
        Pessoas.Dependentes(
            P6_NOME_DEPENDENTE=fake.name(),
            P6_CARTAO_DEPENDENTE=fake.numerify(text='#######'),
            P6_CATEGORIA_DEPENDENTE='2', # Ex: Filho(a)
            P6_STATUS_DEPENDENTE='1',    # Ex: Ativo
            P6_DOCUMENTO_DEPENDENTE=fake.cpf()
        ), True, True, "Caminho feliz: Dependente válido"
    ),
    # Cenário 2: Nome do dependente vazio
    (
        dados_pessoa_validos,
        Pessoas.Dependentes(
            P6_NOME_DEPENDENTE="", # Campo obrigatório vazio
            P6_CARTAO_DEPENDENTE=fake.numerify(text='#######'),
            P6_CATEGORIA_DEPENDENTE='2',
            P6_STATUS_DEPENDENTE='1',
            P6_DOCUMENTO_DEPENDENTE=fake.cpf()
        ), False, True, "Falha: Nome do dependente não pode ser vazio"
    ),
    # Cenário 3: Categoria do dependente não selecionada
    (
        dados_pessoa_validos,
        Pessoas.Dependentes(
            P6_NOME_DEPENDENTE=fake.name(),
            P6_CARTAO_DEPENDENTE=fake.numerify(text='#######'),
            P6_CATEGORIA_DEPENDENTE=None, # Campo obrigatório nulo
            P6_STATUS_DEPENDENTE='1',
            P6_DOCUMENTO_DEPENDENTE=fake.cpf()
        ), False, True, "Falha: Categoria do dependente não selecionada"
    ),
    # Cenário 4: Nome do dependente com comprimento excessivo
    (
        dados_pessoa_validos,
        Pessoas.Dependentes(
            P6_NOME_DEPENDENTE=fake.pystr(min_chars=150, max_chars=160), # Nome muito longo
            P6_CARTAO_DEPENDENTE=fake.numerify(text='#######'),
            P6_CATEGORIA_DEPENDENTE='2',
            P6_STATUS_DEPENDENTE='1',
            P6_DOCUMENTO_DEPENDENTE=fake.cpf()
        ), False, False, "Falha: Nome do dependente com comprimento excessivo"
    ),
    # Cenário 5: Tentativa de XSS no número do cartão
    (
        dados_pessoa_validos,
        Pessoas.Dependentes(
            P6_NOME_DEPENDENTE=fake.name(),
            P6_CARTAO_DEPENDENTE="<script>alert('XSS')</script>",
            P6_CATEGORIA_DEPENDENTE='2',
            P6_STATUS_DEPENDENTE='1',
            P6_DOCUMENTO_DEPENDENTE=fake.cpf()
        ), False, True, "Falha: Tentativa de XSS no número do cartão"
    ),
    # Cenário 6: Documento do dependente preenchido com espaços
    (
        dados_pessoa_validos,
        Pessoas.Dependentes(
            P6_NOME_DEPENDENTE=fake.name(),
            P6_CARTAO_DEPENDENTE=fake.numerify(text='#######'),
            P6_CATEGORIA_DEPENDENTE='2',
            P6_STATUS_DEPENDENTE='1',
            P6_DOCUMENTO_DEPENDENTE="      " # Apenas espaços
        ), False, True, "Falha: Documento do dependente preenchido com espaços"
    ),
    # Cenário 7: Cadastrar o mesmo dependente (mesmo documento) duas vezes
    (
        dados_pessoa_validos,
        Pessoas.Dependentes(
            P6_NOME_DEPENDENTE=fake.name(),
            P6_CARTAO_DEPENDENTE=fake.numerify(text='#######'),
            P6_CATEGORIA_DEPENDENTE='3', # Ex: Cônjuge
            P6_STATUS_DEPENDENTE='1',
            P6_DOCUMENTO_DEPENDENTE=fake.cpf() # Usaremos o mesmo CPF duas vezes
        ), False, True, "Falha: Tentar cadastrar o mesmo dependente duas vezes"
    ),
    # Cenário 8: Status do dependente inválido/inexistente
    (
        dados_pessoa_validos,
        Pessoas.Dependentes(
            P6_NOME_DEPENDENTE=fake.name(),
            P6_CARTAO_DEPENDENTE=fake.numerify(text='#######'),
            P6_CATEGORIA_DEPENDENTE='2',
            P6_STATUS_DEPENDENTE='99', # Status Inválido
            P6_DOCUMENTO_DEPENDENTE=fake.cpf()
        ), False, True, "Falha: Status do dependente inválido"
    ),
    # Cenário 9: Documento do dependente com formato inválido
    (
        dados_pessoa_validos,
        Pessoas.Dependentes(
            P6_NOME_DEPENDENTE=fake.name(),
            P6_CARTAO_DEPENDENTE=fake.numerify(text='#######'),
            P6_CATEGORIA_DEPENDENTE='2',
            P6_STATUS_DEPENDENTE='1',
            P6_DOCUMENTO_DEPENDENTE="123.456.789-XX" # Formato inválido
        ), False, True, "Falha: Documento do dependente com formato inválido"
    ),
    
])
@pytest.mark.dockerCadastroPessoas
def test_insere_dependente_pessoa(init, dadosPessoa, dependentePessoa, devePassar, salvar, cenario):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, selenium_exceptions, error_logger = init
    env_application_type = env_vars['APPLICATION_TYPE']
    
    # --- Nome da rotina nos logs corrigido ---
    rotina_log = f"{Pessoas.rotina} - test_insere_dependente_pessoa"

    Log_manager.add_log(
        application_type=env_application_type,
        level="INFO",
        message=f"Iniciando cenário de teste: {cenario}",
        routine=rotina_log
    )

    try:
        FuncoesUteis.goToPage(init=init, url=Pessoas.url)
        FuncoesUteis.showHideFilter(init=init, seletor=Pessoas.filterSelector)
        Components.btnClick(init=init, seletor="#B88575101250151001")
        Components.has_frame(init=init, seletor="[title='Cadastro de Pessoa']")

        sucesso_pessoa = Pessoas.insereDadosGeraisFisico(
            init=init,
            dadosPessoa=dadosPessoa
        )

        if not isinstance(sucesso_pessoa, Pessoas.Pessoa):
            assert False, "Falha ao inserir os dados base da pessoa. O teste de dependente não pode continuar."

        if "duas vezes" in cenario:
            # Insere o dependente a primeira vez (deve passar)
            Pessoas.insereDependente(init=init, dependentePessoa=dependentePessoa, save=salvar)
            # Tenta inserir o mesmo dependente novamente (deve falhar)
            resultado_final = Pessoas.insereDependente(init=init, dependentePessoa=dependentePessoa, save=salvar)
        else:
            resultado_final = Pessoas.insereDependente(init=init, dependentePessoa=dependentePessoa, save=salvar)

        # --- Lógica de Validação ---
        if devePassar:
            if not resultado_final:
                Log_manager.add_log(
                    application_type=env_application_type, level="WARNING",
                    message=f"Cenário '{cenario}' devia passar, mas retornou uma falha.",
                    routine=rotina_log
                )
            assert resultado_final is not False, f"Falha no cenário: '{cenario}'"
        else:
            if resultado_final is not False:
                Log_manager.add_log(
                    application_type=env_application_type, level="WARNING",
                    message=f"Cenário '{cenario}' devia falhar, mas passou.",
                    routine=rotina_log
                )
            assert resultado_final is False, f"Falha no cenário: '{cenario}'"

    except selenium_exceptions as e:
        logs = error_logger(exc=e, block=rotina_log)
        Log_manager.add_log(
            application_type=env_application_type, level="ERROR",
            message=f"{logs.time} - {logs.message}",
            routine=f"{rotina_log} (Cenário: {cenario})",
            error_details=f"{logs.error} - {logs.type_error} - {logs.function_error}- {logs.file} - {str(logs.row)}"
        )
        assert False, f"Exceção inesperada no cenário '{cenario}': {e}"
    
    finally:
        # Bloco finally está perfeito.
        endTime = time.time()
        executionTime = endTime - starTime
        minutos = int(executionTime // 60)
        segundos = int(executionTime % 60)
        milissegundos = int((executionTime % 1) * 1000)

        Log_manager.add_log(
            application_type=env_application_type, level="INFO",
            message=f"Tempo de execução do teste '{cenario}': {minutos} min {segundos} s {milissegundos} ms",
            routine=rotina_log
        )
        Log_manager.insert_logs_for_execution(logName=Pessoas.rotina)

        try:
            browser.quit()
        except Exception as e:
            Log_manager.add_log(
                application_type=env_application_type, level="WARNING",
                message=f"Falha ao fechar o navegador: {e}",
                routine=rotina_log, error_details=str(e)
            )