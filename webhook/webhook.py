from flask import Flask, request, jsonify
from classes.utils.AI import AI
from classes.utils.ChromaDBManager import ChromaDBManager
from scripts.build import get_markers


app = Flask(__name__)

@app.route('/webhook/jira', methods=['POST'])
def jira_webhook_handler():

    data = request.get_json()
    
    event = data.get('webhookEvent')
    issue_key = data.get('issue', {}).get('key')
    description = data.get('issue', {}).get('fields', {}).get('description', '')
    summary = data.get('issue', {}).get('fields', {}).get('summary', '')
    issue_name = data.get('issue', {}).get('fields', {}).get('name', '')
    tester = data.get('issue', {}).get('customfield_10077', [{}])[0].get('value', 'teste')
    print(f"Recebido evento: {event} para a issue: {issue_key} - {issue_name}, atribuída a: {tester}")


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

        # query_result = chromadb_manager.query_collection(
        #     collection=chromadb_manager.get_or_create_collection(name="MANUAIS_DE_ROTINAS"),
        #     query_embeddings=ai.generate_embedding_jira(jiraEmbedding),
        #     n_results=10
        
        # )

        # chromadb_manager.get_or_create_collection(name="TEMP_BFS_MANUAIS")






        

    except Exception as e:
        print(f"Erro ao processar webhook do Jira: {e}")


    return jsonify({"status": "recebido"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)