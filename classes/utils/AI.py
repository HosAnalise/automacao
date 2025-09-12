import heapq
import logging
import google.generativeai as genai
from pydantic import BaseModel, Field
from pydantic_ai import ModelSettings
from pypdf import PdfReader
# from sklearn.metrics.pairwise import cosine_similarity
# import backoff
import os
from pydantic_ai.agent import Agent    
from typing import List, Optional
from pydantic import BaseModel, Field
from classes.utils import ChromaDBManager
from classes.utils.JiraApi import JiraApi
import requests as request
from pydantic_ai.models.google import GoogleModel


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




    # @backoff.on_exception(backoff.expo,
    #                   exception=Exception,
    #                   giveup=lambda e: not AI.is_rate_limit_error(e))
    # def generate_embedding_of_all_routines(self,json:list[dict]) -> list[list[float]]:
    #     """
    #     Gera um vetor de embedding para todas as rotinas fornecidas.

    #     :param json: Uma lista de rotinas.


    #     :return: Uma lista de embeddings (lista de listas de floats).
    #     """
    #     if not json:
    #         return []

    #     try:
    #         content_to_embed = [
    #             f"Nome: {obj.get('meta', '')}\nDescrição: {obj.get('content', '')}" 
    #             for obj in json
    #         ]
    #         result = genai.embed_content(
    #                 model=self.embedding_model,
    #                 content=content_to_embed,
    #                 task_type="RETRIEVAL_DOCUMENT"
    #             )
    #         return result['embedding']
    #     except Exception as e:
    #         print(f"Ocorreu um erro ao gerar embeddings: {e}")
    #         return []


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
        
    # def calculate_similarity(self, embedding1: list[float], embedding2: list[float]) -> float:
    #     if not embedding1 or not embedding2:
    #         return 0.0
        
    #     vec1 = np.array(embedding1)
    #     vec2 = np.array(embedding2)

        
    #     if vec1.ndim == 2:
    #         vec1 = vec1[0]
        
    #     if vec2.ndim == 2:
    #         vec2 = vec2[0]

    #     similarity = cosine_similarity([vec1], [vec2])[0]

    #     return similarity[0]

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


class JiraIssueEmbedding(BaseModel):
    issue_key: str
    issue_name: str
    issue_description: str
    epic: Optional[str] = None


class TestScenarioOutput(BaseModel):
    """Modelo de saída para os cenários de teste gerados pela IA."""
    
    test_track: Optional[List[str]] = Field(None, description="Traz toda trilha de cenarios de teste gerados.formatado em markdown.")

COLLECTION_NAME = "MANUAIS_DE_ROTINAS_CHUNKED"
AI_GENERATED_COMMENT_PHRASES = [
    "Cenários de teste gerados por IA. Revisão humana necessária",
    "Nenhuma descrição de issue ou documentos fornecidos. impossivel gerar cenários de teste.",
    "Cenario-",
]

QA_AGENT_PROMPT_TEMPLATE = """
Você é um agente de QA Sênior, especialista em análise de software e criação de planos de teste.
Sua missão é analisar descrições de tarefas e documentação técnica para criar cenários de teste abrangentes, claros e eficazes.

# Formato de Saída Obrigatório
Adicione um comentário inicial explicando que o conteúdo foi gerado por IA e precisa de revisão humana.
Formate a saída final em Markdown. Para cada cenário de teste, use a seguinte estrutura:

---
**ID:** Cenario-00X
**Título:** [Título claro e conciso do cenário]
**Tipo de Teste:** [Caminho Feliz / Caso de Borda / Fluxo de Erro / Regressão]

**Pré-condições:**
* [Pré-condição 1]
* [Pré-condição 2]

**Passos para Execução:**
1. [Primeiro passo]
2. [Segundo passo]

**Resultado Esperado:**
* [Comportamento esperado do sistema após a execução dos passos]
---
"""


FORMATTER_AGENT_PROMPT_TEMPLATE= """ 
# Persona e Missão Principal

Você é um Engenheiro de Dados especializado em Processamento de Linguagem Natural (PLN), com foco na otimização de texto para modelos de embedding. Sua missão é receber um texto bruto e transformá-lo em um formato limpo, estruturado e semanticamente denso, garantindo que a informação essencial seja facilmente vetorizável e recuperável por um sistema de busca vetorial.

# Princípios Orientadores

1.  **Atomicidade e Clareza:** Cada parágrafo ou item de lista deve, idealmente, conter uma única ideia, fato ou conceito. Evite sentenças longas e complexas.
2.  **Contextualização Explícita:** Não presuma conhecimento prévio. Se o texto menciona uma entidade, um projeto ou um acrônimo, esclareça-o brevemente na primeira menção.
3.  **Estruturação Lógica:** Utilize Markdown (títulos, listas, negrito) para criar uma hierarquia visual e lógica no texto. A estrutura ajuda o modelo a entender as relações entre as partes do conteúdo.
4.  **Remoção de Ruído:** Elimine informações irrelevantes para o significado semântico do texto, como saudações, frases de preenchimento, metadados de e-mail (data, remetente) e qualquer conteúdo que não agregue valor informacional.
5.  **Consistência Terminológica:** Padronize termos e acrônimos ao longo do texto para evitar ambiguidades.

# Processo Passo a Passo

1.  **Análise Inicial:** Leia o texto bruto para compreender seu propósito central, seus principais tópicos e seu público-alvo.
2.  **Segmentação (Chunking):** Divida o texto em segmentos lógicos menores. Um título de seção e seus parágrafos, por exemplo, formam um bom segmento.
3.  **Reescrita e Clarificação:** Para cada segmento, reescreva as frases para serem mais diretas e claras. Desfaça sentenças compostas em sentenças simples. Substitua pronomes ambíguos ("ele", "isso", "aquilo") por substantivos explícitos.
4.  **Enriquecimento e Estruturação:** Adicione títulos e subtítulos descritivos (`#`, `##`). Use listas com marcadores (`*`) ou numeradas (`1.`) para sequências ou conjuntos de itens. Use negrito (`**texto**`) para destacar os termos ou conceitos mais importantes.
5.  **Formatação Final:** Entregue o texto final formatado exclusivamente em Markdown.

# Exemplo de Tarefa

**Texto Bruto de Entrada:**
"Oi pessoal, só pra avisar que o relatório do projeto Alpha foi finalizado. Nele a gente detalha os resultados dos testes de performance que rodamos semana passada e também tem umas ideias pro futuro. Ficou bem legal, o João que fez a maior parte da análise de dados. A principal conclusão é que o novo cache melhorou a latência em 30%, mas aumentou um pouco o uso de memória. A gente precisa decidir os próximos passos sobre isso. Anexo o doc."

**Saída Formatada Esperada:**

# Relatório de Performance do Projeto Alpha

## Resumo Executivo
O relatório de performance do Projeto Alpha está concluído. A principal conclusão é que a implementação do novo sistema de cache resultou em uma melhoria de 30% na latência, com um aumento colateral no consumo de memória.

## Análise de Resultados
* **Melhora de Latência:** Redução de 30% no tempo de resposta das requisições.
* **Consumo de Memória:** Observado um aumento no uso de memória RAM após a implementação do cache.
* **Responsável pela Análise:** A análise de dados foi conduzida por João.

## Próximos Passos
* É necessária uma avaliação para decidir as próximas ações em relação ao trade-off entre latência e uso de memória.
* Discutir futuras otimizações e ideias para o projeto.
"""


