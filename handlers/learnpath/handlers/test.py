"""
Обработчик финальных тестов модулей - LAZY VERSION
Генерирует вопросы "на лету" при показе пользователю
"""

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from typing import Dict, List, Optional
from datetime import datetime

import fpgDB as pgDB
from states import myState
from ..services.test_service import TestService

import logging
logger = logging.getLogger(__name__)

router = Router(name='module_test_handler')


class TestStates(StatesGroup):
    """Состояния прохождения теста"""
    waiting_for_start = State()
    in_test = State()
    viewing_results = State()


# ============================================================================
# НАЧАЛО ТЕСТА
# ============================================================================

async def launch_module_final_test(
        message: Message,
        state: FSMContext,
        pool_tuple,
        user_id: int,
        module_id: int
):
    """Запуск финального теста модуля (LAZY VERSION - вопросы генерируются при показе)"""
    
    pool_base, pool_log = pool_tuple
    test_service = TestService(pool_base)

    try:
        # ✅ Возвращает: (test_progress_id, templates, topics, config)
        # БЕЗ генерации вопросов!
        test_progress_id, templates, topics, config = await test_service.start_module_test(
            user_id=user_id,
            module_id=module_id
        )

        # ✅ Сохраняем в state: шаблоны, топики, пустой кэш для вопросов
        await state.update_data(
            test_progress_id=test_progress_id,
            module_id=module_id,
            templates=templates,  # Шаблоны для генерации
            topics=topics,        # Топики для каждого вопроса
            generated_questions={},  # Кэш сгенерированных вопросов
            current_question=0,
            start_time=datetime.now().isoformat(),
            config=config
        )

        await show_test_welcome(message, config)
        await state.set_state(TestStates.waiting_for_start)

    except ValueError as e:
        error_msg = str(e)

        if "Not all lessons completed" in error_msg:
            await message.answer(
                "⚠️ Вы еще не завершили все уроки модуля.\n"
                "Пожалуйста, пройдите все уроки перед финальным тестом."
            )
        elif "unfinished test" in error_msg.lower():
            await message.answer(
                "⚠️ У вас есть незавершенный тест.\n"
                "Хотите продолжить его?",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 Начать заново", callback_data="restart_test")]
                ])
            )
        else:
            await message.answer(f"❌ Ошибка при создании теста: {error_msg}")


async def show_test_welcome(message: Message, config: Dict):
    """Показать приветственное сообщение теста"""
    
    text = "📝 <b>Финальный тест модуля</b>\n\n"
    text += f"📌 <b>{config['test_name']}</b>\n\n"
    text += f"❓ Вопросов: <b>{config['total_questions']}</b>\n"
    text += f"✅ Проходной балл: <b>{config['passing_score']}%</b>\n"

    if config.get('time_limit_minutes'):
        text += f"⏱ Время: <b>{config['time_limit_minutes']} минут</b>\n"

    text += f"\n📊 Попытка: <b>#{config['attempt_number']}</b>\n\n"
    text += "⚠️ <b>Внимание!</b>\n"
    text += "• Каждый вопрос генерируется уникально под ваши интересы\n"
    text += "• Вы не сможете вернуться к предыдущим вопросам\n"
    text += "• При превышении лимита времени тест будет завершен\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Начать тест", callback_data="start_test_confirm")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="continue_learn")]
    ])

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "start_test_confirm")
async def start_test_confirmed(callback: CallbackQuery, state: FSMContext, pool):
    """Пользователь подтвердил начало теста"""
    
    await callback.answer()
    await state.set_state(TestStates.in_test)
    
    # ✅ Показываем первый вопрос (генерируется на лету)
    await show_question(callback.message, state, pool, question_num=1)


# ============================================================================
# ПОКАЗ ВОПРОСА - LAZY GENERATION
# ============================================================================

async def show_question(
        message: Message,
        state: FSMContext,
        pool,
        question_num: int
):
    """
    Показать вопрос пользователю
    
    ✅ LAZY: Вопрос генерируется здесь, если его еще нет в кэше
    """
    
    pool_base, pool_log = pool
    data = await state.get_data()
    config = data['config']
    total = config['total_questions']
    current_idx = question_num - 1

    # ✅ Получаем или генерируем вопрос
    question = await get_or_generate_question(
        state=state,
        question_idx=current_idx,
        pool_base=pool_base,
        user_id=message.chat.id
    )

    if not question:
        await message.answer(
            "❌ Ошибка при генерации вопроса. Попробуйте позже.",
            parse_mode=ParseMode.HTML
        )
        return

    # Формируем сообщение
    topic_badge = ""
    if question.get('topic_name'):
        topic_badge = f"📚 <i>{question['topic_name']}</i>\n"

    ai_badge = ""
    if question.get('is_ai_generated'):
        ai_badge = "🤖 "

    text = f"{ai_badge}❓ <b>Вопрос {question_num} / {total}</b>\n"
    text += topic_badge
    text += f"\n{question['question']}\n\n"

    for letter in ['A', 'B', 'C', 'D']:
        option = question['options'].get(letter)
        if option:
            text += f"<b>{letter})</b> {option}\n"

    # Проверка времени
    if config.get('time_limit_minutes'):
        start_time_str = data['start_time']
        start_time = datetime.fromisoformat(start_time_str)
        elapsed = (datetime.now() - start_time).total_seconds() / 60
        remaining = config['time_limit_minutes'] - elapsed

        if remaining > 0:
            text += f"\n⏱ Осталось времени: <b>{int(remaining)} мин</b>"
        else:
            await handle_test_timeout(message, state)
            return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="A", callback_data=f"answer_A_{question_num}"),
            InlineKeyboardButton(text="B", callback_data=f"answer_B_{question_num}"),
        ],
        [
            InlineKeyboardButton(text="C", callback_data=f"answer_C_{question_num}"),
            InlineKeyboardButton(text="D", callback_data=f"answer_D_{question_num}"),
        ]
    ])

    await state.update_data(question_start_time=datetime.now().isoformat())

    try:
        await message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except:
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


