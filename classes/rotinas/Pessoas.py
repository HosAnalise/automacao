from pydantic import BaseModel
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.GerarDados import GeradorDados  
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components
from pydantic import BaseModel, field_validator
from typing import Optional, Union
from faker import Faker
fake = Faker('pt_BR')
import random
from time import sleep

class Pessoas:
    url = "lista-de-pessoa"
    filterSelector = "P5_TIPO_CADASTRO"
    rotina = "Pessoas"

    queries = {
            "tipoCadastro":   """
                                    SELECT
                                        TIPO_CADASTRO_PESSOA_ID
                                    FROM
                                        ERP.TIPO_CADASTRO_PESSOA
                                    WHERE TIPO_CADASTRO_PESSOA_ID <> 10
                                """,

    }

    class Endereco(BaseModel):
        P6_TIPO_ENDERECO_ID: Optional[str] = None
        P6_CEP: Optional[str] = None
        P6_ESTADO_ID: Optional[str] = None
        P6_CIDADE_ID: Optional[str] = None
        P6_BAIRRO: Optional[str] = None
        P6_ENDERECO: Optional[str] = None
        P6_NUMERO: Optional[str] = None
        P6_COMPLEMENTO: Optional[str] = None
        P6_CORRESPONDENCIA: Optional[str] = None # valor deve ser '0' ou '1'
        P6_BOLETO_ENDERECO: Optional[str] = None # valor deve ser '0' ou '1'

        @field_validator('*', mode='before')
        @classmethod
        def forceString(cls, v):
            return str(v) if v is not None else None
        

    class Contato(BaseModel):
        P6_NOME_CONTATO: Optional[str] = None
        P6_CONTATO_EMAIL: Optional[str] = None
        P6_CONTATO_OBSERVACAO: Optional[str] = None
        P6_CONTATO_CELULAR: Optional[str] = None
        P6_CONTATO_TELEFONE: Optional[str] = None
        P6_CPF_RESPONSAVEL: Optional[str] = None
        P6_ENVIAR_EMAIL: Optional[str] = None # valor deve ser '0' ou '1'
        P6_BOLETO_CONTATO: Optional[str] = None # valor deve ser '0' ou '1'

        @field_validator('*', mode='before')
        @classmethod
        def forceString(cls, v):
            return str(v) if v is not None else None
        

    class Documentos(BaseModel):
        P6_N_DOCUMENTO: Optional[str] = None
        P6_TIPO_DOCUMENTO_ID: Optional[str] = None
        P6_UF_EXPEDIDOR_ID: Optional[str] = None
        P6_TIPO_ORGAO_EMISSOR_ID: Optional[str] = None

        @field_validator('*', mode='before')
        @classmethod
        def forceString(cls, v):
            return str(v) if v is not None else None
        

    class Dependentes(BaseModel):
        P6_NOME_DEPENDENTE: Optional[str] = None
        P6_CATEGORIA_DEPENDENTE: Optional[str] = None
        P6_DOCUMENTO_DEPENDENTE: Optional[str] = None
        P6_CARTAO_DEPENDENTE: Optional[str] = None
        P6_STATUS_DEPENDENTE: Optional[str] = None # valor deve ser '0' ou '1'

        @field_validator('*', mode='before')
        @classmethod
        def forceString(cls, v):
            return str(v) if v is not None else None
    

    class Pessoa(BaseModel):
        tipoPessoa: Optional[str] = None # '1' = física; '2' = jurídica
        P6_NOME: Optional[str] = None
        P6_CPF: Optional[str] = None
        P6_RG: Optional[str] = None
        P6_GENERO: Optional[str] = None
        P6_DATA_NASCIMENTO: Optional[str] = None
        P6_APELIDO: Optional[str] = None
        P6_CNPJ: Optional[str] = None
        P6_RAZAO_SOCIAL: Optional[str] = None
        P6_FANTASIA: Optional[str] = None
        P6_IE: Optional[str] = None
        P6_UF_INSCRICAO_ESTADUAL: Optional[str] = None
        P6_ISENTA_IE: Optional[str] = None # 'N' = Não; '1' = Sim
        P6_ENVIAR_PARA_REGISTRO: Optional[str] = None # Escrever 'Sim' ou 'Nao', não considerado como popUpLov
        P6_STATUS: Optional[str] = None
        endereco: Optional["Pessoas.Endereco"] = None
        contato: Optional["Pessoas.Contato"] = None
        documentos: Optional["Pessoas.Documentos"] = None
        dependentes: Optional["Pessoas.Dependentes"] = None

        @field_validator(
            "tipoPessoa", "P6_NOME", "P6_CPF", "P6_RG", "P6_GENERO", 
            "P6_DATA_NASCIMENTO", "P6_APELIDO", "P6_CNPJ", "P6_RAZAO_SOCIAL",
            "P6_FANTASIA", "P6_IE", "P6_UF_INSCRICAO_ESTADUAL", "P6_ISENTA_IE",
            "P6_ENVIAR_PARA_REGISTRO", "P6_STATUS",
            mode="before"
        )
        @classmethod
        def forceString(cls, v):
            return str(v) if v is not None else None


    @staticmethod
    def insereEndereco(init:tuple, enderecoPessoa:"Pessoas.Endereco") -> Union["Pessoas.Endereco", bool]:
        """
        Insere os valores de endereço à uma pessoa.

        :param init:
            Tupla comparâmetros do ambiente.

        :param enderecoPessoa:
            Objeto com seletores e valores referentes ao endereço, informações recebidas priorizadas durante a inserção.

        :return:
            Retorna um objeto com os seletores e valores inseridos no endereço, False caso algum erro ocorra.
        """

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        FuncoesUteis.scrollIntoView(init, 'button[aria-labelledby="a_Collapsible5_endereco_heading"]', True, False)

        FuncoesUteis.scrollIntoView(init, "#btnSalvarEndereco")

        ceps = ["95702000", "69905205", "72823070"]

        random.shuffle(ceps)

        valoresObrigatorios = {
            "P6_CEP" : ceps[0],
            "P6_BAIRRO" : fake.bairro(),
            "P6_ESTADO_ID" : "RS",
            "P6_CIDADE_ID" : "Bento Gonçalves",
            "P6_ENDERECO" : fake.street_name(),
            "P6_NUMERO" : fake.random_int(1, 999),
        }

        camposPopUp = {
            "P6_TIPO_ENDERECO_ID",
            "P6_CORRESPONDENCIA",
            "P6_BOLETO_ENDERECO"
        }

        valoresEndereco = FuncoesUteis.convertDictValoresToStr(init, FuncoesUteis.objToDictObrigatorio(init, enderecoPessoa, valoresObrigatorios))

        valoresCamposFinal, valoresCamposPopUpLovFinal = FuncoesUteis.separaCamposComunsEPopUp(init, valoresEndereco, camposPopUp)

        verificaEnderecoRegex = {
            "P6_CEP" : "cep",
            "P6_BAIRRO" : "text",
            "P6_ENDERECO" : "text",
            "P6_NUMERO" : "num",
            "P6_COMPLEMENTO" : "text"
        }

        verificaEnderecoRegex = FuncoesUteis.filtrarCamposPorDicionario(init, verificaEnderecoRegex, valoresCamposFinal)

        FuncoesUteis.setValue(init, "#P6_CEP", valoresCamposFinal["P6_CEP"])

        Components.btnClick(init, "#P6_COMPLEMENTO")# clicado para que o CEP possivelmente auto complete os outros campos

        sleep(5)

        for seletor in (["P6_ESTADO_ID", "P6_CIDADE_ID", "P6_BAIRRO", "P6_ENDERECO", "P6_NUMERO"]):
            valorObj = getattr(enderecoPessoa, seletor, None)
            if valorObj is not None and seletor in valoresCamposPopUpLovFinal: # 1. Valor do objeto recebido (popUp)
                Apex.setValue(browser, seletor, valorObj)
            
            elif valorObj is not None and seletor in valoresCamposFinal: # 2. Valor do objeto recebido (comum)
                Apex.setValue(browser, seletor, '')
                FuncoesUteis.setValue(init, f"#{seletor}", valorObj)

            elif not Apex.getValue(browser, seletor) and seletor in valoresCamposPopUpLovFinal: # 3. Valor gerado automaticamente (popup)
                Apex.setValue(browser, seletor, valoresCamposPopUpLovFinal[seletor])

            elif not Apex.getValue(browser, seletor) and seletor in valoresCamposFinal: # 4. Valor gerado automaticamente (comum)
                FuncoesUteis.setValue(init, f"#{seletor}", valoresCamposFinal[seletor])
            # 5. Se já tem valor e não está no objeto, ignora

        Components.btnClick(init, "#P6_COMPLEMENTO") # clicado para garantir que o botão de salvar fique disponivel

        valoresRecuperar = set(valoresEndereco.keys())
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Set de campos criado para recuperação: {valoresRecuperar}",
            routine=f"{Pessoas.rotina} - insereEndereco",
            error_details=""
        )

        valoresRecuperados = FuncoesUteis.recuperaValores(init, valoresRecuperar)

        if not FuncoesUteis.validaCamposPorRegex(init, verificaEnderecoRegex):
            Log_manager.add_log(
                application_type=env_application_type,
                level="WARNING",
                message="Teste encerrado por causa dos campos aceitando valores incorretos.",
                routine=f"{Pessoas.rotina} - insereEndereco",
                error_details=""
            )
            return False

        Components.btnClick(init, "#btnSalvarEndereco")

        if Components.has_alert(init):
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Alerta encontrado, endereço não inserido!",
                routine=f"{Pessoas.rotina} - insereEndereco",
                error_details=""
            )
            return False

        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Endereco inserido com sucesso!",
            routine=f"{Pessoas.rotina} - insereEndereco",
            error_details=""
        )
        
        return Pessoas.Endereco(**valoresRecuperados)
