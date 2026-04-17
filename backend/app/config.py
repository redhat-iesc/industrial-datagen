from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Industrial Datagen"
    debug: bool = False
    cors_origins: list[str] = ["*"]
    storage_backend: str = "memory"
    database_url: str = ""

    model_config = {"env_prefix": "INDGEN_"}


settings = Settings()
