from importlib.metadata import version
from typing import Type, Tuple
from pathlib import Path
from click import get_app_dir
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

APP_NAME = "chercher"
APP_DIR = Path(get_app_dir(app_name=APP_NAME))
CONFIG_FILE_PATH = APP_DIR / "config.toml"


class Settings(BaseSettings):
    name: str = APP_NAME
    description: str = "Chercher, the universal and personal search engine."
    version: str = version(APP_NAME)

    db_url: str = f"{APP_DIR}/db.sqlite3"

    model_config = SettingsConfigDict(
        toml_file=CONFIG_FILE_PATH,
        extra="allow",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        APP_DIR.mkdir(parents=True, exist_ok=True)

        return (
            init_settings,
            TomlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


if __name__ == "__main__":
    settings = Settings()
    print(settings.model_dump_json())