async def get_or_generate_question(
        state: FSMContext,
        question_idx: int,
        pool_base,
        user_id: int
) -> Optional[Dict]:
    """
    Получить вопрос из кэша или сгенерировать новый
    
    ✅ LAZY: Генерация происходит только при первом обращении к вопросу
    """
    
    user_data = await state.get_data()
    
    # Проверяем кэш
    generated_questions = user_data.get('generated_questions', {})
    
    if str(question_idx) in generated_questions:
        logger.info(f"⚡ Using cached question {question_idx}")
        return generated_questions[str(question_idx)]

    # Генерируем вопрос
    logger.info(f"🔄 Generating question {question_idx} on-demand...")
    
    templates = user_data.get('templates', [])
    topics = user_data.get('topics', [])
    module_id = user_data.get('module_id')

    if question_idx >= len(templates) or question_idx >= len(topics):
        logger.error(f"Question index {question_idx} out of range")
        return None

    template = templates[question_idx]
    topic = topics[question_idx]

    # Создаем test_service
    test_service = TestService(pool_base)
    
    # Получаем контекст модуля
    module_context = await test_service.get_module_context(module_id)

    # ✅ Генерируем вопрос
    try:
        generated_question = await test_service.generate_single_question(
            template=template,
            topic=topic,
            user_id=user_id,
            module_context=module_context
        )
        
        # Сохраняем в кэш
        generated_questions[str(question_idx)] = generated_question
        await state.update_data(generated_questions=generated_questions)
        
        logger.info(f"✅ Question {question_idx} generated and cached")
        return generated_question
        
    except Exception as e:
        logger.error(f"Error generating question {question_idx}: {e}")
        return None


# ============================================================================
# ОБРАБОТКА ОТВЕТА
# ============================================================================

@router.callback_query(F.data.startswith("answer_"))
async def handle_answer(callback: CallbackQuery, state: FSMContext, pool):
    """Обработка ответа пользователя на вопрос"""
    
    parts = callback.data.split("_")
    user_answer = parts[1]
    question_num = int(parts[2])

    pool_base, _ = pool
    user_id = callback.from_user.id

    data = await state.get_data()
    test_progress_id = data['test_progress_id']
    current_q = data['current_question']
    config = data['config']
    total = config['total_questions']

    if question_num != current_q + 1:
        await callback.answer("⚠️ Этот вопрос уже отвечен", show_alert=True)
        return

    # Получаем вопрос из кэша
    generated_questions = data.get('generated_questions', {})
    question = generated_questions.get(str(current_q))

    if not question:
        await callback.answer("❌ Ошибка: вопрос не найден", show_alert=True)
        return

    # Время на ответ
    time_spent = None
    question_start_time_str = data.get('question_start_time')
    if question_start_time_str:
        question_start_time = datetime.fromisoformat(question_start_time_str)
        time_spent = int((datetime.now() - question_start_time).total_seconds())

    # Сохраняем ответ
    test_service = TestService(pool_base)

    try:
        result = await test_service.submit_answer(
            test_progress_id=test_progress_id,
            question_number=question_num,
            user_answer=user_answer,
            question_data=question,
            time_spent_seconds=time_spent
        )

        is_correct = result['is_correct']

        if is_correct:
            await callback.answer("✅ Правильно!", show_alert=False)
            feedback_emoji = "✅"
        else:
            correct_letter = result['correct_answer']
            correct_option = question['options'][correct_letter]

            feedback_text = (
                f"❌ Неправильно\n\n"
                f"Правильный ответ: {correct_letter}) {correct_option}\n\n"
                f"💡 {result['explanation']}"
            )
            await callback.answer(feedback_text, show_alert=True)
            feedback_emoji = "❌"

        # Зачеркиваем вопрос
        try:
            await callback.message.edit_text(
                f"{feedback_emoji} <s>{callback.message.text}</s>",
                parse_mode="HTML"
            )
        except:
            pass

        current_q += 1
        await state.update_data(current_question=current_q)

        # Следующий вопрос или завершение
        if current_q < total:
            await show_question(callback.message, state, pool, current_q + 1)
        else:
            await finalize_test(callback.message, state, pool_base)

    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        await callback.answer(f"❌ Ошибка при сохранении ответа: {e}", show_alert=True)


