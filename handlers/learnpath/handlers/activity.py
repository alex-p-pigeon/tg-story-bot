"""
Обработчики для отдельных типов заданий (Task 1-8)
"""

# Import question generator
#from ..generators.factory import QuestionGeneratorFactory
#from ..services.gram_20_generator import ToBeQuestionGenerator
#from ..services.gram_30_generator import PresentSimpleQuestionGenerator


from aiogram import types, Router, F        #, Bot
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, WebAppInfo, BufferedInputFile

from aiogram.filters import StateFilter
from typing import Dict, Any, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import random
import os, sys
import hashlib
import json
import csv
import shutil

import fpgDB as pgDB
from states import myState
import selfFunctions as myF
import mynaming as myN
import err_sender as myErr

from ..core.lesson_manager import LessonManager
from ..core.content_generator import ContentGenerator
import prompt as myP

from ..services.test_service import TestService
from ..services.task6_reading_service import Task6ReadingService

from ..handlers.story import show_questionnaire_q0





from .learning import complete_activity


# Get logger for this specific module
import logging
logger = logging.getLogger(__name__)

router = Router(name='activity')

# Константы
TARGET_WORDS_COUNT = 10
WORDS_PER_BATCH = 9
MAX_QUARTERS = 4  # Максимальное количество кварталов сложности

def ______________________task1():
    pass

# ============================================================================
# TASK 1: GRAMMAR ARTICLE (Грамматическая статья в miniapp)
# ============================================================================

async def launch_task1_grammar(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int,
        activity: Dict[str, Any]
) -> None:
    """Показать грамматическую статью"""
    lesson_manager = LessonManager(pool)
    lesson = await lesson_manager.get_lesson(lesson_id)

    grammar_code = lesson['grammar_article_code']
    article_url = activity['config'].get('article_url', '')

    if not article_url:
        # Формируем URL из grammar_code
        article_url = f"https://pigeoncorner.github.io/tg_app_lingo/index.html?page={grammar_code}"

    str_msg = (
        f"📖 <b>Грамматика</b>\n\n"
        f"Изучите грамматическую статью по ссылке ниже.\n"
        f"После прочтения нажмите кнопку для продолжения."
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="📚 Открыть статью",
        web_app=WebAppInfo(url=article_url)
    ))
    builder.add(InlineKeyboardButton(
        text="✅ Прочитал, продолжить",
        callback_data=f"complete_task_{activity['activity_id']}"
    ))
    builder.adjust(1)

    await message.answer(str_msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("complete_task_"))
async def complete_task_callback(callback: types.CallbackQuery, state: FSMContext, pool):
    """Обработка завершения задания"""

    pool_base, pool_log = pool
    user_id = callback.message.chat.id
    bot = callback.bot

    activity_id = int(callback.data.split("_")[-1])
    user_data = await state.get_data()
    lesson_id = user_data.get('current_lesson_id')

    if not lesson_id:
        #await callback.answer("Ошибка: урок не найден")
        await myErr.err_sender(bot, pool_log, user_id, 'Ошибка: урок не найден')
        return

    # Импортируем функцию завершения задания


    await complete_activity(callback.message, state, pool, user_id, lesson_id, activity_id)
    await pgDB.fExec_LogQuery(pool_log, user_id, f"complete_task|activity:{activity_id}")
    await callback.answer("✅ Задание выполнено!")

def ______________________task2():
    pass
# ============================================================================
# TASK 2: WORDS (Добавление слов для запоминания)
# FINAL: Фиксированные границы кварталов на весь урок
# ============================================================================

def fGetEmodjiNum(num: int) -> str:
    """Получить эмодзи цифру"""
    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
    return emojis[num - 1] if 1 <= num <= 9 else str(num)


async def launch_task2_words(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int,
        activity: Dict[str, Any]
) -> None:
    """Запустить добавление слов для запоминания"""
    pool_base = pool[0]

    # Парсим config
    config = activity.get('config', {})
    if isinstance(config, str):

        config = json.loads(config) if config else {}

    target_words = config.get('target_words', TARGET_WORDS_COUNT)

    # ВАЖНО: Рассчитываем границы кварталов ОДИН РАЗ в начале урока

    # X всегда 0, т.к. ranked_words начинается с индекса 1 для неизученных слов
    X = 0

    # Y = количество НЕизученных слов (которые попадут в ranked_words после LEFT JOIN)
    Y = await get_available_words_count(pool_base, user_id)

    # Размер одного квартала (фиксирован на весь урок!)
    quarter_size = Y / 4

    # Границы кварталов (фиксированы на весь урок!)
    # ВАЖНО: Используем строковые ключи, т.к. aiogram state сериализует в JSON
    quarters_bounds = {
        '1': (1, int(quarter_size)),  # Q1: 1 до Y/4
        '2': (int(quarter_size) + 1, int(2 * quarter_size)),  # Q2: Y/4+1 до Y/2
        '3': (int(2 * quarter_size) + 1, int(3 * quarter_size)),  # Q3: Y/2+1 до 3Y/4
        '4': (int(3 * quarter_size) + 1, Y)  # Q4: 3Y/4+1 до Y
    }

    # Инициализируем параметры адаптивной сложности
    await state.update_data(
        task2_activity_id=activity['activity_id'],
        task2_lesson_id=lesson_id,
        task2_target_words=target_words,
        task2_words_added_in_lesson=0,  # Счетчик слов, добавленных в этом уроке
        task2_quarter=1,  # Начинаем с первого квартала
        task2_q1_offset=0,  # Offset для последовательного выбора в квартале 1
        task2_quarters_bounds=quarters_bounds,  # Фиксированные границы кварталов
    )

    # Запускаем процесс выбора слов
    await show_words_selection(message, state, pool, user_id)


