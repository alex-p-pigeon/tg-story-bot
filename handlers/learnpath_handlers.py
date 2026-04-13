from aiogram import Router, F, types, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile, InlineKeyboardButton

from datetime import datetime, date
import json
import logging

# custom imports
from states import myState
import selfFunctions as myF
import prompt as myP
import fpgDB as pgDB

logger = logging.getLogger(__name__)

# Create router for curriculum handlers
r_curriculum = Router()


# ==================== INITIAL ASSESSMENT ====================

@r_curriculum.callback_query(F.data == "curriculum_start")
async def curriculum_init(callback: types.CallbackQuery, state: FSMContext, pool):
    """Начало процесса создания персональной программы"""
    await curriculum_init_handler(callback.message, state, pool)
    await callback.answer()


async def curriculum_init_handler(message, state: FSMContext, pool):
    """Универсальная функция начала создания программы"""
    pool_base, pool_log = pool
    vUserID = message.chat.id
    await state.set_state(myState.curriculum_assessment)

    str_Msg = (
        f"🎓 <b>Персональная программа обучения</b>\n\n"
        f"Давайте создадим программу, которая идеально подойдет именно вам!\n\n"
        f"Это займет 5-7 минут и включает:\n"
        f"• Оценку текущего уровня\n"
        f"• Определение ваших интересов\n"
        f"• Формирование индивидуального плана\n\n"
        f"Готовы начать?"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🚀 Начать", callback_data="assess_level_intro"))
    builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data="menu"))
    builder.adjust(1)

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, "curriculum_init")


@r_curriculum.callback_query(F.data == "assess_level_intro")
async def assess_level_intro(callback: types.CallbackQuery, state: FSMContext, pool):
    """Введение в тестирование уровня"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    str_Msg = (
        f"📊 <b>Шаг 1: Определение уровня</b>\n\n"
        f"Сейчас мы проведем короткий адаптивный тест для определения вашего уровня.\n\n"
        f"Тест состоит из 10 вопросов разной сложности.\n"
        f"Не волнуйтесь - вопросы будут подстраиваться под ваши ответы.\n\n"
        f"Готовы?"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Начать тест", callback_data="assess_level_start"))
    builder.add(
        InlineKeyboardButton(text="⏭️ Пропустить (использовать текущий)", callback_data="assess_interests_intro"))
    builder.adjust(1)

    await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, "assess_level_intro")


@r_curriculum.callback_query(F.data == "assess_level_start")
async def assess_level_start(callback: types.CallbackQuery, state: FSMContext, pool):
    """Начало адаптивного теста уровня"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    # Инициализация теста
    await state.update_data(
        current_question=1,
        total_questions=10,
        estimated_level=2,
        correct_answers=0,
        test_results=[]
    )

    await send_level_question(callback.message, state, pool, vUserID)
    await pgDB.fExec_LogQuery(pool_log, vUserID, "assess_level_start")


async def send_level_question(message, state: FSMContext, pool, vUserID):
    """Отправка следующего вопроса теста уровня"""
    pool_base, pool_log = pool
    user_data = await state.get_data()

    current_q = user_data.get('current_question', 1)
    total_q = user_data.get('total_questions', 10)
    estimated_level = user_data.get('estimated_level', 2)

    # Получаем вопрос из БД
    var_query = f"""
        SELECT c_question_id, c_question_text, c_question_data 
        FROM t_test_questions 
        WHERE c_eng_level = {estimated_level} 
            AND c_question_type = 'multiple_choice'
        ORDER BY RANDOM() 
        LIMIT 1
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if not var_Arr:
        await finish_level_assessment(message, state, pool, vUserID)
        return

    question_id = var_Arr[0][0]
    question_text = var_Arr[0][1]
    question_data = json.loads(var_Arr[0][2])

    await state.update_data(current_question_id=question_id)

    str_Msg = (
        f"❓ <b>Вопрос {current_q}/{total_q}</b>\n\n"
        f"{question_text}\n\n"
        f"Выберите правильный ответ:"
    )

    builder = InlineKeyboardBuilder()
    for idx, option in enumerate(question_data.get('options', [])):
        builder.add(InlineKeyboardButton(
            text=f"{chr(65 + idx)}. {option}",
            callback_data=f"assess_answer_{idx}"
        ))
    builder.adjust(1)

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


@r_curriculum.callback_query(F.data.startswith("assess_answer_"))
async def process_level_answer(callback: types.CallbackQuery, state: FSMContext, pool):
    """Обработка ответа на вопрос теста уровня"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    answer_idx = int(callback.data.split("_")[-1])
    user_data = await state.get_data()

    question_id = user_data.get('current_question_id')
    current_q = user_data.get('current_question', 1)
    total_q = user_data.get('total_questions', 10)
    estimated_level = user_data.get('estimated_level', 2)
    correct_answers = user_data.get('correct_answers', 0)
    test_results = user_data.get('test_results', [])

    # Получаем правильный ответ
    var_query = f"SELECT c_question_data FROM t_test_questions WHERE c_question_id = {question_id}"
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
    question_data = json.loads(var_Arr[0][0])
    correct_idx = question_data.get('correct_answer', 0)

    is_correct = (answer_idx == correct_idx)
    if is_correct:
        correct_answers += 1

    test_results.append({
        'question_id': question_id,
        'answer': answer_idx,
        'correct': is_correct,
        'level': estimated_level
    })

    # Адаптивная логика
    if current_q % 3 == 0:
        accuracy = correct_answers / current_q
        if accuracy > 0.8 and estimated_level < 3:
            estimated_level += 1
        elif accuracy < 0.4 and estimated_level > 1:
            estimated_level -= 1

    await state.update_data(
        current_question=current_q + 1,
        correct_answers=correct_answers,
        estimated_level=estimated_level,
        test_results=test_results
    )

    feedback = "✅ Правильно!" if is_correct else f"❌ Неверно. Правильный ответ: {chr(65 + correct_idx)}"
    await callback.answer(feedback, show_alert=False)

    if current_q >= total_q:
        await finish_level_assessment(callback.message, state, pool, vUserID)
    else:
        await send_level_question(callback.message, state, pool, vUserID)

    await pgDB.fExec_LogQuery(pool_log, vUserID, f"assess_answer|q:{current_q}|correct:{is_correct}")


