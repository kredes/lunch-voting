import os
from enum import StrEnum, auto

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = auto()
    PRODUCTION = auto()
    CI = auto()


ENVIRONMENT = Environment(os.environ.get("ENVIRONMENT", Environment.DEVELOPMENT))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=f"{ENVIRONMENT}.env", env_file_encoding="utf-8")

    votes_per_user: int
    jwt_signing_key: str
    jwt_expiration_minutes: int


# mypy doesn't understand that this call doesn't actually require arguments
Config = Settings()  # type:ignore[call-arg]
