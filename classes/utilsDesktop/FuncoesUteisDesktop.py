
from cycler import V
from classes.utils.LogManager import LogManager
from pywinauto.findwindows import ElementNotFoundError, ElementAmbiguousError
from pywinauto.timings import TimeoutError
from pywinauto.base_wrapper import ElementNotEnabled
from pywinauto.controls.hwndwrapper import ControlNotEnabled,ControlNotVisible



class FuncoesUteisDesktop():
    def __init__(self,env_vars):
        self.env_vars = env_vars
        self.application_type = self.env_vars.get("APPLICATION_TYPE")
        self.log = LogManager()
       
        


    
    def compareValuesDesktop(self,obj:dict) -> bool:
        """
        Compara pares de valores em um dicionário e registra logs de sucesso ou erro.

        :param obj: (dict): Dicionário onde cada chave mapeia para uma tupla (valor_esperado, valor_atual).

        :return:
            bool: True se todos os valores forem iguais, False se houver diferenças.Também cria logs que mostram os valores com diferenças
        """
        

        if not isinstance(obj, dict):
            self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="compareValues - O objeto passado não é um dicionário válido.",
                routine="",
                error_details=""
            )
            return False

        valoresDiferentes = {chave: (v1, v2) for chave, (v1, v2) in obj.items() if v1 != v2}

        if not valoresDiferentes:
            self.log.add_log(
                application_type=self.application_type,
                level="INFO",
                message="Todos valores foram inseridos corretamente.",
                routine="",
                error_details=""
            )
            return True
        else:
            self.log.add_log(
                application_type=self.application_type,
                level="ERROR",
                message="Alguns valores foram inseridos incorretamente.",
                routine="",
                error_details=""
            )
            
            for chave, (v1, v2) in valoresDiferentes.items():
                self.log.add_log(
                    application_type=self.application_type,
                    level="INFO",
                    message=f"Valor incorreto - {chave}: {v1} (esperado) ≠ {v2} (atual)",
                    routine="",
                    error_details=""
                )

            return False
        
    @staticmethod
    def pywinauto_exceptions():
        return (
            ElementNotFoundError,
            ElementAmbiguousError,
            TimeoutError,
            ElementNotEnabled,
            RuntimeError,
            AttributeError,
            TypeError,
            ControlNotEnabled,
            ControlNotVisible,
            IndexError,
            ValueError,
            KeyError,
            AssertionError,
            OSError,
            ImportError,
            NameError,
            UnboundLocalError,
            ReferenceError,
            MemoryError,
            OverflowError,
            ZeroDivisionError,
            EnvironmentError,
            IOError,
            WindowsError,
            FileNotFoundError,
            PermissionError,
            IsADirectoryError,  
            NotADirectoryError,
            BlockingIOError,
            ChildProcessError,
            ConnectionError,    

        )
