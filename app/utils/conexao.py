import requests
from urllib.parse import urlparse

def testar_conexao_url(url: str, timeout: int = 5) -> bool:
    """Tenta acessar a URL (sem hash) e retorna True se HTTP 200"""
    try:
        base_url = url.split("#")[0]  # Remove rota hash
        resposta = requests.get(base_url, timeout=timeout)
        print(f"🌐 Teste de acesso: {base_url} - Status: {resposta.status_code}")
        return resposta.status_code == 200
    except Exception as e:
        print(f"❌ Não foi possível acessar {url}: {e}")
        return False
