"""
Handlers для адаптивного тестирования уровня английского
Версия 2.1 - 3-фазный алгоритм с inference + DUPLICATE PREVENTION
"""

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
import json
from typing import Dict, List, Tuple, Optional

from states import myState
import fpgDB as pgDB

router = Router(name='learnpath_assessment')

# ============================================================================
# КОНСТАНТЫ
# ============================================================================

QLVL_MAP = {
    4: 'A1',
    5: 'A2',
    6: 'B1',
    7: 'B2',
    8: 'C1'
}

PHASE_1_CONFIG = {
    4: {'initial_questions': 3, 'threshold_high': 3, 'threshold_low': 1},  # A1
    5: {'initial_questions': 3, 'threshold_high': 3, 'threshold_low': 1},  # A2
    6: {'initial_questions': 3, 'threshold_high': 3, 'threshold_low': 1},  # B1
    7: {'initial_questions': 3, 'threshold_high': 2, 'threshold_low': 1},  # B2
    8: {'initial_questions': 3, 'threshold_high': 2, 'threshold_low': 1},  # C1
}


# ============================================================================
# HANDLERS
# ============================================================================

@router.callback_query(F.data == "learnpath_start")
async def learnpath_init(callback: types.CallbackQuery, state: FSMContext, pool):
    """Начало процесса создания персональной программы"""
    await learnpath_init_handler(callback.message, state, pool)
    await callback.answer()


async def learnpath_init_handler(message, state: FSMContext, pool):
    """Универсальная функция начала создания программы"""
    pool_base, pool_log = pool
    vUserID = message.chat.id
    await state.set_state(myState.learnpath_assessment)

    str_Msg = (
        f"🎓 <b>Персональная программа обучения</b>\n\n"
        f"Давайте создадим программу, которая идеально подойдет именно вам!\n\n"
        f"Это займет 5-10 минут и включает:\n"
        f"• Адаптивную оценку текущего уровня\n"
        f"• Определение ваших интересов\n"
        f"• Формирование индивидуального плана\n\n"
        f"Готовы начать?"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🚀 Начать", callback_data="assess_level_intro"))
    builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data="menu"))
    builder.adjust(1)

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, "learnpath_init")


@router.callback_query(F.data == "assess_level_intro")
async def assess_level_intro(callback: types.CallbackQuery, state: FSMContext, pool):
    """Введение в тестирование уровня"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    str_Msg = (
        f"📊 <b>Шаг 1: Определение уровня</b>\n\n"
        f"Сейчас мы проведем <b>адаптивный тест</b> для точного определения вашего уровня.\n\n"
        f"<b>Как это работает:</b>\n"
        f"• Тест адаптируется под ваши ответы\n"
        f"• От 10 до 20 вопросов (зависит от результатов)\n"
        f"• 3 фазы: быстрая оценка → детализация → проверка границ\n\n"
        f"Не переживайте, если вопросы кажутся сложными - это нормально!\n\n"
        f"Готовы?"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Начать тест", callback_data="assess_level_start"))
    builder.add(
        InlineKeyboardButton(text="⏭️ Пропустить (использовать текущий)", callback_data="assess_interests_intro"))
    builder.adjust(1)

    await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, "assess_level_intro")


@router.callback_query(F.data == "assess_level_start")
async def assess_level_start(callback: types.CallbackQuery, state: FSMContext, pool):
    """Начало адаптивного теста уровня"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    # Инициализация теста - ФАЗА 1
    await state.update_data(
        # Общие данные
        test_phase=1,  # 1=быстрая оценка, 2=детализация, 3=граничная проверка
        total_questions_asked=0,

        # Фаза 1: быстрая оценка
        current_qlvl=4,  # Начинаем с A1
        phase1_qlvl_results={},  # {qlvl_id: {'correct': int, 'total': int}}

        # Покрытие модулей
        module_coverage={},  # {module_id: {'correct': int, 'attempts': int, 'weight_sum': float}}

        # Все ответы
        all_answers=[],

        # Слабые зоны для фазы 2
        weak_modules=[],

        # 🔥 TRACKING: Отслеживание использованных вопросов
        used_question_ids=[],  # Список всех использованных c_question_id
        used_question_numbers=[],  # Список всех использованных c_number
    )

    await send_phase1_question(callback.message, state, pool, vUserID)
    await pgDB.fExec_LogQuery(pool_log, vUserID, "assess_level_start|phase:1")