async def show_words_selection(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int
) -> None:
    """Показать слова для выбора"""
    pool_base, pool_log = pool
    bot = message.bot

    user_data = await state.get_data()
    target_words = user_data.get('task2_target_words', TARGET_WORDS_COUNT)
    words_added = user_data.get('task2_words_added_in_lesson', 0)
    quarter = user_data.get('task2_quarter', 1)
    q1_offset = user_data.get('task2_q1_offset', 0)
    quarters_bounds = user_data.get('task2_quarters_bounds')

    # Проверка: если quarters_bounds не инициализирован - ошибка состояния
    if not quarters_bounds:
        logger.error("ERROR: quarters_bounds not found in state")
        await myErr.err_sender(bot, pool_log, user_id, 'Произошла ошибка. Попробуйте начать урок заново|ERROR: quarters_bounds not found in state')
        return

    # Проверяем, достигли ли цели в рамках этого урока
    if words_added >= target_words:
        await finish_task2(message, state, pool, user_id)
        return

    # Выбираем слова в зависимости от квартала
    if quarter == 1:
        # Первый квартал - последовательные слова (топ по c_rank)
        words, new_offset = await fetch_words_quarter1(
            pool_base, user_id, WORDS_PER_BATCH,
            quarters_bounds[str(quarter)][0], quarters_bounds[str(quarter)][1], q1_offset
        )
    else:
        # Кварталы 2-4 - рандомные из диапазона
        words = await fetch_words_from_quarter(
            pool_base, user_id, WORDS_PER_BATCH,
            quarters_bounds[str(quarter)][0], quarters_bounds[str(quarter)][1]
        )
        new_offset = q1_offset  # Не меняем offset для кварталов 2-4

    if not words:
        # Нет новых слов - проверяем что делать
        if quarter > 1:
            # Переходим к предыдущему кварталу (4→3→2→1)
            logger.error(f"DEBUG: No words in quarter {quarter}, moving back to {quarter - 1}")
            await state.update_data(task2_quarter=quarter - 1)
            await show_words_selection(message, state, pool, user_id)
            return
        else:
            # Совсем нет слов даже в квартале 1
            str_msg = (
                f"ℹ️ <b>Недостаточно новых слов</b>\n\n"
                f"В базе нет новых слов для изучения.\n"
                f"Добавлено в этом уроке: {words_added} из {target_words}\n\n"
                f"Продолжаем обучение."
            )

            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(
                text="▶️ Продолжить",
                callback_data=f"complete_task_{user_data.get('task2_activity_id')}"
            ))

            await message.answer(str_msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
            return

    # Обновляем offset только для квартала 1
    if quarter == 1:
        await state.update_data(task2_q1_offset=new_offset)

    # Инициализируем toggle
    toggle = {str(i): "0" for i in range(1, len(words) + 1)}

    # Сохраняем в state
    await state.update_data(
        task2_words=words,
        task2_toggle=toggle
    )

    # Формируем сообщение
    str_msg = build_words_message(words, toggle, words_added, target_words, quarter)

    # Формируем клавиатуру
    builder = build_words_keyboard(len(words), toggle, quarter)

    await message.answer(str_msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, user_id, f"task2_words_shown|count:{len(words)}|quarter:{quarter}")


def build_words_message(
        words: List[tuple],
        toggle: Dict[str, str],
        words_added: int,
        target_words: int,
        quarter: int
) -> str:
    """Построить сообщение со списком слов"""

    # Заголовок в зависимости от квартала
    if quarter == 1:
        header = "📝 <b>Выберите слова для изучения</b>"
    else:
        header = f"📝 <b>Усложненный выбор (уровень {quarter}/{MAX_QUARTERS})</b>"

    str_msg = (
        f"{header}\n\n"
        f"Прогресс урока: {words_added} / {target_words} слов\n\n"
    )

    for i, word in enumerate(words, 1):
        obj_id, eng, ipa, rus, rus_alt, rank = word

        # Транскрипция
        transcr = f"[{ipa}] " if ipa else ""

        # Альтернативные переводы
        alt = f" (<i>{rus_alt}</i>)" if rus_alt else ""

        # Частотность
        freq = f" • #{rank}" if rank else ""

        # Галочка выбора
        check = "✅ " if toggle.get(str(i)) == "1" else ""

        str_msg += (
            f"{fGetEmodjiNum(i)} {check}<b>{eng}</b> {transcr}- {rus}{alt}{freq}\n\n"
        )

    str_msg += (
        f"\n<i>💡 Выберите слова, которые хотите выучить, и нажмите Submit</i>"
    )

    return str_msg


def build_words_keyboard(
        words_count: int,
        toggle: Dict[str, str],
        quarter=1
) -> InlineKeyboardBuilder:
    """Построить клавиатуру для выбора слов"""

    builder = InlineKeyboardBuilder()

    # Кнопки с номерами слов
    for i in range(1, words_count + 1):
        label = f"{fGetEmodjiNum(i)}"
        if toggle.get(str(i)) == "1":
            label += " ✅"

        builder.add(InlineKeyboardButton(
            text=label,
            callback_data=f"task2_toggle:{i}"
        ))

    # Кнопка Submit
    builder.add(InlineKeyboardButton(
        text="✅ Submit",
        callback_data="task2_submit"
    ))

    # Расположение кнопок: 3 в ряд + Submit внизу
    rows = [3] * (words_count // 3)
    if words_count % 3 != 0:
        rows.append(words_count % 3)
    rows.append(1)  # Submit отдельно

    if quarter == MAX_QUARTERS:
        builder.add(InlineKeyboardButton(
            text="⏭️ Пропустить",
            callback_data="task2_skip"
        ))
        rows.append(1)

    builder.adjust(*rows)

    return builder


# ============================================================================
# ВЫБОРКА СЛОВ ПО КВАРТАЛАМ
# ============================================================================

async def get_available_words_count(pool_base, user_id: int) -> int:
    """
    Получить количество НЕизученных слов пользователем
    Это Y в формуле расчета кварталов (размер таблицы ranked_words)
    """
    query = f"""
        SELECT COUNT(*)
        FROM tw_obj o
        LEFT JOIN tw_userprogress up 
            ON o.obj_id = up.obj_id 
            AND up.user_id = {user_id}
        WHERE o.theme_id = 3
            AND up.obj_id IS NULL
            AND o.c_rank IS NOT NULL
    """

    result = await pgDB.fExec_SelectQuery(pool_base, query)
    return result[0][0] if result else 0


async def fetch_words_quarter1(
        pool_base,
        user_id: int,
        limit: int,
        left_bound: int,
        right_bound: int,
        offset: int
) -> Tuple[List[tuple], int]:
    """
        Квартал 1: Выбрать первые N слов по c_rank DESC (без рандомизации)

        Args:
            left_bound: начало диапазона квартала (по индексу в ranked_words)
            right_bound: конец диапазона квартала (по индексу в ranked_words)
            offset: текущий offset внутри квартала 1

        Returns:
            (words, new_offset)
    """
    # Проверяем, не вышли ли мы за границы квартала 1
    current_position = left_bound + offset
    if current_position > right_bound:
        return [], offset

    # Вычисляем сколько слов можем взять, не выходя за границу квартала
    remaining_in_quarter = right_bound - current_position + 1
    actual_limit = min(limit, remaining_in_quarter)

    query = f"""
        WITH ranked_words AS (
            SELECT 
                o.obj_id,
                o.obj_eng,
                o.obj_ipa,
                o.obj_rus,
                o.obj_rus_alt,
                o.c_rank,
                ROW_NUMBER() OVER (ORDER BY o.c_rank DESC) as rn
            FROM tw_obj o
            LEFT JOIN tw_userprogress up 
                ON o.obj_id = up.obj_id 
                AND up.user_id = {user_id}
            WHERE o.theme_id = 3
                AND up.obj_id IS NULL
                AND o.c_rank IS NOT NULL
        )
        SELECT obj_id, obj_eng, obj_ipa, obj_rus, obj_rus_alt, c_rank
        FROM ranked_words
        WHERE rn BETWEEN {current_position} AND {current_position + actual_limit - 1}
        ORDER BY rn
        LIMIT {actual_limit}
    """

    result = await pgDB.fExec_SelectQuery(pool_base, query)
    words = result if result else []
    new_offset = offset + len(words)

    return words, new_offset


async def fetch_words_from_quarter(
        pool_base,
        user_id: int,
        limit: int,
        left_bound: int,
        right_bound: int
) -> List[tuple]:
    """
        Кварталы 2-4: Выбрать рандомные слова из фиксированного диапазона
        Границы квартала фиксированы на весь урок!

        Args:
            left_bound: начало диапазона квартала (по индексу)
            right_bound: конец диапазона квартала (по индексу)

        Returns:
            words
    """
    # Диапазон должен быть валидным
    if left_bound > right_bound:
        return []

    # SQL запрос с LEFT JOIN и ROW_NUMBER для выборки из диапазона
    query = f"""
        WITH ranked_words AS (
            SELECT 
                o.obj_id,
                o.obj_eng,
                o.obj_ipa,
                o.obj_rus,
                o.obj_rus_alt,
                o.c_rank,
                ROW_NUMBER() OVER (ORDER BY o.c_rank DESC) as rn
            FROM tw_obj o
            LEFT JOIN tw_userprogress up 
                ON o.obj_id = up.obj_id 
                AND up.user_id = {user_id}
            WHERE o.theme_id = 3
                AND up.obj_id IS NULL
                AND o.c_rank IS NOT NULL
        )
        SELECT obj_id, obj_eng, obj_ipa, obj_rus, obj_rus_alt, c_rank
        FROM ranked_words
        WHERE rn BETWEEN {left_bound + 1} AND {right_bound}
        ORDER BY RANDOM()
        LIMIT {limit}
    """
    logger.info(f'left_bound:{left_bound}|right_bound:{right_bound}|limit:{limit}')
    result = await pgDB.fExec_SelectQuery(pool_base, query)
    return result if result else []


# ============================================================================
# HANDLERS
# ============================================================================

async def handle_task2_toggle(
        callback: types.CallbackQuery,
        state: FSMContext,
        pool
):
    """Обработка переключения выбора слова"""

    # Получаем индекс слова
    word_index = callback.data.split(':')[1]

    # Получаем данные из state
    user_data = await state.get_data()
    toggle = user_data.get('task2_toggle', {})
    words = user_data.get('task2_words', [])
    quarter = user_data.get('task2_quarter', 1)

    # Переключаем значение
    toggle[word_index] = "1" if toggle.get(word_index) == "0" else "0"

    # Сохраняем
    await state.update_data(task2_toggle=toggle)

    # Обновляем клавиатуру
    builder = build_words_keyboard(len(words), toggle, quarter)

    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    await callback.answer("Выбор обновлен")


async def handle_task2_submit(
        callback: types.CallbackQuery,
        state: FSMContext,
        pool
):
    """Обработка Submit - сохранение выбранных слов"""
    pool_base, pool_log = pool
    user_id = callback.message.chat.id

    # Получаем данные
    user_data = await state.get_data()
    words = user_data.get('task2_words', [])
    toggle = user_data.get('task2_toggle', {})
    quarter = user_data.get('task2_quarter', 1)
    words_added = user_data.get('task2_words_added_in_lesson', 0)

    # Разделяем слова на выбранные и невыбранные
    selected_words = []
    rejected_words = []

    for i, word in enumerate(words, 1):
        obj_id = word[0]
        if toggle.get(str(i)) == "1":
            selected_words.append(obj_id)
        else:
            rejected_words.append(obj_id)

    # Добавляем выбранные слова (status_id=2, is_lp=True)
    if selected_words:
        await add_words_to_learning(pool_base, user_id, selected_words)

    # Добавляем отклоненные слова (status_id=9, is_lp=True)
    if rejected_words:
        await add_words_to_known(pool_base, user_id, rejected_words)

    # Обновляем счетчик слов, добавленных в этом уроке
    new_words_added = words_added + len(selected_words)
    await state.update_data(task2_words_added_in_lesson=new_words_added)

    # Логируем
    await pgDB.fExec_LogQuery(
        pool_log,
        user_id,
        f"task2_submit|selected:{len(selected_words)}|rejected:{len(rejected_words)}|quarter:{quarter}|total_added:{new_words_added}"
    )

    # Проверяем - нужно ли усложнить выбор?
    if len(selected_words) <= 1 and quarter < MAX_QUARTERS:
        # Усложняем!
        new_quarter = quarter + 1
        await state.update_data(task2_quarter=new_quarter)

        # Показываем всплывающее окно с уведомлением об усложнении
        alert_msg = (
            f"💪 Отлично, давай немного усложним выбор\n\n"
            f"Предложу слова, которые встречаются реже.\n"
            f"Уровень сложности: {new_quarter}/{MAX_QUARTERS}"
        )
        await callback.answer(alert_msg, show_alert=True)
        await callback.message.delete()

        # Показываем следующую порцию (более сложных слов)
        await show_words_selection(callback.message, state, pool, user_id)

    else:
        # Выбрано достаточно слов или достигнут максимальный квартал
        await callback.answer(f"✅ Добавлено {len(selected_words)} слов", show_alert=False)
        await callback.message.delete()

        # Показываем следующую порцию слов или завершаем
        await show_words_selection(callback.message, state, pool, user_id)


async def add_words_to_learning(
        pool_base,
        user_id: int,
        word_ids: List[int]
) -> None:
    """Добавить слова к изучению (status_id=2, is_lp=True)"""

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
        word_ids: List[int]
) -> None:
    """Добавить слова в известные (status_id=9, is_lp=True)"""

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


async def handle_task2_skip(
        callback: types.CallbackQuery,
        state: FSMContext,
        pool
):
    """Обработка кнопки Пропустить - завершение задания без достижения цели"""
    pool_base, pool_log = pool
    user_id = callback.message.chat.id

    # Получаем данные
    user_data = await state.get_data()
    quarter = user_data.get('task2_quarter', 1)

    # Пропустить можно только в 4-м квартале
    if quarter != MAX_QUARTERS:
        await callback.answer("⚠️ Пропустить можно только на максимальном уровне сложности")
        return

    # Логируем
    await pgDB.fExec_LogQuery(
        pool_log,
        user_id,
        f"task2_skip|quarter:{quarter}"
    )

    # Уведомление
    await callback.answer("⏭️ Задание пропущено", show_alert=False)
    await callback.message.delete()

    # Завершаем задание
    await finish_task2_skipped(callback.message, state, pool, user_id)


async def finish_task2_skipped(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int
) -> None:
    """Завершить Task 2 через пропуск"""
    pool_base, pool_log = pool

    user_data = await state.get_data()
    activity_id = user_data.get('task2_activity_id')
    lesson_id = user_data.get('task2_lesson_id')
    target_words = user_data.get('task2_target_words', TARGET_WORDS_COUNT)
    words_added = user_data.get('task2_words_added_in_lesson', 0)

    str_msg = (
        f"⏭️ <b>Задание пропущено</b>\n\n"
        f"Вы добавили {words_added} из {target_words} слов в этом уроке.\n\n"
        f"Переходим к следующему заданию."
    )

    await message.answer(str_msg, parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, user_id, f"finish_task2_skipped|words:{words_added}")

    # Завершаем задание

    await complete_activity(message, state, pool, user_id, lesson_id, activity_id)


async def finish_task2(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int
) -> None:
    """Завершить Task 2"""
    pool_base, pool_log = pool

    user_data = await state.get_data()
    activity_id = user_data.get('task2_activity_id')
    lesson_id = user_data.get('task2_lesson_id')
    target_words = user_data.get('task2_target_words', TARGET_WORDS_COUNT)
    words_added = user_data.get('task2_words_added_in_lesson', 0)

    str_msg = (
        f"✅ <b>Слова добавлены!</b>\n\n"
        f"Вы добавили {words_added} слов для изучения в этом уроке.\n"
        f"Цель: {target_words} слов\n\n"
        f"Отличная работа! Переходим к следующему заданию."
    )

    await message.answer(str_msg, parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, user_id, f"finish_task2|words:{words_added}")

    # Завершаем задание

    await complete_activity(message, state, pool, user_id, lesson_id, activity_id)


# ============================================================================
# CALLBACK HANDLERS
# ============================================================================

@router.callback_query(F.data.startswith("task2_toggle:"))
async def task2_toggle_callback(callback: types.CallbackQuery, state: FSMContext, pool):
    """Обработка переключения выбора слова"""
    await handle_task2_toggle(callback, state, pool)


@router.callback_query(F.data == "task2_submit")
async def task2_submit_callback(callback: types.CallbackQuery, state: FSMContext, pool):
    """Обработка Submit - сохранение выбранных слов"""
    await handle_task2_submit(callback, state, pool)


@router.callback_query(F.data == "task2_skip")
async def task2_skip_callback(callback: types.CallbackQuery, state: FSMContext, pool):
    """Handler для кнопки Пропустить"""
    await handle_task2_skip(callback, state, pool)


def ______________________task3():
    pass
# ============================================================================
# TASK 3: QUESTIONS (Вопросы на понимание)
# ============================================================================


# ============================================================================
# ОСНОВНЫЕ ФУНКЦИИ TASK 3
# ============================================================================

async def launch_task3_questions(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int,
        activity: Dict[str, Any]
) -> None:
    """
    Запускает задание Task 3 с AI-генерацией вопросов

    Args:
        message: Сообщение пользователя
        state: FSM состояние
        pool: Tuple (pool_base, pool_log)
        user_id: ID пользователя
        lesson_id: ID урока
        activity: Данные активности из БД
    """
    logger.info(f"Activity data: {activity}")

    pool_base, pool_log = pool
    bot = message.bot

    # Получаем template_id
    template_id = activity.get('template_id')
    task3_config = activity.get('config')

    if not template_id:
        await myErr.err_sender(bot, pool_log, user_id, 'Ошибка: не задан template_id для вопросов')
        return

    # Загружаем шаблоны из БД
    templates = await load_question_templates(pool_base, template_id)

    if not templates:
        await myErr.err_sender(bot, pool_log, user_id, '❌ Ошибка: не удалось загрузить шаблоны вопросов')
        '''
        await message.answer(
            "❌ Ошибка: не удалось загрузить шаблоны вопросов",
            parse_mode=ParseMode.HTML
        )
        '''
        return

    # Определяем количество вопросов
    questions_count = activity.get('questions_count', len(templates))
    questions_count = min(questions_count, len(templates))

    # Получаем контекст урока для более качественной генерации
    lesson_context = await get_lesson_context(pool_base, lesson_id)

    # Инициализируем state
    await state.update_data(
        task3_template_id=template_id,
        task3_templates=templates,
        task3_generated_questions={},  # Словарь для кеширования
        task3_current_idx=0,
        task3_answers=[],
        task3_activity_id=activity['activity_id'],
        task3_total_count=questions_count,
        task3_lesson_context=lesson_context,
        task3_config=task3_config
    )

    # Приветственное сообщение
    str_msg = (
        f"❓ <b>Закрепление материала</b>\n\n"
        f"Ответьте на {questions_count} вопросов по пройденному материалу.\n"
        #f"Вопросы будут персонализированы на основе ваших интересов."
    )

    await message.answer(str_msg, parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, user_id, f"start_task3|template:{template_id}|count:{questions_count}")

    # Показываем первый вопрос
    await send_task3_question(message, state, pool)


async def get_lesson_context(pool_base, lesson_id: int) -> Optional[str]:
    """
    Получает контекст урока для улучшения AI генерации

    Args:
        pool_base: Connection pool БД
        lesson_id: ID урока

    Returns:
        Строка с контекстом урока или None
    """

    query = """
        SELECT 
            m.c_module_name, 
            l.c_lesson_name, 
            t3.c_qlvl_name 
        FROM t_lp_lesson l 
        JOIN t_lp_module m ON l.c_module_id = m.c_module_id 
        JOIN ts_qlvl t3 ON m.c_qlvl_id = t3.c_qlvl_id 
        WHERE l.c_lesson_id = $1
    """

    try:
        result = await pgDB.fExec_SelectQuery_args(pool_base, query, lesson_id)

        if result:
            module_name = result[0][0]
            lesson_name = result[0][1]
            englevel = result[0][2]
            return f"{module_name} - {lesson_name} - English level is {englevel}"

        return None

    except Exception as e:
        logger.error(f"Error getting lesson context: {e}")
        return None


async def send_task3_question(
        message: types.Message,
        state: FSMContext,
        pool
) -> None:
    """
    Отправляет вопрос пользователю (генерирует через AI если нужно)

    Args:
        message: Сообщение пользователя
        state: FSM состояние
        pool: Tuple (pool_base, pool_log)
    """

    pool_base, pool_log = pool
    user_id = message.chat.id
    bot = message.bot

    user_data = await state.get_data()
    current_idx = user_data.get('task3_current_idx', 0)
    total_count = user_data.get('task3_total_count', 0)

    # Проверяем завершение теста
    if current_idx >= total_count:
        await finish_task3(message, state, pool)
        return

    # Получаем или генерируем вопрос
    test_service = TestService(pool_base)

    question = await get_or_generate_question(
        state=state,
        question_idx=current_idx,
        pool_base=pool_base,
        user_id=user_id,
        test_service=test_service
    )

    if not question:
        await myErr.err_sender(bot, pool_log, user_id, '❌ Ошибка при генерации вопроса. Пропускаем...')
        '''
        await message.answer(
            "❌ Ошибка при генерации вопроса. Пропускаем...",
            parse_mode=ParseMode.HTML
        )
        '''
        # Пропускаем вопрос
        await state.update_data(task3_current_idx=current_idx + 1)
        await send_task3_question(message, state, pool)
        return

    # Формируем сообщение
    topic_badge = ""
    if question.get('topic_name') and question['topic_name'] != 'General':
        topic_badge = f"📚 <i>{question['topic_name']}</i>\n"

    ai_badge = ""
    if question.get('is_ai_generated'):
        ai_badge = "🤖 "

    str_msg = (
        f"{ai_badge}❓ <b>Вопрос {current_idx + 1} / {total_count}</b>\n"
        f"{topic_badge}\n"
        f"{question['question']}\n\n"
        f"A. {question['options']['A']}\n"
        f"B. {question['options']['B']}\n"
        f"C. {question['options']['C']}\n"
        f"D. {question['options']['D']}\n"
    )

    # Формируем клавиатуру с вариантами ответов
    builder = InlineKeyboardBuilder()

    for key in ['A', 'B', 'C', 'D']:
        if key in question['options']:
            builder.add(InlineKeyboardButton(
                text=f"{key}",  #. {question['options'][key]}
                callback_data=f"task3_answer_{key}"
            ))

    builder.adjust(2,2)

    await message.answer(
        str_msg,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await pgDB.fExec_LogQuery(
        pool_log,
        user_id,
        f"show_question|idx:{current_idx}|topic:{question.get('topic_name', 'General')}"
    )


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

async def load_question_templates(
        pool_base,
        template_id
) -> Optional[List[Dict[str, Any]]]:
    """Загрузить шаблоны вопросов из БД"""

    # Нормализуем template_id
    if isinstance(template_id, (list, tuple)):
        if len(template_id) == 0:
            logger.error("template_id is empty list/tuple")
            return None
        template_id = template_id[0]

    template_id = int(template_id)
    logger.info(f"Loading templates for template_id: {template_id}")

    query = """
        SELECT c_template_data
        FROM t_lp_lesson_activity_template
        WHERE c_template_id = $1
    """

    try:
        result = await pgDB.fExec_SelectQuery_args(pool_base, query, template_id)

        if not result:
            logger.error(f"Template {template_id} not found in database")
            return None

        template_data = result[0][0]

        # ✅ ДОБАВЬТЕ ПАРСИНГ JSON:
        logger.info(f"Template data type: {type(template_data)}")

        # Если это строка - парсим JSON
        if isinstance(template_data, str):
            logger.info("Parsing JSON string to dict")
            template_data = json.loads(template_data)

        # Теперь template_data - это dict
        logger.info(f"Template data keys: {template_data.keys() if isinstance(template_data, dict) else 'not a dict'}")

        if not template_data or 'questions' not in template_data:
            logger.error(f"Invalid template_data structure for template {template_id}")
            logger.error(f"Template data: {template_data}")
            return None

        questions = template_data['questions']

        if not isinstance(questions, list) or len(questions) == 0:
            logger.error(f"Empty questions list in template {template_id}")
            return None

        logger.info(f"Successfully loaded {len(questions)} questions from template {template_id}")
        return questions

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        logger.error(f"Raw data: {result[0][0]}")
        return None

    except Exception as e:
        logger.error(f"Error loading templates: {e}", exc_info=True)
        return None


def build_ai_prompt(
        template: Dict[str, Any],
        topic: Dict[str, Any],
        lesson_context: Optional[str] = None,
        task3_config: Optional[str] = None
) -> str:
    """
    Формирует промпт для AI генерации вопроса

    Args:
        template: Шаблон вопроса из БД
        topic: Информация о топике пользователя
        lesson_context: Опциональный контекст урока (название модуля/урока)

    Returns:
        Промпт для AI API
    """

    # Формируем контекст урока если есть

    context_section = ""
    if lesson_context:
        description = lesson_context['description']
        lesson_theme = lesson_context['lesson_name']
        grammar_focus = task3_config['grammar_focus']

        aux_str = ''
        if grammar_focus:
            aux_str = f'        16. {grammar_focus}'
        logger.info(f'....................aux_str:{aux_str}')

        context_section = f"\nLESSON CONTEXT: {lesson_theme}\n{description}\n"

        prompt = f"""You are an English grammar test generator for ESL learners.
        
        TASK: You are given with: 
            - a question template, 
            - examples of four answer options for the template (including correct answer), 
            - example of a correct answer for the template, 
            - example of an explanation for the template, 
            - and a topic. 
        Your tasks are:
            - to provide a topic-aligned question by slightly changing the question template to personalize it for the topic - preferably by changing words only
            - Next, based on given examples you should provide four answer options for the question - 3 wrong and 1 correct
            - Next, for developed question and answer options and based on given example generate explanation of the correct answer to the question
        
        GIVEN INFO:
        Question: {template['question']}
        Options: {json.dumps(template['options'], ensure_ascii=False, indent=2)}
        Correct Answer: {template['correct_answer']}
        Explanation: {template['explanation']}
        Topic: {topic['topic_name']}

        REQUIREMENTS:
        1. ⚠️ IMPORTANT: The question MUST align with the lesson context: {lesson_theme}-{description}
        2. Keep the SAME question structure and grammatical focus as the template
        3. Use vocabulary and examples related to "{topic['topic_name']}". However, if 
            the template is general with limited personalization potential (for example: 
            "Что такое артикль в английском языке?"), don't personalize it
        4. Personalization should sound natural for educational purposes and avoid awkwardness.
            DO NOT add topic to the question. Bad example - "Выберите правильное предложение о чрезвычайных ситуациях за границей:" for topic "Emergencies abroad"
            Good example - "Выберите правильное предложение:"
        5. All examples in the question MUST be in English. Russian is used to ease question understanding    
        6. Ensure all options are grammatically correct and realistic
        7. Make the question at the same difficulty level as the template
        8. Provide 4 options labeled A, B, C, D
        9. The correct answer should be randomly placed among options A, B, C, D (not always option A)
        10. Write the explanation in Russian (like the template)
        11. ⚠️ IMPORTANT: Keep the explanation CONCISE (max 150 characters)
        12. The explanation should be clear and educational
        13. Focus on WHY the answer is correct, not on repeating the question
        14. If options contain references to other options (e.g., "Both A and B"), ensure these references 
            remain accurate after randomization. The explanation must also reference the correct answer letter.
        15. ⚠️ CRITICAL: Verify that the question, all options, correct answer, and explanation are 
            grammatically correct and follow British English conventions. Zero tolerance for errors. 
        {aux_str}
        
        ⚠️ VALIDATION STEP (MANDATORY):
        Before finalizing your answer, verify:
        - Read the correct answer option out loud - does it sound natural in British English?
        - Check: Would a native speaker say this exact phrase?
        - Verify the explanation is factually accurate
        - If testing articles (a/an): Remember a/an depends on SOUND, not spelling
          Example: "a CV" (sounds like "see-vee"), "an hour" (sounds like "our")
        - Double-check all grammar rules in your explanation are correct

        IMPORTANT:
        - Do NOT change the grammatical concept being tested
        - Do NOT make the options too obvious or too difficult
        - Use natural, real-world examples related to "{topic['topic_name']}"
        - Ensure the correct answer is definitively correct
        - Ensure wrong answers are plausible but clearly incorrect
        - ⚠️ If you're uncertain about any grammar rule, choose a different example
        
        GENERATION PROCESS:
        1. First, create the question and options
        2. Then, verify the correct answer by saying it out loud mentally
        3. Write the explanation based on verified facts
        4. Review everything one final time
        5. Only then output the JSON
        
        OUTPUT FORMAT (strict JSON, no additional text):
        {{
            "question": "Your generated question text in Russian",
            "options": {{
                "A": "First option",
                "B": "Second option",
                "C": "Third option",
                "D": "Fourth option"
            }},
            "correct_answer": "A",
            "explanation": "Clear explanation in Russian why this answer is correct and others are wrong"
        }}

        Generate the question now:"""

    return prompt


async def generate_ai_question(
        template: Dict[str, Any],
        topic: Dict[str, Any],
        pool_base,
        user_id: int,
        lesson_context: Optional[str] = None,
        task3_config: Optional[str] = None
) -> Dict[str, Any]:
    """
    Генерирует вопрос через AI с fallback на оригинальный шаблон

    Args:
        template: Шаблон вопроса
        topic: Информация о топике
        pool_base: Connection pool БД
        user_id: ID пользователя
        lesson_context: Опциональный контекст урока

    Returns:
        Сгенерированный вопрос (или оригинальный шаблон при ошибке)
    """

    try:
        # Формируем промпт
        prompt = build_ai_prompt(template, topic, lesson_context, task3_config)

        # Отправляем запрос к AI
        logger.info(f"Generating AI question for user {user_id}, topic: {topic['topic_name']}")
        ai_response = await myF.afSendMsg2AI(prompt, pool_base, user_id)

        if not ai_response:
            raise ValueError("Empty AI response")

        # Пытаемся извлечь JSON из ответа (на случай если AI добавил текст)
        ai_response = ai_response.strip()

        # Ищем JSON в ответе
        if '```json' in ai_response:
            # Извлекаем JSON из markdown блока
            start = ai_response.find('```json') + 7
            end = ai_response.find('```', start)
            ai_response = ai_response[start:end].strip()
        elif '```' in ai_response:
            # Извлекаем из обычного code block
            start = ai_response.find('```') + 3
            end = ai_response.rfind('```')
            ai_response = ai_response[start:end].strip()

        # Парсим JSON
        generated = json.loads(ai_response)

        # Валидация структуры
        required_fields = ['question', 'options', 'correct_answer', 'explanation']
        if not all(field in generated for field in required_fields):
            raise ValueError(
                f"Invalid AI response structure. Missing fields: {[f for f in required_fields if f not in generated]}")

        # Проверяем options
        if not isinstance(generated['options'], dict):
            raise ValueError("Options must be a dictionary")

        required_options = {'A', 'B', 'C', 'D'}
        if set(generated['options'].keys()) != required_options:
            raise ValueError(f"Options must contain exactly A, B, C, D. Got: {set(generated['options'].keys())}")

        # Проверяем correct_answer
        if generated['correct_answer'] not in required_options:
            raise ValueError(f"Correct answer must be A, B, C, or D. Got: {generated['correct_answer']}")

        # ✅ ДОБАВЛЯЕМ РАНДОМИЗАЦИЮ ОПЦИЙ
        #generated = shuffle_question_options(generated)
        logger.info(f"Question shuffled. New correct answer: {generated['correct_answer']}")

        # Добавляем метаданные
        generated['topic_name'] = topic['topic_name']
        generated['topic_id'] = topic['topic_id']
        generated['is_ai_generated'] = True

        logger.info(f"Successfully generated AI question for topic: {topic['topic_name']}")
        return generated

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}. Response: {ai_response[:200]}")
        return create_fallback_question(template, topic)

    except Exception as e:
        logger.error(f"AI generation failed: {e}")
        return create_fallback_question(template, topic)


def create_fallback_question(
        template: Dict[str, Any],
        topic: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Создает fallback вопрос на основе оригинального шаблона

    Args:
        template: Оригинальный шаблон
        topic: Информация о топике

    Returns:
        Вопрос с добавленными метаданными
    """
    logger.warning(f"Using fallback question for topic: {topic['topic_name']}")

    fallback = {
        **template,
        'topic_name': topic.get('topic_name', 'General'),
        'topic_id': topic.get('topic_id'),
        'is_ai_generated': False
    }
    # ✅ РАНДОМИЗИРУЕМ И FALLBACK ВОПРОСЫ
    return shuffle_question_options(fallback)


async def get_or_generate_question(
        state: FSMContext,
        question_idx: int,
        pool_base,
        user_id: int,
        test_service
) -> Optional[Dict[str, Any]]:
    """
    Получает вопрос из кеша или генерирует новый через AI

    Args:
        state: FSM состояние
        question_idx: Индекс текущего вопроса
        pool_base: Connection pool БД
        user_id: ID пользователя
        test_service: Сервис для работы с топиками

    Returns:
        Вопрос для отображения или None при ошибке
    """

    user_data = await state.get_data()

    # Проверяем кеш
    generated_questions = user_data.get('task3_generated_questions', {})

    if str(question_idx) in generated_questions:
        logger.info(f"Using cached question {question_idx}")
        return generated_questions[str(question_idx)]

    # Получаем шаблон
    templates = user_data.get('task3_templates', [])

    if question_idx >= len(templates):
        logger.error(f"Question index {question_idx} out of range (max: {len(templates) - 1})")
        return None

    template = templates[question_idx]

    # Получаем топик
    topic = await test_service.get_weighted_random_topic(user_id)

    if not topic:
        logger.warning(f"No topics found for user {user_id}, using general topic")
        topic = {
            'topic_id': None,
            'topic_name': 'General'
        }

    # Получаем контекст урока (опционально)
    lesson_context = user_data.get('task3_lesson_context')
    task3_config = user_data.get('task3_config')


    #logger.info(f'>>>>>>>>>>template:{template}')
    #logger.info(f'>>>>>>>>>>topic:{topic}')
    #logger.info(f'>>>>>>>>>>lesson_context:{lesson_context}')

    # Генерируем вопрос
    generated_question = await generate_ai_question(
        template=template,
        topic=topic,
        pool_base=pool_base,
        user_id=user_id,
        lesson_context=lesson_context,
        task3_config=task3_config
    )
    #logger.info(f'>>>>>>>>>>generated_question:{generated_question}')
    # Сохраняем в кеш
    generated_questions[str(question_idx)] = generated_question
    await state.update_data(task3_generated_questions=generated_questions)

    return generated_question


def shuffle_question_options(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Перемешивает варианты ответов в вопросе

    Args:
        question: Вопрос с options и correct_answer

    Returns:
        Вопрос с перемешанными опциями
    """

    # Получаем текущие опции
    options = question.get('options', {})
    correct_answer = question.get('correct_answer')

    if not options or not correct_answer:
        return question

    # Создаем список (ключ, значение)
    options_list = [(key, value) for key, value in options.items()]

    # Перемешиваем значения (сами тексты ответов)
    values = [value for key, value in options_list]
    random.shuffle(values)

    # Создаем новый словарь с перемешанными значениями
    new_options = {}
    new_correct_answer = None

    keys = ['A', 'B', 'C', 'D']

    for i, key in enumerate(keys):
        new_options[key] = values[i]

        # Находим где теперь правильный ответ
        if values[i] == options[correct_answer]:
            new_correct_answer = key

    # Обновляем вопрос
    shuffled_question = {
        **question,
        'options': new_options,
        'correct_answer': new_correct_answer
    }

    return shuffled_question

# ============================================================================
# CALLBACK HANDLERS
# ============================================================================

@router.callback_query(F.data.startswith("task3_answer_"))
async def process_task3_answer(
        callback: types.CallbackQuery,
        state: FSMContext,
        pool
) -> None:
    """Обработка ответа пользователя на вопрос"""

    pool_base, pool_log = pool
    user_id = callback.message.chat.id
    bot = callback.bot

    answer = callback.data.split("_")[-1]
    user_data = await state.get_data()

    current_idx = user_data.get('task3_current_idx', 0)
    answers = user_data.get('task3_answers', [])
    generated_questions = user_data.get('task3_generated_questions', {})

    question = generated_questions.get(str(current_idx))

    if not question:
        await myErr.err_sender(bot, pool_log, user_id, '❌ Ошибка: вопрос не найден')
        #await callback.answer("❌ Ошибка: вопрос не найден", show_alert=True)
        return

    correct_answer = question['correct_answer']
    is_correct = (answer == correct_answer)

    # Сохраняем ответ
    answers.append({
        'question_idx': current_idx,
        'answer': answer,
        'correct': is_correct,
        'topic_name': question.get('topic_name', 'General'),
        'is_ai_generated': question.get('is_ai_generated', False)
    })

    await state.update_data(
        task3_current_idx=current_idx + 1,
        task3_answers=answers
    )

    # ✅ УЛУЧШЕННАЯ ОБРАТНАЯ СВЯЗЬ
    if is_correct:
        # Просто короткое уведомление
        await callback.answer(f"✅ Правильно!", show_alert=False)

    else:
        # Короткое уведомление
        await callback.answer(f"❌ Неверно. Правильный ответ: {correct_answer}", show_alert=True)

    # Полное объяснение в отдельном сообщении
    explanation = question.get('explanation', 'Объяснение отсутствует')

    explanation_message = (
        f"💡 <b>Объяснение</b>\n\n"
        f"{explanation}"
    )

    await callback.message.answer(
        explanation_message,
        parse_mode=ParseMode.HTML
    )

    # Логирование
    await pgDB.fExec_LogQuery(
        pool_log,
        user_id,
        f"task3_answer|q:{current_idx}|ans:{answer}|correct:{is_correct}"
    )

    # Следующий вопрос
    await send_task3_question(callback.message, state, pool)


async def finish_task3(
        message: types.Message,
        state: FSMContext,
        pool
) -> None:
    """
    Завершение задания Task 3 и показ результатов

    Args:
        message: Сообщение пользователя
        state: FSM состояние
        pool: Tuple (pool_base, pool_log)
    """

    pool_base, pool_log = pool
    user_id = message.chat.id

    user_data = await state.get_data()
    answers = user_data.get('task3_answers', [])
    activity_id = user_data.get('task3_activity_id')
    lesson_id = user_data.get('current_lesson_id')

    # ✅ ИСПРАВЛЕНИЕ: Получаем generated_questions из state
    generated_questions = user_data.get('task3_generated_questions', {})

    # Подсчет статистики
    total_count = len(answers)
    correct_count = sum(1 for ans in answers if ans.get('correct'))
    score_percent = (correct_count / total_count * 100) if total_count > 0 else 0

    # Статистика по AI-генерированным вопросам
    ai_questions = [ans for ans in answers if ans.get('is_ai_generated')]
    ai_correct = sum(1 for ans in ai_questions if ans.get('correct'))

    # Формируем сообщение с результатами
    str_msg = (
        f"📊 <b>Результаты теста</b>\n\n"
        f"Правильных ответов: <b>{correct_count}</b> из {total_count}\n"
        f"Результат: <b>{int(score_percent)}%</b>\n\n"
    )

    # Добавляем статистику по AI вопросам
    if ai_questions:
        ai_percent = (ai_correct / len(ai_questions) * 100) if ai_questions else 0
        str_msg += (
            f"🤖 Вопросы: {ai_correct}/{len(ai_questions)} "
            f"({int(ai_percent)}%)\n\n"
        )

    # Оценка результата
    builder = InlineKeyboardBuilder()
    is_kb = False
    if score_percent >= 90:
        str_msg += "🌟 Превосходный результат! Вы отлично усвоили материал."
    elif score_percent >= 70:
        str_msg += "✅ Хорошая работа! Переходим к следующему заданию."
    elif score_percent >= 50:
        str_msg += "⚠️ Неплохо, но рекомендуем повторить некоторые темы."
    else:
        is_kb = True
        str_msg += "📚 Рекомендуем повторить материал урока."
        builder.add(InlineKeyboardButton(
            text="🔄 Пройти урок заново",
            callback_data=f"restart_lesson_{lesson_id}"
        ))


    await message.answer(str_msg, reply_markup=builder.as_markup() if is_kb else None, parse_mode=ParseMode.HTML)

    # Логирование результатов
    await pgDB.fExec_LogQuery(
        pool_log,
        user_id,
        f"finish_task3|score:{score_percent:.1f}|correct:{correct_count}/{total_count}|ai:{ai_correct}/{len(ai_questions) if ai_questions else 0}"
    )

    # Сохраняем результаты в БД (если требуется)
    await save_task3_results(
        pool_base=pool_base,
        user_id=user_id,
        lesson_id=lesson_id,
        activity_id=activity_id,
        answers=answers,
        score_percent=score_percent
    )

    # ✅ ИСПРАВЛЕНИЕ: Проверяем, что generated_questions существует
    if generated_questions:
        # Подсчитываем распределение правильных ответов
        correct_answers_distribution = {}
        for ans in answers:
            question = generated_questions.get(str(ans['question_idx']))
            if question:
                correct_ans = question.get('correct_answer')
                if correct_ans:
                    correct_answers_distribution[correct_ans] = correct_answers_distribution.get(correct_ans, 0) + 1

        logger.info(f"Correct answers distribution for user {user_id}: {correct_answers_distribution}")
        # Output: Correct answers distribution: {'A': 2, 'B': 1, 'C': 2, 'D': 1}
    else:
        logger.warning(f"No generated_questions found in state for user {user_id}")

    # Завершаем активность и переходим к следующей

    await complete_activity(message, state, pool, user_id, lesson_id, activity_id)

@router.callback_query(F.data.startswith("restart_lesson_"))
async def callback_restart_lesson(callback, state, pool):
    lesson_id = int(callback.data.split("_")[2])
    await state.clear()
    await restart_lesson_from_beginning(callback.message, state, pool, user_id, lesson_id)

async def save_task3_results(
        pool_base,
        user_id: int,
        lesson_id: int,
        activity_id: int,
        answers: List[Dict[str, Any]],
        score_percent: float
) -> None:
    """
    Сохраняет результаты теста в БД для аналитики

    Args:
        pool_base: Connection pool БД
        user_id: ID пользователя
        lesson_id: ID урока
        activity_id: ID активности
        answers: Список ответов пользователя
        score_percent: Процент правильных ответов
    """

    try:
        # Подготавливаем данные для сохранения
        results_json = json.dumps({
            'answers': answers,
            'score_percent': score_percent,
            'total_questions': len(answers),
            'correct_answers': sum(1 for ans in answers if ans.get('correct'))
        }, ensure_ascii=False)

        # Сохраняем в таблицу результатов (замените на актуальную таблицу)
        query = """
            INSERT INTO t_lp_activity_results 
            (c_user_id, c_lesson_id, c_activity_id, c_results_data, c_score_percent, c_completed_at)
            VALUES ($1, $2, $3, $4::jsonb, $5, NOW())
            ON CONFLICT (c_user_id, c_activity_id) 
            DO UPDATE SET
                c_results_data = EXCLUDED.c_results_data,
                c_score_percent = EXCLUDED.c_score_percent,
                c_completed_at = NOW()
        """

        await pgDB.fExec_Query_args(
            pool_base,
            query,
            [user_id, lesson_id, activity_id, results_json, score_percent]
        )

        logger.info(f"Saved Task 3 results for user {user_id}, activity {activity_id}")

    except Exception as e:
        logger.error(f"Error saving Task 3 results: {e}")
        # Не прерываем выполнение, просто логируем ошибку


def ______________________task4_task5():
    pass



# ============================================================================
# UNIFIED LISTEN TASKS (Task 4 & Task 5)
# Объединенная система для заданий на прослушивание
# РЕФАКТОРИНГ: Каждое субзадание выбирает свой топик независимо
# ============================================================================


class ListenTaskType(Enum):
    """Типы заданий на прослушивание"""
    LISTEN_SPEAK = "task_4_listen_speak"  # Task 4: Голос или текст
    LISTEN_WRITE = "task_5_listen_write"  # Task 5: Только текст


@dataclass
class ListenTaskConfig:
    """Конфигурация задания на прослушивание"""

    task_type: ListenTaskType
    state: str  # FSM state name

    # UI тексты
    title_emoji: str
    title_text: str
    instruction: str
    caption: str

    # Функциональность
    allow_voice: bool
    calculate_accuracy: bool

    # Callback префиксы
    skip_callback: str
    finish_callback: str
    next_audio_callback: str

    # State ключи
    state_prefix: str  # task4_ или task5_


# Конфигурации для каждого типа задания
LISTEN_TASK_CONFIGS = {
    ListenTaskType.LISTEN_SPEAK: ListenTaskConfig(
        task_type=ListenTaskType.LISTEN_SPEAK,
        state='task4_listen_speak',
        title_emoji='🎧',
        title_text='Послушайте и повторите',
        instruction='Воспроизведите наиболее близко к оригиналу (запишите голосом или введите текстом)',
        caption='🎧 Прослушайте и повторите (голосом или текстом)',
        allow_voice=True,
        calculate_accuracy=False,
        skip_callback='task4_skip',
        finish_callback='task4_finish',
        next_audio_callback='task4_next',
        state_prefix='task4_'
    ),

    ListenTaskType.LISTEN_WRITE: ListenTaskConfig(
        task_type=ListenTaskType.LISTEN_WRITE,
        state='task5_listen_write',
        title_emoji='✍️',
        title_text='Послушайте и напишите',
        instruction='Прослушайте предложение и напишите его текстом',
        caption=(
            "🎧 <b>Прослушайте и напишите</b>\n\n"
            "1️⃣ Прослушайте аудио\n"
            "2️⃣ Напишите предложение текстом\n\n"
            "<i>Введите то, что услышали</i>"
        ),
        allow_voice=False,
        calculate_accuracy=True,
        skip_callback='task5_skip',
        finish_callback='task5_finish',
        next_audio_callback='task5_next',
        state_prefix='task5_'
    )
}


# ============================================================================
# CORE: UNIFIED LAUNCH FUNCTION (РЕФАКТОРИНГ)
# ============================================================================

async def launch_listen_task(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int,
        activity: Dict[str, Any],
        task_type: ListenTaskType
) -> None:
    """
    Универсальная функция запуска заданий на прослушивание

    ИЗМЕНЕНИЯ:
    - Убран выбор топика отсюда
    - Топик будет выбираться для КАЖДОГО субзадания отдельно
    - Сохраняем только общие параметры задания
    """

    pool_base, pool_log = pool
    config = LISTEN_TASK_CONFIGS[task_type]

    # Устанавливаем состояние
    await state.set_state(getattr(myState, config.state))

    # Получаем номер урока
    lesson_num = await get_lesson_number(pool_base, lesson_id)

    # Получаем c_config и c_template_id из activity
    activity_config = activity.get('config', {})
    logger.info(f'>>>>>>>>>>>>>activity_config:{activity_config}')
    template_id = activity.get('template_id')

    sentences_count = activity_config.get('sentences_count', 3)

    # Загружаем example_texts если есть template
    example_texts = []
    if template_id:
        example_texts = await load_example_texts_from_template(pool_base, template_id)
        logger.info(f">>> Loaded {len(example_texts)} example texts from template {template_id}")

    # Сохраняем в state ТОЛЬКО общие параметры
    # Топик и sentences будут определяться для каждого субзадания отдельно
    state_data = {
        f'{config.state_prefix}example_texts': example_texts,
        f'{config.state_prefix}activity_id': activity['activity_id'],
        f'{config.state_prefix}lesson_id': lesson_id,
        f'{config.state_prefix}lesson_num': lesson_num,
        f'{config.state_prefix}task_type': task_type.value,
        f'{config.state_prefix}current_index': 0,
        f'{config.state_prefix}total_count': sentences_count,
        f'{config.state_prefix}activity_config': activity_config,
        f'{config.state_prefix}template_id': template_id
    }

    await state.update_data(**state_data)

    # Отправляем приветственное сообщение
    str_msg = (
        f"{config.title_emoji} <b>{config.title_text}</b>\n"
        f"📝 Количество заданий: <b>{sentences_count}</b>\n\n"
        f"{config.instruction}\n\n"
        f"<i>Каждое задание будет по случайной теме из ваших интересов</i>"
    )

    await message.answer(str_msg, parse_mode=ParseMode.HTML)

    # Отправляем первое аудио (топик выберется внутри функции)
    await send_listen_task_audio(message, state, pool, config, lesson_id)


# ============================================================================
# CORE: UNIFIED AUDIO SENDING WITH AI GENERATION (РЕФАКТОРИНГ)
# ============================================================================

async def send_listen_task_audio(
        message: types.Message,
        state: FSMContext,
        pool,
        config: ListenTaskConfig,
        lesson_id: int
) -> None:
    """
    Универсальная отправка аудио файла с генерацией через AI если нужно

    ИЗМЕНЕНИЯ:
    - Топик выбирается ЗДЕСЬ для КАЖДОГО субзадания
    - Используем test_service.get_weighted_random_topic(user_id)
    - Загружаем sentences из БД для выбранного топика
    - Если нет файлов - создаём заглушку для AI
    """

    pool_base, pool_log = pool
    user_id = message.chat.id
    bot = message.bot

    await myErr.err_sender(bot, pool_log, user_id, 'test')

    user_data = await state.get_data()

    current_index = user_data.get(f'{config.state_prefix}current_index', 0)
    total_count = user_data.get(f'{config.state_prefix}total_count', 0)
    lesson_num = user_data.get(f'{config.state_prefix}lesson_num', 1)
    example_texts = user_data.get(f'{config.state_prefix}example_texts', [])

    # ✅ НОВОЕ: Выбираем топик для ЭТОГО субзадания
    test_service = TestService(pool_base)
    topic = await test_service.get_weighted_random_topic(user_id)

    if not topic:
        await myErr.err_sender(bot, pool_log, user_id, '❌ Не удалось загрузить темы интересов')
        return

    topic_id = topic['topic_id']
    topic_name = topic['topic_name']

    logger.info(f">>> Selected topic for subtask {current_index + 1}: {topic_name} (id={topic_id})")

    # ✅ НОВОЕ: Загружаем sentences из БД для выбранного топика
    content_generator = ContentGenerator(pool)

    sentences = await load_sentences_from_db(
        topic_id=topic_id,
        lesson_num=lesson_num,
        user_id=user_id,
        content_generator=content_generator,
        pool_base=pool_base
    )

    # Если файлы не найдены - пробуем сбросить прогресс
    if not sentences:
        logger.warning(f"⚠️ Аудио файлы не найдены для topic={topic_id}, lesson={lesson_num}")

        await reset_listen_tasks_progress(
            user_id=user_id,
            topic_id=topic_id,
            lesson_num=lesson_num,
            pool_base=pool_base
        )

        sentences = await load_sentences_from_db(
            topic_id=topic_id,
            lesson_num=lesson_num,
            user_id=user_id,
            content_generator=content_generator,
            pool_base=pool_base
        )

    # Если файлы ВСЁ ЕЩЁ не найдены - создаем заглушку для AI
    sentence = None

    if sentences:
        # Берём первое доступное предложение
        sentence = sentences[0]
        logger.info(f">>> Using existing audio: {sentence['filename']}")
    else:
        # Создаём заглушку для AI-генерации
        logger.info(f">>> Создаём заглушку для AI-генерации")

        sentence = {
            'filename': f'ai_placeholder_{current_index}.ogg',
            'text': '',  # Будет заполнено AI
            'audio_path': '',  # Будет создан AI
            'sentence_hash': hashlib.md5(
                f"ai_gen_{user_id}_{lesson_id}_{current_index}_{topic_id}".encode()).hexdigest(),
            'topic_id': topic_id,
            'lesson_num': lesson_num,
            'module_code': f'gram{lesson_num}',
            'is_ai_placeholder': True
        }

    # Проверяем существование файла или флаг AI-заглушки
    audio_path = sentence.get('audio_path', '')
    is_ai_placeholder = sentence.get('is_ai_placeholder', False)

    # Для тестирования можно принудительно включить AI генерацию
    # is_ai_placeholder = True

    if is_ai_placeholder or not os.path.exists(audio_path):
        if is_ai_placeholder:
            logger.info(f">>> AI placeholder detected. Generating audio...")
        else:
            logger.info(f">>> Audio file not found: {audio_path}. Generating with AI...")

        # Генерируем аудио через AI
        generated_sentence = await generate_audio_with_ai(
            message=message,
            state=state,
            pool=pool,
            user_id=user_id,
            lesson_id=lesson_id,
            sentence=sentence,
            config=config,
            topic_name=topic_name,  # Передаём имя топика
            example_texts=example_texts,
            current_index=current_index
        )

        if not generated_sentence:
            logger.error(f"❌ AI generation failed for index {current_index}")
            await handle_generation_failure(message, state, pool, config)
            return

        sentence = generated_sentence
        audio_path = sentence['audio_path']
        logger.info(f"✅ AI audio generated successfully: {audio_path}")

    # Повторная проверка существования файла
    if not os.path.exists(audio_path):
        logger.error(f"❌ Audio file still doesn't exist after generation: {audio_path}")
        await handle_generation_failure(message, state, pool, config)
        return

    # Кнопки
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="⏩ Пропустить",
        callback_data=config.skip_callback
    ))

    # Показываем прогресс и текущий топик
    progress_text = f"Задание {current_index + 1} из {total_count}"
    caption = f"{config.caption}\n\n📚 <b>Тема:</b> {topic_name}\n<i>{progress_text}</i>"

    # Отправляем аудио
    try:
        with open(audio_path, 'rb') as audio_file:
            msg = await message.answer_audio(
                BufferedInputFile(audio_file.read(), filename=sentence['filename']),
                caption=caption,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )

        # Сохраняем текущее предложение, топик и ID сообщения
        await state.update_data(**{
            f'{config.state_prefix}current_sentence': sentence,
            f'{config.state_prefix}current_topic_id': topic_id,
            f'{config.state_prefix}current_topic_name': topic_name,
            f'{config.state_prefix}audio_msg_id': msg.message_id
        })

        logger.info(f">>> Audio sent successfully: {sentence['filename']}, topic: {topic_name}")

    except Exception as e:
        logger.error(f"❌ Error sending audio: {e}", exc_info=True)
        await myErr.err_sender(bot, pool_log, user_id,
                               f'❌ Ошибка при отправке аудио файла. Переходим к следующему заданию | ❌ Error sending audio: {e}')

        # Пропускаем это задание
        await handle_listen_task_skip(
            message=message,
            state=state,
            pool=pool,
            task_type=config.task_type,
            is_error_skip=True
        )