async def finish_level_assessment(message, state: FSMContext, pool, vUserID):
    """Завершение теста уровня"""
    pool_base, pool_log = pool
    user_data = await state.get_data()

    correct_answers = user_data.get('correct_answers', 0)
    total_q = user_data.get('total_questions', 10)
    test_results = user_data.get('test_results', [])

    accuracy = correct_answers / total_q if total_q > 0 else 0

    if accuracy >= 0.8:
        final_level = 3
        level_name = "Advanced (C)"
    elif accuracy >= 0.5:
        final_level = 2
        level_name = "Intermediate (B)"
    else:
        final_level = 1
        level_name = "Beginner (A)"

    # Сохраняем результат
    var_query = f"""
        UPDATE t_user_paramssingle 
        SET c_ups_eng_level = {final_level}
        WHERE c_ups_user_id = {vUserID}
    """
    await pgDB.fExec_UpdateQuery(pool_base, var_query)

    test_data = json.dumps(test_results)
    var_query = f"""
        INSERT INTO t_curriculum_tests 
        (c_user_id, c_topic_id, c_test_type, c_score, c_max_score, c_passed, c_test_data)
        VALUES ({vUserID}, NULL, 'entry', {correct_answers}, {total_q}, true, '{test_data}')
    """
    await pgDB.fExec_UpdateQuery(pool_base, var_query)

    await state.update_data(assessed_level=final_level)

    str_Msg = (
        f"🎉 <b>Тест завершен!</b>\n\n"
        f"Ваш результат: {correct_answers}/{total_q} ({int(accuracy * 100)}%)\n"
        f"Определенный уровень: <b>{level_name}</b>\n\n"
        f"Переходим к следующему шагу!"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="➡️ Далее", callback_data="assess_interests_intro"))

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID,
                              f"level_assessment_complete|level:{final_level}|score:{correct_answers}/{total_q}")


# ==================== INTERESTS ASSESSMENT ====================

@r_curriculum.callback_query(F.data == "assess_interests_intro")
async def assess_interests_intro(callback: types.CallbackQuery, state: FSMContext, pool):
    """Введение в опросник интересов"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    await state.set_state(myState.curriculum_interests)

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


@r_curriculum.callback_query(F.data == "assess_interests_start")
async def assess_interests_start(callback: types.CallbackQuery, state: FSMContext, pool):
    """Начало опроса интересов"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    user_data = await state.get_data()
    user_level = user_data.get('assessed_level')

    if not user_level:
        var_query = f"SELECT c_ups_eng_level FROM t_user_paramssingle WHERE c_ups_user_id = {vUserID}"
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
        user_level = var_Arr[0][0] if var_Arr else 2

    var_query = f"""
        SELECT c_topic_id, c_topic_name, c_topic_name_ru, c_description, c_category
        FROM t_curriculum_topics
        WHERE c_eng_level <= {user_level}
        ORDER BY c_order_priority
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if not var_Arr:
        await callback.answer("Темы не найдены. Обратитесь к администратору.", show_alert=True)
        return

    topics = [{'id': row[0], 'name': row[1], 'name_ru': row[2], 'desc': row[3], 'category': row[4]} for row in var_Arr]

    await state.update_data(
        topics_to_rate=topics,
        current_topic_idx=0,
        interests_ratings={}
    )

    await send_interest_question(callback.message, state, pool, vUserID)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"assess_interests_start|topics_count:{len(topics)}")


async def send_interest_question(message, state: FSMContext, pool, vUserID):
    """Отправка следующего вопроса об интересах"""
    pool_base, pool_log = pool
    user_data = await state.get_data()

    topics = user_data.get('topics_to_rate', [])
    current_idx = user_data.get('current_topic_idx', 0)

    if current_idx >= len(topics):
        await finish_interests_assessment(message, state, pool, vUserID)
        return

    topic = topics[current_idx]
    topic_name_ru = topic.get('name_ru', topic.get('name'))
    topic_desc = topic.get('desc', '')

    progress = f"{current_idx + 1}/{len(topics)}"

    str_Msg = (
        f"📚 <b>Тема {progress}</b>\n\n"
        f"<b>{topic_name_ru}</b>\n"
        f"{topic_desc}\n\n"
        f"Насколько вам интересна эта тема?"
    )

    builder = InlineKeyboardBuilder()
    for stars in range(1, 6):
        builder.add(InlineKeyboardButton(
            text="⭐" * stars,
            callback_data=f"interest_rate_{stars}"
        ))
    builder.adjust(5)

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


@r_curriculum.callback_query(F.data.startswith("interest_rate_"))
async def process_interest_rating(callback: types.CallbackQuery, state: FSMContext, pool):
    """Обработка оценки интереса к теме"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    rating = int(callback.data.split("_")[-1])
    user_data = await state.get_data()

    topics = user_data.get('topics_to_rate', [])
    current_idx = user_data.get('current_topic_idx', 0)
    interests_ratings = user_data.get('interests_ratings', {})

    topic = topics[current_idx]
    topic_id = topic.get('id')

    interests_ratings[topic_id] = rating

    await state.update_data(
        current_topic_idx=current_idx + 1,
        interests_ratings=interests_ratings
    )

    await callback.answer(f"{'⭐' * rating}", show_alert=False)
    await send_interest_question(callback.message, state, pool, vUserID)

    await pgDB.fExec_LogQuery(pool_log, vUserID, f"interest_rated|topic:{topic_id}|rating:{rating}")


