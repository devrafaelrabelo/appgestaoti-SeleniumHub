from fastapi import APIRouter
from app.services.health_service import get_cached_health_status

router = APIRouter()

@router.get("/health")
async def health_check():
    return get_cached_health_status()