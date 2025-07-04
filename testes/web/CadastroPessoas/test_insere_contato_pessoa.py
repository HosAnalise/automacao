import time
import pytest
from classes.rotinas.CadastroPessoas import Pessoas
from classes.utils.Components import Components
from classes.utils.FuncoesUteis import FuncoesUteis
from faker import Faker
fake = Faker(locale='pt_BR')

# --- Objeto de Pessoa Gerado Dinamicamente ---
# Criamos um único objeto de pessoa com dados válidos usando o Faker.
# Este mesmo objeto será usado em todos os cenários de teste de contato.
# Isso garante que a primeira parte do teste (inserir pessoa) seja consistente
# e que o foco da falha seja apenas nos dados do contato.
dados_pessoa_validos = Pessoas.Pessoa(
    P6_CPF=fake.cpf(),
    P6_RG=fake.rg(),
    P6_NOME=fake.name(), # Adicionei o P6_NOME que provavelmente é necessário
    P6_E_PACIENTE='0',
    P6_GENERO='F',
    P6_APELIDO=fake.first_name(),
    P6_DATA_NASCIMENTO=fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%d/%m/%Y'),
    P6_ENVIAR_PARA_REGISTRO='0',
    P6_STATUS='1'
)


@pytest.mark.parametrize("dadosPessoa, contatoPessoa, devePassar, salvar, cenario", [
    # Cenário 1: Caminho feliz com dados de contato válidos
    (
        dados_pessoa_validos,
        Pessoas.Contato(
            P6_NOME_CONTATO=fake.name(),
            P6_CONTATO_EMAIL=fake.email(),
            P6_CONTATO_OBSERVACAO=fake.text(50),
            P6_CONTATO_TELEFONE=fake.numerify('(##) 3###-####'),
            P6_CONTATO_CELULAR=fake.numerify('(##) 9####-####'),
            P6_E_RESPONSAVEL='0',
            P6_ENVIAR_EMAIL='0',
            P6_BOLETO_CONTATO='1'
        ), True, True, "Caminho feliz com dados de contato válidos" # Salvar = True para criar o registro completo
    ),
    # Cenário 2: Contato com dados de comprimento excessivo
    (
        dados_pessoa_validos,
        Pessoas.Contato(
            P6_NOME_CONTATO=fake.text(500),
            P6_CONTATO_EMAIL=fake.email(),
            P6_CONTATO_OBSERVACAO=fake.text(1000),
            P6_CONTATO_TELEFONE=fake.text(50),
            P6_CONTATO_CELULAR=fake.text(50),
            P6_E_RESPONSAVEL='1',
            P6_ENVIAR_EMAIL='1',
            P6_BOLETO_CONTATO='0'
        ), False, False, "Contato com dados de comprimento excessivo"
    ),
    # Cenário 3: Contato com nome vazio
    (
        dados_pessoa_validos,
        Pessoas.Contato(
            P6_NOME_CONTATO="",  # Nome vazio
            P6_CONTATO_EMAIL=fake.email(),
            P6_CONTATO_OBSERVACAO="Teste",
            P6_CONTATO_TELEFONE=fake.numerify('(##) ####-####'),
            P6_CONTATO_CELULAR=fake.numerify('(##) #####-####'),
            P6_E_RESPONSAVEL='0',
            P6_ENVIAR_EMAIL='0',
            P6_BOLETO_CONTATO='1'
        ), False, False, "Nome do contato vazio"
    ),
    # Cenário 4: Contato com e-mail em formato inválido
    (
        dados_pessoa_validos,
        Pessoas.Contato(
            P6_NOME_CONTATO=fake.name(),
            P6_CONTATO_EMAIL="email_invalido.com",  # E-mail inválido
            P6_CONTATO_OBSERVACAO="Teste",
            P6_CONTATO_TELEFONE=fake.numerify('(##) ####-####'),
            P6_CONTATO_CELULAR=fake.numerify('(##) #####-####'),
            P6_E_RESPONSAVEL='0',
            P6_ENVIAR_EMAIL='1',
            P6_BOLETO_CONTATO='0'
        ), False, False, "Formato de e-mail do contato inválido"
    ),
     # Cenário: Tentativa de inserir caracteres especiais e scripts (XSS) no nome
    (
        dados_pessoa_validos,
        Pessoas.Contato(
            P6_NOME_CONTATO="<script>alert('XSS')</script>",  # Tentativa de XSS
            P6_CONTATO_EMAIL=fake.email(),
            P6_CONTATO_OBSERVACAO="Teste com caracteres '\"`´{[]}",
            P6_CONTATO_TELEFONE=fake.numerify('(##) ####-####'),
            P6_CONTATO_CELULAR=fake.numerify('(##) #####-####'),
            P6_E_RESPONSAVEL='0',
            P6_ENVIAR_EMAIL='0',
            P6_BOLETO_CONTATO='1'
        ), False, True, "Nome do contato com tentativa de XSS"
    ),

    # Cenário: Inserir apenas espaços em campos de texto
    (
        dados_pessoa_validos,
        Pessoas.Contato(
            P6_NOME_CONTATO="   ",  # Apenas espaços
            P6_CONTATO_EMAIL=fake.email(),
            P6_CONTATO_OBSERVACAO="   ", # Apenas espaços
            P6_CONTATO_TELEFONE=fake.numerify('(##) ####-####'),
            P6_CONTATO_CELULAR=fake.numerify('(##) #####-####'),
            P6_E_RESPONSAVEL='0',
            P6_ENVIAR_EMAIL='0',
            P6_BOLETO_CONTATO='1'
        ), False, True, "Campos de texto preenchidos apenas com espaços"
    ),

    # Cenário: Telefones com caracteres não numéricos
    (
        dados_pessoa_validos,
        Pessoas.Contato(
            P6_NOME_CONTATO=fake.name(),
            P6_CONTATO_EMAIL=fake.email(),
            P6_CONTATO_OBSERVACAO="Teste",
            P6_CONTATO_TELEFONE="Telefone Invalido", # Telefone com letras
            P6_CONTATO_CELULAR="(99) 9-ABC-DEFG", # Celular com letras
            P6_E_RESPONSAVEL='0',
            P6_ENVIAR_EMAIL='0',
            P6_BOLETO_CONTATO='1'
        ), False, True, "Telefone e celular com caracteres não numéricos"
    ),

    # Cenário: Flags com valores inesperados
    (
        dados_pessoa_validos,
        Pessoas.Contato(
            P6_NOME_CONTATO=fake.name(),
            P6_CONTATO_EMAIL=fake.email(),
            P6_CONTATO_OBSERVACAO="Teste",
            P6_CONTATO_TELEFONE=fake.numerify('(##) ####-####'),
            P6_CONTATO_CELULAR=fake.numerify('(##) #####-####'),
            P6_E_RESPONSAVEL='True', # Valor inválido (esperado '0' ou '1')
            P6_ENVIAR_EMAIL='sim', # Valor inválido
            P6_BOLETO_CONTATO=None # Valor nulo
        ), False, True, "Flags (booleans) com valores inválidos"
    ),
    # Cenário 5: Contato para boleto sem e-mail
    (
        dados_pessoa_validos,
        Pessoas.Contato(
            P6_NOME_CONTATO=fake.name(),
            P6_CONTATO_EMAIL="",  # E-mail está vazio
            P6_CONTATO_OBSERVACAO="Teste boleto sem email",
            P6_CONTATO_TELEFONE=fake.numerify('(##) 3###-####'),
            P6_CONTATO_CELULAR=fake.numerify('(##) 9####-####'),
            P6_E_RESPONSAVEL='1',
            P6_ENVIAR_EMAIL='0', # Flag de envio de email geral está desligada
            P6_BOLETO_CONTATO='1' # Mas a flag de boleto está ligada
        ), False, True, "Falha: Contato para boleto deve ter e-mail"
    ),
    # Adicione aqui outros cenários focados em quebrar os dados do CONTATO...
])
@pytest.mark.dockerCadastroPessoas
# Removi fiscaJuridica que não estava sendo usado
def test_insere_contato_pessoa(init, dadosPessoa, contatoPessoa, devePassar, salvar, cenario):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, selenium_exceptions, error_logger = init
    env_application_type = env_vars['APPLICATION_TYPE']

    Log_manager.add_log(
        application_type=env_application_type,
        level="INFO",
        message=f"Iniciando cenário de teste: {cenario}",
        routine=f"{Pessoas.rotina} - test_insere_contato_pessoa",
        error_details=''
    )

    try:
        FuncoesUteis.goToPage(init=init, url=Pessoas.url)
        FuncoesUteis.showHideFilter(init=init, seletor=Pessoas.filterSelector)
        Components.btnClick(init=init, seletor="#B88575101250151001")
        Components.has_frame(init=init, seletor="[title='Cadastro de Pessoa']")

        # ETAPA 1: Inserir os dados da pessoa (pré-condição)
        # Assumindo que essa função retorna True em sucesso e False em falha.
        sucesso_pessoa = Pessoas.insereDadosGeraisFisico(
            init=init,
            dadosPessoa=dadosPessoa
        )

        # Apenas prossegue se a inserção da pessoa funcionar.
        if not isinstance(sucesso_pessoa,Pessoas.Pessoa):
            # Força uma falha no teste se a pré-condição não for atendida.
            assert False, "Falha ao inserir os dados base da pessoa. O teste de contato não pode continuar."


        # ETAPA 2: Inserir os dados de contato e validar o resultado
        resultado_contato = Pessoas.insereContato(init=init, contatoPessoa=contatoPessoa, save=salvar)


        if devePassar:
            if not resultado_contato:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="WARNING",
                    message=f"Cenário '{cenario}' devia passar, mas retornou uma falha.",
                    routine=f"{Pessoas.rotina} - test_insere_contato_pessoa"
                )
            assert resultado_contato is not False, f"Falha no cenário: '{cenario}'"
        else:
            if resultado_contato:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="WARNING",
                    message=f"Cenário '{cenario}' devia falhar, mas passou.",
                    routine=f"{Pessoas.rotina} - test_insere_contato_pessoa"
                )
            assert resultado_contato is False, f"Falha no cenário: '{cenario}'"

    except selenium_exceptions as e:
        print(f"Exceção do Selenium: {e}")
        logs = error_logger(exc=e, block=f"{Pessoas.rotina} - test_insere_contato_pessoa")
        print(f"teste traceback{logs}")
        Log_manager.add_log(
            application_type=env_application_type,
            level="ERROR",
            message=f"{logs.time} - {logs.message}",
            routine=f"{Pessoas.rotina} - test_insere_contato_pessoa (Cenário: {cenario})",
            error_details=f"{logs.error} - {logs.type_error} - {logs.function_error}- {logs.file} - {str(logs.row)}"
        )
        assert False, f"Exceção inesperada no cenário '{cenario}': {e}"
    
    finally:
        # Seu bloco finally está ótimo, mantive como está.
        endTime = time.time()
        executionTime = endTime - starTime
        minutos = int(executionTime // 60)
        segundos = int(executionTime % 60)
        milissegundos = int((executionTime % 1) * 1000)

        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Tempo de execução do teste '{cenario}': {minutos} min {segundos} s {milissegundos} ms",
            routine=f"{Pessoas.rotina} - test_insere_contato_pessoa",
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
                routine=f"{Pessoas.rotina} - test_insere_contato_pessoa",
                error_details=str(e)
            )