async def finish_interests_assessment(message, state: FSMContext, pool, vUserID):
    """Завершение опроса интересов"""
    pool_base, pool_log = pool
    user_data = await state.get_data()

    interests_ratings = user_data.get('interests_ratings', {})

    for topic_id, rating in interests_ratings.items():
        var_query = f"""
            INSERT INTO t_user_interests (c_user_id, c_topic_id, c_priority)
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
    builder.add(InlineKeyboardButton(text="🎓 Создать программу", callback_data="generate_curriculum"))

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"interests_complete|topics_rated:{len(interests_ratings)}")


# ==================== CURRICULUM GENERATION ====================

@r_curriculum.callback_query(F.data == "generate_curriculum")
async def generate_curriculum(callback: types.CallbackQuery, state: FSMContext, pool):
    """Генерация персональной программы"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    await state.set_state(myState.curriculum_active)

    await callback.answer("Генерирую программу...", show_alert=False)

    var_query = f"SELECT c_ups_eng_level FROM t_user_paramssingle WHERE c_ups_user_id = {vUserID}"
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
    user_level = var_Arr[0][0] if var_Arr else 2

    var_query = f"""
        SELECT c_topic_id, c_priority 
        FROM t_user_interests 
        WHERE c_user_id = {vUserID} AND c_priority >= 3
        ORDER BY c_priority DESC, c_date_set DESC
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    interested_topics = [row[0] for row in var_Arr] if var_Arr else []

    var_query = f"""
        SELECT c_topic_id 
        FROM t_curriculum_topics
        WHERE c_eng_level = {user_level} 
            AND c_category = 'essential'
        ORDER BY c_order_priority
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
    essential_topics = [row[0] for row in var_Arr] if var_Arr else []

    all_topics = list(dict.fromkeys(essential_topics + interested_topics))

    for idx, topic_id in enumerate(all_topics, start=1):
        var_query = f"""
            INSERT INTO t_user_curriculum 
            (c_user_id, c_topic_id, c_status, c_order_in_program, c_progress_percent)
            VALUES ({vUserID}, {topic_id}, 'not_started', {idx}, 0)
            ON CONFLICT (c_user_id, c_topic_id) DO NOTHING
        """
        await pgDB.fExec_UpdateQuery(pool_base, var_query)

    if all_topics:
        var_query = f"""
            UPDATE t_user_curriculum 
            SET c_status = 'in_progress', c_start_date = CURRENT_TIMESTAMP
            WHERE c_user_id = {vUserID} AND c_topic_id = {all_topics[0]}
        """
        await pgDB.fExec_UpdateQuery(pool_base, var_query)

    str_Msg = (
        f"🎉 <b>Ваша программа готова!</b>\n\n"
        f"Создана персональная программа из {len(all_topics)} тем.\n\n"
        f"Программа учитывает:\n"
        f"✅ Ваш уровень английского\n"
        f"✅ Ваши интересы и цели\n"
        f"✅ Рекомендованную последовательность\n\n"
        f"Готовы начать обучение?"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📚 Моя программа", callback_data="view_curriculum"))
    builder.add(InlineKeyboardButton(text="🚀 Начать первую тему", callback_data="start_current_topic"))
    builder.adjust(1)

    await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"curriculum_generated|topics:{len(all_topics)}")


# ==================== CURRICULUM VIEWING ====================

@r_curriculum.callback_query(F.data == "view_curriculum")
async def view_curriculum(callback: types.CallbackQuery, state: FSMContext, pool):
    """Просмотр персональной программы"""
    await view_curriculum_handler(callback.message, state, pool)
    await callback.answer()


async def view_curriculum_handler(message, state: FSMContext, pool):
    """Универсальная функция просмотра программы"""
    pool_base, pool_log = pool
    vUserID = message.chat.id

    var_query = f"""
        SELECT 
            uc.c_topic_id, 
            uc.c_status, 
            uc.c_progress_percent,
            uc.c_order_in_program,
            t.c_topic_name_ru,
            t.c_estimated_hours
        FROM t_user_curriculum uc
        JOIN t_curriculum_topics t ON uc.c_topic_id = t.c_topic_id
        WHERE uc.c_user_id = {vUserID}
        ORDER BY uc.c_order_in_program
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if not var_Arr:
        await message.answer("Программа не найдена. Создайте новую.", parse_mode=ParseMode.HTML)
        return

    status_emoji = {
        'not_started': '⚪',
        'in_progress': '🟡',
        'completed': '🟢',
        'skipped': '⚫'
    }

    topics_list = []
    total_progress = 0

    for row in var_Arr:
        topic_id, status, progress, order, name_ru, hours = row
        emoji = status_emoji.get(status, '⚪')
        topics_list.append(f"{emoji} {order}. {name_ru} ({progress}%)")
        total_progress += progress

    avg_progress = total_progress // len(var_Arr) if var_Arr else 0

    str_Msg = (
            f"📚 <b>Ваша программа обучения</b>\n\n"
            f"Общий прогресс: {avg_progress}%\n"
            f"Тем в программе: {len(var_Arr)}\n\n"
            f"<b>Темы:</b>\n"
            + "\n".join(topics_list)
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🚀 Продолжить обучение", callback_data="continue_learning"))
    builder.add(InlineKeyboardButton(text="⚙️ Настроить программу", callback_data="edit_curriculum"))
    builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data="menu"))
    builder.adjust(1)

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, "view_curriculum")


@r_curriculum.callback_query(F.data == "continue_learning")
async def continue_learning(callback: types.CallbackQuery, state: FSMContext, pool):
    """Продолжить обучение с текущей темы"""
    await continue_learning_handler(callback.message, state, pool)
    await callback.answer()


async def continue_learning_handler(message, state: FSMContext, pool):
    """Универсальная функция продолжения обучения"""
    pool_base, pool_log = pool
    vUserID = message.chat.id

    var_query = f"""
        SELECT c_topic_id, c_current_module_id
        FROM t_user_curriculum
        WHERE c_user_id = {vUserID} AND c_status = 'in_progress'
        ORDER BY c_order_in_program
        LIMIT 1
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if not var_Arr:
        var_query = f"""
            UPDATE t_user_curriculum 
            SET c_status = 'in_progress', c_start_date = CURRENT_TIMESTAMP
            WHERE c_user_id = {vUserID} 
                AND c_status = 'not_started'
                AND c_topic_id = (
                    SELECT c_topic_id FROM t_user_curriculum 
                    WHERE c_user_id = {vUserID} AND c_status = 'not_started'
                    ORDER BY c_order_in_program LIMIT 1
                )
        """
        await pgDB.fExec_UpdateQuery(pool_base, var_query)

        var_query = f"""
            SELECT c_topic_id, c_current_module_id
            FROM t_user_curriculum
            WHERE c_user_id = {vUserID} AND c_status = 'in_progress'
            LIMIT 1
        """
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if not var_Arr:
        await message.answer("Все темы завершены! 🎉", parse_mode=ParseMode.HTML)
        return

    topic_id = var_Arr[0][0]
    current_module_id = var_Arr[0][1]

    await state.update_data(current_topic_id=topic_id)
    await show_topic_overview(message, state, pool, vUserID, topic_id)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"continue_learning|topic:{topic_id}")


