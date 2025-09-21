from fastapi import APIRouter, HTTPException, responses, Depends, Header
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
import os
from typing import Annotated
from dotenv import load_dotenv
from depends import QueryRequest
from db_manager import dbs
import asyncio
from concurrent.futures import ThreadPoolExecutor

auth_routes = APIRouter(prefix="/auth", tags=["token"])

@auth_routes.get("/")
async def read_root():
    return {"Acessando rota de autenticacao"}

# Carregar variáveis de ambiente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "vector_database")
env_path = os.path.join(BASE_DIR,"..","..", "config.env")
load_dotenv(env_path)

executor = ThreadPoolExecutor(max_workers=20)

API_KEY = os.getenv("API_KEY")

prompt_template = """
Você é um assistente especializado em atendimento ao cliente.  
Responda SOMENTE com base nas informações abaixo.  

INFORMAÇÕES DISPONÍVEIS:  
{base_conhecimento}  

PERGUNTA: {pergunta}  
Resposta:
"""

llm = OllamaLLM(model="llama3:8b", gpu=True)

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["pergunta", "base_conhecimento"]
)

# Verificação da API Key
async def verificar_api_key(api_key: Annotated[str, Header(alias="X-API-Key")] = None):
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Chave de API não fornecida. Use o header 'X-API-Key'"
        )
    
    if api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Chave de API inválida"
        )
    
    return api_key

# Endpoint principal
@auth_routes.post("/query")
async def query_auth(request: QueryRequest, api_key: str = Depends(verificar_api_key)):
    
    try:
        pergunta = request.pergunta
    

        # Buscar no banco da categoria
        db = dbs.get("default")
        if db is None:
            raise HTTPException(status_code=500, detail="Banco vetorial não carregado")

        loop = asyncio.get_running_loop()
        resultados = await loop.run_in_executor(
            executor, db.similarity_search, pergunta, 6
        )
        #resultados = db.similarity_search(pergunta, k=6)

        print(f"Resultados encontrados para '{pergunta}': {len(resultados)}")

        if not resultados:
            return responses.JSONResponse(
                content={"message": "Nenhum resultado encontrado para sua pergunta."}
            )
            
        base_conhecimento = "\n".join([doc.page_content for doc in resultados])

        # Montar prompt
        entrada = prompt.format(base_conhecimento=base_conhecimento, pergunta=pergunta)

        # Chamar modelo
        resposta = llm.invoke(entrada)
        return responses.JSONResponse(content={"message": resposta})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

# Endpoint de debug
@auth_routes.get("/debug")
async def debug_paths():
    """Rota para debug dos caminhos"""
    return {
        "base_dir": BASE_DIR,
        "db_path": DB_PATH,
        "db_path_exists": os.path.exists(DB_PATH),
        "categorias_disponiveis": list(dbs.keys()),
        "env": env_path,
    }
