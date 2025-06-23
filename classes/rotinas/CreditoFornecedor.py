from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from classes.utils.GerarDados import GeradorDados  
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components
from classes.rotinas.ExtratoContas import ExtratoContas
from pydantic import BaseModel, field_validator
from typing import Optional
from time import sleep
import random


class CreditoFornecedor:
    url = "listagem-de-crédito-de-devolução-de-fornecedor"
    filterSelector = "#P166_SELETOR_LOJA"

    rotina = "Credito de Fornecedor"

    class Filtros(BaseModel):
        P166_SELETOR_LOJA: Optional [str] = None
        P166_FORNECEDOR: Optional [str] = None
        P163_ORIGEM: Optional [str] = None
        P166_NUMERO_NOTA_DEVOLUCAO: Optional [str] = None
        P166_MAIOR_QUE: Optional [str] = None # apenas quando #P166_SALDO = 0

        @field_validator('*', mode='before')
        @classmethod
        def forceString(cls, v):
            return str(v) if v is not None else None


    class Credito(BaseModel):
        P169_DATA: Optional[str] = None
        P169_CREDITO_FORNECEDOR_ORIGEM_ID: Optional[str] = None
        P169_PESSOA_FORNECEDOR_ID: Optional[str] = None
        P169_NUMERO_NOTA_SAIDA: Optional[str] = None
        P169_NUMERO_NOTA_ENTRADA: Optional[str] = None
        P169_LOJA_ID: Optional[str] = None
        P169_VALOR: Optional[str] = None
        P169_OBSERVACAO: Optional[str] = None

        @field_validator('*', mode='before')
        @classmethod
        def forceString(cls, v):
            return str(v) if v is not None else None


    mapeamentoObjToFiltros = {
        "P169_CREDITO_FORNECEDOR_ORIGEM_ID" : "P163_ORIGEM",
        "P169_PESSOA_FORNECEDOR_ID" : "P166_FORNECEDOR",
        "P169_NUMERO_NOTA_SAIDA" : "P166_NUMERO_NOTA_DEVOLUCAO",
        "P169_LOJA_ID" : "P166_SELETOR_LOJA"
        # "P169_VALOR" : "P166_MAIOR_QUE" - não utilizado pois para filtrar, por exemplo, R$30, é necessario colocar pelo menos R$29,99. Filtro desnecessário.
    }


    @staticmethod
    def insereCreditoFornecedor(init:tuple, valores:Credito = None) -> Credito | bool:
        """
        Método que insere crédito no Gestão via a rotina de Crédito de Fornecedor.

        :param init:
        Tupla com parâmetros do ambiente.

        :param valores:
        Objeto opcional instanciado da classe Credito, utilizado para a inserção do crédito,
        caso possua atributos obrigatórios faltantes, ou o mesmo não seja passado, será gerado pelo método.

        :return:
        Retorna um objeto Credito com os dados utilizados na inserção, ou False se a inserção falhar.
        """
        
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        queries = {
            "queryFornecedorId": """
                                SELECT PESSOA_ID 
                                FROM ERP.PESSOA 
                                WHERE GRUPO_LOJA_ID = 1501
                                    AND EXISTS (
                                        SELECT 1 
                                        FROM ERP.PESSOA_CADASTRO 
                                        WHERE PESSOA_CADASTRO.PESSOA_ID = PESSOA.PESSOA_ID 
                                            AND PESSOA_CADASTRO.TIPO_CADASTRO_PESSOA_ID = 2
                                    )
                                    AND STATUS = 1
                            """,

            "queryEmpresa": """
                                SELECT LOJA_ID FROM ERP.LOJA WHERE GRUPO_LOJA_ID = 1501
                            """
        }

        queryContaReceber = FuncoesUteis.getQueryResults(init, queries)

        valoresCamposObrigatorios = {
            "P169_DATA" : "date",
            "P169_NUMERO_NOTA_SAIDA" : (int, 100000, 9999999),
            "P169_NUMERO_NOTA_ENTRADA" : (int, 100000, 9999999),
            "P169_VALOR" : (float, 20, 60)
        }

        valoresCamposObrigatorios = FuncoesUteis.geraValoresRandom(init, valoresCamposObrigatorios)
        valoresCamposObrigatorios["P169_CREDITO_FORNECEDOR_ORIGEM_ID"] = random.choice([1, 2, 21, 22])

        valoresCamposObrigatoriosLov = {
            "P169_PESSOA_FORNECEDOR_ID" : queryContaReceber["Query_queryFornecedorId"],
            "P169_LOJA_ID" : queryContaReceber["Query_queryEmpresa"]
        }

        valoresDict = FuncoesUteis.preencheCamposComunsEPopUp(init, valores, valoresCamposObrigatorios, valoresCamposObrigatoriosLov)

        valoresCamposFinal, valoresCamposPopUpLovFinal = FuncoesUteis.separaCamposComunsEPopUp(init, valoresDict, valoresCamposObrigatoriosLov)

        verificaCampos = {
            "P169_DATA" : "date",
            "P169_NUMERO_NOTA_SAIDA" : "num",
            "P169_NUMERO_NOTA_ENTRADA" : "num",
            "P169_VALOR" : "valor",
            "P169_OBSERVACAO" : "text"
        }

        verificaCampos = FuncoesUteis.filtrarCamposPorDicionario(init, verificaCampos, valoresDict)

        Components.btnClick(init, "#B79642276909633610")

        hasFrame = Components.has_frame(init, "iframe[src*='editar-visualizar']")
        if hasFrame:
            Components.btnClick(init, "#P169_DOC_SAIDA_OPCAO_LABEL")
            Components.btnClick(init, "#P169_DOC_ENTRADA_OPCAO_LABEL")

            FuncoesUteis.prepareToCompareValues(init, valoresCamposFinal, True)

            FuncoesUteis.prepareToCompareValues(init, valoresCamposPopUpLovFinal, False)

            valoresRecuperar = set(valoresDict.keys())
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Criado um Set via chaves do dicionario.",
                routine=f"{CreditoFornecedor.rotina} - insereCreditoFornecedor",
                error_details=""
            )

            valoresRecuperados = FuncoesUteis.recuperaValores(init, valoresRecuperar)

            if not FuncoesUteis.validaCamposPorRegex(init, verificaCampos):
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="WARNING",
                    message="Teste encerrado por causa dos campos aceitando valores incorretos.",
                    routine=f"{CreditoFornecedor.rotina} - insereCreditoFornecedor",
                    error_details=""
                )
                return False

            Components.btnClick(init, "#salvar")

            if not Components.has_alert(init):

                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message="Crédito inserido com sucesso!",
                    routine=f"{CreditoFornecedor.rotina} - insereCreditoFornecedor",
                    error_details=""
                )
                return CreditoFornecedor.Credito(**valoresRecuperados)
    
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Apareceu um alerta, crédito não inserido.",
                routine=f"{CreditoFornecedor.rotina} - insereCreditoFornecedor",
                error_details=""
            )
            
            return False
