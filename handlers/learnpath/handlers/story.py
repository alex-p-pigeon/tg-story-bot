"""
Story Handlers - Обработчики для интерактивных историй (Task 8)
Интегрируется с activity.py
"""



import logging
from aiogram import Router, F, types
from aiogram.types import Message, ReplyKeyboardRemove, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
import json
from aiogram.exceptions import TelegramBadRequest
from typing import Dict, Any, Optional, List

from aiogram.types import BufferedInputFile
import os
from pathlib import Path

import selfFunctions as myF
from states import myState

from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..story.engines.interactive_story_engine import InteractiveStoryEngine
#from ..story.generators.skeleton_generator import StorySkeletonGenerator
from ..story.generators.skeleton_generator_v2 import StorySkeletonGeneratorV2
from ..story.managers.npc_manager import NPCManager
from ..story.managers.item_manager import ItemManager
from ..story.engines.dialogue_engine import DialogueEngine
from .story_helpers import generate_npc_voice_message

from .story_helpers import (
    get_story_final_message,
    get_scene_important_reveals,
    mark_story_completed,
    check_if_story_ending,
    format_revelation_message,
    get_action_verb_for_item,
    generate_story_report
)





import mynaming as myN
import fpgDB as pgDB

import logging
logger = logging.getLogger(__name__)

story_router = Router(name='story')

GOALS_BY_GENRE = {
    'adventure': {
        'reach_destination': {
            'label': '🎯 Reach destination',
            'description': 'Reach a specific destination, overcoming obstacles along the way'
        },
        'find_lost_treasure': {
            'label': '🏺 Find lost treasure',
            'description': 'Find a lost item, artifact, or treasure by following clues'
        },
        'rescue_someone': {
            'label': '🚨 Rescue someone',
            'description': 'Rescue someone who is missing or in danger'
        },
        'escape_danger': {
            'label': '🏃 Escape danger',
            'description': 'Escape from a dangerous situation or location'
        },
        'uncover_truth': {
            'label': '📜 Uncover the truth',
            'description': 'Uncover a hidden truth or secret about the place or situation'
        }
    },

    'mystery': {
        'solve_crime': {
            'label': '🔍 Solve the crime',
            'description': 'Solve a crime or mystery by gathering evidence and interviewing people'
        },
        'find_missing_person': {
            'label': '👤 Find missing person',
            'description': 'Locate a missing person by following leads and clues'
        },
        'reveal_culprit': {
            'label': '🎭 Reveal the culprit',
            'description': 'Identify and expose the person responsible for the mystery'
        },
        'decode_clues': {
            'label': '🧩 Decode the clues',
            'description': 'Decode mysterious clues and piece together what happened'
        },
        'uncover_truth': {
            'label': '📜 Uncover the truth',
            'description': 'Uncover the hidden truth behind mysterious events'
        }
    },

    'slice_of_life': {
        'complete_routine': {
            'label': '📅 Complete daily routine',
            'description': 'Successfully complete daily routine tasks within time constraints'
        },
        'handle_situation': {
            'label': '💼 Handle important situation',
            'description': 'Handle an important life situation (interview, appointment, meeting, etc.)'
        },
        'achieve_personal_goal': {
            'label': '⭐ Achieve personal goal',
            'description': 'Achieve a specific personal objective through planning and interaction'
        },
        'solve_problem': {
            'label': '🔧 Solve everyday problem',
            'description': 'Solve a practical everyday problem that requires help from others'
        },
        'uncover_truth': {
            'label': '📜 Uncover the truth',
            'description': 'Discover the truth about a personal or professional situation'
        }
    }
}




# ============================================================================
# Other actions
# ============================================================================





def ____________questionnaire(): pass


# ========================================
# ВОПРОС 0: ОПИСАНИЕ ИСТОРИИ
# ========================================

