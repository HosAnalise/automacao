import base64
import datetime
import json
from bs4 import BeautifulSoup
from dotenv import dotenv_values
from fastapi import HTTPException,requests
import oracledb
import warnings
from bs4 import MarkupResemblesLocatorWarning
import requests


getEnv = dotenv_values(".env")
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

class Decode:
    urlSendjson = getEnv.get("URL_SEND_JSON",'')

    _conn = None  # Conexão única

    @staticmethod
    def open_connection():
        if Decode._conn is None:
            user = getEnv.get("ORACLE_USER")
            password = getEnv.get("ORACLE_PASSWORD")
            host = getEnv.get("ORACLE_HOST")
            port = getEnv.get("ORACLE_PORT")
            service_name = getEnv.get("ORACLE_SERVICE_NAME")

            dsn = oracledb.makedsn(host, port, service_name)
            Decode._conn = oracledb.connect(user=user, password=password, dsn=dsn)
            print("✅ Conexão Oracle aberta.")

    @staticmethod
    def close_connection():
        if Decode._conn:
            Decode._conn.close()
            Decode._conn = None
            print("🔌 Conexão Oracle fechada.")


    @staticmethod
    def fetch_data(query=None, func=None, params=None):
        
        cursor = Decode._conn.cursor()

        if func and params:
            result = cursor.callfunc(func, str, params)
            Decode._conn.commit()
            return result
        elif query:
            if query.strip().lower().startswith("select"):
                cursor.execute(query)
                data = cursor.fetchall()
                result = []
                for row in data:
                    json_conteudo = row[2]
                    if isinstance(json_conteudo, oracledb.LOB):
                        json_conteudo = json_conteudo.read()
                    result.append((row[0], row[1], json_conteudo, row[3], row[4], row[5]))
                return result
            else:
                Decode._conn.commit()
                return None
    
    @staticmethod
    def decode_json_conteudo(encoded_content):
        if isinstance(encoded_content, oracledb.LOB):
            encoded_content = encoded_content.read()  # Converte LOB para string

        decoded = base64.b64decode(encoded_content).decode("utf-8")
        return json.loads(decoded)

  

    @staticmethod
    def process_content(json_data):
        content_list = []  # Lista para armazenar os conteúdos processados
        
        for item in json_data:
            tipo = item.get("tipo")
            conteudo = item.get("conteudo", "")
            
            if tipo in ["TEXTO", "SUBTITULO", "CARD_TITULO", "CARD"]:
                cleaned_text = BeautifulSoup(conteudo, "html.parser").get_text(separator="")
                content_list.append(cleaned_text)
                
            elif tipo == "VIDEO":
                content_list.append(f" linkVideo: {conteudo}")

        return "".join(content_list)  # Junta tudo em uma única string com quebras de linha
    

    @staticmethod
    def update_table(ids):
           Decode.open_connection()
           update =f"""
                        UPDATE 
                            ERP.BASE_CONHECIMENTO_FILA_RAG a 
                        SET 
                            a.SINCRONIZADO = 1 
                        WHERE 
                            a.PAGINA_BASE_ID in {ids} and a.SINCRONIZADO = 0
                    """
           Decode.fetch_data(query=update)
           Decode.close_connection()
           
    
    @staticmethod
    def generate_json():

        Decode.open_connection()
     
        query = """
            SELECT 
                PB.PAGINA_BASE_ID,
                PB.TITULO,
                PB.JSON_CONTEUDO,
                PB.BASE_ENTRADA_MENU_ID,
                PB.PAGINA_BASE_NIVEL_ACESSO_ID,
                PBN.DESCRICAO
            FROM 
                ERP.PAGINA_BASE  PB
            JOIN
                ERP.PAGINA_BASE_NIVEL_ACESSO PBN 
                ON PB.PAGINA_BASE_NIVEL_ACESSO_ID = PBN.PAGINA_BASE_NIVEL_ACESSO_ID

            WHERE
                exists (SELECT * FROM ERP.BASE_CONHECIMENTO_FILA_RAG a WHERE a.PAGINA_BASE_ID = PB.PAGINA_BASE_ID AND a.SINCRONIZADO = 0)
        """   
        data = Decode.fetch_data(query,None,None)
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S:%f")
        processed_data = []
        
        for row in data:
            json_conteudo = Decode.decode_json_conteudo(row[2])
            content = Decode.process_content(json_conteudo)
            linktype = 1 if row[4] == 1 else 2
            params = [linktype,"220",12,"P12_PAGINA_MOSTRAR",str(row[0])]
            func = "ERP.BD_LINK_REDIRECIONAMENTO.GERAR_LINK_REDIRECIONAMENTO"
            link = Decode.fetch_data(None,func,params)

            
            obj = {
                "meta": {
                    "documentoId": row[0],
                    "documentoMenuId": row[3],
                    "titulo": row[1],
                    "geradoEm": timestamp,
                    "nivelAcesso": row[5],
                    "url": link
                },
                "content": content
            }
            processed_data.append(obj)
        
        return json.dumps(processed_data, ensure_ascii=False, indent=4)
    


    @staticmethod
    def init():
        
        Decode.open_connection()
        data = Decode.generate_json()
        try:
            headers = {
                'Content-Type': 'application/json',
                "x-api-key": "22b63e7f5a73fc73227841a80b0c3ed788e06fc2d350c2d380118bc00f2776e6"
            }

            response = requests.post(Decode.urlSendjson, data=data, headers=headers)
            response.raise_for_status()
            print(response.json())
        except requests.exceptions.RequestException as e:
            print(f"Erro: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            Decode.close_connection()   


if __name__ == "__main__":
    Decode.init()
# Decode.close_connection() 

# Decode.init()  

    ids = 2181,4121,3901,4081
    Decode.update_table(ids)