"""
Главный обработчик обучения - координирует процесс прохождения уроков
"""

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from typing import Optional, Dict, Any

import fpgDB as pgDB
from states import myState
from ..core.lesson_manager import LessonManager
from ..core.progress_manager import ProgressManager
from ..core.content_generator import ContentGenerator
#from .test import launch_module_final_test as launch_test_handler
from .test import launch_module_final_test
#from .test import launch_module_final_test as launch_test
#from ..handlers.test import launch_module_final_test
#from ..handlers.test import launch_module_final_test as launch_test

import logging

# Get logger for this specific module
logger = logging.getLogger(__name__)

router = Router(name='learnpath_learning')


@router.callback_query(F.data == "continue_learn")
async def continue_learn(callback: types.CallbackQuery, state: FSMContext, pool):
    """
    Главная точка входа в систему обучения
    Определяет следующую активность для студента
    ✅ ИСПРАВЛЕНО: Убрана рекурсия
    """
    pool_base, pool_log = pool
    user_id = callback.message.chat.id

    # ✅ ЦИКЛ вместо рекурсии для обработки завершенных уроков
    while True:
        # 1. Получить текущий активный модуль
        active_module = await get_active_module(pool, user_id)
        logger.info(f'active_module:{active_module}')
        if not active_module:
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
            await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
            await callback.answer()
            return

        module_id = active_module['module_id']

        # 2. Проверить, есть ли незавершенный тест модуля
        test_progress_id = await check_pending_test(pool, user_id, module_id)
        logger.info(f'test_progress_id:{test_progress_id}')

        if test_progress_id:
            # Есть незавершенный тест - показываем его
            await launch_module_final_test(callback.message, state, pool, user_id, module_id)
            await callback.answer()
            return

        # 3. Получить следующий урок для прохождения
        next_lesson_id = await get_next_lesson(pool, user_id, module_id)

        if not next_lesson_id:
            # Все уроки пройдены → запустить финальный тест
            await launch_module_final_test(callback.message, state, pool, user_id, module_id)
            await callback.answer()
            return

        # 4. Получить или создать прогресс по уроку
        progress_manager = ProgressManager(pool)
        lesson_progress = await progress_manager.get_or_create_lesson_progress(user_id, next_lesson_id)

        # 5. Определить текущее задание
        if lesson_progress['status'] == 'not_started':
            # Начать урок с первого задания
            lesson_manager = LessonManager(pool)
            first_activity = await lesson_manager.get_first_activity(next_lesson_id)

            if not first_activity:
                await callback.message.answer("Ошибка: урок не содержит заданий")
                await callback.answer()
                return

            await start_lesson(callback.message, state, pool, user_id, next_lesson_id, first_activity)
            break  # Выход из цикла

        elif lesson_progress['status'] == 'in_progress':
            # Продолжить с текущего задания
            current_activity_id = lesson_progress['current_activity_id']

            if not current_activity_id:
                # Если current_activity_id не установлен - начинаем с первого
                lesson_manager = LessonManager(pool)
                first_activity = await lesson_manager.get_first_activity(next_lesson_id)
                await start_lesson(callback.message, state, pool, user_id, next_lesson_id, first_activity)
            else:
                lesson_manager = LessonManager(pool)
                current_activity = await lesson_manager.get_activity(current_activity_id)
                await continue_lesson(callback.message, state, pool, user_id, next_lesson_id, current_activity)
            break  # Выход из цикла

        elif lesson_progress['status'] == 'completed':
            # ✅ ИСПРАВЛЕНО: Вместо рекурсии продолжаем цикл
            continue  # Переходим к следующей итерации while

        else:  # failed
            # Урок провален, нужно пересдать
            await restart_lesson(callback.message, state, pool, user_id, next_lesson_id)
            break  # Выход из цикла

    await pgDB.fExec_LogQuery(pool_log, user_id, f"continue_learn|lesson:{next_lesson_id}")
    await callback.answer()



