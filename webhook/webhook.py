from flask import Flask, request, jsonify
from classes.utils.AI import AI
from classes.utils.Decoder import Decode
from classes.utils.ChromaDBManager import ChromaDBManager

app = Flask(__name__)

@app.route('/webhook/jira', methods=['POST'])
def jira_webhook_handler():
    data = request.get_json()
    
    event = data.get('webhookEvent')
    issue_key = data.get('issue', {}).get('key')
    description = data.get('issue', {}).get('fields', {}).get('description', '')
    summary = data.get('issue', {}).get('fields', {}).get('summary', '')
    issue_name = data.get('issue', {}).get('fields', {}).get('name', '')
    print(f"Evento recebido: {event}, Issue Key: {issue_key},  Nome da Issue: {issue_name}")

    try:
        chromadb_manager = ChromaDBManager()
        ai = AI()

        jiraEmbedding = AI.JiraIssueEmbedding(
            event=event,
            issue_key=issue_key,
            issue_name=issue_name,
            issue_description=description,
            summary=summary
        )

        embedding1 = ai.generate_embedding_jira(jiraEmbedding)

        collection = chromadb_manager.get_or_create_collection(name="MANUAIS_DE_ROTINAS")

        print(f"Total de documentos na coleção: {collection.count()}")

        query_result = chromadb_manager.query_collection(
            collection=chromadb_manager.get_or_create_collection(name="MANUAIS_DE_ROTINAS"),
            query_embeddings=embedding1
        )

        for ids in query_result:
            print(f"ID encontrado: {ids[0].split(':')[0]}\n")

    except Exception as e:
        print(f"Erro ao processar webhook do Jira: {e}")


    return jsonify({"status": "recebido"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)