from datetime import datetime, time
import subprocess
import time as time_module

# Configuração do horário permitido
HORA_INICIO = time(16, 0)
HORA_FIM = time(8, 0)
INTERVALO_VERIFICACAO = 1800  # Intervalo de verificação em segundos (30 minutos)

def dentro_do_horario(hora_inicio, hora_fim):
    """
    Verifica se o horário atual está dentro do intervalo permitido.
    """
    agora = datetime.now().time()
    if hora_inicio < hora_fim:
        return hora_inicio <= agora <= hora_fim
    # Quando o intervalo cruza a meia-noite
    return agora >= hora_inicio or agora <= hora_fim

def executar_tarefa():
    """
    Executa o comando pytest com os parâmetros especificados.
    """
    print(f"[{datetime.now()}] Dentro do horário permitido. Executando pytest...")
    subprocess.call(["pytest", "-m", "docker", "-s"])

def main():
    """
    Loop principal para verificar o horário e executar a tarefa.
    """
    print(f"Iniciando verificação contínua entre {HORA_INICIO} e {HORA_FIM}...")
    while True:
        if dentro_do_horario(HORA_INICIO, HORA_FIM):
            executar_tarefa()
        else:
            print(f"[{datetime.now()}] Fora do horário permitido. Aguardando...")
        time_module.sleep(INTERVALO_VERIFICACAO)

if __name__ == "__main__":
    main()