#END insereEndereco(init, enderecoPessoa)

    @staticmethod
    def insereContato(init:tuple, contatoPessoa:"Pessoas.Contato") -> Union["Pessoas.Contato", bool]:
        """
        Insere os valores de contato à uma pessoa.

        :param init:
            Tupla comparâmetros do ambiente.

        :param enderecoPessoa:
            Objeto com seletores e valores referentes ao contato, informações recebidas priorizadas durante a inserção.

        :return:
            Retorna um objeto com os seletores e valores inseridos no contato, False caso algum erro ocorra.
        """

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        FuncoesUteis.scrollIntoView(init, 'button[aria-labelledby="a_Collapsible6_contato_heading"]', True, False)

        if contatoPessoa.P6_CPF_RESPONSAVEL:
            Apex.setValue(browser, "P6_E_RESPONSAVEL_1", '1')

        FuncoesUteis.scrollIntoView(init, "#btnSalvarContato")

        valoresObrigatorios = {
            "P6_CONTATO_CELULAR" : fake.random_number(11, True),
            "P6_CONTATO_TELEFONE" : fake.random_number(10, True)
        }

        valoresContato = FuncoesUteis.convertDictValoresToStr(init, FuncoesUteis.objToDictObrigatorio(init, contatoPessoa, valoresObrigatorios))

        verificaCamposContato = {
            "P6_NOME_CONTATO" : "text",
            "P6_CONTATO_EMAIL" : "text",
            "P6_CONTATO_OBSERVACAO" : "text",
            "P6_CONTATO_CELULAR" : "celular",
            "P6_CONTATO_TELEFONE" : "telefone"
        }

        verificaCamposContato = FuncoesUteis.filtrarCamposPorDicionario(init, verificaCamposContato, valoresContato)

        FuncoesUteis.prepareToCompareValues(init, valoresContato, True)

        valoresRecuperar = set(valoresContato.keys())
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Set de campos criado para recuperação: {valoresRecuperar}",
            routine=f"{Pessoas.rotina} - insereContato",
            error_details=""
        )

        valoresRecuperados = FuncoesUteis.recuperaValores(init, valoresRecuperar)

        if not FuncoesUteis.validaCamposPorRegex(init, verificaCamposContato):
            Log_manager.add_log(
                application_type=env_application_type,
                level="WARNING",
                message="Teste encerrado por causa dos campos aceitando valores incorretos.",
                routine=f"{Pessoas.rotina} - insereContato",
                error_details=""
            )
            return False

        Components.btnClick(init, "#btnSalvarContato")

        if Components.has_alert(init):
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Alerta encontrado, contato não inserido!",
                routine=f"{Pessoas.rotina} - insereContato",
                error_details=""
            )
            return False

        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Contato inserido com sucesso!",
            routine=f"{Pessoas.rotina} - insereContato",
            error_details=""
        )
        
        return Pessoas.Contato(**valoresRecuperados)
