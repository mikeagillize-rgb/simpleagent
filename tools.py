import os
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


load_dotenv()

MY_DB = "db"
MODELO = "intfloat/multilingual-e5-small"


def carregar_db():
    embeddings = HuggingFaceEmbeddings(model_name=MODELO)
    return Chroma(
        persist_directory=MY_DB,
        embedding_function=embeddings,
    )

@tool
def dados_server():
    """Retorna informações sobre o servidor, como CPU, memória e disco.

    Use esta ferramenta sempre que o usuário perguntar sobre o estado do servidor, status do servidor, como o servidor está, ou qualquer pergunta relacionada ao servidor
    desempenho, recursos ou monitoramento.
    NÃO use para perguntas sobre clima, biografias ou assuntos gerais.
    """
    cpu = os.cpu_count()
    memoria = round(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024. ** 3), 2)
    disco = round(os.statvfs('/').f_frsize * os.statvfs('/').f_blocks / (1024. ** 3), 2)
    return f"CPU: {cpu} núcleos, Memória: {memoria} GB, Disco: {disco} GB."


@tool
def tempo_hoje(cidade: str) -> str:
    """Retorna a previsão do tempo atual para uma cidade específica.

    Use esta ferramenta sempre que o usuário perguntar sobre clima,
    temperatura, chuva ou condições meteorológicas de uma cidade.
    NÃO use para perguntas sobre pessoas, biografias ou assuntos gerais.
    """
    return f"O tempo em {cidade} hoje é ensolarado com 25°C."


@tool
def enviar_email(destinatario: str, destinatario_nome: str, corpo: str) -> str:
    """Envia um email em nome do Mike para um destinatário.

    Use esta ferramenta SOMENTE quando o usuário (Mike) pedir explicitamente
    para enviar um email. Nunca envie emails por iniciativa própria.

    O email será formatado automaticamente com uma introdução bem-humorada
    do assistente do Mike, seguida da mensagem que o Mike quer transmitir.

    Args:
        destinatario: endereço de email do destinatário (ex: alguem@exemplo.com)
        destinatario_nome: nome ou apelido do destinatário (ex: Fulano, João, chefe)
        corpo: mensagem que o Mike quer transmitir ao destinatário
    """
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    remetente = os.getenv("SMTP_FROM", user)

    if not all([host, user, password]):
        return "Erro: credenciais SMTP não configuradas no .env."

    # Monta a introdução bem-humorada do assistente
    introducao = (
        f"Fala {destinatario_nome}, tudo em paz?\n\n"
        f"Sou o agente assistente da Vossa Excelência Mike, vim passar um recado?\n\n"
    )

    assinatura = (
        "\n\n---\n"
        "Enviado pelo assistente pessoal do Mike 🤖\n"
        "(Sim, ele tem um agora. A modernidade chegou.)"
    )

    mensagem_formatada = introducao + corpo + assinatura

    msg = MIMEMultipart()
    msg["From"] = remetente
    msg["To"] = destinatario
    msg["Subject"] = "Recado da Vossa Excelência Mike"
    msg.attach(MIMEText(mensagem_formatada, "plain", "utf-8"))

    try:
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
        return f"Email enviado com sucesso para {destinatario} ({destinatario_nome})."
    except smtplib.SMTPAuthenticationError:
        return "Erro: falha na autenticação SMTP. Verifique usuário/senha de app."
    except smtplib.SMTPException as e:
        return f"Erro SMTP ao enviar email: {e}"
    except Exception as e:
        return f"Erro inesperado ao enviar email: {e}"

@tool
def buscar_biografia_mike(pergunta: str) -> str:
    """Busca informações sobre a biografia, história, vida ou dados
    pessoais do Mike na base de conhecimento local.

    Use esta ferramenta SEMPRE que o usuário perguntar sobre o Mike,
    quem ele é, sua história, sua vida, suas preferências, etc.
    NÃO use para perguntas sobre clima, cálculos ou assuntos gerais.
    """
    db = carregar_db()
    resultados = db.similarity_search_with_relevance_scores(pergunta, k=4)

    # filtra por score mínimo
    resultados = [(doc, score) for doc, score in resultados if score >= 0.7]

    if not resultados:
        return "Nenhuma informação relevante sobre o Mike foi encontrada na base."

    trechos = []
    for i, (doc, score) in enumerate(resultados, 1):
        trechos.append(f"Trecho {i} (relevância {score:.2f}):\n{doc.page_content}")

    return "\n\n".join(trechos)