@r_curriculum.callback_query(F.data == "start_current_topic")
async def start_current_topic(callback: types.CallbackQuery, state: FSMContext, pool):
    """Начать текущую тему"""
    await continue_learning_handler(callback.message, state, pool)
    await callback.answer()


async def show_topic_overview(message, state: FSMContext, pool, vUserID, topic_id):
    """Показать обзор темы"""
    pool_base, pool_log = pool

    var_query = f"""
        SELECT 
            t.c_topic_name_ru,
            t.c_description,
            t.c_estimated_hours,
            uc.c_progress_percent
        FROM t_curriculum_topics t
        JOIN t_user_curriculum uc ON t.c_topic_id = uc.c_topic_id
        WHERE t.c_topic_id = {topic_id} AND uc.c_user_id = {vUserID}
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if not var_Arr:
        await message.answer("Тема не найдена", parse_mode=ParseMode.HTML)
        return

    name_ru, description, hours, progress = var_Arr[0]

    var_query = f"""
        SELECT 
            m.c_module_id,
            m.c_module_name,
            m.c_content_type,
            m.c_estimated_minutes,
            COALESCE(ump.c_status, 'not_started') as status
        FROM t_curriculum_modules m
        LEFT JOIN t_user_module_progress ump 
            ON m.c_module_id = ump.c_module_id AND ump.c_user_id = {vUserID}
        WHERE m.c_topic_id = {topic_id}
        ORDER BY m.c_module_order
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    modules_list = []
    for idx, row in enumerate(var_Arr, start=1):
        module_id, module_name, content_type, minutes, status = row
        status_icon = '✅' if status == 'completed' else '🔄' if status == 'in_progress' else '⚪'
        modules_list.append(f"{status_icon} {idx}. {module_name} (~{minutes} мин)")

    str_Msg = (
            f"📖 <b>{name_ru}</b>\n\n"
            f"{description}\n\n"
            f"Прогресс: {progress}%\n"
            f"Примерное время: {hours} ч\n\n"
            f"<b>Модули:</b>\n"
            + "\n".join(modules_list)
    )

    builder = InlineKeyboardBuilder()

    next_module = None
    for row in var_Arr:
        if row[4] != 'completed':
            next_module = row[0]
            break

    if next_module:
        builder.add(InlineKeyboardButton(text="▶️ Начать занятие", callback_data=f"start_module_{next_module}"))

    builder.add(InlineKeyboardButton(text="📊 Пройти тест по теме", callback_data=f"topic_test_{topic_id}"))
    builder.add(InlineKeyboardButton(text="◀️ К программе", callback_data="view_curriculum"))
    builder.adjust(1)

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


# ==================== MODULE LEARNING ====================

@r_curriculum.callback_query(F.data.startswith("start_module_"))
async def start_module(callback: types.CallbackQuery, state: FSMContext, pool):
    """Начать модуль обучения"""
    module_id = int(callback.data.split("_")[-1])
    await start_module_handler(callback.message, state, pool, module_id)
    await callback.answer()


