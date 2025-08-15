from flask import Flask, request, jsonify
import json 

app = Flask(__name__)

@app.route('/webhook/jira', methods=['POST'])
def jira_webhook_handler():
    data = request.get_json()

    print("===================================================")
    print("🎉 Webhook do Jira foi recebido com sucesso! 🎉")
    
    event = data.get('webhookEvent')
    issue_key = data.get('issue', {}).get('key')
    description = data.get('issue', {}).get('fields', {}).get('description', '')
    summary = data.get('issue', {}).get('fields', {}).get('summary', '')
    issue_name = data.get('issue', {}).get('fields', {}).get('name', '')

    print(f"Nome da Issue: {issue_name}")
    print(f"Tipo de Evento: {event}")
    print(f"Chave da Issue: {issue_key}")

    print(f"Nome da issue: {summary}")
    print(f"Descrição: {description}")

    

    
    

    return jsonify({"status": "recebido"}), 200

# Roda o servidor quando o script é executado
if __name__ == '__main__':
    # host='0.0.0.0' faz o servidor ser acessível por outros na sua rede
    # port=5000 é a porta padrão, pode ser outra se preferir
    app.run(host='0.0.0.0', port=5000)