#END insereContato(init, contatoPessoa)

    @staticmethod
    def insereDocumento(init:tuple, documentoPessoa:"Pessoas.Documentos") -> Union["Pessoas.Documentos", bool]:
        """
        Insere os valores de documento à uma pessoa.

        :param init:
            Tupla comparâmetros do ambiente.

        :param enderecoPessoa:
            Objeto com seletores e valores referentes ao documento, informações recebidas priorizadas durante a inserção.

        :return:
            Retorna um objeto com os seletores e valores inseridos no documento, False caso algum erro ocorra.
        """

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        FuncoesUteis.scrollIntoView(init, 'button[aria-labelledby="a_Collapsible7_Documento_heading"]', True, False)

        FuncoesUteis.scrollIntoView(init, "#btnSalvarDocumento")

        valoresObrigatorios = {
            "P6_N_DOCUMENTO" : fake.random_number(7, False)
        }

        valoresObrigatoriosPopUp = {
            "P6_TIPO_DOCUMENTO_ID" : random.randint(1, 20)
        }

        camposPopUp = {
            "P6_TIPO_DOCUMENTO_ID",
            "P6_UF_EXPEDIDOR_ID",
            "P6_TIPO_ORGAO_EMISSOR_ID"
        }

        valoresDocumento = FuncoesUteis.preencheCamposComunsEPopUp(init, documentoPessoa, valoresObrigatorios, valoresObrigatoriosPopUp)

        valoresCamposFinal, valoresCamposPopUpLovFinal = FuncoesUteis.separaCamposComunsEPopUp(init, valoresDocumento, camposPopUp)

        verificaDocumentoRegex = {
            "P6_N_DOCUMENTO" : "num"
        }

        verificaDocumentoRegex = FuncoesUteis.filtrarCamposPorDicionario(init, verificaDocumentoRegex, valoresCamposFinal)

        FuncoesUteis.prepareToCompareValues(init, valoresCamposFinal, True)

        FuncoesUteis.prepareToCompareValues(init, valoresCamposPopUpLovFinal)

        valoresRecuperar = set(valoresDocumento.keys())
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Set de campos criado para recuperação: {valoresRecuperar}",
            routine=f"{Pessoas.rotina} - insereDocumento",
            error_details=""
        )

        valoresRecuperados = FuncoesUteis.recuperaValores(init, valoresRecuperar)

        if not FuncoesUteis.validaCamposPorRegex(init, verificaDocumentoRegex):
            Log_manager.add_log(
                application_type=env_application_type,
                level="WARNING",
                message="Teste encerrado por causa dos campos aceitando valores incorretos.",
                routine=f"{Pessoas.rotina} - insereDocumento",
                error_details=""
            )
            return False

        Components.btnClick(init, "#btnSalvarDocumento")

        if Components.has_alert(init):
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Alerta encontrado, documento não inserido!",
                routine=f"{Pessoas.rotina} - insereDocumento",
                error_details=""
            )
            return False

        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Documento inserido com sucesso!",
            routine=f"{Pessoas.rotina} - insereDocumento",
            error_details=""
        )
        
        return Pessoas.Documentos(**valoresRecuperados)
