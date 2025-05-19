from classes.utils.LogManager import LogManager
Log_manager = LogManager()







class Home:
    def __init__(self, app,env_vars):
        self.app = app
        self.title = "HOS - Farma Splash"
        self.farma_window = self.app.window(auto_id="hosFarmaWindow")
        self.application_type = env_vars.get("APPLICATION_TYPE")

    def wait_for_home(self):
        try:
            self.app.window(title=self.title).wait("exists enabled visible ready", timeout=60)
            Log_manager.add_log(application_type=self.application_type, level="INFO", message=f"Janela: {self.title} encontrada ", routine="", error_details="")

        except Exception as e:
            Log_manager.add_log(application_type=self.application_type, level="ERROR", message="", routine="", error_details=str(e))

        


    def searchBar(self, search_text: str):
        try:
            principal_window = self.farma_window  # Substitua com o handle correto
            principal_window.wait("exists enabled visible ready", timeout=60)
            
            search_bar = principal_window.child_window(auto_id="txtSearchMenu", control_type="Edit")
            search_bar.wait("exists visible", timeout=30)
            
            search_bar.set_text(search_text)
            text = search_bar.texts()
            print(f"texto da barra de pesquisa {text}")
        except Exception as e:
            print(f"Erro ao interagir com a barra de pesquisa: {e}")
            raise




       
    def sideMenu(self):
        """
        Acessa o menu lateral e retorna o objeto do menu
        :param menu_name: Nome do menu a ser acessado.
        """
        side_menu = self.farma_window.child_window(auto_id="btnMenus", control_type="Button").wait("exists enabled visible ready", timeout=15)
        side_menu.click()

    def clickMenu(self, menu_name: str):
        """
        Clica no menu especificado.

        :param menu_name: Nome do menu a ser clicado. Deve ser o nome do menu com a primeira letra maiúscula e sem acento.

        Menus disponíveis: Cadastros, Estoque, Compras, Vendas, Financeiro, Crediario, P344, Gerencial, Relatorios, Ferramentas
        """
        # Garantir que o nome do menu esteja em um formato válido
        menu_name = menu_name.capitalize()  # Certifica-se de que a primeira letra é maiúscula

        # Construir o auto_id a partir do nome do menu
        try:
            self.farma_window.child_window(auto_id=f"btn{menu_name}", control_type="RadioButton").wait("exists enabled visible ready", timeout=30).click()
            
        except Exception as e:
            raise RuntimeError(f"Falha ao clicar no menu '{menu_name}': {str(e)}")
