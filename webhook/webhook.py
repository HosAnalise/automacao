# webhook_server.py
from flask import Flask, request, jsonify
import json 

app = Flask(__name__)

# Define a rota (o "caminho" da URL) que vai receber os dados do Jira.
# O método é POST porque o Jira vai ENVIAR dados para cá.
@app.route('/webhook/jira', methods=['POST'])
def jira_webhook_handler():
    # Pega os dados (payload) que o Jira enviou.
    data = request.get_json()

    # --- PONTO PRINCIPAL: AQUI A MÁGICA ACONTECE ---
    print("===================================================")
    print("🎉 Webhook do Jira foi recebido com sucesso! 🎉")
    
    # Vamos extrair algumas informações para ver o que recebemos
    event = data.get('webhookEvent')
    issue_key = data.get('issue', {}).get('key')
    
    print(f"Tipo de Evento: {event}")
    print(f"Chave da Issue: {issue_key}")

    # Para depuração, vamos imprimir o JSON completo de forma legível
    print("\nPayload completo recebido:")
    print(json.dumps(data, indent=2))

    # **AQUI VOCÊ VAI CONECTAR COM A SUA CLASSE DE AUTOMAÇÃO!**
    # Exemplo de como você poderia chamar sua lógica:
    # -------------------------------------------------------------
    # from sua_classe_jira import SuaClasseDeAutomacao
    #
    # if event == 'jira:issue_updated':
    #     meu_automator = SuaClasseDeAutomacao()
    #     meu_automator.processar_mudanca_de_status(issue_key, data)
    # -------------------------------------------------------------
    
    print("===================================================")

    # É uma boa prática responder ao Jira para ele saber que deu tudo certo.
    return jsonify({"status": "recebido"}), 200

# Roda o servidor quando o script é executado
if __name__ == '__main__':
    # host='0.0.0.0' faz o servidor ser acessível por outros na sua rede
    # port=5000 é a porta padrão, pode ser outra se preferir
    app.run(host='0.0.0.0', port=5000)