# ============================================================================
# AI AUDIO GENERATION (РЕФАКТОРИНГ)
# ============================================================================

async def generate_audio_with_ai(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int,
        sentence: Dict[str, Any],
        config: ListenTaskConfig,
        topic_name: str,  # ✅ НОВЫЙ параметр
        example_texts: List[Dict[str, str]],  # ✅ НОВЫЙ параметр
        current_index: int  # ✅ НОВЫЙ параметр
) -> Optional[Dict[str, Any]]:
    """
    Генерирует аудио через AI если файл не найден

    ИЗМЕНЕНИЯ:
    - Принимает topic_name напрямую
    - Принимает example_texts напрямую
    - Не читает из state
    """
    pool_base, pool_log = pool

    try:
        user_data = await state.get_data()
        activity_config = user_data.get(f'{config.state_prefix}activity_config', {})

        # Получаем lesson_context
        lesson_context = await get_lesson_context(pool_base, lesson_id)

        # Берём пример текста для этого индекса (если есть)
        example_text = None
        if example_texts and current_index < len(example_texts):
            example_text = example_texts[current_index]

        # Формируем промпт для AI
        prompt = build_listen_task_ai_prompt(
            example_text=example_text,
            topic_name=topic_name,
            lesson_context=lesson_context,
            ai_params=activity_config.get('ai_params', {})
        )

        logger.info(f"Generating AI audio text for user {user_id}, topic: {topic_name}")
        logger.info(f"prompt: {prompt}")

        # Генерируем текст через AI
        ai_response = await myF.afSendMsg2AI(prompt, pool_base, user_id)

        if not ai_response:
            logger.error("AI returned empty response")
            return None

        # Парсим ответ AI
        audio_text_data = parse_ai_audio_response(ai_response)

        if not audio_text_data:
            logger.error(f"Failed to parse AI response: {ai_response}")
            return None

        audio_text_en = audio_text_data['en']
        audio_text_ru = audio_text_data.get('ru', '')

        # Генерируем аудио файл
        isPremium, sub_stat = await myF.getSubscription(state, user_id, pool)
        arrVoiceParams = myF.fGenerateVoiceParams(isPremium)

        nm_ogg = await myF.afTxtToOGG(audio_text_en, arrVoiceParams)

        if not nm_ogg or not os.path.exists(nm_ogg):
            logger.error("Failed to generate OGG file")
            return None

        # Определяем путь для сохранения
        lesson_num = sentence.get('lesson_num', 1)
        topic_id = sentence.get('topic_id')
        module_code = sentence.get('module_code', 'gram30')

        python_folder = os.path.dirname(sys.executable)
        storage_dir = os.path.join(python_folder, 'storage', 'lp', module_code)
        os.makedirs(storage_dir, exist_ok=True)

        # Генерируем имя файла
        filename = f"{module_code}_less{lesson_num}_topic{topic_id}_ai_{current_index + 1}.ogg"
        final_audio_path = os.path.join(storage_dir, filename)

        # Перемещаем файл

        shutil.move(nm_ogg, final_audio_path)

        # Сохраняем в БД
        await save_generated_audio_to_db(
            pool_base=pool_base,
            filename=filename,
            text_en=audio_text_en,
            text_ru=audio_text_ru,
            topic_id=topic_id,
            lesson_num=lesson_num,
            module_code=module_code
        )

        # Обновляем sentence
        sentence_hash = hashlib.md5(f"{filename}_{audio_text_en}".encode('utf-8')).hexdigest()

        updated_sentence = {
            'filename': filename,
            'text': audio_text_en,
            'audio_path': final_audio_path,
            'sentence_hash': sentence_hash,
            'topic_id': topic_id,
            'lesson_num': lesson_num,
            'module_code': module_code,
            'text_ru': audio_text_ru
        }

        logger.info(f"✅ AI audio generated successfully: {filename}")
        return updated_sentence

    except Exception as e:
        logger.error(f"Error generating AI audio: {e}", exc_info=True)
        await pgDB.fExec_LogQuery(pool_log, user_id, f"ai_audio_generation_error|{str(e)}")
        return None


