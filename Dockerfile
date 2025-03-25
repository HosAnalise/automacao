# Usa a imagem oficial do Python
FROM python:3.12.7

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto para o container
COPY . .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt


# Expõe uma porta caso necessário (se for rodar um servidor para os testes)
EXPOSE 5000  

# Define o comando padrão para rodar os testes
CMD ["pytest", "--headless:No"]