#END insereDocumento(init, documentoPessoa)

    @staticmethod
    def insereDependente(init:tuple, dependentePessoa:"Pessoas.Dependentes") -> Union["Pessoas.Dependentes", bool]:
        """
        Insere os valores de dependente à uma pessoa.

        :param init:
            Tupla comparâmetros do ambiente.

        :param enderecoPessoa:
            Objeto com seletores e valores referentes ao dependente, informações recebidas priorizadas durante a inserção.

        :return:
            Retorna um objeto com os seletores e valores inseridos no dependente, False caso algum erro ocorra.
        """

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        FuncoesUteis.scrollIntoView(init, 'button[aria-labelledby="a_Collapsible7_dependentes_heading"]', True, False)

        FuncoesUteis.scrollIntoView(init, "#btnSalvarDependente")

        valoresObrigatorios = {
            "P6_NOME_DEPENDENTE" : fake.name()
        }

        valoresObrigatoriosPopUp = {
            "P6_CATEGORIA_DEPENDENTE" : random.randint(1, 3)
        }

        valoresDependente = FuncoesUteis.preencheCamposComunsEPopUp(init, dependentePessoa, valoresObrigatorios, valoresObrigatoriosPopUp)

        valoresCamposFinal, valoresCamposPopUpLovFinal = FuncoesUteis.separaCamposComunsEPopUp(init, valoresDependente, valoresObrigatoriosPopUp)

        verificaDependenteRegex = {
            "P6_NOME_DEPENDENTE" : "text",
            "P6_DOCUMENTO_DEPENDENTE" : "text",
            "P6_CARTAO_DEPENDENTE" : "text"
        }

        verificaDependenteRegex = FuncoesUteis.filtrarCamposPorDicionario(init, verificaDependenteRegex, valoresCamposFinal)

        FuncoesUteis.prepareToCompareValues(init, valoresCamposFinal, True)

        FuncoesUteis.prepareToCompareValues(init, valoresCamposPopUpLovFinal)

        valoresRecuperar = set(valoresDependente.keys())
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Set de campos criado para recuperação: {valoresRecuperar}",
            routine=f"{Pessoas.rotina} - insereDependente",
            error_details=""
        )

        valoresRecuperados = FuncoesUteis.recuperaValores(init, valoresRecuperar)

        if not FuncoesUteis.validaCamposPorRegex(init, verificaDependenteRegex):
            Log_manager.add_log(
                application_type=env_application_type,
                level="WARNING",
                message="Teste encerrado por causa dos campos aceitando valores incorretos.",
                routine=f"{Pessoas.rotina} - insereDependente",
                error_details=""
            )
            return False

        Components.btnClick(init, "#btnSalvarDependente")

        if Components.has_alert(init):
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Alerta encontrado, dependente não inserido!",
                routine=f"{Pessoas.rotina} - insereDependente",
                error_details=""
            )
            return False

        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Dependente inserido com sucesso!",
            routine=f"{Pessoas.rotina} - insereDependente",
            error_details=""
        )
        
        return Pessoas.Dependentes(**valoresRecuperados)
