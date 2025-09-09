from jira import JIRA
from jira.resources import Issue
from jira.exceptions import JIRAError
from classes.utils.LogManager import LogManager
import os

log_manager = LogManager()


class JiraApi:




    def __init__(self):
        self.token = os.environ.get("JIRA_API_TOKEN")
        self.base_url = os.environ.get("JIRA_API_BASE_URL")
        self.email = os.environ.get("EMAIL_JIRA")

    def connect(self) -> JIRA | None:
        """
        Conecta a api do Jira e retorna uma instância da classe JIRA.
        """
      
        try:
            jira = JIRA(server=self.base_url, basic_auth=(self.email, self.token))
            return jira
        except JIRAError as e:
            log_manager.add_error(
                                    level="ERROR",
                                    message=f"Erro ao conectar ao Jira: {e}",
                                    application_type="JIRA",
                                    error_details=str(e),
                                    routine="JiraApi.connect"
                                 )
            print(f"Erro ao conectar ao Jira: {e}")
            return None



    def get_cards_jql(self,jql) -> dict | None:
        """
        Obtém os detalhes de um cartão do Jira.

        :param jql: A consulta JQL para buscar os cartões.

        :return: Um dicionário com os detalhes dos cartões encontrados ou None em caso de erro.

        project_key = "FIN"
        status_id = 10039  # O ID único do seu status "Teste"
        f'project = "{project_key}" AND status = {status_id}' 
        """      
        
        jql_query = jql       

        jira = self.connect()
        if not jira:
            return None

        try:            
            return jira.search_issues(jql_str=jql_query,maxResults=False) 
        except JIRAError as e:
            log_manager.add_error(
                                    level="ERROR",
                                    message=f"Erro ao obter cartão do Jira: {e}",
                                    application_type="JIRA",
                                    error_details=str(e),
                                    routine="JiraApi.get_card_in_test"
                                 )
            print(f"Erro ao obter cartão do Jira: {e}")
            return None
        

    def get_projects(self):
        """
        Obtém a lista de projetos do Jira.
        """
        jira = self.connect()

        if not jira:
            return None

        try:
            
            return jira.projects()
        except JIRAError as e:
            log_manager.add_error(
                                    level="ERROR",
                                    message=f"Erro ao obter projetos do Jira: {e}",
                                    application_type="JIRA",
                                    error_details=str(e),
                                    routine="JiraApi.get_projects"
                                 )
            print(f"Erro ao obter projetos do Jira: {e}")
            return None
        
    def get_status(self):
        jira = self.connect()
        if not jira:
            return None

        try:
            return jira.statuses()
        except JIRAError as e:
            log_manager.add_error(
                                    level="ERROR",
                                    message=f"Erro ao obter status do Jira: {e}",
                                    application_type="JIRA",
                                    error_details=str(e),
                                    routine="JiraApi.get_status"
                                 )
            print(f"Erro ao obter status do Jira: {e}")
            return None
    
    
    def get_issue(self, issue_id:str) -> Issue | None:

        """
        Obtém os detalhes de uma issue específica do Jira pelo seu ID.
        """
        try:
           
            return self.connect().issue(issue_id) if self.connect() else None
        except JIRAError as e:
            log_manager.add_error(
                                    level="ERROR",
                                    message=f"Erro ao obter issue do Jira: {e}",
                                    application_type="JIRA",
                                    error_details=str(e),
                                    routine="JiraApi.get_issue"
                                 )
            return None  
        
    def get_comments(self, issue_id: str):
        """
        Obtém os comentários de uma issue específica do Jira pelo seu ID.
        """
        try:
            jira = self.connect()
            if not jira:
                return None


            return jira.comments(issue_id)
        except JIRAError as e:
            log_manager.add_error(
                                    level="ERROR",
                                    message=f"Erro ao obter comentários do Jira: {e}",
                                    application_type="JIRA",
                                    error_details=str(e),
                                    routine="JiraApi.get_comments"
                                 )
            print(f"Erro ao obter comentários do Jira: {e}")
            return None
    def get_text_comments(self, issue_id: str) -> list[str] | None:
        """
        Obtém os textos dos comentários de uma issue específica do Jira pelo seu ID.
        """
        try:
            jira = self.connect()
            if not jira:
                return None

            comments = jira.comments(issue_id)
            return [comment.body for comment in comments]
        except JIRAError as e:
            log_manager.add_error(
                                    level="ERROR",
                                    message=f"Erro ao obter textos dos comentários do Jira: {e}",
                                    application_type="JIRA",
                                    error_details=str(e),
                                    routine="JiraApi.get_text_comments"
                                 )
            print(f"Erro ao obter textos dos comentários do Jira: {e}")
            return None    


    def insert_comment(self, issue_id: str, comment: str) -> bool:
        """
        Insere um comentário em uma issue específica do Jira.

        :param issue_id: O ID da issue onde o comentário será inserido.
        :param comment: O texto do comentário a ser inserido.

        :return: True se o comentário foi inserido com sucesso, False caso contrário.
        """
        try:
            jira = self.connect()
            if not jira:
                return False

            jira.add_comment(issue_id, comment)
            return True
        except JIRAError as e:
            log_manager.add_error(
                                    level="ERROR",
                                    message=f"Erro ao inserir comentário no Jira: {e}",
                                    application_type="JIRA",
                                    error_details=str(e),
                                    routine="JiraApi.insert_comment"
                                 )
            print(f"Erro ao inserir comentário no Jira: {e}")
            return False    



if __name__ == "__main__":
    jira_api = JiraApi()
    card_in_test = jira_api.get_card_in_test()


    if card_in_test:
        for card in card_in_test:
            print(f"Cartão em teste obtido com sucesso: {card.fields.summary}")
    else:
        print("Não foi possível obter o cartão em teste.")