"""
Handlers для опроса интересов пользователя
"""

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

from states import myState
import fpgDB as pgDB
from ..utils.keyboards import get_rating_kb, get_subtopic_rating_kb

router = Router(name='learnpath_interests')


@router.callback_query(F.data == "assess_interests_intro")
async def assess_interests_intro(callback: types.CallbackQuery, state: FSMContext, pool):
    """Введение в опросник интересов"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    await state.set_state(myState.learnpath_interests)

    str_Msg = (
        f"🎯 <b>Шаг 2: Ваши интересы</b>\n\n"
        f"Теперь давайте определим, какие темы вам интересны!\n\n"
        f"Я покажу список тем, а вы оцените свой интерес к каждой:\n"
        f"⭐ - не интересно\n"
        f"⭐⭐ - немного интересно\n"
        f"⭐⭐⭐ - интересно\n"
        f"⭐⭐⭐⭐ - очень интересно\n"
        f"⭐⭐⭐⭐⭐ - крайне интересно\n\n"
        f"Это поможет создать программу именно для вас!"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Начать", callback_data="assess_interests_start"))
    builder.adjust(1)

    await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, "assess_interests_intro")


@router.callback_query(F.data == "assess_interests_start")
async def assess_interests_start(callback: types.CallbackQuery, state: FSMContext, pool):
    """Начало опроса интересов"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    # Загружаем только родительские категории (без привязки к уровню)
    var_query = """
        SELECT c_topic_id, c_topic_name, c_topic_name_ru, c_description
        FROM t_lp_topics
        WHERE c_parent_id IS NULL
        ORDER BY c_order_priority
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if not var_Arr:
        await callback.answer("Темы не найдены. Обратитесь к администратору.", show_alert=True)
        return

    parent_topics = [
        {
            'id': row[0],
            'name': row[1],
            'name_ru': row[2],
            'desc': row[3]
        }
        for row in var_Arr
    ]

    await state.update_data(
        parent_topics=parent_topics,
        current_parent_idx=0,
        interests_ratings={},
        in_subtopic_mode=False
    )

    await send_parent_category_question(callback.message, state, pool, vUserID)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"assess_interests_start|categories_count:{len(parent_topics)}")


async def send_parent_category_question(message, state: FSMContext, pool, vUserID):
    """Отправка вопроса о родительской категории"""
    pool_base, pool_log = pool
    user_data = await state.get_data()

    parent_topics = user_data.get('parent_topics', [])
    current_idx = user_data.get('current_parent_idx', 0)

    if current_idx >= len(parent_topics):
        await finish_interests_assessment(message, state, pool, vUserID)
        return

    parent = parent_topics[current_idx]
    parent_id = parent['id']

    # Загружаем подтемы
    var_query = f"""
        SELECT c_topic_id, c_topic_name, c_topic_name_ru, c_description
        FROM t_lp_topics
        WHERE c_parent_id = {parent_id}
        ORDER BY c_order_priority
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    subtopics = [
        {
            'id': row[0],
            'name': row[1],
            'name_ru': row[2],
            'desc': row[3]
        }
        for row in var_Arr
    ]

    # Сохраняем подтемы в state
    await state.update_data(current_subtopics=subtopics)

    # Формируем список подтем для отображения
    subtopics_list = "\n".join([f"  • {st['name_ru']}" for st in subtopics])

    progress = f"{current_idx + 1}/{len(parent_topics)}"

    str_Msg = (
        f"📚 <b>Категория {progress}</b>\n\n"
        f"<b>{parent['name_ru']}</b>\n\n"
        f"<i>{parent['desc']}</i>\n\n"
        f"<b>Включает темы:</b>\n"
        f"{subtopics_list}\n\n"
        f"💡 <i>Выбранный рейтинг будет применен ко всем подтемам этой категории.</i>\n\n"
        f"Насколько вам интересна эта категория?"
    )

    keyboard = get_rating_kb(show_subtopic_button=True)
    await message.answer(str_Msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("interest_rate_"))
async def process_interest_rating(callback: types.CallbackQuery, state: FSMContext, pool):
    """Обработка оценки интереса к категории (применяется ко всем подтемам)"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    rating = int(callback.data.split("_")[-1])
    user_data = await state.get_data()

    parent_topics = user_data.get('parent_topics', [])
    current_idx = user_data.get('current_parent_idx', 0)
    interests_ratings = user_data.get('interests_ratings', {})
    subtopics = user_data.get('current_subtopics', [])

    parent = parent_topics[current_idx]

    # Применяем рейтинг ко всем подтемам
    for subtopic in subtopics:
        interests_ratings[subtopic['id']] = rating

    await state.update_data(
        current_parent_idx=current_idx + 1,
        interests_ratings=interests_ratings
    )

    await callback.answer(f"{'⭐' * rating} применено ко всем подтемам", show_alert=False)
    await send_parent_category_question(callback.message, state, pool, vUserID)

    await pgDB.fExec_LogQuery(
        pool_log,
        vUserID,
        f"category_rated|parent:{parent['id']}|rating:{rating}|subtopics:{len(subtopics)}"
    )


@router.callback_query(F.data == "specify_subtopic_rating")
async def start_subtopic_rating_mode(callback: types.CallbackQuery, state: FSMContext, pool):
    """Начало режима уточнения рейтинга для подтем"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    await state.update_data(
        in_subtopic_mode=True,
        current_subtopic_idx=0
    )

    await callback.answer("Оценим каждую подтему отдельно", show_alert=False)
    await send_subtopic_question(callback.message, state, pool, vUserID)

    await pgDB.fExec_LogQuery(pool_log, vUserID, "subtopic_mode_started")


