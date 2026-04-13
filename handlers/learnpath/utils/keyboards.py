"""
Клавиатуры для LearnPath модуля
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_continue_learnpath_kb() -> InlineKeyboardMarkup:
    """Клавиатура продолжения обучения"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="🚀 Продолжить обучение",
        callback_data="continue_learning"
    ))
    builder.add(InlineKeyboardButton(
        text="📚 Моя программа",
        callback_data="view_learnpath"
    ))
    builder.add(InlineKeyboardButton(
        text="◀️ Назад",
        callback_data="menu"
    ))
    builder.adjust(1)
    return builder.as_markup()


def get_rating_kb(show_subtopic_button: bool = False) -> InlineKeyboardMarkup:
    """
    Клавиатура оценки 1-5 звезд

    Args:
        show_subtopic_button: Показывать ли кнопку "Указать рейтинг субтемы"
    """
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки с рейтингом
    for stars in range(1, 6):
        builder.add(InlineKeyboardButton(
            text="⭐" * stars,
            callback_data=f"interest_rate_{stars}"
        ))

    # Если нужно, добавляем кнопку для уточнения рейтинга подтем
    if show_subtopic_button:
        builder.add(InlineKeyboardButton(
            text="📋 Указать рейтинг подтем",
            callback_data="specify_subtopic_rating"
        ))
        builder.adjust(5, 1)  # 5 звезд в ряд, потом кнопка на отдельной строке
    else:
        builder.adjust(5)  # Только 5 звезд в ряд

    return builder.as_markup()


def get_subtopic_rating_kb() -> InlineKeyboardMarkup:
    """Клавиатура оценки подтемы с кнопкой завершения"""
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки с рейтингом для подтем
    for stars in range(1, 6):
        builder.add(InlineKeyboardButton(
            text="⭐" * stars,
            callback_data=f"subtopic_rate_{stars}"
        ))

    # Добавляем кнопку завершения уточнения
    builder.add(InlineKeyboardButton(
        text="✅ Завершить уточнение",
        callback_data="finish_subtopic_rating"
    ))

    builder.adjust(5, 1)  # 5 звезд в ряд, потом кнопка завершения
    return builder.as_markup()


def get_module_navigation_kb(module_id: int, topic_id: int, show_skip: bool = True) -> InlineKeyboardMarkup:
    """
    Навигация по модулю

    Args:
        module_id: ID модуля
        topic_id: ID темы
        show_skip: Показывать ли кнопку "Пропустить"
    """
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="✅ Понятно, продолжить",
        callback_data=f"complete_module_{module_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="❓ Нужно объяснение",
        callback_data=f"explain_module_{module_id}"
    ))

    if show_skip:
        builder.add(InlineKeyboardButton(
            text="⏭️ Пропустить",
            callback_data=f"skip_module_{module_id}"
        ))

    builder.add(InlineKeyboardButton(
        text="◀️ К теме",
        callback_data=f"topic_overview_{topic_id}"
    ))
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def get_topic_overview_kb(topic_id: int, has_next_module: bool = True) -> InlineKeyboardMarkup:
    """
    Клавиатура обзора темы

    Args:
        topic_id: ID темы
        has_next_module: Есть ли следующий модуль
    """
    builder = InlineKeyboardBuilder()

    if has_next_module:
        builder.add(InlineKeyboardButton(
            text="▶️ Начать занятие",
            callback_data=f"start_next_module_{topic_id}"
        ))

    builder.add(InlineKeyboardButton(
        text="📊 Пройти тест по теме",
        callback_data=f"topic_test_{topic_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="◀️ К программе",
        callback_data="view_learnpath"
    ))
    builder.adjust(1)
    return builder.as_markup()


def get_back_to_menu_kb() -> InlineKeyboardMarkup:
    """Простая клавиатура возврата в меню"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="◀️ Назад в меню",
        callback_data="menu"
    ))
    return builder.as_markup()


def get_answer_options_kb(options: list, callback_prefix: str = "answer") -> InlineKeyboardMarkup:
    """
    Клавиатура с вариантами ответов

    Args:
        options: Список вариантов
        callback_prefix: Префикс для callback_data
    """
    builder = InlineKeyboardBuilder()
    for idx, option in enumerate(options):
        builder.add(InlineKeyboardButton(
            text=f"{chr(65 + idx)}. {option}",
            callback_data=f"{callback_prefix}_{idx}"
        ))
    builder.adjust(1)
    return builder.as_markup()