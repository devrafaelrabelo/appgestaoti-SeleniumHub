from pydantic import BaseModel


class CPFRequest(BaseModel):
    cpf: str
    data_nascimento: str


class CPFResponse(BaseModel):
    status: str  # "sucesso" ou "falha"
    nome: str | None = None
    mensagem: str | None = None