def build_listen_task_ai_prompt(
        example_text: Optional[Dict[str, str]],
        topic_name: str,
        lesson_context: Optional[str],
        ai_params: Dict[str, Any]
) -> str:
    """
    Формирует промпт для AI генерации текста аудирования
    """

    # Параметры по умолчанию
    sentence_length = ai_params.get('sentence_length', '5-7 words')
    complexity = ai_params.get('complexity', 'CEFR A1')
    grammar_focus = ai_params.get('grammar_focus', 'Present Simple')

    prompt = f"""Create a short English sentence for listening comprehension practice.

Requirements:
- Topic: {topic_name}
- Level: {complexity}
- Length: {sentence_length}
- Grammar: {grammar_focus}"""

    if lesson_context:
        prompt += f"\n- Lesson context: {lesson_context}"

    if example_text:
        prompt += f"\n- Example sentence: \"{example_text.get('en', '')}\""

    prompt += """

Return your response as JSON with two fields:
{
  "en": "Your English sentence here",
  "ru": "Russian translation here"
}

Requirements:
- Use simple, clear vocabulary
- Sentence MUST sound completely natural and idiomatic to a native English speaker (not a literal or translated version)
- Follow the grammar pattern specified
- Make it relevant to the topic
- Ensure it's easy to pronounce
- Return ONLY the JSON, no additional text"""

    return prompt


