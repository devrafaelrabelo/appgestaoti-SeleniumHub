# app/middleware/auth_middleware.py

import base64
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError, DecodeError

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED

from app.config.settings import settings


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.jwt_secret = base64.b64decode(settings.ENCODED_SECRET)
        self.jwt_algorithm = settings.JWT_ALGORITHM
        self.cookie_name = settings.COOKIE_NAME
        self.public_paths = set(settings.public_paths_list)


    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Ignora caminhos públicos e OPTIONS (CORS)
        if path in self.public_paths or path.startswith("/static") or request.method == "OPTIONS":
            return await call_next(request)

        # Tenta obter token
        token = request.cookies.get(self.cookie_name)
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]

        if not token:
            return JSONResponse(status_code=HTTP_401_UNAUTHORIZED, content={"error": "Token não encontrado"})

        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            request.state.user = payload
        except ExpiredSignatureError:
            return JSONResponse(status_code=HTTP_401_UNAUTHORIZED, content={"error": "Token expirado"})
        except (InvalidTokenError, DecodeError) as e:
            return JSONResponse(status_code=HTTP_401_UNAUTHORIZED, content={"error": "Token inválido"})

        return await call_next(request)
