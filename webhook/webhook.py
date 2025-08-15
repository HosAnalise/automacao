from flask import Flask, request, jsonify
from classes.utils.AI import AI
from classes.utils.Decoder import Decode

app = Flask(__name__)

@app.route('/webhook/jira', methods=['POST'])
def jira_webhook_handler():
    data = request.get_json()
    
    event = data.get('webhookEvent')
    issue_key = data.get('issue', {}).get('key')
    description = data.get('issue', {}).get('fields', {}).get('description', '')
    summary = data.get('issue', {}).get('fields', {}).get('summary', '')
    issue_name = data.get('issue', {}).get('fields', {}).get('name', '')

    ai = AI()
    jiraEmbedding = AI.JiraIssueEmbedding(
        event=event,
        issue_key=issue_key,
        issue_name=issue_name,
        issue_description=description,
        summary=summary
    )

    embedding1 = ai.generate_embedding_jira(jiraEmbedding)

    embedding2 = ai.generate_embedding_of_all_routines(Decode.generate_json())

    similarity = ai.calculate_similarity(embedding1, embedding2)

    ranked_documents = ai.rank_documents([similarity])

    print(f"Ranked documents {ranked_documents}")

    return jsonify({"status": "recebido"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)