#END insereDependente(init, dependentePessoa)

    @staticmethod
    def insereDadosGeraisFisico(init:tuple, dadosPessoa:"Pessoas.Pessoa") -> Union["Pessoas.Pessoa", bool]:
        """
        Insere os valores de dados gerais à uma pessoa física.

        :param init:
            Tupla comparâmetros do ambiente.

        :param dadosPessoa:
            Objeto com seletores e valores referentes aos dados gerais de uma pessoa física, informações recebidas priorizadas durante a inserção.

        :return:
            Retorna um objeto com os seletores e valores inseridos nos dados gerais, False caso algum erro ocorra.
        """

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        valoresObrigatorios = {
            "P6_NOME" : fake.name()
        }
        camposPopUp = {
            "P6_GENERO",
            "P6_ENVIAR_PARA_REGISTRO"
        }
        
        valoresDados = FuncoesUteis.convertDictValoresToStr(init, FuncoesUteis.objToDictObrigatorio(init, dadosPessoa, valoresObrigatorios))

        # for camposRemover in ["tipoPessoa", "P6_CNPJ", "P6_RAZAO_SOCIAL", "P6_FANTASIA", "P6_IE", "P6_UF_INSCRICAO_ESTADUAL", "P6_ISENTA_IE"]:
        #     valoresDados.pop(camposRemover, None)

        valoresCamposFinal, valoresCamposPopUpLovFinal = FuncoesUteis.separaCamposComunsEPopUp(init, valoresDados, camposPopUp)

        verificaPessoaFisicaRegex = {
            "P6_NOME" : "text",
            "P6_CPF" : "cpf",
            "P6_RG" : "num",
            "P6_DATA_NASCIMENTO" : "date",
            "P6_APELIDO" : "text"
        }

        verificaPessoaFisicaRegex = FuncoesUteis.filtrarCamposPorDicionario(init, verificaPessoaFisicaRegex, valoresCamposFinal)

        FuncoesUteis.prepareToCompareValues(init, valoresCamposFinal, True)

        if all(not v for v in valoresCamposPopUpLovFinal.values()):
            FuncoesUteis.prepareToCompareValues(init, valoresCamposPopUpLovFinal)

        valoresRecuperar = set(valoresDados.keys())
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Set de campos criado para recuperação: {valoresRecuperar}",
            routine=f"{Pessoas.rotina} - insereDadosGeraisFisico",
            error_details=""
        )

        valoresRecuperados = FuncoesUteis.recuperaValores(init, valoresRecuperar)

        if not FuncoesUteis.validaCamposPorRegex(init, verificaPessoaFisicaRegex):
            Log_manager.add_log(
                application_type=env_application_type,
                level="WARNING",
                message="Teste encerrado por causa dos campos aceitando valores incorretos.",
                routine=f"{Pessoas.rotina} - insereDadosGeraisFisico",
                error_details=""
            )
            return False

        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Dados da pessoa fisica inserida com sucesso!",
            routine=f"{Pessoas.rotina} - insereDadosGeraisFisico",
            error_details=""
        )
        
        return Pessoas.Pessoa(**valoresRecuperados)
