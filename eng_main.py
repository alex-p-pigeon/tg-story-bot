
from datetime import datetime, date, timezone, timedelta

print("Current time1:", datetime.now().time().strftime("%H:%M:%S"))
#import sqlite3
#from sqlite3 import Error

#from openai import OpenAI
#from telegram.constants import ParseMode
#import time


import logging
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.fsm.context import FSMContext
#from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.state import StatesGroup, State
import redis.asyncio as aioredis  # This provides async Redis support
import asyncio

import sys, io, os



from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


'''
import nltk
from nltk.corpus import cmudict
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import pos_tag
from spellchecker import SpellChecker
import language_tool_python
import spacy
'''

#from google.cloud import texttospeech          #

#import signal
#from aiogram.contrib.middlewares.logging import LoggingMiddleware
#from aiogram.types import ParseMode
#from aiogram.utils import executor
#new
#import langid
#import fasttext

#personal functions, routers, libs
from config_reader import config
import selfFunctions as myF
import prompt as myP
#import fDB as myDB
import fpgDB as pgDB
from handlers import r_oth, r_learnpath
from states import myState
import classes as myClass



print("Current time2:end import:", datetime.now().time().strftime("%H:%M:%S"))


#========================================================================================================================================================classes

class MaintenanceMiddleware(BaseMiddleware):
    """Middleware для уведомления о технических работах"""

    def __init__(self, maintenance_mode: bool = False, custom_message: str = None):
        super().__init__()
        self.maintenance_mode = maintenance_mode
        self.custom_message = custom_message or (
            "? <b>Временные технические работы</b>\n\n"
            "Наш хостинг-провайдер испытывает серьезный сбой в датацентре. "
            "Работаем над восстановлением сервиса.\n\n"
            "⏰ Сервис будет полностью восстановлен в течение 24-48 часов.\n"
            "? Все ваши данные и прогресс сохранены.\n\n"
            "Спасибо за понимание! ?"
        )

    async def __call__(
            self,
            handler,
            event: TelegramObject,
            data: dict
    ):
        if not self.maintenance_mode:
            # Если режим обслуживания отключен, продолжаем обычную обработку
            return await handler(event, data)

        # Получаем объект бота из data
        bot = data.get('bot')
        if not bot:
            return await handler(event, data)

        # Обрабатываем разные типы событий
        chat_id = None
        if hasattr(event, 'message') and event.message:
            chat_id = event.message.chat.id
        elif hasattr(event, 'chat') and event.chat:
            chat_id = event.chat.id
        elif hasattr(event, 'callback_query') and event.callback_query:
            chat_id = event.callback_query.message.chat.id
            # Отвечаем на callback query
            await event.callback_query.answer("Бот временно недоступен из-за технических работ")

        if chat_id:
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=self.custom_message,
                    parse_mode="HTML"
                )
                logger.info(f"Sent maintenance message to chat_id: {chat_id}")
            except Exception as e:
                logger.error(f"Failed to send maintenance message: {e}")

        # НЕ продолжаем обработку - возвращаем None
        return None


#========================================================================================================================================================INIT

def setup_logging():
    # Fix Windows console encoding first
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    project_root = os.path.dirname(os.path.abspath(__file__))
    logging.info(f'-----------project_root:{project_root}')
    log_file = os.path.join(project_root, 'app.log')

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # Добавьте эту строку - очистить ВСЕ handlers
    root_logger.setLevel(logging.DEBUG)  # Set to lowest level

    # Console handler (INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File handler (DEBUG level)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    #file_handler = logging.FileHandler('app.log')
    #logging.info(f'-----------file_handler:{file_handler}')
    #logging.info(f'-----------log_file:{log_file}')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Reduce logging verbosity
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    logging.info("Logging setup completed")


def configure_aiogram_logging():
    """Настройка логирования aiogram после инициализации"""
    for logger_name in ['aiogram', 'aiogram.event', 'aiogram.dispatcher']:
        aiogram_logger = logging.getLogger(logger_name)
        aiogram_logger.handlers.clear()  # Удаляем handlers aiogram
        aiogram_logger.propagate = True  # Используем root logger
        aiogram_logger.setLevel(logging.INFO)

    logger.info("Aiogram logging configured")

# Call setup function
setup_logging()

# Get logger for your module
logger = logging.getLogger(__name__)
logger.info("start logging")

# Capture uncaught exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception

#global constants
#db_name = 'engDB.sqlite'

#gcTime = 0
#gDivider = 4

#nltk.pos_tag(["test"])  # Forces POS tagger to load
#_ = wordnet.synsets("test")  # Forces WordNet to load

print('wordnet.synsets|end')

main_router = Router()

bot = Bot(token=config.bot_token.get_secret_value())
redis_client = aioredis.from_url("redis://localhost:6379")  #                172.25.138.213
storage = RedisStorage(redis_client)
dp = Dispatcher(storage=storage)


#========================================================================================================================================================functions async
    
#-----------------------------------------------------------------------------------------------------------------------------------------------ChatGPT f








# Создаем экземпляр бота
async def main():
    # ВКЛЮЧИТЬ/ВЫКЛЮЧИТЬ РЕЖИМ ТЕХНИЧЕСКИХ РАБОТ
    MAINTENANCE_MODE = False  # Поставь False чтобы отключить

    # Кастомное сообщение (опционально)
    maintenance_message = (
        "🔧 <b>Временные технические работы</b>\n\n"
        "Наш датацентр испытывает сбой оборудования. "
        "Команда техподдержки работает над восстановлением.\n\n"
        "⏰ Ожидаемое время восстановления: 24-48 часов\n"
        "📧 Уведомим о восстановлении через уведомления\n\n"
        "Извиняемся за неудобства! 🙏\n\n"
        "Команда LingoMojo"
    )

    pool = await pgDB.fPool_Init()
    pool_base, pool_log = pool


    nlp_tools = myClass.AsyncNLPTools()
    await nlp_tools.initialize()
    dp.workflow_data.update(nlp_tools=nlp_tools)        # Store in dispatcher's workflow data

    free_counter = myClass.FreeActionCounter(pool_base)
    dp.workflow_data.update(free_counter=free_counter)

    dp.message.middleware(myClass.DispatcherMiddleware(dp))     # Register middleware to inject dispatcher
    dp.callback_query.middleware(myClass.DispatcherMiddleware(dp))  # Add this line for callback queries

    main_router.include_router(r_learnpath)
    main_router.include_router(r_oth)
    dp.include_router(main_router)

    maintenance_middleware = MaintenanceMiddleware(
        maintenance_mode=MAINTENANCE_MODE,
        custom_message=maintenance_message
    )
    dp.update.middleware(maintenance_middleware)  # Добавляем первым!
    dp.update.middleware(myClass.FreeActionMiddleware(pool))  # Check free actions first
    dp.update.middleware(myClass.LogonStatusMiddleware(pool))
    dp.update.middleware(myClass.ConnPoolMiddleware(pool))

    #configure_aiogram_logging()
    logger.info(f"Starting bot with MAINTENANCE_MODE={MAINTENANCE_MODE}")

    await dp.start_polling(bot)    #
       
if __name__ == '__main__':
    asyncio.run(main())
   







