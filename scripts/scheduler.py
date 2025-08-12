import argparse
from datetime import datetime
import subprocess
from classes.utils.LogManager import LogManager

log = LogManager()


def dentro_do_horario(hora_inicio, hora_fim):
    """
    Verifica se o horário atual está dentro do intervalo permitido.
    """
    agora = datetime.now().time()
    if hora_inicio < hora_fim:
        return hora_inicio <= agora <= hora_fim
    # Quando o intervalo cruza a meia-noite
    return agora >= hora_inicio or agora <= hora_fim

def executar_tarefa(tarefa):
    """
    Executa o comando pytest com os parâmetros especificados.
    """
    print(f"[{datetime.now()}] Dentro do horário permitido. Executando pytest para {tarefa}...")

    subprocess.call(["pytest","-v","-n", "auto", "-m", tarefa, "-s"])

def main():
    """
    Loop principal para verificar o horário e executar a tarefa.
    """
    # Parser de argumentos
    parser = argparse.ArgumentParser(description="Verifica e executa tarefas dentro de um horário específico.")
    parser.add_argument('--hora_inicio', type=str, default="00:00", help="Hora de início (formato HH:MM)")
    parser.add_argument('--hora_fim', type=str, default="06:00", help="Hora de término (formato HH:MM)")
    parser.add_argument('--intervalo_verificacao', type=int, default=1800, help="Intervalo de verificação em segundos")
    parser.add_argument('--tarefa', type=str, required=True, help="Nome da tarefa a ser executada (ex: dockerContaPagar)")

    args = parser.parse_args()

    # Convertendo os horários para objetos time
    hora_inicio = datetime.strptime(args.hora_inicio, "%H:%M").time()
    hora_fim = datetime.strptime(args.hora_fim, "%H:%M").time()

    print(f"Iniciando verificação contínua entre {hora_inicio} e {hora_fim}...")

    while True:
        # if dentro_do_horario(hora_inicio, hora_fim):
        # else:
        #     print(f"[{datetime.now()}] Fora do horário permitido. Aguardando...")
        # time_module.sleep(args.intervalo_verificacao)
        executar_tarefa(args.tarefa)
        log.delete_logs_older_than(days=2,collection_name='web_logs')  # Limpa logs mais antigos que 2 dias
        log.delete_logs_older_than(days=2,collection_name='error_logs')  # Limpa logs mais antigos que 2 dias

if __name__ == "__main__":
    main()
