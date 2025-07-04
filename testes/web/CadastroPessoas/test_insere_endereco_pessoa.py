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

# --- Objeto de Pessoa Gerado Dinamicamente (Pré-condição) ---
dados_pessoa_validos = Pessoas.Pessoa(
    P6_CPF=fake.cpf(),
    P6_RG=fake.rg(),
    P6_NOME=fake.name(),
    P6_E_PACIENTE='0',
    P6_GENERO='F',
    P6_APELIDO=fake.first_name(),
    P6_DATA_NASCIMENTO=fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%d/%m/%Y'),
    P6_ENVIAR_PARA_REGISTRO='0',
    P6_STATUS='1'
)
@pytest.mark.parametrize("pessoa,endereco, devePassar,salvar, cenario", [

    # ==== CENÁRIOS EXISTENTES (REFATORADOS) ====
    (   # Endereço válido com CEP
        dados_pessoa_validos,
        Pessoas.Endereco(
            P6_TIPO_ENDERECO_ID='1',
            P6_CEP='95700028',
            P6_NUMERO='123',
            P6_COMPLEMENTO='Apto 101',
            P6_CORRESPONDENCIA='0',
            P6_BOLETO_ENDERECO='1'
        ), True, True, "Endereço - Criação com CEP válido"
    ),
    (   # Endereco sem CEP, com preenchimento manual
        dados_pessoa_validos,
        Pessoas.Endereco(
            P6_TIPO_ENDERECO_ID='1',
            P6_ESTADO_ID='23', # RS
            P6_CIDADE_ID='4688', # Bento Gonçalves
            P6_ENDERECO='Rua Teste Manual',
            P6_BAIRRO='Bairro Teste',
            P6_NUMERO='456',
            P6_COMPLEMENTO='Casa',
            P6_CORRESPONDENCIA='1',
            P6_BOLETO_ENDERECO='0'
        ), True, True, "Endereço - Criação sem CEP (manual)"
    ),
    (   # CEP com formato inválido (letras)
        dados_pessoa_validos,
        Pessoas.Endereco(
            P6_TIPO_ENDERECO_ID='1',
            P6_CEP='ABCDE-FGH',
            P6_NUMERO='123'
        ), False, False, "Endereço - CEP com formato inválido (letras)"
    ),
    (   # CEP que não existe na base de dados
        dados_pessoa_validos,
        Pessoas.Endereco(
            P6_TIPO_ENDERECO_ID='1',
            P6_CEP='99999999',
            P6_NUMERO='123'
        ), False, False, "Endereço - CEP inexistente"
    ),

    # ==== CENÁRIOS DE SEGURANÇA (REFATORADOS E NOVOS) ====
    (   # Tentativa de XSS no campo Complemento (Básico)
        dados_pessoa_validos,
        Pessoas.Endereco(
            P6_CEP='95700028',
            P6_NUMERO='123',
            P6_COMPLEMENTO=XSS_PAYLOAD_BASIC
        ), False, True, "Endereço - Segurança: Tentativa de XSS no complemento"
    ),
    (   # Tentativa de XSS de imagem no campo Complemento
        dados_pessoa_validos,
        Pessoas.Endereco(
            P6_CEP='95700028',
            P6_NUMERO='123',
            P6_COMPLEMENTO=XSS_PAYLOAD_IMG
        ), False, True, "Endereço - Segurança: Tentativa de XSS de imagem no complemento"
    ),
    (   # Tentativa de SQL Injection no campo Endereço (manual)
        dados_pessoa_validos,
        Pessoas.Endereco(
            P6_ESTADO_ID='23',
            P6_CIDADE_ID='4688',
            P6_ENDERECO=SQL_INJECTION_PAYLOAD_SIMPLE,
            P6_NUMERO='123'
        ), False, True, "Endereço - Segurança: Tentativa de SQL Injection no endereço"
    ),
    (   # Tentativa de SQL Injection no campo Bairro (manual)
        dados_pessoa_validos,
        Pessoas.Endereco(
            P6_ESTADO_ID='23',
            P6_CIDADE_ID='4688',
            P6_ENDERECO='Rua Inofensiva',
            P6_BAIRRO=SQL_INJECTION_PAYLOAD_SIMPLE,
            P6_NUMERO='123'
        ), False, True, "Endereço - Segurança: Tentativa de SQL Injection no bairro"
    ),
    (   # Tentativa de XSS complexo no campo Complemento
        dados_pessoa_validos,
        Pessoas.Endereco(
            P6_CEP='95700028',
            P6_NUMERO='123',
            P6_COMPLEMENTO='<script>alert(String.fromCharCode(88,83,83))</script>'
        ), False, True, "Endereço - Segurança: Tentativa de XSS complexo no complemento"
    ),

    # ==== CENÁRIOS DE VALIDAÇÃO E CASOS EXTREMOS (REFATORADOS E NOVOS) ====
    (   # Campo obrigatório (Número) vazio
        dados_pessoa_validos,
        Pessoas.Endereco(
            P6_CEP='95700028',
            P6_NUMERO=''
        ), False, False, "Endereço - Validação: Campo obrigatório 'Número' vazio"
    ),
    (   # Campo obrigatório (Tipo de Endereço) vazio
        dados_pessoa_validos,
        Pessoas.Endereco(
            P6_TIPO_ENDERECO_ID='',
            P6_CEP='95700028',
            P6_NUMERO='123'
        ), False, False, "Endereço - Validação: Campo obrigatório 'Tipo de Endereço' vazio"
    ),
    (   # Campo obrigatório (Cidade) vazio no modo manual
        dados_pessoa_validos,
        Pessoas.Endereco(
            P6_TIPO_ENDERECO_ID='1',
            P6_ESTADO_ID='23',
            P6_ENDERECO='Rua Teste Manual',
            P6_BAIRRO='Bairro Teste',
            P6_NUMERO='456'
        ), False, False, "Endereço - Validação: Campo obrigatório 'Cidade' vazio (manual)"
    ),
    (   # Complemento com texto muito longo (estouro de limite)
        dados_pessoa_validos,
        Pessoas.Endereco(
            P6_CEP='95700028',
            P6_NUMERO='789',
            P6_COMPLEMENTO=fake.text(max_nb_chars=501)  # Assumindo limite de 500
        ), False, False, "Endereço - Validação: Limite de caracteres no complemento"
    ),
    (   # Número com caracteres não numéricos
        dados_pessoa_validos,
        Pessoas.Endereco(
            P6_CEP='95700028',
            P6_NUMERO='abc'
        ), False, False, "Endereço - Validação: 'Número' com caracteres não numéricos"
    ),
    
    
    (   # Tentar salvar sem preencher nenhum campo obrigatório
        dados_pessoa_validos,
        Pessoas.Endereco(), # Objeto Endereco vazio
        False, True, "Endereço - Validação: Tentativa de salvar formulário vazio"
    )
])
@pytest.mark.dockerCadastroPessoas
def test_insere_endereco(init, pessoa, endereco, devePassar,salvar, cenario):
    """
    Testa a inserção de endereços com diferentes cenários.
    Cenário testado: {}
    """.format(cenario)
    
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, selenium_exceptions, error_logger = init
    env_application_type = env_vars['APPLICATION_TYPE']

    # Nota: Este teste assume que já estamos no contexto do modal de "Cadastro de Pessoa".
    # Em um fluxo real, seria necessário primeiro preencher os dados da pessoa.
    Log_manager.add_log(level="INFO", message=f"Iniciando teste para o cenário: '{cenario}'",application_type=env_application_type, routine=Pessoas.rotina)

    try:
        # A navegação e abertura do modal deveriam, idealmente, ser parte de uma fixture ou setup
        FuncoesUteis.goToPage(init=init, url=Pessoas.url)
        FuncoesUteis.showHideFilter(init=init, seletor=Pessoas.filterSelector)
        Components.btnClick(init=init, seletor="#B88575101250151001") # Botão "Novo"
        Components.has_frame(init=init, seletor="[title='Cadastro de Pessoa']")
    
        sucesso_pessoa = Pessoas.insereDadosGeraisFisico(
            init=init,
            dadosPessoa=pessoa
        )

        # Apenas prossegue se a inserção da pessoa funcionar.
        if not isinstance(sucesso_pessoa,Pessoas.Pessoa):
            # Força uma falha no teste se a pré-condição não for atendida.
            assert False, "Falha ao inserir os dados base da pessoa. O teste de contato não pode continuar."

        # --- Ação principal do teste ---
        resultado = Pessoas.insereEndereco(init=init, enderecoPessoa=endereco,salvar=salvar)

        if resultado is not False:
            dados_retornados = resultado.model_dump(exclude_none=True)
            print(f"Dados retornados: {dados_retornados}")
        else:
            print("Função de inserção de endereço retornou False, como esperado para o cenário.")

        # --- Validação ---
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
    finally:
        endTime = time.time()
        executionTime = endTime - starTime
        minutos, segundos = divmod(executionTime, 60)
        
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Tempo de execução do cenário '{cenario}': {int(minutos)}m {segundos:.2f}s",
            routine=f"{Pessoas.rotina} - test_insere_endereco",
            error_details=''
        )
        
        try:
            browser.quit()
        except Exception as e:
            Log_manager.add_log(
                application_type=env_application_type,
                level="WARNING",
                message=f"Falha ao fechar o navegador no final do cenário '{cenario}': {e}",
                routine=f"{Pessoas.rotina} - test_insere_endereco",
                error_details=str(e)
            )
        
        Log_manager.insert_logs_for_execution(logName=f"{Pessoas.rotina} - {cenario}")