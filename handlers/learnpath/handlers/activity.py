import logging
from typing import Dict, Any, Optional

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import fpgDB as pgDB
import mynaming as myN
from states import myState

logger = logging.getLogger(__name__)


async def check_user_active_story(pool_base, user_id: int) -> Optional[Dict[str, Any]]:
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
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=myN.fCSS('st_cont'), callback_data=f"task8_continue:{story_id}"))
    builder.add(InlineKeyboardButton(text=myN.fCSS('st_reset'), callback_data=f"story_reset_yes:{story_id}"))
    builder.add(InlineKeyboardButton(text=myN.fCSS('st_list'), callback_data="story_list:unf-0"))
    builder.add(InlineKeyboardButton(text=myN.fCSS('menu'), callback_data="menu"))
    builder.adjust(1)

    text = (
        "📚 <u>У вас есть незавершенная история!</u>\n\n"
        f"<b>{story_name}</b>\n"
        f"📖 Сцена: {scene_name}\n\n"
        "Вы можете продолжить с того места, где остановились, "
        "или начать новую историю (прогресс будет сброшен)."
    )

    await message.answer(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await state.set_state(myState.task8_choose_continue_or_restart)


async def start_story_questionnaire(
        message: types.Message,
        state: FSMContext,
        lesson_context: Dict[str, Any]
):
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
            "Я задам вам несколько вопросов, чтобы создать историю.\n\n"
            "Давайте начнем! 🎯"
        )

    await message.answer(text, parse_mode="HTML")

    from .story import show_questionnaire_q0
    await show_questionnaire_q0(message, state)
