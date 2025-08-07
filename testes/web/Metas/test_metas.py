from classes.rotinas.MetasPorRegiao import MetasPorRegiao
from classes.utils.Components import Components
from classes.utils.FuncoesUteis import FuncoesUteis
import pytest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.parametrize("meta_data, devePassar, valor_metas_lojas, cenario", [
    # ==== CENÁRIOS DE SUCESSO ====
    (
        MetasPorRegiao.Metas(
            P311_DESCRICAO="Meta Teste Válida (Ativa)",
            P311_SELETOR_LOJA=["2381", "3625"],
            P311_STATUS="1" # 1 = Ativo
        ), True, 10, "Criação de meta com status ativo e lojas selecionadas - Criação com sucesso"
    )
])
def test_metas(init, meta_data, devePassar, valor_metas_lojas, cenario):

    _, _, Log_manager, _, env_vars, _, selenium_exceptions, error_logger = init

    env_application_type = env_vars['APPLICATION_TYPE']

    Log_manager.add_log(level="INFO", application_type=env_application_type, message=f"Iniciando teste: '{cenario}'", routine="")

    try:
        # --- PASSO 1: TENTATIVA DE CRIAÇÃO (COMUM A TODOS OS CENÁRIOS) ---
        FuncoesUteis.goToPage(init=init, url=MetasPorRegiao.url)
        MetasPorRegiao.criarMeta(init=init)

        # A função criarMetaComissao retorna False em caso de erro de preenchimento
        resultado_criacao = MetasPorRegiao.criarMetaComissao(init=init, meta=meta_data)
        logger.info(f"Resultado da criação: {resultado_criacao}")



        if devePassar:
            # Para cenários de sucesso, esperamos que a criação tenha funcionado
            assert resultado_criacao, "A etapa de criação da meta falhou inesperadamente."
    except selenium_exceptions as e:
        Log_manager.add_log(level="ERROR", application_type=env_application_type, message=f"Erro ao criar meta: {str(e)}", routine="")
        assert False, "Erro inesperado durante o teste."

    finally:
        Log_manager.insert_logs_for_execution(logName=f"{MetasPorRegiao.rotina} - test_criar_e_editar_meta_por_regiao")
    