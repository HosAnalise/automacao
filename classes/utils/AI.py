import heapq
import google.generativeai as genai
import os
from pydantic import BaseModel
from pypdf import PdfReader
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import backoff



class AI:
    """
    Classe centralizadora para todas as interações com a API do Google Gemini,
    incluindo geração de embeddings e análise de texto.
    """
    
    def __init__(self):
        """
        Configura os modelos de IA usando uma chave de API a partir das variáveis de ambiente.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi definida.")
            
        genai.configure(api_key=api_key)
        
        # --- Modelos Específicos para cada Tarefa ---
        
        # 1. Modelo para ANÁLISE DE TEXTO (identificar erros, resumir, etc.)
        generation_config = {
            "temperature": 0.5, # Temperatura mais baixa para respostas mais consistentes e menos "criativas"
            "max_output_tokens": 4096,
        }
        self.generative_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest", # Modelo rápido e eficiente para análise estruturada
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
        event: str
        issue_key: str
        issue_name: str
        issue_description: str
        summary: str

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
                   f"Resumo: {obj.summary}\n"

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
               

# --- Exemplo de como usar a classe centralizada ---
if __name__ == '__main__':
    ia_helper = AI()
    
   