#END insereDadosGeraisFisico(init, dadosPessoa)

    @staticmethod
    def insereDadosGeraisJuridico(init:tuple, dadosPessoa:"Pessoas.Pessoa") -> Union["Pessoas.Pessoa", bool]:
        """
        Insere os valores de dados gerais à uma pessoa juridica.

        :param init:
            Tupla comparâmetros do ambiente.

        :param dadosPessoa:
            Objeto com seletores e valores referentes aos dados gerais de uma pessoa juridica, informações recebidas priorizadas durante a inserção.

        :return:
            Retorna um objeto com os seletores e valores inseridos nos dados gerais, False caso algum erro ocorra.
        """

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        Apex.setValue(browser, "P6_FISICA_JURIDICA", '2')

        valoresObrigatorios = {
            "P6_CNPJ" : random.choice(["43.264.326/0001-39", "23.054.355/0001-69"]),
            "P6_RAZAO_SOCIAL": fake.company()
        }
        if dadosPessoa.P6_ISENTA_IE == 'N':
            valoresObrigatorios["P6_IE"] = random.choice(["460884567505", "576539554316"]) # tem validação entre IE e UF, deixar UF apenas SP
            valoresObrigatorios["P6_UF_INSCRICAO_ESTADUAL"] = "SP"

        
        valoresDados = FuncoesUteis.convertDictValoresToStr(init, FuncoesUteis.objToDictObrigatorio(init, dadosPessoa, valoresObrigatorios))

        valoresCamposFinal = valoresDados.copy()

        verificaPessoaJuridicaRegex = {
            "P6_CNPJ" : 'cnpj',
            "P6_RAZAO_SOCIAL" : 'text',
            "P6_FANTASIA" : 'text',
            "P6_IE" : 'num',
            "P6_APELIDO" : 'text'
        }

        verificaPessoaJuridicaRegex = FuncoesUteis.filtrarCamposPorDicionario(init, verificaPessoaJuridicaRegex, valoresCamposFinal)

        Apex.setValue(browser, "P6_CNPJ", valoresCamposFinal["P6_CNPJ"]) 
        valoresCamposFinal.pop("P6_CNPJ")

        Apex.setValue(browser, "P6_ISENTA_IE", 'N')

        Components.btnClick(init, "#P6_APELIDO")

        camposAutoPreencher = ["P6_RAZAO_SOCIAL"]
        if dadosPessoa.P6_ISENTA_IE == "N":
            camposAutoPreencher.append("P6_IE")
            camposAutoPreencher.append("P6_UF_INSCRICAO_ESTADUAL")

        sleep(5) # Garantir se o CNPJ vai preencher os campos ou não

        for seletor in (camposAutoPreencher):
            valorObj = getattr(dadosPessoa, seletor, None)
            if valorObj is not None: # 1. Valor do objeto recebido
                Apex.setValue(browser, seletor, '')
                FuncoesUteis.setValue(init, f"#{seletor}", valorObj)

            elif not Apex.getValue(browser, seletor): # 2. Campo vazio, usar valor gerado automaticamente
                FuncoesUteis.setValue(init, f"#{seletor}", valoresCamposFinal[seletor])
            # 3. Se já tem valor e não está no objeto, ignora

        valoresRecuperar = set(valoresDados.keys())
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Set de campos criado para recuperação: {valoresRecuperar}",
            routine=f"{Pessoas.rotina} - insereDadosGeraisJuridico",
            error_details=""
        )

        valoresRecuperados = FuncoesUteis.recuperaValores(init, valoresRecuperar)

        if not FuncoesUteis.validaCamposPorRegex(init, verificaPessoaJuridicaRegex):
            Log_manager.add_log(
                application_type=env_application_type,
                level="WARNING",
                message="Teste encerrado por causa dos campos aceitando valores incorretos.",
                routine=f"{Pessoas.rotina} - insereDadosGeraisJuridico",
                error_details=""
            )
            return False

        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Dados da pessoa juridica inserida com sucesso!",
            routine=f"{Pessoas.rotina} - insereDadosGeraisJuridico",
            error_details=""
        )
        
        return Pessoas.Pessoa(**valoresRecuperados)