async def show_questionnaire_q0(message: types.Message, state: FSMContext):
    """
    Показать вопрос 0: Описание истории от пользователя
    """

    text = (
        "📖 <b>Создание персональной истории</b>\n\n"
        "Опишите историю, которую хотели бы пройти.\n"
        "Можете указать:\n"
        "• Место действия (остров, город, космос...)\n"
        "• Что вы ищете или исследуете\n"
        "• Кого можете встретить\n\n"
        "<i>Например: \"Я исследую заброшенный замок в горах и ищу древний артефакт. "
        "Встречаю загадочного хранителя и учёного-археолога.\"</i>\n\n"
        "Или нажмите <b>Skip</b>, чтобы сгенерировать случайную историю."
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="⏭️ Skip (random story)",
        callback_data="q0:skip"
    ))

    await message.answer(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

    await state.set_state(myState.task8_questionnaire_q0)


@story_router.message((F.text & ~F.text.startswith('/')), StateFilter(myState.task8_questionnaire_q0))
async def handle_q0_text(message: types.Message, state: FSMContext):
    """Обработать текстовое описание от пользователя"""

    user_description = message.text.strip()

    # Валидация (минимум 10 символов)
    if len(user_description) < 10:
        await message.answer(
            "⚠️ Пожалуйста, введите более подробное описание (минимум 10 символов) "
            "или нажмите Skip для случайной истории."
        )
        return

    # Сохраняем описание
    await state.update_data(task8_q0_description=user_description)

    await message.answer("✅ Описание принято!")

    # Переходим к вопросу 1
    await show_questionnaire_q1(message, state)


@story_router.callback_query(
    F.data == "q0:skip",
    StateFilter(myState.task8_questionnaire_q0)
)
async def handle_q0_skip(callback: types.CallbackQuery, state: FSMContext):
    """Пропустить описание - случайная история"""

    # Сохраняем пустое описание
    await state.update_data(task8_q0_description=None)

    await callback.answer("✅ Будет сгенерирована случайная история")

    # Переходим к вопросу 1
    await show_questionnaire_q1(callback.message, state)


# ========================================
# ВОПРОС 1: ЖАНР
# ========================================

async def show_questionnaire_q1(message: types.Message, state: FSMContext):
    """
    Показать вопрос 1: Жанр истории
    """

    text = (
        "📖 <b>Вопрос 1 из 4: Жанр</b>\n\n"
        "Какой жанр истории вы предпочитаете?"
    )

    builder = InlineKeyboardBuilder()

    genres = [
        ("🗺️ Adventure", "genre:adventure"),
        ("🔍 Detective", "genre:mystery"),
        ("☕ Slice of Life", "genre:slice_of_life"),
    ]

    for label, callback_data in genres:
        builder.add(InlineKeyboardButton(
            text=label,
            callback_data=callback_data
        ))

    builder.adjust(1)

    await message.answer(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

    await state.set_state(myState.task8_questionnaire_q1)


@story_router.callback_query(
    F.data.startswith("genre:"),
    StateFilter(myState.task8_questionnaire_q1)
)
async def handle_q1_answer(callback: types.CallbackQuery, state: FSMContext):
    """Обработать ответ на вопрос 1"""

    genre = callback.data.split(":")[1]

    await state.update_data(task8_q1_genre=genre)

    await callback.answer("✅ Жанр выбран!")

    # Переходим к вопросу 2
    await show_questionnaire_q2(callback.message, state)


# ========================================
# ВОПРОС 2: НАСТРОЕНИЕ
# ========================================

async def show_questionnaire_q2(message: types.Message, state: FSMContext):
    """
    Показать вопрос 2: Настроение истории
    """

    text = (
        "📖 <b>Вопрос 2 из 4: Настроение</b>\n\n"
        "Какое настроение должно быть у истории?"
    )

    builder = InlineKeyboardBuilder()

    moods = [
        ("😊 Optimistic", "mood:optimistic"),
        ("😰 Tense", "mood:tense"),
        ("😂 Funny", "mood:funny"),
    ]

    for label, callback_data in moods:
        builder.add(InlineKeyboardButton(
            text=label,
            callback_data=callback_data
        ))

    builder.adjust(1)

    await message.answer(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

    await state.set_state(myState.task8_questionnaire_q2)


@story_router.callback_query(
    F.data.startswith("mood:"),
    StateFilter(myState.task8_questionnaire_q2)
)
async def handle_q2_answer(callback: types.CallbackQuery, state: FSMContext):
    """Обработать ответ на вопрос 2"""

    mood = callback.data.split(":")[1]

    await state.update_data(task8_q2_mood=mood)
    await callback.answer("✅ Настроение выбрано!")

    await show_questionnaire_q3(callback.message, state)


# ========================================
# ВОПРОС 3: РЕАЛИСТИЧНОСТЬ
# ========================================

async def show_questionnaire_q3(message: types.Message, state: FSMContext):
    """
    Показать вопрос 3: Реалистичность
    """

    text = (
        "📖 <b>Вопрос 3 из 4: Реалистичность</b>\n\n"
        "Насколько реалистичной должна быть история?"
    )

    builder = InlineKeyboardBuilder()

    realism_levels = [
        ("✨ Full Fantasy", "realism:full_fantasy"),
        ("🎪 Unlikely but possible", "realism:unlikely"),
        ("🏙️ Unusual but real", "realism:unusual"),
        ("📰 Fully realistic", "realism:realistic")
    ]

    for label, callback_data in realism_levels:
        builder.add(InlineKeyboardButton(
            text=label,
            callback_data=callback_data
        ))

    builder.adjust(1)

    await message.answer(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

    await state.set_state(myState.task8_questionnaire_q3)


@story_router.callback_query(
    F.data.startswith("realism:"),
    StateFilter(myState.task8_questionnaire_q3)
)
async def handle_q3_answer(callback: types.CallbackQuery, state: FSMContext):
    """Обработать ответ на вопрос 3"""

    realism = callback.data.split(":")[1]

    await state.update_data(task8_q3_realism=realism)
    await callback.answer("✅ Реалистичность выбрана!")

    # ✅ Переходим к вопросу 4 - ВЫБОР ЦЕЛИ (новое!)
    await show_questionnaire_q4(callback.message, state)


# ========================================
# ВОПРОС 4: ГЛАВНАЯ ЦЕЛЬ (динамический по жанру)
# ========================================

async def show_questionnaire_q4(message: types.Message, state: FSMContext):
    """
    Показать вопрос 4: Главная цель (зависит от жанра)
    """

    user_data = await state.get_data()
    genre = user_data.get('task8_q1_genre', 'adventure')
    user_description = user_data.get('task8_q0_description')

    # ✅ Получаем цели для выбранного жанра из справочника
    genre_goals = GOALS_BY_GENRE.get(genre, GOALS_BY_GENRE['adventure'])

    # Формируем текст
    if user_description:
        text = (
            "📖 <b>Вопрос 4 из 4: Главная цель</b>\n\n"
            "На основе вашего описания, выберите главную цель истории:"
        )
    else:
        text = (
            "📖 <b>Вопрос 4 из 4: Главная цель</b>\n\n"
            "Какой должна быть главная цель в истории?"
        )

    builder = InlineKeyboardBuilder()

    # ✅ Динамически создаем кнопки из справочника
    for goal_key, goal_data in genre_goals.items():
        builder.add(InlineKeyboardButton(
            text=goal_data['label'],
            callback_data=f"goal:{goal_key}"
        ))

    builder.adjust(1)

    await message.answer(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

    await state.set_state(myState.task8_questionnaire_q4)


@story_router.callback_query(
    F.data.startswith("goal:"),
    StateFilter(myState.task8_questionnaire_q4)
)
async def handle_q4_answer(callback: types.CallbackQuery, state: FSMContext, pool):
    """Обработать ответ на вопрос 4 и начать генерацию истории"""

    goal = callback.data.split(":")[1]

    await state.update_data(task8_q4_goal=goal)
    await callback.answer("✅ Цель выбрана!")

    # Собираем все ответы
    user_data = await state.get_data()

    questionnaire_answers = {
        'user_description': user_data.get('task8_q0_description'),
        'genre': user_data['task8_q1_genre'],
        'mood': user_data['task8_q2_mood'],
        'realism': user_data['task8_q3_realism'],
        'complexity': ['puzzles', 'dialogues'],  # Фиксированные
        'goal': goal  # ✅ Всегда выбирается из справочника!
    }

    #logger.info(f"Questionnaire completed: {questionnaire_answers}")

    # Показываем "Генерируем историю..."
    msg = await callback.message.answer(
        "⏳ <b>Генерируем вашу историю...</b>\n\n"
        "Это может занять 30-60 секунд. Пожалуйста, подождите.",
        parse_mode="HTML"
    )

    # Переходим к генерации истории
    await generate_and_start_story(
        callback.message,
        state,
        pool,
        questionnaire_answers,
        user_data
    )

def ____________starting_continuing(): pass
# ========================================
# ГЕНЕРАЦИЯ И ЗАПУСК ИСТОРИИ
# ========================================

async def generate_and_start_story(         #appr
        message: types.Message,
        state: FSMContext,
        pool,
        questionnaire_answers: dict,
        user_data: dict
):
    """
    Сгенерировать историю на основе ответов опросника
    """

    pool_base, pool_log = pool
    user_id = message.chat.id       #.from_user.id
    #lesson_context = user_data.get('task8_lesson_context', {
    #    'grammar_focus': 'General grammar practice',
    #    'cefr_level': 'B1'
    #})

    try:
        # Создаем генератор V2
        from ..story.generators.skeleton_generator_v2 import StorySkeletonGeneratorV2
        generator = StorySkeletonGeneratorV2(pool, user_id)

        # Генерируем каркас истории
        skeleton = await generator.generate_skeleton(
            #user_id=user_id,
            genre=questionnaire_answers['genre'],
            mood=questionnaire_answers['mood'],
            realism=questionnaire_answers['realism'],
            complexity=questionnaire_answers['complexity'],
            goal=questionnaire_answers['goal'],
            #initial_lesson_context=lesson_context,
            num_chapters=2,
            scenes_structure=[2, 2],
            user_description=questionnaire_answers.get('user_description')  # ✅ Новое!
        )

        story_id = skeleton['story_id']
        logger.info(f"Story generated: {story_id} for user {user_id}")

        # ====================================================================
        # ВАЛИДАЦИЯ + AUTO-FIX
        # ====================================================================
        from ..story.validators.story_validator import StoryQualityValidator
        from ..story.validators.grammar_validator import GrammarValidator
        from ..story.fixers.story_fixer import StoryFixerWithValidation

        # 1. Структурная валидация
        validator = StoryQualityValidator()
        validation = await validator.validate_story(skeleton, skeleton.get('elaboration'))

        logger.info(f"Story quality: {validation.score:.1f}/100 - {len(validation.issues)} issues")

        # 2. Grammar валидация
        grammar_validator = GrammarValidator(pool=pool_base, user_id=user_id)
        grammar_validation = await grammar_validator.validate_story_texts(
            story_skeleton=skeleton,
            story_elaboration=skeleton.get('elaboration', {}),
            target_cefr='B1'  #lesson_context.get('cefr_level', 'B1')
        )

        logger.info(f"Grammar quality: {grammar_validation.grammar_score:.1f}/100")

        # 3. Auto-fix если качество низкое
        if not validation.is_valid and validation.score < 80:
            logger.warning(f"!!!️ Story quality below threshold: {validation.score:.1f}/100. Attempting auto-fix...")

            fixer = StoryFixerWithValidation(pool, user_id)
            fixed_story, was_fixed = await fixer.fix_and_validate(
                story_skeleton=skeleton,
                validation_result=validation,
                max_attempts=2
            )

            if was_fixed:
                logger.info("✅ Story auto-fixed successfully")
                skeleton = fixed_story
                story_id = skeleton['story_id']

                # Re-validate после fix
                validation = await validator.validate_story(skeleton, skeleton.get('elaboration'))
                logger.info(f" After fix: {validation.score:.1f}/100")
            else:
                logger.warning("!!!️ Auto-fix failed or insufficient improvement")

        # 4. Проверка критических проблем
        critical_issues = [i for i in validation.issues if i.severity.value == 'CRITICAL']
        if critical_issues and validation.score < 60:
            # Слишком много критических проблем - отклоняем историю
            logger.error(f"x Story has {len(critical_issues)} critical issues (score: {validation.score:.1f}/100)")

            await message.answer(
                "❌ <b>История не прошла проверку качества</b>\n\n"
                "Обнаружены критические проблемы. Попробуйте выбрать другие параметры.",
                parse_mode="HTML"
            )
            return

        # 5. Логируем проблемы (не критические)
        if not validation.is_valid:
            logger.warning(f"!!!️ Story has quality issues (score: {validation.score:.1f}/100):")
            for issue in validation.issues[:5]:
                logger.warning(f"  [{issue.severity.value}] {issue.description}")

        if not grammar_validation.is_valid:
            logger.warning(
                f"!!!️ Grammar: CEFR {grammar_validation.cefr_level_detected} "
                f"vs target {grammar_validation.cefr_level_target}"
            )

        # ====================================================================
        # STORY APPROVED - SAVE AND START
        # ====================================================================

        # Сохраняем story_id в state
        await state.update_data(task8_story_id=story_id)

        # Отправляем подтверждение
        await message.answer(
            f"✅ <b>История создана!</b>\n\n"
            f"📖 <b>{skeleton['story_name']}</b>\n\n"
            f"{skeleton['description']}\n\n"
            f"Готовы начать?",
            parse_mode="HTML"
        )

        # Загружаем первую сцену
        await load_and_show_first_scene(message, state, pool, story_id)

    except Exception as e:
        logger.error(f"Error generating story: {e}", exc_info=True)
        await message.answer(
            "❌ <b>Ошибка при генерации истории</b>\n\n"
            "Пожалуйста, попробуйте еще раз или обратитесь к администратору.",
            parse_mode="HTML"
        )

async def load_and_show_first_scene(
        message: types.Message,
        state: FSMContext,
        pool,
        story_id: int
):
    """Загрузить и показать первую сцену истории"""

    pool_base, pool_log = pool
    user_id = message.chat.id

    try:
        # Создаем engine
        engine = InteractiveStoryEngine(pool, user_id)

        # Получаем ID первой сцены (минимальный запрос)
        query = """
            SELECT c_scene_id
            FROM t_story_scenes
            WHERE c_story_id = $1
            ORDER BY c_scene_number
            LIMIT 1
        """

        result = await pgDB.fExec_SelectQuery_args(pool_base, query, story_id)

        if not result:
            logger.error(f"No scenes found for story {story_id}")
            return

        scene_id = result[0][0]

        # ✅ Создать прогресс с инициализацией инвентаря
        await engine._create_user_progress(story_id, scene_id, state)

        # ✅ Загрузить созданный прогресс (с инвентарем!)
        user_progress = await engine._get_user_progress(story_id)

        # ✅ Получить полные данные сцены через generate_scene_description
        # (он сам сделает SELECT и парсинг всех JSONB полей)
        scene_data = await engine.dialogue_engine.generate_scene_description(
            scene_id=scene_id,
            story_id=story_id,
            user_progress=user_progress  # ✅ С реальным инвентарем!
        )
        logger.info(f'-------------user_progress:{user_progress}')
        logger.info(f'--------------scene_data0:{scene_data}')
        # ✅ Обогатить NPC info (имена для кнопок)
        scene_data = await _enrich_scene_with_npc_info(pool_base, scene_data)
        logger.info(f'--------------scene_data:{scene_data}')


        # Показать сцену
        await show_scene(message, state, scene_data, pool)

        # Переходим в режим активной истории
        await state.set_state(myState.task8_story_active)

    except Exception as e:
        logger.error(f"Error loading first scene: {e}", exc_info=True)


async def _enrich_scene_with_npc_info(pool_base, scene_data: dict) -> dict:          #appr
    """
    Обогатить данные сцены информацией об NPC

    Конвертирует c_npcs_present из [11, 12, 13] в
    [{'id': 11, 'name': 'Emma'}, {'id': 12, 'name': 'Liam'}, ...]
    """

    npc_ids = scene_data.get('npcs_present', [])

    # Парсим если строка
    if isinstance(npc_ids, str):

        npc_ids = json.loads(npc_ids)

    if not npc_ids:
        scene_data['npcs_info'] = []
        return scene_data

    # Загружаем имена NPC из БД
    placeholders = ', '.join([f'${i + 1}' for i in range(len(npc_ids))])
    query = f"""
        SELECT c_npc_id, c_name
        FROM t_story_npcs
        WHERE c_npc_id IN ({placeholders})
    """

    result = await pgDB.fExec_SelectQuery_args(pool_base, query, *npc_ids)

    npcs_info = []
    if result:
        for row in result:
            npcs_info.append({
                'npc_id': row[0],
                'name': row[1]
            })

    scene_data['npcs_info'] = npcs_info
    return scene_data



# ============================================================================
# Continue/Restart handlers
# ============================================================================
#engine = InteractiveStoryEngine(pool, user_id)

@story_router.callback_query(F.data.startswith("task8_continue:"))          #approved
async def handle_continue_story(callback: types.CallbackQuery, state: FSMContext, pool):
    """Continue existing story"""

    story_id = int(callback.data.split(":")[1])
    user_id = callback.message.chat.id  #.from_user.id

    await state.update_data(task8_story_id=story_id)

    logger.info(f'AJRM - story_id:{story_id}')



    try:
        await _show_current_scene(callback.message, state, pool, story_id)      #ajrm
        await state.set_state(myState.task8_story_active)
        await callback.answer()

    except Exception as e:
        logger.error(f"Error continuing story: {e}", exc_info=True)
        await callback.message.answer("❌ Error loading story. Please try again.")


# ============================================================================
# Scene display
# ============================================================================
async def _show_current_scene(message, state, pool, story_id):      #appr
    """Show current scene"""

    user_id = message.chat.id   #.from_user.id
    engine = InteractiveStoryEngine(pool, user_id)

    user_progress = await engine._get_user_progress(story_id)

    logger.info(f'AJRM - user_progress:{user_progress}')
    if not user_progress:
        await message.answer("❌ Progress not found.")
        return

    scene_data = await engine.dialogue_engine.generate_scene_description(
        scene_id=user_progress['current_scene_id'],
        story_id=story_id,
        user_progress=user_progress
    )

    logger.info(f'AJRM - scene_data:{scene_data}')

    # Get NPC info
    npcs_info = []
    for npc_id in scene_data.get('npcs_present', []):
        npc = await engine.npc_manager.get_npc(npc_id)
        if npc:
            npcs_info.append({'npc_id': npc['npc_id'], 'name': npc['name']})
    scene_data['npcs_info'] = npcs_info

    # Get items info
    items_info = []
    for item_id in scene_data.get('items_available', []):
        item = await engine.item_manager.get_item(item_id)
        if item:
            items_info.append({'item_id': item['item_id'], 'name': item['name'], 'description': item['description']})
    scene_data['items_info'] = items_info

    logger.info(f'AJRM2 - scene_data:{scene_data}')

    await show_scene(message, state, scene_data, pool)
    #await _send_scene_description(message, scene_data)
    #await _send_scene_actions(message, scene_data)


def ______________finishings(): pass
@story_router.callback_query(F.data.startswith("story_finish_scene:"))
async def callback_finish_scene(callback: types.CallbackQuery, state: FSMContext):
    """
    Пользователь хочет завершить сцену вручную
    """

    scene_id = int(callback.data.split(":")[1])

    data = await state.get_data()
    story_id = data['story_id']
    user_id = callback.message.chat.id

    # Показать подтверждение
    text = "Are you sure you want to finish this scene?\n\n"
    text += "⚠️ Any incomplete objectives will be marked as completed automatically."

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✅ Yes, finish", callback_data=f"story_finish_confirm:{scene_id}"),
        InlineKeyboardButton("❌ No, continue", callback_data="story_cancel")
    )

    await callback.message.edit_text(text, reply_markup=keyboard)


@story_router.callback_query(F.data.startswith("story_finish_confirm:"))
async def callback_finish_confirm(callback: types.CallbackQuery, state: FSMContext):
    """
    Подтверждение завершения сцены
    """

    scene_id = int(callback.data.split(":")[1])

    data = await state.get_data()
    story_id = data['story_id']
    user_id = callback.message.chat.id

    # TODO: Автоматически завершить все objectives
    # TODO: Показать резюме сцены
    # TODO: Перейти к следующей сцене

    await callback.message.edit_text("🎉 Scene completed!")

    # Переход к следующей сцене
    await show_next_scene(callback.message, state, story_id, scene_id)


@story_router.callback_query(F.data == "next_scene")
async def callback_next_scene(callback: types.CallbackQuery, state: FSMContext, pool):
    """Переход к следующей сцене"""

    await callback.answer()

    data = await state.get_data()
    story_id = data.get('task8_story_id')
    current_scene_id = data.get('current_scene_id')
    user_id = callback.message.chat.id

    # Проверка данных
    if not story_id or not current_scene_id:
        await callback.message.answer("❌ Error: Story or scene not found")
        return

    await callback.message.answer("⏳ Loading next scene...")

    try:
        # ✅ Используем централизованную функцию
        engine = InteractiveStoryEngine(pool, user_id)
        result = await engine.proceed_to_next_scene(
            user_id=user_id,
            story_id=story_id,
            current_scene_id=current_scene_id
        )

        # Проверка успешности
        if not result['success']:
            error_msg = result.get('error', 'Unknown error')
            await callback.message.answer(f"❌ Error: {error_msg}")
            return

        # ✅ Проверка концовки
        '''
        if result['is_story_ending']:
            await _show_story_ending(
                callback.message,
                state,
                pool,
                story_id,
                result['ending_type']
            )
            return
        '''

        # Обновить state
        next_scene_id = result['next_scene_id']
        await state.update_data(
            current_scene_id=next_scene_id,
            pending_next_scene_id=None  # Очистить
        )

        # ✅ Уже обогащена NPC в proceed_to_next_scene
        next_scene_data = result['next_scene_data']

        # Показать следующую сцену
        await show_scene(callback.message, state, next_scene_data, pool)

    except Exception as e:
        logger.error(f"Error loading next scene: {e}", exc_info=True)
        await callback.message.answer(f"❌ Error loading next scene")


@story_router.callback_query(F.data.startswith("t8_pause"))
async def callback_pause(callback, state, pool):
    """Skip story"""
    user_id = callback.message.chat.id


    if callback.data[0:9] == 't8_pause:':
        story_id = int(callback.data.split(":")[1])

        # Показываем "генерируем отчет..."
        wait_msg = await callback.message.answer(
            "📊 Анализирую твои результаты...",
            parse_mode=ParseMode.HTML
        )

        try:
            # ========================================
            # ГЛАВНОЕ ИЗМЕНЕНИЕ: Генерируем отчет
            # ========================================
            report = await generate_story_report(user_id, story_id, pool)

            # Удаляем сообщение "загрузка"
            await wait_msg.delete()

            if story_id == 21:
                btn_text = 'Узнать, что дальше →'
                clbck_data = "vB_st2"
            else:
                btn_text = myN.fCSS('menu')
                clbck_data = 'menu'


            # Кнопки после отчета
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=btn_text, callback_data=clbck_data))

            # Отправляем отчет пользователю
            await callback.message.answer(
                report['text'],
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )

            # Логируем успешное завершение истории
            pool_base, pool_log = pool
            import fpgDB as pgDB
            await pgDB.fExec_LogQuery(pool_log, user_id, f"story_completed_with_report|story:{story_id}")

        except ValueError as e:
            # Если нет сообщений пользователя в истории
            await wait_msg.delete()
            logger.warning(f"No messages found for story report: user {user_id}, story {story_id}")

            # Показываем упрощенную версию без отчета
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text='✔️ Да', callback_data="menu"))
            builder.add(types.InlineKeyboardButton(text='❌ Нет', callback_data=f"task8_continue:{story_id}"))
            builder.adjust(2)

            import mynaming as myN
            str_Msg = f"{myN.fCSS('pause_txt')}?"
            await callback.message.answer(
                str_Msg,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )

        except Exception as e:
            # Любая другая ошибка
            await wait_msg.delete()
            logger.error(f"Error generating story report: {e}", exc_info=True)

            await callback.message.answer(
                "❌ Произошла ошибка при создании отчёта. Попробуй позже.",
                parse_mode=ParseMode.HTML
            )

            # Fallback к старому поведению
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text='✔️ Завершить', callback_data="menu"))
            builder.add(types.InlineKeyboardButton(text='❌ Продолжить', callback_data=f"task8_continue:{story_id}"))
            builder.adjust(2)

            await callback.message.answer(
                "Что дальше?",
                reply_markup=builder.as_markup()
            )
        '''
        story_id = int(callback.data.split(":")[1])
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text='✔️Yes', callback_data="menu"))
        builder.add(types.InlineKeyboardButton(text='❌ No', callback_data=f"task8_continue:{story_id}"))
        builder.adjust(2)
        str_Msg = f"{myN.fCSS('pause_txt')}?"
        await callback.message.answer(str_Msg,  reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        '''
        # TODO: Complete activity
        #await state.clear()
        #await callback.answer()
    elif callback.data[-1] == 'y':
        user_data = await state.get_data()
        lesson_id = user_data['task8_lesson_id']
        logger.info(f'-------------------->>>>>>>>>>lesson_id:{lesson_id}')
        activity_id = user_data['task8_activity_id']
        logger.info(f'-------------------->>>>>>>>>>activity_id:{activity_id}')
        if not activity_id or not lesson_id:        #получаем из бд
            active_module = await get_active_module(pool, user_id)
            logger.info(f'-------------------->>>>>>>>>>active_module:{active_module}')
            if not active_module: pass
            module_id = active_module['module_id']
            logger.info(f'-------------------->>>>>>>>>>module_id:{module_id}')
            progress_manager = ProgressManager(pool)
            lesson_id = await progress_manager.get_lesson_by_status(user_id, module_id, 'in_progress')
            logger.info(f'-------------------->>>>>>>>>>lesson_id:{lesson_id}')
            lesson_progress = await progress_manager.get_or_create_lesson_progress(user_id, lesson_id)
            activity_id = lesson_progress['current_activity_id']
            logger.info(f'-------------------->>>>>>>>>>activity_id:{activity_id}')
            pass
        await complete_activity(callback.message, state, pool, user_id, lesson_id, activity_id)



