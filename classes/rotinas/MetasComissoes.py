from itertools import count

from classes.utils.Components import Components
from pydantic import BaseModel
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components
from pydantic import BaseModel, field_validator


class MetasComissoes:

    rotina = 'MetasComissoes'
    url='metas-por-regiao'




    @staticmethod
    def criarMeta(init):

        browser = init[0]


        Components.btnClick(init=init,seletor="#botaoMeta")

        has_frame = Components.has_frame(init=init, seletor="[title='Cadastro de Metas']")

        if has_frame:
            WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[#P311_DESCRICAO]")))


    class Metas(BaseModel):
        P311_DESCRICAO: str
        P311_SELETOR_LOJA: float
        P311_STATUS: str

        @field_validator('P311_DESCRICAO')
        def descricao_must_not_be_empty(cls, v):
            if not v:
                raise ValueError('A descrição não pode estar vazia.')
            return v

        @field_validator('P311_SELETOR_LOJA')
        def seletor_loja_must_be_positive(cls, v):
            if v <= 0:
                raise ValueError('O valor deve ser positivo.')
            return v
        


    @staticmethod
    def criarMetaComissao(init, meta: Metas):

       
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
    def salvarMeta(init, meta: Metas):


        if isinstance(meta, MetasComissoes.Metas):
            Components.btnClick(init=init,seletor="#B362593820643618646")
            return True
        else:
            return False
        

   
        

    @staticmethod
    def editarMeta(init, value):
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
                        