from pathlib import Path

from pydantic import BaseSettings


class GeneralSettings(BaseSettings):
    DEBUG: bool = True
    BASE_DIR: Path = Path(__file__).parents[2]
    TEMPLATE_FOLDER: Path = BASE_DIR / "templates"
    DOMAIN: str