async def start_module_handler(message, state: FSMContext, pool, module_id):
    """Универсальная функция начала модуля"""
    pool_base, pool_log = pool
    vUserID = message.chat.id

    var_query = f"""
        SELECT 
            m.c_module_name,
            m.c_content_type,
            m.c_content,
            m.c_topic_id
        FROM t_curriculum_modules m
        WHERE m.c_module_id = {module_id}
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if not var_Arr:
        await message.answer("Модуль не найден", parse_mode=ParseMode.HTML)
        return

    module_name, content_type, content_json, topic_id = var_Arr[0]
    content = json.loads(content_json) if content_json else {}

    var_query = f"""
        INSERT INTO t_user_module_progress 
        (c_user_id, c_module_id, c_status, c_attempts)
        VALUES ({vUserID}, {module_id}, 'in_progress', 1)
        ON CONFLICT (c_user_id, c_module_id) 
        DO UPDATE SET 
            c_status = 'in_progress',
            c_attempts = t_user_module_progress.c_attempts + 1
    """
    await pgDB.fExec_UpdateQuery(pool_base, var_query)

    var_query = f"""
        UPDATE t_user_curriculum 
        SET c_current_module_id = {module_id}
        WHERE c_user_id = {vUserID} AND c_topic_id = {topic_id}
    """
    await pgDB.fExec_UpdateQuery(pool_base, var_query)

    await state.update_data(
        current_module_id=module_id,
        current_topic_id=topic_id,
        module_content=content
    )

    if content_type == 'lesson':
        await show_lesson(message, state, pool, vUserID, module_id, content)
    elif content_type == 'practice':
        await show_practice(message, state, pool, vUserID, module_id, content)
    elif content_type == 'test':
        await show_module_test(message, state, pool, vUserID, module_id, content)

    await pgDB.fExec_LogQuery(pool_log, vUserID, f"start_module|module:{module_id}|type:{content_type}")


async def show_lesson(message, state: FSMContext, pool, vUserID, module_id, content):
    """Показать урок"""
    pool_base, pool_log = pool

    lesson_text = content.get('text', 'Содержание урока отсутствует')
    examples = content.get('examples', [])

    str_Msg = (
        f"📚 <b>Урок</b>\n\n"
        f"{lesson_text}\n\n"
    )

    if examples:
        str_Msg += "<b>Примеры:</b>\n"
        for ex in examples:
            str_Msg += f"• {ex}\n"

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Понятно, продолжить", callback_data=f"complete_module_{module_id}"))
    builder.add(InlineKeyboardButton(text="❓ Нужно объяснение", callback_data=f"explain_module_{module_id}"))
    builder.adjust(1)

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


async def show_practice(message, state: FSMContext, pool, vUserID, module_id, content):
    """Показать практическое задание"""
    pool_base, pool_log = pool

    task_text = content.get('task', 'Задание отсутствует')
    task_type = content.get('type', 'text')

    str_Msg = (
        f"✍️ <b>Практика</b>\n\n"
        f"{task_text}\n\n"
    )

    if task_type == 'voice':
        str_Msg += "🎤 Отправьте голосовое сообщение с вашим ответом"
        await state.set_state(myState.curriculum_practice_voice)
    elif task_type == 'dialogue':
        str_Msg += "💬 Начните диалог, напишите или запишите ваш ответ"
        await state.set_state(myState.curriculum_practice_dialogue)
    else:
        str_Msg += "✍️ Напишите ваш ответ"
        await state.set_state(myState.curriculum_practice_text)

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="⏭️ Пропустить", callback_data=f"skip_module_{module_id}"))

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


async def show_module_test(message, state: FSMContext, pool, vUserID, module_id, content):
    """Показать тест модуля"""
    questions = content.get('questions', [])

    if not questions:
        await message.answer("Вопросы не найдены", parse_mode=ParseMode.HTML)
        return

    await state.update_data(
        test_questions=questions,
        current_question_idx=0,
        test_answers=[]
    )
    await state.set_state(myState.curriculum_module_test)

    await send_module_test_question(message, state, pool, vUserID)


async def send_module_test_question(message, state: FSMContext, pool, vUserID):
    """Отправить вопрос теста модуля"""
    user_data = await state.get_data()
    questions = user_data.get('test_questions', [])
    current_idx = user_data.get('current_question_idx', 0)

    if current_idx >= len(questions):
        await finish_module_test(message, state, pool, vUserID)
        return

    question = questions[current_idx]
    q_text = question.get('question', '')
    options = question.get('options', [])

    str_Msg = (
        f"❓ <b>Вопрос {current_idx + 1}/{len(questions)}</b>\n\n"
        f"{q_text}"
    )

    builder = InlineKeyboardBuilder()
    for idx, option in enumerate(options):
        builder.add(InlineKeyboardButton(
            text=f"{chr(65 + idx)}. {option}",
            callback_data=f"module_test_answer_{idx}"
        ))
    builder.adjust(1)

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


@r_curriculum.callback_query(F.data.startswith("module_test_answer_"))
async def process_module_test_answer(callback: types.CallbackQuery, state: FSMContext, pool):
    """Обработка ответа на вопрос теста модуля"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    answer_idx = int(callback.data.split("_")[-1])
    user_data = await state.get_data()

    questions = user_data.get('test_questions', [])
    current_idx = user_data.get('current_question_idx', 0)
    test_answers = user_data.get('test_answers', [])

    question = questions[current_idx]
    correct_idx = question.get('correct', 0)
    is_correct = (answer_idx == correct_idx)

    test_answers.append({
        'question_idx': current_idx,
        'answer': answer_idx,
        'correct': is_correct
    })

    await state.update_data(
        current_question_idx=current_idx + 1,
        test_answers=test_answers
    )

    feedback = "✅ Правильно!" if is_correct else "❌ Неверно"
    await callback.answer(feedback, show_alert=False)

    await send_module_test_question(callback.message, state, pool, vUserID)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"module_test_answer|q:{current_idx}|correct:{is_correct}")


async def finish_module_test(message, state: FSMContext, pool, vUserID):
    """Завершение теста модуля"""
    pool_base, pool_log = pool
    user_data = await state.get_data()

    test_answers = user_data.get('test_answers', [])
    module_id = user_data.get('current_module_id')
    topic_id = user_data.get('current_topic_id')

    correct_count = sum(1 for ans in test_answers if ans.get('correct'))
    total_count = len(test_answers)
    score = (correct_count / total_count * 100) if total_count > 0 else 0
    passed = score >= 70

    var_query = f"""
        UPDATE t_user_module_progress 
        SET 
            c_status = '{'completed' if passed else 'in_progress'}',
            c_score = {score},
            c_completed_at = {'CURRENT_TIMESTAMP' if passed else 'NULL'}
        WHERE c_user_id = {vUserID} AND c_module_id = {module_id}
    """
    await pgDB.fExec_UpdateQuery(pool_base, var_query)

    if passed:
        await update_topic_progress(pool_base, vUserID, topic_id)

    str_Msg = (
        f"{'🎉 Отлично!' if passed else '📚 Попробуйте еще раз'}\n\n"
        f"Результат: {correct_count}/{total_count} ({int(score)}%)\n"
        f"{'✅ Модуль завершен!' if passed else '❌ Для завершения нужно 70%'}"
    )

    builder = InlineKeyboardBuilder()
    if passed:
        builder.add(InlineKeyboardButton(text="➡️ Следующий модуль", callback_data=f"next_module_{topic_id}"))
    else:
        builder.add(InlineKeyboardButton(text="🔄 Повторить", callback_data=f"start_module_{module_id}"))
    builder.add(InlineKeyboardButton(text="◀️ К теме", callback_data=f"topic_overview_{topic_id}"))
    builder.adjust(1)

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"module_test_complete|score:{score}|passed:{passed}")


# ==================== MODULE COMPLETION ====================