def ____________show_scene(): pass




async def show_scene(
        message: types.Message,
        state: FSMContext,
        scene_data: dict,
        pool=None  # Добавляем pool для создания DialogueEngine
):
    """Показать сцену пользователю  is_ending """
    await state.set_state(myState.task8_story_active)

    user_id = message.chat.id
    user_data = await state.get_data()
    #story_id = user_data.get('task8_story_id')
    story_id = scene_data.get('story_id')
    scene_id = scene_data.get('scene_id')

    # 1. Название и описание локации
    text = f"📍 <b>{scene_data['scene_name']}</b>\n\n"
    text += scene_data['location_description']

    # Перевод локации
    if scene_data.get('location_description_trs'):
        trs = scene_data['location_description_trs']
        if isinstance(trs, str):
            trs = json.loads(trs)
        translation = trs.get('ru', '') if isinstance(trs, dict) else ''
        if translation:
            text += f"\n<blockquote expandable='true'><tg-spoiler>{translation}</tg-spoiler></blockquote>"

    # 2. Цель сцены
    objective_text = f"\n\n🎯 <b>Objectives:</b> {scene_data['objective']}"

    if scene_data.get('objective_trs'):
        trs = scene_data['objective_trs']
        if isinstance(trs, str):
            trs = json.loads(trs)
        obj_translation = trs.get('ru', '') if isinstance(trs, dict) else ''
        if obj_translation:
            objective_text += f"\n<blockquote expandable='true'><tg-spoiler>{obj_translation}</tg-spoiler></blockquote>"

    # 3. Objectives checklist (используем DialogueEngine)

    # 4. Список NPC для текста
    npcs_info = scene_data.get('npcs_info', [])


    str_npc_list = ''
    if npcs_info:
        #for i, npc in enumerate(npcs_info, start=1):
        #    str_npc_list += f'{fGetEmodjiNum(i)} {npc["name"]}\n'
        str_npc_list = ', '.join(
            f'{fGetEmodjiNum(i)} {npc["name"]}'
            for i, npc in enumerate(npcs_info, start=1)
        )

    # ✅ ДОБАВИТЬ СЮДА - ПЕРЕД get_scene_objectives_status:
    # Пересчитать objectives перед показом сцены
    if pool and story_id and scene_id:
        try:
            dialogue_engine = DialogueEngine(pool, user_id)

            # Пересчитываем все objectives
            await dialogue_engine.check_objective_completion(
                scene_id=scene_id,
                story_id=story_id,
                user_id=user_id,
                recent_interaction={
                    'interaction_type': 'scene_display',
                    'force_recheck_items': True  # Маркер что нужно проверить items
                }
            )
        except Exception as e:
            logger.error(f"Error rechecking objectives: {e}", exc_info=True)

    # 5. service (key/legend)       #showscene
    is_show_pause = await _get_msg_cnt(state)  # Update actions count
    objective_status_text, is_min_objectives_met, _ = await get_scene_objectives_status(pool, user_id, story_id, scene_id)
    str_key = ''
    if is_show_pause or is_min_objectives_met:
        str_key = (
            f'🗝<blockquote expandable="true">\n\n'
        )
        if is_show_pause:
            text_skip = f"{myN.fCSS('pause')} - {myN.fCSS('pause_txt')}" if is_show_pause else ''
            str_key = f'{str_key}{text_skip}\n'
        if is_min_objectives_met:
            txt_completed = (
                f'{myN.fCSS("next_scene")} - {myN.fCSS("next_scene_txt")}'
            )
            str_key = f'{str_key}{txt_completed}'
        str_key = f'{str_key}</blockquote>'

    # ====================================================================
    # ПРОВЕРИТЬ ЗАВЕРШЕНИЕ СЦЕНЫ И ENDING
    # ====================================================================
    is_ending_scene = scene_data.get('is_ending', False)
    show_ending_message = False
    final_message = None
    scene_reveals = []

    # Если objectives выполнены И это ending scene
    if is_min_objectives_met and is_ending_scene:
        logger.info(f"=== Scene {scene_id} is completed ending scene ===")

        # Получить pool_base
        #pool_base = pool[0] if isinstance(pool, tuple) else pool

        # Получить final message
        from .story_helpers import (
            get_story_final_message,
            get_scene_important_reveals,
            mark_story_completed
        )

        final_message = await get_story_final_message(pool, story_id)
        scene_reveals = await get_scene_important_reveals(pool, scene_id)

        # Отметить историю как завершенную
        await mark_story_completed(pool, user_id, story_id)

        show_ending_message = True

        logger.info(f"=== Story {story_id} marked as completed for user {user_id} ===")

    # 5. Формируем финальное сообщение
    # Если это ending - добавить revelation и final message
    if show_ending_message:
        ending_text = "\n\n"

        # Scene reveals
        if scene_reveals:
            ending_text += "🔮 <b>The Truth Revealed:</b>\n"
            for reveal in scene_reveals:
                ending_text += f"• <i>{reveal}</i>\n"
            ending_text += "\n"

        # Final message
        if final_message:
            ending_text += f"📖 {final_message}\n\n"

        ending_text += "🎉 <b>Story completed!</b>\n\n"

        str_msg = (
            f'{text}'
            f'{objective_text}\n'
            f'{objective_status_text}\n\n'
            f'{ending_text}'
        )
    else:
        # Обычная сцена
        str_msg = (
            f'{text}'
            f'{objective_text}\n'
            f'{objective_status_text}\n\n'
            f'What is your next step?\n'
            f'💬 Talk to: {str_npc_list}\n'
            f'or {myN.fCSS("look")}\n'
            f'or check {myN.fCSS("inv")}\n'
            #f'{str_key}'
        )

    logger.info(f'---------------is_ending_scene:{is_ending_scene}')

    # 6. Создаем клавиатуру
    keyboard = await _build_scene_keyboard(
        npcs_info,
        story_id,
        is_show_pause=is_show_pause,
        is_scene_completed=is_min_objectives_met,
        is_ending=is_ending_scene
    )



    msg_p = await message.answer(str_msg, reply_markup=keyboard, parse_mode="HTML")

    await state.update_data(
        msg_id=msg_p.message_id,
        npcs_info=npcs_info,
        #str_npc_list=str_npc_list,
        current_scene_id=scene_id,
        task8_story_id=story_id,
        task8_active_npc_id=None
    )

    user_data = await state.get_data()
    tmp = user_data['npcs_info']


    #test
    npc_id = user_data['task8_active_npc_id']
    npcs_info = user_data['npcs_info']
    logger.info(f'-------------show_scene--------npc_id:{npc_id}|npcs_info:{npcs_info}')

    # обучающий блок
    '''
    if story_id == 21:
        text = "test1"
        await callback.answer(text, show_alert=True, parse_mode="HTML")
        text = "test2"
        await callback.answer(text, show_alert=True, parse_mode="HTML")
        text = "test3"
        await callback.answer(text, show_alert=True, parse_mode="HTML")
        # pass    #AJRM
    '''


