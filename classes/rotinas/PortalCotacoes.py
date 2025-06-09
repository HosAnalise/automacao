from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.GerarDados import GeradorDados  
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components
from classes.rotinas.ExtratoContas import ExtratoContas

class PortalCotacoes:

    filterSelector = "#P1_REGIAO"
    rotina = "Portal de Cotações"
    filters =[
        "P1_REGIAO",
        "P1_TIPO_PERIODO",
        "P1_DATA_INICIO",
        "P1_DATA_FIM",
        "P1_NOME_PEDIDO",
        "P1_NUMERO_PEDIDO",
        "P1_SITUACAO"]

    @staticmethod
    def exportCotacao(init):
        browser,login,Log_manager,get_ambiente,env_vars,seletor_ambiente,screenshots,oracle_db_connection = init

        Components.btnClick(init, "#L197697988027934774")
        Components.btnClick(init, "#menu_L197697988027934774_0i")

    
#END exportCotacao(init)