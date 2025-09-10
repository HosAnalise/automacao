import logging

from typing import Dict, Any, Optional, List
from functools import lru_cache

from fastapi import FastAPI, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from pydantic_ai.models.google import GoogleModel

from classes.utils.JiraApi import JiraApi
from classes.utils.AI import AI, JiraIssueEmbedding, TestScenarioService
from classes.utils.ChromaDBManager import ChromaDBManager

logging.basicConfig( format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="Jira Test Scenario Generator",
    description="Um serviço que recebe webhooks do Jira para gerar cenários de teste com IA.",
    version="1.0.0"
)


class JiraIssueFields(BaseModel):
    summary: str = ""
    description: Optional[str] = ""
    tester_info: Optional[List[Dict[str, Any]]] = Field(alias="customfield_10077", default=[])

class JiraIssue(BaseModel):
    key: str
    fields: JiraIssueFields

class JiraWebhookPayload(BaseModel):
    webhookEvent: str
    issue: JiraIssue


@lru_cache(maxsize=1)
def get_jira_client() -> JiraApi:
    """Retorna uma instância singleton do cliente Jira."""
    return JiraApi()

@lru_cache(maxsize=1)
def get_db_manager() -> ChromaDBManager:
    """Retorna uma instância singleton do gerenciador do ChromaDB."""
    return ChromaDBManager()


MODEL_NAME = "gemini-1.5-pro-latest"

@lru_cache(maxsize=1)
def get_ai_model() -> GoogleModel:
    """
    Cria e retorna uma instância singleton do modelo GoogleModel,
    configurada com a chave de API do ambiente.
    """
    
    return GoogleModel(model_name=MODEL_NAME, provider="google")

def get_test_scenario_service(
    jira_client: JiraApi = Depends(get_jira_client),
    db_manager: ChromaDBManager = Depends(get_db_manager),
    ai_model: AI = Depends(get_ai_model),
) -> TestScenarioService:
    """Cria e retorna o serviço principal, injetando suas dependências."""
    return TestScenarioService(
        jira_client=jira_client, db_manager=db_manager, ai_model=ai_model
    )


def generate_and_post_scenarios(
    jira_issue: JiraIssueEmbedding,
    service: TestScenarioService 
):
    """Função alvo da tarefa em segundo plano."""
    try:
        logging.info(f"Iniciando processamento para a issue: {jira_issue.issue_key}")
        qa_agent = service.create_qa_agent()
        
        prompt = f"Issue Details: {jira_issue.model_dump_json(indent=2)}\n\nGenerate test cases for the above user story in markdown format."
        qa_agent.run_sync(prompt)        

        logging.info(f"Processamento concluído para a issue: {jira_issue.issue_key}")
    except Exception as e:
        logging.error(f"Falha ao processar a issue {jira_issue.issue_key}: {e}", exc_info=True)


@app.post("/webhook/jira", status_code=202)
def jira_webhook_handler(
    payload: JiraWebhookPayload,
    background_tasks: BackgroundTasks,
    service: TestScenarioService = Depends(get_test_scenario_service),
):
    """
    Recebe o webhook do Jira, valida os dados e agenda o processamento em segundo plano.
    """
    logging.info(f"Recebido webhook: {payload.webhookEvent} para a issue {payload.issue.key}")
    issue_fields = payload.issue.fields
    description = ' '.join(issue_fields.description.split()) if issue_fields.description else ""
    tester_value = issue_fields.tester_info[0].get('value') if issue_fields.tester_info else None
    formatter_model = service.create_formatter_agent()

    jira_issue_object = JiraIssueEmbedding(
        event=payload.webhookEvent,
        issue_key=payload.issue.key,
        issue_description=formatter_model.run_sync(description).output if description else "",
        issue_name=issue_fields.summary,
        tester=tester_value,
        epic=None 
    )

    logging.info(f"Agendando processamento para a issue: {jira_issue_object.issue_key}")
    background_tasks.add_task(generate_and_post_scenarios, jira_issue_object, service)
    
    return {"status": "Recebido e agendado para processamento."}