# ============================================================================
# ЗАВЕРШЕНИЕ ТЕСТА
# ============================================================================

async def finalize_test(message: Message, state: FSMContext, pool_base):
    """Завершить тест и показать результаты"""
    
    data = await state.get_data()
    test_progress_id = data['test_progress_id']

    processing_msg = await message.answer("⏳ Подсчитываем результаты...")

    try:
        test_service = TestService(pool_base)
        results = await test_service.complete_test(test_progress_id=test_progress_id)
        
        await processing_msg.delete()
        await show_test_results(message, state, results)
        await state.set_state(TestStates.viewing_results)

    except Exception as e:
        await processing_msg.edit_text(f"❌ Ошибка при завершении теста: {e}")


async def show_test_results(message: Message, state: FSMContext, results: Dict):
    """Показать результаты теста"""
    
    passed = results['passed']
    score = results['score']
    max_score = results['max_score']
    percentage = results['percentage']
    passing_score = results['passing_score']

    if passed:
        text = "🎉 <b>Поздравляем! Тест пройден!</b>\n\n"
        emoji = "✅"
    else:
        text = "📝 <b>Тест не пройден</b>\n\n"
        emoji = "❌"

    text += f"{emoji} Ваш результат: <b>{score} / {max_score}</b> ({percentage}%)\n"
    text += f"📊 Проходной балл: <b>{passing_score}%</b>\n"

    if results.get('time_taken_minutes'):
        text += f"⏱ Время: <b>{results['time_taken_minutes']} мин</b>\n"

    #if results.get('topic_stats'):
        #text += "\n📈 <b>Результаты по темам:</b>\n"
        #topic_stats = results['topic_stats']
        #sorted_topics = sorted(topic_stats.items(), key=lambda x: x[1]['percentage'])

        #for topic_id, stats in sorted_topics[:5]:
        #    emoji_topic = "✅" if stats['percentage'] >= 70 else "⚠️"
        #    text += f"{emoji_topic} {stats['topic_name']}: {stats['correct']}/{stats['total']} ({stats['percentage']}%)\n"

    if not passed:
        text += "\n💡 <b>Рекомендации:</b>\n"
        if results.get('failed_topics'):
            text += "• Повторите уроки, где возникли сложности\n"
        text += "• Вы можете пройти тест повторно\n"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Пройти тест заново", callback_data="restart_test_new")],
            [InlineKeyboardButton(text="📚 Вернуться к урокам", callback_data="continue_learn")]
        ])
    else:
        text += "\n🎓 Модуль успешно завершен!\n"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Следующий модуль", callback_data="continue_learn")]
        ])

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


# ============================================================================
# ПРОДОЛЖЕНИЕ И ПЕРЕЗАПУСК
# ============================================================================

@router.callback_query(F.data == "restart_test")
async def restart_test_handler(callback: CallbackQuery, state: FSMContext, pool):
    """Удаляет незавершенный тест и запускает новый"""
    
    await callback.answer()

    pool_base, pool_log = pool
    user_id = callback.from_user.id

    data = await state.get_data()
    module_id = data.get('module_id')

    if not module_id:
        test_service = TestService(pool_base)
        pending_test = await test_service.get_pending_test_info(user_id)
        if pending_test:
            module_id = pending_test['module_id']

    if not module_id:
        await callback.message.answer("❌ Ошибка: не найден незавершенный тест")
        return

    test_service = TestService(pool_base)
    deleted = await test_service.delete_pending_test(user_id, module_id)

    if not deleted:
        await callback.message.answer("❌ Ошибка при удалении теста")
        return

    await state.clear()

    try:
        await callback.message.edit_text("🔄 Тест сброшен. Запускаем новый...")
    except:
        await callback.message.answer("🔄 Тест сброшен. Запускаем новый...")

    await launch_module_final_test(
        callback.message, state, (pool_base, pool_log), user_id, module_id
    )


@router.callback_query(F.data == "restart_test_new")
async def restart_test_new(callback: CallbackQuery, state: FSMContext, pool):
    """Начать тест заново (после провала)"""
    
    await callback.answer()

    pool_base, pool_log = pool
    user_id = callback.from_user.id
    data = await state.get_data()

    module_id = data.get('module_id')
    if not module_id and data.get('config'):
        module_id = data['config'].get('module_id')

    if not module_id:
        await callback.message.answer("❌ Ошибка: не найден ID модуля")
        return

    await launch_module_final_test(
        message=callback.message,
        state=state,
        pool_tuple=(pool_base, pool_log),
        user_id=user_id,
        module_id=module_id
    )


# ============================================================================
# ТАЙМАУТ
# ============================================================================

async def handle_test_timeout(message: Message, state: FSMContext):
    """Обработка истечения времени теста"""
    
    text = "⏰ <b>Время теста истекло!</b>\n\n"
    text += "К сожалению, вы не успели ответить на все вопросы.\n"
    text += "Тест будет помечен как проваленный.\n\n"
    text += "Вы можете пройти тест повторно."

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти заново", callback_data="restart_test_new")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="continue_learn")]
    ])

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    await state.clear()
