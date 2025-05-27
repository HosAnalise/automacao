from re import Match
from applitools.selenium import Eyes, Target, BatchInfo
from selenium.webdriver.remote.webdriver import WebDriver
import os
from applitools.common import MatchLevel



class VisualValidator:
    """
    Classe responsável por gerenciar testes visuais com o Applitools Eyes.
    """
    def __init__(self, app_name: str = "Minha Aplicação", batch_name: str = "Testes Visuais"):
        """
        Inicializa o VisualValidator com nome do app e nome do batch.
        
        Args:
            app_name (str): Nome da aplicação para exibição nos relatórios do Applitools.
            batch_name (str): Nome do grupo (batch) dos testes visuais.
        
        Raises:
            ValueError: Se a variável de ambiente 'APPLITOOLS_API_KEY' não estiver definida.
        """
        self.eyes: Eyes = Eyes()
        self.eyes.api_key = os.getenv("APPLITOOLS_API_KEY")
        if not self.eyes.api_key:
            raise ValueError("APPLITOOLS_API_KEY não está definida no ambiente!")
        
        MATCH_LEVEL = os.getenv("APPLITOOLS_MATCH_LEVEL", "LAYOUT")

        self.app_name: str = app_name
        self.batch: BatchInfo = BatchInfo(name=batch_name)
        self.eyes.match_level = MatchLevel[MATCH_LEVEL]

    def open(self, driver: WebDriver, test_name: str, viewport_size: tuple[int, int] = (1280, 720)) -> None:
        """
        Inicia o teste visual com o navegador e configurações definidas.
        
        Args:
            driver (WebDriver): Instância do navegador usada pelo Selenium.
            test_name (str): Nome do teste que aparecerá no Applitools.
            viewport_size (tuple[int, int]): Tamanho da janela do navegador (largura, altura).
        """
        self.eyes.batch = self.batch
        self.eyes.open(driver, self.app_name, test_name, viewport_size)

    def check_window(self, label: str) -> None:
        """
        Captura e valida visualmente toda a janela atual do navegador.
        
        Args:
            label (str): Descrição do ponto de verificação (checkpoint).
        """
        self.eyes.check(label, Target.window())

    def check_region(self, label: str, selector: str) -> None:
        """
        Captura e valida visualmente uma região específica da tela, definida por seletor CSS.
        
        Args:
            label (str): Descrição do ponto de verificação.
            selector (str): Seletor CSS da região a ser validada.
        """      
        self.eyes.check(label, Target.region(selector))

    def close(self) -> None:
        """
        Finaliza o teste visual e envia os resultados para o Applitools.
        """
        self.eyes.close()

    def abort(self) -> None:
        """
        Aborta o teste visual se ele ainda não tiver sido finalizado corretamente.
        Útil para cenários onde ocorre uma exceção antes da finalização.
        """
        self.eyes.abort_if_not_closed()
