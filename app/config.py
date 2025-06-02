from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_SECONDS: int = Field(86400, env="ACCESS_TOKEN_EXPIRE_SECONDS")
    BASIC_AUTH_USERNAME: str = Field(..., env="BASIC_AUTH_USERNAME")
    BASIC_AUTH_PASSWORD_HASH: str = Field(..., env="BASIC_AUTH_PASSWORD_HASH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
