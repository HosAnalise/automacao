from classes.rotinasDesktop.Home import Home
from classes.rotinasDesktop.GerenciadorNotasNfe import GerenciadorNotasNfe
import pytest

@pytest.mark.dockerDesktopGerenciadorNotas
@pytest.mark.parametrize("nota, deve_passar", [
    (
        GerenciadorNotasNfe.NotasFiscais(
            DtInicial="01/04/2025",
            CboMostrarVendas="SIM",
        ), True
    ),
    (
        GerenciadorNotasNfe.NotasFiscais(
            DtInicial="banana",
            DtFinal="banana",
            TxtSerie="banana",
            txtEmpresas="banana",
            TxtNrInicial="banana",
            TxtNrFinal="banana",
            TxtCupom="banana",
            txtDestinatarios="banana",
            CboStatus="banana",
            CboMostrarVendas=10,
            TxtNatureza="banana"
        ), False
    ),
])
def test_filtragem_nota(app, login, env_vars, getQueryResults, log_manager, nota, deve_passar):
    home = None
    try:
        home = Home(app, env_vars, log_manager)
        home.wait_for_home()

        gerenciador = GerenciadorNotasNfe(app, env_vars, getQueryResults, log_manager)
        gerenciador.caminho_gerenciar_nota_via_barra_pesquisa()
        home.autenticar()

        try:
            resultado = gerenciador.filtrar_notas_fiscais(obj=nota)

            if deve_passar:
                assert resultado is True, "Esperado sucesso na filtragem, mas ela falhou."
            else:
                assert resultado is False, "Filtragem passou com dados inválidos, o que não era esperado."

        except home.exceptions as e:
            if deve_passar:
                home.log.add_log(
                    application_type=home.application_type,
                    level="ERROR",
                    message="Erro inesperado ao aplicar filtro com dados válidos.",
                    routine="GerenciadorNotasNfe",
                    error_details=str(e)
                )
                raise  # Repassa erro porque não deveria acontecer
            else:
                log_manager.add_log(
                    application_type=gerenciador.application_type,
                    level="INFO",
                    message="Erro esperado ao tentar aplicar filtro com dados inválidos.",
                    routine="GerenciadorNotasNfe",
                    error_details=str(e)
                )
                assert True  # erro era esperado, teste passa

    finally:
        if home:
            home.log.insert_logs_for_execution(logName="GerenciadorNotasNfe")
        else:
            log_manager.insert_logs_for_execution(logName="GerenciadorNotasNfe")
