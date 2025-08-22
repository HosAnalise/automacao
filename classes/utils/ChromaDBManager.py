import os
import chromadb
from chromadb.api.client import Client
from chromadb.api.models.Collection import Collection
from typing import List, Optional, Any, Dict




# Analogia: Pense nesta classe como um "Controle Remoto Universal" para o ChromaDB.
# A versão original era como um controle que só tinha o botão de ligar.
# Esta nova versão tem botões de volume, canais, input, etc.,
# dando a você acesso a mais funcionalidades de forma segura e organizada.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class ChromaDBManager:
    """
    Uma classe wrapper para gerenciar interações com o ChromaDB,
    promovendo flexibilidade e boas práticas.
    """

    def __init__(self, client: Optional[Client] = None):
        """
        Inicializa o gerenciador do ChromaDB.

        Permite injetar um cliente existente (ex: PersistentClient) ou
        cria um cliente efêmero (em memória) por padrão.

        Args:
            client (Optional[Client]): Uma instância de cliente ChromaDB.
                                       Se None, um EphemeralClient será criado.
        """
        self.client: Client = client or chromadb.PersistentClient('assets')

    def get_or_create_collection(self, name: str) -> Collection:
        """
        Obtém uma coleção existente ou cria uma nova se não existir.
        Este é um padrão muito comum e útil.

        Args:
            name (str): O nome da coleção.

        Returns:
            Collection: A instância da coleção.
        """

        # Este método é mais seguro e conveniente que ter create e get separados.
        return self.client.get_or_create_collection(name=name)

    def add_to_collection(
        self,
        collection: Collection,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        embeddings: Optional[List[List[float]]] = None
    ) -> None:
        """
        Adiciona documentos, embeddings e metadados a uma coleção.

        Note que o ChromaDB precisa de pelo menos `documents` ou `embeddings`.

        Args:
            collection (Collection): A coleção onde os dados serão adicionados.
            ids (List[str]): Uma lista de IDs únicos para cada item.
            documents (Optional[List[str]]): A lista de textos/documentos.
            metadatas (Optional[List[Dict[str, Any]]]): Metadados associados a cada item.
            embeddings (Optional[List[List[float]]]): Embeddings pré-calculados.
        """
        collection.upsert(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Adicionados {len(ids)} itens à coleção '{collection.name}'.")


    def query_collection(
        self,
        collection: Collection,
        query_texts: Optional[List[str]] = None,
        query_embeddings: Optional[List[List[float]]] = None,
        n_results: int = 5,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executa uma consulta na coleção por texto ou por embeddings.

        Args:
            collection (Collection): A coleção a ser consultada.
            query_texts (Optional[List[str]]): Textos para a consulta.
            query_embeddings (Optional[List[List[float]]]): Embeddings para a consulta.
            n_results (int): O número de resultados a serem retornados.
            where_filter (Optional[Dict[str, Any]]): Um filtro para os metadados.

        Returns:
            Dict[str, Any]: Os resultados da consulta.

        Raises:
            ValueError: Se nem `query_texts` nem `query_embeddings` forem fornecidos.
        """
        if not query_texts and not query_embeddings:
            raise ValueError("Você deve fornecer 'query_texts' ou 'query_embeddings' para a consulta.")

        results = collection.query(
            query_embeddings=query_embeddings,
            query_texts=query_texts,
            n_results=n_results,
            where=where_filter
        )
        return results

    def get_collection(self, name: str) -> Optional[Collection]:
        """
        Obtém uma coleção pelo nome, tratando o caso de ela não existir.

        Args:
            name (str): O nome da coleção.

        Returns:
            Optional[Collection]: A instância da coleção ou None se não for encontrada.
        """
        try:
            return self.client.get_collection(name=name)
        except ValueError:
            # O ChromaDB levanta um ValueError se a coleção não existe.
            print(f"A coleção '{name}' não foi encontrada.")
            return None

    def delete_collection(self, name: str) -> None:
        """
        Deleta uma coleção pelo nome.

        Args:
            name (str): O nome da coleção a ser deletada.
        """
        try:
            self.client.delete_collection(name=name)
            print(f"Coleção '{name}' deletada com sucesso.")
        except ValueError:
            print(f"Falha ao deletar: A coleção '{name}' não foi encontrada.")