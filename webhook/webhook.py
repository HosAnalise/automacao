import logging
import threading
from flask import Flask, request, jsonify
from classes.utils.AI import AI
from classes.utils.ChromaDBManager import ChromaDBManager
from classes.utils.Decoder import Decode



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





def process_jira_webhook(data: dict) -> AI.JiraIssueEmbedding:
    """
    Processa os dados recebidos do webhook do Jira.

    Args:
        data (dict): O payload JSON recebido do webhook.
    """

    return AI.JiraIssueEmbedding(
            event = data.get('webhookEvent'),
            issue_key = data.get('issue', {}).get('key'),
            issue_description = data.get('issue', {}).get('fields', {}).get('description', '').replace('\n', ' ').replace('\r', ' '),
            issue_name = data.get('issue', {}).get('fields', {}).get('summary', ''),
            tester = data.get('issue', {}).get('fields', {}).get('customfield_10077', {})[0].get('value',None),
            epic= data.get('issue', {}).get('fields', {}).get('parent', {}).get('fields', None).get('summary', None)
        )


def filter_embeddings(embeddings: list[dict]) -> list[dict]:
    """
    Filtra e retorna os top_n embeddings com base na similaridade.

    Args:
        embeddings (list[dict]): Lista de embeddings com suas similaridades.
        top_n (int): Número de embeddings a retornar.

    Returns:
        list[dict]: Lista dos top_n embeddings mais similares.
    """
    if not embeddings:
        return []
    
    return [
        emb.replace('\n', ' ').replace('\r', ' ').replace('\xa0', ' ')
        for emb_arr in embeddings.get('documents', [])
        for emb in emb_arr
    ]

def generate_content_from_embedding(data) -> str:
    """
    Gera conteúdo baseado no embedding da issue do Jira.

    Args:
       data (AI.JiraIssueEmbedding): Detalhes da issue do Jira.

    Returns:
        str: O conteúdo gerado.
    """
    jira_details = process_jira_webhook(data)


    chromadb_manager = ChromaDBManager()

    collection = chromadb_manager.get_or_create_collection(name="MANUAIS_DE_ROTINAS")



    response =  chromadb_manager.query_collection(  collection=collection,
                                                    query_texts=[jira_details.issue_description, jira_details.issue_name],
                                                    n_results=5,
                                                    # where_filter={"titulo": {"$in": [ jira_details.issue_name,jira_details.epic]}},
                                                ) 
    filter_embeddingsd = filter_embeddings(response)
    logging.info(f"Embeddings filtrados: {filter_embeddingsd}")

@app.route('/webhook/jira', methods=['POST'])
def jira_webhook_handler():
    """
    Endpoint que recebe o webhook, valida os dados e dispara o processamento
    em segundo plano.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Payload inválido"}), 400
    

    # logging.info(f"Webhook recebido com sucesso: {data}")
   

    
    thread = threading.Thread(target=generate_content_from_embedding, args=(data,))
    thread.start()

   
    return jsonify({"status": "recebido e agendado para processamento"}), 202

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)