async def _build_scene_keyboard(
        npcs_info: list,
        story_id,
        is_show_pause=False,
        is_scene_completed=False,
        is_ending=False
) -> InlineKeyboardMarkup:
    """
    Создать клавиатуру для сцены

    Args:
        npcs_info: Список NPC с данными [{"npc_id": int, "name": str}, ...]

    Returns:
        InlineKeyboardMarkup с кнопками NPC и действий
    """
    logger.info(f'---------------is_ending:{is_ending}')
    builder = InlineKeyboardBuilder()

    #если история завершилась, то кнопка только одна - exit
    str4PauseBtn = ''
    str4_clbck_data = f"t8_pause:{story_id}"
    layout = []     # Расчет layout

    if is_ending and is_scene_completed and story_id == 21:
        str4PauseBtn = myN.fCSS('exit')
        #if story_id == 21:  str4_clbck_data = 'vB_st2'
        builder.add(InlineKeyboardButton(text=str4PauseBtn, callback_data=str4_clbck_data))
        layout.append(1)
    else:
        npc_count = len(npcs_info)
        # Добавляем кнопки для каждого NPC
        if npc_count > 0:
            for i, npc in enumerate(npcs_info, start=1):
                builder.add(
                    InlineKeyboardButton(
                        text=f'{fGetEmodjiNum(i)} {npc["name"]}',
                        callback_data=f"talk:{npc['npc_id']}"
                    )
                )

        # Кнопки действий
        builder.add(InlineKeyboardButton(text=myN.fCSS('look'), callback_data="look_around"))
        builder.add(InlineKeyboardButton(text=myN.fCSS('inv'), callback_data="check_inventory"))
        builder.add(InlineKeyboardButton(text='🗝', callback_data="story_key_s"))


        bool4NextSceneBtn = False


        if is_show_pause:
            str4PauseBtn = myN.fCSS('pause')
            if story_id == 21: str4PauseBtn = ''
        if is_scene_completed:
            if is_ending:
                str4PauseBtn = myN.fCSS('exit')
                #if story_id == 21:  str4_clbck_data='vB_st2'

            else:
                bool4NextSceneBtn = True    # Обычная сцена - кнопка перехода

        if str4PauseBtn:
            builder.add(InlineKeyboardButton(text=str4PauseBtn, callback_data=str4_clbck_data)) #f"t8_pause:{story_id}"
        if bool4NextSceneBtn:
            builder.add(types.InlineKeyboardButton(text=myN.fCSS('next_scene'), callback_data="next_scene"))



        # NPC кнопки по 2 в ряд
        if npc_count > 0:
            full_rows = npc_count // 2
            remainder = npc_count % 2

            for _ in range(full_rows):
                layout.append(2)
            if remainder > 0:
                layout.append(remainder)

        # Look around и Inventory в один ряд
        layout.append(2)
        layout.append(1)    #key

        # Pause и/или next_scene в один ряд
        if is_show_pause and is_scene_completed:
            layout.append(2)
        elif is_show_pause or is_scene_completed:
            layout.append(1)

    builder.adjust(*layout)

    return builder.as_markup()



@story_router.callback_query(F.data == "look_around")
async def callback_look_around(callback: types.CallbackQuery, state: FSMContext, pool):
    """
    Пользователь осматривается в поисках предметов
    """
    await state.set_state(myState.task8_story_active)
    data = await state.get_data()
    story_id = data['task8_story_id']
    scene_id = data['current_scene_id']
    user_id = callback.message.chat.id


    # Получаем discoverable items в сцене
    items = await _get_discoverable_items(pool, scene_id, story_id, user_id)
    #logger.info(f'----------->>>>>>>>>items"{items}')
    if not items:
        text = "🔍 You look around carefully, but don't find anything interesting."
    else:
        text = "🔍 <b>Looking around...</b>\n\n"
        text += "You notice:\n"

        for item in items:
            location_details = item.get('location_details', {})
            desc = location_details.get('location_description', '')
            text += f"• {desc}\n"

        text += "\n<i>What do you want to do?</i>"

    builder = InlineKeyboardBuilder()

    # Кнопки для каждого item
    for item in items:
        # Получить acquisition_conditions для определения типа
        acquisition_conditions = item.get('acquisition_conditions', {})

        # Парсим JSON если нужно
        if isinstance(acquisition_conditions, str):
            import json
            acquisition_conditions = json.loads(acquisition_conditions) if acquisition_conditions else {}

        if acquisition_conditions is None:
            acquisition_conditions = {}

        condition_type = acquisition_conditions.get('type')
        requirements = acquisition_conditions.get('requirements', {})

        # Определяем тип кнопки
        if condition_type == 'container':
            # Для контейнеров - кнопка "Use item on"
            required_item = requirements.get('required_item', 'key')
            button_text = f"🔓 Use {required_item} on {item['name']}"
            callback_data = f"use_item_on:{item['item_id']}"
        else:
            # Для обычных items - кнопка "Search"
            button_text = f"🔎 Search {item['name']}"
            callback_data = f"search_item:{item['item_id']}"

        builder.row(InlineKeyboardButton(
            text=button_text,
            callback_data=callback_data
        ))

    # Кнопка назад в отдельном ряду
    builder.row(InlineKeyboardButton(text=myN.fCSS('back'),callback_data=f"task8_continue:{story_id}"))

    await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

    '''
    #проверка выполнения objective с типом action
    dialogue_engine = DialogueEngine(pool, user_id)

    scene_completed = await dialogue_engine.check_objective_completion(
        scene_id=scene_id,
        story_id=story_id,
        user_id=user_id,
        recent_interaction={
            'interaction_type': 'action',
            'action': 'look_around'
        }
    )

    logger.info(f'=== LOOK_AROUND: scene_completed={scene_completed} ===')
    '''
    # Обновляем objectives в БД (если нужно) без проверки завершения
    dialogue_engine = DialogueEngine(pool, user_id)

    await dialogue_engine.check_objective_completion(
        scene_id=scene_id,
        story_id=story_id,
        user_id=user_id,
        recent_interaction={
            'interaction_type': 'action',
            'action': 'look_around'
        }
    )


async def _get_revealed_items_for_user(
        pool_base,
        user_id: int,
        story_id: int,
        scene_id: int
) -> List[str]:
    """Получить раскрытые items"""

    query = """
        SELECT c_scene_progress
        FROM t_story_user_progress
        WHERE c_user_id = $1 AND c_story_id = $2
    """

    result = await pgDB.fExec_SelectQuery_args(pool_base, query, user_id, story_id)

    if not result:
        return []

    scene_progress = result[0][0]
    if isinstance(scene_progress, str):
        scene_progress = json.loads(scene_progress)

    if not scene_progress:
        return []

    scene_key = f"scene_{scene_id}"
    return scene_progress.get(scene_key, {}).get('revealed_items', [])

async def _get_discoverable_items(pool, scene_id: int, story_id: int, user_id: int) -> List[Dict]:
    """
    Получить items которые можно найти в сцене
    """
    pool_base, pool_log = pool
    # ✅ FIX: Сначала проверяем есть ли вообще items в сцене
    check_query = """
            SELECT c_items_available
            FROM t_story_scenes
            WHERE c_scene_id = $1 AND c_story_id = $2
        """

    check_result = await pgDB.fExec_SelectQuery_args(
        pool_base,
        check_query,
        scene_id,
        story_id
    )

    logger.info(f'----------->>>>>>>>>check_result"{check_result}')

    if not check_result:
        logger.warning(f"Scene {scene_id} not found")
        return []

    items_available = check_result[0][0]

    # Парсим если строка
    if isinstance(items_available, str):
        items_available = json.loads(items_available)

    # Если нет items в сцене - сразу возвращаем пустой список
    if not items_available or len(items_available) == 0:
        logger.info(f"No items available in scene {scene_id}")
        return []

    # ⭐ НОВОЕ: Получаем revealed_items
    revealed_items = await _get_revealed_items_for_user(
        pool_base, user_id, story_id, scene_id
    )
    logger.info(f"Revealed items: {revealed_items}")

    # ✅ FIX: Используем = ANY() только если массив не пустой
    query = """
            SELECT 
                i.c_item_id,
                i.c_name,
                i.c_description,
                i.c_location_type,
                i.c_location_details,
                i.c_acquisition_conditions
            FROM t_story_items i
            WHERE i.c_story_id = $1
              AND i.c_location_type IN ('hidden', 'visible')
              AND i.c_item_id = ANY($2::int[])
        """

    result = await pgDB.fExec_SelectQuery_args(
        pool_base,
        query,
        story_id,
        items_available  # Передаём массив напрямую
    )

    if not result:
        return []

    items = []
    for row in result:
        location_details = row[4]
        if isinstance(location_details, str):
            location_details = json.loads(location_details)

        if location_details is None:
            location_details = {}

        # Проверить  visible ИЛИ revealed
        item_name = row[1]
        visible_on_look = location_details.get('visible_on_look_around', True)
        is_discoverable = visible_on_look or (item_name in revealed_items)

        if is_discoverable:  # ⬅️ ИЗМЕНЕНО!
            # Проверить не получен ли уже item
            from ..story.managers.item_manager import ItemManager
            item_manager = ItemManager(pool)

            inventory = await item_manager.get_user_inventory(user_id, story_id)
            item_ids_in_inventory = [item['item_id'] for item in inventory]

            if row[0] not in item_ids_in_inventory:
                items.append({
                    'item_id': row[0],
                    'name': item_name,  # ⬅️ Используем переменную
                    'description': row[2],
                    'location_type': row[3],
                    'location_details': location_details,
                    'acquisition_conditions': row[5]
                })
                logger.debug(f"✅ Item '{item_name}' discoverable")
        else:
            logger.debug(f"🔒 Item '{item_name}' hidden")  # ⬅️ НОВОЕ!

    return items


