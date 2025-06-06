from classes.utilsDesktop.FuncoesUteisDesktop import FuncoesUteisDesktop







class Home:
    def __init__(self, app,env_vars,log_manager):
        self.app = app
        self.title = "HOS - Farma Splash"
        self.farma_window = self.app.window(auto_id="hosFarmaWindow")
        self.application_type = env_vars.get("APPLICATION_TYPE")
        self.screenshot_path = env_vars.get("SCREENSHOT_PATH")
        self.user = env_vars.get("USER")
        self.password = env_vars.get("PASSWORD")
        self.log = log_manager
        self.exceptions = FuncoesUteisDesktop.pywinauto_exceptions()

    def wait_for_home(self):
        try:
            self.app.window(title=self.title).wait("exists enabled visible ready", timeout=60)
            self.log.add_log(application_type=self.application_type, level="INFO", message=f"Janela: {self.title} encontrada ", routine="", error_details="")

        except self.exceptions as e:
            self.log.add_log(application_type=self.application_type, level="ERROR", message="", routine="", error_details=str(e))

        


    def searchBar(self, search_text: str):

        try:
            principal_window = self.farma_window  # Substitua com o handle correto
            principal_window.wait("exists enabled visible ready", timeout=60)
            self.log.add_log(
                application_type=self.application_type,
                level="INFO",
                message="Janela principal encontrada",
                routine="",
                error_details=""
            )
            
            search_bar = principal_window.child_window(auto_id="txtSearchMenu", control_type="Edit")\
                .wait("exists visible", timeout=30)
            self.log.add_log(
                application_type=self.application_type,
                level="INFO",
                message="cBarra de pesquisa encontrada",
                routine="",
                error_details=""
            )
            
            search_bar.set_text(search_text)
            self.log.add_log(
                application_type=self.application_type,
                level="INFO",
                message="Texto inserido na barra de pesquisa",
                routine="",
                error_details=""
            )

            text = search_bar.texts()
            self.log.add_log(
                application_type=self.application_type,
                level="INFO",
                message=f"Texto recuperado da barra de pesquisa: {text}",
                routine="",
                error_details=""
            )
        except self.exceptions as e:
           self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Erro ao acessar a barra de pesquisa",
                routine="",
                error_details=str(e)
            )




       
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
            self.log.add_log(level="INFO", message=f"btn{menu_name} clicado com sucesso", routine="", application_type=self.application_type, error_details='')

            
        except self.exceptions as e:
            self.log.add_log(level="INFO", message=f"btn{menu_name} não foi clicado", routine="", application_type=self.application_type, error_details=str(e))


    def autenticar(self, user:str|int = False, password:str|int = False):

        """
        autentica o usuário no sistema.

        :param user: Nome do usuário. Se não for fornecido, usa o valor padrão.
        :param password: Senha do usuário. Se não for fornecido, usa o valor padrão       
        """
        # Lógica para autenticar o usuário
        user = user if user else self.user
        password = password if password else self.password

        user_filed = self.farma_window.child_window(auto_id="txtUsuario", control_type="Edit").wait("exists enabled visible ready", timeout=30)
        user_filed.set_text(user)

        password_field = self.farma_window.child_window(auto_id="txtSenha", control_type="Edit").wait("exists enabled visible ready", timeout=30)
        password_field.set_text(password)

        self.farma_window.child_window(auto_id="BtnConfirmar", control_type="Button").wait("exists enabled visible ready", timeout=30).click()


        