async def check_pending_test(pool, user_id: int, module_id: int) -> Optional[int]:
    """
    Проверить, есть ли незавершенный тест модуля
    ✅ ИСПРАВЛЕНО: Правильная работа с pool tuple
    """
    from ..services.test_service import TestService

    pool_base, _ = pool  # ✅ Распаковываем tuple

    # ✅ Создаем экземпляр с pool
    test_service = TestService(pool_base)

    # ✅ Вызываем БЕЗ передачи pool (он уже в self.pool)
    test_progress_id = await test_service.has_pending_test(user_id, module_id)

    return test_progress_id

async def get_active_module(pool, user_id: int) -> Optional[Dict[str, Any]]:
    """Получить текущий активный модуль студента"""
    pool_base, _ = pool

    query = f"""
        SELECT 
            mu.c_module_id,
            m.c_module_name,
            m.c_module_order
        FROM t_lp_module_user mu
        JOIN t_lp_module m ON mu.c_module_id = m.c_module_id
        WHERE mu.c_user_id = {user_id}
            AND mu.c_status = 'in_progress'
        ORDER BY mu.c_start_date DESC
        LIMIT 1
    """

    result = await pgDB.fExec_SelectQuery(pool_base, query)

    if not result:
        # Если нет активного - активируем первый незавершенный
        query = f"""
            UPDATE t_lp_module_user
            SET c_status = 'in_progress',
                c_start_date = CURRENT_TIMESTAMP
            WHERE c_user_id = {user_id}
                AND c_status = 'not_started'
                AND c_module_id = (
                    SELECT c_module_id 
                    FROM t_lp_module_user
                    WHERE c_user_id = {user_id} AND c_status = 'not_started'
                    ORDER BY c_order_in_program
                    LIMIT 1
                )
            RETURNING c_module_id
        """

        module_id_result = await pgDB.fExec_SelectQuery(pool_base, query)

        if not module_id_result:
            return None

        # Получаем информацию о модуле
        module_id = module_id_result[0][0]
        query = f"""
            SELECT c_module_id, c_module_name, c_module_order
            FROM t_lp_module
            WHERE c_module_id = {module_id}
        """
        result = await pgDB.fExec_SelectQuery(pool_base, query)

        if not result:
            return None

    row = result[0]
    return {
        'module_id': row[0],
        'module_name': row[1],
        'module_order': row[2]
    }


async def get_next_lesson(pool, user_id: int, module_id: int) -> Optional[int]:
    """
    Определяет следующий урок для прохождения

    Приоритет:
    1. Незавершенный урок (in_progress)
    2. Remedial уроки (созданные после fail теста)
    3. Следующий regular урок по порядку
    """
    progress_manager = ProgressManager(pool)

    # 1. Ищем незавершенный урок
    in_progress_lesson = await progress_manager.get_lesson_by_status(user_id, module_id, 'in_progress')
    if in_progress_lesson:
        return in_progress_lesson

    # 2. Ищем remedial уроки
    remedial_lessons = await progress_manager.get_pending_remedial_lessons(user_id, module_id)
    if remedial_lessons:
        return remedial_lessons[0]

    # 3. Ищем следующий regular урок
    completed_lessons = await progress_manager.get_completed_lessons(user_id, module_id)

    pool_base, _ = pool

    # Получаем следующий regular урок, который не завершен
    completed_ids_str = ','.join(map(str, completed_lessons)) if completed_lessons else '0'

    query = f"""
        SELECT c_lesson_id
        FROM t_lp_lesson
        WHERE c_module_id = {module_id}
            AND c_lesson_type = 'regular'
            AND c_is_active = TRUE
            AND c_lesson_id NOT IN ({completed_ids_str})
        ORDER BY c_lesson_number
        LIMIT 1
    """

    result = await pgDB.fExec_SelectQuery(pool_base, query)

    if not result:
        return None

    return result[0][0]