async def _get_revealed_items_for_user(
        pool_base,
        user_id: int,
        story_id: int,
        scene_id: int
) -> List[str]:
    """
    Получить список раскрытых items для пользователя в текущей сцене

    Returns:
        List of item names that were revealed through dialogue
        Example: ["milk", "cheese", "eggs"]
    """

    query = """
        SELECT c_scene_progress
        FROM t_story_user_progress
        WHERE c_user_id = $1 AND c_story_id = $2
    """

    result = await pgDB.fExec_SelectQuery_args(
        pool_base,
        query,
        user_id,
        story_id
    )

    if not result:
        return []

    scene_progress = result[0][0]
    if isinstance(scene_progress, str):
        scene_progress = json.loads(scene_progress)

    if not scene_progress:
        return []

    # Получить revealed_items для текущей сцены
    scene_key = f"scene_{scene_id}"
    revealed_items = scene_progress.get(scene_key, {}).get('revealed_items', [])

    logger.debug(f"Revealed items for user {user_id} in scene {scene_id}: {revealed_items}")

    return revealed_items

@story_router.callback_query(F.data.startswith("search_item:"))
async def callback_search_item(callback: types.CallbackQuery, state: FSMContext, pool):
    """
    Пользователь ищет/получает item
    """

    item_id = int(callback.data.split(":")[1])

    await state.set_state(myState.task8_story_active)

    data = await state.get_data()
    story_id = data.get('task8_story_id')
    user_id = callback.message.chat.id

    if not story_id:
        await callback.answer("❌ Error: Story not found", show_alert=True)
        return

    try:
        # Получаем информацию об item
        from ..story.managers.item_manager import ItemManager
        item_manager = ItemManager(pool)

        item = await item_manager.get_item(item_id)

        if not item:
            await callback.answer("❌ Item not found", show_alert=True)
            return

        # Проверяем можно ли получить этот item
        can_acquire, reason = await item_manager.can_acquire_item(
            item_id, user_id, story_id, data.get('current_scene_id')
        )

        if not can_acquire:
            text = f"🔒 <b>{item['name']}</b>\n\n"
            text += f"You cannot take this item yet.\n\n"
            text += f"<i>{reason}</i>"

            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text=myN.fCSS('back'),callback_data="story_back_to_scene"))

            await callback.message.edit_text(
                text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )
            await callback.answer()
            return

        # Добавляем item в инвентарь
        await item_manager.add_item_to_inventory(user_id, story_id, item_id)

        # Обновляем статус objective если это item objective
        from ..story.engines.dialogue_engine import DialogueEngine
        dialogue_engine = DialogueEngine(pool, user_id)

        scene_id = data.get('current_scene_id')
        if scene_id:
            # Пересчитываем objectives (item получен!)
            await dialogue_engine.check_objective_completion(
                scene_id, story_id, user_id,
                recent_interaction={
                    'interaction_type': 'item_obtained',
                    'item_id': item_id,
                    'item_name': item['name']
                }
            )

        # Показываем успех
        text = f"✨ <b>You found: {item['name']}!</b>\n\n"
        text += f"{item['description']}\n\n"
        text += f"<i>The item has been added to your inventory.</i>"

        if item.get('description_trs', {}).get('ru'):
            text += f"\n\n<blockquote expandable='true'>{item['description_trs']['ru']}</blockquote>"

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(
            text="Forward >>",
            callback_data=f"task8_continue:{story_id}"
        ))

        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

        await callback.answer("✨ Item obtained!")

    except Exception as e:
        logger.error(f"Error searching item: {e}", exc_info=True)
        await callback.answer("❌ Error getting item", show_alert=True)



@story_router.callback_query(F.data.startswith("use_item_on:"))
async def callback_use_item_on(callback: types.CallbackQuery, state: FSMContext, pool):
    """
    Использовать item на контейнере (например, Golden Key на Ancient Chest)
    """

    container_id = int(callback.data.split(":")[1])
    await state.set_state(myState.task8_story_active)

    data = await state.get_data()
    story_id = data.get('task8_story_id')
    scene_id = data.get('current_scene_id')
    user_id = callback.message.chat.id

    if not story_id:
        await callback.answer("❌ Error: Story not found", show_alert=True)
        return

    logger.info(f"=== USE_ITEM_ON: container_id={container_id}, user_id={user_id} ===")

    try:
        # Получить ItemManager
        from ..story.managers.item_manager import ItemManager
        item_manager = ItemManager(pool)

        # Получить информацию о контейнере
        container = await item_manager.get_item(container_id)

        if not container:
            await callback.answer("❌ Container not found", show_alert=True)
            return

        logger.info(f"=== Container: {container['name']} ===")

        # Проверить можно ли использовать item на контейнере
        can_use, message, required_item_id = await item_manager.can_use_item_on_container(
            container_id, user_id, story_id
        )

        logger.info(f"=== can_use={can_use}, message={message}, required_item_id={required_item_id} ===")

        if not can_use:
            # Нельзя использовать - показать причину
            acquisition_conditions = container.get('acquisition_conditions', {})
            if isinstance(acquisition_conditions, str):
                import json
                acquisition_conditions = json.loads(acquisition_conditions) if acquisition_conditions else {}

            requirements = acquisition_conditions.get('requirements', {})
            required_item_name = requirements.get('required_item', 'key')

            text = f"🔒 <b>{container['name']}</b>\n\n"
            text += f"{container.get('description', 'A locked container.')}\n\n"
            text += f"<i>{message}</i>\n\n"
            text += f"💡 You need: <b>{required_item_name}</b>"

            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text=myN.fCSS('back'),callback_data="look_around"))

            await callback.message.edit_text(
                text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )
            await callback.answer()
            return

        # ✅ Можно использовать - открываем контейнер!
        logger.info(f"=== Opening container {container['name']} ===")

        # Получить имя использованного item
        acquisition_conditions = container.get('acquisition_conditions', {})
        if isinstance(acquisition_conditions, str):
            import json
            acquisition_conditions = json.loads(acquisition_conditions) if acquisition_conditions else {}

        requirements = acquisition_conditions.get('requirements', {})
        required_item_name = requirements.get('required_item', 'key')

        # Проверить objectives (использование item может быть целью)
        from ..story.engines.dialogue_engine import DialogueEngine
        dialogue_engine = DialogueEngine(pool, user_id)

        scene_completed = await dialogue_engine.check_objective_completion(
            scene_id, story_id, user_id,
            recent_interaction={
                'interaction_type': 'item_use',
                'item_used': required_item_name,
                'item_used_id': required_item_id,
                'target': container['name'],
                'target_id': container_id
            }
        )

        # ✅ Можно использовать - открываем контейнер!
        logger.info(f"=== Opening container {container['name']} ===")

        # ====================================================================
        # ПОЛУЧИТЬ СОДЕРЖИМОЕ КОНТЕЙНЕРА
        # ====================================================================

        container_contents = await item_manager.get_container_contents(container_id, story_id)

        logger.info(f"=== Container contents: {container_contents} ===")

        # ====================================================================
        # ДОБАВИТЬ ITEMS ИЗ КОНТЕЙНЕРА В ИНВЕНТАРЬ
        # ====================================================================

        items_inside = container_contents.get('items_inside', [])
        items_obtained = []

        if items_inside:
            logger.info(f"=== Adding {len(items_inside)} items from container ===")
            items_obtained = await item_manager.add_items_from_container(
                user_id, story_id, items_inside
            )

        # ====================================================================
        # ПОЛУЧИТЬ REVELATION TEXT, SCENE REVEALS, FINAL MESSAGE
        # ====================================================================

        # Revelation text из контейнера
        revelation_text = container_contents.get('revelation_text')
        custom_message = container_contents.get('custom_message')

        # Scene reveals (если trigger включен)
        scene_reveals = []
        if container_contents.get('trigger_scene_reveal'):
            scene_reveals = await get_scene_important_reveals(pool, scene_id)
            logger.info(f"=== Got {len(scene_reveals)} scene reveals ===")

        # Final message (если trigger включен)
        final_message = None
        if container_contents.get('trigger_final_message'):
            final_message = await get_story_final_message(pool, story_id)
            logger.info(f"=== Got final message: {bool(final_message)} ===")

        # ====================================================================
        # ПРОВЕРИТЬ OBJECTIVES
        # ====================================================================

        # Получить имя использованного item для objectives
        acquisition_conditions = container.get('acquisition_conditions', {})
        if isinstance(acquisition_conditions, str):
            import json
            acquisition_conditions = json.loads(acquisition_conditions) if acquisition_conditions else {}

        requirements = acquisition_conditions.get('requirements', {})
        required_item_name = requirements.get('required_item', 'key')


        # Обновить objectives в БД
        from ..story.engines.dialogue_engine import DialogueEngine
        dialogue_engine = DialogueEngine(pool, user_id)

        await dialogue_engine.check_objective_completion(
            scene_id, story_id, user_id,
            recent_interaction={
                'interaction_type': 'item_use',
                'item_used': required_item_name,
                'item_used_id': required_item_id,
                'target': container['name'],
                'target_id': container_id
            }
        )

        # Сформировать текст с revelation
        text = f"✨ <b>You used {required_item_name} on {container['name']}!</b>\n\n"
        text += f"🔓 The lock clicks open...\n\n"

        # Добавить revelation message
        revelation_message = await format_revelation_message(
            revelation_text=revelation_text,
            items_obtained=items_obtained,
            scene_reveals=scene_reveals,
            final_message=final_message,
            custom_message=custom_message
        )

        if revelation_message:
            text += revelation_message

        # ВСЕГДА только кнопка Back - show_scene решит про завершение
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text=myN.fCSS('back'), callback_data=f"task8_continue:{story_id}"))    #"« Back to scene"

        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"=== ERROR in use_item_on: {e} ===", exc_info=True)
        await callback.answer("❌ Error occurred", show_alert=True)








