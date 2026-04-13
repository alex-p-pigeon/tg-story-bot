"""
Handlers для обработки практических заданий
"""

from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

from states import myState
import fpgDB as pgDB
import selfFunctions as myF

router = Router(name='learnpath_practice')


@router.message(F.text, StateFilter(myState.learnpath_practice_text))
async def handle_practice_text(message: types.Message, state: FSMContext, pool, dp):
    """Обработка текстового ответа на практику"""
    pool_base, pool_log = pool
    vUserID = message.chat.id

    user_data = await state.get_data()
    module_id = user_data.get('current_module_id')
    topic_id = user_data.get('current_topic_id')
    module_content = user_data.get('module_content', {})

    usertext = message.text.strip()

    nlp_tools = dp.workflow_data.get("nlp_tools")

    # Грамматическая проверка
    str_grammar, index_rule_pairs, improved_line = await myF.fGrammarCheck_txt(
        nlp_tools.tool, usertext, pool, vUserID
    )

    # AI оценка ответа
    task_description = module_content.get('task', '')
    prompt = f"Evaluate this answer to the task: {task_description}\n\nStudent answer: {usertext}\n\nProvide brief feedback."

    ai_feedback = await myF.afSendMsg2AI(prompt, pool_base, vUserID, toggleParam=2)

    str_Msg = (
        f"✅ <b>Ваш ответ получен</b>\n\n"
        f"{ai_feedback}\n\n"
        f"<b>Грамматическая проверка:</b>\n"
        f"{str_grammar}"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Продолжить", callback_data=f"complete_module_{module_id}"))
    builder.add(InlineKeyboardButton(text="🔄 Попробовать снова", callback_data=f"start_module_{module_id}"))
    builder.add(InlineKeyboardButton(text="◀️ К теме", callback_data=f"topic_overview_{topic_id}"))
    builder.adjust(2, 1)

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"practice_text_submitted|module:{module_id}")


@router.message(F.voice, StateFilter(myState.learnpath_practice_voice))
async def handle_practice_voice(message: types.Message, state: FSMContext, pool, dp):
    """Обработка голосового ответа на практику"""
    pool_base, pool_log = pool
    vUserID = message.chat.id

    user_data = await state.get_data()
    module_id = user_data.get('current_module_id')
    topic_id = user_data.get('current_topic_id')

    # Распознавание речи
    usertext = await myF.afVoiceToTxt(message, pool, vUserID)

    if not usertext:
        await message.answer("Не удалось распознать речь. Попробуйте еще раз.", parse_mode=ParseMode.HTML)
        return

    nlp_tools = dp.workflow_data.get("nlp_tools")

    # Грамматическая проверка
    str_grammar, index_rule_pairs, improved_line = await myF.fGrammarCheck_txt(
        nlp_tools.tool, usertext, pool, vUserID
    )

    str_Msg = (
        f"🎤 <b>Распознанный текст:</b>\n"
        f"{usertext}\n\n"
        f"<b>Грамматическая проверка:</b>\n"
        f"{str_grammar}"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Продолжить", callback_data=f"complete_module_{module_id}"))
    builder.add(InlineKeyboardButton(text="🔄 Попробовать снова", callback_data=f"start_module_{module_id}"))
    builder.add(InlineKeyboardButton(text="◀️ К теме", callback_data=f"topic_overview_{topic_id}"))
    builder.adjust(2, 1)

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"practice_voice_submitted|module:{module_id}")


@router.message(F.text | F.voice, StateFilter(myState.learnpath_practice_dialogue))
async def handle_practice_dialogue(message: types.Message, state: FSMContext, pool, dp):
    """Обработка диалогового задания"""
    pool_base, pool_log = pool
    vUserID = message.chat.id

    user_data = await state.get_data()
    module_id = user_data.get('current_module_id')
    topic_id = user_data.get('current_topic_id')
    module_content = user_data.get('module_content', {})

    # Получаем текст (текстовый или голосовой)
    if message.voice:
        usertext = await myF.afVoiceToTxt(message, pool, vUserID)
        if not usertext:
            await message.answer("Не удалось распознать речь. Попробуйте еще раз.", parse_mode=ParseMode.HTML)
            return
    else:
        usertext = message.text.strip()

    nlp_tools = dp.workflow_data.get("nlp_tools")

    # Грамматическая проверка
    str_grammar, index_rule_pairs, improved_line = await myF.fGrammarCheck_txt(
        nlp_tools.tool, usertext, pool, vUserID
    )

    # AI ответ в диалоге
    task_description = module_content.get('task', '')
    prompt = f"Continue this dialogue scenario: {task_description}\n\nStudent message: {usertext}\n\nRespond naturally and provide feedback."

    ai_response = await myF.afSendMsg2AI(prompt, pool_base, vUserID, toggleParam=2)

    str_Msg = (
        f"💬 <b>Ответ:</b>\n"
        f"{ai_response}\n\n"
        f"<b>Грамматика:</b>\n"
        f"{str_grammar}"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Завершить диалог", callback_data=f"complete_module_{module_id}"))
    builder.add(InlineKeyboardButton(text="💬 Продолжить диалог", callback_data=f"continue_dialogue_{module_id}"))
    builder.add(InlineKeyboardButton(text="◀️ К теме", callback_data=f"topic_overview_{topic_id}"))
    builder.adjust(2, 1)

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"practice_dialogue|module:{module_id}")


@router.callback_query(F.data.startswith("continue_dialogue_"))
async def continue_dialogue(callback: types.CallbackQuery, state: FSMContext, pool):
    """Продолжить диалог"""
    await callback.answer("Продолжайте диалог ✍️", show_alert=False)