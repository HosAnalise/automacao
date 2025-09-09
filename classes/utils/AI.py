from gc import collect
import heapq
import logging
from typing import Optional
from unittest.mock import Base
import chromadb
from duckdb import description
import google.generativeai as genai
# from proto import Field
from pydantic import BaseModel, Field
from pypdf import PdfReader
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import backoff
import os
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.agent import Agent

from classes.utils import ChromaDBManager
from classes.utils.JiraApi import JiraApi

API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL = "gemini-2.5-pro-latest"

class AI:
    """
    Classe centralizadora para todas as interações com a API do Google Gemini,
    incluindo geração de embeddings e análise de texto.
    """
    
    def __init__(self):
        """
        Configura os modelos de IA usando uma chave de API a partir das variáveis de ambiente.
        """
        if not API_KEY:
            raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi definida.")

        genai.configure(api_key=API_KEY)

        # --- Modelos Específicos para cada Tarefa ---
        
        generation_config = {
            "temperature": 0.5, 
            "max_output_tokens": 4096,
        }
        self.generative_model = genai.GenerativeModel(
            model_name=MODEL, 
            generation_config=generation_config
        )

        # 2. Modelo para GERAR EMBEDDINGS (busca semântica)
        self.embedding_model = 'gemini-embedding-001'

    def gerar_embeddings_para_logs(self, logs: list[str]) -> list[list[float]]:
        """
        Gera um vetor de embedding para cada linha de log fornecida.

        :param logs: Uma lista de strings, onde cada string é uma linha de log.
        :return: Uma lista de embeddings (lista de listas de floats).
        """
        if not logs:
            return []
        
        print(f"Gerando embeddings para {len(logs)} linhas de log...")
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=logs,
                task_type="RETRIEVAL_DOCUMENT"
            )
            return result['embedding']
        except Exception as e:
            print(f"Ocorreu um erro ao gerar embeddings: {e}")
            return []
        

    class JiraIssueEmbedding(BaseModel):
        event: Optional[str] = None
        issue_key: Optional[str] = None
        issue_name: Optional[str] = None
        issue_description: Optional[str] = None
        summary: Optional[str] = None
        tester: Optional[str|dict] = None
        epic: Optional[str] = None
        priority: Optional[str] = None
        project : Optional[str] = None

    def generate_embedding_jira(self, jira_issue: JiraIssueEmbedding) -> list[float]:
        """
        Gera um vetor de embedding para a descrição de uma issue do Jira.

        :param jira_issue: A descrição da issue.

        :return: Um vetor de embedding (lista de floats).
        """

        def obj_to_text(obj: AI.JiraIssueEmbedding) -> str:
            return f"Evento: {obj.event}\n" \
                   f"Chave da Issue: {obj.issue_key}\n" \
                   f"Nome da Issue: {obj.issue_name}\n" \
                   f"Descrição da Issue: {obj.issue_description}\n" \
                   f"Resumo: {obj.summary}\n" \
                   f"Testador: {obj.tester if obj.tester else 'N/A'}"

        if not jira_issue:
            return []

        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=[obj_to_text(jira_issue)],
                task_type="RETRIEVAL_QUERY"
            )
            return result['embedding'][0]
        except Exception as e:
            print(f"Ocorreu um erro ao gerar embeddings: {e}")
            return None


    def is_rate_limit_error(e):
        """Verifica se a exceção contém o código de status 429."""
        return "429" in str(e)




    @backoff.on_exception(backoff.expo,
                      exception=Exception,
                      giveup=lambda e: not AI.is_rate_limit_error(e))
    def generate_embedding_of_all_routines(self,json:list[dict]) -> list[list[float]]:
        """
        Gera um vetor de embedding para todas as rotinas fornecidas.

        :param json: Uma lista de rotinas.


        :return: Uma lista de embeddings (lista de listas de floats).
        """
        if not json:
            return []

        try:
            content_to_embed = [
                f"Nome: {obj.get('meta', '')}\nDescrição: {obj.get('content', '')}" 
                for obj in json
            ]
            result = genai.embed_content(
                    model=self.embedding_model,
                    content=content_to_embed,
                    task_type="RETRIEVAL_DOCUMENT"
                )
            return result['embedding']
        except Exception as e:
            print(f"Ocorreu um erro ao gerar embeddings: {e}")
            return []


    def tranform_document_in_lot_for_embedd(self,dict_to_batch:list[dict]) -> list[list[dict]]:

        batch_size=10
        return [dict_to_batch[i:i + batch_size] for i in range(0, len(dict_to_batch), batch_size)]

    def analisar_e_comparar_pdfs(self, pdf1: str, pdf2: str) -> bool:
        """
        Compara dois arquivos PDF e retorna True se forem idênticos, False caso contrário.
        
        :param pdf1: Caminho para o primeiro arquivo PDF.
        :param pdf2: Caminho para o segundo arquivo PDF.
        :return: Booleano indicando se os PDFs são idênticos.
        """       
        
        try:
            reader1 = PdfReader(pdf1)
            reader2 = PdfReader(pdf2)     

            texto1 = "\n".join([page.extract_text().strip() for page in reader1.pages if page.extract_text()])
            texto2 = "\n".join([page.extract_text().strip() for page in reader2.pages if page.extract_text()])

            if not texto1 or not texto2:
                print("Um ou ambos os PDFs não contêm texto legível.")
                return False
            
            # Prompt para a IA comparar os textos extraídos dos PDFs
            # Aqui, usamos o modelo generativo para comparar os textos extraídos
            
            prompt = f""" 
            Você é um especialista em comparação de arquivos PDF.
            Sua tarefa é comparar dois arquivos PDF e determinar se eles são semelhantes.
            Eles podem ter alguns nomes diferentes porem o conteúdo textual deve ser o mesmo.
            Voce deve ser capaz de identificar se os PDFs são idênticos em termos de conteúdo textual, mesmo que tenham diferenças em metadados, formatação, semântica ou imagens.
            Comparando valores de campo e trazendo as diferenças entre eles.
            **Instruções Críticas:**
            1. Compare o conteúdo textual de cada página dos PDFs.
            2. Ignore metadados, formatação e imagens; foque apenas no texto.
            3. Retorne uma analise dos campos que são diferentes.
            4. Retorne um resumo das diferenças encontradas, se houver. Se houver campos numéricos diferentes, calcule e informe a soma total das diferenças entre esses valores.
            Conteudo a ser analisado:
            PDF 1: {texto1}
            PDF 2: {texto2}
            """
            

            response = self.generative_model.generate_content(prompt)

            return response.text.strip().lower() if response else False
        
        except Exception as e:
            print(f"Erro ao comparar PDFs: {e}")
            return False
        
    def calculate_similarity(self, embedding1: list[float], embedding2: list[float]) -> float:
        if not embedding1 or not embedding2:
            return 0.0
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        
        if vec1.ndim == 2:
            vec1 = vec1[0]
        
        if vec2.ndim == 2:
            vec2 = vec2[0]

        similarity = cosine_similarity([vec1], [vec2])[0]

        return similarity[0]

    def rank_documents(self, similarity_scores: list[float], top_k: int = 3) -> list[dict[str, any]]:
        """
        Classifica os documentos com base em seus scores de similaridade e retorna os melhores.

        Args:
            similarity_scores: Uma lista de scores de similaridade.
            top_k: O número de melhores resultados a serem retornados.

        Returns:
            Uma lista de dicionários, cada um contendo o índice original
            do documento e seu score de similaridade.
        """
        top_k_items = heapq.nlargest(top_k, enumerate(similarity_scores), key=lambda item: item[1])

        return [
            {
                "original_index": int(idx),
                "score": float(similarity_scores[int(idx)])
            }
            for idx, _ in top_k_items
        ]

    def qa_agent(self, issue_description: str,documents:str) -> str:
        """
        Gera uma resposta para o prompt fornecido usando o modelo generativo.

        :param prompt: O prompt de entrada.
        :return: A resposta gerada pelo modelo.
        """
        
        if not issue_description and not documents:
            return " Nenhuma descrição de issue ou documentos fornecidos. impossivel gerar cenários de teste."
        
        
        prompt = f"""
                # Persona e Objetivo

                Você é um Agente de QA Sênior, um especialista em análise de software e criação de planos de teste. Sua principal habilidade é analisar descrições de tarefas (issues) e documentação técnica para criar cenários de teste abrangentes, claros e eficazes. Você é metódico, detalhista e pensa em todos os possíveis cenários, incluindo caminhos felizes, casos de borda e fluxos de erro.

                Sua tarefa é gerar uma trilha de testes completa para a issue fornecida abaixo, utilizando a documentação de apoio como base para o comportamento esperado do sistema.

                # Contexto do Sistema

                [O sistema hos é divido em 3 partes distintas: Farma: Responsavel por toda parte de cadastros, relatorios, etc; Frente de caixa: Responsavel por toda parte de vendas, caixa, fluxo de caixa, etc; Gestão: Responsavel por toda parte financeira, conferencias, etc.]

                # Entradas

                ## 1. Descrição da Issue:
                {issue_description}

                ## 2. Documentação Relevante:
                {documents}

                :** Com base na issue e na documentação, liste todos os cenários de teste possíveis. Pense em:
                    * **Caminho Feliz (Happy Path):** O fluxo ideal, onde tudo funciona como esperado.
                    * **Casos de Borda (Edge Cases):** Testes com valores limites (ex: 0, -1, valor máximo, strings vazias, etc.).
                    * **Fluxos de Erro e Exceção:** O que acontece quando o usuário faz algo errado ou quando ocorre um erro no sistema? (ex: preenchimento de formulário inválido, falha de conexão).
                    * **Testes de Regressão:** Quais funcionalidades adjacentes podem ter sido quebradas por essa mudança? Liste cenários para verificar isso.
                    * **Testes de Usabilidade (se aplicável):** A interface é clara? O fluxo é intuitivo?
                4.  **Estruture a Saída:** Organize os cenários que você criou no formato especificado abaixo. Seja extremamente claro e detalhado nos passos e nos resultados esperados.

                # Formato de Saída Obrigatório
                Adicione um comentario antes de dos cenarios de teste explcando que foi gerado por uma IA e que deve ser revisado por um humano.
                Formate a saída final em Markdown. Para cada cenário de teste, use a seguinte estrutura:

                ---
                **ID:** Cenario-00X
                **Título:** [Título claro e conciso do cenário]
                **Tipo de Teste:** [Caminho Feliz / Caso de Borda / Fluxo de Erro / Regressão]

                **Pré-condições:**
                * [Pré-condição 1]
                * [Pré-condição 2]

                **Passos para Execução:**
                1.  [Primeiro passo]
                2.  [Segundo passo]
                3.  [Terceiro passo]

                **Resultado Esperado:**
                * [Comportamento esperado do sistema após a execução dos passos]
                ---

            """     
       
        
        try:
            response = self.generative_model.generate_content(prompt)
            return response.text.strip() if response else ""
        except Exception as e:
            print(f"Ocorreu um erro ao gerar a resposta: {e}")
            return ""
               