@r_curriculum.callback_query(F.data.startswith("complete_module_"))
async def complete_module(callback: types.CallbackQuery, state: FSMContext, pool):
    """Завершение модуля"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    module_id = int(callback.data.split("_")[-1])
    user_data = await state.get_data()
    topic_id = user_data.get('current_topic_id')

    var_query = f"""
        UPDATE t_user_module_progress 
        SET 
            c_status = 'completed',
            c_completed_at = CURRENT_TIMESTAMP,
            c_score = 100
        WHERE c_user_id = {vUserID} AND c_module_id = {module_id}
    """
    await pgDB.fExec_UpdateQuery(pool_base, var_query)

    await update_topic_progress(pool_base, vUserID, topic_id)

    await callback.answer("✅ Модуль завершен!", show_alert=False)

    await next_module_handler(callback.message, state, pool, topic_id)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"complete_module|module:{module_id}")


async def next_module_handler(message, state, pool, topic_id):
    """Переход к следующему модулю - универсальная функция"""
    pool_base, pool_log = pool
    vUserID = message.chat.id

    var_query = f"""
        SELECT m.c_module_id
        FROM t_curriculum_modules m
        LEFT JOIN t_user_module_progress ump 
            ON m.c_module_id = ump.c_module_id AND ump.c_user_id = {vUserID}
        WHERE m.c_topic_id = {topic_id}
            AND COALESCE(ump.c_status, 'not_started') != 'completed'
        ORDER BY m.c_module_order
        LIMIT 1
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if var_Arr:
        next_module_id = var_Arr[0][0]
        await start_module_handler(message, state, pool, next_module_id)
    else:
        str_Msg = (
            f"🎉 <b>Поздравляем!</b>\n\n"
            f"Вы завершили все модули темы!\n"
            f"Теперь пройдите финальный тест для закрытия темы."
        )

        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="📝 Пройти финальный тест", callback_data=f"topic_test_{topic_id}"))
        builder.add(InlineKeyboardButton(text="◀️ К программе", callback_data="view_curriculum"))
        builder.adjust(1)

        await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


@r_curriculum.callback_query(F.data.startswith("next_module_"))
async def next_module_callback(callback: types.CallbackQuery, state: FSMContext, pool):
    """Callback для перехода к следующему модулю"""
    topic_id = int(callback.data.split("_")[-1])
    await next_module_handler(callback.message, state, pool, topic_id)
    await callback.answer()


async def update_topic_progress(pool_base, vUserID, topic_id):
    """Обновление прогресса по теме"""
    var_query = f"""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN COALESCE(ump.c_status, 'not_started') = 'completed' THEN 1 ELSE 0 END) as completed
        FROM t_curriculum_modules m
        LEFT JOIN t_user_module_progress ump 
            ON m.c_module_id = ump.c_module_id AND ump.c_user_id = {vUserID}
        WHERE m.c_topic_id = {topic_id}
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if var_Arr:
        total, completed = var_Arr[0]
        progress = int((completed / total * 100)) if total > 0 else 0

        var_query = f"""
            UPDATE t_user_curriculum 
            SET c_progress_percent = {progress}
            WHERE c_user_id = {vUserID} AND c_topic_id = {topic_id}
        """
        await pgDB.fExec_UpdateQuery(pool_base, var_query)


# ==================== PRACTICE HANDLERS ====================

@r_curriculum.message(F.text, StateFilter(myState.curriculum_practice_text))
async def handle_practice_text(message: types.Message, state: FSMContext, pool, dp):
    """Обработка текстового ответа на практику"""
    pool_base, pool_log = pool
    vUserID = message.chat.id

    user_data = await state.get_data()
    module_id = user_data.get('current_module_id')
    module_content = user_data.get('module_content', {})

    usertext = message.text.strip()

    nlp_tools = dp.workflow_data.get("nlp_tools")

    str_grammar, index_rule_pairs, improved_line = await myF.fGrammarCheck_txt(
        nlp_tools.tool, usertext, pool, vUserID
    )

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
    builder.adjust(1)

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"practice_text_submitted|module:{module_id}")


@r_curriculum.message(F.voice, StateFilter(myState.curriculum_practice_voice))
async def handle_practice_voice(message: types.Message, state: FSMContext, pool, dp):
    """Обработка голосового ответа на практику"""
    pool_base, pool_log = pool
    vUserID = message.chat.id

    user_data = await state.get_data()
    module_id = user_data.get('current_module_id')

    usertext = await myF.afVoiceToTxt(message, pool, vUserID)

    if not usertext:
        await message.answer("Не удалось распознать речь. Попробуйте еще раз.", parse_mode=ParseMode.HTML)
        return

    nlp_tools = dp.workflow_data.get("nlp_tools")
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
    builder.adjust(1)

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"practice_voice_submitted|module:{module_id}")


@r_curriculum.callback_query(F.data.startswith("skip_module_"))
async def skip_module(callback: types.CallbackQuery, state: FSMContext, pool):
    """Пропустить модуль"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    module_id = int(callback.data.split("_")[-1])
    user_data = await state.get_data()
    topic_id = user_data.get('current_topic_id')

    await callback.answer("Модуль пропущен", show_alert=False)
    await next_module_handler(callback.message, state, pool, topic_id)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"skip_module|module:{module_id}")


@r_curriculum.callback_query(F.data.startswith("explain_module_"))
async def explain_module(callback: types.CallbackQuery, state: FSMContext, pool, dp):
    """Запрос дополнительного объяснения"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    module_id = int(callback.data.split("_")[-1])
    user_data = await state.get_data()
    module_content = user_data.get('module_content', {})

    lesson_text = module_content.get('text', '')

    prompt = f"Provide a simpler, more detailed explanation of this concept:\n\n{lesson_text}"
    explanation = await myF.afSendMsg2AI(prompt, pool_base, vUserID, toggleParam=2)

    str_Msg = (
        f"💡 <b>Дополнительное объяснение:</b>\n\n"
        f"{explanation}"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Понятно, продолжить", callback_data=f"complete_module_{module_id}"))
    builder.add(InlineKeyboardButton(text="❓ Еще вопросы", callback_data=f"ask_question_{module_id}"))
    builder.adjust(1)

    await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"explain_module|module:{module_id}")


@r_curriculum.callback_query(F.data.startswith("topic_overview_"))
async def topic_overview_callback(callback: types.CallbackQuery, state: FSMContext, pool):
    """Показать обзор темы через callback"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    topic_id = int(callback.data.split("_")[-1])
    await show_topic_overview(callback.message, state, pool, vUserID, topic_id)


# ==================== CURRICULUM EDITING ====================

