import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 1. Conecte-se ao seu servidor local do Chroma
client = chromadb.HttpClient(host='localhost', port=8000)

# Coleções de origem e destino
source_collection_name = "MANUAIS_DE_ROTINAS"
target_collection_name = "MANUAIS_DE_ROTINAS_CHUNKED"

# Pega a coleção de origem
source_collection = client.get_collection(name=source_collection_name)
documents = source_collection.get(include=["documents", "metadatas"])

# 2. Crie a nova coleção (se já existir, apague para recomeçar)
if target_collection_name in [c.name for c in client.list_collections()]:
    client.delete_collection(name=target_collection_name)
new_collection = client.create_collection(name=target_collection_name)

# 3. Configure o divisor de texto
# Vamos mirar em pedaços de ~1000 caracteres com alguma sobreposição
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    length_function=len,
)

# 4. Itere, divida e adicione os documentos na nova coleção
for i in range(len(documents['ids'])):
    doc_id = documents['ids'][i]
    doc_content = documents['documents'][i]
    doc_metadata = documents['metadatas'][i]

    # Se o documento for grande, divida-o
    if len(doc_content.encode('utf-8')) > 16000: # Um pouco abaixo do limite por segurança
        print(f"Dividindo documento grande: {doc_id}")
        chunks = text_splitter.split_text(doc_content)
        
        # Cria novos IDs e metadados para cada chunk
        chunk_ids = [f"{doc_id}-chunk{j}" for j in range(len(chunks))]
        chunk_metadatas = [doc_metadata.copy() for _ in range(len(chunks))]
        for j, meta in enumerate(chunk_metadatas):
            meta['chunk_number'] = j # Adiciona metadados úteis

        new_collection.add(
            ids=chunk_ids,
            documents=chunks,
            metadatas=chunk_metadatas
        )
    else:
        # Se o documento for pequeno, apenas o adicione
        new_collection.add(
            ids=[doc_id],
            documents=[doc_content],
            metadatas=[doc_metadata]
        )

print(f"\nProcesso concluído! A nova coleção '{target_collection_name}' está pronta.")