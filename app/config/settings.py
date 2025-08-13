from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # Variáveis de string direta
    URL_CONSULTA_CPF: str
    API_PORTAL_URL: str
    API_PORTAL_KEY: str

    REMOTE_SELENIUM_URL: str
    REMOTE_SELENIUM_URL_STATUS: str

    INTRANET_URL_BASE: str
    INTRANET_LOGIN_URL: str
    INTRANET_CADASTRO_USUARIO_URL: str
    INTRANET_LISTA_USUARIOS_URL: str

    EZCHAT_URL_BASE: str
    EZCHAT_LOGIN_URL: str
    EZCHAT_CADASTRO_USUARIO_URL: str

    IRONVOX_URL: str
    IRONVOX_URL_RAMAL: str
    IRONVOX_URL_AGENT: str
    IRONVOX_USER: str
    IRONVOX_PASSWORD: str

    WEBASSIST_URL_BASE: str
    WEBASSIST_URL_LOGIN: str
    WEBASSIST_URL_CADASTRO: str
    WEBASSIST_USER: str
    WEBASSIST_PASSWORD: str

    TIMEOUT_REQUESTS_SELENIUM: int
    TIMEOUT_REQUESTS: int

    EMAIL_DOMINIO_PERMITIDO: str
    ENCODED_SECRET: str
    JWT_ALGORITHM: str
    COOKIE_NAME: str

    # 🔥 Mudar o tipo para string
    PUBLIC_PATHS: str

    @property
    def public_paths_list(self) -> list[str]:
        return [x.strip() for x in self.PUBLIC_PATHS.split(",") if x.strip()]

    class Config:
        env_file = os.getenv("ENV_FILE", ".env.dev-container")
        extra = "ignore"


settings = Settings()
