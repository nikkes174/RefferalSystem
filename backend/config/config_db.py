from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    url: str
    echo: bool = False

    class Config:
        env_prefix = "DB_"
        env_file = ".env"
