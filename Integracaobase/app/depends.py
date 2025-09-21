from pydantic import BaseModel

class QueryRequest(BaseModel):
    pergunta: str
    
