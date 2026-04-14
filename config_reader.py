from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from typing import ClassVar
import os
from pathlib import Path

class Settings(BaseSettings):

    bot_token: SecretStr
    DB_USER: SecretStr
    DB_PASSWORD: SecretStr
    DB_PORT: SecretStr
    GGL_API_KEY: SecretStr
    TG_API_ID: SecretStr
    TG_API_HASH: SecretStr
    BOT_NAME: SecretStr
    DB_NAME: SecretStr
    DBLOG_NAME: SecretStr
    PROD_DB_HOST: SecretStr
    PROD_DB_PORT: SecretStr
    PROD_DB_USER: SecretStr
    PROD_DB_PASSWORD: SecretStr

    URL_AGR: ClassVar[str] = "https://pigeoncorner.github.io/tg_app_lingo/index.html?page=agreement"
    URL_TZ: ClassVar[str] = "https://pigeoncorner.github.io/tg_app_lingo/index.html?page=timezone"
    URL_HELP: ClassVar[str] = "https://pigeoncorner.github.io/tg_app_lingo/index.html?page=help"

    if os.name == 'nt':
        font_path: ClassVar[str] = r"C:\Windows\Fonts\constan.ttf"
        model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    else:
        script_dir: ClassVar[Path] = Path(__file__).parent
        model_config = SettingsConfigDict(env_file=str(script_dir / 'env.env'), env_file_encoding='utf-8')
        font_path: ClassVar[str] = "/usr/share/fonts/truetype/vista/constan.ttf"



config = Settings()


