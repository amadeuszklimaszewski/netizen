from fastapi_another_jwt_auth import AuthJWT
from src.settings.database import DatabaseSettings
from src.settings.jwt import AuthJWTSettings
from src.settings.email import EmailSettings
from src.settings.general import BaseSettings


class Settings(AuthJWTSettings, DatabaseSettings, EmailSettings, BaseSettings):
    class Config:
        env_file = ".env"


settings = Settings()


@AuthJWT.load_config
def get_config() -> Settings:
    return settings
