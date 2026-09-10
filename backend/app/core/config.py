from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://labuser:labpass@db:5432/labdb"
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
