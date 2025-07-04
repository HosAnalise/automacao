from datetime import datetime, timedelta
import re
from typing import Optional
from dotenv import load_dotenv
import os
import uuid  # Para gerar identificadores únicos
from pydantic import BaseModel
from pymongo import MongoClient  # Importando MongoClient
from pymongo.server_api import ServerApi
from collections import defaultdict






load_dotenv()


class LogManager:



    class LogModel(BaseModel) :
        application_type:str
        level:str
        message:str
        routine:str
        error_details:Optional[str]=None
        timestamp:str = datetime.now().strftime("%d/%m/%Y %H:%M:%S:%f")

    class LogForInsert(BaseModel):
        execution_id:str
        dev:str
        logs: list['LogManager.LogModel']
        timestamp:str = datetime.now().strftime("%d/%m/%Y %H:%M:%S:%f")

    class LogForError(BaseModel):
        execution_id: str
        logs: list['LogManager.LogModel']
        timestamp: str = datetime.now().strftime("%d/%m/%Y %H:%M:%S:%f")    




    def __init__(self):
        # Carregar variáveis do .env
        mongodb_uri = os.getenv("MONGODB_URI")
        db_name = os.getenv("DB_NAME")
        collection_name = os.getenv("COLLECTION_NAME")
        dev = os.getenv("DEV")
        dias_pra_deletar_logs = os.getenv('DAYS_TO_DELETE_LOGS')
        dias_pra_deletar_logs = int(dias_pra_deletar_logs) if dias_pra_deletar_logs else 7 
        
        if not mongodb_uri or not db_name or not collection_name:
            raise ValueError("Faltando variáveis de ambiente: MONGODB_URI, DB_NAME ou COLLECTION_NAME")

        # Conexão com o MongoDB
        self.client = MongoClient(mongodb_uri,server_api=ServerApi('1'))
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

        # Inicializa um array para armazenar logs durante a execução
        self.logs = []
        self.days = dias_pra_deletar_logs

        self.dev = dev

   

        

    def _generate_execution_id(self)->str:
        """
        Gera um identificador único para cada execução de script.
        """
        return str(uuid.uuid4())  # Gerando um ID único para a execução

    def add_log(self,application_type:str, level:str, message:str, routine:str, error_details:str|None =None):
        """
        Adiciona um log ao array de logs em memória.
        
        :param level: Nível do log (ex: "INFO", "ERROR", "DEBUG")
        :param message: Mensagem do log
        :param routine: Nome da rotina onde o log foi gerado
        :param error_details: Detalhes do erro (opcional, padrão None)
        """
        log_entry = {
            "application_type": application_type,
            "level": level,
            "message": message,
            "routine": routine,
            "error_details": error_details,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S:%f")

        }

        # Adiciona o log ao array de logs
        self.logs.append(log_entry)

    def insert_logs_for_execution(self,logName:str|None =None):
        """
        Insere todos os logs coletados durante a execução em um único documento no banco de dados.
        
        :param logName: nome do log que será inserido junto com o id de execução
        """
       
        execution_id = self._generate_execution_id()  # Gerar novo ID caso não seja fornecido

        execution_entry = {
            
            "execution_id": f"{logName}_{execution_id}",  # ID da execução
            "dev": self.dev,
            "logs": self.logs,  # Lista de logs
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S:%f")
        }


        try:
            # Inserção do documento com logs na coleção do MongoDB
            result = self.collection.insert_one(execution_entry)
            print(f"Execução inserida com ID: {result.inserted_id}")
        except Exception as e:
            print(f"Erro ao inserir execução: {e}")
        finally:
            self.insert_error_log()    




    def get_logs_not_async(self,collection: str = "web_logs") -> list:
        """
        Recupera logs de uma Collection específica do MongoDB.
        
    
        :param collection: Nome da Collection onde os logs serão recuperados. Padrão é 'log'.
        """
        
        self.collection = self.db[collection]

        if self.collection is None:
            raise ValueError(f"Collection '{collection}' not found in dynamic_collections_sync.")

        cursor = self.collection.find({})
        logs = []
        for log in cursor:
            logs.append(log)
        return logs

    def get_error_logs(self, execution_id:str|None = None)-> dict:
        """
        Recupera os logs com level = ERROR e categoriza eles por executionId.
              
        :param execution_id: id de execução especifico a ser filtrado
        
        """
        logs_por_execucao = defaultdict(list)

        filtro = {}
        if execution_id is not None:
            filtro["execution_id"] = execution_id


        logs_cursor = self.collection.find(filtro)

        for doc in logs_cursor:
            exec_id = doc.get("execution_id", "sem_execucao")

            for log in doc.get("logs", []):
                level = str(log.get("level", "")).strip().upper()
                if level == "ERROR":
                    logs_por_execucao[exec_id].append(log)

        # Exemplo de print para visualizar agrupado
        for exec_id, erros in logs_por_execucao.items():
            print(f"\nExecution ID: {exec_id}")
            for erro in erros:
                print(f" - {erro['message']}")

        return logs_por_execucao
    

    def get_all_logs(self) -> list:
        """
        Recupera todos os documentos de log do banco.
        """
        return list(self.collection.find({}))
    

    def filtrar_logs_por_rotina(self, docs: list) -> dict:
        """
        Agrupa os logs por execution_id.
        
        :param docs: lista de documentos brutos do Mongo
        :return: dict com execution_id como chave e lista de logs como valor
        """
        agrupado = defaultdict(list)

        for doc in docs:
            exec_id = doc.get("execution_id", "sem_execucao")
            for log in doc.get("logs", []):
                agrupado[exec_id].append(log)

        return agrupado
    

    def remover_logs_ambiguos(self, group: dict) -> dict:
        """
        Remove logs que não são ERROR ou que batem com padrões de erros ignorados (via regex).

        :param group: dict de logs agrupados por routine

        :return: dict filtrado com apenas logs relevantes
        """

        # Lista de padrões que representam erros comuns/irrelevantes
        padroes_ignorados = [
            r"nosuchelementexception",
            r"timeoutexception",
            r"elementclickinterceptedexception",
            r"staleelementreferenceexception",
            r"elementnotinteractableexception",
            r"gethandleverifier",
            r"message:\s*",
            r"element click intercepted",
            r"has no attribute",
            r"cannot access local variable",
            r"stale element reference",
            r"Valor incorreto - ",
            r"Message: ",
            r"Alguns valores foram inseridos incorretamente.",
            r"positional argument",
            r"'P"
        ]

        # Compila todos os padrões em regex com IGNORECASE
        regex_erros_ignorados = [re.compile(p, re.IGNORECASE) for p in padroes_ignorados]

        def is_relevante(log):
            # Garantia de tratamento mesmo que campos estejam ausentes
            level = str(log.get("level", "")).strip().upper()
            if level not in ("ERROR", "WARNING"):
                return False

            msg = str(log.get("error_details", "") or log.get("message", "")).strip()

            # Retorna False se QUALQUER padrão bater com a mensagem
            return not any(padrao.search(msg) for padrao in regex_erros_ignorados)

        # Monta novo dicionário com apenas os logs relevantes
        filtrado = {}

        for exec_id, logs in group.items():
            relevantes = [log for log in logs if is_relevante(log)]
            if relevantes:
                filtrado[exec_id] = relevantes

        return filtrado
        
    
    def rankear_rotinas_por_erros(self, filtrado: dict) -> dict:
        """
        Ordena as rotinas com base na quantidade de erros relevantes.

        :param filtrado: dict de logs relevantes por rotina
        :return: dict ordenado por total de erros (desc)
        """
        resultado = {
            exec_id: {
                "total_errors": len(logs),
                "errors": logs
            }
            for exec_id, logs in filtrado.items()
        }

        return dict(
            sorted(resultado.items(), key=lambda item: item[1]["total_errors"], reverse=True)
        )
    


    def analisar_erros(self,collection_name:str|None = None) -> dict:
        todos = self.get_logs_not_async()
        agrupado = self.filtrar_logs_por_rotina(todos)
        filtrado = self.remover_logs_ambiguos(agrupado)
        ranqueado = self.rankear_rotinas_por_erros(filtrado)
        return ranqueado
    

    def delete_logs_older_than(self, days:int=None):
        if days is None:
            days = self.days
        """
        Exclui logs que são mais antigos do que o número de dias fornecido.

        :param days: Número de dias para verificar se o log é mais antigo. O padrão é 7 dias.
        """
        # Definir a data limite como datetime
        date_limit = datetime.now() - timedelta(days=days)

        # Buscar logs e converter os timestamps antes da exclusão
        logs_to_delete = []

        for log in self.collection.find({}):
            try:
                log_date = datetime.strptime(log["timestamp"], "%d/%m/%Y %H:%M:%S:%f")  # Converte string para datetime
                if log_date < date_limit:
                    logs_to_delete.append(log["_id"])  # Coleta os IDs dos logs antigos
            except ValueError:
                print(f"Erro ao converter timestamp: {log['timestamp']}")  # Debug para logs corrompidos

        # Excluir logs antigos pelo ID
        if logs_to_delete:
            result = self.collection.delete_many({"_id": {"$in": logs_to_delete}})
            print(f"{result.deleted_count} logs foram deletados.")
        else:
            print("Nenhum log antigo encontrado.")

    def insert_error_log(self):    
        """
        Insere logs de erro em um documento separado no banco de dados.
        
        :param log: Instância de LogForError contendo os logs de erro
        """
        log = self.analisar_erros()  # Obtém os logs de erro analisados
        self.collection = self.db["error_logs"]  # Coleção específica para logs de erro
        
        try:
            # Inserção do documento com logs de erro na coleção do MongoDB
            result = self.collection.insert_one(log)
            print(f"Erro inserido com ID: {result.inserted_id}")
        except Exception as e:
            print(f"Erro ao inserir log de erro: {e}")


