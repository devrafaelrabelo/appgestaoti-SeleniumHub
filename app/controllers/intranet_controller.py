from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List
from app.config.settings import settings 
import re

from app.services.intranet_service import (
    cadastrar_usuario_intranet_simples,
    apagar_usuarios_intranet_multiplos
)


# ✅ Definir antes de usar
router = APIRouter()

from app.config.settings import settings 
EMAIL_REGEX = re.compile(rf"^[a-zA-Z0-9_.+-]+@{re.escape(settings.EMAIL_DOMINIO_PERMITIDO)}$")

class IntranetCadastroRequest(BaseModel):
    nome_completo: str
    email: EmailStr

class EmailListaRequest(BaseModel):
    emails: List[str]

@router.post("/cadastrointranet", summary="Cadastrar usuário simples na intranet")
def cadastrar_intranet(request: IntranetCadastroRequest):
    if not request.nome_completo or not request.email:
        raise HTTPException(status_code=400, detail="Informe nome_completo e email")

    resultado = cadastrar_usuario_intranet_simples(request.nome_completo, request.email)
    status = 200 if resultado.get("status") == "sucesso" else 500
    return resultado, status

@router.post("/apagarlista", summary="Apagar múltiplos usuários da intranet")
def apagar_lista_intranet(request: EmailListaRequest):
    emails_validos = [email for email in request.emails if EMAIL_REGEX.match(email)]
    emails_invalidos = [email for email in request.emails if email not in emails_validos]

    if not emails_validos:
        raise HTTPException(status_code=400, detail="Nenhum e-mail válido com domínio permitido encontrado")

    resultado = apagar_usuarios_intranet_multiplos(emails_validos)

    if emails_invalidos:
        resultado.setdefault("log", []).append({
            "status": "e-mails ignorados por domínio inválido",
            "itens": emails_invalidos
        })

    return resultado