def ______________dialog(): pass
# ============================================================================
# Dialogue handlers
# ============================================================================
@story_router.callback_query(F.data.startswith("talk:"), StateFilter(myState.task8_story_active))       #appr
async def callback_talk(callback: types.CallbackQuery, state: FSMContext, pool):
    """Start dialogue with NPC"""

    npc_id = int(callback.data.split(":")[1])
    await state.update_data(task8_active_npc_id=npc_id)
    #await state.set_state(myState.task8_story_dialogue)



    npc_manager = NPCManager(pool)
    npc = await npc_manager.get_npc(npc_id)



    await callback.message.answer(
        f"💬 <b>Talking to {npc['name'] if npc else 'NPC'}</b>\n\nSend or text your message.",
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@story_router.message((F.voice | (F.text & ~F.text.startswith('/'))), StateFilter(myState.task8_story_active))
async def media_talk(message, state, pool):
    """Process dialogue message"""
    pool_base, pool_log = pool

    logger.info('-------------media_talk')

    user_id = message.chat.id
    user_data = await state.get_data()
    scene_id = user_data['current_scene_id']
    story_id = user_data['task8_story_id']

    npc_id = user_data.get('task8_active_npc_id')

    # ====================================================================
    # ✅ ПРОВЕРКА active_npc_id
    # ====================================================================
    if not npc_id:
        npcs_info = user_data.get('npcs_info', [])

        if not npcs_info or len(npcs_info) == 0:
            # ❌ Сценарий 2: Нет NPC - показать уведомление и ВЫЙТИ
            await message.reply(
                "🤷‍♂️ <i>No one to talk to here. Try</i> 🔍 <i>Look around instead.</i>",
                parse_mode="HTML"
            )
            logger.info(f"User {user_id} tried to talk with no NPCs in scene {scene_id}")
            return

        # ✅ Сценарий 1: Есть NPC - берем первого
        npc_id = npcs_info[0]['npc_id']
        await state.update_data(task8_active_npc_id=npc_id)

        npc_name = npcs_info[0]['name']
        await message.reply(
            f"💬 <i>Talking to <b>{npc_name}</b>...</i>",
            parse_mode="HTML"
        )
        logger.info(f"Auto-selected NPC {npc_id} ({npc_name}) for user {user_id}")

    # ====================================================================
    # СТАНДАРТНАЯ ЛОГИКА
    # ====================================================================
    npcs_info = user_data['npcs_info']
    logger.info(f'-------------media_talk--------npc_id:{npc_id}|npcs_info:{npcs_info}')

    msg_id = user_data.get('msg_id')
    await _del_prev_kb(msg_id, message_obj=message)

    input_type = 'voice' if message.voice else 'text'

    if message.voice:
        user_text = await myF.afVoiceToTxt(message, pool, user_id)
        input_data = user_text if user_text else "[Voice]"
    else:
        user_text = ' '.join(message.text.split())
        input_data = user_text

    await state.update_data(usertext=user_text)

    engine = InteractiveStoryEngine(pool, user_id)

    try:
        # stage 1 voice response
        # ----------------------------------------------------------------------------------------------------
        result, recent_interaction = await engine.process_user_input(
            story_id=story_id,
            input_type=input_type,
            input_data=input_data,
            target_npc_id=npc_id
        )

        # npc+tutor response
        text = ''
        voice_file = None
        npc_response = result.get('npc_response')
        if npc_response:
            response_text = npc_response['response']


            voice_file = await generate_npc_voice_message(
                pool=pool,
                user_id=user_id,
                story_id=story_id,
                npc_id=npc_id,
                text=response_text
            )

            text = f"💬 <b>{npc_response['npc_name']}</b>: "
            if npc_response.get('npc_action'):
                text += f"  (<i>{npc_response['npc_action']}</i>)"

            text += f"\n{npc_response['response']}"

            if npc_response.get('text_trs', {}).get('ru'):
                text += f"\n<blockquote expandable='true'><tg-spoiler>📝 {npc_response['text_trs']['ru']}</tg-spoiler></blockquote>"

            if npc_response.get('correction') and npc_response['correction'].lower() not in ['n/a', 'no corrections']:
                text += f"\n\n👨‍🏫 <b>Tutor:</b> <i>{npc_response['correction']}</i>"

            npc_gives_item = result.get('npc_gives_item')
            if npc_gives_item:
                text += f"\n\n🎁 <b>{npc_response['npc_name']} gave you: {npc_gives_item['item_name']}!</b>"
                if npc_gives_item.get('description'):
                    text += f"\n<i>{npc_gives_item['description']}</i>"



        # display msg
        str_Msg = (
            f'{text}\n\n'
            f'<b>💡 The objectives status is processing and will appear shortly...</b>'
        )

        # ОТПРАВКА: Голос + текст в caption
        if voice_file:

            try:
                with open(voice_file, 'rb') as ogg:
                    await message.answer_voice(
                        BufferedInputFile(ogg.read(), filename="voice.ogg"),
                        # caption='',
                        # reply_markup=builder.as_markup(),
                        parse_mode="HTML"
                    )


                voice_path = Path(voice_file)
                if 'sfx' not in str(voice_path):
                    # Это временный TTS файл - можно удалить
                    os.remove(voice_file)
                    logger.debug(f"Deleted temporary voice file: {voice_file}")
                else:
                    # Это предзаписанный звук из sfx/ - НЕ удалять
                    logger.debug(f"Kept sound effect file: {voice_file}")

                msg_p = await message.answer(str_Msg, parse_mode="HTML")    #reply_markup=builder.as_markup(),

            except Exception as e:
                logger.error(f"Error sending voice message: {e}", exc_info=True)
                msg_p = await message.answer(str_Msg, parse_mode="HTML")    #reply_markup=builder.as_markup(),
        else:
             msg_p = await message.answer(str_Msg, parse_mode="HTML")    #reply_markup=builder.as_markup(),

        #stage 2 narrator, objectives
        #----------------------------------------------------------------------------------------------------
        # narrator hints
        text_narrator = ''
        hint = result.get('narrator_hint')
        if hint:
            text_narrator = (
                f"\n\n🤔 \n"
                f"💭 <i>{hint['text']}</i>"
            )
            if hint.get('text_trs', {}).get('ru'):
                text_narrator += f"\n<blockquote expandable='true'>📝 {hint['text_trs']['ru']}</blockquote>"

        # ====================================================================
        # ✅ ПОЛУЧИТЬ is_ending ИЗ БД (динамически!)
        # ====================================================================
        query_is_ending = """
                    SELECT c_is_ending
                    FROM t_story_scenes
                    WHERE c_scene_id = $1 AND c_story_id = $2
                """
        result_ending = await pgDB.fExec_SelectQuery_args(pool_base, query_is_ending, scene_id, story_id)
        is_ending = result_ending[0][0] if result_ending else False

        logger.info(f"Scene {scene_id} is_ending: {is_ending}")

        _ = await engine.dialogue_engine.check_objective_completion(
            scene_id=scene_id,
            story_id=story_id,
            user_id=user_id,
            recent_interaction=recent_interaction
        )


        # service (key/legend)
        is_show_pause = await _get_msg_cnt(state)
        objective_status_text, is_min_objectives_met, _ = await get_scene_objectives_status(pool, user_id, story_id,
                                                                                         scene_id)
        objective_status_text = f'\n\n🎯 <b>Objectives:</b>\n{objective_status_text}\n'

        str_key = ''    #mediatalk
        if is_show_pause or is_min_objectives_met:
            str_key = (
                f'\n🗝<blockquote expandable="true">\n\n'
                f"{myN.fCSS('st_action')} - {myN.fCSS('st_action_txt')}\n"
                f"{myN.fCSS('inv')} - {myN.fCSS('inv_txt')}\n"
                f"{myN.fCSS('st_grammar')} - {myN.fCSS('st_grammar_txt')}\n"
            )
            if is_show_pause:
                text_skip = f"{myN.fCSS('pause')} - {myN.fCSS('pause_txt')}"
                str_key = f'{str_key}{text_skip}\n'
            if is_min_objectives_met:
                # ✅ Динамический текст в зависимости от is_ending
                if is_ending:
                    txt_completed = f'{myN.fCSS("exit")} - {myN.fCSS("exit_txt")}'
                else:
                    txt_completed = f'{myN.fCSS("next_scene")} - {myN.fCSS("next_scene_txt")}'
                str_key = f'{str_key}{txt_completed}'
            str_key = f'{str_key}</blockquote>'

        # display msg
        str_Msg = (
            #f'{text}\n\n'
            #f'<b>💡 Message update:</b>'
            f'{text_narrator}'
            f'{objective_status_text}'
            #f'{str_key}'
        )

        # ✅ ПЕРЕДАТЬ is_ending в клавиатуру
        builder = await _build_dialogue_keyboard(
            story_id=story_id,
            npc_id=npc_id,
            is_show_pause=is_show_pause,
            is_min_objectives_met=is_min_objectives_met,
            is_ending=is_ending  # ⬅️ ДОБАВЛЕНО!
        )

        msg_p = await msg_p.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode="HTML")
        '''
        # ОТПРАВКА: Голос + текст в caption
        if voice_file:
            from aiogram.types import BufferedInputFile
            try:
                with open(voice_file, 'rb') as ogg:
                    await message.answer_voice(
                        BufferedInputFile(ogg.read(), filename="voice.ogg"),
                        #caption='',
                        #reply_markup=builder.as_markup(),
                        parse_mode="HTML"
                    )
                import os
                from pathlib import Path

                voice_path = Path(voice_file)
                if 'sfx' not in str(voice_path):
                    # Это временный TTS файл - можно удалить
                    os.remove(voice_file)
                    logger.debug(f"Deleted temporary voice file: {voice_file}")
                else:
                    # Это предзаписанный звук из sfx/ - НЕ удалять
                    logger.debug(f"Kept sound effect file: {voice_file}")

                msg_p = await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode="HTML")

            except Exception as e:
                logger.error(f"Error sending voice message: {e}", exc_info=True)
                msg_p = await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode="HTML")
        else:
            msg_p = await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode="HTML")
        '''

        await state.update_data(
            msg_id=msg_p.message_id,
            str_Msg=str_Msg,
            is_show_pause=is_show_pause,
            is_min_objectives_met=is_min_objectives_met,
            is_ending=is_ending
        )


        if is_min_objectives_met:
            await _handle_story_completion(message, state, pool, result)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        await message.answer("❌ Error processing message.")


async def _build_dialogue_keyboard(
        story_id: int,
        npc_id: int,
        is_show_pause: bool,
        is_min_objectives_met: bool,
        is_ending: bool = False
) -> InlineKeyboardBuilder:
    """Построить клавиатуру для диалога"""
    builder = InlineKeyboardBuilder()

    #если история завершилась (is_ending), то только одна кнопка - exit
    str4PauseBtn = ''
    bool4NextSceneBtn = False
    str4_clbck_data = f"t8_pause:{story_id}"

    if is_ending and is_min_objectives_met and story_id == 21:
        str4PauseBtn = myN.fCSS('exit')  # ⬅️ Ending - Exit
        #if story_id == 21: str4_clbck_data = 'vB_st2'
        builder.add(InlineKeyboardButton(text=str4PauseBtn, callback_data=str4_clbck_data))
        layout = [1]
    elif story_id == 21:
        builder.add(InlineKeyboardButton(text=myN.fCSS('st_grammar'), callback_data=f"story_check_grammar"))
        layout = [1]
    else:

        builder.row(InlineKeyboardButton(text=myN.fCSS('back'),callback_data=f"task8_continue:{story_id}"))
        builder.add(InlineKeyboardButton(text=myN.fCSS('st_action'),callback_data=f"action_on_npc:{npc_id}"))
        builder.add(InlineKeyboardButton(text=myN.fCSS('inv'),callback_data="check_inventory"))
        builder.add(InlineKeyboardButton(text=myN.fCSS('st_grammar'), callback_data=f"story_check_grammar"))
        builder.add(InlineKeyboardButton(text='🗝', callback_data=f"story_key_d"))

        logger.info(f'dialogue_keyboard+++++++++++++>>>>>>>>>npc_id:{npc_id}')



        if is_show_pause:
            str4PauseBtn = myN.fCSS('pause')
            #if story_id == 21: str4PauseBtn = ''

        if is_min_objectives_met:
            if is_ending:
                str4PauseBtn = myN.fCSS('exit')  # ⬅️ Ending - Exit
                #if story_id == 21:  str4_clbck_data='vB_st2'

            else:
                bool4NextSceneBtn = True  # ⬅️ Обычная сцена - Next Scene

        if str4PauseBtn:
            builder.add(InlineKeyboardButton(
                text=str4PauseBtn,
                callback_data=str4_clbck_data       #f"t8_pause:{story_id}"
            ))
        if bool4NextSceneBtn:
            builder.add(InlineKeyboardButton(
                text=myN.fCSS('next_scene'),
                callback_data="next_scene"
            ))

        layout = [1]  # back
        #layout.append(2)  # action + inv
        layout.append(2)  # action + inv
        layout.append(2)  # grammar + key

        if is_show_pause and is_min_objectives_met:
            layout.append(2)
        elif is_show_pause or is_min_objectives_met:
            layout.append(1)
    builder.adjust(*layout)

    return builder