def parse_ai_audio_response(ai_response: str) -> Optional[Dict[str, str]]:
    """
    Парсит ответ AI и извлекает английский и русский текст
    """
    try:
        # Пробуем распарсить как JSON
        data = json.loads(ai_response.strip())

        if 'en' in data and data['en']:
            return {
                'en': data['en'].strip(),
                'ru': data.get('ru', '').strip()
            }
    except json.JSONDecodeError:
        logger.warning(f"AI response is not JSON: {ai_response[:100]}")

        # Простая эвристика: берём первое предложение
        lines = ai_response.strip().split('\n')
        if lines:
            first_line = lines[0].strip()
            first_line = first_line.replace('**', '').replace('*', '').strip('"\'')
            if len(first_line.split()) >= 3:
                return {
                    'en': first_line,
                    'ru': ''
                }

    return None


async def save_generated_audio_to_db(
        pool_base,
        filename: str,
        text_en: str,
        text_ru: str,
        topic_id: int,
        lesson_num: int,
        module_code: str
) -> None:
    """Сохраняет сгенерированное аудио в БД"""

    text_trs_json = json.dumps({'ru': text_ru}) if text_ru else None

    query = """
        INSERT INTO t_lp_audio_files 
            (c_filename, c_text, c_topic_id, c_lesson_num, c_question_type, c_variant, c_module_code, c_text_trs)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (c_filename) DO NOTHING
    """

    await pgDB.fExec_UpdateQuery_args(
        pool_base,
        query,
        filename,
        text_en,
        topic_id,
        lesson_num,
        'ai_generated',
        1,
        module_code,
        text_trs_json
    )

    logger.info(f"Saved AI generated audio to DB: {filename}")


