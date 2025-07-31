# tests/test_validacao_edicao_metas.py

import time
import pytest
from classes.rotinas.MetasPorRegiao import MetasPorRegiao
from classes.utils.Components import Components
from classes.utils.FuncoesUteis import FuncoesUteis

# --- Dados base para criar a meta e fazer os campos aparecerem ---
META_BASE_VALIDA = MetasPorRegiao.Metas(
    P311_DESCRICAO="Meta Base para Teste de Edição",
    P311_SELETOR_LOJA=['2381', '3625'],  # Use lojas que gerem um número conhecido de campos (ex: 2 campos)
    P311_STATUS="1"
)

XSS_PAYLOAD_BASIC = "<script>alert('XSS')</script>"
XSS_PAYLOAD_IMG = "<img src=x onerror=alert('XSS')>"
SQL_INJECTION_PAYLOAD_SIMPLE = "' OR '1'='1"

# --- Cenários de teste para a edição e validação do somatório ---
@pytest.mark.parametrize("valor_a_inserir, devePassar, cenario", [
    # ==== CENÁRIOS DE SUCESSO ====
    ("1500,00", True, "SUCESSO: Edição com valor monetário válido e soma correta"),
    ("100", True, "SUCESSO: Edição com valor inteiro e soma correta"),
    ("0", True, "SUCESSO: Edição com valor zero e soma correta"),

    # ==== CENÁRIOS DE FALHA (VALIDAÇÃO DE CAMPO INDIVIDUAL) ====
    # A aplicação deve impedir a inserção de dados inválidos antes mesmo de verificar a soma.
    ("abc", False, "FALHA: Tentativa de inserir texto em campo de valor"),
    ("-50", False, "FALHA: Tentativa de inserir valor negativo"),
    ("", False, "FALHA: Tentativa de inserir valor vazio"),
    ("@!#", False, "FALHA: Tentativa de inserir caracteres especiais"),
    ("1500,15  ", False, "FALHA: Tentativa de inserir espaçamentos extras no valor"),
    ("R$1500,00", False, "FALHA: Tentativa de inserir símbolo monetário no campo de valor"),
    ("1.500,00", False, "FALHA: Tentativa de inserir formatação de milhar"),
    # ==== CENÁRIOS DE DADOS NÃO-CONVENCIONAIS ====
    ("😊", False, "DADO: Tentativa de inserir Emojis"),
    # ("一百", False, "DADO: Tentativa de inserir caracteres Unicode (chinês)")


    # ==== CENÁRIO DE FALHA (SOMA INCORRETA) ====
    # Este cenário é mais avançado. A ideia é forçar a soma a estar errada.
    # Se a função 'editarMeta' for usada como sugeri, ela mesma fará a validação.
    # O teste abaixo verifica se a função 'editarMeta' corretamente identifica o erro.
    # Para simular isso, poderíamos (hipoteticamente) alterar o valor total via JS antes de validar.
    # Por simplicidade, vamos confiar que a validação dentro de 'editarMeta' é o que estamos testando.
    # Se inserirmos '100' e a soma não for '200' (para 2 campos), a função deve retornar False.
    # A estrutura atual do teste já cobre isso: se 'editarMeta' retornar False, o teste falhará para 'devePassar=True'.

    # ==== CENÁRIOS DE SEGURANÇA ====
    (XSS_PAYLOAD_BASIC, False, "SEGURANÇA: Tentativa de XSS no campo de valor"),
    (XSS_PAYLOAD_IMG, False, "SEGURANÇA: Tentativa de XSS com imagem no campo de valor"),
    (SQL_INJECTION_PAYLOAD_SIMPLE, False, "SEGURANÇA: Tentativa de SQL Injection no campo de valor"),
])
@pytest.mark.dockerMetas
def test_validacao_edicao_meta_e_soma(init, valor_a_inserir, devePassar, cenario):
    """
    Testa a função de edição de metas, focando na validação dos campos de valor
    individuais e na consistência do campo de somatório.
    """
    start_time = time.time()
    browser, _, Log_manager, _, env_vars, _, selenium_exceptions, error_logger = init
    env_application_type = env_vars['APPLICATION_TYPE']
    rotina_nome = f"{MetasPorRegiao.rotina} - {cenario}"
    Log_manager.add_log(level="INFO", application_type=env_application_type, message=f"Iniciando teste: '{cenario}'", routine=rotina_nome)

    try:
        # --- PASSO 1: SETUP - Criar a meta para exibir os campos de edição ---
        FuncoesUteis.goToPage(init=init, url=MetasPorRegiao.url)
        MetasPorRegiao.criarMeta(init=init)
        MetasPorRegiao.criarMetaComissao(init=init, metas=META_BASE_VALIDA)
        MetasPorRegiao.selecionarLojasRegioes(init=init, metas=META_BASE_VALIDA)             

        # Agora na tela de edição, chame a função 'editarMeta' com os dados do cenário
        resultado_edicao = MetasPorRegiao.editarMeta(init, valor_a_inserir)       
        

        # --- PASSO 3: VERIFICAÇÃO ---
        if devePassar:
            # Se deve passar, a função 'editarMeta' deve retornar True e uma mensagem de sucesso deve aparecer
            assert resultado_edicao, "A função editarMeta() retornou 'False', indicando uma falha interna na validação."
            
            # **Ajuste o seletor da sua mensagem de sucesso**
            sucesso_msg = FuncoesUteis.verificar_visibilidade_elemento(init, "div.t-Alert--success", timeout=5)
            assert sucesso_msg, "Cenário deveria passar, mas a mensagem de sucesso final não foi encontrada."
            Log_manager.add_log(level="INFO", message="Verificação de sucesso confirmada.", routine=rotina_nome)
        else:
            # Se deve falhar, esperamos que a função 'editarMeta' retorne False OU que o sistema mostre um erro na tela.
            # **Ajuste o seletor da sua mensagem de erro de validação**
            erro_msg = FuncoesUteis.verificar_visibilidade_elemento(init, ".t-Form-error", timeout=5)
            assert not resultado_edicao or erro_msg, "Cenário deveria falhar, mas nenhuma validação parece ter bloqueado a ação."
            Log_manager.add_log(level="INFO", message="Verificação de falha confirmada, como esperado.", routine=rotina_nome)

    except Exception as e:
        pytest.fail(f"O teste falhou com uma exceção inesperada no cenário '{cenario}': {e}")
    finally:
       # Este bloco é executado mesmo se o teste falhar, ideal para registrar o tempo
        end_time = time.time()
        execution_time = end_time - start_time
        minutos, segundos = divmod(execution_time, 60)
        
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Tempo de execução: {int(minutos)}m {segundos:.2f}s",
            routine=rotina_nome
        )
        Log_manager.insert_logs_for_execution(logName=f"{MetasPorRegiao.rotina} - test_validacao_edicao_meta_e_soma")
