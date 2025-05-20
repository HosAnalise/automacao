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


class CreditoCliente:
    url = "listagem-credito-cliente"
    filterSelector = "#P163_TIPO_VALOR"


    class Filtros(BaseModel):
        P163_SITUACAO_SELECIONADA : Optional [str] = None #exemplo de get = '1, 2, 3, 5'
        P163_ORIGEM : Optional [str] = None #exemplo de get = ['3', '1']
        P163_TIPO_VALOR : Optional [str] = None #exemplo de get = '1'
        P163_VALOR_MIN : Optional [str] = None #exemplo de get = '3,05'
        P163_VALOR_MAX : Optional [str] = None #exemplo de get = '10,66'
        P163_TIPO_DATA : Optional [str] = None #exemplo de get = '1'
        P163_DATA_INICIAL : Optional [str] = None #exemplo de get = '13/05/2025'
        P163_DATA_FINAL : Optional [str] = None #exemplo de get = '13/05/2025'
        P163_MOTIVO : Optional [str] = None #exemplo de get = ['teste multiplas', 'd']
        P163_CLIENTE : Optional [str] = None #exemplo de get = ['2747364']
        P163_EMPRESA : Optional [str] = None #exemplo de get = ['2381', '3625']

        @field_validator('*', mode='before')
        @classmethod
        def forceString(cls, v):
            return str(v) if v is not None else None


    class Credito(BaseModel):
        P164_CLIENTE: Optional[str] = None  # exemplo de get = '2747365'
        P164_VALOR: Optional[str] = None # exemplo de get = '52,88'
        P164_RECEBIDO_EM: Optional[str] = None # exemplo de get = '10'
        P164_DATA_RECEBIMENTO: Optional[str] = None # exemplo de get = '08/05/2025'
        P164_EMPRESA: Optional[str] = None # exemplo de get = '4105'
        P164_NA_CONTA: Optional[str] = None # exemplo de get = '7210'
        P164_MOTIVO: Optional[str] = None  # exemplo de get = 'teste'

        @field_validator('*', mode='before')
        @classmethod
        def forceString(cls, v):
            return str(v) if v is not None else None


    mapeamentoObjToFiltros = {
        "P164_CLIENTE": ["P163_CLIENTE"],
        "P164_VALOR": ["P163_VALOR_MIN", "P163_VALOR_MAX"],
        "P164_DATA_RECEBIMENTO": ["P163_DATA_INICIAL", "P163_DATA_FINAL"],
        "P164_EMPRESA": ["P163_EMPRESA"],
        "P164_MOTIVO": ["P163_MOTIVO"]
    }


    @staticmethod
    def insereCreditoCliente(init:tuple, valores:Credito = None) -> Credito | bool:
        """
        Método que insere crédito no Gestão via a rotina de Crédito de Cliente.

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
            "queryEmpresa": """
                                SELECT LOJA_ID FROM ERP.LOJA WHERE GRUPO_LOJA_ID = 1501
                            """,

            "queryContaId": """
                            SELECT CONTA.CONTA_ID  
                            FROM ERP.CONTA
                            JOIN ERP.CONTA_ESPECIFICACAO ON CONTA.CONTA_ID = CONTA_ESPECIFICACAO.CONTA_ID
                            LEFT JOIN ERP.LOJA ON LOJA.LOJA_ID = CONTA_ESPECIFICACAO.LOJA_ID
                            WHERE CONTA_ESPECIFICACAO.GRUPO_LOJA_ID = 1501
                                AND CONTA.TIPO_CONTA_ID IN (1, 2)
                                AND (CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IN (1) OR CONTA_ESPECIFICACAO.TIPO_CONTA_BANCARIA_ID IS NULL)
                                AND (CONTA.CONTA_ID IN (0) OR CONTA_ESPECIFICACAO.STATUS IN (1))
                        """
        }

        queryContaReceber = FuncoesUteis.getQueryResults(init, queries)

        valoresCamposObrigatorios = {
            "P164_VALOR" : (float, 20, 50),
            "P164_DATA_RECEBIMENTO" : "date",
        }

        valoresCamposObrigatorios = FuncoesUteis.geraValoresRandom(init, valoresCamposObrigatorios)

        valoresCamposObrigatorios["P164_RECEBIDO_EM"] = random.choice([1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 41, 61, 81])
        valoresCamposObrigatorios["P164_EMPRESA"] = queryContaReceber["Query_queryEmpresa"]
        valoresCamposObrigatorios["P164_NA_CONTA"] = queryContaReceber["Query_queryContaId"]


        if valores is not None:
            dictValores = valores.model_dump(exclude_none=True)
            for seletor in valoresCamposObrigatorios:
                if dictValores.get(seletor) is None:
                    dictValores[seletor] = valoresCamposObrigatorios[seletor]

        else:
            dictValores = valoresCamposObrigatorios.copy()
        
        Components.btnClick(init, "#B52784763246400536")
        sleep(2)
        hasFrame = Components.has_frame(init, "iframe[src*='lancamento-credito-cliente']")
        if hasFrame:
            FuncoesUteis.setFilters(init, dictValores)

            valoresRecuperar = set(dictValores.keys())
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Criado um Set via chaves do dicionario.",
                routine="",
                error_details=""
            )

            valoresRecuperados = FuncoesUteis.recuperaValores(init, valoresRecuperar)

            Components.btnClick(init, "#B53155440292595715")
            if not Components.has_alert(init):
                browser.switch_to.default_content()
            else:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message="Apareceu um alerta, crédito não inserido.",
                    routine="",
                    error_details=""
                )

            try:
                WebDriverWait(browser, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#listagemSecundaria_actions_button")) # utilizado botão de ações, para que não seja bloqueado pelo filtro lateral.
                )
                sucesso = True
            except TimeoutException:
                sucesso = False

            if sucesso:
                Log_manager.add_log(
                    application_type=env_application_type,
                    level="INFO",
                    message="Crédito inserido com sucesso!",
                    routine="",
                    error_details=""
                )
                return CreditoCliente.Credito(**valoresRecuperados)

        return False
#END insereCreditoCliente(init, valores)

    @staticmethod
    def procuraCreditoCliente(init:tuple, credito:Optional[Credito] = None) -> bool:
        """
        Procura filtrando por um crédito de cliente via informações passadas pelo objeto Credito.

        :param init:
            Tupla com parâmetros do ambiente.
        
        :param credito:
            Objeto Credito opcional que será utilizado para pesquisar pelo crédito via filtragem.
            Caso não passado, sera chamado o método insereCreditoCliente para criar um.

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
                routine="",
                error_details=""
            )
            FuncoesUteis.showHideFilter(init, CreditoCliente.filterSelector)
            credito = CreditoCliente.insereCreditoCliente(init)
        else:
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Crédito para filtragem recebido.",
                routine="",
                error_details=""
            )

        dictFiltro = FuncoesUteis.mapearObjeto(init, credito, CreditoCliente.mapeamentoObjToFiltros)
        dictFiltro["P163_TIPO_VALOR"] = '1'
        dictFiltro["P163_TIPO_DATA"] = '1'

        FuncoesUteis.aplyFilter(init, dictFiltro)

        achou = bool(browser.find_elements(By.CSS_SELECTOR, ".fa.fa-edit.icon-color.edit")) > 0

        if achou:
            Log_manager.add_log(
                application_type=env_application_type,
                level="INFO",
                message="Crédito informado achado!",
                routine="",
                error_details=""
            )

            return True
        
        Log_manager.add_log(
            application_type=env_application_type,
            level="INFO",
            message="Crédito informado não achado!",
            routine="",
            error_details=""
        )

        return False
#END procuraCreditoCliente(init, credito)