async def start_lesson(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int,
        first_activity: Dict[str, Any]
) -> None:
    """Начать урок с первого задания"""
    lesson_manager = LessonManager(pool)
    progress_manager = ProgressManager(pool)

    # Получаем информацию об уроке
    lesson = await lesson_manager.get_lesson(lesson_id)

    if not lesson:
        await message.answer("Ошибка: урок не найден")
        return

    # Обновляем статус и текущее задание
    await progress_manager.update_progress_status(user_id, lesson_id, 'in_progress')
    await progress_manager.set_current_activity(user_id, lesson_id, first_activity['activity_id'])

    # Сохраняем в state
    await state.update_data(
        current_lesson_id=lesson_id,
        current_activity_id=first_activity['activity_id']
    )

    # Показываем приветствие урока и первое задание
    str_msg = (
        f"📚 <b>{lesson['lesson_name']}</b>\n\n"
        f"{lesson['description']}\n\n"
        #f"⏱ Примерное время: {lesson['estimated_minutes']} мин\n"
    )

    await message.answer(str_msg, parse_mode=ParseMode.HTML)

    # Запускаем первое задание
    await launch_activity(message, state, pool, user_id, lesson_id, first_activity)

async def continue_lesson(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int,
        current_activity: Dict[str, Any]
) -> None:
    """Продолжить урок с текущего задания"""
    lesson_manager = LessonManager(pool)
    lesson = await lesson_manager.get_lesson(lesson_id)

    str_msg = (
        f"📚 Продолжаем урок: <b>{lesson['lesson_name']}</b>\n\n"
        f"Переходим к следующему заданию..."
    )

    await message.answer(str_msg, parse_mode=ParseMode.HTML)

    # Запускаем текущее задание
    await launch_activity(message, state, pool, user_id, lesson_id, current_activity)


async def restart_lesson(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int
) -> None:
    """Пересдать провальный урок"""
    lesson_manager = LessonManager(pool)
    progress_manager = ProgressManager(pool)

    lesson = await lesson_manager.get_lesson(lesson_id)
    first_activity = await lesson_manager.get_first_activity(lesson_id)

    # Сбрасываем прогресс
    await progress_manager.update_progress_status(user_id, lesson_id, 'in_progress')
    await progress_manager.increment_attempts(user_id, lesson_id)

    str_msg = (
        f"🔄 Пересдаем урок: <b>{lesson['lesson_name']}</b>\n\n"
        f"Начинаем сначала..."
    )

    await message.answer(str_msg, parse_mode=ParseMode.HTML)

    await start_lesson(message, state, pool, user_id, lesson_id, first_activity)

async def launch_activity(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int,
        activity: Dict[str, Any]
) -> None:
    """
    Запустить конкретное задание
    Делегирует выполнение специализированным обработчикам
    """
    activity_type = activity['activity_type']
    activity_id = activity['activity_id']

    # Импортируем обработчики заданий
    from ..handlers.activity import (
        launch_task1_grammar,
        launch_task2_words,
        launch_task3_questions,
        launch_task4_listen_speak,
        launch_task5_listen_write,
        launch_task6_reading,
        launch_task7_word_repeat,
        launch_task8_story
    )

    # Сохраняем контекст
    await state.update_data(
        current_lesson_id=lesson_id,
        current_activity_id=activity_id,
        current_activity_type=activity_type
    )

    # Запускаем соответствующий обработчик
    if activity_type == 'task_1_grammar':
        await launch_task1_grammar(message, state, pool, user_id, lesson_id, activity)

    elif activity_type == 'task_2_words':
        await launch_task2_words(message, state, pool, user_id, lesson_id, activity)

    elif activity_type == 'task_3_questions':
        await launch_task3_questions(message, state, pool, user_id, lesson_id, activity)

    elif activity_type == 'task_4_listen_speak':
        await launch_task4_listen_speak(message, state, pool, user_id, lesson_id, activity)

    elif activity_type == 'task_5_listen_write':
        await launch_task5_listen_write(message, state, pool, user_id, lesson_id, activity)

    elif activity_type == 'task_6_reading':
        await launch_task6_reading(message, state, pool, user_id, lesson_id, activity)

    elif activity_type == 'task_7_word_repeat':
        await launch_task7_word_repeat(message, state, pool, user_id, lesson_id, activity)

    elif activity_type == 'task_8_dialog':
        #await launch_task8_dialog(message, state, pool, user_id, lesson_id, activity)
        await launch_task8_story(message, state, pool, user_id, lesson_id, activity)

    else:
        await message.answer(f"Неизвестный тип задания: {activity_type}")


