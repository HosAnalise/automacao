import random
import string

class GeradorDados:
    @staticmethod
    def gerar_chave_aleatoria(tamanho=32):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=tamanho))

    @staticmethod
    def gerar_chave_nfe():
        chave_uf = str(random.randint(1, 99)).zfill(2)
        chave_cnpj = str(random.randint(100000000000000, 999999999999999)).zfill(14)
        chave_modelo = '55'
        chave_serie = str(random.randint(1, 99)).zfill(2)
        chave_numero = str(random.randint(1, 9999)).zfill(4)
        chave_aleatoria = ''.join(str(random.randint(0, 9)) for _ in range(26))
        return f"{chave_uf}{chave_cnpj}{chave_modelo}{chave_serie}{chave_numero}{chave_aleatoria}"

    @staticmethod
    def gerar_email():
        nome_aleatorio = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        dominio = random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com'])
        return f"{nome_aleatorio}@{dominio}"

    @staticmethod
    def calcular_dv(cpf_part):
        cpf = [int(d) for d in cpf_part]
        peso1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
        dv1 = (sum(cpf[i] * peso1[i] for i in range(9)) * 10) % 11
        dv1 = 0 if dv1 == 10 else dv1
        
        peso2 = [11] + peso1
        dv2 = (sum(cpf[i] * peso2[i] for i in range(9)) + dv1 * 2) * 10 % 11
        dv2 = 0 if dv2 == 10 else dv2
        
        return str(dv1), str(dv2)

    @staticmethod
    def gerar_cpf():
        cpf_base = [random.randint(0, 9) for _ in range(9)]
        dv1, dv2 = GeradorDados.calcular_dv(cpf_base)
        return ''.join(map(str, cpf_base)) + dv1 + dv2

    @staticmethod
    def calcular_dv_cnpj(cnpj_part):
        cnpj = [int(d) for d in cnpj_part]
        peso1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        dv1 = 11 - (sum(cnpj[i] * peso1[i] for i in range(12)) % 11)
        dv1 = 0 if dv1 >= 10 else dv1
        
        peso2 = [6] + peso1
        dv2 = 11 - (sum(cnpj[i] * peso2[i] for i in range(12)) + dv1 * 2) % 11
        dv2 = 0 if dv2 >= 10 else dv2
        
        return str(dv1), str(dv2)

    @staticmethod
    def gerar_cnpj():
        cnpj_base = [random.randint(0, 9) for _ in range(12)]
        dv1, dv2 = GeradorDados.calcular_dv_cnpj(cnpj_base)
        return ''.join(map(str, cnpj_base)) + dv1 + dv2

    @staticmethod
    def gerar_numero_celular():
        ddd = random.randint(11, 99)
        numero = random.randint(900000000, 999999999)
        return f"({ddd}) 9{numero:08d}"

    @staticmethod
    def randomNumberDinamic(v1, v2):
        return random.randint(v1, v2)
    
    
    @staticmethod
    def gerar_nome():
        primeiros_nomes = ["João", "Maria", "Pedro", "Ana", "Lucas", "Carla", "Fernando", "Juliana", "Rafael", "Camila"]
        sobrenomes = ["Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Ferreira", "Costa", "Almeida", "Rodrigues"]
        return f"{random.choice(primeiros_nomes)} {random.choice(sobrenomes)}"
    
    @staticmethod
    def gerar_texto(tamanho):
        return ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=tamanho))
    
    @staticmethod
    def gerar_caracteres_especiais(qtd=1):
        caracteres = "!@#$%^&*()_+[]{}|;:,.<>?/~"
        return ''.join(random.choices(caracteres, k=qtd))
    
    @staticmethod
    def simpleRandString(init, min:int, max:int, nome_variavel: str = None) -> string:
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        tamanho = random.randint(min, max)
        chars = string.ascii_letters + string.digits

        stringGerada = ''.join(random.choices(chars, k=tamanho))

        log_msg = f"Gerado a string aleatória : {stringGerada}"
        if nome_variavel:
            log_msg += f" | Variável: {nome_variavel}"

        Log_manager.add_log(
            level="INFO",
            message=log_msg,
            routine="",
            application_type=env_application_type,
            error_details=""
        )

        return stringGerada
#END simpleRandString(min, max)

    @staticmethod
    def simpleRandDate(init) -> string:
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        dia = str(random.randint(1, 28)).zfill(2)
        mes = str(random.randint(1, 12)).zfill(2)
        ano = random.randint(2019, 2024)

        data = f"{dia}/{mes}/{ano}"

        Log_manager.add_log(
            level="INFO", 
            message=f"Gerado a data aleatoria : {data}", 
            routine="",
            application_type=env_application_type, 
            error_details=""
        )

        return data
#END simpleRandDate()