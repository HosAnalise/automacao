

import time
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
    _application_type = 'web'

    rotina = 'MetasPorRegiao'
    url='metas-por-regiao'


    @staticmethod
    def criarMeta(init:tuple):

        """
        Navega até a modal de criação de metas.
        
        :param init: Lista contendo o browser e outros parâmetros necessários para manipulação dos componentes.
        """



        Components.btnClick(init=init,seletor="#botaoMeta")

        return Components.has_frame(init=init, seletor="[title='Cadastro de Metas']")



    class Metas(BaseModel):
        P311_DESCRICAO: str
        P311_SELETOR_LOJA: list[str]
        P311_STATUS: str



    @staticmethod
    def criarMetaComissao(init:tuple, meta: Metas)-> Metas|bool:
        
        """
        Cria uma meta de comissão com os dados fornecidos.

        :param init: Lista contendo o browser e outros parâmetros necessários para manipulação dos componentes.
        :param meta: Objeto contendo os dados da meta a ser criada. Deve ser um objeto modelo da classe Metas.
        :return: Retorna o objeto meta criada ou False se houver erro.
        """


        try:
            
            log_manager = init[2]
            selenium_exceptions = init[6]

            regex = {"P311_DESCRICAO": 'text',
                     }

            WebDriverWait(init[0], 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#P311_DESCRICAO")))

            log_manager.add_log(level="INFO", application_type=MetasPorRegiao._application_type, message="Iniciando criação de meta de comissão.", routine=MetasPorRegiao.rotina)
            
            for key, value in meta.model_dump(exclude_none=False).items():

                if key == "P311_DESCRICAO":
                    FuncoesUteis.setValue(init=init, seletor=f"#{key}", value=value)
                if key ==  "P311_STATUS" and value == "0":
                    # Se o status for "0", clica no botão para desativar
                    Components.btnClick(init=init, seletor=f"#{key}")
                else:
                    WebDriverWait(init[0], 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"#{key}")))    
                    Apex.setValue(browser=init[0], element=key, value=value)

            log_manager.add_log(level="INFO", application_type=MetasPorRegiao._application_type, message="Campos preenchidos com sucesso.", routine=MetasPorRegiao.rotina)

            # Filtra os campos de acordo com o dicionário regex
            log_manager.add_log(level="INFO", application_type=MetasPorRegiao._application_type, message="Filtrando campos por regex.", routine=MetasPorRegiao.rotina)
            dicionarioFiltradoParaRegex = FuncoesUteis.filtrarCamposPorDicionario(init=init, dictAFiltrar=regex, dictFiltro=meta.model_dump(exclude_none=True))
            log_manager.add_log(level="INFO", application_type=MetasPorRegiao._application_type, message="Validando campos por regex.", routine=MetasPorRegiao.rotina)
            regex_ok = FuncoesUteis.validaCamposPorRegex(init=init,camposAVerificar=dicionarioFiltradoParaRegex) 
            log_manager.add_log(level="INFO", application_type=MetasPorRegiao._application_type, message="Campos validados com sucesso.", routine=MetasPorRegiao.rotina)

            return regex_ok
        except selenium_exceptions as e:
            log_manager.add_log(level="ERROR", application_type=MetasPorRegiao._application_type, message=f"Erro ao criar meta de comissão: {str(e)}", routine=MetasPorRegiao.rotina)
            return False

    @staticmethod
    def selecionarLojasRegioes(init:tuple):

           return Components.btnClick(init=init,seletor="#B362593820643618646")            
        

   
        

    # Em MetasPorRegiao.py

    @staticmethod
    def insereValorMetaLojasRegioes(init: tuple, value_to_insert: str) -> bool:
        """
        Edita o valor da meta para todos os campos de loja encontrados, valida o preenchimento
        e confere se o somatório total está correto.

        :param init: Tupla de inicialização do teste.
        :param value_to_insert: Valor a ser inserido nos campos de meta (ex: "1500,00").
        :return: True se a edição e a validação da soma forem bem-sucedidas, False caso contrário.
        """
        browser, _, log_manager, _, _, _, _, _ = init
        selenium_exceptions = init[6]
        rotina = MetasPorRegiao.rotina
        log_manager.add_log(level="INFO", application_type=MetasPorRegiao._application_type, message="Iniciando edição e validação de metas.", routine=rotina)

        try:
            # 1. Encontrar todos os campos de valor para as lojas
            seletor_campos_loja = ".apex-item-text.valorMetaLoja"
            elementos = WebDriverWait(browser, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, seletor_campos_loja))
            )

            if not elementos:
                log_manager.add_log(level="ERROR", application_type=MetasPorRegiao._application_type, message=f"Nenhum campo de meta de loja encontrado com o seletor '{seletor_campos_loja}'.", routine=rotina)
                return False

            # Variável para contar os elementos é inicializada AQUI
            elemento_count = len(elementos)
            log_manager.add_log(level="INFO", application_type=MetasPorRegiao._application_type, message=f"{elemento_count} campos de meta encontrados. Preenchendo...", routine=rotina)

            # 2. Loop corrigido: itera sobre cada elemento e atua nele diretamente
            for elemento in elementos:
                if elemento.is_displayed():
                    elemento.clear()
                    elemento.send_keys(value_to_insert)

            log_manager.add_log(level="INFO", application_type=MetasPorRegiao._application_type, message=f"Todos os campos preenchidos com o valor '{value_to_insert}'.", routine=rotina)
            

            # 3. Validar o somatório total
            seletor_total = "#P311_META_VENDA_LIQUIDA"
            WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, seletor_total))
            )

            # Pausa curta para o front-end recalcular o total. Ajuste se necessário.
            time.sleep(1)
            
            # Obter o valor do campo de somatório (geralmente um input ou span)
            # O método .get_attribute('value') é mais confiável para inputs
            valor_total_str = Apex.getValue(browser=init[0], element=seletor_total)

            # 4. Limpar e converter os valores para float de forma segura
            # Esta função auxiliar remove R$, pontos de milhar e troca vírgula por ponto decimal
            def limpar_e_converter_para_float(valor_str: str) -> float:
                if not isinstance(valor_str, str):
                    return 0.0
                valor_limpo = valor_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
                try:
                    return float(valor_limpo)
                except (ValueError, TypeError):
                    return 0.0

            valor_individual_float = limpar_e_converter_para_float(value_to_insert)
            valor_total_float = limpar_e_converter_para_float(valor_total_str)
            
            soma_esperada = valor_individual_float * elemento_count

            # 5. Comparar o valor total exibido com a soma esperada
            # Usamos uma tolerância (epsilon) para evitar problemas com arredondamento de float
            if abs(valor_total_float - soma_esperada) > 0.01:
                log_manager.add_log(level="ERROR", application_type=MetasPorRegiao._application_type, message=f"FALHA NA SOMA! Total Exibido: {valor_total_float:.2f} | Soma Esperada: {soma_esperada:.2f}", routine=rotina)
                return False
            
            log_manager.add_log(level="INFO", application_type=MetasPorRegiao._application_type, message=f"SUCESSO NA SOMA! Total Exibido: {valor_total_float:.2f} | Soma Esperada: {soma_esperada:.2f}", routine=rotina)
            
            # Se chegou até aqui, a edição e a validação foram um sucesso
            return True

        except selenium_exceptions as e:
            log_manager.add_log(level="ERROR", application_type=MetasPorRegiao._application_type, message=f"Ocorreu um erro inesperado em 'editarMeta': {str(e)}", routine=rotina)
            return False

    class SubMetas(BaseModel):
        P311_DESCRICAO_SUBMETA: str
        P311_LOJA_SUBMETA: str
        P311_CATEGORIA_ID: list[str]
        P311_HORARIO_INICIO: str
        P311_HORARIO_FIM: str
        P311_VALOR_SUBMETA: str

    def subMetas(init:tuple):
        """ Acessa a seção de submetas.

        :param init: Lista contendo o browser e outros parâmetros necessários para manipulação dos componentes.
        :return: Retorna True se a seção foi acessada com sucesso, False caso contrário.
        """
        return Components.btnClick(init=init, seletor="#R303905487677075712 > div.t-Region-header > div.t-Region-headerItems.t-Region-headerItems--controls > button > span")


    def preencherSubMetas(init:tuple, submeta: SubMetas)->SubMetas|bool:
        """
        Cria uma submeta com os dados fornecidos.
        :param init: Lista contendo o browser e outros parâmetros necessários para manipulação dos componentes.
        :param submeta: Objeto SubMetas contendo os dados da submeta a ser criada.
        :return: Retorna a submeta criada ou False se houver erro.
        """


        Regex = {
            "P311_DESCRICAO_SUBMETA": 'text',
            "P311_HORARIO_INICIO": 'horario_sem_segundos',
            "P311_HORARIO_FIM": 'horario_sem_segundos',
            "P311_VALOR_SUBMETA": 'valor'
        }
        log_manager = init[2]
        log_manager.add_log(level="INFO", application_type=MetasPorRegiao._application_type, message="Iniciando criação de submeta.", routine=MetasPorRegiao.rotina)

        FuncoesUteis.limpaCampoEPreenche(init=init, camposAEditar=submeta.model_dump())
        log_manager.add_log(level="INFO", application_type=MetasPorRegiao._application_type, message="Campos preenchidos com sucesso.", routine=MetasPorRegiao.rotina)
        dicionarioFiltradoParaRegex = FuncoesUteis.filtrarCamposPorDicionario(init=init, dictAFiltrar=Regex, dictFiltro=submeta.model_dump(exclude_none=True))
        log_manager.add_log(level="INFO", application_type=MetasPorRegiao._application_type, message="Validando campos por regex.", routine=MetasPorRegiao.rotina)
        regex_ok = FuncoesUteis.validaCamposPorRegex(init=init, camposAVerificar=dicionarioFiltradoParaRegex)
        log_manager.add_log(level="INFO", application_type=MetasPorRegiao._application_type, message="Campos validados com sucesso.", routine=MetasPorRegiao.rotina)

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
    


    def cadastrarMeta(init:tuple)-> bool:
        """
        Clica no botão de cadastrar meta.
        :param init: Lista contendo o browser e outros parâmetros necessários para manipulação dos componentes.
        :return: Retorna True se o botão foi clicado com sucesso, False caso contrário.
        """

        return Components.btnClick(init=init, seletor="#B301589282722497948")
    

    def cancelaCadastroMeta(init:tuple)-> bool:
        """
        Cancela o cadastro de meta.
        :param init: Lista contendo o browser e outros parâmetros necessários para manipulação dos componentes.
        :return: Retorna True se o cadastro foi cancelado com sucesso, False caso contrário.
        """

        return Components.btnClick(init=init, seletor="#B301589282722497948")