async def _handle_story_completion(message, state, pool, result):
    """Handle scene completion"""

    if result.get('story_completed'):
        ending_text = {
            'good': "🎉 Great ending!",
            'neutral': "👍 Story completed",
            'bad': "😔 Story ended"
        }.get(result.get('ending_type'), "✅ Story completed")

        await message.answer(
            f"{ending_text}\n\n📚 Well done!",
            parse_mode=ParseMode.HTML
        )

        # TODO: Complete activity
        await state.clear()
    '''
    else:
        text = "✅ <b>Scene completed!</b>\n\n"
        text += "🎉 You've finished this scene. Ready for the next one?"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="➡️ Go to next scene",
                callback_data="next_scene"
            )]
        ])

        await message.answer(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

        # Сохранить ID следующей сцены
        next_scene_id = result.get('next_scene_id')
        await state.update_data(pending_next_scene_id=next_scene_id)
    '''

@story_router.callback_query(F.data.startswith("back_to_media"))
async def callback_back_to_media(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool

    user_id = callback.message.chat.id
    user_data = await state.get_data()
    scene_id = user_data['current_scene_id']
    story_id = user_data['task8_story_id']
    npc_id = user_data.get('task8_active_npc_id')
    str_Msg = user_data.get('str_Msg')
    is_show_pause = user_data.get('is_show_pause')
    is_min_objectives_met = user_data.get('is_min_objectives_met')
    is_ending = user_data.get('is_ending')
    msg_id = user_data.get('msg_id')

    await _del_prev_kb(msg_id, message_obj=callback.message)

    builder = await _build_dialogue_keyboard(
        story_id=story_id,
        npc_id=npc_id,
        is_show_pause=is_show_pause,
        is_min_objectives_met=is_min_objectives_met,
        is_ending=is_ending
    )
    msg_p = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode="HTML")

    await state.update_data(msg_id=msg_p.message_id)



@story_router.callback_query(F.data.startswith("action_on_npc:"))
async def callback_action_on_npc(callback: types.CallbackQuery, state: FSMContext, pool):
    """
    Показать inventory для выбора item для использования на NPC
    """
    await state.set_state(myState.task8_story_active)
    npc_id = int(callback.data.split(":")[1])

    data = await state.get_data()
    story_id = data.get('task8_story_id')
    user_id = callback.message.chat.id

    logger.info(f'callback_action_on_npc++++++++++++++>>>>>>>>>>>>story_id:{story_id}')

    # Получить NPC info
    from ..story.managers.npc_manager import NPCManager
    npc_manager = NPCManager(pool)
    npc = await npc_manager.get_npc(npc_id)

    # Получить inventory
    from ..story.managers.item_manager import ItemManager
    item_manager = ItemManager(pool)
    inventory = await item_manager.get_user_inventory(user_id, story_id)


    if not inventory:
        await callback.answer("Your inventory is empty!", show_alert=True)
        return

    # Показать items для выбора
    str_Msg = f"🎬 <b>Action with {npc['name']}</b>\n\n"
    str_Msg += "Choose an item to use:\n\n"

    builder = InlineKeyboardBuilder()

    for item in inventory:
        builder.row(InlineKeyboardButton(
            text=f"{item['name']}",
            callback_data=f"use_item_on_npc:{item['item_id']}:{npc_id}"
        ))

    builder.row(InlineKeyboardButton(text=myN.fCSS('back'),callback_data=f"back_to_media"))

    #logger.info(f'callback_action_on_npc---------->>>>>str_Msg:{str_Msg}')

    msg_p = await callback.message.answer(
        str_Msg,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await state.update_data(msg_id=msg_p.message_id)
    await callback.answer()


@story_router.callback_query(F.data.startswith("use_item_on_npc:"))
async def callback_use_item_on_npc(callback: types.CallbackQuery, state: FSMContext, pool):
    """
    Использовать выбранный item на NPC
    """
    await state.set_state(myState.task8_story_active)
    parts = callback.data.split(":")
    item_id = int(parts[1])
    npc_id = int(parts[2])

    data = await state.get_data()
    story_id = data.get('task8_story_id')
    scene_id = data.get('current_scene_id')
    user_id = callback.message.chat.id

    pool_base, pool_log = pool
    recent_interaction = None
    try:
        # stage 1 get response
        # ----------------------------------------------------------------------------------------------------

        # Получить managers
        from ..story.managers.item_manager import ItemManager
        from ..story.managers.npc_manager import NPCManager
        from ..story.engines.interactive_story_engine import InteractiveStoryEngine

        item_manager = ItemManager(pool)
        npc_manager = NPCManager(pool)
        engine = InteractiveStoryEngine(pool, user_id)

        # Получить info
        item = await item_manager.get_item(item_id)
        npc = await npc_manager.get_npc(npc_id)

        # ✅ Использовать item на NPC (НЕ удаляем из inventory!)
        use_result = await item_manager.use_item(
            user_id=user_id,
            story_id=story_id,
            item_id=item_id,
            target=f"npc:{npc['name']}",
            remove_after_use=False
        )

        if not use_result['success']:
            await callback.answer(use_result['message'], show_alert=True)
            return

        # ✅ Определить контекстное действие
        item_purpose = item.get('purpose', '')
        logger.info(f'----item_purpose:{item_purpose}')
        action_description = get_action_verb_for_item(
            item_name=item['name'],
            item_purpose=item_purpose,
            npc_name=npc['name']
        )

        logger.info(f"Action: {action_description}")

        # ✅ Записать взаимодействие для проверки objectives
        result, recent_interaction = await engine.process_user_input(
            story_id=story_id,
            input_type='item_use',
            input_data={
                'item_name': item['name'],
                'item_id': item_id,
                'target': npc['name'],
                'action': action_description
            },
            target_npc_id=npc_id
        )

        # ====================================================================
        # ✅ НОВОЕ: Формат как в media_talk
        # ====================================================================

        # 1. NPC response + voice
        text = ''
        voice_file = None
        npc_response = result.get('npc_response')

        if npc_response:
            response_text = npc_response['response']

            # ✅ Генерировать голос
            from .story_helpers import generate_npc_voice_message
            voice_file = await generate_npc_voice_message(
                pool=pool,
                user_id=user_id,
                story_id=story_id,
                npc_id=npc_id,
                text=response_text
            )

            # Форматирование текста
            text = f"🎬 <b>You {action_description}</b>\n\n"
            text += f"💬 <b>{npc_response['npc_name']}</b>: "

            if npc_response.get('npc_action'):
                text += f"(<i>{npc_response['npc_action']}</i>)"

            text += f"\n{npc_response['response']}"

            # Translation
            if npc_response.get('text_trs', {}).get('ru'):
                text += f"\n<blockquote expandable='true'>🔍 {npc_response['text_trs']['ru']}</blockquote>"

            # ✅ Correction (Tutor feedback)
            if npc_response.get('correction') and npc_response['correction'].lower() not in ['n/a', 'no corrections',
                                                                                             'great job!']:
                text += f"\n\n👨‍🏫 <b>Tutor:</b> <i>{npc_response['correction']}</i>"

            # NPC gave item
            npc_gives_item = result.get('npc_gives_item')
            if npc_gives_item:
                text += f"\n\n🎁 <b>{npc_response['npc_name']} gave you: {npc_gives_item['item_name']}!</b>"
                if npc_gives_item.get('description'):
                    text += f"\n<i>{npc_gives_item['description']}</i>"

        # 6. ✅ Собрать итоговое сообщение
        str_Msg = (
            f'{text}\n\n'
            f'<b>💡 The objectives status is processing and will appear shortly...</b>'
        )

        # 8. ✅ Отправить voice + caption
        if voice_file:

            try:
                with open(voice_file, 'rb') as ogg:
                    msg_p = await callback.message.answer_voice(
                        BufferedInputFile(ogg.read(), filename="npc_voice.ogg"),
                        # caption=str_Msg,
                        # reply_markup=builder.as_markup(),
                        parse_mode="HTML"
                    )

                msg_p = await callback.message.answer(
                    str_Msg,
                    #reply_markup=builder.as_markup(),
                    parse_mode="HTML"
                )

                # ✅ Удалять только временные файлы, не трогать sfx

                voice_path = Path(voice_file)
                if 'sfx' not in str(voice_path):
                    os.remove(voice_file)
                    logger.debug(f"Deleted temporary TTS file: {voice_file}")
                else:
                    logger.debug(f"Kept sound effect file: {voice_file}")

            except Exception as e:
                logger.error(f"Error sending voice message: {e}", exc_info=True)
                msg_p = await callback.message.answer(
                    str_Msg,
                    #reply_markup=builder.as_markup(),
                    parse_mode="HTML"
                )

        else:
            msg_p = await callback.message.answer(
                str_Msg,
                #reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )


        # stage 2   narrator + objectives
        # ----------------------------------------------------------------------------------------------------
        _ = await engine.dialogue_engine.check_objective_completion(
            scene_id=scene_id,
            story_id=story_id,
            user_id=user_id,
            recent_interaction=recent_interaction
        )


        # 2. ✅ Narrator hints
        text_narrator = ''
        hint = result.get('narrator_hint')
        if hint:
            text_narrator = (
                f"\n\n🤔 \n"
                f"💭 <i>{hint['text']}</i>"
            )
            if hint.get('text_trs', {}).get('ru'):
                text_narrator += f"\n<blockquote expandable='true'>🔍 {hint['text_trs']['ru']}</blockquote>"

        # 3. ✅ Получить is_ending из БД
        query_is_ending = """
            SELECT c_is_ending
            FROM t_story_scenes
            WHERE c_scene_id = $1 AND c_story_id = $2
        """
        result_ending = await pgDB.fExec_SelectQuery_args(pool_base, query_is_ending, scene_id, story_id)
        is_ending = result_ending[0][0] if result_ending else False

        # 4. ✅ Objectives status
        is_show_pause = await _get_msg_cnt(state)
        objective_status_text, is_min_objectives_met, _ = await get_scene_objectives_status(
            pool, user_id, story_id, scene_id
        )
        objective_status_text = f'\n\n🎯 <b>Objectives:</b>\n{objective_status_text}\n'

        # 5. ✅ Key/legend
        str_key = ''
        if is_show_pause or is_min_objectives_met:
            str_key = '\n🗝<blockquote expandable="true">\n\n'
            if is_show_pause:
                text_skip = f"{myN.fCSS('pause')} - {myN.fCSS('pause_txt')}"
                str_key = f'{str_key}{text_skip}\n'
            if is_min_objectives_met:
                if is_ending:
                    txt_completed = f'{myN.fCSS("exit")} - Complete story'
                else:
                    txt_completed = f'{myN.fCSS("next_scene")} - {myN.fCSS("next_scene_txt")}'
                str_key = f'{str_key}{txt_completed}'
            str_key = f'{str_key}</blockquote>'

        # 6. ✅ Собрать итоговое сообщение
        str_Msg = (
            #f'{text}\n\n'
            #f'<b>💡 Message update:</b>'
            f'{text_narrator}'
            f'{objective_status_text}'
            #f'{str_key}'
        )

        # 7. ✅ Клавиатура как в media_talk
        builder = await _build_dialogue_keyboard(
            story_id=story_id,
            npc_id=npc_id,
            is_show_pause=is_show_pause,
            is_min_objectives_met=is_min_objectives_met,
            is_ending=is_ending
        )

        msg_p = await msg_p.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode="HTML")

        '''
        # 8. ✅ Отправить voice + caption
        if voice_file:
            from aiogram.types import BufferedInputFile
            try:
                with open(voice_file, 'rb') as ogg:
                    msg_p = await callback.message.answer_voice(
                        BufferedInputFile(ogg.read(), filename="npc_voice.ogg"),
                        #caption=str_Msg,
                        #reply_markup=builder.as_markup(),
                        parse_mode="HTML"
                    )

                msg_p = await callback.message.answer(
                    str_Msg,
                    reply_markup=builder.as_markup(),
                    parse_mode="HTML"
                )

                # ✅ Удалять только временные файлы, не трогать sfx
                import os
                from pathlib import Path
                voice_path = Path(voice_file)
                if 'sfx' not in str(voice_path):
                    os.remove(voice_file)
                    logger.debug(f"Deleted temporary TTS file: {voice_file}")
                else:
                    logger.debug(f"Kept sound effect file: {voice_file}")

            except Exception as e:
                logger.error(f"Error sending voice message: {e}", exc_info=True)
                msg_p = await callback.message.answer(
                    str_Msg,
                    reply_markup=builder.as_markup(),
                    parse_mode="HTML"
                )
        
        else:
            msg_p = await callback.message.answer(
                str_Msg,
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )
        '''

        await state.update_data(msg_id=msg_p.message_id)

        # 9. ✅ Обработка завершения сцены
        if is_min_objectives_met:
            await _handle_story_completion(callback.message, state, pool, result)

        await callback.answer()

    except Exception as e:
        logger.error(f"Error using item on NPC: {e}", exc_info=True)
        await callback.answer("❌ Error", show_alert=True)




def ______________inventory(): pass  #inventory
@story_router.callback_query(F.data == "check_inventory", StateFilter(myState.task8_story_active))
async def callback_inventory(callback, state, pool):
    """Check inventory"""
    await state.set_state(myState.task8_story_active)
    user_id = callback.message.chat.id      #.from_user.id
    user_data = await state.get_data()


    item_manager = ItemManager(pool)

    try:
        inventory = await item_manager.get_user_inventory(user_id, user_data['task8_story_id'])

        if not inventory:
            await callback.answer("Your inventory is empty.", show_alert=True)
            return

        text = "🎒 Your inventory:\n\n" + "\n".join(
            [f"🔹 {item['name']}\n" for item in inventory])
        #await callback.message.answer(text, parse_mode=ParseMode.HTML)
        await callback.answer(text, show_alert=True, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        await callback.answer("❌ Error", show_alert=True)


@story_router.callback_query(F.data.startswith("story_key_"))
async def callback_key(callback: types.CallbackQuery, state: FSMContext, pool):
    if callback.data == "story_key_d":
        text = (
            f"🗝\n"
            f"{myN.fCSS('st_action')} - {myN.fCSS('st_action_txt')}\n\n"
            f"{myN.fCSS('inv')} - {myN.fCSS('inv_txt')}\n\n"
            f"{myN.fCSS('st_grammar')} - {myN.fCSS('st_grammar_txt')}\n\n"
            #f"{myN.fCSS('pause')} - {myN.fCSS('pause_txt')}\n\n"
            f'{myN.fCSS("exit")} - {myN.fCSS("exit_txt")}\n\n'
            #f'{myN.fCSS("next_scene")} - {myN.fCSS("next_scene_txt")}\n\n'
        )

    elif callback.data == "story_key_s":
        text = (
            f"🗝\n"
            f"{myN.fCSS('pause')} - {myN.fCSS('pause_txt')}\n\n"
            f'{myN.fCSS("next_scene")} - {myN.fCSS("next_scene_txt")}\n'
        )
    await callback.answer(text, show_alert=True, parse_mode="HTML")


def ______________grammar_check(): pass  # Grammar check handlers

@story_router.callback_query(F.data == "story_check_grammar", StateFilter(myState.task8_story_active))
async def callback_story_check_grammar(callback: types.CallbackQuery, state: FSMContext, pool, dp):
    """Перенаправление на универсальный handler проверки грамматики"""
    from ...start_handlers import gen___clbck_grammarcheck
    await gen___clbck_grammarcheck(callback, state, pool, dp)


@story_router.callback_query(F.data == "story_gram_back", StateFilter(myState.task8_story_active))
async def callback_story_grammar_back(callback: types.CallbackQuery, state: FSMContext, pool):
    """
    Возврат к диалогу из режима проверки грамматики

    Это единственная функция которую нельзя переиспользовать,
    потому что она специфична для story (возврат к диалогу NPC).
    """
    try:
        # Получаем данные из state
        data = await state.get_data()
        story_id = data.get('task8_story_id')
        scene_id = data.get('current_scene_id')
        npc_id = data.get('task8_active_npc_id')
        user_id = callback.message.chat.id

        # Получаем статус objectives
        is_show_pause = await _get_msg_cnt(state)
        objective_status_text, is_min_objectives_met, _ = await get_scene_objectives_status(
            pool, user_id, story_id, scene_id
        )

        # Проверяем is_ending
        pool_base, _ = pool
        query_is_ending = """
            SELECT c_is_ending
            FROM t_story_scenes
            WHERE c_scene_id = $1 AND c_story_id = $2
        """
        result_ending = await pgDB.fExec_SelectQuery_args(pool_base, query_is_ending, scene_id, story_id)
        is_ending = result_ending[0][0] if result_ending else False

        # Восстанавливаем клавиатуру диалога
        builder = await _build_dialogue_keyboard(
            story_id=story_id,
            npc_id=npc_id,
            is_show_pause=is_show_pause,
            is_min_objectives_met=is_min_objectives_met,
            is_ending=is_ending
        )

        # Показываем подтверждение возврата
        text = (
            f"✅ <b>Grammar check completed</b>\n\n"
            f"📝 Continue your conversation below."
        )

        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in callback_story_grammar_back: {e}", exc_info=True)
        await callback.answer("Error returning to dialogue.")


def ______________functions(): pass


def fGetEmodjiNum(index):
    response = {
        1: '1️⃣',
        2: '2️⃣',
        3: '3️⃣',
        4: '4️⃣',
        5: '5️⃣',
        6: '6️⃣',
        7: '7️⃣',
        8: '8️⃣',
        9: '9️⃣'
    }
    return response.get(index)


async def _get_msg_cnt(state):
    user_data = await state.get_data()
    actions_count = user_data.get('task8_actions_count', 0) + 1
    await state.update_data(task8_actions_count=actions_count)

    if actions_count >= 5:
        return True
    else:
        return False



async def _del_prev_kb(msg_id, message_obj = None, callback_obj = None):
    if message_obj:
        user_id = message_obj.chat.id
        bot = message_obj.bot
    else:
        user_id = callback_obj.message.chat.id
        bot = callback_obj.bot

    if not msg_id:
        return

    try:
        await bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=msg_id,
            reply_markup=None
        )
        logger.debug(f"Removed keyboard from message {msg_id}")
    except TelegramBadRequest as e:
        # These errors are OK - just log and ignore
        if "message is not modified" in str(e):
            logger.debug(f"Keyboard already removed from message {msg_id}")
        elif "message to edit not found" in str(e):
            logger.debug(f"Message {msg_id} not found (probably deleted)")
        elif "message can't be edited" in str(e):
            logger.debug(f"Message {msg_id} too old to edit")
        else:
            # Unexpected error - log it
            logger.warning(f"Could not edit message {msg_id}: {e}")

    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"Unexpected error removing keyboard: {e}")