#END insereDadosGeraisJuridico(init, dadosPessoa)

    @staticmethod
    def inserePessoaCompleta(init:tuple, pessoa:"Pessoas.Pessoa") -> Union["Pessoas.Pessoa", bool]:
        """
        Cria uma nova pessoa, preenchendo as abas que tem seus valores presentes no objeto recebido.

        :param init:
            Tupla comparâmetros do ambiente.

        :param pessoa:
            Objeto com seletores e valores referentes ao cadastro de pessoa total, dita se uma aba será preenchida ou não,
            por exemplo, caso possua pelo menos um seletor presente da classe Endereco, todos campos obrigatórios da aba Endereço serão preenchidos e salvados no cadastro.

        :return:
            Retorna um objeto com todos os campos preenchidos durante o cadastro, False caso algum erro ocorra.
        """

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        tipoPessoa = pessoa.tipoPessoa if pessoa.tipoPessoa else random.choice(["1", "2"])

        dadosPessoa = pessoa.model_dump(exclude={"endereco", "contato", "documentos", "dependentes", "tipoPessoa"})

        if tipoPessoa == "1":
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Inserindo valores para os dados gerais fisicos.",
                routine=f"{Pessoas.rotina} - inserePessoaCompleta",
                error_details=""
            )
            for camposRemover in ["tipoPessoa", "P6_CNPJ", "P6_RAZAO_SOCIAL", "P6_FANTASIA", "P6_IE", "P6_UF_INSCRICAO_ESTADUAL", "P6_ISENTA_IE"]:
                dadosPessoa.pop(camposRemover, None)
            dadosGerais = Pessoas.insereDadosGeraisFisico(init, Pessoas.Pessoa(**dadosPessoa))
        elif tipoPessoa == "2":
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Inserindo valores para os dados gerais juridicos.",
                routine=f"{Pessoas.rotina} - inserePessoaCompleta",
                error_details=""
            )
            for camposRemover in ["tipoPessoa", "P6_NOME", "P6_CPF", "P6_RG", "P6_GENERO", "P6_DATA_NASCIMENTO"]:
                dadosPessoa.pop(camposRemover, None)
            dadosGerais = Pessoas.insereDadosGeraisJuridico(init, Pessoas.Pessoa(**dadosPessoa))
        else: 
            Log_manager.add_log(
                application_type=env_application_type,
                level="WARNING",
                message=f"Tipo de pessoa inválido: {pessoa.tipoPessoa}",
                routine=f"{Pessoas.rotina} - inserePessoaCompleta",
                error_details=""
            )
            return False

        if pessoa.endereco:
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Inserindo valores para o endereço do cliente.",
                routine=f"{Pessoas.rotina} - inserePessoaCompleta",
                error_details=""
            )
            enderecoReceb = Pessoas.insereEndereco(init, pessoa.endereco)
        else: enderecoReceb = None

        if pessoa.contato:
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Inserindo valores para o contato do cliente.",
                routine=f"{Pessoas.rotina} - inserePessoaCompleta",
                error_details=""
            )
            contatoReceb = Pessoas.insereContato(init, pessoa.contato)
        else: contatoReceb = None

        if pessoa.dependentes:
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Inserindo valores para o dependente do cliente.",
                routine=f"{Pessoas.rotina} - inserePessoaCompleta",
                error_details=""
            )
            dependenteReceb = Pessoas.insereDependente(init, pessoa.dependentes)
        else: dependenteReceb = None

        dadosAtualizados = {
            k: v for k, v in {
                "endereco": enderecoReceb,
                "contato": contatoReceb,
                "dependentes": dependenteReceb
            }.items() if v is not None
        }
        return dadosGerais.model_copy(update=dadosAtualizados)
#END inserePessoaCompleta(init, pessoa)