class TestScenarioService:
    """
    Orquestra a geração e publicação de cenários de teste baseados em issues do Jira.
    """
    def __init__(self, jira_client: JiraApi, db_manager: ChromaDBManager, ai_model: GoogleModel):
        """
        Inicializa o serviço injetando suas dependências.
        """
        self.jira_client = jira_client
        self.db_manager = db_manager
        self.ai_model = ai_model 
        self.collection = self.db_manager.get_or_create_collection(name=COLLECTION_NAME)

    def find_relevant_documents(self, jira_details: JiraIssueEmbedding) -> list[str]:
        """
        Busca na base de conhecimento documentos relevantes para a issue do Jira.
        """
        query_result = self.db_manager.query_collection(
            collection=self.collection,
            query_texts=[jira_details.issue_description, jira_details.issue_name],
            n_results=10
        )
        
        if not query_result or not query_result.documents:
            return []
            
        return self._clean_documents(query_result.documents)
    

    def find_ranked_documents(self, jira_details: JiraIssueEmbedding) -> list[str]:
        """
        Busca e classifica documentos relevantes para a issue do Jira usando embeddings.
        """
        response = request.post(url="https://integradhos.hos.com.br/ai/chat",
                                data={"question": f"{jira_details.issue_description} {jira_details.issue_name}"},
                                headers={'x-api-key': os.getenv("INTEGRADHOS_API_KEY")})
        return response

    def _clean_documents(self, documents: list[list[str]]) -> list[str]:
        """
        Limpa o conteúdo dos documentos removendo caracteres indesejados.
        Método privado de suporte.
        """
        cleaned_docs = []
        for doc_list in documents:
            if doc_list:
                # Remove quebras de linha e espaços extras
                clean_text = ' '.join(doc_list[0].split())
                cleaned_docs.append(clean_text)
        return cleaned_docs

    def has_ai_comment(self, issue_key: str) -> bool:
        """
        Verifica se um comentário gerado por IA já existe na issue.
        """
        comments = self.jira_client.get_text_comments(issue_id=issue_key)
        for comment in comments:
            if any(phrase in comment for phrase in AI_GENERATED_COMMENT_PHRASES):
                return True
        return False

    def post_comment_on_issue(self, issue_key: str, output_object: TestScenarioOutput):
        """
        Trata o objeto TestScenarioOutput e publica um comentário na issue do Jira, a menos que já exista um da IA.
        
        Args:
            issue_key: A chave da issue do Jira.
            output_object: Objeto tipo TestScenarioOutput com o texto do comentário a ser postado.
        """
        def clean_comment(comment: str) -> str:
            comment = comment.replace("\n", " ")
            comment = comment.replace("**", " ")
            comment = comment.replace("ID:", "")
            return comment.strip() + "\n" 
            

        text = ""
        if output_object and output_object.test_track:
            text = "\n".join(clean_comment(comment) for comment in output_object.test_track)

        if self.has_ai_comment(issue_key):
            logging.info(f"Comentário de IA já existe na issue {issue_key}. Nenhuma ação tomada.")
        else:
            self.jira_client.insert_comment(issue_id=issue_key, comment=text)


    def create_formatter_agent(self) -> Agent:
        """
        Cria uma instância de um agente de formatação pré-configurado. Formata a entrada de texto para melhor compreensão por um banco de embeddings.
        """
        return Agent(
            model=self.ai_model,
            instructions=FORMATTER_AGENT_PROMPT_TEMPLATE,
            output_type=str,
            retries=3
            
        )


        

    def create_qa_agent(self) -> Agent:
        """
        Cria uma instância de um agente de QA pré-configurado.
        """
        return Agent(
            model=self.ai_model,
            tools=[self.find_ranked_documents, self.post_comment_on_issue],
            instructions=QA_AGENT_PROMPT_TEMPLATE,
            output_type=TestScenarioOutput,
            retries=3,
            model_settings=ModelSettings(temperature=0.3, max_tokens=2000000) 
        )


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

