from classes.rotinasDesktop.Home import Home
from faker import Faker
from classes.utils.LogManager import LogManager
from classes.utils.FuncoesUteis import FuncoesUteis

# Classe CadastroCliente herda de Home

fake = Faker('pt_BR')

class GerenciadorNotasCompra(Home):
    def __init__(self, app, env_vars,getQueryResults):
        # Chama o construtor da classe Home (superclasse)
        super().__init__(app, env_vars)

        password = env_vars.get("PASSWORD")
        user = env_vars.get("USER")
        
        # Atributos específicos de CadastroCliente
        self.user = password
        self.password = user
        self.window_client = self.farma_window.child_window(auto_id="genericWindowCadastros", control_type="Window")
        self.getQueryResults = getQueryResults
        

    
    

            



        


        