from datetime import datetime, timedelta
from traceback import print_tb
from dotenv import load_dotenv
import os
import uuid  # Para gerar identificadores únicos
from pymongo import MongoClient  # Importando MongoClient
from pymongo.server_api import ServerApi
from collections import defaultdict
from pydantic import BaseModel






load_dotenv()


class LogManager:
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


    
    def get_error_logs(self, execution_id:str = None)-> list:
        """
        Recupera os logs com level = ERROR e categoriza eles por executionId.
              
        :param execution_id: id de execução especifico a ser filtrado
        
        """
        logs_por_execucao = defaultdict(list)

        filtro = {}
        if execution_id:
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