@r_curriculum.callback_query(F.data == "edit_curriculum")
async def edit_curriculum_menu(callback: types.CallbackQuery, state: FSMContext, pool):
    """Меню редактирования программы"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    str_Msg = (
        f"⚙️ <b>Настройка программы</b>\n\n"
        f"Что вы хотите изменить?"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔄 Пересоздать программу", callback_data="recreate_curriculum"))
    builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data="view_curriculum"))
    builder.adjust(1)

    await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, "edit_curriculum_menu")


@r_curriculum.callback_query(F.data == "recreate_curriculum")
async def recreate_curriculum(callback: types.CallbackQuery, state: FSMContext, pool):
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
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="edit_curriculum"))
    builder.adjust(1)

    await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, "recreate_curriculum_confirm")


@r_curriculum.callback_query(F.data == "confirm_recreate")
async def confirm_recreate_curriculum(callback: types.CallbackQuery, state: FSMContext, pool):
    """Подтверждение пересоздания программы"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    var_query = f"DELETE FROM t_user_curriculum WHERE c_user_id = {vUserID}"
    await pgDB.fExec_UpdateQuery(pool_base, var_query)

    var_query = f"DELETE FROM t_user_module_progress WHERE c_user_id = {vUserID}"
    await pgDB.fExec_UpdateQuery(pool_base, var_query)

    var_query = f"DELETE FROM t_user_interests WHERE c_user_id = {vUserID}"
    await pgDB.fExec_UpdateQuery(pool_base, var_query)

    await callback.answer("Программа удалена. Начинаем заново.", show_alert=True)

    await curriculum_init_handler(callback.message, state, pool)
    await pgDB.fExec_LogQuery(pool_log, vUserID, "curriculum_recreated")


# ==================== COMMAND ====================

@r_curriculum.message(Command("curriculum"))
async def cmd_curriculum(message: types.Message, state: FSMContext, pool):
    """Команда для быстрого доступа к программе"""
    pool_base, pool_log = pool
    vUserID = message.chat.id

    var_query = f"SELECT COUNT(*) FROM t_user_curriculum WHERE c_user_id = {vUserID}"
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    has_curriculum = var_Arr[0][0] > 0 if var_Arr else False

    if has_curriculum:
        await view_curriculum_handler(message, state, pool)
    else:
        await curriculum_init_handler(message, state, pool)

    await pgDB.fExec_LogQuery(pool_log, vUserID, "cmd_curriculum")


# ==================== TOPIC TESTING ====================

@r_curriculum.callback_query(F.data.startswith("topic_test_"))
async def topic_test_intro(callback: types.CallbackQuery, state: FSMContext, pool):
    """Введение в финальный тест темы"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    topic_id = int(callback.data.split("_")[-1])

    var_query = f"""
        SELECT c_topic_name_ru
        FROM t_curriculum_topics
        WHERE c_topic_id = {topic_id}
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if not var_Arr:
        await callback.answer("Тема не найдена", show_alert=True)
        return

    topic_name = var_Arr[0][0]

    str_Msg = (
        f"📝 <b>Финальный тест</b>\n\n"
        f"Тема: {topic_name}\n\n"
        f"Тест проверит ваше понимание темы.\n"
        f"Для прохождения нужно набрать минимум 80%.\n\n"
        f"Готовы начать?"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Начать тест", callback_data=f"topic_test_start_{topic_id}"))
    builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data=f"topic_overview_{topic_id}"))
    builder.adjust(1)

    await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"topic_test_intro|topic:{topic_id}")


@r_curriculum.callback_query(F.data.startswith("topic_test_start_"))
async def topic_test_start(callback: types.CallbackQuery, state: FSMContext, pool):
    """Начало финального теста темы"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    topic_id = int(callback.data.split("_")[-1])

    var_query = f"""
        SELECT c_question_id, c_question_text, c_question_data
        FROM t_test_questions
        WHERE c_topic_id = {topic_id}
        ORDER BY RANDOM()
        LIMIT 15
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if not var_Arr:
        await callback.answer("Вопросы для теста не найдены", show_alert=True)
        return

    questions = []
    for row in var_Arr:
        questions.append({
            'id': row[0],
            'text': row[1],
            'data': json.loads(row[2])
        })

    await state.update_data(
        topic_test_id=topic_id,
        topic_test_questions=questions,
        topic_test_current=0,
        topic_test_answers=[]
    )
    await state.set_state(myState.curriculum_topic_test)

    await send_topic_test_question(callback.message, state, pool, vUserID)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"topic_test_start|topic:{topic_id}")


async def send_topic_test_question(message, state: FSMContext, pool, vUserID):
    """Отправить вопрос финального теста"""
    user_data = await state.get_data()
    questions = user_data.get('topic_test_questions', [])
    current_idx = user_data.get('topic_test_current', 0)

    if current_idx >= len(questions):
        await finish_topic_test(message, state, pool, vUserID)
        return

    question = questions[current_idx]
    q_text = question['text']
    q_data = question['data']
    options = q_data.get('options', [])

    str_Msg = (
        f"❓ <b>Вопрос {current_idx + 1}/{len(questions)}</b>\n\n"
        f"{q_text}"
    )

    builder = InlineKeyboardBuilder()
    for idx, option in enumerate(options):
        builder.add(InlineKeyboardButton(
            text=f"{chr(65 + idx)}. {option}",
            callback_data=f"topic_test_ans_{idx}"
        ))
    builder.adjust(1)

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


