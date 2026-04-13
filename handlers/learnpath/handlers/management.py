"""
Handlers для управления программой и статистики
"""

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

import fpgDB as pgDB
from ..services.learnpath_service import LearnPathService
from ..services.progress_service import ProgressService

router = Router(name='learnpath_management')


@router.callback_query(F.data == "edit_learnpath")
async def edit_learnpath_menu(callback: types.CallbackQuery, state: FSMContext, pool):
    """Меню редактирования программы"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    str_Msg = (
        f"⚙️ <b>Настройка программы</b>\n\n"
        f"Что вы хотите изменить?"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔄 Пересоздать программу", callback_data="recreate_learnpath"))
    builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data="view_learnpath"))
    builder.adjust(1)

    await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, "edit_learnpath_menu")


@router.callback_query(F.data == "recreate_learnpath")
async def recreate_learnpath(callback: types.CallbackQuery, state: FSMContext, pool):
    """Пересоздание программы"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    str_Msg = (
        f"⚠️ <b>Внимание!</b>\n\n"
        f"Это удалит текущую программу и весь прогресс.\n"
        f"Вы уверены?"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Да, пересоздать", callback_data="confirm_recreate"))
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="edit_learnpath"))
    builder.adjust(1)

    await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, "recreate_learnpath_confirm")


@router.callback_query(F.data == "confirm_recreate")
async def confirm_recreate_learnpath(callback: types.CallbackQuery, state: FSMContext, pool):
    """Подтверждение пересоздания программы"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    service = LearnPathService(pool)
    await service.delete_learnpath(vUserID)

    await callback.answer("Программа удалена. Начинаем заново.", show_alert=True)

    # Импортируем функцию из assessment
    from .assessment import learnpath_init_handler
    await learnpath_init_handler(callback.message, state, pool)

    await pgDB.fExec_LogQuery(pool_log, vUserID, "learnpath_recreated")


@router.callback_query(F.data == "learnpath_stats")
async def learnpath_stats(callback: types.CallbackQuery, state: FSMContext, pool):
    """Статистика по программе"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    progress_service = ProgressService(pool)
    stats = await progress_service.get_statistics(vUserID)

    if not stats:
        await callback.answer("Статистика недоступна", show_alert=True)
        return

    str_Msg = (
        f"📊 <b>Ваша статистика</b>\n\n"
        f"<b>Темы:</b>\n"
        f"• Всего: {stats['total_topics']}\n"
        f"• Завершено: {stats['completed_topics']}\n"
        f"• В процессе: {stats['in_progress_topics']}\n"
        f"• Средний прогресс: {stats['avg_progress']}%\n\n"
        f"<b>Тесты:</b>\n"
        f"• Пройдено: {stats['total_tests']}\n"
        f"• Успешно: {stats['passed_tests']}\n"
        f"• Средний балл: {stats['avg_score']}%\n\n"
        f"<b>Время обучения:</b>\n"
        f"{stats['hours']} ч {stats['minutes']} мин"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data="view_learnpath"))

    await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, "learnpath_stats")