
from re import S

from bson import Regex
from classes.utils.Components import Components
from pydantic import BaseModel
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components
from pydantic import BaseModel


class MetasPorRegiao:

    rotina = 'MetasPorRegiao'
    url='metas-por-regiao'




    @staticmethod
    def criarMeta(init:tuple):

        browser = init[0]


        Components.btnClick(init=init,seletor="#botaoMeta")

        has_frame = Components.has_frame(init=init, seletor="[title='Cadastro de Metas']")

        if has_frame:
            WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[#P311_DESCRICAO]")))


    class Metas(BaseModel):
        P311_DESCRICAO: str
        P311_SELETOR_LOJA: list[str]
        P311_STATUS: str



    @staticmethod
    def criarMetaComissao(init:tuple, meta: Metas):

       
        regex = {

            "P311_DESCRICAO":'alfanum',
            "P311_SELETOR_LOJA": 'num',
            "P311_STATUS": 'alfanum'
        }
        FuncoesUteis.limpaCampoEPreenche(init=init, camposAEditar=meta.model_dump())
        dicionarioFiltradoParaRegex = FuncoesUteis.filtrarCamposPorDicionario(init=init, dictAFiltrar=regex, dictFiltro=meta.model_dump(exclude_none=True))

        regex_ok = FuncoesUteis.validaCamposPorRegex(init=init,camposAVerificar=dicionarioFiltradoParaRegex) 

        return meta if not regex_ok else regex_ok

    @staticmethod
    def salvarMeta(init:tuple, meta: Metas):


        if isinstance(meta, MetasPorRegiao.Metas):
            Components.btnClick(init=init,seletor="#B362593820643618646")
            return True
        else:
            return False
        

   
        

    @staticmethod
    def editarMeta(init:tuple, value):
        """
        Edita o valor da meta para todos os elementos encontrados pelo seletor '.apex-item-text.valorMetaLoja'.

        Parâmetros:
            init: Lista contendo o browser e outros parâmetros necessários para manipulação dos componentes.
            value: Valor a ser definido nos campos de meta.

        Levanta:
            ValueError: Se nenhum elemento for encontrado, se o valor líquido for inválido ou se os valores não corresponderem.
        """

        browser = init[0]

        elementos  = WebDriverWait(browser, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".apex-item-text.valorMetaLoja")))


        if not elementos:           
            raise ValueError("Nenhum elemento encontrado com o seletor especificado.")
        
        
        for elemento in elementos:
            elemento_count += 1
            # Verifica se o elemento está visível
            if elemento.is_displayed():
                FuncoesUteis.setValue(init=init, seletor=".apex-item-text.valorMetaLoja", value=value)
                regex = {".apex-item-text.valorMetaLoja":'valor' }
                FuncoesUteis.validaCamposPorRegex(init=init, camposAVerificar=regex,apexOrNot=False)
            print(f"valor count: {elemento_count} - valor: {value}")
        valor_liquido = Apex.getValue(init=init, seletor="#P311_META_VENDA_LIQUIDA")   

        regex= {
            "P311_META_VENDA_LIQUIDA": 'valor'
        }

        if not FuncoesUteis.validaCamposPorRegex(init=init, camposAVerificar=regex, apexOrNot=False):
            raise ValueError("Valor líquido inválido.")

        if (float(valor_liquido) * elemento_count) != (float(value) * elemento_count):
            raise ValueError("Os valores não correspondem.")
        
    class SubMetas(BaseModel):
        P311_DESCRICAO_SUBMETA: str
        P311_LOJA_SUBMETA: str
        P311_CATEGORIA_ID: list[str]
        P311_HORARIO_INICIO: str
        P311_HORARIO_FIM: str
        P311_VALOR_SUBMETA: str

    def subMetas(init:tuple):

        return Components.btnClick(init=init, seletor="#R303905487677075712 > div.t-Region-header > div.t-Region-headerItems.t-Region-headerItems--controls > button > span")


    def criarSubMeta(init:tuple, submeta: SubMetas)->SubMetas|None:
        """
        Cria uma submeta com os dados fornecidos.
        :param init: Lista contendo o browser e outros parâmetros necessários para manipulação dos componentes.
        :param submeta: Objeto SubMetas contendo os dados da submeta a ser criada.
        :return: Retorna a submeta criada ou None se houver erro.        
        """


        Regex = {
            "P311_DESCRICAO_SUBMETA": 'alfanum',
            "P311_HORARIO_INICIO": 'horario_sem_segundos',
            "P311_HORARIO_FIM": 'horario_sem_segundos',
            "P311_VALOR_SUBMETA": 'valor'
        }

        FuncoesUteis.limpaCampoEPreenche(init=init, camposAEditar=submeta.model_dump())
        dicionarioFiltradoParaRegex = FuncoesUteis.filtrarCamposPorDicionario(init=init, dictAFiltrar=Regex, dictFiltro=submeta.model_dump(exclude_none=True))

        regex_ok = FuncoesUteis.validaCamposPorRegex(init=init, camposAVerificar=dicionarioFiltradoParaRegex)

        return submeta if not regex_ok else regex_ok
    

    def adicionarSubMeta(init:tuple)-> bool:
        """
        Salva a submeta criada.
        :param init: Lista contendo o browser e outros parâmetros necessários para manipulação dos componentes.
        :param submeta: Objeto SubMetas contendo os dados da submeta a ser salva.
        :return: Retorna True se a submeta foi salva com sucesso, False caso contrário.
        """

        return Components.btnClick(init=init, seletor="#B303907145743075729")

    def limparCamposSubMeta(init:tuple):
        """
        Limpa os campos de submeta.
        :param init: Lista contendo o browser e outros parâmetros necessários para manipulação dos componentes.
        :return: Retorna True se os campos foram limpos com sucesso, False caso contrário.
        """

        return Components.btnClick(init=init, seletor="#limparSubmeta")
    

    def comissoesPremios(init:tuple):
        """
        Acessa a seção de comissões e prêmios.
        :param init: Lista contendo o browser e outros parâmetros necessários para manipulação dos componentes.
        :return: Retorna True se a seção foi acessada com sucesso, False caso contrário.
        """

        return Components.btnClick(init=init, seletor="#R363928222315810106 > div.t-Region-header > div.t-Region-headerItems.t-Region-headerItems--controls > button > span")
    


