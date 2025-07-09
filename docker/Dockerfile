# 1. Ponto de Partida: Sua imagem base do Docker Hub.
FROM hosanalise/minha-imagem-base:1.0

# 2. Diretório de Trabalho:
WORKDIR /app

# 3. Argumentos e Variáveis de Ambiente
# O ARG PYTESTMARK ainda é útil para definir um marcador padrão.
ARG PYTESTMARK
ENV PYTESTMARK=${PYTESTMARK:-"all"}

# 4. Cópia de Arquivos
# Copiamos TUDO o que é necessário para QUALQUER teste.
COPY .env.docker /app/.env
COPY classes /app/classes
COPY conftest.py /app/conftest.py
COPY pytest.ini /app/pytest.ini
# A GRANDE MUDANÇA: Copia a pasta 'web' inteira, com todos os testes.
COPY testes/web /app/testes/web

# 5. Comando de Execução Padrão:
# Este comando será executado se nenhum outro for especificado no docker-compose.
CMD ["pytest", "-m", "${PYTESTMARK}"]