# --- Exemplo de como usar a classe centralizada ---
if __name__ == '__main__':
    ia_helper = AI()
    
class AI_agents:   

    _collection = "MANUAIS_DE_ROTINAS_CHUNKED"


    def __init__(self):
        self.api_key =  API_KEY if API_KEY else None
        self.google_model = GoogleModel(model_name=MODEL,provider=GoogleProvider(api_key=API_KEY))






    def process_jira_webhook(data: dict) -> AI.JiraIssueEmbedding:
        """
        Processa os dados recebidos do webhook do Jira e retorna um objeto JiraIssueEmbedding.

        Args:
            data (dict): O payload JSON recebido do webhook.
        """

        return AI.JiraIssueEmbedding(
                event = data.get('webhookEvent'),
                issue_key = data.get('issue', {}).get('key') if data.get('issue', {}).get('key', None) else '',
                issue_description = data.get('issue', {}).get('fields', {}).get('description', '').replace('\n', ' ').replace('\r', ' ') if data.get('issue', {}).get('fields', {}).get('description', None) else '',
                issue_name = data.get('issue', {}).get('fields', {}).get('summary', '') if data.get('issue', {}).get('fields', {}).get('summary', None) else '',
                tester = data.get('issue', {}).get('fields', {}).get('customfield_10077', {})[0].get('value',None) if data.get('issue', {}).get('fields', {}).get('customfield_10077', None) else None,
                epic= data.get('issue', {}).get('fields', {}).get('parent', {}).get('fields', None).get('summary', None) if data.get('issue', {}).get('fields', {}).get('parent', None) else None,
            )


    def clean_documents(self,embeddings: list[dict]) -> list[str]:
        """
        Remove quebras de linha e espaços em branco e caracteres indesejados.

        Args:
            embeddings (list[dict]): Lista de embeddings com suas similaridades.

        Returns:
            list[dict]: Lista dos top_n embeddings mais similares.
        """
        if not embeddings:
            return []
        
        return [
            emb_arr[0].replace('\n', ' ').replace('\r', ' ').replace('\xa0', ' ') if emb_arr else ""
            for emb_arr in embeddings.documents 
            
        ]


    def find_similar_documents(self,jira_details: AI.JiraIssueEmbedding) -> str:
        """
        Procura conteúdo baseado no embedding da issue do Jira.

        Args:
        data (AI.JiraIssueEmbedding): Detalhes da issue do Jira.

        Returns:
            str: O conteúdo gerado.
        """
        CLIENT = chromadb.CloudClient(
        api_key='ck-Eov2T8HGLCmepvmLaiAhuCiLAt4m6b229RiSLZryy1P9',
        tenant='147a5208-c5cb-4dfd-8a84-00784b03999e',
        database='Automacao'
        )

        if not jira_details.issue_description:
            return logging.info(f"Nenhuma descrição encontrada na issue {jira_details.issue_key}. Nenhuma ação tomada.")

        chromadb_manager = ChromaDBManager(client=CLIENT)

        collection = chromadb_manager.get_or_create_collection(name=AI_agents._collection)
        query_result = chromadb_manager.query_collection(
            collection=collection,
            query_texts=[jira_details.issue_description, jira_details.issue_name],
            n_results=10,
            # where_filter={"titulo": {"$in": [ jira_details.issue_name,jira_details.epic]}},
                                                    )

        return [] if not query_result or not query_result.documents else query_result

    def verify_comment_exists(self,comments: list[str]) -> bool:
        """
        Verifica se um comentários específicos já existem na lista de comentários.

        Args:
            comments (list[str]): Lista de comentários.

        Returns:
            bool: True se o comentário existir, False caso contrário.
        """
        for comment in comments:
            if any(phrase in comment for phrase in ["Cenários de teste gerados por IA. Revisão humana necessária","Nenhuma descrição de issue ou documentos fornecidos. impossivel gerar cenários de teste.","Cenario-"]):
                return True 
        return False


    def insert_comment(self,data,jira:JiraApi,issue_text):
        """
        Metodo recebe o webhook do Jira transformando em um objeto JiraIssueEmbedding,
        busca documentos similares na base de conhecimento para gerar cenários de teste,
        filtra os documentos retornados, gera um texto com eles,
        apos isso ele gera os cenários de teste e insere um comentário na issue do Jira.

        ARGS:
            data (dict): Dados do webhook do Jira.
            jira (JiraApi): Instância da classe JiraApi.
            issue_text (str): Texto do comentário a ser inserido na issue.
        """

        jira_details = AI_agents.process_jira_webhook(data=data)


        comments = jira.get_text_comments(issue_id=jira_details.issue_key)    

        jira.insert_comment(issue_id=jira_details.issue_key, comment=issue_text) if AI_agents.verify_comment_exists(comments=comments) == False else logging.info(f"O comentário já existe na issue {jira_details.issue_key}. Nenhuma ação tomada.")

    def create_agent(self,model,tools: list,instructions: str,output_model)-> Agent:
        """Cria um agente com o modelo fornecido.

        Args:
            model (str): O nome do modelo a ser utilizado.

        Returns:
            Agent: Uma instância do agente criado.
        """
        return Agent(model=model if model else self.google_model,
                     tools=tools,
                     instructions=instructions,
                     output_type=output_model,
                     retries=3)
    
    def get_prompt(self,issue_description: str,documents:str) -> str:
        """
        Gera o prompt para o agente de QA.

        Args:
            issue_description (str): A descrição da issue.
            documents (str): Documentos relevantes para a issue.

        Returns:
            str: O prompt gerado.
        """
        if not issue_description and not documents:
            return " Nenhuma descrição de issue ou documentos fornecidos. impossivel gerar cenários de teste."
        
        
        return f"""
                 # Contexto do Sistema

                [O sistema hos é divido em 3 partes distintas: Farma: Responsavel por toda parte de cadastros, relatorios, etc; Frente de caixa: Responsavel por toda parte de vendas, caixa, fluxo de caixa, etc; Gestão: Responsavel por toda parte financeira, conferencias, etc.]

                # Entradas

                ## 1. Descrição da Issue:
                {issue_description}

                ## 2. Documentação Relevante:
                {documents}

                :** Com base na issue e na documentação, liste todos os cenários de teste possíveis. Pense em:
                    * **Caminho Feliz (Happy Path):** O fluxo ideal, onde tudo funciona como esperado.
                    * **Casos de Borda (Edge Cases):** Testes com valores limites (ex: 0, -1, valor máximo, strings vazias, etc.).
                    * **Fluxos de Erro e Exceção:** O que acontece quando o usuário faz algo errado ou quando ocorre um erro no sistema? (ex: preenchimento de formulário inválido, falha de conexão).
                    * **Testes de Regressão:** Quais funcionalidades adjacentes podem ter sido quebradas por essa mudança? Liste cenários para verificar isso.
                    * **Testes de Usabilidade (se aplicável):** A interface é clara? O fluxo é intuitivo?
                4.  **Estruture a Saída:** Organize os cenários que você criou no formato especificado abaixo. Seja extremamente claro e detalhado nos passos e nos resultados esperados.

                # Formato de Saída Obrigatório
                Adicione um comentario antes de dos cenarios de teste explcando que foi gerado por uma IA e que deve ser revisado por um humano.
                Formate a saída final em Markdown. Para cada cenário de teste, use a seguinte estrutura:

                ---
                **ID:** Cenario-00X
                **Título:** [Título claro e conciso do cenário]
                **Tipo de Teste:** [Caminho Feliz / Caso de Borda / Fluxo de Erro / Regressão]

                **Pré-condições:**
                * [Pré-condição 1]
                * [Pré-condição 2]

                **Passos para Execução:**
                1.  [Primeiro passo]
                2.  [Segundo passo]
                3.  [Terceiro passo]

                **Resultado Esperado:**
                * [Comportamento esperado do sistema após a execução dos passos]
                ---

            """

    def qa_agent(self) -> str:
        """
        Metodo que cria um agente especializado em QA.
        """
        return self.create_agent(tools=[self.clean_documents,self.find_similar_documents,self.verify_comment_exists,self.insert_comment,self.process_jira_webhook,self.get_prompt],
                                     model=self.google_model,
                                     instructions="Você é um agente de QA Sênior, um especialista em análise de software e criação de planos de teste. Sua principal habilidade é analisar descrições de tarefas (issues) e documentação técnica para criar cenários de teste abrangentes, claros e eficazes. Você é metódico, detalhista e pensa em todos os possíveis cenários, incluindo caminhos felizes, casos de borda e fluxos de erro.",
                                     output_model=str)
    



        # def process_webhook_data(data):
    #     """
    #     Função que executa o processamento pesado em segundo plano.
    #     """
    #     issue_key = data.get('issue', {}).get('key', 'N/A')
    #     logging.info(f"Iniciando processamento em background para a issue: {issue_key}")

    #     try:
            
    #         all_results = Decode.generate_json()
            
    #         chromadb_manager = ChromaDBManager()
    #         ai = AI()
    #         collection = chromadb_manager.get_or_create_collection(name="MANUAIS_DE_ROTINAS")

    #         document_batches = ai.tranform_document_in_lot_for_embedd(all_results)

            
    #         for i, batch_of_docs in enumerate(document_batches):
    #             logging.info(f"Processando lote {i+1}/{len(document_batches)} com {len(batch_of_docs)} documentos.")                  
                
    #             chromadb_manager.add_to_collection(
    #                 collection=collection,
    #                 ids=[f"{doc.meta.documentoId}:{doc.meta.titulo}" for doc in batch_of_docs],
    #                 documents=[doc.content for doc in batch_of_docs],
    #                 metadatas=[(doc.meta.model_dump(mode='json')) for doc in batch_of_docs],
    #             )
            
    #         logging.info(f"Processamento para a issue {issue_key} concluído com sucesso.")

        # except Exception as e:
        #     logging.error(f"Erro ao processar dados para a issue {issue_key}: {e}", exc_info=True)

