from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "vector_database")

funcao_embedding = HuggingFaceEmbeddings(
    model_name="intfloat/e5-large-v2",
    model_kwargs={'device': 'cpu', 'trust_remote_code': True},
    encode_kwargs={'batch_size': 8, 'normalize_embeddings': True}
)

# Dicionário de bases carregadas
dbs = {}

def load_vector_db():
    """
    Carrega e mantém o banco aberto (singleton).
    Chame no startup da aplicação.
    """
    global dbs
    if not dbs:
        print("Carregando base vetorial…")
        dbs["default"] = Chroma(
            persist_directory=DB_PATH,
            embedding_function=funcao_embedding
        )
    return dbs
