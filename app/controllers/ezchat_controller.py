from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.ezchat_service import cadastrar_user_ezchat, desativar_users_ezchat

router = APIRouter()

class EzchatRequest(BaseModel):
    email: str
    setores: List[str]

class EzchatDeactivateRequest(BaseModel):
    emails: List[str]

@router.post("/create", summary="Cria usuário no EZChat")
def ezchat_create(request: EzchatRequest):
    if not request.email or not request.setores:
        raise HTTPException(status_code=400, detail="Campos obrigatórios: email e setores[]")

    resposta, status = cadastrar_user_ezchat(request.email, request.setores)

    if status >= 400:
        raise HTTPException(status_code=status, detail=resposta)

    return resposta

@router.post("/deactivate", summary="Desativa usuários no EZChat")
def ezchat_deactivate(request: EzchatDeactivateRequest):
    if not request.emails:
        raise HTTPException(status_code=400, detail="Campo obrigatório: emails[]")

    resposta, status = desativar_users_ezchat(request.emails)

    if status >= 400:
        raise HTTPException(status_code=status, detail=resposta)
    
    print(resposta)

    return resposta
