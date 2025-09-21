from langchain_community.document_loaders import PyPDFDirectoryLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import shutil
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# PATH deve ser o caminho para a pasta "base_conhecimento"
PATH = os.path.join(BASE_DIR, "..", "base_conhecimento")
DB_PATH = os.path.join(BASE_DIR, "..", "vector_database")

def criar_db():
    shutil.rmtree(DB_PATH, ignore_errors=True)
    os.makedirs(DB_PATH, exist_ok=True)
    
    embeddings = HuggingFaceEmbeddings(
        model_name="intfloat/e5-large-v2",
        model_kwargs={
            'device': 'cpu',
            'trust_remote_code': True
        },
        encode_kwargs={
            'batch_size': 8,
            'normalize_embeddings': True
        }
    )
    
    try:
        # Constroi o caminho completo do arquivo
        caminho_arquivo = os.path.join(PATH, "ArquivoBase.docx")
        
        # Usa o Docx2txtLoader para carregar o arquivo
        loader = Docx2txtLoader(caminho_arquivo)
        
        # O loader retorna uma lista de documentos que o text splitter pode processar
        documentos = loader.load()
        
        chunks = dividir_em_chunks(documentos)
        vetorizar_chunks(chunks, embeddings)
        
    except FileNotFoundError:
        print(f"Erro ao criar DB: Arquivo não encontrado em {caminho_arquivo}")
    except Exception as e:
        print(f"Erro ao criar DB: {e}")

def dividir_em_chunks(documentos):
    separador = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    chunks = separador.split_documents(documentos)
    print(f"Chunks criados: {len(chunks)}")
    return chunks

def vetorizar_chunks(chunks, embeddings):
    # O caminho para o banco de dados também deve ser um diretório
    persist_path = DB_PATH
    db = Chroma.from_documents(chunks, embeddings, persist_directory=persist_path)
    print(f"Vetorizada com sucesso!")

criar_db()