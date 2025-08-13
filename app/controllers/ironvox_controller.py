from fastapi import APIRouter, HTTPException
from app.schemas.ironvox_schema import IronvoxAgenteRequest, IronvoxRamalRequest
from app.services.ironvox_service import processar_lista_agentes, processar_lista_ramais

router = APIRouter()


@router.post("/atualizar-agente", summary="Atualizar múltiplos agentes no IronVox")
def atualizar_agentes_endpoint(request: IronvoxAgenteRequest):
    try:
        resultados = processar_lista_agentes(request.agentes)
        return {
            "status": "ok",
            "qtd": len(resultados),
            "resultados": resultados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar agentes: {str(e)}")


@router.post("/atualizar-ramal", summary="Atualizar múltiplos ramais no IronVox")
def atualizar_ramais_endpoint(request: IronvoxRamalRequest):
    try:
        resultados = processar_lista_ramais(request.dados)
        return {
            "status": "ok",
            "qtd": len(resultados),
            "resultados": resultados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar ramais: {str(e)}")
