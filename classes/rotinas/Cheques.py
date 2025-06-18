from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from classes.rotinas.ContasReceber import ContaReceber
from classes.utils.GerarDados import GeradorDados  
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components
from classes.rotinas.ExtratoContas import ExtratoContas
from pydantic import BaseModel, field_validator
from typing import Optional
from time import sleep
import random
from faker import Faker
from classes.utils.decorators import com_visual


class Cheques:
    url = "gerenciador-de-cheques"
    filterSelector = "#P150_SELETOR_LOJA"
    rotina = "Cheques"

    class Filtros(BaseModel):
        P150_SELETOR_LOJA: Optional[str] = None
        P150_DATA_INICIAL: Optional[str] = None
        P150_DATA_FINAL: Optional[str] = None
        P150_CHEQUE_TIPO: Optional[str] = None
        P150_CHEQUE_STATUS: Optional[str] = None
        P150_NUMERO_CHEQUE: Optional[str] = None
        P150_BANCO: Optional[str] = None
        P150_EMITENTE: Optional[str] = None
        P150_LOCALIZACAO: Optional[str] = None
        P150_VALOR_INICIAL: Optional[str] = None
        P150_VALOR_FINAL: Optional[str] = None

        @field_validator('*', mode='before')
        @classmethod
        def forceString(cls, v):
            return str(v) if v is not None else None


    class Emitente(BaseModel):
        tipoEmissao: Optional[str] = None # 0 = Terceiro; 1 = Cliente; 2 = Emissão Própria
        P130_NOME_EMITENTE: Optional[str] = None # Terceiro
        P130_PESSOA_EMITENTE_ID: Optional[str] = None # Cliente
        P130_LOJA_EMITENTE_ID: Optional[str] = None #Emissão Própria
        P130_CPF_CNPJ: Optional[str] = None # Terceiro & Cliente
        P130_RG: Optional[str] = None # Terceiro & Cliente
        P130_CELULAR: Optional[str] = None # Terceiro & Cliente
        P130_TELEFONE: Optional[str] = None # Terceiro & Cliente

        @field_validator('*', mode='before')
        @classmethod
        def forceString(cls, v):
            return str(v) if v is not None else None
        
    
    class Cheque(BaseModel):
        P130_LOJA: Optional[str] = None
        P130_LOCALIZACAO: Optional[str] = None
        P130_CMC7: Optional[str] = None
        P130_DATA_EMISSAO: Optional[str] = None
        P130_BOM_PARA: Optional[str] = None
        P130_BANCO_ID: Optional[str] = None
        P130_AGENCIA: Optional[str] = None
        P130_DIGITO_AGENCIA: Optional[str] = None
        P130_CONTA: Optional[str] = None
        P130_DIGITO_CONTA: Optional[str] = None
        P130_NUMERO_CHEQUE: Optional[str] = None
        P130_NUMERO_SERIE: Optional[str] = None
        P130_VALOR: Optional[str] = None
        P130_OBSERVACAO: Optional[str] = None

        @field_validator('*', mode='before')
        @classmethod
        def forceString(cls, v):
            return str(v) if v is not None else None


    mapeamentoObjToFiltros = {
        "P130_LOJA" : "P150_SELETOR_LOJA",
        "P130_DATA_EMISSAO" : ["P150_DATA_INICIAL","P150_DATA_FINAL"],
        "P130_NUMERO_CHEQUE" : "P150_NUMERO_CHEQUE",
        "P130_BANCO_ID" : "P150_BANCO",
        "P130_LOCALIZACAO" : "P150_LOCALIZACAO",
        "P130_VALOR" : ["P150_VALOR_INICIAL", "P163_VALOR_MAX"]
    }


    @staticmethod
    def insereEmitente(init:tuple, infoEmitente:Emitente = None) -> Emitente | bool:
        """
        Método que insere informações do emitente em um cheque.

        :param init:
            Tupla com parâmetros do ambiente.

        :param infoEmitente:
            Objeto opcional instanciado da classe Emitente, utilizado para a criação do cheque,
            caso possua atributos obrigatórios faltantes, ou o mesmo não seja passado, será gerado pelo método.

        :return:
            Retorna um objeto Emitente com os dados recuperados da inserção, ou False se falhar.
        """
        
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        fake = Faker('pt_BR')

        queries = {
            "queryEmpresa": """
                                SELECT LOJA_ID FROM ERP.LOJA WHERE GRUPO_LOJA_ID = 1501
                            """
                            ,
            "queryCliente": """
                                SELECT
                                    PESSOA.PESSOA_ID       
                                FROM 
                                    ERP.PESSOA
                                WHERE 
                                    GRUPO_LOJA_ID = 1501
                                    AND STATUS = 1
                            """
        }

        queryEmitente = FuncoesUteis.getQueryResults(init, queries)

        if not infoEmitente or infoEmitente.tipoEmissao not in ["0", "1", "2"]:
            infoEmitente = Cheques.Emitente()
            infoEmitente.tipoEmissao = str(random.randint(0, 2))

        match infoEmitente.tipoEmissao:
            case "0":
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Emitente do tipo 'Terceiro' selecionado.",
                    routine=f"{Cheques.rotina} - insereEmitente",
                    error_details=""
                )

                Apex.setValue(browser, "P130_CHEQUE_TIPO_ID_0", '2')
                sleep(1)
                valoresObrigatoriosEmitente = {
                    "P130_NOME_EMITENTE" : fake.name(),
                    "P130_CPF_CNPJ" : random.choice([fake.cpf(), fake.cnpj()]),
                    "P130_RG" : GeradorDados.simpleRandString(init, 5, 10),
                    "P130_CELULAR" : fake.random_number(11, True),
                    "P130_TELEFONE" : fake.random_number(10, True)
                }
                notPopUp = True
                
            case "1":
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Emitente do tipo 'Cliente' selecionado.",
                    routine=f"{Cheques.rotina} - insereEmitente",
                    error_details=""
                )

                Apex.setValue(browser, "P130_CHEQUE_TIPO_ID_1", '1')
                valoresObrigatoriosEmitente = {
                    "P130_PESSOA_EMITENTE_ID" : queryEmitente["Query_queryCliente"]
                }
                notPopUp = False

            case _:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message=f"Emitente do tipo 'Emissão Própria' selecionado.",
                    routine=f"{Cheques.rotina} - insereEmitente",
                    error_details=""
                )

                Apex.setValue(browser, "P130_CHEQUE_TIPO_ID_2", '3')
                valoresObrigatoriosEmitente = {
                    "P130_LOJA_EMITENTE_ID" : queryEmitente["Query_queryEmpresa"]
                }
                notPopUp = False

        dictEmitente = FuncoesUteis.convertDictValoresToStr(init, FuncoesUteis.objToDictObrigatorio(init, infoEmitente, valoresObrigatoriosEmitente))

        del dictEmitente["tipoEmissao"]

        verificaCamposEmitente = {
            "P130_NOME_EMITENTE" : "text",
            "P130_CPF_CNPJ" : ("cpf", "cnpj"),
            "P130_RG" : "alfanum",
            "P130_CELULAR" : "celular",
            "P130_TELEFONE" : "telefone"
        }

        verificaCamposEmitente = FuncoesUteis.filtrarCamposPorDicionario(init, verificaCamposEmitente, dictEmitente)

        FuncoesUteis.prepareToCompareValues(init, dictEmitente, notPopUp)

        valoresRecuperar = set(dictEmitente.keys())
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Set de campos criado para recuperação: {valoresRecuperar}",
            routine=f"{Cheques.rotina} - insereEmitente",
            error_details=""
        )

        valoresRecuperados = FuncoesUteis.recuperaValores(init, valoresRecuperar)

        if not FuncoesUteis.validaCamposPorRegex(init, verificaCamposEmitente):
            Log_manager.add_log(
                application_type=env_application_type,
                level="WARNING",
                message="Teste encerrado por causa dos campos aceitando valores incorretos.",
                routine=f"{Cheques.rotina} - insereEmitente",
                error_details=""
            )
            return False
        
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Emitente inserido com sucesso!",
            routine=f"{Cheques.rotina} - insereEmitente",
            error_details=""
        )
        
        return Cheques.Emitente(**valoresRecuperados)