# Exemplo de uso
if __name__ == "__main__":
    log_manager = LogManager()

    # Gerar um ID para a execução do script (simulando a execução de um script)
    execution_id = log_manager._generate_execution_id()

    # Adicionando logs ao array durante a execução
    log_manager.add_log("INFO", "Início do script", routine="MainScript")
    log_manager.add_log("DEBUG", "Processando dados", routine="MainScript")
    log_manager.add_log("ERROR", "Erro ao processar dados", routine="DataProcessing", error_details="Dados inválidos")
    log_manager.add_log("INFO", "Fim da execução do script", routine="MainScript")

    # Após a execução, inserindo os logs no banco de dados
    log_manager.insert_logs_for_execution(execution_id)

    # Buscando logs da execução específica
    log_manager.get_logs(
        execution_id="some_execution_id", 
        limit=10, 
        start_date="01/02/2025 00:00:00:000000", 
        end_date="05/02/2025 23:59:59:999999"
    )


# ✅ Estratégia recomendada
# 📌 Níveis de severidade
# Use a hierarquia comum:

# Level	Quando usar
# DEBUG	Informações técnicas detalhadas (usado em desenvolvimento ou troubleshooting)
# INFO	Ações esperadas (ex: "Campo preenchido com sucesso")
# WARNING	Algo deu errado, mas o processo seguiu normalmente
# ERROR	Algo falhou e impediu o fluxo normal
# CRITICAL	Situação grave que requer atenção imediata (pode ser opcional no seu caso)