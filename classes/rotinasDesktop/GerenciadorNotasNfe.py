
from classes.rotinasDesktop.Home import Home
from pydantic import BaseModel
from pywinauto.controls.uia_controls import ButtonWrapper
from pywinauto.uia_defines import toggle_state_on, toggle_state_off
from typing import Optional
from pywinauto.keyboard import send_keys






class GerenciadorNotasNfe(Home):

    def __init__(self, app, env_vars,getQueryResults,log_manager):
        # Chama o construtor da classe Home (superclasse)
        super().__init__(app, env_vars, log_manager)

        password = env_vars.get("PASSWORD")
        user = env_vars.get("USER")
        
        # Atributos específicos de GerenciadorNotasNfe
        self.user = password
        self.password = user
        self.nfe_window = self.app.window(title_re=".*Notas.*")
        self.encontrar_janela_aviso = self.app.window(title_re=".*HOSFarma - Aviso.*")
        self.edicao_nota_window = self.app.window(title_re=".*Edição de Notas*",control_type="Window")
        self.getQueryResults = getQueryResults


    class NotasFiscais(BaseModel):
        """
        Classe para representar as notas fiscais.
        """
        DtInicial:  Optional[str | int] = None
        DtFinal:  Optional[str | int] = None
        TxtSerie:  Optional[str | int] = None
        txtEmpresas:  Optional[str | int] = None
        TxtNrInicial:  Optional[str | int] = None
        TxtNrFinal:  Optional[str | int] = None
        TxtCupom:  Optional[str | int] = None
        txtDestinatarios:  Optional[str | int] = None
        CboStatus:  Optional[str | int] = None
        CboMostrarVendas:  Optional[str | int] = None
        TxtNatureza: Optional[str | int] = None

    def caminho_gerenciar_nota(self):
        """
        Vai até a janela de gerenciamento de notas fiscais.
        """
        try:
            # Acessa o menu usando o método da classe pai (Home)
            self.clickMenu(menu_name="Estoque")
            
            self.farma_window.child_window(auto_id="Notas Fiscais de Saída", control_type="Button").wait("exists enabled visible ready", timeout=30).click()
            self.log.add_log(
                application_type=self.application_type,
                level="INFO",
                message="Menu Notas fiscais de Saída encontrado",
                routine="GerenciadorNotasNfe",
                error_details=""
            )
            
            self.farma_window.child_window(auto_id="", control_type="Button").wait("exists enabled visible ready", timeout=30).click()
            self.log.add_log(
                application_type=self.application_type,
                level="INFO",
                message="Menu Gerenciar NFE encontrado",
                routine="GerenciadorNotasNfe",
                error_details=""
            )

        except self.exceptions as e:
           self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Gerenciador de notas fiscais não encontrado",
                routine="GerenciadorNotasNfe",
                error_details=""
            )

    def caminho_gerenciar_nota_via_barra_pesquisa(self) -> bool:
        """
        Vai até a janela de gerenciamento de notas fiscais.
        """
        try:
            # Acessa o menu usando o método da classe pai (Home)
            self.searchBar(search_text="gerenciador nfe")
            self.log.add_log(
                application_type=self.application_type,
                level="INFO",
                message="Barra de pesquisa encontada",
                routine="GerenciadorNotasNfe",
                error_details=""
            )       
                        
            self.farma_window.child_window(auto_id="Gerenciador NFE", control_type="Button")\
                .wait("exists enabled visible ready", timeout=30).click()
            self.log.add_log(
                application_type=self.application_type,
                level="INFO",
                message="Menu Gerenciar NFE encontrado",
                routine="GerenciadorNotasNfe",
                error_details=""
            )
            return True

        except self.exceptions as e:
           self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Barra de pesquisa não encontrada",
                routine="GerenciadorNotasNfe",
                error_details=str(e)
            )
           return False
                

    def filtrar_notas_fiscais(self, obj: NotasFiscais) -> bool:
        """
        Realiza o filtro de notas fiscais.

        :param obj: Instância de NotasFiscais com os dados de filtro.
        :return: True se filtro for aplicado com sucesso, False em caso de erro.
        """
        try:
            self.nfe_window.wait("exists enabled visible ready", timeout=60)

            textboxes = self.nfe_window.descendants(control_type="Edit", class_name="TextBox")
    
            if len(textboxes) > 8:  # índice 8, pois lista começa no 0
                valor_inicial =  textboxes[9].window_text()
                self.log.add_log(
                    application_type=self.application_type,
                    level="INFO",
                    message=f"Valor inicial encontrado: {valor_inicial}",
                    routine="GerenciadorNotasNfe",
                    error_details=''
                )
                
               
            else:
                self.log.add_log(
                    application_type=self.application_type,
                    level="ERROR",
                    message="TextBox 9 não encontrado. Menos de 9 campos disponíveis.",
                    routine="GerenciadorNotasNfe",
                    error_details=f"Total encontrado: {len(textboxes)}"
                )


            for field_name, value in obj.model_dump().items():
                if value in [None, ""]:
                    continue  # ignora campos vazios

                if "Cbo" in field_name:
                    control_type = "ComboBox"
                elif "Dt" in field_name:
                    control_type = "Custom"
                else:
                    control_type = "Edit"

                element = self.nfe_window.child_window(auto_id=field_name, control_type=control_type)\
                                        .wait("exists enabled visible ready", timeout=30)

                try:
                    if control_type == "ComboBox":
                        opcoes_disponiveis = element.texts()
                        if value in opcoes_disponiveis:
                            element.select(value)
                            valor_elemento = element.get_selection()
                        else:
                            self.log.add_log(
                                    application_type=self.application_type,
                                    level="INFO",
                                    message=f"Valor '{value}' não encontrado nas opções do ComboBox '{field_name}': {opcoes_disponiveis}",
                                    routine="GerenciadorNotasNfe",
                                    error_details=""
                            )


                    else :
                        element.click_input()
                        element.type_keys(value, with_spaces=True)
                        valor_elemento = element.window_text()
                    

                    self.log.add_log(
                        application_type=self.application_type,
                        level="INFO",
                        message=f"Filtro '{field_name}' aplicado com valor '{valor_elemento}'",
                        routine="GerenciadorNotasNfe",
                        error_details=""
                    )

                except self.exceptions as e:
                    self.log.add_log(
                        application_type=self.application_type,
                        level="ERROR",
                        message=f"Erro ao aplicar filtro em '{field_name}'",
                        routine="GerenciadorNotasNfe",
                        error_details=str(e)
                    )
                    return False  # erro ao aplicar o filtro

            # Clica no botão "Pesquisar"
            for btn in self.nfe_window.descendants(control_type="Button"):
                try:
                    if any("Pesquisar" in child.window_text() for child in btn.children()):
                        ButtonWrapper(btn.element_info).click_input()
                        self.log.add_log(
                            application_type=self.application_type,
                            level="INFO",
                            message="Botão 'Pesquisar' clicado com sucesso",
                            routine="GerenciadorNotasNfe",
                            error_details=""
                        )

                        textboxes = self.nfe_window.descendants(control_type="Edit", class_name="TextBox")
                        if len(textboxes) > 8:  # índice 8, pois lista começa no 0
                            valor_final =  textboxes[9].window_text()
                            self.log.add_log(
                                application_type=self.application_type,
                                level="INFO",
                                message=f"Valor Final encontrado: {valor_final}",
                                routine="GerenciadorNotasNfe",
                                error_details=f"Total encontrado: {len(textboxes)}"
                            )

                            if valor_inicial == valor_final:
                                self.log.add_log(
                                    application_type=self.application_type,
                                    level="INFO",
                                    message=f"Quantidade de registros encontrados após aplicar o filtro: {valor_final}",
                                    routine="GerenciadorNotasNfe",
                                    error_details=""
                                )
                                return False
                            else:
                                self.log.add_log(
                                    application_type=self.application_type,
                                    level="INFO",
                                    message=f"Quantidade de registros encontrados após aplicar o filtro: {valor_final}",
                                    routine="GerenciadorNotasNfe",
                                    error_details=""
                                )
                                return True

                except self.exceptions as e:

                    self.log.add_log(
                        application_type=self.application_type,
                        level="ERROR",
                        message="Botão 'Pesquisar' não encontrado",
                        routine="GerenciadorNotasNfe",
                        error_details=""
                    )
                    return False
                


            
           
        except self.exceptions as e:
            self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Erro ao aplicar filtros",
                routine="GerenciadorNotasNfe",
                error_details=str(e)
            )
            return False


    def filtro_retorna_valores(self) -> bool:
        """
        Verifica se existe ao menos uma linha com class_name 'DataGridRow' visível na tela.

        :return: True se encontrar, False caso contrário.
        """
        try:
           
            linhas = self.nfe_window.descendants(class_name="DataGridRow")\
                .wait("exists enabled visible ready", timeout=30)

            for linha in linhas:
                if linha.is_visible():
                    self.log.add_log(
                        application_type=self.application_type,
                        level="INFO",
                        message="Linha visível com class_name='DataGridRow' encontrada.",
                        routine="GerenciadorNotasNfe",
                        error_details=""
                    )
                    return True
                
                else:
                    self.log.add_log(
                        application_type=self.application_type,
                        level="WARNING",
                        message="Nenhuma linha visível com class_name='DataGridRow' encontrada.",
                        routine="GerenciadorNotasNfe",
                        error_details=""
                    )
                    return False

        except self.exceptions as e:
            self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Erro ao buscar linhas com class_name='DataGridRow'.",
                routine="GerenciadorNotasNfe",
                error_details=repr(e)
            )
            return False

    def aviso_janela(self) -> bool:
        try:
            aviso_window = self.app.window(title_re=".*HOSFarma - Aviso.*")\
                .wait("exists enabled visible ready", timeout=30)
            
            btn = aviso_window.child_window(auto_id="Btn1", control_type="Button")\
                .wait("exists enabled visible ready", timeout=30)

            self.log.add_log(
                application_type=self.application_type,
                level="INFO",
                message="Janela de aviso encontrada.",
                routine="GerenciadorNotasNfe",
                error_details=""
            )
            btn.click_input()
            return True


        except self.exceptions as e:
            self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Janela de aviso não encontrada.",
                routine="GerenciadorNotasNfe",
                error_details=str(e)
            )
            return False
        

      


    def clica_primeiro_checkbox_na_listagem(self) -> bool:
        """
        Clica no primeiro checkbox encontrado na listagem de notas fiscais (DataGrid).

        :return: True se a checkbox for clicada com sucesso, False em caso de erro.
        """
        try:
            # Localiza o DataGrid pelo AutomationId
            data_grid = self.nfe_window.child_window(auto_id="DgNotas", control_type="DataGrid")

            # Aguarda ele estar pronto
            data_grid.wait("exists enabled visible ready", timeout=15)

            # Acha todas as linhas (itens de dados)
            linhas = data_grid.children(control_type="DataItem")

            if not linhas:
                self.log.add_log(
                    application_type=self.application_type,
                    level="ERRO",
                    message="Nenhuma linha encontrada no DataGrid.",
                    routine="GerenciadorNotasNfe",
                    error_details=""
                )
                return False

            primeira_linha = linhas[0]

            # Procura checkbox dentro da primeira linha
            checkbox = next(
                (
                    cb for cb in primeira_linha.descendants(control_type="CheckBox")
                    if cb.is_enabled() and cb.is_visible()
                ),
                None
            )

            if checkbox:
                checkbox.toggle()
                self.log.add_log(
                    application_type=self.application_type,
                    level="INFO",
                    message="Checkbox da primeira linha clicada com sucesso.",
                    routine="GerenciadorNotasNfe",
                    error_details=""
                )
                return True
            else:
                self.log.add_log(
                    application_type=self.application_type,
                    level="ERRO",
                    message="Nenhum checkbox encontrado na primeira linha do DataGrid.",
                    routine="GerenciadorNotasNfe",
                    error_details=""
                )
                return False

        except Exception as e:
            self.log.add_log(
                application_type=self.application_type,
                level="ERRO",
                message="Erro ao tentar clicar na checkbox da primeira linha.",
                routine="GerenciadorNotasNfe",
                error_details=str(e)
            )
            return False

        

  

    def abre_editar_nota_por_cupom(self, cupom: str) -> bool:
        """
        Encontra no grid a linha cujo valor da coluna 'Cupom' seja igual a cupom,
        seleciona-a e dá duplo-clique para abrir.

        :param cupom: clica a linha do cupom selecionado 
        """
        try:
            # Pega o DataGrid
            grid = self.nfe_window.child_window(control_type="DataGrid").wrapper_object()
        except self.exceptions:
            self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Grid de notas não encontrado.",
                routine="GerenciadorNotasNfe",
                error_details=""
            )
            return False

        try:
            # Filtra apenas os DataItems (linhas de dados) — ignora headers e footers
            rows = self.nfe_window.descendants(control_type="DataItem")
        except Exception as e:
            self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Falha ao listar linhas do grid.",
                routine="GerenciadorNotasNfe",
                error_details=str(e)
            )
            return False

        for elem in rows:
            try:
                row = elem.wrapper_object()  # agora é sempre um UIAWrapper válido
                # window_text() traz todas as células separadas por "\r\n"
                texts = row.window_text().split("\r\n")
            except Exception:
                # se não puder embrulhar, pula
                continue

            if cupom and cupom in texts:
                try:
                    row.scroll_into_view()
                    row.select()
                    row.double_click_input()
                    self.log.add_log(
                        application_type=self.application_type,
                        level="INFO",
                        message=f"Linha com cupom '{cupom}' aberta com sucesso.",
                        routine="GerenciadorNotasNfe",
                        error_details=""
                    )
                    return True
                except Exception as e:
                    self.log.add_log(
                        application_type=self.application_type,
                        level="ERROR",
                        message="Erro ao interagir com a linha encontrada.",
                        routine="GerenciadorNotasNfe",
                        error_details=str(e)
                    )
                    return False

        # se não achou nenhuma com aquele cupom
        self.log.add_log(
            application_type=self.application_type,
            level="ERROR",
            message=f"Nenhuma linha com cupom '{cupom}' foi encontrada.",
            routine="GerenciadorNotasNfe",
            error_details=""
        )
        return False

    def abre_editar_nota(self) -> bool:
        """
        Clica no botão 'Editar' e aguarda a abertura da janela de edição.
        :return: True se a janela de edição for aberta com sucesso, False em caso de erro.
        """
        try:    
            # Clica no botão "Editar"
            for btn in self.nfe_window.descendants(control_type="Button"):
                try:
                    if any("Editar" in child.window_text() for child in btn.children()):
                        ButtonWrapper(btn.element_info).click()
                        self.log.add_log(
                            application_type=self.application_type,
                            level="INFO",
                            message="Botão 'Editar' clicado com sucesso",
                            routine="GerenciadorNotasNfe",
                            error_details=""
                        )
                        return True  # Sai do loop após clicar no botão

                except self.exceptions as e:
                    self.log.add_log(
                        application_type=self.application_type,
                        level="ERROR",
                        message="Botão 'Editar' não encontrado ou erro ao clicar",
                        routine="GerenciadorNotasNfe",
                        error_details=str(e)
                    )
                    return False

           

        except self.exceptions as e:
            self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Erro ao tentar editar nota",
                routine="GerenciadorNotasNfe",
                error_details=str(e)
            )
            return False
        

    def procura_janela_edicao_nota(self) -> bool:
        """
        Aguarda a janela de edição de nota aparecer.
        :return: True se a janela for encontrada, False em caso de erro.
        """
        try:
            # Reatribui a janela na hora, para garantir que ela exista no momento da chamada
            self.edicao_nota_window = self.app.window(title_re=".*Edição de Notas.*")

            self.edicao_nota_window.wait("exists enabled visible ready", timeout=30)

            self.log.add_log(
                application_type=self.application_type,
                level="INFO",
                message="Janela de edição de nota encontrada.",
                routine="GerenciadorNotasNfe",
                error_details=""
            )
            return True

        except Exception as e:  # Usa Exception se `self.exceptions` não estiver definido corretamente
            self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Janela de edição de nota não encontrada.",
                routine="GerenciadorNotasNfe",
                error_details=str(e)
            )
            return False

        

    def quantas_janelas(self) -> int:
        # Obtém todas as janelas principais da aplicação
        matches = self.app.windows(title_re=".*Notas.*")  # Melhor usar `windows()` ao invés de `window.children()`
        
        # Lista os elementos encontrados
        for i, match in enumerate(matches):
            print(f"Elemento {i}: {match.window_text()} - {match.element_info.control_type}")
        
        return len(matches)
    
    
        
    #### inicio dos metodos relacionado ao cabeçalho    
    class InfoNotas(BaseModel):
        """
        Armazena os auto IDs de todos os campos relacionados às informações da nota fiscal na tela de edição de notas.
        """
        TxtNumeroNota: Optional[str | int] = None
        TxtNaturezaOperacao: Optional[str | int] = None
        CboFinalidadeNFE: Optional[str | int] = None
        TxtNumeroFatura: Optional[str | int] = None
        DtMovimentacao: Optional[str | int] = None
        DtEmissao: Optional[str | int] = None
        HoraMov: Optional[str | int] = None
        HoraEmiss: Optional[str | int] = None
        CboTipoFrete: Optional[str | int] = None
        TxtTransportadora: Optional[str | int] = None
        CboVeiculo: Optional[str | int] = None
        TxtNrOrdemCompras: Optional[str | int] = None

    def editar_nota_cabecalho_info_nota(self, obj: InfoNotas) -> bool:
        """
        Preenche os campos de cabeçalho da nota em edição com base no objeto InfoNotas.
        
        :param obj: Instância com os dados da nota.
        :return: True se sucesso, False em caso de erro.
        """
        try:
            janela = self.procura_janela_edicao_nota()

            if not janela:
                return False

            sucesso_total = True  # Flag para monitorar sucesso geral

            for field_name, value in obj.model_dump().items():
                if value in [None, ""]:
                    continue  # ignora campos vazios

                if "Hora" in field_name:
                    try:
                        edits = self.edicao_nota_window.descendants(control_type="Edit", class_name="TextBox")
                        for edit in edits:
                            previous_elem = edit.get_previous_sibling()
                            if previous_elem.window_text() in ["Hora Emissão", "Hora Mov."]:
                                campo_hora = edit.wrapper_object()
                                campo_hora.set_text(value)
                                self.log.add_log(
                                    application_type=self.application_type,
                                    level="INFO",
                                    message=f"Campo '{previous_elem.window_text()}' preenchido com '{value}'",
                                    routine="GerenciadorNotasNfe",
                                    error_details=""
                                )
                                break  # Continua com os demais campos
                    except self.exceptions as e:
                        self.log.add_log(
                            application_type=self.application_type,
                            level="ERROR",
                            message=f"Erro ao preencher campo de hora '{field_name}'",
                            routine="GerenciadorNotasNfe",
                            error_details=str(e)
                        )
                        sucesso_total = False
                    continue

                # Define tipo de controle
                if "Cbo" in field_name:
                    control_type = "ComboBox"
                elif "Dt" in field_name:
                    control_type = "Custom"
                else:
                    control_type = "Edit"

                try:
                    element = self.edicao_nota_window.child_window(
                        auto_id=field_name,
                        control_type=control_type
                    ).wait("exists enabled visible ready", timeout=30)

                    if control_type == "ComboBox":
                        element.select(value)
                    elif control_type == "Custom":
                        element.click_input()
                        element.type_keys(value, with_spaces=True)
                    else:
                        element.set_text(value)

                    self.log.add_log(
                        application_type=self.application_type,
                        level="INFO",
                        message=f"Campo '{field_name}' preenchido com '{value}'",
                        routine="GerenciadorNotasNfe",
                        error_details=""
                    )

                except self.exceptions as e:
                    self.log.add_log(
                        application_type=self.application_type,
                        level="ERROR",
                        message=f"Erro ao preencher campo '{field_name}'",
                        routine="GerenciadorNotasNfe",
                        error_details=str(e)
                    )
                    sucesso_total = False

            return sucesso_total

        except Exception as e:
            self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Erro inesperado ao preencher campos da nota",
                routine="GerenciadorNotasNfe",
                error_details=str(e)
            )
            return False



    class DadosDestino(BaseModel):
        """
        Armazena os auto IDs de todos os campos de dados do destinatário na janela de edição de notas.
        
        """
        txtDestinatarios: Optional[str | int] = None
        TxtCnpjCpf: Optional[str | int] = None
        TxtIEDocIdEstrangeiro: Optional[str | int] = None
        CboConsumidorFinal: Optional[str | int] = None
        txtCEP: Optional[str | int] = None #Se passar valor do  txtCEP não é necessario passar TxtLogradouro,TxtBairro,CboPais,CboUF,CboCidade
        TxtLogradouro: Optional[str | int] = None
        TxtNumeroEndereco: Optional[str | int] = None
        TxtBairro: Optional[str | int] = None
        CboContribuinteICMS: Optional[str | int] = None
        CboPais: Optional[str | int] = None
        CboUF: Optional[str | int] = None
        CboCidade: Optional[str | int] = None
        TxtComplemento: Optional[str | int] = None
        TxtTelefone: Optional[str | int] = None
        TxtCelular: Optional[str | int] = None

    def editar_nota_cabecalho_dados_destinatario(self,obj:DadosDestino)->bool:
        """
        Preenche os campos de cabeçalho da nota em edição com base no objeto DadosDestino.
        
        :param obj: Instância com os dados do destinatario.
        :return: True se sucesso, False em caso de erro.
        """


        def selecionar_destinatario(self, valor):
            btn = self.nfe_window.child_window(auto_id="__btnSearch", control_type="Button")\
                                .wait("exists enabled visible ready", timeout=30)
            btn.click()

            selecao_window = self.app.window(title="Seleção de Dados - Destinatários")
            destinatario = selecao_window.child_window(title=valor, control_type="Text")\
                                .wait("exists enabled visible ready", timeout=30)
            destinatario.parent().double_click_input()


        try:
            campos_ignorar = [ "TxtLogradouro","TxtBairro","CboPais","CboUF","CboCidade"]  

            for field_name, value in obj.model_dump().items():
                if value in [None, ""]:
                    continue  # ignora campos vazios
                if field_name == "txtCEP" and value not in [None, ""]:
                    if field_name in campos_ignorar:
                        continue  # pula a adição desse campo

                # Trata os outros campos normalmente
                if "Cbo" in field_name:
                    control_type = "ComboBox"
                else:
                    control_type = "Edit"

                try:
                    element = self.nfe_window.child_window(auto_id=field_name, control_type=control_type)\
                                            .wait("exists enabled visible ready", timeout=30)

                    if control_type == "ComboBox":
                        element.select(value)

                    elif control_type == "Edit" and field_name == "txtDestinatarios":
                        element.set_text(value)
                        selecionar_destinatario(value)
                    elif control_type == "Edit" and field_name == "txtCEP":
                        element.set_text(value)
                        send_keys("{~}")
                    else:
                        element.set_text(value)

                    self.log.add_log(
                        application_type=self.application_type,
                        level="INFO",
                        message=f"Campo '{field_name}' preenchido com '{value}'",
                        routine="GerenciadorNotasNfe",
                        error_details=""
                    )

                except self.exceptions as e:
                    self.log.add_log(
                        application_type=self.application_type,
                        level="ERROR",
                        message=f"Erro ao preencher campo '{field_name}'",
                        routine="GerenciadorNotasNfe",
                        error_details=str(e)
                    )
                    return False

            return True  # Tudo OK

        except self.exceptions as e:
            self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Erro inesperado ao preencher campos Dados do destinatario",
                routine="GerenciadorNotasNfe",
                error_details=str(e)
            )
            return False
        
    class Partilha(BaseModel):
        """
        Armazena os auto IDs de todos os campos de Partilha na janela de edição de notas.
        
        """
        TxtIcmsUfDestino: Optional[str | int] = None
        TxtICMSUfEmitente: Optional[str | int] = None
        TxtPartilhaFcb: Optional[str | int] = None
        TogDentro: Optional[str | int] = None
        TogFora: Optional[str | int] = None



    def editar_nota_cabecalho_partilha(self,obj:Partilha)->bool:
        """
        Preenche os campos de cabeçalho da nota em edição com base no objeto Partilha.
        
        :param obj: Instância com os dados do destinatario.
        :return: True se sucesso, False em caso de erro.
        """
        try:
            for field_name, value in obj.model_dump().items():
                if value in [None, ""]:
                    continue  # ignora campos vazios
                # Trata os outros campos normalmente
                control_type = "Button" if "Tog" in field_name else "Edit"

                try:
                    element = self.nfe_window.child_window(auto_id=field_name, control_type=control_type)\
                                            .wait("exists enabled visible ready", timeout=30)

                    if control_type == "Button" and value:
                        toggle_state = element.get_toggle_state()
                        if  toggle_state == toggle_state_on:
                            continue
                        if toggle_state == toggle_state_off:
                            element.click()
                        else:
                            self.log.add_log(
                                application_type=self.application_type,
                                level="ERROR",
                                message=f"Campo '{field_name}' está em estado de alternância indefinido (valor: {toggle_state})",
                                routine="GerenciadorNotasNfe",
                                error_details=""
                            )

                    else:
                        element.set_text(value)

                    self.log.add_log(
                        application_type=self.application_type,
                        level="INFO",
                        message=f"Campo '{field_name}' preenchido com '{value}'",
                        routine="GerenciadorNotasNfe",
                        error_details=""
                    )

                except self.exceptions as e:
                    self.log.add_log(
                        application_type=self.application_type,
                        level="ERROR",
                        message=f"Erro ao preencher campo '{field_name}'",
                        routine="GerenciadorNotasNfe",
                        error_details=str(e)
                    )
                    return False

            return True  # Tudo OK

        except self.exceptions as e:
            self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Erro inesperado ao preencher campos Partilha",
                routine="GerenciadorNotasNfe",
                error_details=str(e)
            )
            return False    
    
    
    class Intermediador(BaseModel):
        """
        Armazena os auto IDs de todos os campos de Intermediador na janela de edição de notas.
        """
        TxtCnpjIntermediador: Optional[str | int] = None
        TxtUsuarioIntermediador: Optional[str | int] = None
        
    def editar_nota_cabecalho_intermediador(self,obj:Intermediador)->bool:
        """
        Preenche os campos de cabeçalho da nota em edição com base no objeto intermediador.
        
        :param obj: Instância com os dados do destinatario.
        :return: True se sucesso, False em caso de erro.
        """
        try:
            for field_name, value in obj.model_dump().items():

                # ignora campos vazios
                if value in [None, ""]:
                    continue                  

                try:
                    element = self.nfe_window.child_window(auto_id=field_name, control_type="Edit")\
                                            .wait("exists enabled visible ready", timeout=30)
                    
                    element.set_text(value)

                    self.log.add_log(
                        application_type=self.application_type,
                        level="INFO",
                        message=f"Campo '{field_name}' preenchido com '{value}'",
                        routine="GerenciadorNotasNfe",
                        error_details=""
                    )

                except self.exceptions as e:
                    self.log.add_log(
                        application_type=self.application_type,
                        level="ERROR",
                        message=f"Erro ao preencher campo '{field_name}'",
                        routine="GerenciadorNotasNfe",
                        error_details=str(e)
                    )
                    return False

            return True  # Tudo OK

        except self.exceptions as e:
            self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Erro inesperado ao preencher campos Intermediador",
                routine="GerenciadorNotasNfe",
                error_details=str(e)
            )
            return False    
        
    class Totais(BaseModel):
        TxtValorBc: Optional[str | int] = None
        TxtICMS: Optional[str | int] = None
        TxtValorPis: Optional[str | int] = None
        TxtValorIPI: Optional[str | int] = None
        TxtIPIDevolvido: Optional[str | int] = None
        TxtValorBcSt: Optional[str | int] = None
        TxtValorProdutos: Optional[str | int] = None
        TxtValorDesconto: Optional[str | int] = None
        TxtValorSt: Optional[str | int] = None
        TxtValorCofins: Optional[str | int] = None
        TxtValorOutros: Optional[str | int] = None
        TxtGNRE: Optional[str | int] = None
        TxtFCP: Optional[str | int] = None
        TxtFcpSt: Optional[str | int] = None
        TxtFcpStRet: Optional[str | int] = None
        TxtValorFrete: Optional[str | int] = None    
        TxtIcmsDesonerado: Optional[str | int] = None 
        TxtValorBcStRetido: Optional[str | int] = None 
        TxtValorStRetido: Optional[str | int] = None 
        txtValorIrrf: Optional[str | int] = None 
        TxtValorCsll: Optional[str | int] = None 
        TxtTotal: Optional[str | int] = None 

    def editar_nota_cabecalho_totais(self,obj:Totais)->bool:
        """
        Preenche os campos de cabeçalho da nota em edição com base no objeto totais.
        
        :param obj: Instância com os dados do destinatario.
        :return: True se sucesso, False em caso de erro.
        """
        try:
            for field_name, value in obj.model_dump().items():

                # ignora campos vazios
                if value in [None, ""]:
                    continue                  

                try:
                    element = self.nfe_window.child_window(auto_id=field_name, control_type="Edit")\
                                            .wait("exists enabled visible ready", timeout=30)
                    
                    element.set_text(value)

                    self.log.add_log(
                        application_type=self.application_type,
                        level="INFO",
                        message=f"Campo '{field_name}' preenchido com '{value}'",
                        routine="GerenciadorNotasNfe",
                        error_details=""
                    )

                except self.exceptions as e:
                    self.log.add_log(
                        application_type=self.application_type,
                        level="ERROR",
                        message=f"Erro ao preencher campo '{field_name}'",
                        routine="GerenciadorNotasNfe",
                        error_details=str(e)
                    )
                    return False

            return True  # Tudo OK

        except self.exceptions as e:
            self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Erro inesperado ao preencher campos Totais",
                routine="GerenciadorNotasNfe",
                error_details=str(e)
            )
            return False        
        

    def aba_cabecalho(self) -> bool:
        """
        Seleciona a aba 'Cabeçalho' na janela de edição de nota.

        :return: True se a aba foi selecionada com sucesso, False caso contrário.
        """
        try:
            aba_cabecalho = self.edicao_nota_window.child_window(
                auto_id="tabCabecalho", control_type="TabItem"
            ).wait("exists enabled visible ready", timeout=10)

            aba_cabecalho.select()

            self.log.add_log(
                application_type=self.application_type,
                level="INFO",
                message="Aba 'Cabeçalho' selecionada com sucesso.",
                routine="GerenciadorNotasNfe",
                error_details=""
            )
            return True

        except self.exceptions as e:
            self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Erro ao selecionar a aba 'Cabeçalho'.",
                routine="GerenciadorNotasNfe",
                error_details=str(e)
            )
            return False
        

    #### inicio dos metodos relacionado a produtos    
    #####
    ####
    ####


    def aba_produtos(self) -> bool:
        """
        Seleciona a aba 'Produtos' na janela de edição de nota.

        :return: True se a aba foi selecionada com sucesso, False caso contrário.
        """
        try:
            aba_produtos = self.edicao_nota_window.child_window(
                auto_id="tabProdutos", control_type="TabItem"
            ).wait("exists enabled visible ready", timeout=10)

            aba_produtos.select()

            self.log.add_log(
                application_type=self.application_type,
                level="INFO",
                message="Aba 'Produtos' selecionada com sucesso.",
                routine="GerenciadorNotasNfe",
                error_details=""
            )
            return True

        except self.exceptions as e:
            self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Erro ao selecionar a aba 'Produtos'.",
                routine="GerenciadorNotasNfe",
                error_details=str(e)
            )
            return False    

