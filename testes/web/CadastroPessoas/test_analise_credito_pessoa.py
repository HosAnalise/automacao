from os import error
import time
import pytest
from classes.rotinas.CadastroPessoas import Pessoas
from classes.utils.Components import Components
from classes.utils.FuncoesUteis import FuncoesUteis
from faker import Faker

fake = Faker(locale='pt_BR')

# Mantenha sua fixture para gerar dados de pessoa válidos
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

# Payloads de segurança para reutilização
XSS_PAYLOAD = "<script>alert('XSS')</script>"
SQL_INJECTION_PAYLOAD = "' OR '1'='1"

# O parâmetro 'objDecisaoCredito' foi removido
@pytest.mark.parametrize("pessoaValida, objAnalisePropria, devePassar, salvar, cenario", [

    # ==== CENÁRIO DE SUCESSO (HAPPY PATH) ====
    (
        dados_pessoa_validos,
        Pessoas.AnaliseCredito.AnalisePropria(
            P277_DATA_ANALISE=fake.date(pattern='%d/%m/%Y'),
            P277_RENDA_INFORMADA=str(fake.random_number(digits=5)),
            P277_LIMITE_CREDITO=str(fake.random_number(digits=5)),
            P277_OBSERVACAO=fake.text(max_nb_chars=200),
            P277_SITUACAO='0',  # 'Liberado'
            P277_RENDA_COMPROVADA=str(fake.random_number(digits=5)),
            P277_VALIDADE_ANALISE=str(fake.random_number(digits=3)),
            P277_DECISAO_ANALISE='0'  # 'Aprovado'
        ),
        True, True, "Sucesso - Criação de análise com todos os campos válidos"
    ),
    (
        dados_pessoa_validos,
        Pessoas.AnaliseCredito.AnalisePropria(
            P277_DATA_ANALISE=fake.date(pattern='%d/%m/%Y'),
            P277_RENDA_INFORMADA="1500.50",
            P277_LIMITE_CREDITO="500",
            P277_OBSERVACAO="Cliente com bom histórico",
            P277_SITUACAO='1',  # 'Bloqueado'
            P277_RENDA_COMPROVADA="1400.00",
            P277_VALIDADE_ANALISE="365",
            P277_DECISAO_ANALISE='1'  # 'Reprovado'
        ),
        True, True, "Sucesso - Criação de análise com decisão 'Reprovado' e situação 'Bloqueado'"
    ),
    (
        dados_pessoa_validos,
        Pessoas.AnaliseCredito.AnalisePropria(
            P277_DATA_ANALISE=fake.date(pattern='%d/%m/%Y'),
            P277_LIMITE_CREDITO='0',  # Limite de crédito zerado
            P277_DECISAO_ANALISE='0'
        ),
        True, True, "Sucesso - Criação de análise com limite de crédito igual a zero"
    ),

    # ==== CENÁRIOS DE VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS ====
    (
        dados_pessoa_validos,
        Pessoas.AnaliseCredito.AnalisePropria(
            P277_DATA_ANALISE="None",  # Campo obrigatório ausente
            P277_LIMITE_CREDITO="5000",
            P277_DECISAO_ANALISE='0'
        ),
        False, False, "Validação - Campo obrigatório 'Data da Análise' não preenchido"
    ),
    (
        dados_pessoa_validos,
        Pessoas.AnaliseCredito.AnalisePropria(
            P277_DATA_ANALISE=fake.date(pattern='%d/%m/%Y'),
            P277_LIMITE_CREDITO="None",  # Campo obrigatório ausente
            P277_DECISAO_ANALISE='0'
        ),
        False, False, "Validação - Campo obrigatório 'Limite de Crédito' não preenchido"
    ),
    (
        dados_pessoa_validos,
        Pessoas.AnaliseCredito.AnalisePropria(
            P277_DATA_ANALISE=fake.date(pattern='%d/%m/%Y'),
            P277_LIMITE_CREDITO='5000',
            P277_DECISAO_ANALISE="None"  # Campo obrigatório ausente
        ),
        False, False, "Validação - Campo obrigatório 'Decisão da Análise' não preenchido"
    ),

    # ==== CENÁRIOS DE VALIDAÇÃO DE FORMATO E DADOS INVÁLIDOS ====
    (
        dados_pessoa_validos,
        Pessoas.AnaliseCredito.AnalisePropria(
            P277_DATA_ANALISE="2023-01-30",  # Formato de data inválido
            P277_LIMITE_CREDITO="5000",
            P277_DECISAO_ANALISE='0'
        ),
        False, False, "Validação - Formato de data inválido para 'Data da Análise'"
    ),
    (
        dados_pessoa_validos,
        Pessoas.AnaliseCredito.AnalisePropria(
            P277_DATA_ANALISE=fake.date(pattern='%d/%m/%Y'),
            P277_RENDA_INFORMADA="mil reais",  # Valor não numérico
            P277_LIMITE_CREDITO="5000",
            P277_DECISAO_ANALISE='0'
        ),
        False, False, "Validação - Valor não numérico no campo 'Renda Informada'"
    ),
    (
        dados_pessoa_validos,
        Pessoas.AnaliseCredito.AnalisePropria(
            P277_DATA_ANALISE=fake.date(pattern='%d/%m/%Y'),
            P277_LIMITE_CREDITO="-100",  # Valor negativo
            P277_DECISAO_ANALISE='0'
        ),
        False, False, "Validação - Valor negativo no campo 'Limite de Crédito'"
    ),

    # ==== CENÁRIOS DE SEGURANÇA ====
    (
        dados_pessoa_validos,
        Pessoas.AnaliseCredito.AnalisePropria(
            P277_DATA_ANALISE=fake.date(pattern='%d/%m/%Y'),
            P277_LIMITE_CREDITO="1000",
            P277_DECISAO_ANALISE='0',
            P277_OBSERVACAO=XSS_PAYLOAD
        ),
        False, False, "Segurança - Tentativa de injeção de XSS no campo 'Observação'"
    ),
    (
        dados_pessoa_validos,
        Pessoas.AnaliseCredito.AnalisePropria(
            P277_DATA_ANALISE=fake.date(pattern='%d/%m/%Y'),
            P277_LIMITE_CREDITO="1000",
            P277_DECISAO_ANALISE='0',
            P277_OBSERVACAO=SQL_INJECTION_PAYLOAD
        ),
        False, False, "Segurança - Tentativa de SQL Injection no campo 'Observação'"
    ),

    # ==== CENÁRIOS DE CASOS EXTREMOS E LIMITES ====
    (
        dados_pessoa_validos,
        Pessoas.AnaliseCredito.AnalisePropria(
            P277_DATA_ANALISE=fake.date(pattern='%d/%m/%Y'),
            P277_LIMITE_CREDITO="1000",
            P277_DECISAO_ANALISE='0',
            P277_OBSERVACAO=fake.text(max_nb_chars=1001)  # Supondo que o limite seja 1000
        ),
        False, False, "Limite - Estouro de caracteres no campo 'Observação'"
    ),
    (
        dados_pessoa_validos,
        Pessoas.AnaliseCredito.AnalisePropria(
            P277_DATA_ANALISE=fake.date(pattern='%d/%m/%Y'),
            P277_LIMITE_CREDITO=str(9999999999),  # Valor de limite de crédito muito alto
            P277_DECISAO_ANALISE='0'
        ),
        True, True, "Limite - Valor muito alto para 'Limite de Crédito' (dentro do aceitável)"
    )
])
@pytest.mark.dockerCadastroPessoas
# O parâmetro 'objDecisaoCredito' foi removido da assinatura da função
def test_analise_credito_pessoa(init, pessoaValida, objAnalisePropria, devePassar, salvar, cenario):
    """
    Testa a criação de uma Análise de Crédito Própria para uma pessoa física.

    O teste segue os seguintes passos:
    1.  Acessa a tela de cadastro de pessoas.
    2.  Cria uma nova pessoa física com dados válidos.
    3.  Acessa a funcionalidade de Análise de Crédito.
    4.  Preenche e tenta salvar uma nova Análise Própria com base nos parâmetros do cenário.
    5.  Verifica se o resultado (sucesso ou falha) corresponde ao esperado.
    """
    startTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, selenium_exceptions, error_logger = init
    env_application_type = env_vars['APPLICATION_TYPE']
    Log_manager.add_log(level="INFO", message=f"Iniciando teste para o cenário: '{cenario}'",application_type=env_application_type, routine=Pessoas.rotina)

    try:
        # --------------------------------------------------------------------
        # ARRANGE: Preparação do ambiente e dos dados de pré-requisito
        # --------------------------------------------------------------------
        FuncoesUteis.goToPage(init=init, url=Pessoas.url)
        FuncoesUteis.showHideFilter(init=init, seletor=Pessoas.filterSelector)
        Components.btnClick(init=init, seletor="#B88575101250151001") # Botão "Criar"
        Components.has_frame(init=init, seletor="[title='Cadastro de Pessoa']")

        # Cadastra a pessoa que receberá a análise de crédito. Falha o teste se não conseguir.
        pessoa_cadastrada = Pessoas.insereDadosGeraisFisico(init=init, dadosPessoa=pessoaValida)
        if not isinstance(pessoa_cadastrada, Pessoas.Pessoa):
            pytest.fail("Falha no pré-requisito: Não foi possível cadastrar a pessoa base para o teste.")

        # Abre a tela para uma nova análise de crédito
        if not Pessoas.AnaliseCredito.novaAnaliseCredito(init=init):
            pytest.fail("Falha ao clicar no botão para iniciar uma nova análise de crédito.")

        # --------------------------------------------------------------------
        # ACT: Execução da ação principal a ser testada
        # --------------------------------------------------------------------
        # Preenche o formulário de análise própria e tenta salvar (ou não), conforme o cenário
        resultado_obtido = Pessoas.AnaliseCredito.novaAnalisePropria(init=init, obj=objAnalisePropria, save=salvar)
        # --------------------------------------------------------------------
        # ASSERT: Verificação do resultado
        # --------------------------------------------------------------------
        # Verifica se a análise foi salva (ou não), conforme o esperado pelo cenário
        # 'resultado_obtido' será um objeto (True-like) se a análise for encontrada, e False caso contrário.
        assert (resultado_obtido is not False) == devePassar, f"Falha no cenário '{cenario}'. Resultado esperado: {devePassar}, Resultado obtido: {resultado_obtido is not False}"

    except selenium_exceptions as e:
        # Tratamento de exceções do Selenium e log detalhado
        logs = error_logger(exc=e, block=f"Cenário: {cenario}")
        Log_manager.add_log(
            application_type=env_application_type, level="ERROR",
            message=f"{logs.time} - {logs.message}",
            routine=f"{Pessoas.rotina} - {logs.function_error} - {logs.file} - Linha {str(logs.row)}",
            error_details=f"{logs.error} - {logs.type_error}"
        )
        pytest.fail(f"Ocorreu um erro de Selenium no cenário '{cenario}': {logs.message}")

    finally:
        # --------------------------------------------------------------------
        # CLEANUP: Finalização e registro de logs
        # --------------------------------------------------------------------
        executionTime = time.time() - startTime
        minutos, segundos = divmod(int(executionTime), 60)
        milissegundos = int((executionTime % 1) * 1000)
        Log_manager.add_log(
            level="INFO",
            message=f"Cenário '{cenario}' finalizado. Tempo de execução: {minutos}m {segundos}s {milissegundos}ms",
            error_details="None",
            application_type=env_application_type,
            routine=Pessoas.rotina
        )
        Log_manager.insert_logs_for_execution(logName=Pessoas.rotina)

        browser.quit()
       