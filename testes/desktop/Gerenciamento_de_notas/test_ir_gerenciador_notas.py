from classes.rotinasDesktop.Home import Home
from classes.rotinasDesktop.GerenciadorNotasNfe import GerenciadorNotasNfe
import pytest


@pytest.mark.dockerDesktopGerenciadorNotas
def test_ir_gerenciador_notas(app,login, env_vars, getQueryResults, log_manager):
    try:
        home = Home(app, env_vars, log_manager)
        home.wait_for_home()

        gerenciador = GerenciadorNotasNfe(app, env_vars, getQueryResults, log_manager)
        caminho = gerenciador.caminho_gerenciar_nota_via_barra_pesquisa()


        if caminho:
            home.log.add_log(
                    application_type=home.application_type,
                    level="INFO",
                    message="A navegação para o Gerenciador de Notas Nfe foi bem-sucedida.",
                    routine="GerenciadorNotasNfe",
                    error_details=""
                )
        else:
            home.log.add_log(
                    application_type=home.application_type,
                    level="ERROR",
                    message="A navegação para o Gerenciador de Notas Nfe falhou.",
                    routine="GerenciadorNotasNfe",
                    error_details=""
                )   
    finally:
        home.log.insert_logs_for_execution(logName="GerenciadorNotasNfe")        



