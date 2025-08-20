import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr, FilePath
from typing import Optional
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- 1. O MODELO DE DADOS (O "PEDIDO") ---
# Movido para fora para ser um componente independente e reutilizável.
class EmailModel(BaseModel):
    """Modelo Pydantic para validar os dados de um e-mail."""
    destinatario: EmailStr  # Pydantic já valida se é um e-mail válido
    assunto: str
    corpo: str
    # O caminho da imagem é opcional. Se não for fornecido, não anexa nada.
    caminho_imagem: Optional[FilePath] = None # Pydantic valida se o arquivo existe
    nome_arquivo_anexo: Optional[str] = None


# --- 2. O COMPOSITOR (O "MONTADOR") ---
class EmailComposer:
    """
    Constrói um objeto MIMEMultipart a partir de um modelo de dados.
    Sua única responsabilidade é montar a mensagem.
    """
    def __init__(self, remetente: str, data: EmailModel):
        self.remetente = remetente
        self.data = data
        self.msg = MIMEMultipart()

    def _build_headers(self):
        """Constrói os cabeçalhos do e-mail."""
        self.msg['From'] = self.remetente
        self.msg['To'] = self.data.destinatario
        self.msg['Subject'] = self.data.assunto

    def _attach_body(self):
        """Anexa o corpo de texto ao e-mail."""
        self.msg.attach(MIMEText(self.data.corpo, 'plain', 'utf-8'))

    def _attach_image(self):
        """Anexa a imagem, se um caminho for fornecido."""
        if self.data.caminho_imagem and self.data.nome_arquivo_anexo:
            with open(self.data.caminho_imagem, 'rb') as fp:
                imagem = MIMEImage(fp.read(), name=self.data.nome_arquivo_anexo)
                imagem.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{self.data.nome_arquivo_anexo}"'
                )
                self.msg.attach(imagem)

    def build_message(self) -> MIMEMultipart:
        """
        Orquestra a construção do e-mail e retorna o objeto MIME completo.
        """
        self._build_headers()
        self._attach_body()
        self._attach_image()
        return self.msg


# --- 3. O ENVIADOR (O "CARTEIRO") ---
class EmailSender:
    """
    Envia um objeto MIMEMultipart usando um servidor SMTP.
    Sua única responsabilidade é a comunicação com o servidor.
    """
    def __init__(self, host: str, port: int, email: str, senha: str):
        self.host = host
        self.port = port
        self.email = email
        self.senha = senha

    def send(self, message: MIMEMultipart):
        """Conecta-se ao servidor e envia a mensagem."""
        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.email, self.senha)
                server.send_message(message)
            print("E-mail enviado com sucesso!")
            return True
        except smtplib.SMTPAuthenticationError:
            print("Erro de autenticação. Verifique e-mail/senha ou use uma Senha de App.")
            return False
        except Exception as e:
            print(f"Ocorreu um erro ao enviar o e-mail: {e}")
            return False


# --- 4. EXEMPLO DE USO ---
if __name__ == "__main__":
    # Carrega as credenciais de forma segura
    EMAIL_REMETENTE = os.getenv('EMAIL')
    SENHA_REMETENTE = os.getenv('SENHA')

    # Valida se as credenciais foram carregadas
    if not EMAIL_REMETENTE or not SENHA_REMETENTE:
        raise ValueError("As variáveis de ambiente EMAIL e SENHA não foram definidas.")

    # a) Crie o "pedido" do e-mail usando o modelo Pydantic
    try:
        dados_email = EmailModel(
            destinatario="destinatario.feliz@exemplo.com",
            assunto="Código Refatorado e Modular!",
            corpo="Olá!\n\nEste e-mail foi enviado com uma arquitetura de classes muito mais limpa e modular em Python.\n\nAtenciosamente,\nSeu Código.",
            caminho_imagem="./caminho/para/sua/imagem.jpg", # Altere para um caminho válido
            nome_arquivo_anexo="python-logo.jpg"
        )
    except Exception as e:
        print(f"Erro na validação dos dados do e-mail: {e}")
        exit()

    # b) Use o "Montador" para construir a mensagem
    print("Montando a mensagem...")
    compositor = EmailComposer(remetente=EMAIL_REMETENTE, data=dados_email)
    mensagem_pronta = compositor.build_message()

    # c) Configure o "Carteiro" para o Outlook
    servidor_gmail = {
        "host": "smtp.gmail.com",
        "port": 587,
        "email": EMAIL_REMETENTE,
        "senha": SENHA_REMETENTE
    }
    enviador = EmailSender(**servidor_gmail)

    # d) Envie!
    print("Enviando o e-mail...")
    enviador.send(mensagem_pronta)