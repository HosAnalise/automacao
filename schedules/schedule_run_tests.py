import schedule
import time
import subprocess
from datetime import datetime, time 

def executar_tarefa(tarefa):
    """
    Executa o comando pytest com os parâmetros especificados.
    """
    print(f"[{datetime.now()}] Dentro do horário permitido. Executando pytest para {tarefa}...")
    subprocess.call(["pytest", "-m", tarefa, "-s"])




# Agendar a tarefa_pesada para rodar todo dia às 15:30.
schedule.every().day.at("15:30").do(executar_tarefa, tarefa = mark)

# Outros exemplos de agendamento (descomente para testar):
# schedule.every().minute.do(executar_tarefa, "tarefa_leve")
# schedule.every().hour.do(executar_tarefa, "tarefa_pesada")
# schedule.every().monday.at("09:00").do(executar_tarefa, "tarefa_pesada")
# schedule.every(5).to(10).minutes.do(executar_tarefa, "tarefa_leve") # A cada 5 a 10 minutos

# --- 3. O Loop Infinito (O "Assistente") ---
# Esta é a parte crucial. O script precisa continuar rodando para
# verificar se há tarefas pendentes.

while True:
    schedule.run_pending()
    time.sleep(1) # Espere 1 segundo antes de checar novamente.
                  # Isso evita que o loop consuma 100% da CPU!