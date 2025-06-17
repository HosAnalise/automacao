from classes.rotinasDesktop.Home import Home
from faker import Faker
from classes.utils import FuncoesUteis
from classes.utils.LogManager import LogManager
from classes.utils.FuncoesUteis import FuncoesUteis

# Classe CadastroCliente herda de Home

fake = Faker('pt_BR')

class CadastroCliente(Home):
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
        

    
    def cadastrar_cliente(self):
        try:
            # Acessa o menu usando o método da classe pai (Home)
            self.clickMenu(menu_name="Cadastros")
            
            # Simula o cadastro do cliente
            self.farma_window.child_window(auto_id=f"Clientes", control_type="Button").wait("exists enabled visible ready", timeout=30).click()
            
        except Exception as e:
            print(f"Erro ao cadastrar o cliente: {e}")

            
    

    def cadastro_cliente_geral_identificacao(self, obj: dict = False):
        """
        Preenche os campos de identificação do cliente na janela de cadastro, na aba geral.

        :param obj: Dicionário com os valores a serem preenchidos. Se não for fornecido, usa valores gerados aleatoriamente.
        
        """
        def preencher_campos(values, pfpj=None):
            """
            Preenche os campos de identificação do cliente na janela de cadastro.

            :param values: Dicionário com os valores a serem preenchidos.

            :param pfpj: Tipo de pessoa (Física ou Jurídica). Se não for fornecido, usa o padrão.
            """
            for key, value in values.items():
                if key == pfpj:
                    tipo = "RadioButton"
                    self.window_client.child_window(auto_id=key, control_type=tipo)\
                        .wait("exists enabled visible ready", timeout=30).click_input()
                elif key == "cboSexo":
                    tipo = "ComboBox"
                    self.window_client.child_window(auto_id=key, control_type=tipo)\
                        .wait("exists enabled visible ready", timeout=30).select(value)
                else:
                    tipo = "Edit"
                    self.window_client.child_window(auto_id=key, control_type=tipo)\
                        .wait("exists enabled visible ready", timeout=30).set_text(str(value))

        if isinstance(obj, dict):
            preencher_campos(obj)
        else:

            for increment in range(1, 3):
                queries = {"classificacao": "SELECT codigo FROM CLASSIFICACAO_CLIENTE"}
                classificacao = self.getQueryResults(queries=queries)["classificacao"]
                pfpj = "rdbTipoPessoaJuridica" if increment == 2 else "rdbTipoPessoaFisica"

                values = {
                    "txtNome": fake.name() if increment == 1 else fake.text(max_nb_chars=100),
                    "txtCPF": fake.cpf() if increment == 1 else fake.text(max_nb_chars=100),
                    "txtEmail": fake.email() if increment == 1 else fake.text(max_nb_chars=100),
                    "DatePicker": fake.date_of_birth() if increment == 1 else fake.text(max_nb_chars=100),
                    "txtApelido": fake.first_name() if increment == 1 else fake.text(max_nb_chars=100),
                    "cboSexo": fake.random_element(elements=("Masculino", "Feminino")),
                    "SelClassificacao": classificacao,
                    pfpj: ""
                }
                #Faltam alguns auto_ids que não estão disponiveis no código: loja cadastro,whatsapp,celular,telefone.


                preencher_campos(values, pfpj)


    def cadastro_cliente_geral_endereco(self,obj:dict = False):

        """
        Preenche os campos de identificação do cliente na janela de cadastro, na aba geral.

        :param obj: Dicionário com os valores a serem preenchidos. Se não for fornecido, usa valores gerados aleatoriamente.
        
        """

        def preencher_campos(values:dict)->dict:
            """
            Preenche os campos de identificação do cliente na janela de cadastro.

            :param values: Dicionário com os valores a serem preenchidos.

            :return: Dicionário com os valores preenchidos, valor inputado e valor recuperado.
            """

            dicionarioComparacao = {}
            for key, value in values.items():
                # if key == pfpj:
                #     tipo = "RadioButton"
                #     self.window_client.child_window(auto_id=key, control_type=tipo)\
                #         .wait("exists enabled visible ready", timeout=30).click_input()
                if key in("cboTipoLogradouro", "cboUf", "cboCidade"):
                    tipo = "ComboBox"
                    campo = self.window_client.child_window(auto_id=key, control_type=tipo)\
                        .wait("exists enabled visible ready", timeout=30).select(value)
                    valor = campo.selected_text()
                else:
                    tipo = "Edit"
                    campo = self.window_client.child_window(auto_id=key, control_type=tipo)\
                        .wait("exists enabled visible ready", timeout=30).set_text(str(value))
                    valor = campo.texts()
                dicionarioComparacao[key] = valor    

            campos = {seletor: (dicionarioComparacao.get(seletor, None), value) for seletor, value in values.items()}
            return campos

                
        if isinstance(obj, dict):
            campos = preencher_campos(values=obj)
        else:
            for increment in range(1, 3):                

                values = {
                    "txtCEP": fake.name() if increment == 1 else fake.text(max_nb_chars=100),
                    "cboTipoLogradouro": fake.cpf(),
                    "txtEndereco": fake.rg(),
                    "txtNumero": fake.email(),
                    "txtBairro": fake.date_of_birth(),
                    "txtComplemento": fake.first_name(),
                    "cboUf": fake.random_element(elements=("Masculino", "Feminino")),
                    "cboCidade": "Bento Gonçalves",                    
                }


                campos = preencher_campos(values=values)

            FuncoesUteis.compareValuesDesktop(obj=campos)


            



            



        


        