async def handle_generation_failure(
        message: types.Message,
        state: FSMContext,
        pool,
        config: ListenTaskConfig
) -> None:
    """Обработка ошибки генерации - показываем fallback"""

    pool_base, pool_log = pool
    user_id = message.chat.id

    user_data = await state.get_data()
    lesson_id = user_data.get(f'{config.state_prefix}lesson_id')
    activity_id = user_data.get(f'{config.state_prefix}activity_id')

    # Логируем ошибку
    await pgDB.fExec_LogQuery(pool_log, user_id, f"{config.task_type.value}|ai_generation_failed")

    # Показываем сообщение пользователю
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="➡️ Продолжить",
        callback_data=config.finish_callback
    ))

    str_msg = (
        "⚠️ <b>Что-то пошло не так</b>\n\n"
        "Не удалось подготовить аудио для этого задания.\n"
        "Переходим к следующему заданию."
    )

    await message.answer(str_msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


# ============================================================================
# CORE: UNIFIED ANSWER PROCESSING
# ============================================================================

async def process_listen_task_answer(
        message: types.Message,
        state: FSMContext,
        pool,
        task_type: ListenTaskType
) -> None:
    """
    Универсальная обработка ответа пользователя
    """


    pool_base, pool_log = pool
    user_id = message.chat.id
    config = LISTEN_TASK_CONFIGS[task_type]

    user_data = await state.get_data()

    # Проверяем что это наш handler
    sentence_key = f'{config.state_prefix}current_sentence'
    if sentence_key not in user_data:
        return

    sentence = user_data.get(sentence_key)
    original_text = sentence['text']

    # Получаем ответ пользователя
    user_answer = ''

    if message.voice and config.allow_voice:
        user_answer = await myF.afVoiceToTxt(message, pool, user_id)
    elif message.text:
        user_answer = ' '.join(message.text.split())
    else:
        await message.answer("❌ Неподдерживаемый тип ввода для этого задания")
        return

    if not user_answer:
        await message.answer("❌ Не удалось распознать ответ. Попробуйте еще раз.")
        return

    # Очищаем ответ
    user_answer = myF.fRemoveLastBadSymbol(user_answer)

    # Сравниваем с оригиналом
    str1, str2, strBool = myF.fGetCompare(original_text, user_answer)
    is_correct = (strBool == '✅')

    # Вычисляем точность если нужно (только для Task 5)
    accuracy = 0.0
    if config.calculate_accuracy and is_correct:
        accuracy = calculate_accuracy(original_text, user_answer)

    # Формируем сообщение с результатом
    str_msg = (
        f"{strBool}\n\n"
        f"<b>Оригинал:</b>\n{str1}\n\n"
        f"<b>Ваш ответ:</b>\n{str2}"
    )

    # Сохраняем прогресс
    await save_listen_task_progress(
        user_id=user_id,
        sentence=sentence,
        is_correct=is_correct,
        user_answer=user_answer,
        accuracy=accuracy,
        pool_base=pool_base,
        activity_type=task_type.value,
        is_completed=True
    )

    # Проверяем, есть ли ещё задания
    current_index = user_data.get(f'{config.state_prefix}current_index', 0)
    total_count = user_data.get(f'{config.state_prefix}total_count', 0)

    # Увеличиваем счётчик
    next_index = current_index + 1
    await state.update_data(**{f'{config.state_prefix}current_index': next_index})

    # Определяем кнопку
    builder = InlineKeyboardBuilder()

    if next_index < total_count:
        builder.add(InlineKeyboardButton(
            text=f"{myN.fCSS('>>')}",
            callback_data=config.next_audio_callback
        ))
    else:
        builder.add(InlineKeyboardButton(
            text=f"{myN.fCSS('fw')}",
            callback_data=config.finish_callback
        ))

    await message.answer(str_msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

    # Логируем
    log_msg = f"{task_type.value}_answer|correct:{is_correct}|progress:{next_index}/{total_count}"
    if config.calculate_accuracy:
        log_msg += f"|accuracy:{accuracy}"

    await pgDB.fExec_LogQuery(pool_log, user_id, log_msg)


# ============================================================================
# CALLBACKS: Next Audio Handlers
# ============================================================================

async def handle_next_audio(
        callback: types.CallbackQuery,
        state: FSMContext,
        pool,
        task_type: ListenTaskType
) -> None:
    """Обработка перехода к следующему аудио"""

    pool_base, pool_log = pool
    user_id = callback.message.chat.id
    config = LISTEN_TASK_CONFIGS[task_type]

    user_data = await state.get_data()
    lesson_id = user_data.get(f'{config.state_prefix}lesson_id')

    await callback.answer("➡️ Следующее задание")

    # Отправляем следующее аудио (топик выберется автоматически)
    await send_listen_task_audio(callback.message, state, pool, config, lesson_id)

    await pgDB.fExec_LogQuery(pool_log, user_id, f"{task_type.value}_next_audio")


@router.callback_query(F.data == "task4_next")
async def callback_task4_next(callback: types.CallbackQuery, state: FSMContext, pool):
    """Callback: Следующее аудио Task 4"""
    await handle_next_audio(callback, state, pool, ListenTaskType.LISTEN_SPEAK)


@router.callback_query(F.data == "task5_next")
async def callback_task5_next(callback: types.CallbackQuery, state: FSMContext, pool):
    """Callback: Следующее аудио Task 5"""
    await handle_next_audio(callback, state, pool, ListenTaskType.LISTEN_WRITE)


# ============================================================================
# PUBLIC API: Task 4 Entry Points
# ============================================================================

async def launch_task4_listen_speak(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int,
        activity: Dict[str, Any]
) -> None:
    """Запустить задание Task 4: Listen & Speak"""
    await launch_listen_task(
        message, state, pool, user_id, lesson_id, activity,
        ListenTaskType.LISTEN_SPEAK
    )


@router.message(
    (F.voice | (F.text & ~F.text.startswith('/'))),
    StateFilter(myState.task4_listen_speak)
)
async def process_task4_answer(message: types.Message, state: FSMContext, pool):
    """Обработка ответа Task 4 (голос или текст)"""
    await process_listen_task_answer(message, state, pool, ListenTaskType.LISTEN_SPEAK)


# ============================================================================
# PUBLIC API: Task 5 Entry Points
# ============================================================================

async def launch_task5_listen_write(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int,
        activity: Dict[str, Any]
) -> None:
    """Запустить задание Task 5: Listen & Write"""
    await launch_listen_task(
        message, state, pool, user_id, lesson_id, activity,
        ListenTaskType.LISTEN_WRITE
    )


@router.message(
    (F.text & ~F.text.startswith('/')),
    StateFilter(myState.task5_listen_write)
)
async def process_task5_answer(message: types.Message, state: FSMContext, pool):
    """Обработка ответа Task 5 (только текст)"""
    await process_listen_task_answer(message, state, pool, ListenTaskType.LISTEN_WRITE)


# ============================================================================
# CALLBACKS: Skip Handlers
# ============================================================================

async def handle_listen_task_skip(
        callback: types.CallbackQuery,
        state: FSMContext,
        pool,
        task_type: ListenTaskType,
        is_error_skip: bool = False
) -> None:
    """Универсальная обработка пропуска"""

    pool_base, pool_log = pool
    user_id = callback.message.chat.id
    config = LISTEN_TASK_CONFIGS[task_type]

    user_data = await state.get_data()
    sentence = user_data.get(f'{config.state_prefix}current_sentence')

    # Сохраняем как пропущенное
    await save_listen_task_progress(
        user_id=user_id,
        sentence=sentence,
        is_correct=None,
        user_answer=None,
        accuracy=0,
        pool_base=pool_base,
        activity_type=task_type.value,
        is_completed=False
    )

    if not is_error_skip:
        await callback.answer("⏩ Пропущено")

    # Проверяем, есть ли ещё задания
    current_index = user_data.get(f'{config.state_prefix}current_index', 0)
    total_count = user_data.get(f'{config.state_prefix}total_count', 0)

    next_index = current_index + 1
    await state.update_data(**{f'{config.state_prefix}current_index': next_index})

    if next_index < total_count:
        # Есть ещё задания - показываем следующее (топик выберется автоматически)
        lesson_id = user_data.get(f'{config.state_prefix}lesson_id')
        await send_listen_task_audio(callback.message, state, pool, config, lesson_id)
    else:
        # Это было последнее - завершаем
        await finish_listen_task(callback.message, state, pool, task_type)

    await pgDB.fExec_LogQuery(pool_log, user_id, f"{task_type.value}_skip|{next_index}/{total_count}")


@router.callback_query(F.data == "task4_skip")
async def callback_task4_skip(callback: types.CallbackQuery, state: FSMContext, pool):
    """Callback: Пропустить Task 4"""
    await handle_listen_task_skip(callback, state, pool, ListenTaskType.LISTEN_SPEAK)


@router.callback_query(F.data == "task5_skip")
async def callback_task5_skip(callback: types.CallbackQuery, state: FSMContext, pool):
    """Callback: Пропустить Task 5"""
    await handle_listen_task_skip(callback, state, pool, ListenTaskType.LISTEN_WRITE)


# ============================================================================
# CALLBACKS: Finish Handlers
# ============================================================================

async def handle_listen_task_finish(
        callback: types.CallbackQuery,
        state: FSMContext,
        pool,
        task_type: ListenTaskType
) -> None:
    """Универсальная обработка завершения"""
    await finish_listen_task(callback.message, state, pool, task_type)


@router.callback_query(F.data == "task4_finish")
async def callback_task4_finish(callback: types.CallbackQuery, state: FSMContext, pool):
    """Callback: Завершить Task 4"""
    await handle_listen_task_finish(callback, state, pool, ListenTaskType.LISTEN_SPEAK)


@router.callback_query(F.data == "task5_finish")
async def callback_task5_finish(callback: types.CallbackQuery, state: FSMContext, pool):
    """Callback: Завершить Task 5"""
    await handle_listen_task_finish(callback, state, pool, ListenTaskType.LISTEN_WRITE)


# ============================================================================
# CORE: UNIFIED FINISH FUNCTION
# ============================================================================

async def finish_listen_task(
        message: types.Message,
        state: FSMContext,
        pool,
        task_type: ListenTaskType
) -> None:
    """Универсальное завершение задания"""

    pool_base, pool_log = pool
    user_id = message.chat.id
    config = LISTEN_TASK_CONFIGS[task_type]

    user_data = await state.get_data()
    activity_id = user_data.get(f'{config.state_prefix}activity_id')
    lesson_id = user_data.get(f'{config.state_prefix}lesson_id')

    str_msg = "✅ Задание выполнено! Переходим к следующему."

    await message.answer(str_msg, parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, user_id, f"finish_{task_type.value}")

    # Очищаем state
    clear_data = {
        f'{config.state_prefix}example_texts': None,
        f'{config.state_prefix}current_sentence': None,
        f'{config.state_prefix}current_topic_id': None,
        f'{config.state_prefix}current_topic_name': None,
        f'{config.state_prefix}activity_id': None,
        f'{config.state_prefix}lesson_id': None,
        f'{config.state_prefix}lesson_num': None,
        f'{config.state_prefix}audio_msg_id': None,
        f'{config.state_prefix}task_type': None,
        f'{config.state_prefix}current_index': None,
        f'{config.state_prefix}total_count': None,
        f'{config.state_prefix}activity_config': None,
        f'{config.state_prefix}template_id': None
    }

    await state.update_data(**clear_data)

    # Завершаем активность

    await complete_activity(message, state, pool, user_id, lesson_id, activity_id)


# ============================================================================
# HELPER FUNCTIONS: Template Loading
# ============================================================================

async def load_example_texts_from_template(
        pool_base,
        template_id: int
) -> List[Dict[str, str]]:
    """
    Загрузить example_texts из template
    """

    query = """
        SELECT c_template_data
        FROM t_lp_lesson_activity_template
        WHERE c_template_id = $1
    """

    try:
        result = await pgDB.fExec_SelectQuery_args(pool_base, query, template_id)

        if not result:
            logger.warning(f"Template {template_id} not found")
            return []

        template_data = result[0][0]

        if isinstance(template_data, str):
            template_data = json.loads(template_data)

        example_texts = template_data.get('example_texts', [])

        if not isinstance(example_texts, list):
            logger.warning(f"example_texts is not a list in template {template_id}")
            return []

        logger.info(f"Loaded {len(example_texts)} example texts from template {template_id}")
        return example_texts

    except Exception as e:
        logger.error(f"Error loading example texts from template {template_id}: {e}")
        return []


async def get_lesson_context(pool_base, lesson_id: int) -> Optional[str]:
    """
    Получает контекст урока для улучшения AI генерации
    """

    query = """
        SELECT 
            m.c_module_name, 
            l.c_lesson_name, 
            t3.c_qlvl_name 
        FROM t_lp_lesson l 
        JOIN t_lp_module m ON l.c_module_id = m.c_module_id 
        JOIN ts_qlvl t3 ON m.c_qlvl_id = t3.c_qlvl_id 
        WHERE l.c_lesson_id = $1
    """

    try:
        result = await pgDB.fExec_SelectQuery_args(pool_base, query, lesson_id)

        if result:
            module_name = result[0][0]
            lesson_name = result[0][1]
            englevel = result[0][2]
            return f"{module_name} - {lesson_name} - English level is {englevel}"

        return None

    except Exception as e:
        logger.error(f"Error getting lesson context: {e}")
        return None


# ============================================================================
# HELPER FUNCTIONS: Database Operations
# ============================================================================

async def load_sentences_from_db(
        topic_id: int,
        lesson_num: int,
        user_id: int,
        content_generator,
        pool_base
) -> List[Dict[str, Any]]:
    """
    Загрузить предложения из БД
    """

    # Получаем уже прослушанные хеши
    completed_hashes = await get_completed_audio_hashes(
        user_id=user_id,
        topic_id=topic_id,
        lesson_num=lesson_num,
        pool_base=pool_base
    )

    # SQL запрос с фильтрацией
    var_query = f"""
        SELECT 
            c_filename,
            c_text,
            c_topic_id,
            c_lesson_num,
            c_question_type, 
            c_module_code
        FROM t_lp_audio_files
        WHERE c_topic_id = {topic_id}
        AND c_lesson_num = {lesson_num}
        ORDER BY RANDOM()
    """

    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    available_sentences = []
    python_folder = os.path.dirname(sys.executable)

    for row in var_Arr:
        filename = row[0]
        text = row[1]
        audFolder = row[5]

        # Создаем хеш
        sentence_hash = hashlib.md5(f"{filename}_{text}".encode('utf-8')).hexdigest()

        # Пропускаем прослушанные
        if sentence_hash not in completed_hashes:
            audio_path = os.path.join(python_folder, 'storage', 'lp', audFolder, filename)

            available_sentences.append({
                'filename': filename,
                'text': text,
                'audio_path': audio_path,
                'sentence_hash': sentence_hash,
                'topic_id': int(row[2]),
                'lesson_num': int(row[3]),
                'module_code': audFolder
            })

    return available_sentences


async def get_completed_audio_hashes(
        user_id: int,
        topic_id: int,
        lesson_num: int,
        pool_base
) -> set:
    """
    Получить хеши прослушанных аудио для обоих типов заданий
    """

    var_query = f"""
        SELECT c_content_hash
        FROM t_lp_lesson_activity_progress
        WHERE c_user_id = {user_id}
        AND c_activity_type IN ('task_4_listen_speak', 'task_5_listen_write')
        AND c_is_completed = TRUE
        AND c_content_data->>'topic_id' = '{topic_id}'
        AND c_content_data->>'lesson_num' = '{lesson_num}'
    """

    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if not var_Arr:
        return set()

    return {row[0] for row in var_Arr}


async def reset_listen_tasks_progress(
        user_id: int,
        topic_id: int,
        lesson_num: int,
        pool_base
) -> None:
    """
    Обнулить прогресс для обоих типов заданий
    """

    var_query = f"""
        DELETE FROM t_lp_lesson_activity_progress
        WHERE c_user_id = {user_id}
        AND c_activity_type IN ('task_4_listen_speak', 'task_5_listen_write')
        AND c_content_data->>'topic_id' = '{topic_id}'
        AND c_content_data->>'lesson_num' = '{lesson_num}'
    """

    await pgDB.fExec_UpdateQuery(pool_base, var_query)
    logger.info(
        f"⚠️ Обнулен прогресс listen tasks для "
        f"user={user_id}, topic={topic_id}, lesson={lesson_num}"
    )


async def save_listen_task_progress(
        user_id: int,
        sentence: Dict[str, Any],
        is_correct: Optional[bool],
        user_answer: Optional[str],
        accuracy: float,
        pool_base,
        activity_type: str,
        is_completed: bool = True
) -> None:
    """Универсальное сохранение прогресса для обоих заданий"""

    content_generator = ContentGenerator((pool_base, None))

    content_data = {
        'filename': sentence['filename'],
        'original_text': sentence['text'],
        'topic_id': sentence['topic_id'],
        'lesson_num': sentence['lesson_num']
    }

    if accuracy > 0:
        content_data['accuracy'] = accuracy

    if user_answer:
        content_data['user_answer'] = user_answer

    await content_generator.mark_content_progress(
        user_id=user_id,
        template_id=None,
        activity_type=activity_type,
        content_hash=sentence['sentence_hash'],
        content_text=sentence['text'],
        is_completed=is_completed,
        is_correct=is_correct,
        content_data=content_data
    )


async def get_lesson_number(pool_base, lesson_id: int) -> int:
    """Получить номер урока"""

    var_query = f"""
        SELECT c_lesson_number 
        FROM t_lp_lesson 
        WHERE c_lesson_id = {lesson_id}
    """

    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if var_Arr:
        return var_Arr[0][0]

    return 1


def calculate_accuracy(correct: str, user: str) -> float:
    """
    Вычислить точность ответа
    """
    correct_words = correct.lower().split()
    user_words = user.lower().split()

    if not correct_words:
        return 100.0

    correct_set = set(correct_words)
    user_set = set(user_words)
    matches = len(correct_set & user_set)

    accuracy = (matches / len(correct_set)) * 100

    return round(accuracy, 1)


def ______________________task6():
    pass
# ============================================================================
# TASK 6: Reading
# ============================================================================

# ============================================================================
# ОСНОВНЫЕ ФУНКЦИИ TASK 6
# ============================================================================

async def launch_task6_reading(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int,
        activity: Dict[str, Any]
) -> None:
    """
    Запускает задание Reading Comprehension с AI-генерацией

    Args:
        message: Сообщение пользователя
        state: FSM состояние
        pool: Tuple (pool_base, pool_log)
        user_id: ID пользователя
        lesson_id: ID урока
        activity: Данные активности из БД
    """


    pool_base, pool_log = pool
    bot = message.bot

    template_id = activity.get('template_id')
    config = activity.get('config', {})

    if not template_id:
        await myErr.err_sender(bot, pool_log, user_id,"❌ Ошибка: не задан template_id для текстов")
        '''
        await message.answer(
            "❌ Ошибка: не задан template_id для текстов",
            parse_mode=ParseMode.HTML
        )
        '''
        return

    # Инициализируем сервисы
    reading_service = Task6ReadingService(pool_base)
    content_generator = ContentGenerator(pool)
    test_service = TestService(pool_base)

    # 1. Загружаем шаблоны типов текстов
    template_data = await reading_service.load_text_templates(template_id)

    if not template_data:
        await myErr.err_sender(bot, pool_log, user_id, "❌ Ошибка: не удалось загрузить шаблоны текстов")
        '''
        await message.answer(
            "❌ Ошибка: не удалось загрузить шаблоны текстов",
            parse_mode=ParseMode.HTML
        )
        '''
        return

    # 2. Выбираем случайный тип текста
    try:
        text_type_id, text_type_data = reading_service.select_random_text_type(
            template_data
        )
    except ValueError as e:
        logger.error(f"Error selecting text type: {e}")
        await myErr.err_sender(bot, pool_log, user_id, f"❌ Ошибка: не удалось выбрать тип текста | Error selecting text type: {e}")
        '''
        await message.answer(
            "❌ Ошибка: не удалось выбрать тип текста",
            parse_mode=ParseMode.HTML
        )
        '''
        return

    # 3. Получаем топик пользователя
    topic = await test_service.get_weighted_random_topic(user_id)

    if not topic:
        logger.warning(f"No topics found for user {user_id}, using general topic")
        topic = {
            'topic_id': None,
            'topic_name': 'General',
            'priority': 1
        }

    # 4. Получаем контекст урока для AI
    lesson_context = await get_lesson_context(pool_base, lesson_id)

    # 5. Генерируем текст через AI
    text_length = template_data.get('text_length', '80-120 words')
    questions_count = template_data.get('questions_count', 4)

    reading_data = await reading_service.generate_reading_with_ai(
        text_type=text_type_data,
        topic=topic,
        lesson_context=lesson_context,
        user_id=user_id,
        text_length=text_length,
        questions_count=questions_count
    )

    if not reading_data:
        await myErr.err_sender(bot, pool_log, user_id,"❌ Ошибка при генерации текста. Попробуйте позже.")
        '''
        await message.answer(
            "❌ Ошибка при генерации текста. Попробуйте позже.",
            parse_mode=ParseMode.HTML
        )
        '''
        return

    # 6. Перемешиваем опции в вопросах
    reading_data = reading_service.shuffle_all_questions(reading_data)

    # 7. Сохраняем в state
    await state.update_data(
        task6_reading_data=reading_data,
        task6_current_question_idx=0,
        task6_correct_count=0,
        task6_activity_id=activity['activity_id'],
        task6_template_id=template_id,
        task6_selected_topic=topic['topic_name'],
        task6_text_type=text_type_data.get('name', 'Unknown')
    )

    # 8. Формируем приветственное сообщение
    type_badge = ""
    if reading_data.get('text_type'):
        type_badge = f"📝 <i>{reading_data['text_type']}</i>\n"

    topic_badge = ""
    if reading_data.get('topic_name') and reading_data['topic_name'] != 'General':
        topic_badge = f"📚 <i>{reading_data['topic_name']}</i>\n"

    ai_badge = ""
    if reading_data.get('is_ai_generated'):
        ai_badge = "🤖 "

    str_msg = (
        f"{ai_badge}📖 <b>Reading Comprehension</b>\n\n"
        f"{type_badge}"
        f"{topic_badge}\n"
        f"Прочитайте текст и ответьте на {questions_count} вопросов.\n"
        f"Проверим ваше понимание прочитанного."
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="▶️ Начать чтение",
        callback_data="task6_start"
    ))
    builder.adjust(1)

    await message.answer(
        str_msg,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    # await state.set_state(myState.task6_reading)
    await pgDB.fExec_LogQuery(
        pool_log,
        user_id,
        f"task6|intro|type:{text_type_data.get('name')}|topic:{topic['topic_name']}"
    )

    logger.info(
        f"Task 6 launched for user {user_id}: "
        f"type={text_type_data.get('name')}, topic={topic['topic_name']}, "
        f"ai_generated={reading_data.get('is_ai_generated')}"
    )


async def get_lesson_context(pool_base, lesson_id: int) -> str:
    """
    Получает контекст урока для AI генерации

    Args:
        pool_base: Connection pool БД
        lesson_id: ID урока

    Returns:
        Строка с контекстом урока
    """


    query = """
        SELECT 
            m.c_module_name, 
            l.c_lesson_name, 
            t3.c_qlvl_name, 
            m.c_module_id
        FROM t_lp_lesson l 
        JOIN t_lp_module m ON l.c_module_id = m.c_module_id 
        JOIN ts_qlvl t3 ON m.c_qlvl_id = t3.c_qlvl_id 
        WHERE l.c_lesson_id = $1
    """

    try:
        result = await pgDB.fExec_SelectQuery_args(pool_base, query, lesson_id)

        if result:
            module_name = result[0][0]
            lesson_name = result[0][1]
            eng_level = result[0][2]
            return f"{module_name} - {lesson_name} - English level is {eng_level}"

        return "General English lesson"

    except Exception as e:
        logger.error(f"Error getting lesson context: {e}")
        return "General English lesson"


# ============================================================================
# CALLBACK HANDLERS
# ============================================================================

@router.callback_query(F.data == "task6_start")
async def task6_show_text(
        callback: types.CallbackQuery,
        state: FSMContext,
        pool
) -> None:
    """Показать текст для чтения"""


    pool_base, pool_log = pool
    user_id = callback.message.chat.id

    await callback.answer("✅ Начинаем!")
    await callback.message.delete()

    user_data = await state.get_data()
    reading_data = user_data.get('task6_reading_data', {})

    title = reading_data.get('title', 'Reading Text')
    text = reading_data.get('text', '')
    word_count = reading_data.get('word_count', 0)
    questions_count = len(reading_data.get('questions', []))

    # Добавляем бейджи
    type_badge = ""
    if reading_data.get('text_type'):
        type_badge = f"📝 {reading_data['text_type']} | "

    topic_badge = ""
    if reading_data.get('topic_name') and reading_data['topic_name'] != 'General':
        topic_badge = f"📚 {reading_data['topic_name']} | "

    # Формируем сообщение с текстом
    str_msg = (
        f"📖 <b>{title}</b>\n\n"
        f"{text}\n\n"
        f"<i>{type_badge}{topic_badge}"
        f"Слов: {word_count} | Вопросов: {questions_count}</i>"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="✅ Прочитал, начинаем вопросы",
        callback_data="task6_begin_questions"
    ))
    builder.adjust(1)

    await callback.message.answer(
        str_msg,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await pgDB.fExec_LogQuery(pool_log, user_id, "task6|text_shown")


@router.callback_query(F.data == "task6_begin_questions")
async def task6_begin_questions(
        callback: types.CallbackQuery,
        state: FSMContext,
        pool
) -> None:
    """Начать вопросы"""


    pool_base, pool_log = pool
    user_id = callback.message.chat.id

    await callback.answer("✅ Начинаем вопросы!")
    await callback.message.delete()

    # Показываем первый вопрос
    await send_task6_question(callback.message, state, pool, user_id)
    await pgDB.fExec_LogQuery(pool_log, user_id, "task6|questions_started")


async def send_task6_question(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int
) -> None:
    """
    Отправить вопрос пользователю

    Args:
        message: Сообщение
        state: FSM состояние
        pool: Tuple (pool_base, pool_log)
        user_id: ID пользователя
    """


    pool_base, pool_log = pool

    user_data = await state.get_data()
    reading_data = user_data.get('task6_reading_data', {})
    questions = reading_data.get('questions', [])
    current_idx = user_data.get('task6_current_question_idx', 0)

    if current_idx >= len(questions):
        # Все вопросы пройдены
        await finish_task6(message, state, pool, user_id)
        return

    question_data = questions[current_idx]
    question_text = question_data.get('question', '')
    options = question_data.get('options', {})

    # Формируем сообщение с вопросом
    str_msg = (
        f"❓ <b>Вопрос {current_idx + 1} / {len(questions)}</b>\n\n"
        f"{question_text}"
    )

    # Формируем кнопки с вариантами ответа
    builder = InlineKeyboardBuilder()
    for option_key in ['A', 'B', 'C', 'D']:
        if option_key in options:
            # Укорачиваем длинные варианты для кнопки
            option_text = options[option_key]
            if len(option_text) > 50:
                button_text = f"{option_key}: {option_text[:47]}..."
            else:
                button_text = f"{option_key}: {option_text}"

            builder.add(InlineKeyboardButton(
                text=button_text,
                callback_data=f"task6_answer_{option_key}"
            ))

    builder.adjust(1)

    await message.answer(
        str_msg,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await pgDB.fExec_LogQuery(
        pool_log,
        user_id,
        f"task6|question_sent|idx:{current_idx}"
    )


@router.callback_query(F.data.startswith("task6_answer_"))
async def task6_check_answer(
        callback: types.CallbackQuery,
        state: FSMContext,
        pool
) -> None:
    """
    Проверить ответ на вопрос

    Args:
        callback: Callback query
        state: FSM состояние
        pool: Tuple (pool_base, pool_log)
    """


    pool_base, pool_log = pool
    user_id = callback.message.chat.id

    # Получаем выбранный ответ (A, B, C, D)
    selected_answer = callback.data.split('_')[-1]

    user_data = await state.get_data()
    reading_data = user_data.get('task6_reading_data', {})
    questions = reading_data.get('questions', [])
    current_idx = user_data.get('task6_current_question_idx', 0)
    correct_count = user_data.get('task6_correct_count', 0)

    question_data = questions[current_idx]
    correct_answer = question_data.get('correct_answer', '')
    explanation = question_data.get('explanation', '')

    # Проверяем правильность ответа
    is_correct = (selected_answer == correct_answer)

    if is_correct:
        correct_count += 1
        await state.update_data(task6_correct_count=correct_count)

    # Формируем сообщение с результатом
    if is_correct:
        result_emoji = "✅"
        result_text = "Верно!"
        await callback.answer(result_text, show_alert=False)
    else:
        result_emoji = "❌"
        result_text = f"Неверно! Правильный ответ: <b>{correct_answer}</b>"
        await callback.answer(
            f"Неверно. Правильный ответ: {correct_answer}",
            show_alert=True
        )

    str_msg = (
        f"{result_emoji} <b>{result_text}</b>\n\n"
        f"💡 <i>{explanation}</i>"
    )

    builder = InlineKeyboardBuilder()

    # Проверяем, есть ли еще вопросы
    if current_idx + 1 < len(questions):
        builder.add(InlineKeyboardButton(
            text=f"{myN.fCSS('>>')}",       #"➡️ Следующий вопрос",
            callback_data="task6_next"
        ))
        str_msg += f"\n\n<i>Готовы к следующему вопросу?</i>"
    else:
        builder.add(InlineKeyboardButton(
            text=f"{myN.fCSS('fw')}",        #"✅ Завершить"
            callback_data="task6_complete"
        ))
        str_msg += f"\n\n<b>Это был последний вопрос!</b>"

    builder.adjust(1)

    await callback.message.edit_text(
        str_msg,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await pgDB.fExec_LogQuery(
        pool_log,
        user_id,
        f"task6|answer|correct:{is_correct}|idx:{current_idx}"
    )


@router.callback_query(F.data == "task6_next")
async def task6_next_question(
        callback: types.CallbackQuery,
        state: FSMContext,
        pool
) -> None:
    """Перейти к следующему вопросу"""


    pool_base, pool_log = pool
    user_id = callback.message.chat.id

    user_data = await state.get_data()
    current_idx = user_data.get('task6_current_question_idx', 0)

    await state.update_data(task6_current_question_idx=current_idx + 1)
    await callback.answer("✅ Отлично!")
    await callback.message.delete()

    # Показываем следующий вопрос
    await send_task6_question(callback.message, state, pool, user_id)
    await pgDB.fExec_LogQuery(
        pool_log,
        user_id,
        f"task6|next|idx:{current_idx + 1}"
    )


@router.callback_query(F.data == "task6_complete")
async def task6_complete_reading(
        callback: types.CallbackQuery,
        state: FSMContext,
        pool
) -> None:
    """Завершить задание"""
    pool_base, pool_log = pool
    user_id = callback.message.chat.id

    await callback.answer("🎉 Отлично!")
    await callback.message.delete()

    await finish_task6(callback.message, state, pool, user_id)


# ============================================================================
# ЗАВЕРШЕНИЕ ЗАДАНИЯ
# ============================================================================

async def finish_task6(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int
) -> None:
    """
    Завершение Task 6 и сохранение результатов

    Args:
        message: Сообщение
        state: FSM состояние
        pool: Tuple (pool_base, pool_log)
        user_id: ID пользователя
    """



    pool_base, pool_log = pool
    content_generator = ContentGenerator(pool)

    user_data = await state.get_data()
    activity_id = user_data.get('task6_activity_id')
    lesson_id = user_data.get('current_lesson_id')
    correct_count = user_data.get('task6_correct_count', 0)
    reading_data = user_data.get('task6_reading_data', {})
    template_id = user_data.get('task6_template_id')
    total_questions = len(reading_data.get('questions', []))

    # Вычисляем процент правильных ответов
    accuracy = round(
        (correct_count / total_questions * 100), 1
    ) if total_questions > 0 else 0

    # Определяем правильность (порог 75%)
    is_correct = accuracy >= 75.0

    # Сохраняем результат в БД
    title = reading_data.get('title', '')
    text = reading_data.get('text', '')
    reading_hash = reading_data.get(
        'reading_hash',
        hashlib.md5(title.encode('utf-8')).hexdigest()
    )

    await content_generator.mark_content_progress(
        user_id=user_id,
        template_id=template_id,
        activity_type='task_6_reading',
        content_hash=reading_hash,
        content_text=title,
        is_completed=True,
        is_correct=is_correct,
        content_data={
            'title': title,
            'text': text[:200] + '...' if len(text) > 200 else text,
            'word_count': reading_data.get('word_count', 0),
            'text_type': reading_data.get('text_type', 'Unknown'),
            'topic_name': reading_data.get('topic_name', 'General'),
            'is_ai_generated': reading_data.get('is_ai_generated', False),
            'total_questions': total_questions,
            'correct_count': correct_count,
            'accuracy': accuracy
        }
    )

    # Формируем сообщение с результатами
    str_msg = (
        f"🎉 <b>Отлично!</b>\n\n"
        f"Вы завершили упражнение на чтение.\n\n"
        f"<b>Результат:</b>\n"
        f"Правильных ответов: <b>{correct_count} из {total_questions}</b>\n"
        f"Точность: <b>{accuracy}%</b>\n\n"
    )

    # Оценка результата
    if accuracy >= 90:
        str_msg += "🌟 Превосходный результат! Вы отлично понимаете прочитанное."
    elif accuracy >= 75:
        str_msg += "✅ Хорошая работа! Переходим к следующему заданию."
    elif accuracy >= 50:
        str_msg += "⚠️ Неплохо, но рекомендуем больше практики чтения."
    else:
        str_msg += "📚 Рекомендуем чаще читать тексты на английском."

    await message.answer(str_msg, parse_mode=ParseMode.HTML)

    await pgDB.fExec_LogQuery(
        pool_log,
        user_id,
        f"task6|finished|correct:{correct_count}/{total_questions}|"
        f"accuracy:{accuracy}|type:{reading_data.get('text_type')}"
    )

    logger.info(
        f"Task 6 completed for user {user_id}: "
        f"accuracy={accuracy}%, ai_generated={reading_data.get('is_ai_generated')}"
    )

    # Очищаем state от данных task6
    await clear_task6_state(state)

    # Завершаем задание и переходим к следующему

    await complete_activity(message, state, pool, user_id, lesson_id, activity_id)


async def clear_task6_state(state: FSMContext) -> None:
    """
    Очистить данные Task 6 из state

    Args:
        state: FSM состояние
    """
    await state.update_data(
        task6_reading_data=None,
        task6_current_question_idx=0,
        task6_correct_count=0,
        task6_activity_id=None,
        task6_template_id=None,
        task6_selected_topic=None,
        task6_text_type=None
    )


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================



def ______________________task7():
    pass

# ============================================================================
# TASK 7: Word repeat
# ============================================================================

async def launch_task7_word_repeat(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int,
        activity: Dict[str, Any]
) -> None:
    """Запустить задание Word Repeat (повтор слов)"""
    pool_base, pool_log = pool

    # Получаем слова для повтора: сначала is_lp=true, потом is_lp=false
    words_lp = await get_words_for_repeat(pool_base, user_id, is_lp=True)
    words_other = await get_words_for_repeat(pool_base, user_id, is_lp=False)

    # Если нет слов вообще - сразу завершаем
    if not words_lp and not words_other:
        str_msg = (
            "📚 <b>Повтор слов</b>\n\n"
            "Сейчас нет слов к повтору.\n"
            "Приходите позже!"
        )
        await message.answer(str_msg, parse_mode=ParseMode.HTML)

        await pgDB.fExec_LogQuery(pool_log, user_id, "task7|no_words")

        # Завершаем задание

        await complete_activity(message, state, pool, user_id, lesson_id, activity['activity_id'])
        return

    # Сохраняем в state
    await state.update_data(
        task7_words_lp=words_lp,
        task7_words_other=words_other,
        task7_current_idx=0,
        task7_current_phase='lp' if words_lp else 'other',  # Начинаем с lp если есть
        task7_activity_id=activity['activity_id'],
        task7_choices=[],
        task7_correct_count=0,  # Счетчик правильных ответов
        task7_lp_correct_count=0  # Счетчик правильных для фазы lp
    )

    # Формируем приветственное сообщение
    total_words = len(words_lp) + len(words_other)

    str_msg = (
        f"📚 <b>Повтор слов</b>\n\n"
        f"Всего слов к повтору: <b>{total_words}</b>\n"
    )

    if words_lp:
        str_msg += f"• Из текущего урока: <b>{len(words_lp)}</b>\n"
    if words_other:
        str_msg += f"• Из ранее изученных: <b>{len(words_other)}</b>\n"

    str_msg += (
        f"\n<i>Выберите правильный перевод для каждого слова.</i>"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="▶️ Начать", callback_data="task7_start"))
    builder.adjust(1)

    await message.answer(str_msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await state.set_state(myState.task7_word_repeat)
    await pgDB.fExec_LogQuery(pool_log, user_id, f"task7|intro|lp:{len(words_lp)}|other:{len(words_other)}")


async def get_words_for_repeat(
        pool_base,
        user_id: int,
        is_lp: bool
) -> List[tuple]:
    """
    Получить слова для повтора

    Args:
        pool_base: Пул базы данных
        user_id: ID пользователя
        is_lp: True - слова из learning path, False - остальные

    Returns:
        List[tuple]: [(user_id, obj_id, status_id, obj_eng, obj_rus, obj_ipa,
                       obj_desc1, c_exa_ruen, c_origin, c_dict), ...]
    """
    is_lp_filter = 'TRUE' if is_lp else 'FALSE'

    query = f"""
        SELECT 
            t1.user_id, 
            t1.obj_id, 
            t1.status_id, 
            t2.obj_eng, 
            t2.obj_rus, 
            t2.obj_ipa, 
            t2.obj_desc1, 
            t2.c_exa_ruen, 
            t2.c_origin, 
            t2.c_dict
        FROM tw_userprogress AS t1 
        LEFT JOIN tw_obj AS t2 ON t1.obj_id = t2.obj_id
        WHERE t1.user_id = '{user_id}' 
        AND t1.date_repeat <= CURRENT_DATE
        AND t1.status_id > 1
        AND t1.is_lp = {is_lp_filter}
        ORDER BY t1.date_repeat ASC
    """

    result = await pgDB.fExec_SelectQuery(pool_base, query)
    return result if result else []


@router.callback_query(F.data == "task7_start")
async def task7_start_repeat(callback: types.CallbackQuery, state: FSMContext, pool):
    """Начать повтор слов"""
    pool_base, pool_log = pool
    user_id = callback.message.chat.id

    await callback.answer("✅ Начинаем!")
    await callback.message.delete()

    # Показываем первое слово
    await send_task7_word(callback.message, state, pool, user_id)
    await pgDB.fExec_LogQuery(pool_log, user_id, "task7|start")


async def send_task7_word(message: types.Message, state: FSMContext, pool, user_id: int):
    """Отправить слово для повтора с вариантами ответа"""
    pool_base, pool_log = pool

    user_data = await state.get_data()
    current_phase = user_data.get('task7_current_phase', 'lp')
    current_idx = user_data.get('task7_current_idx', 0)

    # Получаем массив слов текущей фазы
    if current_phase == 'lp':
        words = user_data.get('task7_words_lp', [])
    else:
        words = user_data.get('task7_words_other', [])

    # Проверка на завершение текущей фазы
    if current_idx >= len(words):
        await finish_task7_phase(message, state, pool, user_id)
        return

    # Получаем текущее слово
    word = words[current_idx]

    # Генерируем варианты ответа
    arr_choice = await myF.fArrChoiceGen(words, current_idx, pool_base)

    # Сохраняем варианты в state
    await state.update_data(task7_choices=arr_choice)

    # Формируем сообщение
    total_words = len(words)
    phase_label = "🎯 Слова из урока" if current_phase == 'lp' else "📖 Ранее изученные"

    str_msg = (
        f"{phase_label}\n"
        f"<i>{current_idx + 1} из {total_words}</i>\n\n"
        f"❓ <b>{word[4]}</b>"  # obj_rus - русское слово
    )

    # Формируем кнопки с вариантами ответа
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=arr_choice[0], callback_data="task7_answer_0"))
    builder.add(InlineKeyboardButton(text=arr_choice[1], callback_data="task7_answer_1"))
    builder.add(InlineKeyboardButton(text=arr_choice[2], callback_data="task7_answer_2"))
    builder.add(InlineKeyboardButton(text=arr_choice[3], callback_data="task7_answer_3"))
    builder.adjust(2, 2)

    await message.answer(str_msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, user_id, f"task7|word_sent|phase:{current_phase}|idx:{current_idx}")


@router.callback_query(F.data.startswith("task7_answer_"))
async def task7_check_answer(callback: types.CallbackQuery, state: FSMContext, pool):
    """Проверить ответ пользователя"""
    pool_base, pool_log = pool
    user_id = callback.message.chat.id

    # Получаем индекс выбранного ответа
    answer_idx = int(callback.data.split('_')[-1])

    user_data = await state.get_data()
    current_phase = user_data.get('task7_current_phase', 'lp')
    current_idx = user_data.get('task7_current_idx', 0)
    arr_choice = user_data.get('task7_choices', [])
    correct_count = user_data.get('task7_correct_count', 0)
    lp_correct_count = user_data.get('task7_lp_correct_count', 0)

    # Получаем массив слов текущей фазы
    if current_phase == 'lp':
        words = user_data.get('task7_words_lp', [])
    else:
        words = user_data.get('task7_words_other', [])

    word = words[current_idx]
    correct_answer = word[3]  # obj_eng - английское слово
    user_answer = arr_choice[answer_idx]

    # Формируем карточку слова
    word_card = myF.fShapeWordCard(
        word[3],  # obj_eng
        word[4],  # obj_rus
        word[5],  # obj_ipa
        word[7],  # c_exa_ruen
        word[8],  # c_origin
        word[9]  # c_dict
    )

    str_word_card = (
        f"\n<u>Карточка слова:</u>\n"
        f"{word_card}"
    )

    # Проверяем правильность ответа
    is_correct = (correct_answer == user_answer)

    if is_correct:
        # Правильный ответ
        var_str = f"✅ Верно!\n{str_word_card}"

        # Обновляем статус в базе данных
        v_date_repeat = myF.getDateRepeatShift(word[2])  # status_id
        v_obj_id = word[1]
        v_status_id = word[2] + 1

        if v_status_id == 8:
            v_date_repeat = 'NULL'

        query = f"""
            UPDATE tw_userprogress
            SET status_id = '{v_status_id}', 
                date_last_change = CURRENT_TIMESTAMP::timestamp, 
                date_repeat = {v_date_repeat}
            WHERE obj_id = '{v_obj_id}' 
            AND user_id = '{user_id}'
        """

        await pgDB.fExec_UpdateQuery(pool_base, query)

        # Увеличиваем счетчики правильных ответов
        correct_count += 1
        if current_phase == 'lp':
            lp_correct_count += 1
            await state.update_data(task7_lp_correct_count=lp_correct_count)

        await state.update_data(task7_correct_count=correct_count)

    else:
        # Неправильный ответ - добавляем слово в конец для повтора
        var_str = f"❌ Неверно!\n{str_word_card}"
        words.append(word)

        # Обновляем массив слов в state
        if current_phase == 'lp':
            await state.update_data(task7_words_lp=words)
        else:
            await state.update_data(task7_words_other=words)

    # Формируем кнопки
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="➡️ Дальше", callback_data="task7_next"))

    # Для фазы other добавляем кнопки Skip и "Убрать из повтора"
    if current_phase == 'other':
        builder.add(InlineKeyboardButton(text="🗑 Убрать из повтора", callback_data="task7_exclude"))
        builder.add(InlineKeyboardButton(text="⏭ Skip", callback_data="task7_skip"))
        builder.adjust(1, 2)
    else:
        builder.adjust(1)

    await callback.message.edit_text(var_str, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, user_id, f"task7|answer|correct:{is_correct}|phase:{current_phase}")