# ============================================================================
# ФАЗА 1: БЫСТРАЯ ОЦЕНКА УРОВНЯ
# ============================================================================

async def send_phase1_question(message, state: FSMContext, pool, vUserID):
    """Отправка вопроса в фазе 1 - быстрая оценка уровня"""
    pool_base, pool_log = pool
    user_data = await state.get_data()

    current_qlvl = user_data.get('current_qlvl', 4)
    total_asked = user_data.get('total_questions_asked', 0)
    phase1_results = user_data.get('phase1_qlvl_results', {})

    # 🔥 TRACKING: Получаем списки использованных вопросов
    used_question_ids = user_data.get('used_question_ids', [])
    used_question_numbers = user_data.get('used_question_numbers', [])

    # 🎯 ПРИОРИТЕТ 1: Найти НОВЫЙ c_number (непроверенная тема)
    used_ids_str = ','.join(map(str, used_question_ids)) if used_question_ids else '-1'
    used_numbers_str = ','.join(map(str, used_question_numbers)) if used_question_numbers else '-1'

    var_query = f"""
        SELECT 
            q.c_question_id,
            q.c_number,
            q.c_question_text,
            q.c_question_data,
            q.c_question_metadata
        FROM t_lp_init_assess_questions q
        JOIN t_lp_init_assess_numbers qn ON q.c_number = qn.c_number
        WHERE qn.c_qlvl_id = {current_qlvl}
            AND qn.c_is_active = true
            AND q.c_question_type = 'multiple_choice'
            AND q.c_number NOT IN ({used_numbers_str})
            AND q.c_question_id NOT IN ({used_ids_str})
        ORDER BY RANDOM()
        LIMIT 1
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if var_Arr:
        # Нашли новую тему - это приоритет!
        await process_selected_question(message, state, var_Arr[0], current_qlvl, total_asked, phase1_results)
        return

    # 🔄 ПРИОРИТЕТ 2: Если новых тем нет - разная вариация уже использованной темы
    if used_question_numbers:
        used_numbers_str = ','.join(map(str, used_question_numbers))
        used_ids_str = ','.join(map(str, used_question_ids)) if used_question_ids else '-1'

        var_query = f"""
            SELECT 
                q.c_question_id,
                q.c_number,
                q.c_question_text,
                q.c_question_data,
                q.c_question_metadata
            FROM t_lp_init_assess_questions q
            JOIN t_lp_init_assess_numbers qn ON q.c_number = qn.c_number
            WHERE qn.c_qlvl_id = {current_qlvl}
                AND qn.c_is_active = true
                AND q.c_question_type = 'multiple_choice'
                AND q.c_number IN ({used_numbers_str})
                AND q.c_question_id NOT IN ({used_ids_str})
            ORDER BY RANDOM()
            LIMIT 1
        """
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

        if var_Arr:
            # Все новые темы проверены, берем разную вариацию
            await process_selected_question(message, state, var_Arr[0], current_qlvl, total_asked, phase1_results)
            return

    # ⛔ ПРИОРИТЕТ 3: Все вопросы исчерпаны - переходим к следующей фазе
    await pgDB.fExec_LogQuery(pool_log, vUserID,
                              f"phase1_exhausted|qlvl:{current_qlvl}|used_numbers:{len(used_question_numbers)}|used_ids:{len(used_question_ids)}")
    await transition_to_phase2(message, state, pool, vUserID)


async def process_selected_question(message, state: FSMContext, question_row, current_qlvl, total_asked,
                                    phase1_results):
    """Обработка выбранного вопроса и отправка пользователю"""
    user_data = await state.get_data()

    question_id = question_row[0]
    question_number = question_row[1]
    question_text = question_row[2]
    question_data = json.loads(question_row[3])
    question_metadata = json.loads(question_row[4]) if question_row[4] else {}

    # 🔥 TRACKING: Добавляем в использованные
    used_question_ids = user_data.get('used_question_ids', [])
    used_question_numbers = user_data.get('used_question_numbers', [])

    used_question_ids.append(question_id)
    if question_number not in used_question_numbers:
        used_question_numbers.append(question_number)

    # Сохраняем текущий вопрос + обновляем tracking
    await state.update_data(
        current_question_id=question_id,
        current_question_number=question_number,
        current_qlvl=current_qlvl,
        used_question_ids=used_question_ids,
        used_question_numbers=used_question_numbers
    )

    # Текущая статистика по уровню
    qlvl_stats = phase1_results.get(str(current_qlvl), {'correct': 0, 'total': 0})

    str_Msg = (
        f"📊 <b>Фаза 1: Быстрая оценка</b>\n"
        f"Уровень: {QLVL_MAP[current_qlvl]} | Вопрос {total_asked + 1}\n\n"
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


@router.callback_query(F.data.startswith("assess_answer_"))
async def process_answer(callback: types.CallbackQuery, state: FSMContext, pool):
    """Обработка ответа на вопрос теста (все фазы)"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    answer_idx = int(callback.data.split("_")[-1])
    user_data = await state.get_data()

    question_id = user_data.get('current_question_id')
    question_number = user_data.get('current_question_number')
    current_qlvl = user_data.get('current_qlvl')
    test_phase = user_data.get('test_phase', 1)

    # Получаем правильный ответ и покрываемые модули
    var_query = f"""
        SELECT 
            q.c_question_data,
            (
                SELECT json_agg(
                    json_build_object(
                        'module_id', qnm.c_module_id,
                        'coverage_type', qnm.c_coverage_type,
                        'coverage_weight', qnm.c_coverage_weight
                    )
                )
                FROM t_lp_module_map_question_number qnm
                WHERE qnm.c_number = q.c_number
            ) as covered_modules
        FROM t_lp_init_assess_questions q
        WHERE q.c_question_id = {question_id}
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
    question_data = json.loads(var_Arr[0][0])
    covered_modules = json.loads(var_Arr[0][1]) if var_Arr[0][1] else []

    correct_idx = question_data.get('correct_answer', 0)
    is_correct = (answer_idx == correct_idx)

    # Обновляем покрытие модулей
    module_coverage = user_data.get('module_coverage', {})
    for mod in covered_modules:
        mod_id = str(mod['module_id'])
        weight = float(mod['coverage_weight'])

        if mod_id not in module_coverage:
            module_coverage[mod_id] = {'correct': 0, 'attempts': 0, 'weight_sum': 0.0}

        module_coverage[mod_id]['attempts'] += 1
        module_coverage[mod_id]['weight_sum'] += weight
        if is_correct:
            module_coverage[mod_id]['correct'] += weight

    # Сохраняем ответ
    all_answers = user_data.get('all_answers', [])
    all_answers.append({
        'question_id': question_id,
        'question_number': question_number,
        'answer': answer_idx,
        'correct': is_correct,
        'qlvl': current_qlvl,
        'phase': test_phase,
        'covered_modules': covered_modules
    })

    total_asked = user_data.get('total_questions_asked', 0) + 1

    await state.update_data(
        module_coverage=module_coverage,
        all_answers=all_answers,
        total_questions_asked=total_asked
    )

    # Feedback
    feedback = "✅ Правильно!" if is_correct else f"❌ Неверно. Правильный ответ: {chr(65 + correct_idx)}"
    await callback.answer(feedback, show_alert=False)

    # Маршрутизация по фазам
    if test_phase == 1:
        await process_phase1_answer(callback.message, state, pool, vUserID, is_correct)
    elif test_phase == 2:
        await process_phase2_answer(callback.message, state, pool, vUserID, is_correct)
    elif test_phase == 3:
        await process_phase3_answer(callback.message, state, pool, vUserID, is_correct)

    await pgDB.fExec_LogQuery(pool_log, vUserID,
                              f"assess_answer|phase:{test_phase}|qlvl:{current_qlvl}|correct:{is_correct}")


async def process_phase1_answer(message, state: FSMContext, pool, vUserID, is_correct: bool):
    """Обработка ответа в фазе 1 и определение следующего шага"""
    user_data = await state.get_data()
    current_qlvl = user_data.get('current_qlvl', 4)
    phase1_results = user_data.get('phase1_qlvl_results', {})

    # Обновляем статистику текущего уровня
    qlvl_key = str(current_qlvl)
    if qlvl_key not in phase1_results:
        phase1_results[qlvl_key] = {'correct': 0, 'total': 0}

    phase1_results[qlvl_key]['total'] += 1
    if is_correct:
        phase1_results[qlvl_key]['correct'] += 1

    await state.update_data(phase1_qlvl_results=phase1_results)

    # Логика принятия решения
    stats = phase1_results[qlvl_key]
    config = PHASE_1_CONFIG[current_qlvl]

    # Проверка: достигли ли мы минимального количества вопросов для уровня
    if stats['total'] < config['initial_questions']:
        # Продолжаем задавать вопросы текущего уровня
        await send_phase1_question(message, state, pool, vUserID)
        return

    # Анализ результатов
    correct_count = stats['correct']

    if correct_count <= config['threshold_low']:
        # Слабые результаты - останавливаемся, это его уровень
        await finalize_level_assessment(message, state, pool, vUserID, current_qlvl)
        return

    elif correct_count == config['threshold_high']:
        # Отличные результаты - пропускаем к следующему уровню
        if current_qlvl < 8:  # C1 - максимум
            await state.update_data(current_qlvl=current_qlvl + 1)
            await send_phase1_question(message, state, pool, vUserID)
        else:
            # Достигли максимального уровня
            await finalize_level_assessment(message, state, pool, vUserID, 8)
        return

    else:
        # Средние результаты (2 из 3) - нужно больше вопросов
        if stats['total'] < 5:
            # Задаем еще 2 вопроса текущего уровня
            await send_phase1_question(message, state, pool, vUserID)
        else:
            # После 5 вопросов принимаем решение
            accuracy = correct_count / stats['total']
            if accuracy >= 0.6:
                # Можем попробовать следующий уровень
                if current_qlvl < 8:
                    await state.update_data(current_qlvl=current_qlvl + 1)
                    await send_phase1_question(message, state, pool, vUserID)
                else:
                    await finalize_level_assessment(message, state, pool, vUserID, 8)
            else:
                # Остаемся на текущем
                await finalize_level_assessment(message, state, pool, vUserID, current_qlvl)


# ============================================================================
# ФАЗА 2: ДЕТАЛЬНОЕ СКАНИРОВАНИЕ ПРОБЛЕМНЫХ ЗОН
# ============================================================================

async def transition_to_phase2(message, state: FSMContext, pool, vUserID):
    """Переход к фазе 2 - детальное сканирование"""
    pool_base, pool_log = pool
    user_data = await state.get_data()

    # Определяем определенный уровень из фазы 1
    phase1_results = user_data.get('phase1_qlvl_results', {})
    determined_level = determine_level_from_phase1(phase1_results)

    # Анализируем покрытие модулей и находим слабые зоны
    module_coverage = user_data.get('module_coverage', {})
    weak_modules = identify_weak_modules(module_coverage, determined_level)

    if not weak_modules:
        # Нет слабых зон - переходим к фазе 3 или завершаем
        await transition_to_phase3(message, state, pool, vUserID, determined_level)
        return

    # Обновляем состояние для фазы 2
    await state.update_data(
        test_phase=2,
        determined_level=determined_level,
        weak_modules=weak_modules,
        phase2_module_index=0
    )

    # Информируем пользователя
    str_Msg = (
        f"📋 <b>Фаза 2: Детальная проверка</b>\n\n"
        f"Ваш базовый уровень: <b>{QLVL_MAP[determined_level]}</b>\n\n"
        f"Обнаружено {len(weak_modules)} тем, требующих дополнительной проверки.\n"
        f"Зададим несколько уточняющих вопросов..."
    )

    await message.answer(str_Msg, parse_mode=ParseMode.HTML)
    await send_phase2_question(message, state, pool, vUserID)
    await pgDB.fExec_LogQuery(pool_log, vUserID,
                              f"assess_phase2_start|level:{determined_level}|weak:{len(weak_modules)}")


def determine_level_from_phase1(phase1_results: Dict) -> int:
    """Определить уровень на основе результатов фазы 1"""
    max_passed_level = 4  # Начинаем с A1

    for qlvl_str, stats in phase1_results.items():
        qlvl = int(qlvl_str)
        accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0

        if accuracy >= 0.6:  # Если прошел уровень >= 60%
            max_passed_level = max(max_passed_level, qlvl)

    return max_passed_level


def identify_weak_modules(module_coverage: Dict, determined_level: int) -> List[int]:
    """Идентифицировать слабые модули для дополнительной проверки"""
    weak_modules = []

    for mod_id_str, stats in module_coverage.items():
        if stats['attempts'] == 0:
            continue

        # Accuracy с учетом веса
        accuracy = stats['correct'] / stats['weight_sum'] if stats['weight_sum'] > 0 else 0

        # Модуль слабый, если accuracy < 0.5 и было хотя бы одно покрытие
        if accuracy < 0.5 and stats['attempts'] > 0:
            weak_modules.append(int(mod_id_str))

    return weak_modules[:5]  # Максимум 5 слабых модулей для проверки


async def send_phase2_question(message, state: FSMContext, pool, vUserID):
    """Отправка целевого вопроса в фазе 2"""
    pool_base, pool_log = pool
    user_data = await state.get_data()

    weak_modules = user_data.get('weak_modules', [])
    phase2_index = user_data.get('phase2_module_index', 0)

    # 🔥 TRACKING: Получаем списки использованных вопросов
    used_question_ids = user_data.get('used_question_ids', [])
    used_question_numbers = user_data.get('used_question_numbers', [])

    if phase2_index >= len(weak_modules):
        # Закончили проверку слабых зон
        determined_level = user_data.get('determined_level', 4)
        await transition_to_phase3(message, state, pool, vUserID, determined_level)
        return

    target_module_id = weak_modules[phase2_index]

    # 🎯 ПРИОРИТЕТ 1: Найти вопрос с НОВЫМ c_number для этого модуля
    used_ids_str = ','.join(map(str, used_question_ids)) if used_question_ids else '-1'
    used_numbers_str = ','.join(map(str, used_question_numbers)) if used_question_numbers else '-1'

    var_query = f"""
        SELECT 
            q.c_question_id,
            q.c_number,
            q.c_question_text,
            q.c_question_data,
            q.c_qlvl_id
        FROM t_lp_init_assess_questions q
        JOIN t_lp_module_map_question_number qnm ON q.c_number = qnm.c_number
        WHERE qnm.c_module_id = {target_module_id}
            AND qnm.c_coverage_type = 'primary'
            AND q.c_question_type = 'multiple_choice'
            AND q.c_number NOT IN ({used_numbers_str})
            AND q.c_question_id NOT IN ({used_ids_str})
        ORDER BY RANDOM()
        LIMIT 1
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if var_Arr:
        # Нашли вопрос с новой темой
        question_id = var_Arr[0][0]
        question_number = var_Arr[0][1]
        question_text = var_Arr[0][2]
        question_data = json.loads(var_Arr[0][3])
        question_qlvl = var_Arr[0][4]

        # 🔥 TRACKING: Добавляем в использованные
        used_question_ids.append(question_id)
        if question_number not in used_question_numbers:
            used_question_numbers.append(question_number)

        await state.update_data(
            current_question_id=question_id,
            current_question_number=question_number,
            current_qlvl=question_qlvl,
            used_question_ids=used_question_ids,
            used_question_numbers=used_question_numbers
        )

        total_asked = user_data.get('total_questions_asked', 0)

        str_Msg = (
            f"🔍 <b>Фаза 2: Детализация</b>\n"
            f"Проверяем слабую зону {phase2_index + 1}/{len(weak_modules)} | Всего: {total_asked + 1}\n\n"
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
        return

    # 🔄 ПРИОРИТЕТ 2: Разная вариация уже использованной темы для этого модуля
    used_ids_str = ','.join(map(str, used_question_ids)) if used_question_ids else '-1'

    var_query = f"""
        SELECT 
            q.c_question_id,
            q.c_number,
            q.c_question_text,
            q.c_question_data,
            q.c_qlvl_id
        FROM t_lp_init_assess_questions q
        JOIN t_lp_module_map_question_number qnm ON q.c_number = qnm.c_number
        WHERE qnm.c_module_id = {target_module_id}
            AND qnm.c_coverage_type = 'primary'
            AND q.c_question_type = 'multiple_choice'
            AND q.c_question_id NOT IN ({used_ids_str})
        ORDER BY RANDOM()
        LIMIT 1
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if var_Arr:
        # Нашли разную вариацию
        question_id = var_Arr[0][0]
        question_number = var_Arr[0][1]
        question_text = var_Arr[0][2]
        question_data = json.loads(var_Arr[0][3])
        question_qlvl = var_Arr[0][4]

        used_question_ids.append(question_id)

        await state.update_data(
            current_question_id=question_id,
            current_question_number=question_number,
            current_qlvl=question_qlvl,
            used_question_ids=used_question_ids
        )

        total_asked = user_data.get('total_questions_asked', 0)

        str_Msg = (
            f"🔍 <b>Фаза 2: Детализация</b>\n"
            f"Проверяем слабую зону {phase2_index + 1}/{len(weak_modules)} | Всего: {total_asked + 1}\n\n"
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
        return

    # ⛔ Нет вопросов для этого модуля - пропускаем
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"phase2_skip_module|module:{target_module_id}|no_questions")
    await state.update_data(phase2_module_index=phase2_index + 1)
    await send_phase2_question(message, state, pool, vUserID)


async def process_phase2_answer(message, state: FSMContext, pool, vUserID, is_correct: bool):
    """Обработка ответа в фазе 2"""
    user_data = await state.get_data()
    phase2_index = user_data.get('phase2_module_index', 0)

    # Переходим к следующему слабому модулю
    await state.update_data(phase2_module_index=phase2_index + 1)
    await send_phase2_question(message, state, pool, vUserID)


# ============================================================================
# ФАЗА 3: ГРАНИЧНАЯ ПРОВЕРКА
# ============================================================================

async def transition_to_phase3(message, state: FSMContext, pool, vUserID, determined_level: int):
    """Переход к фазе 3 - граничная проверка"""
    pool_base, pool_log = pool

    # Проверяем, готов ли студент к следующему уровню
    if determined_level >= 8:  # C1 - максимум
        await finalize_level_assessment(message, state, pool, vUserID, determined_level)
        return

    next_level = determined_level + 1

    await state.update_data(
        test_phase=3,
        boundary_level=next_level,
        phase3_questions_asked=0,
        phase3_correct=0
    )

    str_Msg = (
        f"🎯 <b>Фаза 3: Граничная проверка</b>\n\n"
        f"Проверим, готовы ли вы к уровню <b>{QLVL_MAP[next_level]}</b>\n"
        f"Зададим 3-5 вопросов следующего уровня..."
    )

    await message.answer(str_Msg, parse_mode=ParseMode.HTML)
    await send_phase3_question(message, state, pool, vUserID)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"assess_phase3_start|next_level:{next_level}")


async def send_phase3_question(message, state: FSMContext, pool, vUserID):
    """Отправка вопроса следующего уровня в фазе 3"""
    pool_base, pool_log = pool
    user_data = await state.get_data()

    boundary_level = user_data.get('boundary_level')
    phase3_asked = user_data.get('phase3_questions_asked', 0)

    # 🔥 TRACKING: Получаем списки использованных вопросов
    used_question_ids = user_data.get('used_question_ids', [])

    # 🔥 TRACKING: Получаем неиспользованный вопрос следующего уровня
    used_ids_str = ','.join(map(str, used_question_ids)) if used_question_ids else '-1'

    var_query = f"""
        SELECT 
            q.c_question_id,
            q.c_number,
            q.c_question_text,
            q.c_question_data
        FROM t_lp_init_assess_questions q
        JOIN t_lp_init_assess_numbers qn ON q.c_number = qn.c_number
        WHERE qn.c_qlvl_id = {boundary_level}
            AND qn.c_is_active = true
            AND q.c_question_type = 'multiple_choice'
            AND q.c_question_id NOT IN ({used_ids_str})
        ORDER BY RANDOM()
        LIMIT 1
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    if not var_Arr:
        # Нет неиспользованных вопросов - завершаем фазу 3
        determined_level = user_data.get('determined_level', 4)
        await finalize_level_assessment(message, state, pool, vUserID, determined_level)
        return

    question_id = var_Arr[0][0]
    question_number = var_Arr[0][1]
    question_text = var_Arr[0][2]
    question_data = json.loads(var_Arr[0][3])

    # 🔥 TRACKING: Добавляем в использованные
    used_question_ids.append(question_id)

    await state.update_data(
        current_question_id=question_id,
        current_question_number=question_number,
        current_qlvl=boundary_level,
        used_question_ids=used_question_ids
    )

    total_asked = user_data.get('total_questions_asked', 0)

    str_Msg = (
        f"⚡ <b>Фаза 3: Граничная проверка</b>\n"
        f"Уровень: {QLVL_MAP[boundary_level]} | Вопрос {phase3_asked + 1}/5 | Всего: {total_asked + 1}\n\n"
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


async def process_phase3_answer(message, state: FSMContext, pool, vUserID, is_correct: bool):
    """Обработка ответа в фазе 3"""
    user_data = await state.get_data()
    phase3_asked = user_data.get('phase3_questions_asked', 0) + 1
    phase3_correct = user_data.get('phase3_correct', 0) + (1 if is_correct else 0)

    await state.update_data(
        phase3_questions_asked=phase3_asked,
        phase3_correct=phase3_correct
    )

    # Логика завершения фазы 3
    if phase3_asked >= 3:
        accuracy = phase3_correct / phase3_asked
        determined_level = user_data.get('determined_level', 4)
        boundary_level = user_data.get('boundary_level')

        if accuracy >= 0.6:
            # Готов к следующему уровню
            final_level = boundary_level
        else:
            # Нужно укрепить текущий
            final_level = determined_level

        await finalize_level_assessment(message, state, pool, vUserID, final_level)
    elif phase3_asked < 5:
        # Продолжаем, максимум 5 вопросов
        await send_phase3_question(message, state, pool, vUserID)
    else:
        # Достигли лимита
        determined_level = user_data.get('determined_level', 4)
        phase3_accuracy = phase3_correct / 5
        final_level = user_data.get('boundary_level') if phase3_accuracy >= 0.6 else determined_level
        await finalize_level_assessment(message, state, pool, vUserID, final_level)


# ============================================================================
# ЗАВЕРШЕНИЕ ТЕСТА И INFERENCE
# ============================================================================

async def finalize_level_assessment(message, state: FSMContext, pool, vUserID, final_level: int):
    """Завершение теста с inference и сохранением результатов"""
    pool_base, pool_log = pool
    user_data = await state.get_data()

    all_answers = user_data.get('all_answers', [])
    module_coverage = user_data.get('module_coverage', {})
    total_asked = len(all_answers)
    correct_count = sum(1 for a in all_answers if a['correct'])

    # ========== INFERENCE ==========
    # Применяем логический вывод для непроверенных модулей
    inferred_modules = await apply_inference(pool_base, module_coverage, final_level)

    # Объединяем проверенные и выведенные модули
    all_module_knowledge = {**module_coverage}
    for mod_id, inference_score in inferred_modules.items():
        if mod_id not in all_module_knowledge:
            all_module_knowledge[mod_id] = {
                'correct': inference_score,
                'attempts': 0,  # 0 = inferred, not tested
                'weight_sum': 1.0,
                'inference_score': inference_score
            }

    # Сохраняем результат теста в БД
    test_data = {
        'answers': all_answers,
        'module_coverage': module_coverage,
        'inferred_modules': inferred_modules,
        'phase1_results': user_data.get('phase1_qlvl_results', {}),
        'weak_modules': user_data.get('weak_modules', []),
        'phase3_accuracy': user_data.get('phase3_correct', 0) / max(user_data.get('phase3_questions_asked', 1), 1)
    }

    test_data_json = json.dumps(test_data).replace("'", "''")

    var_query = f"""
        INSERT INTO t_lp_init_assess_user_results 
        (c_user_id, c_topic_id, c_test_type, c_score, c_max_score, c_passed, c_test_data)
        VALUES ({vUserID}, NULL, 'entry', {correct_count}, {total_asked}, true, '{test_data_json}')
    """
    await pgDB.fExec_UpdateQuery(pool_base, var_query)

    # Обновляем уровень пользователя
    var_query = f"""
        UPDATE t_user_paramssingle 
        SET c_ups_eng_level = {final_level}
        WHERE c_ups_user_id = {vUserID}
    """
    await pgDB.fExec_UpdateQuery(pool_base, var_query)

    # Сохраняем для следующих шагов
    await state.update_data(
        assessed_level=final_level,
        all_module_knowledge=all_module_knowledge
    )

    # Формируем отчет
    accuracy = correct_count / total_asked if total_asked > 0 else 0
    tested_modules = len([m for m in module_coverage.values() if m['attempts'] > 0])
    inferred_count = len(inferred_modules)

    str_Msg = (
        f"🎉 <b>Тест завершен!</b>\n\n"
        f"📊 <b>Результаты:</b>\n"
        f"• Всего вопросов: {total_asked}\n"
        f"• Правильных ответов: {correct_count} ({int(accuracy * 100)}%)\n"
        f"• Проверено модулей: {tested_modules}\n"
        f"• Выведено модулей: {inferred_count}\n\n"
        f"🎯 <b>Ваш уровень: {QLVL_MAP[final_level]}</b>\n\n"
        f"Теперь перейдем к определению ваших интересов!"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="➡️ Далее", callback_data="assess_interests_intro"))

    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID,
                              f"level_assessment_complete|level:{final_level}|score:{correct_count}/{total_asked}|modules:{tested_modules}+{inferred_count}")