async def complete_activity(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int,
        activity_id: int
) -> None:
    """
    Завершить задание и перейти к следующему
    Универсальная функция, вызываемая после выполнения любого задания
    """
    lesson_manager = LessonManager(pool)
    progress_manager = ProgressManager(pool)

    # Отмечаем задание как выполненное
    await progress_manager.mark_activity_completed(user_id, lesson_id, activity_id)

    # Получаем текущее задание для определения следующего
    current_activity = await lesson_manager.get_activity(activity_id)

    # Ищем следующее задание
    next_activity = await lesson_manager.get_next_activity(
        lesson_id,
        current_activity['activity_order']
    )

    if next_activity:
        # Есть следующее задание - запускаем его
        await progress_manager.set_current_activity(user_id, lesson_id, next_activity['activity_id'])
        await launch_activity(message, state, pool, user_id, lesson_id, next_activity)
    else:
        # Все задания выполнены - завершаем урок
        await finish_lesson(message, state, pool, user_id, lesson_id)


async def finish_lesson(
        message: types.Message,
        state: FSMContext,
        pool,
        user_id: int,
        lesson_id: int
) -> None:
    """Завершить урок и показать результаты"""
    pool_base, pool_log = pool

    lesson_manager = LessonManager(pool)
    progress_manager = ProgressManager(pool)

    lesson = await lesson_manager.get_lesson(lesson_id)

    # Обновляем статус урока
    await progress_manager.update_progress_status(user_id, lesson_id, 'completed')

    str_msg = (
        f"🎉 <b>Урок завершен!</b>\n\n"
        f"Вы успешно прошли: {lesson['lesson_name']}\n\n"
        f"Отличная работа! Переходим к следующему уроку..."
    )

    # ✅ Показываем кнопку вместо автоматического перехода
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="▶️ Следующий урок",
        callback_data="continue_learn"
    ))
    builder.add(InlineKeyboardButton(
        text="📚 Моя программа",
        callback_data="view_learnpath"
    ))
    builder.adjust(1)

    await message.answer(str_msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, user_id, f"finish_lesson|lesson:{lesson_id}")



def _________dummy(): pass

async def load_and_show_first_scene(            #approved
        message: types.Message,
        state: FSMContext,
        pool,
        story_id: int
):
    """Загрузить и показать первую сцену истории"""

    pool_base, pool_log = pool

    # Получаем первую сцену
    query = """
        SELECT 
            c_scene_id,
            c_scene_name,
            c_location_description,
            c_location_description_trs,
            c_objective,
            c_objective_trs,
            c_npcs_present,
            c_items_available
        FROM t_story_scenes
        WHERE c_story_id = $1
        ORDER BY c_scene_number
        LIMIT 1
    """

    try:
        result = await pgDB.fExec_SelectQuery_args(pool_base, query, story_id)

        if not result:
            logger.error(f"No scenes found for story {story_id}")
            return

        scene_data = {
            'scene_id': result[0][0],
            'scene_name': result[0][1],
            'location_description': result[0][2],
            'location_description_trs': result[0][3],
            'objective': result[0][4],
            'objective_trs': result[0][5],
            'npcs_present': result[0][6],  # Это ID!
            'items_available': result[0][7]
        }

        # ✅ Загружаем информацию об NPC
        scene_data = await enrich_scene_with_npc_info(pool_base, scene_data)

        # Показываем сцену
        await show_scene(message, state, scene_data)

        # Переходим в режим активной истории
        await state.set_state(myState.task8_story_active)

    except Exception as e:
        logger.error(f"Error loading first scene: {e}", exc_info=True)
