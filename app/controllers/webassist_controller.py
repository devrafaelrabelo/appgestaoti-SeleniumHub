from fastapi import APIRouter
from app.schemas.webassist_schema import ListaUsuariosWebAssist
from app.services.webassist_service import cadastrar_usuarios_webassist

router = APIRouter()

@router.post("/criar-acesso")
def criar_acesso_webassist(lista: ListaUsuariosWebAssist):
    return cadastrar_usuarios_webassist(lista.usuarios)