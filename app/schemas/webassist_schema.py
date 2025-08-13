from pydantic import BaseModel
from typing import List

class WebAssistUser(BaseModel):
    nome: str
    email: str
    login: str
    situacao: str
    cliente: str
    perfil: str

class ListaUsuariosWebAssist(BaseModel):
    usuarios: List[WebAssistUser]