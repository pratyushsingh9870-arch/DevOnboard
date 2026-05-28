from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    app_name: str = "DevOnboard"
    database_url: str
    secret_key: str
    github_token: str = ""
    openrouter_api_key: str = ""
    debug: bool = True

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()