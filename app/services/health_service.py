# app/services/health_service.py

from app.utils.lifecycle import startup_time
from datetime import datetime, timedelta
from app.config.settings import settings
from app.utils.health_checks import (
    testar_get,
    testar_portal_transparencia,
    testar_selenium_grid_status_resumido
)

# Cache global
health_status_cache = {
    "status": "unknown",
    "timestamp": None,
    "services": {}
}

def get_cached_health_status():
    now = datetime.utcnow()
    uptime_seconds = int((now - startup_time).total_seconds())
    uptime_str = str(timedelta(seconds=uptime_seconds))

    return {
        **health_status_cache,
        "uptime_seconds": uptime_seconds,
        "uptime": uptime_str
    }

async def atualizar_health_cache():
    global health_status_cache

    receita_federal = await testar_get(settings.URL_CONSULTA_CPF)
    portal_transparencia = await testar_portal_transparencia()
    selenium_status = await testar_selenium_grid_status_resumido()
    intranet = await testar_get(settings.INTRANET_URL_BASE)
    ezchat = await testar_get(settings.EZCHAT_LOGIN_URL)
    ironvox_ramal = await testar_get(settings.IRONVOX_URL_RAMAL)
    ironvox_agent = await testar_get(settings.IRONVOX_URL_AGENT)

    status_geral = all([
        receita_federal,
        portal_transparencia,
        selenium_status.get("ok"),
        intranet,
        ezchat,
        ironvox_ramal,
        ironvox_agent
    ])

    health_status_cache = {
        "status": "ok" if status_geral else "degraded",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {
            "receita_federal": "ok" if receita_federal else "fail",
            "portal_transparencia": "ok" if portal_transparencia else "fail",
            "selenium_grid": selenium_status,
            "intranet": "ok" if intranet else "fail",
            "ezchat": "ok" if ezchat else "fail",
            "ironvox_ramal": "ok" if ironvox_ramal else "fail",
            "ironvox_agent": "ok" if ironvox_agent else "fail"
        }
    }
