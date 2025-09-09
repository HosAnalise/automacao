import logging
import threading
from flask import Flask, request, jsonify
from classes.utils.JiraApi import JiraApi
from classes.utils.AI import AI
from classes.utils.ChromaDBManager import ChromaDBManager
import chromadb

# from classes.utils.Decoder import Decode



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)


# def process_webhook_data(data):
#     """
#     Função que executa o processamento pesado em segundo plano.
#     """
#     issue_key = data.get('issue', {}).get('key', 'N/A')
#     logging.info(f"Iniciando processamento em background para a issue: {issue_key}")

#     try:
        
#         all_results = Decode.generate_json()
        
#         chromadb_manager = ChromaDBManager()
#         ai = AI()
#         collection = chromadb_manager.get_or_create_collection(name="MANUAIS_DE_ROTINAS")

#         document_batches = ai.tranform_document_in_lot_for_embedd(all_results)

        
#         for i, batch_of_docs in enumerate(document_batches):
#             logging.info(f"Processando lote {i+1}/{len(document_batches)} com {len(batch_of_docs)} documentos.")                  
            
#             chromadb_manager.add_to_collection(
#                 collection=collection,
#                 ids=[f"{doc.meta.documentoId}:{doc.meta.titulo}" for doc in batch_of_docs],
#                 documents=[doc.content for doc in batch_of_docs],
#                 metadatas=[(doc.meta.model_dump(mode='json')) for doc in batch_of_docs],
#             )
        
#         logging.info(f"Processamento para a issue {issue_key} concluído com sucesso.")

    # except Exception as e:
    #     logging.error(f"Erro ao processar dados para a issue {issue_key}: {e}", exc_info=True)



COLLECTION = "MANUAIS_DE_ROTINAS_CHUNKED"

def process_jira_webhook(data: dict) -> AI.JiraIssueEmbedding:
    """
    Processa os dados recebidos do webhook do Jira e retorna um objeto JiraIssueEmbedding.

    Args:
        data (dict): O payload JSON recebido do webhook.
    """

    return AI.JiraIssueEmbedding(
            event = data.get('webhookEvent'),
            issue_key = data.get('issue', {}).get('key') if data.get('issue', {}).get('key', None) else '',
            issue_description = data.get('issue', {}).get('fields', {}).get('description', '').replace('\n', ' ').replace('\r', ' ') if data.get('issue', {}).get('fields', {}).get('description', None) else '',
            issue_name = data.get('issue', {}).get('fields', {}).get('summary', '') if data.get('issue', {}).get('fields', {}).get('summary', None) else '',
            tester = data.get('issue', {}).get('fields', {}).get('customfield_10077', {})[0].get('value',None) if data.get('issue', {}).get('fields', {}).get('customfield_10077', None) else None,
            epic= data.get('issue', {}).get('fields', {}).get('parent', {}).get('fields', None).get('summary', None) if data.get('issue', {}).get('fields', {}).get('parent', None) else None,
        )


def clean_documents(embeddings: list[dict]) -> list[str]:
    """
    Remove quebras de linha e espaços em branco e caracteres indesejados.

    Args:
        embeddings (list[dict]): Lista de embeddings com suas similaridades.

    Returns:
        list[dict]: Lista dos top_n embeddings mais similares.
    """
    if not embeddings:
        return []
    
    return [
        emb_arr[0].replace('\n', ' ').replace('\r', ' ').replace('\xa0', ' ') if emb_arr else ""
        for emb_arr in embeddings.documents 
        
    ]


def find_similar_documents(jira_details: AI.JiraIssueEmbedding) -> str:
    """
    Procura conteúdo baseado no embedding da issue do Jira.

    Args:
       data (AI.JiraIssueEmbedding): Detalhes da issue do Jira.

    Returns:
        str: O conteúdo gerado.
    """
    CLIENT = chromadb.CloudClient(
    api_key='ck-Eov2T8HGLCmepvmLaiAhuCiLAt4m6b229RiSLZryy1P9',
    tenant='147a5208-c5cb-4dfd-8a84-00784b03999e',
    database='Automacao'
    )

    if not jira_details.issue_description:
        return logging.info(f"Nenhuma descrição encontrada na issue {jira_details.issue_key}. Nenhuma ação tomada.")

    chromadb_manager = ChromaDBManager(client=CLIENT)

    collection = chromadb_manager.get_or_create_collection(name=COLLECTION)
    query_result = chromadb_manager.query_collection(
        collection=collection,
        query_texts=[jira_details.issue_description, jira_details.issue_name],
        n_results=10,
        # where_filter={"titulo": {"$in": [ jira_details.issue_name,jira_details.epic]}},
                                                )

    return [] if not query_result or not query_result.documents else query_result

def verify_comment_exists(comments: list[str]) -> bool:
    """
    Verifica se um comentários específicos já existem na lista de comentários.

    Args:
        comments (list[str]): Lista de comentários.

    Returns:
        bool: True se o comentário existir, False caso contrário.
    """
    for comment in comments:
        if any(phrase in comment for phrase in ["Cenários de teste gerados por IA. Revisão humana necessária","Nenhuma descrição de issue ou documentos fornecidos. impossivel gerar cenários de teste.","Cenario-"]):
            return True 
    return False

    
def init(data):

    jira_details = process_jira_webhook(data=data)
    response =  find_similar_documents(jira_details=jira_details)

    cleaned_docs = clean_documents(embeddings=response) 
    text_embeddings = "\n".join(cleaned_docs)

    ai = AI()

    issue_text  = ai.qa_agent(issue_description = jira_details.issue_description, documents = text_embeddings)

    jira = JiraApi()

    comments = jira.get_text_comments(issue_id=jira_details.issue_key)    

    jira.insert_comment(issue_id=jira_details.issue_key, comment=issue_text) if verify_comment_exists(comments=comments) == False else logging.info(f"O comentário já existe na issue {jira_details.issue_key}. Nenhuma ação tomada.")


@app.route('/webhook/jira', methods=['POST'])
def jira_webhook_handler():
    """
    Endpoint que recebe o webhook, valida os dados e dispara o processamento
    em segundo plano.
    """
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Payload inválido"}), 400  


    thread = threading.Thread(target=init, args=(data,))
    thread.start()

   
    return jsonify({"status": "recebido e agendado para processamento"}), 202

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)