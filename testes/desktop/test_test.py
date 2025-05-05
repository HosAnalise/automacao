from classes.rotinasDesktop.Home import Home
from classes.rotinasDesktop.CadastroCliente import CadastroCliente


def test_login_success(app, login,env_vars,getQueryResults):
   
        Home(app,env_vars).wait_for_home()
        Home(app,env_vars).sideMenu()
        Home(app,env_vars).clickMenu(menu_name ="Cadastros")
        CadastroCliente(app,env_vars,getQueryResults).cadastrar_cliente()
        CadastroCliente(app,env_vars,getQueryResults).autenticar()
        CadastroCliente(app,env_vars,getQueryResults).cadastro_cliente_geral_endereco()

    