
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
from langchain_huggingface import HuggingFaceEmbeddings


PASTA_PDF = "pdfs"

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")

def criar_indexador():
    documento_pdf = carregar_documentos_pdf()
    chunks = split_chinks(documento_pdf)
    vetorizador(chunks)

def carregar_documentos_pdf():
        carregador = PyPDFDirectoryLoader(PASTA_PDF, glob="**/*.pdf")
        documentos = carregador.load()
        return documentos

def split_chinks(documentos):
    separador_documento = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=80,
        length_function=len,
        add_start_index=True
    )
    
    chunks = separador_documento.split_documents(documentos)

    print(len(chunks))
    return chunks

def vetorizador(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-small",
    )
    db = Chroma.from_documents(
        documents = chunks,
        embedding = embeddings,
        persist_directory = "db"
    )

criar_indexador()

