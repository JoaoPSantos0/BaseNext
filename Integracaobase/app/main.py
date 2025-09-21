from fastapi import FastAPI
from contextlib import asynccontextmanager
from db_manager import dbs, DB_PATH, funcao_embedding
from langchain_chroma import Chroma
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    global dbs
    print("Carregando bancos na inicialização")

    path_categoria = DB_PATH
    if os.path.isdir(path_categoria):
        # aqui garante que a pasta tem dados do Chroma
        if os.listdir(path_categoria):
            dbs["default"] = Chroma(
                persist_directory=path_categoria,
                embedding_function=funcao_embedding
            )
            print("Categoria 'default' carregada")
        else:
            print(f"Pasta {path_categoria} existe, mas está vazia.")
    else:
        print(f"Pasta {path_categoria} não encontrada.")

    yield
    print("Limpando recursos")
    dbs.clear()

app = FastAPI(lifespan=lifespan)

from routes.routes import auth_routes
app.include_router(auth_routes)

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",   # dev local
    "http://192.168.0.1:3000", # se for acessar pela rede local
    # coloque o domínio de produção aqui depois
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