async def send_subtopic_question(message, state: FSMContext, pool, vUserID):
    """Отправка вопроса о подтеме"""
    pool_base, pool_log = pool
    user_data = await state.get_data()

    subtopics = user_data.get('current_subtopics', [])
    current_subtopic_idx = user_data.get('current_subtopic_idx', 0)
    parent_topics = user_data.get('parent_topics', [])
    current_parent_idx = user_data.get('current_parent_idx', 0)

    if current_subtopic_idx >= len(subtopics):
        # Закончили с подтемами, переходим к следующей категории
        await finish_subtopic_mode(message, state, pool, vUserID)
        return

    subtopic = subtopics[current_subtopic_idx]
    parent = parent_topics[current_parent_idx]

    progress = f"{current_subtopic_idx + 1}/{len(subtopics)}"

    str_Msg = (
        f"📖 <b>Подтема {progress}</b>\n"
        f"<i>Категория: {parent['name_ru']}</i>\n\n"
        f"<b>{subtopic['name_ru']}</b>\n\n"
        f"{subtopic['desc']}\n\n"
        f"Насколько вам интересна эта подтема?"
    )

    keyboard = get_subtopic_rating_kb()
    await message.answer(str_Msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("subtopic_rate_"))
async def process_subtopic_rating(callback: types.CallbackQuery, state: FSMContext, pool):
    """Обработка оценки подтемы"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    rating = int(callback.data.split("_")[-1])
    user_data = await state.get_data()

    subtopics = user_data.get('current_subtopics', [])
    current_subtopic_idx = user_data.get('current_subtopic_idx', 0)
    interests_ratings = user_data.get('interests_ratings', {})

    subtopic = subtopics[current_subtopic_idx]
    interests_ratings[subtopic['id']] = rating

    await state.update_data(
        current_subtopic_idx=current_subtopic_idx + 1,
        interests_ratings=interests_ratings
    )

    await callback.answer(f"{'⭐' * rating}", show_alert=False)
    await send_subtopic_question(callback.message, state, pool, vUserID)

    await pgDB.fExec_LogQuery(pool_log, vUserID, f"subtopic_rated|topic:{subtopic['id']}|rating:{rating}")


@router.callback_query(F.data == "finish_subtopic_rating")
async def finish_subtopic_mode(callback: types.CallbackQuery, state: FSMContext, pool):
    """Завершение режима уточнения подтем"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    user_data = await state.get_data()
    current_parent_idx = user_data.get('current_parent_idx', 0)

    await state.update_data(
        in_subtopic_mode=False,
        current_parent_idx=current_parent_idx + 1
    )

    await callback.answer("Переходим к следующей категории", show_alert=False)
    await send_parent_category_question(callback.message, state, pool, vUserID)

    await pgDB.fExec_LogQuery(pool_log, vUserID, "subtopic_mode_finished")


async def finish_subtopic_mode(message, state: FSMContext, pool, vUserID):
    """Завершение режима уточнения подтем (вызывается из send_subtopic_question)"""
    pool_base, pool_log = pool
    user_data = await state.get_data()

    current_parent_idx = user_data.get('current_parent_idx', 0)

    await state.update_data(
        in_subtopic_mode=False,
        current_parent_idx=current_parent_idx + 1
    )

    await send_parent_category_question(message, state, pool, vUserID)


async def finish_interests_assessment(message, state: FSMContext, pool, vUserID):
    """Завершение опроса интересов"""
    pool_base, pool_log = pool
    user_data = await state.get_data()

    interests_ratings = user_data.get('interests_ratings', {})

    # Сохраняем только рейтинги подтем (не родительских категорий)
    for topic_id, rating in interests_ratings.items():
        var_query = f"""
            INSERT INTO t_lp_topics_user (c_user_id, c_topic_id, c_priority)
            VALUES ({vUserID}, {topic_id}, {rating})
            ON CONFLICT (c_user_id, c_topic_id) 
            DO UPDATE SET c_priority = {rating}, c_date_set = CURRENT_TIMESTAMP
        """
        await pgDB.fExec_UpdateQuery(pool_base, var_query)

    str_Msg = (
        f"✅ <b>Отлично!</b>\n\n"
        f"Ваши интересы сохранены.\n"
        f"Теперь я создам персональную программу специально для вас!"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🎓 Создать программу", callback_data="generate_learnpath"))

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"interests_complete|topics_rated:{len(interests_ratings)}")