async def apply_inference(pool_base, module_coverage: Dict, final_level: int) -> Dict[str, float]:
    """
    Применить логический вывод для определения знания непроверенных модулей

    Возвращает: {module_id: inference_score} где score от 0.0 до 1.0
    """
    # Получаем все модули с prerequisites
    var_query = """
        SELECT c_module_id, c_module_name, c_qlvl_id, c_content
        FROM t_lp_module
        WHERE c_content_type = 'grammar_theory'
        ORDER BY c_module_order
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    all_modules = {}
    for row in var_Arr:
        mod_id = row[0]
        mod_name = row[1]
        mod_qlvl = row[2]
        content = json.loads(row[3]) if row[3] else {}

        all_modules[str(mod_id)] = {
            'name': mod_name,
            'qlvl': mod_qlvl,
            'prerequisites': content.get('prerequisites', [])
        }

    # Определяем знание каждого протестированного модуля
    tested_knowledge = {}
    for mod_id_str, stats in module_coverage.items():
        if stats['attempts'] > 0:
            accuracy = stats['correct'] / stats['weight_sum'] if stats['weight_sum'] > 0 else 0
            tested_knowledge[mod_id_str] = accuracy

    # Применяем правила inference
    inferred = {}

    for mod_id_str, mod_info in all_modules.items():
        if mod_id_str in tested_knowledge:
            # Уже проверен
            continue

        mod_qlvl = mod_info['qlvl']
        prerequisites = mod_info['prerequisites']

        # Правило 1: Если модуль выше определенного уровня - пропускаем
        if mod_qlvl > final_level:
            continue

        # Правило 2: Если все prerequisites известны - высокая вероятность
        if prerequisites:
            prereq_scores = []
            for prereq_id in prerequisites:
                prereq_str = str(prereq_id)
                if prereq_str in tested_knowledge:
                    prereq_scores.append(tested_knowledge[prereq_str])
                elif prereq_str in inferred:
                    prereq_scores.append(inferred[prereq_str])

            if prereq_scores:
                avg_prereq = sum(prereq_scores) / len(prereq_scores)
                # Если prerequisites известны хорошо - есть шанс, что и этот модуль тоже
                if avg_prereq >= 0.7:
                    inferred[mod_id_str] = min(0.8, avg_prereq * 0.9)  # Чуть ниже prerequisites
                elif avg_prereq >= 0.5:
                    inferred[mod_id_str] = 0.5
                else:
                    inferred[mod_id_str] = 0.3
                continue

        # Правило 3: Если модуль на 2+ уровня ниже - вероятно известен
        if mod_qlvl <= final_level - 2:
            inferred[mod_id_str] = 0.7
            continue

        # Правило 4: Если модуль на 1 уровень ниже - средняя вероятность
        if mod_qlvl == final_level - 1:
            inferred[mod_id_str] = 0.6
            continue

        # Правило 5: Модуль на текущем уровне без prerequisites - низкая вероятность
        if mod_qlvl == final_level and not prerequisites:
            inferred[mod_id_str] = 0.4

    return inferred