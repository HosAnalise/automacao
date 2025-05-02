# Usa a imagem base com Chrome e dependências já instaladas
FROM hosanalise/server-farma-base:1.0

# Cria diretório de trabalho
WORKDIR /app

# Recebe argumentos para definir os arquivos a serem copiados
ARG TESTS_DIR
ARG PYTESTMARK

ENV PYTESTMARK=$PYTESTMARK


# Copia arquivos e diretórios dinamicamente
COPY classes/utils /app/classes/utils
COPY classes/rotinas /app/classes/rotinas
COPY conftest.py /app/conftest.py
COPY .env.docker .env
COPY pytest.ini /app/pytest.ini

# Copia o script e o diretório de testes com base nos argumentos passados
COPY scripts/run_tests.py /app/run_tests.py
COPY testes/web/${TESTS_DIR} /app/testes/web/${TESTS_DIR}

# (Opcional) Reinstala dependências se necessário:
# RUN pip install --no-cache-dir -r requirements.txt

# Comando default para rodar os testes
CMD sh -c "python run_tests.py --tarefa $PYTESTMARK"