#END insereCreditoFornecedor(init, valores)


    @staticmethod
    def procuraCreditoFornecedor(init:tuple, credito:Optional[Credito] = None) -> bool:
        """
        Procura filtrando por um crédito de fornecedor via informações passadas pelo objeto Credito.

        :param init:
            Tupla com parâmetros do ambiente.
        
        :param credito:
            Objeto Credito opcional que será utilizado para pesquisar pelo crédito via filtragem.
            Caso não passado, sera chamado o método insereCreditoFornecedor para criar um.

        :return:
            True caso tenha sido encontrado a credito, False caso contrário.
        """

        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init
        getEnv = env_vars
        env_application_type = getEnv.get("WEB")

        if credito is None:
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Crédito não passado, criando um novo para utilizar.",
                routine=f"{CreditoFornecedor.rotina} - procuraCreditoFornecedor",
                error_details=""
            )
            FuncoesUteis.showHideFilter(init, CreditoFornecedor.filterSelector)
            credito = CreditoFornecedor.insereCreditoFornecedor(init)
            FuncoesUteis.showHideFilter(init)
        else:
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Crédito para filtragem recebido.",
                routine=f"{CreditoFornecedor.rotina} - procuraCreditoFornecedor",
                error_details=""
            )

        dictFiltro = FuncoesUteis.mapearObjeto(init, credito, CreditoFornecedor.mapeamentoObjToFiltros)
        dictFiltro["P166_SALDO"] = '-1'
        FuncoesUteis.aplyFilter(init, dictFiltro)

        achou = bool(browser.find_elements(By.CSS_SELECTOR, ".t-Button.t-Button--stretch.t-Button--hot.detalheCredito")) > 0

        if achou:
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Crédito informado achado!",
                routine=f"{CreditoFornecedor.rotina} - procuraCreditoFornecedor",
                error_details=""
            )

            return True
        
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Crédito informado não achado!",
            routine=f"{CreditoFornecedor.rotina} - procuraCreditoFornecedor",
            error_details=""
        )

        return False
#END procuraCreditoCliente(init, credito)