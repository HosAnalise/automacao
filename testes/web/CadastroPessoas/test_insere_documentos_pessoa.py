import time
import pytest
# ERRO CORRIGIDO: Removido import desnecessário e incorreto.
# from sqlalchemy import true 
from classes.rotinas.CadastroPessoas import Pessoas
from classes.utils.Components import Components
from classes.utils.FuncoesUteis import FuncoesUteis
from faker import Faker
fake = Faker(locale='pt_BR')

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

# --- Cenários de Teste para DOCUMENTOS (Lógica de 'salvar' refinada) ---
@pytest.mark.parametrize("dadosPessoa, documentoPessoa, devePassar, salvar, cenario", [
    # Cenário 1: Caminho feliz. Deve salvar para garantir que o registro seja criado no banco.
    (
        dados_pessoa_validos,
        Pessoas.Documentos(
        P6_N_DOCUMENTO=fake.rg(), 
        P6_TIPO_DOCUMENTO_ID="3", 
        P6_UF_EXPEDIDOR_ID='23', 
        P6_TIPO_ORGAO_EMISSOR_ID="1"
        ),
        True, True, "Caminho feliz: Documento válido" # AJUSTE: Salvar = True para validar a persistência.
    ),
    # Cenário 2: Validação de campo vazio. Geralmente ocorre no back-end ao tentar salvar.
    (
        dados_pessoa_validos,
        Pessoas.Documentos(
        P6_N_DOCUMENTO="", 
        P6_TIPO_DOCUMENTO_ID="3", 
        P6_UF_EXPEDIDOR_ID='23', 
        P6_TIPO_ORGAO_EMISSOR_ID="1"
        ),
        False, True, "Falha: Número do documento não pode ser vazio"
    ),
    # Cenário 3: Validação de campo não selecionado. Ocorre no back-end.
    (
        dados_pessoa_validos,
        Pessoas.Documentos(
        P6_N_DOCUMENTO=fake.rg(), 
        P6_TIPO_DOCUMENTO_ID=None, 
        P6_UF_EXPEDIDOR_ID='23', 
        P6_TIPO_ORGAO_EMISSOR_ID="1"
        ),
        False, True, "Falha: Tipo de documento não selecionado"
    ),
    # Cenário 4: Validação de comprimento. Pode ser no front-end (maxlength), então não precisa salvar.
    (
        dados_pessoa_validos,
        Pessoas.Documentos(
        P6_N_DOCUMENTO=fake.pystr(min_chars=100, max_chars=120), 
        P6_TIPO_DOCUMENTO_ID="3", 
        P6_UF_EXPEDIDOR_ID='23', 
        P6_TIPO_ORGAO_EMISSOR_ID="1"
        ),
        False, False, "Falha: Número do documento com comprimento excessivo" # AJUSTE: Salvar = False é apropriado aqui.
    ),
    # Cenário 5: Tentativa de XSS. A validação real ocorre no back-end ao salvar.
    (
        dados_pessoa_validos,
        Pessoas.Documentos(
        P6_N_DOCUMENTO="<script>alert('XSS')</script>", 
        P6_TIPO_DOCUMENTO_ID="3", 
        P6_UF_EXPEDIDOR_ID='23', 
        P6_TIPO_ORGAO_EMISSOR_ID="1"
        ),
        False, True, "Falha: Tentativa de XSS no número do documento"
    ),
    # Cenário 6: Validação de espaços em branco. Ocorre no back-end.
    (
        dados_pessoa_validos,
        Pessoas.Documentos(
        P6_N_DOCUMENTO="      ", 
        P6_TIPO_DOCUMENTO_ID="3", 
        P6_UF_EXPEDIDOR_ID='23', 
        P6_TIPO_ORGAO_EMISSOR_ID="1"
        ),
        False, True, "Falha: Número do documento preenchido com espaços"
    ),
    # Cenário 7: Validação de duplicidade. Regra de negócio de back-end.
    (
        dados_pessoa_validos,
        Pessoas.Documentos(
        P6_N_DOCUMENTO=fake.rg(), 
        P6_TIPO_DOCUMENTO_ID="4", 
        P6_UF_EXPEDIDOR_ID='SP', 
        P6_TIPO_ORGAO_EMISSOR_ID="2"
        ),
        False, True, "Falha: Tentar cadastrar o mesmo tipo de documento duas vezes"
    ),
    # Cenário 8: UF inválida. Se for um campo de texto, a validação é no back-end.
    (
        dados_pessoa_validos,
        Pessoas.Documentos(
        P6_N_DOCUMENTO=fake.rg(), 
        P6_TIPO_DOCUMENTO_ID="3", 
        P6_UF_EXPEDIDOR_ID='95', 
        P6_TIPO_ORGAO_EMISSOR_ID="1"
        ),
        False, True, "Falha: UF do expedidor inválida" # AJUSTE: Salvar = True para testar a regra no servidor.
    ),
    # Cenário 9: Órgão emissor não selecionado. Validação de back-end.
    (
        dados_pessoa_validos,
        Pessoas.Documentos(
        P6_N_DOCUMENTO=fake.rg(), 
        P6_TIPO_DOCUMENTO_ID="3", 
        P6_UF_EXPEDIDOR_ID='23', 
        P6_TIPO_ORGAO_EMISSOR_ID=None
        ),
        False, True, "Falha: Órgão emissor não selecionado"
    ),
])
@pytest.mark.dockerCadastroPessoas
# ERRO CORRIGIDO: Ordem dos parâmetros na definição da função.
def test_insere_documento_pessoa(init, dadosPessoa, documentoPessoa, devePassar, salvar, cenario):
    starTime = time.time()
    browser, login, Log_manager, get_ambiente, env_vars, seletor_ambiente, selenium_exceptions, error_logger = init
    env_application_type = env_vars['APPLICATION_TYPE']
    rotina_log = f"{Pessoas.rotina} - test_insere_documento_pessoa"

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
            assert False, "Falha ao inserir os dados base da pessoa. O teste de documento não pode continuar."

        # A lógica de teste de duplicidade está correta.
        if "duas vezes" in cenario:
            Pessoas.insereDocumento(init=init, documentoPessoa=documentoPessoa, save=salvar)
            resultado_final = Pessoas.insereDocumento(init=init, documentoPessoa=documentoPessoa, save=salvar)
        else:
            resultado_final = Pessoas.insereDocumento(init=init, documentoPessoa=documentoPessoa, save=salvar)

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
            # ERRO CORRIGIDO: Lógica de asserção mais consistente.
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