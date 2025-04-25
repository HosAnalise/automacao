from fastapi import FastAPI,Query
from classes.utils.LogManager import LogManager
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from fastapi.responses import JSONResponse



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou ["http://localhost:5174"] para mais restrição
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Logs = LogManager()


@app.get("/items/")
def return_errors(id: Optional[str] = Query(default=None)):
    """
    Retorna os logs de erro.
    Se um ID de execução for fornecido, filtra por esse ID.
    Se não, retorna todos os logs de erro.
    """
    logs = Logs.get_error_logs(execution_id=id)
    return JSONResponse(content=logs)