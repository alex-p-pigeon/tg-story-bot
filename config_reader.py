from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from typing import ClassVar
import os
from pathlib import Path

class Settings(BaseSettings):


    # Желательно вместо str использовать SecretStr 
    # для конфиденциальных данных, например, токена бота
    bot_token: SecretStr
    YC_ACCOUNT_ID: SecretStr
    YC_SECRET_KEY: SecretStr
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
    #URL_WORD_SELECTOR: ClassVar[str] = "https://pigeoncorner.github.io/tg_app_lingo/index.html?page=wordselector"



    # Начиная со второй версии pydantic, настройки класса настроек задаются
    # через model_config
    # В данном случае будет использоваться файла .env, который будет прочитан
    # с кодировкой UTF-8
    if os.name == 'nt':
        font_path: ClassVar[str] = r"C:\Windows\Fonts\constan.ttf"
        model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    else:
        script_dir: ClassVar[Path] = Path(__file__).parent
        model_config = SettingsConfigDict(env_file=str(script_dir / 'env.env'), env_file_encoding='utf-8') #'~/lingo/env.env'
        font_path: ClassVar[str] = "/usr/share/fonts/truetype/vista/constan.ttf"



# При импорте файла сразу создастся 
# и провалидируется объект конфига, 
# который можно далее импортировать из разных мест
config = Settings()


