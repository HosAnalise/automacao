from classes.rotinasDesktop.Home import Home
from classes.rotinasDesktop.CadastroCliente import CadastroCliente
from classes.rotinasDesktop.GerenciadorNotasNfe import GerenciadorNotasNfe
import pytest


@pytest.mark.parametrize("info_nota, deve_passar", [
    (
        GerenciadorNotasNfe.InfoNotas(
           CboFinalidadeNFE="COMPLEMENTAR",
           TxtNumeroFatura=100,
           DtMovimentacao="05/05/2025",
           DtEmissao="05/05/2025",

        ), True
    ),
    (
        GerenciadorNotasNfe.InfoNotas(
            CboFinalidadeNFE="Não existe",
            TxtNumeroFatura=100,
            DtMovimentacao="05/05/an",
            DtEmissao="05/05/2026",
        ), False
    ),
])
def test_edita_nota(app,login, env_vars, getQueryResults, log_manager, info_nota, deve_passar):
    home = None
    home = Home(app, env_vars, log_manager)
    home.wait_for_home()
    nota_editada = False


    nota = GerenciadorNotasNfe.NotasFiscais(
            DtInicial="01/03/2025",
            CboStatus="PENDENTE",
            CboMostrarVendas="SIM",
            
        )

    gerenciador = GerenciadorNotasNfe(app, env_vars, getQueryResults, log_manager)
    gerenciador.caminho_gerenciar_nota_via_barra_pesquisa()
    home.autenticar()    

    try:
        resultado = gerenciador.filtrar_notas_fiscais(obj=nota)

        if resultado:
            # click_linha = gerenciador.abre_editar_nota_por_cupom(cupom=54)
            click_check = gerenciador.clica_primeiro_checkbox_na_listagem()
            
            if click_check:
                editar = gerenciador.abre_editar_nota()
                if editar:
                    janela = gerenciador.procura_janela_edicao_nota()  
                    
                    if janela:
                        nota_editada = gerenciador.editar_nota_cabecalho_info_nota(obj=info_nota)
                    

        if deve_passar:
            assert nota_editada is True, "Edição falhou inesperadamente com dados válidos."
        else:
            assert nota_editada is False, "Edição passou com dados inválidos, o que não era esperado."


    except home.exceptions as e:
        if deve_passar:
            home.log.add_log(
                application_type=home.application_type,
                level="ERROR",
                message="Erro inesperado ao aplicar filtro",
                routine="GerenciadorNotasNfe",
                error_details=str(e)
            )
            raise  # erro real
        else:
            log_manager.add_log(
                application_type=gerenciador.application_type,
                level="INFO",
                message="Erro esperado ao tentar aplicar filtro com dados inválidos",
                routine="GerenciadorNotasNfe",
                error_details=str(e)
            )
    finally:    
        if home:
            home.log.insert_logs_for_execution(logName="GerenciadorNotasNfe")
        else:
            log_manager.insert_logs_for_execution(logName="GerenciadorNotasNfe") 