#END insereEmitente(init, infoEmitente)

    @staticmethod
    def insereCheque(init:tuple, infoCheque:Cheque = None) -> Cheque | bool:
        """
        Método que insere informações do cheque em um cheque.

        :param init:
            Tupla com parâmetros do ambiente.

        :param infoCheque:
            Objeto opcional instanciado da classe Cheque, utilizado para a criação do cheque,
            caso possua atributos obrigatórios faltantes, ou o mesmo não seja passado, será gerado pelo método.

        :return:
            Retorna um objeto Cheque com os dados recuperados da inserção, ou False se falhar.
        """
        
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        fake = Faker('pt_BR')

        queries = {
            "queryEmpresa": """
                                SELECT LOJA_ID FROM ERP.LOJA WHERE GRUPO_LOJA_ID = 1501
                            """
                            ,
            "queryBanco":   """
                                SELECT BANCO_ID FROM ERP.BANCO
                            """
                            ,
            "queryLocalizacao": """
                                SELECT CONTA.CONTA_ID  
                                    FROM ERP.CONTA
                                    JOIN ERP.CONTA_ESPECIFICACAO ON CONTA.CONTA_ID = CONTA_ESPECIFICACAO.CONTA_ID
                                    LEFT JOIN ERP.LOJA ON LOJA.LOJA_ID = CONTA_ESPECIFICACAO.LOJA_ID
                                    WHERE CONTA_ESPECIFICACAO.GRUPO_LOJA_ID = 1501
                                        AND CONTA.TIPO_CONTA_ID = 2
                                        AND (CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IN (1) OR CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IS NULL)
                                        AND (CONTA.CONTA_ID IN (0) OR CONTA_ESPECIFICACAO.STATUS IN (1))
                                """
        }

        queryCheques = FuncoesUteis.getQueryResults(init, queries)

        valoresObrigatoriosCheque = {
            "P130_AGENCIA" : (int, 4, 15),
            "P130_NUMERO_CHEQUE" : (int, 100, 999999),
            "P130_VALOR" : (float, 10, 9999),
            "P130_DATA_EMISSAO" : "date"
        }

        valoresObrigatoriosCheque = FuncoesUteis.geraValoresRandom(init, valoresObrigatoriosCheque)

        valoresObrigatoriosChequePopUp = {
            "P130_LOJA" : queryCheques["Query_queryEmpresa"],
            "P130_BANCO_ID" : queryCheques["Query_queryBanco"]
        }

        todosCamposPopUp = { # necessária pois nem todos popuplov são obrigátorios, utilizado para saber se um seletor é campo normal ou popuplov
            "P130_LOJA",
            "P130_LOCALIZACAO",
            "P130_BANCO_ID"
        }

        valoresCheque = FuncoesUteis.preencheCamposComunsEPopUp(init, infoCheque, valoresObrigatoriosCheque, valoresObrigatoriosChequePopUp)

        valoresCamposFinal, valoresCamposPopUpLovFinal = FuncoesUteis.separaCamposComunsEPopUp(init, valoresCheque, todosCamposPopUp)

        verificaCamposCheque = { # pesquisado na internet quais caracteres cada campo tem que aceitar, só numeros, numeros e letras, etc.
            "P130_CMC7" : "numComEspaco",
            "P130_DATA_EMISSAO" : "date",
            "P130_BOM_PARA" : "date",
            "P130_AGENCIA" : "num",
            "P130_DIGITO_AGENCIA" : "alfanum",
            "P130_CONTA" : "num",
            "P130_DIGITO_CONTA" : "alfanum",
            "P130_NUMERO_CHEQUE" : "num",
            "P130_NUMERO_SERIE" : "num",
            "P130_VALOR" : "valor",
            "P130_OBSERVACAO" : "text"
        }

        verificaCamposCheque = FuncoesUteis.filtrarCamposPorDicionario(init, verificaCamposCheque, valoresCamposFinal)

        FuncoesUteis.prepareToCompareValues(init, valoresCamposFinal, True)

        FuncoesUteis.prepareToCompareValues(init, valoresCamposPopUpLovFinal, False)

        valoresRecuperar = set(valoresCheque.keys())
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message=f"Set de campos criado para recuperação: {valoresRecuperar}",
            routine=f"{Cheques.rotina} - insereCheque",
            error_details=""
        )

        valoresRecuperados = FuncoesUteis.recuperaValores(init, valoresRecuperar)

        if not FuncoesUteis.validaCamposPorRegex(init, verificaCamposCheque):
            Log_manager.add_log(
                application_type=env_application_type,
                level="WARNING",
                message="Teste encerrado por causa dos campos aceitando valores incorretos.",
                routine=f"{Cheques.rotina} - insereCheque",
                error_details=""
            )
            return False
        
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Cheque inserido com sucesso!",
            routine=f"{Cheques.rotina} - insereCheque",
            error_details=""
        )

        return Cheques.Cheque(**valoresRecuperados)

