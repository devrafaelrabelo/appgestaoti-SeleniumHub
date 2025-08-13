# =========================
# app/utils/health_checks.py
# =========================

import httpx
from app.config.settings import settings
from docker import from_env

docker_client = from_env()

def mapear_container_por_ip(ip: str) -> str | None:
    for container in docker_client.containers.list():
        redes = container.attrs.get("NetworkSettings", {}).get("Networks", {})
        for _, dados in redes.items():
            if dados.get("IPAddress") == ip:
                return container.name
    return None

async def testar_get(url: str, headers: dict = None, params: dict = None) -> bool:
    try:
        async with httpx.AsyncClient(timeout=settings.TIMEOUT_REQUESTS) as client:
            response = await client.get(url, headers=headers, params=params)
            return response.status_code < 400
    except Exception:
        return False

async def testar_portal_transparencia() -> bool:
    url = settings.API_PORTAL_URL
    headers = {
        "chave-api-dados": settings.API_PORTAL_KEY
    }
    params = {
        "cpf": "00000000191",
        "pagina": 1
    }
    return await testar_get(url, headers=headers, params=params)

async def testar_selenium_grid_status_resumido():
    try:
        async with httpx.AsyncClient(timeout=settings.TIMEOUT_REQUESTS_SELENIUM) as client:
            response = await client.get(settings.REMOTE_SELENIUM_URL_STATUS)
            if response.status_code != 200:
                return {"ok": False, "error": f"Status {response.status_code}"}

            data = response.json().get("value", {})
            nodes = data.get("nodes", [])

            total_nodes = len(nodes)
            total_sessions = 0
            total_slots = 0
            nodes_em_uso = 0
            chrome_nodes = []

            for node in nodes:
                uri = node.get("uri")
                ip = uri.split("//")[-1].split(":")[0]
                container_name = mapear_container_por_ip(ip)

                slots = node.get("slots", [])
                active_sessions = sum(1 for slot in slots if slot.get("session"))
                total_sessions += active_sessions
                total_slots += len(slots)

                if active_sessions > 0:
                    nodes_em_uso += 1

                chrome_nodes.append({
                    "uri": uri,
                    "container_name": container_name,
                    "in_use": active_sessions > 0,
                    "active_sessions": active_sessions,
                    "total_slots": len(slots)
                })

            return {
                "ok": data.get("ready", False),
                "nodes_total": total_nodes,
                "sessions_active": total_sessions,
                "sessions_max": total_slots,
                "nodes_em_uso": nodes_em_uso,
                "chrome_nodes": chrome_nodes
            }

    except Exception as e:
        return {"ok": False, "error": str(e)}
