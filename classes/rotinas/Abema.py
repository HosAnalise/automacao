from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from classes.utils.GerarDados import GeradorDados  
from classes.utils.ApexUtil import Apex
from classes.utils.FuncoesUteis import FuncoesUteis
from classes.utils.Components import Components
from classes.rotinas.ExtratoContas import ExtratoContas
from time import sleep

class AbemaRelatorioPrestador:
    
    rotina = "Abema"

    filterSelector = "#P56_PRESTADOR_1"
    filters =[
        "P56_PRESTADOR_1",
        "P56_INCLUIR_INATIVOS_0",
        "P56_EMPRESA_ASSOCIADA",
        "P56_CONTRATOS",
        "P56_COMPETENCIA_FOLHA_1",
        "P56_COMPETENCIA_FOLHA_FIM_1",
        "P56_STATUS_LOTE",
        "prestadorempresa_saved_reports"
    ]