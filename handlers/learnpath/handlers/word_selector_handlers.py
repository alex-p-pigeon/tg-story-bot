"""
Word Selector WebApp Handlers
Обработка выбора слов через WebApp
"""

import json
import base64
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from aiogram.enums import ParseMode
import fpgDB as pgDB
from config_reader import config


# ============================================================================
# ЗАПУСК WEBAPP
# ============================================================================

async def launch_word_selector_webapp(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int,
        activity_id: int
) -> None:
    """
    Запустить WebApp для выбора слов

    Args:
        message: Telegram message object
        state: FSM state
        pool: Database pool
        user_id: User ID
        lesson_id: Lesson ID
        activity_id: Activity ID
    """
    pool_base, pool_log = pool

    # Получаем 30 новых слов (чтобы URL не был слишком длинным)
    words = await fetch_words_for_selection(pool_base, user_id, limit=30)

    if not words:
        # Нет слов для выбора
        await message.answer(
            "ℹ️ <b>Недостаточно новых слов</b>\n\n"
            "В базе нет новых слов для изучения.",
            parse_mode=ParseMode.HTML
        )
        return

    # Сохраняем контекст в state
    await state.update_data(
        word_selector_activity_id=activity_id,
        word_selector_lesson_id=lesson_id
    )

    # Подготавливаем данные для WebApp
    words_data = []
    for word in words:
        obj_id, eng, ipa, rus, rus_alt, rank = word
        words_data.append({
            'obj_id': obj_id,
            'eng': eng,
            'ipa': ipa or '',
            'rus': rus,
            'rus_alt': rus_alt or '',
            'rank': rank or 0
        })

    # Кодируем данные в base64 с правильной обработкой UTF-8
    json_data = json.dumps(words_data, ensure_ascii=False)

    # Кодируем UTF-8 строку в base64
    encoded_data = base64.b64encode(json_data.encode('utf-8')).decode('ascii')

    print(f"DEBUG: Words count: {len(words)}")
    print(f"DEBUG: JSON length: {len(json_data)}")
    print(f"DEBUG: Base64 length: {len(encoded_data)}")
    print(f"DEBUG: First word: {words_data[0] if words_data else 'None'}")

    # Формируем URL через index.html с роутингом
    webapp_url = f"https://pigeoncorner.github.io/tg_app_lingo/index.html?page=wordselector&words={encoded_data}"

    # Создаем WebApp кнопку
    webapp = WebAppInfo(url=webapp_url)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(
            text="📝 Выбрать слова",
            web_app=webapp
        )]],
        resize_keyboard=True
    )

    # Отправляем сообщение с кнопкой
    str_msg = (
        f"📚 <b>Выбор слов для изучения</b>\n\n"
        f"Доступно <b>{len(words)}</b> новых слов.\n\n"
        f"Нажмите кнопку ниже, чтобы выбрать слова, "
        f"которые хотите добавить к изучению.\n\n"
        f"💡 <i>Рекомендуем выбирать не более 10 слов за раз</i>"
    )

    msg = await message.answer(
        str_msg,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

    await pgDB.fExec_LogQuery(
        pool_log,
        user_id,
        f"word_selector_launched|words_count:{len(words)}"
    )


# ============================================================================
# ОБРАБОТКА ДАННЫХ ОТ WEBAPP
# ============================================================================

async def handle_word_selector_data(
        message: types.Message,
        state: FSMContext,
        pool
) -> None:
    """
    Обработать данные от WebApp с выбранными словами

    Args:
        message: Message с web_app_data
        state: FSM state
        pool: Database pool
    """
    pool_base, pool_log = pool
    user_id = message.from_user.id

    try:
        # Парсим данные от WebApp
        data = json.loads(message.web_app_data.data)

        selected_ids = data.get('selected', [])
        rejected_ids = data.get('rejected', [])

        print(f"Word selector data - Selected: {len(selected_ids)}, Rejected: {len(rejected_ids)}")

        # Добавляем выбранные слова (status_id=2, is_lp=True)
        if selected_ids:
            await add_words_to_learning(pool_base, user_id, selected_ids)

        # Добавляем отклоненные слова (status_id=9, is_lp=True)
        if rejected_ids:
            await add_words_to_known(pool_base, user_id, rejected_ids)

        # Убираем WebApp кнопку
        from aiogram.types import ReplyKeyboardRemove
        await message.answer(
            ".",
            reply_markup=ReplyKeyboardRemove()
        )

        # Отправляем подтверждение
        str_msg = (
            f"✅ <b>Слова добавлены!</b>\n\n"
            f"• Добавлено к изучению: <b>{len(selected_ids)}</b>\n"
            f"• Отмечено как известные: <b>{len(rejected_ids)}</b>\n\n"
            f"Отличная работа! Продолжаем обучение."
        )

        await message.answer(str_msg, parse_mode=ParseMode.HTML)

        # Логируем
        await pgDB.fExec_LogQuery(
            pool_log,
            user_id,
            f"word_selector_completed|selected:{len(selected_ids)}|rejected:{len(rejected_ids)}"
        )

        # Получаем данные из state
        user_data = await state.get_data()
        activity_id = user_data.get('word_selector_activity_id')
        lesson_id = user_data.get('word_selector_lesson_id')

        # Завершаем активность
        if activity_id and lesson_id:
            from .learning_handler import complete_activity
            await complete_activity(message, state, pool, user_id, lesson_id, activity_id)

    except Exception as e:
        print(f"Error handling word selector data: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке данных. Попробуйте еще раз.",
            parse_mode=ParseMode.HTML
        )
        await pgDB.fExec_LogQuery(
            pool_log,
            user_id,
            f"word_selector_error|error:{str(e)}"
        )


# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

async def fetch_words_for_selection(
        pool_base,
        user_id: int,
        limit: int = 100
) -> list:
    """
    Выгрузить слова для выбора

    Returns:
        List[(obj_id, eng, ipa, rus, rus_alt, rank)]
    """
    query = f"""
        SELECT 
            o.obj_id,
            o.obj_eng,
            o.obj_ipa,
            o.obj_rus,
            o.obj_rus_alt,
            o.c_rank
        FROM tw_obj o
        WHERE o.theme_id = 3
            AND o.obj_id NOT IN (
                SELECT obj_id 
                FROM tw_userprogress 
                WHERE user_id = {user_id}
            )
            AND o.c_rank IS NOT NULL
        ORDER BY o.c_rank DESC
        LIMIT {limit}
    """

    result = await pgDB.fExec_SelectQuery(pool_base, query)
    return result if result else []


async def add_words_to_learning(
        pool_base,
        user_id: int,
        word_ids: list
) -> None:
    """
    Добавить слова к изучению (status_id=2, is_lp=True)

    Args:
        pool_base: Database pool
        user_id: User ID
        word_ids: List of word IDs
    """
    if not word_ids:
        return

    values = []
    for obj_id in word_ids:
        values.append(
            f"({user_id}, {obj_id}, 2, CURRENT_TIMESTAMP, CURRENT_DATE, TRUE)"
        )

    values_str = ", ".join(values)

    query = f"""
        INSERT INTO tw_userprogress 
        (user_id, obj_id, status_id, date_last_change, date_repeat, is_lp)
        VALUES {values_str}
        ON CONFLICT (user_id, obj_id) 
        DO UPDATE SET 
            status_id = 2,
            date_last_change = CURRENT_TIMESTAMP,
            date_repeat = CURRENT_DATE,
            is_lp = TRUE
    """

    await pgDB.fExec_UpdateQuery(pool_base, query)


async def add_words_to_known(
        pool_base,
        user_id: int,
        word_ids: list
) -> None:
    """
    Добавить слова в известные (status_id=9, is_lp=True)

    Args:
        pool_base: Database pool
        user_id: User ID
        word_ids: List of word IDs
    """
    if not word_ids:
        return

    values = []
    for obj_id in word_ids:
        values.append(f"({user_id}, {obj_id}, 9, TRUE)")

    values_str = ", ".join(values)

    query = f"""
        INSERT INTO tw_userprogress 
        (user_id, obj_id, status_id, is_lp)
        VALUES {values_str}
        ON CONFLICT (user_id, obj_id) 
        DO UPDATE SET 
            status_id = 9,
            date_last_change = NULL,
            date_repeat = NULL,
            is_lp = TRUE
    """

    await pgDB.fExec_UpdateQuery(pool_base, query)

# ============================================================================
# ROUTER REGISTRATION
# ============================================================================

# Добавьте этот handler в ваш router:
#
# @router.message(F.web_app_data)
# async def web_app_data_handler(message: types.Message, state: FSMContext, pool):
#     """Обработка всех данных от WebApp"""
#
#     # Определяем тип данных по содержимому
#     try:
#         data = json.loads(message.web_app_data.data)
#
#         if 'timezone' in data:
#             # Это данные timezone
#             await app_set_tz(message, state, pool)
#         elif 'selected' in data and 'rejected' in data:
#             # Это данные word selector
#             await handle_word_selector_data(message, state, pool)
#         else:
#             print(f"Unknown web_app_data format: {data}")
#
#     except Exception as e:
#         print(f"Error handling web_app_data: {e}")


# ============================================================================
# CONFIG
# ============================================================================

# Добавьте в config.py:
# URL_WORD_SELECTOR = "https://pigeoncorner.github.io/tg_app_lingo/index.html?page=wordselector"