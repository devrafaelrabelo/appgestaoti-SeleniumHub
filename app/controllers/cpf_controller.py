from fastapi import APIRouter, HTTPException
from app.services.cpf_service import processar_consulta
from app.schemas.cpf_schema import CPFRequest, CPFResponse

router = APIRouter()


@router.post("/consultarcpf", response_model=CPFResponse, summary="Consulta CPF com fallback inteligente")
async def consultar_cpf(request: CPFRequest):
    if not request.cpf or not request.data_nascimento:
        raise HTTPException(status_code=400, detail="Informe cpf e data_nascimento")

    resultado = await processar_consulta(request.cpf, request.data_nascimento)

    if resultado.get("status") == "falha":
        raise HTTPException(status_code=400, detail=resultado.get("mensagem"))

    return resultado