@r_curriculum.callback_query(F.data.startswith("topic_test_ans_"))
async def process_topic_test_answer(callback: types.CallbackQuery, state: FSMContext, pool):
    """Обработка ответа на вопрос финального теста"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    answer_idx = int(callback.data.split("_")[-1])
    user_data = await state.get_data()

    questions = user_data.get('topic_test_questions', [])
    current_idx = user_data.get('topic_test_current', 0)
    answers = user_data.get('topic_test_answers', [])

    question = questions[current_idx]
    correct_idx = question['data'].get('correct_answer', 0)
    is_correct = (answer_idx == correct_idx)

    answers.append({
        'question_id': question['id'],
        'answer': answer_idx,
        'correct': is_correct
    })

    await state.update_data(
        topic_test_current=current_idx + 1,
        topic_test_answers=answers
    )

    feedback = "✅" if is_correct else "❌"
    await callback.answer(feedback, show_alert=False)

    await send_topic_test_question(callback.message, state, pool, vUserID)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"topic_test_ans|q:{current_idx}|correct:{is_correct}")


async def finish_topic_test(message, state: FSMContext, pool, vUserID):
    """Завершение финального теста темы"""
    pool_base, pool_log = pool
    user_data = await state.get_data()

    topic_id = user_data.get('topic_test_id')
    answers = user_data.get('topic_test_answers', [])

    correct_count = sum(1 for ans in answers if ans.get('correct'))
    total_count = len(answers)
    score = (correct_count / total_count * 100) if total_count > 0 else 0
    passed = score >= 80

    test_data = json.dumps(answers)
    var_query = f"""
        INSERT INTO t_curriculum_tests 
        (c_user_id, c_topic_id, c_test_type, c_score, c_max_score, c_passed, c_test_data)
        VALUES ({vUserID}, {topic_id}, 'final', {correct_count}, {total_count}, {passed}, '{test_data}')
    """
    await pgDB.fExec_UpdateQuery(pool_base, var_query)

    if passed:
        var_query = f"""
            UPDATE t_user_curriculum 
            SET 
                c_status = 'completed',
                c_completion_date = CURRENT_TIMESTAMP,
                c_progress_percent = 100
            WHERE c_user_id = {vUserID} AND c_topic_id = {topic_id}
        """
        await pgDB.fExec_UpdateQuery(pool_base, var_query)

        var_query = f"""
            SELECT c_topic_id 
            FROM t_user_curriculum
            WHERE c_user_id = {vUserID} 
                AND c_status = 'not_started'
            ORDER BY c_order_in_program
            LIMIT 1
        """
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

        has_next = bool(var_Arr)

        str_Msg = (
            f"🎉 <b>Поздравляем!</b>\n\n"
            f"Тема успешно завершена!\n"
            f"Результат: {correct_count}/{total_count} ({int(score)}%)\n\n"
            f"{'Готовы перейти к следующей теме?' if has_next else 'Вы завершили всю программу! 🏆'}"
        )

        builder = InlineKeyboardBuilder()
        if has_next:
            next_topic_id = var_Arr[0][0]
            builder.add(
                InlineKeyboardButton(text="➡️ Следующая тема", callback_data=f"start_next_topic_{next_topic_id}"))
        builder.add(InlineKeyboardButton(text="📚 Моя программа", callback_data="view_curriculum"))
        builder.adjust(1)
    else:
        str_Msg = (
            f"📚 <b>Еще немного!</b>\n\n"
            f"Результат: {correct_count}/{total_count} ({int(score)}%)\n"
            f"Для прохождения нужно 80%\n\n"
            f"Рекомендуем повторить материал и попробовать снова."
        )

        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="📖 Повторить тему", callback_data=f"topic_overview_{topic_id}"))
        builder.add(InlineKeyboardButton(text="🔄 Пересдать тест", callback_data=f"topic_test_{topic_id}"))
        builder.adjust(1)

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"topic_test_complete|score:{score}|passed:{passed}")


@r_curriculum.callback_query(F.data.startswith("start_next_topic_"))
async def start_next_topic(callback: types.CallbackQuery, state: FSMContext, pool):
    """Начать следующую тему"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    topic_id = int(callback.data.split("_")[-1])

    var_query = f"""
        UPDATE t_user_curriculum 
        SET c_status = 'in_progress', c_start_date = CURRENT_TIMESTAMP
        WHERE c_user_id = {vUserID} AND c_topic_id = {topic_id}
    """
    await pgDB.fExec_UpdateQuery(pool_base, var_query)

    await state.update_data(current_topic_id=topic_id)
    await show_topic_overview(callback.message, state, pool, vUserID, topic_id)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"start_next_topic|topic:{topic_id}")


# ==================== STATISTICS ====================

@r_curriculum.callback_query(F.data == "curriculum_stats")
async def curriculum_stats(callback: types.CallbackQuery, state: FSMContext, pool):
    """Статистика по программе"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    var_query = f"""
        SELECT 
            COUNT(*) as total_topics,
            SUM(CASE WHEN c_status = 'completed' THEN 1 ELSE 0 END) as completed_topics,
            SUM(CASE WHEN c_status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
            AVG(c_progress_percent) as avg_progress
        FROM t_user_curriculum
        WHERE c_user_id = {vUserID}
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if not var_Arr:
        await callback.answer("Статистика недоступна", show_alert=True)
        return

    total_topics, completed, in_progress, avg_progress = var_Arr[0]
    avg_progress = int(avg_progress) if avg_progress else 0

    var_query = f"""
        SELECT 
            COUNT(*) as total_tests,
            AVG(c_score / c_max_score * 100) as avg_score,
            SUM(CASE WHEN c_passed THEN 1 ELSE 0 END) as passed_tests
        FROM t_curriculum_tests
        WHERE c_user_id = {vUserID}
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    total_tests, avg_score, passed_tests = var_Arr[0] if var_Arr else (0, 0, 0)
    avg_score = int(avg_score) if avg_score else 0

    var_query = f"""
        SELECT SUM(c_time_spent_minutes)
        FROM t_user_module_progress
        WHERE c_user_id = {vUserID}
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
    total_minutes = var_Arr[0][0] if var_Arr and var_Arr[0][0] else 0
    hours = total_minutes // 60
    minutes = total_minutes % 60

    str_Msg = (
        f"📊 <b>Ваша статистика</b>\n\n"
        f"<b>Темы:</b>\n"
        f"• Всего: {total_topics}\n"
        f"• Завершено: {completed}\n"
        f"• В процессе: {in_progress}\n"
        f"• Средний прогресс: {avg_progress}%\n\n"
        f"<b>Тесты:</b>\n"
        f"• Пройдено: {total_tests}\n"
        f"• Успешно: {passed_tests}\n"
        f"• Средний балл: {avg_score}%\n\n"
        f"<b>Время обучения:</b>\n"
        f"{hours} ч {minutes} мин"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data="view_curriculum"))

    await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, "curriculum_stats")