async def get_scene_objectives_status(
        pool,
        user_id: int,
        story_id: int,
        scene_id: int
) -> tuple[str, bool]:
    """
    Получить статус выполнения objectives сцены

    Args:
        pool: пул соединений с БД
        user_id: ID пользователя
        story_id: ID истории
        scene_id: ID текущей сцены

    Returns:
        tuple[str, bool]: (форматированный список objectives, все ли выполнены min_objectives)
    """

    pool_base, _ = pool
    logger.info(f'------------>>>user_id"{user_id}')
    logger.info(f'------------>>>story_id"{story_id}')
    logger.info(f'------------>>>scene_id"{scene_id}')

    # Получаем все данные одним запросом через JOIN
    query = """
        SELECT 
            sup.c_scene_progress,
            ss.c_detailed_objectives,
            ss.c_success_conditions
        FROM t_story_user_progress sup
        JOIN t_story_scenes ss ON ss.c_scene_id = $3
        WHERE sup.c_user_id = $1 AND sup.c_story_id = $2
    """

    result = await pgDB.fExec_SelectQuery_args(
        pool_base,
        query,
        user_id,
        story_id,
        scene_id
    )


    if not result:
        logger.error(f"Data not found for user {user_id}, story {story_id}, scene {scene_id}")
    logger.info(f'--------->>result:{result}')
    # Получаем данные из первой строки результата
    scene_progress = result[0][0]
    detailed_objectives = result[0][1]
    success_conditions = result[0][2]

    # Парсим JSON если нужно
    if isinstance(scene_progress, str):
        scene_progress = json.loads(scene_progress)
    if isinstance(detailed_objectives, str):
        detailed_objectives = json.loads(detailed_objectives)
    if isinstance(success_conditions, str):
        success_conditions = json.loads(success_conditions)

    scene_progress = scene_progress or {}
    detailed_objectives = detailed_objectives or {}
    success_conditions = success_conditions or {}

    # Получаем список objectives из detailed_objectives
    objectives_list = detailed_objectives.get('objectives', [])

    # Получаем min_objectives из success_conditions
    min_objectives = success_conditions.get('min_objectives', len(objectives_list))

    # Получаем прогресс текущей сцены
    scene_key = f"scene_{scene_id}"
    current_scene_progress = scene_progress.get(scene_key, {})
    completed_objectives = current_scene_progress.get('objectives', {})

    # Формируем список objectives с статусами
    objectives_status_lines = []
    completed_count = 0

    uncompleted_obj = []

    for obj in objectives_list:
        obj_id = obj.get('id')
        description = obj.get('description', 'Unknown objective')

        # Проверяем, выполнен ли objective
        is_completed = obj_id in completed_objectives and completed_objectives[obj_id].get('completed', False)

        if is_completed:
            status_icon = "✅"
            completed_count += 1
        else:
            status_icon = "⬜️"
            uncompleted_obj.append(description)

        objectives_status_lines.append(f"{status_icon} {description}")

    logger.info(f'----------------uncompleted_obj:{uncompleted_obj}')

    # Формируем итоговую строку
    objectives_string = "\n".join(objectives_status_lines)

    # Проверяем, выполнено ли минимальное количество objectives
    is_min_objectives_met = completed_count >= min_objectives

    return objectives_string, is_min_objectives_met, uncompleted_obj



__all__ = [
    'show_questionnaire_q1',
]

def ______________dummy(): pass