#END insereCheque(init, infoCheque)

    @staticmethod
    def vinculaContaReceber(init:tuple) -> bool:
        """
        Vincula à um cheque uma conta a receber via criação.

        :param init:
            Tupla com parâmetros do ambiente.

        :return:
            True se foi vinculado, False caso contrário.
        """
        
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        FuncoesUteis.scrollIntoView(init, "botaoVincular", True)

        browser.switch_to.default_content()
            
        if Components.has_frame(init, "[title='Vincular Cheque']"):

            Components.btnClick(init, "#R235218972113439446_cards > li.t-Cards-item.goLancarCR")

            browser.switch_to.default_content()

            if Components.has_frame(init, "[title='Cadastro de Contas a Receber Resumido']"):

                if not ContaReceber.insereContaReceberResumida(init):
                    return False

                browser.switch_to.default_content()

            return True
#END vinculaContaReceber()


    # @com_visual (any, batch_name="Cheques - Cria Cheque")
    @staticmethod
    def criaChequeCompleto(init:tuple, infoEmitente:Emitente = None, infoCheque:Cheque = None) -> Cheque | bool:
        """
        Cria um cheque com informações do emitente e do próprio cheque.

        :param init:
        Tupla com parâmetros do ambiente.

        :param infoEmitente:
        Objeto opcional instanciado da classe Emitente, utilizado para a criação do cheque,
        caso possua atributos obrigatórios faltantes, ou o mesmo não seja passado, será gerado pelo método chamado.

        :param infoCheque:
        Objeto opcional instanciado da classe Cheque, funcionalidade igual ao infoEmitente.

        :return:
        Objeto do tipo Cheque caso o cheque seja inserido corretamente, retorna False caso falhe em qualquer etapa da criação.
        """
        
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        # validator=None

        Components.btnClick(init, "#incluir")

        if Components.has_frame(init, "iframe[src*='cheque']"):

            emitente = Cheques.insereEmitente(init, infoEmitente)

            # if validator:
            #     validator.check_region("#identificacaoEmitente")
            
            cheque = Cheques.insereCheque(init, infoCheque)

            # if validator:
            #     validator.check_region("#dadosCheque")

            if Cheques.vinculaContaReceber(init):

                browser.switch_to.default_content()

                if Components.has_frame(init, "iframe[src*='cheque']"):

                    if emitente and cheque:
                        Log_manager.add_log(
                            application_type=env_vars.get("WEB"),
                            level="INFO",
                            message="Emitente ✔️ | Cheque ✔️",
                            routine=f"{Cheques.rotina} - criaChequeCompleto",
                            error_details=""
                        )
                        FuncoesUteis.scrollIntoView(init, "#B16327445204607180", True) # salvar

                        if Components.has_alert(init):
                            return False
                        
                        Log_manager.add_log(
                            application_type=env_vars.get("WEB"),
                            level="INFO",
                            message="Cheque vinculado com sucesso à conta a receber!",
                            routine=f"{Cheques.rotina} - criaChequeCompleto",
                            error_details=""
                        )

                        return cheque

                    elif not emitente and not cheque:
                        Log_manager.add_log(
                            application_type=env_vars.get("WEB"),
                            level="WARNING",
                            message="Emitente ❌ | Cheque ❌",
                            routine=f"{Cheques.rotina} - criaChequeCompleto",
                            error_details=""
                        )

                    elif not emitente:
                        Log_manager.add_log(
                            application_type=env_vars.get("WEB"),
                            level="WARNING",
                            message="Emitente ❌ | Cheque ✔️",
                            routine=f"{Cheques.rotina} - criaChequeCompleto",
                            error_details=""
                        )

                    elif not cheque:
                        Log_manager.add_log(
                            application_type=env_vars.get("WEB"),
                            level="WARNING",
                            message="Emitente ✔️ | Cheque ❌",
                            routine=f"{Cheques.rotina} - criaChequeCompleto",
                            error_details=""
                        )
            
        return False
#END criaChequeCompleto(init, infoEmitente, infoCheque)