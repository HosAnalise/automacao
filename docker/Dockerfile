# 1. Ponto de Partida: Sua imagem base do Docker Hub. 
FROM hosanalise/server-farma-v5:latest


# 2. Diretório de Trabalho: 
WORKDIR /app

# 3. Argumentos e Variáveis de Ambiente
ARG TESTS_DIR
ARG PYTESTMARK
ENV PYTESTMARK=$PYTESTMARK

# 4. Cópia de Arquivos
COPY .env.docker /app/.env
COPY classes/utils /app/classes/utils
COPY classes/rotinas /app/classes/rotinas
COPY conftest.py /app/conftest.py
COPY pytest.ini /app/pytest.ini
COPY testes/web/${TESTS_DIR} /app/testes/web/${TESTS_DIR}
COPY run_tests.py /app/run_tests.py

# 5. Comando de Execução: 
CMD ["sh", "-c", "python run_tests.py --tarefa ${PYTESTMARK}"]