@router.callback_query(F.data == "task7_next")
async def task7_next_word(callback: types.CallbackQuery, state: FSMContext, pool):
    """Перейти к следующему слову"""
    pool_base, pool_log = pool
    user_id = callback.message.chat.id

    user_data = await state.get_data()
    current_idx = user_data.get('task7_current_idx', 0)

    # Увеличиваем индекс
    await state.update_data(task7_current_idx=current_idx + 1, task7_choices=[])

    await callback.answer()
    await callback.message.delete()

    # Показываем следующее слово
    await send_task7_word(callback.message, state, pool, user_id)
    await pgDB.fExec_LogQuery(pool_log, user_id, f"task7|next|idx:{current_idx + 1}")


async def finish_task7_phase(message: types.Message, state: FSMContext, pool, user_id: int):
    """Завершить текущую фазу повтора"""
    pool_base, pool_log = pool

    user_data = await state.get_data()
    current_phase = user_data.get('task7_current_phase', 'lp')
    words_other = user_data.get('task7_words_other', [])
    lp_correct_count = user_data.get('task7_lp_correct_count', 0)
    words_lp = user_data.get('task7_words_lp', [])

    if current_phase == 'lp':
        # Завершена фаза lp - переходим к other
        if words_other:
            # Показываем статистику по фазе lp
            str_msg = (
                f"✅ <b>Слова из урока повторены!</b>\n\n"
                f"Правильных ответов: <b>{lp_correct_count} из {len(words_lp)}</b>\n\n"
                f"Теперь повторим ранее изученные слова: <b>{len(words_other)}</b>\n\n"
                f"<i>Если хотите пропустить, нажмите Skip</i>"
            )

            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="▶️ Продолжить", callback_data="task7_transition"))
            builder.add(InlineKeyboardButton(text="⏭ Skip", callback_data="task7_skip"))
            builder.adjust(1)

            await message.answer(str_msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
            await pgDB.fExec_LogQuery(pool_log, user_id, f"task7|phase_lp_complete|correct:{lp_correct_count}")
        else:
            # Нет слов other - завершаем полностью
            await finish_task7_completely(message, state, pool, user_id)
    else:
        # Завершена фаза other - завершаем полностью
        await finish_task7_completely(message, state, pool, user_id)


@router.callback_query(F.data == "task7_transition")
async def task7_transition_to_other(callback: types.CallbackQuery, state: FSMContext, pool):
    """Переход к повтору слов other (is_lp=false)"""
    pool_base, pool_log = pool
    user_id = callback.message.chat.id

    # Переключаем фазу и сбрасываем индекс
    await state.update_data(
        task7_current_phase='other',
        task7_current_idx=0,
        task7_choices=[]
    )

    await callback.answer("✅ Продолжаем!")
    await callback.message.delete()

    # Показываем первое слово из other
    await send_task7_word(callback.message, state, pool, user_id)
    await pgDB.fExec_LogQuery(pool_log, user_id, "task7|transition_to_other")


@router.callback_query(F.data == "task7_skip")
async def task7_skip_other(callback: types.CallbackQuery, state: FSMContext, pool):
    """Пропустить оставшиеся слова"""
    pool_base, pool_log = pool
    user_id = callback.message.chat.id

    await callback.answer("⏭ Пропущено")
    await callback.message.delete()

    # Завершаем задание полностью
    await finish_task7_completely(callback.message, state, pool, user_id)
    await pgDB.fExec_LogQuery(pool_log, user_id, "task7|skipped")


@router.callback_query(F.data == "task7_exclude")
async def task7_exclude_word(callback: types.CallbackQuery, state: FSMContext, pool):
    """Убрать текущее слово из повтора"""
    pool_base, pool_log = pool
    user_id = callback.message.chat.id

    user_data = await state.get_data()
    current_phase = user_data.get('task7_current_phase', 'lp')
    current_idx = user_data.get('task7_current_idx', 0)

    # Получаем массив слов текущей фазы
    if current_phase == 'lp':
        words = user_data.get('task7_words_lp', [])
    else:
        words = user_data.get('task7_words_other', [])

    word = words[current_idx]
    v_obj_id = word[1]  # obj_id

    # Обновляем статус в базе данных
    query = f"""
        UPDATE tw_userprogress
        SET status_id = '9', 
            date_last_change = NULL, 
            date_repeat = NULL
        WHERE obj_id = '{v_obj_id}' 
        AND user_id = '{user_id}'
    """

    await pgDB.fExec_UpdateQuery(pool_base, query)
    await callback.answer("🗑 Убрано из повтора")

    # Формируем кнопки
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="➡️ Дальше", callback_data="task7_next"))

    if current_phase == 'other':
        builder.add(InlineKeyboardButton(text="⏭ Skip", callback_data="task7_skip"))
        builder.adjust(1, 1)
    else:
        builder.adjust(1)

    await callback.message.edit_text(
        "🗑 Исключено из повтора",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await pgDB.fExec_LogQuery(pool_log, user_id, f"task7|excluded|obj_id:{v_obj_id}")


async def finish_task7_completely(message: types.Message, state: FSMContext, pool, user_id: int):
    """Полностью завершить Task 7"""
    pool_base, pool_log = pool

    user_data = await state.get_data()
    activity_id = user_data.get('task7_activity_id')
    lesson_id = user_data.get('current_lesson_id')
    correct_count = user_data.get('task7_correct_count', 0)
    words_lp = user_data.get('task7_words_lp', [])
    words_other = user_data.get('task7_words_other', [])
    total_words = len(words_lp) + len(words_other)

    # Получаем случайный emoji
    var_emoji = myF.getRandomEmoji('wd')

    str_msg = (
        f"{var_emoji} <b>Отлично! Все слова повторены</b>\n\n"
        f"Правильных ответов: <b>{correct_count} из {total_words}</b>\n\n"
        f"Переходим к следующему заданию."
    )

    await message.answer(str_msg, parse_mode=ParseMode.HTML)



    await pgDB.fExec_LogQuery(pool_log, user_id, f"task7|finished|correct:{correct_count}/{total_words}")

    # Очищаем state
    await state.update_data(
        task7_words_lp=None,
        task7_words_other=None,
        task7_current_idx=0,
        task7_current_phase=None,
        task7_activity_id=None,
        task7_choices=[],
        task7_correct_count=0,
        task7_lp_correct_count=0
    )

    # Завершаем задание

    await complete_activity(message, state, pool, user_id, lesson_id, activity_id)


def ______________________task8():
    pass


# ============================================================================
# TASK 8: Interactive Story
# ============================================================================
async def launch_task8_story(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int,
        activity_id: int
):
    """
    Запуск Task 8 - Interactive Story

    Логика:
    1. Проверить есть ли активная история у пользователя
    2. Если есть - предложить продолжить или начать новую
    3. Если нет - запустить опросник
    4. После 5 действий показывать кнопку Skip

    Args:
        message: Telegram message
        state: FSM state
        pool: Database pool
        user_id: User ID
        lesson_id: Current lesson ID
        activity_id: Activity ID
    """

    pool_base, pool_log = pool

    try:
        # ========================================
        # 1. Получить контекст урока (как dict!)
        # ========================================
        lesson_context = await get4story_lesson_context(pool_base, lesson_id)

        logger.info(f"Lesson context for task_8: {lesson_context}")

        # ========================================
        # 2. Проверить есть ли активная история
        # ========================================
        existing_story = await check_user_active_story(
            pool_base,
            user_id
        )

        if existing_story:
            # История найдена - предложить продолжить или начать новую
            await show_continue_or_restart_choice(
                message=message,
                state=state,
                story_id=existing_story['story_id'],
                story_name=existing_story['story_name'],
                scene_name=existing_story['scene_name']
            )

            # Сохраняем контекст в state
            await state.update_data(
                task8_lesson_id=lesson_id,
                task8_activity_id=activity_id,
                task8_lesson_context=lesson_context,
                task8_existing_story_id=existing_story['story_id']
            )

            return

        # ========================================
        # 3. Нет активной истории - начать опросник
        # ========================================

        # Сохраняем контекст в state для дальнейшего использования
        await state.update_data(
            task8_lesson_id=lesson_id,
            task8_activity_id=activity_id,
            task8_lesson_context=lesson_context,
            task8_actions_count=0  # Счетчик действий
        )

        # Запускаем опросник
        await start_story_questionnaire(
            message=message,
            state=state,
            lesson_context=lesson_context
        )

    except Exception as e:
        logger.error(f"Error in launch_task8_story: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при запуске истории.\n"
            "Попробуйте еще раз или обратитесь к администратору.",
            parse_mode="HTML"
        )


# ========================================
# Вспомогательные функции
# ========================================

async def check_user_active_story(
        pool_base,
        user_id: int
) -> Optional[Dict[str, Any]]:
    """
    Проверить есть ли у пользователя активная история

    Returns:
        Dict с данными истории или None
        {
            'story_id': int,
            'story_name': str,
            'current_scene': int,
            'actions_count': int,
            'last_interaction': datetime
        }
    """

    query = """
        SELECT 
            s.c_story_id,
            s.c_story_name,
            p.c_current_scene_id,
            p.c_actions_count,
            p.c_last_interaction_at,
            t3.c_scene_name 
        FROM t_story_user_progress p
        JOIN t_story_interactive_stories s ON p.c_story_id = s.c_story_id 
        JOIN t_story_scenes t3 ON s.c_story_id = t3.c_story_id 
        WHERE p.c_user_id = $1
          AND p.c_is_completed = false
          AND s.c_is_active = true
        ORDER BY p.c_last_interaction_at DESC
        LIMIT 1
    """

    try:
        result = await pgDB.fExec_SelectQuery_args(pool_base, query, user_id)

        if result:
            return {
                'story_id': result[0][0],
                'story_name': result[0][1],
                'current_scene': result[0][2],
                'actions_count': result[0][3],
                'last_interaction': result[0][4],
                'scene_name': result[0][5],
            }

        return None

    except Exception as e:
        logger.error(f"Error checking active story: {e}")
        return None


async def show_continue_or_restart_choice(
        message: types.Message,
        state: FSMContext,
        story_id: int,
        story_name: str,
        scene_name: str
):
    """
    Показать выбор: продолжить или начать новую историю
    """
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text=myN.fCSS('st_cont'), callback_data=f"task8_continue:{story_id}"))

    #builder.add(InlineKeyboardButton(text="🔄 Начать новую историю", callback_data="story_new"))
    builder.add(InlineKeyboardButton(text=myN.fCSS('st_reset'), callback_data=f"story_reset_yes:{story_id}"))

    builder.add(InlineKeyboardButton(text=myN.fCSS('st_list'), callback_data="story_list:unf-0"))
    builder.add(InlineKeyboardButton(text=myN.fCSS('menu'), callback_data="menu"))

    builder.adjust(1)  # По одной кнопке в ряд

    text = (
        "📚 <u>У вас есть незавершенная история!</u>\n\n"
        f"<b>{story_name}</b>\n"
        f"📖 Сцена: {scene_name}\n\n"
        "Вы можете продолжить с того места, где остановились, "
        "или начать новую историю (прогресс будет сброшен)."
    )

    await message.answer(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

    # Устанавливаем state для ожидания выбора
    await state.set_state(myState.task8_choose_continue_or_restart)


async def start_story_questionnaire(
        message: types.Message,
        state: FSMContext,
        lesson_context: Dict[str, Any]
):
    """
    Запустить опросник для генерации истории
    """
    if lesson_context:
        text = (
            "📖 <b>Создание интерактивной истории</b>\n\n"
            "Я задам вам несколько вопросов, чтобы создать историю "
            f"для практики <b>{lesson_context['grammar_focus']}</b> "
            f"на уровне <b>{lesson_context['cefr_level']}</b>.\n\n"
            "Давайте начнем! 🎯"
        )
    else:
        text = (
            "📖 <b>Создание интерактивной истории</b>\n\n"
            "Я задам вам несколько вопросов, чтобы создать историю \n\n"
            "Давайте начнем! 🎯"
        )

    await message.answer(text, parse_mode="HTML")

    # Запускаем первый вопрос опросника
    await show_questionnaire_q0(message, state)


async def update_story_module_context(
        pool_base,
        story_id: int,
        user_id: int,
        lesson_context: Dict[str, Any]
):
    """
    Обновить контекст текущего модуля в прогрессе истории

    Вызывается при каждом запуске task_8 в новом уроке
    """

    # Обновляем current_module_context в t_story_user_progress
    update_query = """
        UPDATE t_story_user_progress
        SET 
            c_current_lesson_id = $1,
            c_current_module_context = $2,
            c_last_interaction_at = NOW()
        WHERE c_user_id = $3 AND c_story_id = $4
    """

    module_context = {
        'module_id': lesson_context['module_id'],
        'module_name': lesson_context['module_name'],
        'lesson_name': lesson_context['lesson_name'],
        'cefr_level': lesson_context['cefr_level'],
        'grammar_focus': lesson_context['grammar_focus']
    }

    try:
        await pgDB.fExec_UpdateQuery_args(
            pool_base,
            update_query,
            lesson_context['lesson_id'],
            json.dumps(module_context),
            user_id,
            story_id
        )

        # Добавляем запись в историю модулей (если еще не было)
        history_query = """
            INSERT INTO t_story_module_history
                (c_story_id, c_user_id, c_lesson_id, c_module_id, 
                 c_module_name, c_cefr_level)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (c_story_id, c_lesson_id) DO NOTHING
        """

        await pgDB.fExec_UpdateQuery_args(
            pool_base,
            history_query,
            story_id,
            user_id,
            lesson_context['lesson_id'],
            lesson_context['module_id'],
            lesson_context['module_name'],
            lesson_context['cefr_level']
        )

        logger.info(
            f"Updated module context for story {story_id}, "
            f"user {user_id}, module {lesson_context['module_name']}"
        )

    except Exception as e:
        logger.error(f"Error updating module context: {e}")


async def increment_actions_counter(
        pool_base,
        user_id: int,
        story_id: int
) -> int:
    """
    Увеличить счетчик действий пользователя

    Returns:
        Новое значение счетчика
    """

    query = """
        UPDATE t_story_user_progress
        SET 
            c_actions_count = c_actions_count + 1,
            c_last_interaction_at = NOW()
        WHERE c_user_id = $1 AND c_story_id = $2
        RETURNING c_actions_count
    """

    try:
        result = await pgDB.fExec_UpdateQuery_args(
            pool_base, query, user_id, story_id
        )

        if result:
            return result[0][0]

        return 0

    except Exception as e:
        logger.error(f"Error incrementing actions counter: {e}")
        return 0


async def should_show_skip_button(
        pool_base,
        user_id: int,
        story_id: int,
        threshold: int = 5
) -> bool:
    """
    Проверить нужно ли показывать кнопку Skip

    Args:
        threshold: После скольких действий показывать Skip (по умолчанию 5)

    Returns:
        True если нужно показать кнопку Skip
    """

    query = """
        SELECT c_actions_count
        FROM t_story_user_progress
        WHERE c_user_id = $1 AND c_story_id = $2
    """

    try:
        result = await pgDB.fExec_SelectQuery_args(
            pool_base, query, user_id, story_id
        )

        if result:
            actions_count = result[0][0]
            return actions_count >= threshold

        return False

    except Exception as e:
        logger.error(f"Error checking skip button: {e}")
        return False


async def get4story_lesson_context(pool_base, lesson_id: int) -> Dict[str, Any]:
    """
    Получает контекст урока для AI генерации и story system

    Args:
        pool_base: Connection pool БД
        lesson_id: ID урока

    Returns:
        Dict с контекстом урока:
        {
            'lesson_id': int,
            'module_id': int,
            'module_name': str,
            'lesson_name': str,
            'cefr_level': str,
            'grammar_focus': str,  # module_name как grammar focus
            'context_string': str  # для старых функций
        }
    """

    query = """
        SELECT 
            l.c_lesson_id,
            m.c_module_id,
            m.c_module_name, 
            l.c_lesson_name, 
            t3.c_qlvl_name
        FROM t_lp_lesson l 
        JOIN t_lp_module m ON l.c_module_id = m.c_module_id 
        JOIN ts_qlvl t3 ON m.c_qlvl_id = t3.c_qlvl_id 
        WHERE l.c_lesson_id = $1
    """

    try:
        result = await pgDB.fExec_SelectQuery_args(pool_base, query, lesson_id)

        if result:
            lesson_id_db = result[0][0]
            module_id = result[0][1]
            module_name = result[0][2]
            lesson_name = result[0][3]
            cefr_level = result[0][4]

            # Формируем context string для обратной совместимости
            context_string = f"{module_name} - {lesson_name} - English level is {cefr_level}"

            return {
                'lesson_id': lesson_id_db,
                'module_id': module_id,
                'module_name': module_name,
                'lesson_name': lesson_name,
                'cefr_level': cefr_level,
                'grammar_focus': module_name,  # grammar focus = module name
                'context_string': context_string
            }

        # Default fallback
        return {
            'lesson_id': lesson_id,
            'module_id': None,
            'module_name': 'General English',
            'lesson_name': 'General Lesson',
            'cefr_level': 'A1',
            'grammar_focus': 'General English',
            'context_string': 'General English lesson'
        }

    except Exception as e:
        logger.error(f"Error getting lesson context: {e}")
        return {
            'lesson_id': lesson_id,
            'module_id': None,
            'module_name': 'General English',
            'lesson_name': 'General Lesson',
            'cefr_level': 'A1',
            'grammar_focus': 'General English',
            'context_string': 'General English lesson'
        }


