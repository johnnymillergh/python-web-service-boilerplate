from pathlib import Path
from typing import Final, Literal

import tomllib
from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from python_web_service_boilerplate.common.common_function import (
    PROJECT_ROOT_PATH,
    get_resources_dir,
)


def check_existence(file_path: Path) -> bool:
    return file_path.exists() and file_path.is_file()


_pyproject_toml_file = PROJECT_ROOT_PATH / "pyproject.toml"
if not check_existence(_pyproject_toml_file):
    logger.warning(f"File not found: {_pyproject_toml_file}")
    _pyproject_toml_file = Path(__file__).parent.parent.parent / "pyproject.toml"
    logger.warning(f"Fallback to: {_pyproject_toml_file}")
    if not check_existence(_pyproject_toml_file):
        logger.error(f"Fallback failed due to file not found: {_pyproject_toml_file}")
        raise FileNotFoundError(f"File not found: {_pyproject_toml_file}")
with _pyproject_toml_file.open("rb") as file:
    pyproject_toml: Final = tomllib.load(file)


LogLevel = Literal["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="DATABASE_",
        case_sensitive=False,
    )

    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = Field(default="password")
    db_name: str = "boilerplate_db"
    sql_log_enabled: bool = True


def _default_logger() -> dict[str, LogLevel]:
    return {"faker": "INFO"}


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=get_resources_dir() / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
        env_nested_max_split=1,
    )

    offline: bool = False
    log_level: LogLevel = "DEBUG"
    logger: dict[str, LogLevel] = Field(default_factory=_default_logger)
    intercepted_loggers: list[str] = Field(default_factory=lambda: ["sqlalchemy.engine.Engine"])
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)


settings: Final[Settings] = Settings()


def configure() -> None:
    """Configure application."""
    logger.warning(f"Application configuration loaded, {settings}, {pyproject_toml['tool']['poetry']['name']}")
