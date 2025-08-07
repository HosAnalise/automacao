# classes/utils/AI.py
import google.generativeai as genai
import os
import json
from pypdf import PdfReader


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
        self.embedding_model = 'models/text-embedding-004'

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

    def analisar_logs_e_extrair_erros(self, logs: list[str]) -> dict:
        """
        Envia uma lista de logs para a IA e pede um resumo estruturado dos erros mais relevantes.
        
        :param logs: Uma lista de strings com os logs a serem analisados.
        :return: Um dicionário (JSON) com o resumo dos erros por rotina.
        """
        if not logs:
            return {"resumo_erros": []}

        # O prompt é a parte mais importante: damos instruções claras para a IA.
        prompt = f"""
        Você é um analista de QA sênior e sua especialidade é depurar logs de testes de automação com Selenium em Python.
        Sua tarefa é analisar a lista de logs de uma execução de teste e retornar um resumo estruturado dos erros mais relevantes.

        **Instruções Críticas:**
        1.  **Foque na Causa Raiz:** Priorize erros de lógica de negócio (ex: "CPF já cadastrado") ou erros específicos de fluxo (ex: "Botão 'Salvar' não encontrado após preencher o formulário").
        2.  **Descarte Erros Genéricos:** Ignore exceções técnicas genéricas como 'TimeoutException' ou 'StaleElementReferenceException', pois elas são geralmente sintomas de um problema anterior, e não a causa.
        3.  **Filtre por Nível:** Considere apenas logs que contenham "level='ERROR'" ou "level='WARNING'".
        4.  **Agrupe por Rotina:** Agrupe todos os erros encontrados pela 'rotina' mencionada no log.

        **Formato da Saída:**
        Responda **APENAS** em formato JSON, sem nenhum texto ou explicação adicional antes ou depois.
        O formato deve ser um objeto com uma chave "resumo_erros", que contém uma lista de objetos.
        Cada objeto deve representar uma rotina com erro e ter as seguintes chaves:
        - "rotina": O nome da rotina onde o erro ocorreu.
        - "quantidade_erros": A contagem total de erros relevantes encontrados para essa rotina.
        - "logs_relevantes": Uma lista contendo apenas as mensagens de log dos erros que você considerou relevantes.
        
        **Logs para Analisar:**
        ---
        {chr(10).join(logs)}
        ---
        """
        
        try:
            print("Enviando logs para análise da IA...")
            response = self.generative_model.generate_content(prompt)
            # Limpeza para garantir que a resposta seja um JSON válido
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)
        except Exception as e:
            print(f"Ocorreu um erro ao chamar a API do Gemini para análise: {e}")
            return {"error": "Erro ao processar a análise dos logs.", "details": str(e)}

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
        

    


        
# --- Exemplo de como usar a classe centralizada ---
if __name__ == '__main__':
    ia_helper = AI()
    
    # Exemplo de uma lista de logs que viria do seu Log_manager
    logs_da_execucao = [
        "[INFO] - routine='Pessoas - test_insere_documento_pessoa' - Iniciando cenário de teste: Caminho feliz.",
        "[ERROR] - routine='Pessoas - test_insere_documento_pessoa' - level='ERROR' - Falha ao inserir pessoa: O CPF '12345678900' já está cadastrado no sistema.",
        "[INFO] - routine='Pessoas - test_insere_documento_pessoa' - Teste finalizado.",
        "[WARNING] - routine='Pessoas - test_insere_dependente_pessoa' - level='WARNING' - O campo 'Cartão Dependente' está vazio, mas não é obrigatório.",
        "[ERROR] - routine='Pessoas - test_insere_dependente_pessoa' - level='ERROR' - Elemento '#botaoSalvarDependente' não encontrado na tela.",
        "[ERROR] - routine='Pessoas - test_insere_dependente_pessoa' - level='ERROR' - TimeoutException: Timed out receiving message from renderer.",
        "[INFO] - routine='Login' - Teste de login com sucesso.",
    ]
    
    # 1. Usando a função para analisar e filtrar os erros
    resumo_dos_erros = ia_helper.analisar_logs_e_extrair_erros(logs_da_execucao)
    
    print("\n--- ANÁLISE DE ERROS RELEVANTES PELA IA ---")
    print(json.dumps(resumo_dos_erros, indent=2, ensure_ascii=False))

    # 2. Usando a função para gerar embeddings (apenas como exemplo)
    # embeddings = ia_helper.gerar_embeddings_para_logs(logs_da_execucao)
    # if embeddings:
    #     print(f"\n--- EMBEDDINGS GERADOS ---")
    #     print(f"Gerado {len(embeddings)} embeddings. Exemplo do primeiro:")
    #     print(embeddings[0])

