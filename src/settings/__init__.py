from fastapi_another_jwt_auth import AuthJWT
from src.settings.database import DatabaseSettings
from src.settings.jwt import AuthJWTSettings
from src.settings.email import EmailSettings


class Settings(AuthJWTSettings, DatabaseSettings, EmailSettings):
    class Config:
        env_file = ".env"


settings = Settings()


@AuthJWT.load_config
def get_config() -> Settings:
    return settings
