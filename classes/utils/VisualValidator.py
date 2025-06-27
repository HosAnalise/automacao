import os
from typing import List, Union, Tuple

from applitools.common import BatchInfo, Configuration, MatchLevel, Region
from applitools.selenium import ClassicRunner, Eyes, Target
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver

class VisualValidator:
    """
    Classe aprimorada para gerenciar testes visuais com o Applitools Eyes,
    utilizando Runners e o objeto Configuration para um design moderno e robusto.
    """

    def __init__(self, app_name: str = "Automação Web", batch_name: str = "Testes Visuais"):
        """
        Inicializa o validador, o runner e o objeto de configuração.

        Args:
            app_name (str): Nome da aplicação para exibição nos relatórios do Applitools.
            batch_name (str): Nome do grupo (batch) dos testes visuais.
        """
        # 1. Inicializa o Runner para gerenciar todos os testes
        self.runner = ClassicRunner()
        self.eyes = None # O objeto Eyes será criado por teste

        # 2. Centraliza todas as configurações no objeto Configuration
        self.config = Configuration()
        self.config.set_app_name(app_name)
        self.config.set_batch(BatchInfo(name=batch_name))

        # Configura a API Key a partir do ambiente
        api_key = os.getenv("APPLITOOLS_API_KEY")
        if not api_key:
            raise ValueError("APPLITOOLS_API_KEY não está definida no ambiente!")
        self.config.set_api_key(api_key)

        # Configura o nível de correspondência a partir do ambiente, com um padrão seguro
        match_level_str = os.getenv("APPLITOOLS_MATCH_LEVEL", "LAYOUT")
        self.config.set_default_match_level(MatchLevel[match_level_str])
        
        # Opcional: define uma espera padrão. Pode ser removido se as esperas do Selenium forem suficientes.
        self.config.set_wait_before_capture(1000)

    def start_test(self, driver: WebDriver, test_name: str, viewport_size: tuple[int, int] = (1280, 720)) -> None:
        """
        Inicia um novo teste visual. Cria a instância do Eyes e abre a conexão.

        Args:
            driver (WebDriver): Instância do navegador usada pelo Selenium.
            test_name (str): Nome do teste que aparecerá no Applitools.
            viewport_size (tuple[int, int]): Tamanho da janela do navegador (largura, altura).
        """
        # Cria uma nova instância do Eyes para cada teste, associada ao runner
        self.eyes = Eyes(self.runner)
        # Aplica a configuração predefinida
        self.eyes.set_configuration(self.config)
        
        # Abre o teste
        self.eyes.open(driver, self.config.app_name, test_name, {'width': viewport_size[0], 'height': viewport_size[1]})

    def check_window(self, label: str, ignore_regions: List[Union[WebElement, Tuple[By, str], Region]] = None) -> None:
        """
        Captura a janela inteira, com opção de ignorar regiões específicas.

        Args:
            label (str): Descrição (tag) do ponto de verificação.
            ignore_regions (List): Uma lista de regiões para ignorar. Pode conter:
                                   - WebElements do Selenium.
                                   - Tuplas de seletor (By, "meu-seletor").
                                   - Objetos Region(left, top, width, height).
        """
        if not self.eyes or not self.eyes.is_open:
            raise Exception("O teste não foi iniciado. Chame start_test() primeiro.")

        target = Target.window().fully()

        if ignore_regions:
            for region in ignore_regions:
                # O método ignore é fluente e pode ser encadeado
                if isinstance(region, Region):
                    target = target.ignore(region)
                elif isinstance(region, WebElement):
                    target = target.ignore(region)
                elif isinstance(region, tuple) and len(region) == 2:
                    # O método ignore aceita um seletor By
                    target = target.ignore(region)
        
        self.eyes.check(label, target)

    def check_region(self, label: str, element: Union[WebElement, Tuple[By, str]], is_fully: bool = True) -> None:
        """
        Captura e valida uma região específica da tela.

        Args:
            label (str): Descrição do ponto de verificação.
            element (Union[WebElement, Tuple[By, str]]): O WebElement ou seletor da região.
            is_fully (bool): Se True, rola a página para capturar a região inteira.
        """
        if not self.eyes or not self.eyes.is_open:
            raise Exception("O teste não foi iniciado. Chame start_test() primeiro.")

        target = Target.region(element)
        if is_fully:
            target = target.fully()
            
        self.eyes.check(label, target)

    def close_test(self) -> None:
        """
        Finaliza o teste visual. Não lança exceção imediatamente.
        """
        if self.eyes:
            self.eyes.close_async()

    def abort_test_if_needed(self) -> None:
        """
        Aborta o teste se ele ainda não tiver sido finalizado.
        """
        if self.eyes:
            self.eyes.abort()

    def get_all_results(self, raise_ex: bool = True):
        """
        Coleta todos os resultados dos testes executados pelo runner.
        Deve ser chamado no final de toda a suíte de testes.

        Args:
            raise_ex (bool): Se True, lança DiffsFoundError se houver diferenças visuais.
        
        Returns:
            TestResultsSummary: Um objeto com o resumo de todos os resultados.
        """
        return self.runner.get_all_test_results(raise_ex=raise_ex)