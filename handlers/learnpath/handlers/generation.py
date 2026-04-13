"""
Handlers для генерации персональной программы обучения
Версия 3.0 - Адаптация под новую архитектуру (t_lp_lesson)
"""

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
import json
from typing import List, Dict

from states import myState
import fpgDB as pgDB

router = Router(name='learnpath_generation')

# Маппинг уровней
QLVL_MAP = {4: 'A1', 5: 'A2', 6: 'B1', 7: 'B2', 8: 'C1'}


@router.callback_query(F.data == "generate_learnpath")
async def generate_learnpath(callback: types.CallbackQuery, state: FSMContext, pool):
    """Генерация персональной программы обучения"""
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    await state.set_state(myState.learnpath_active)

    await callback.answer("Генерирую программу...", show_alert=False)

    # Получаем данные из тестирования и опроса интересов
    user_data = await state.get_data()
    assessed_level = user_data.get('assessed_level')
    all_module_knowledge = user_data.get('all_module_knowledge', {})
    interests_ratings = user_data.get('interests_ratings', {})

    if not assessed_level:
        # Если не прошли тест - берем из БД
        var_query = f"SELECT c_ups_eng_level FROM t_user_paramssingle WHERE c_ups_user_id = {vUserID}"
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
        assessed_level = var_Arr[0][0] if var_Arr else 4  # По умолчанию A1

    # Генерируем программу
    program_result = await create_personalized_program(
        pool_base,
        vUserID,
        assessed_level,
        all_module_knowledge,
        interests_ratings
    )

    modules_count = program_result['total_modules']
    estimated_weeks = program_result['estimated_weeks']

    str_Msg = (
        f"🎉 <b>Ваша программа готова!</b>\n\n"
        f"📊 <b>Структура программы:</b>\n"
        f"• Всего модулей: {modules_count}\n"
        f"• Примерная длительность: {estimated_weeks} недель\n\n"
        f"✨ <b>Персонализация:</b>\n"
        f"• Все примеры адаптированы под ваши интересы\n"
        f"• Задания используют темы: {', '.join(program_result.get('themes', []))}\n"
        f"• Программа покрывает уровни от {QLVL_MAP[assessed_level]} до C1\n\n"
        f"Готовы начать обучение?"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🚀 Начать обучение", callback_data="continue_learn"))
    builder.add(InlineKeyboardButton(text="📚 Моя программа", callback_data="view_learnpath"))
    builder.adjust(1)

    await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID,
                              f"learnpath_generated|modules:{modules_count}|weeks:{estimated_weeks}")


async def create_personalized_program(
        pool_base,
        user_id: int,
        assessed_level: int,
        all_module_knowledge: dict,
        interests_ratings: dict
) -> dict:
    """
    Создание персональной программы обучения

    Новая логика (v3.0):
    1. Анализ знаний модулей
    2. Формирование списка модулей для программы (все уровни A1-C1)
    3. Добавление персонализации через metadata
    4. Сохранение в t_lp_module_user
    5. Уроки (t_lp_lesson) уже существуют и привязаны к модулям
    """

    # ========================================================================
    # ЭТАП 1: Получение всех модулей
    # ========================================================================

    var_query = """
        SELECT 
            c_module_id, 
            c_module_name, 
            c_qlvl_id, 
            c_module_order, 
            c_content_type,
            c_content
        FROM t_lp_module
        WHERE c_content_type IN ('grammar_module', 'vocabulary_essential', 'vocabulary_thematic')
        ORDER BY c_module_order
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    all_modules_db = {}
    for row in var_Arr:
        module_id = row[0]
        content = json.loads(row[5]) if row[5] else {}
        all_modules_db[str(module_id)] = {
            'id': module_id,
            'name': row[1],
            'qlvl': row[2],
            'order': row[3],
            'content_type': row[4],
            'content': content
        }

    # ========================================================================
    # ЭТАП 2: Категоризация модулей по знанию
    # ========================================================================

    weak_modules = []  # score < 0.4
    partial_modules = []  # 0.4 <= score < 0.7
    known_modules = []  # score >= 0.7
    new_modules = []  # не проверялись

    for module_id_str, module_info in all_modules_db.items():
        module_qlvl = module_info['qlvl']

        if module_id_str in all_module_knowledge:
            stats = all_module_knowledge[module_id_str]
            score = calculate_knowledge_score(stats)
            source = 'tested' if stats.get('attempts', 0) > 0 else 'inferred'

            if score < 0.4:
                weak_modules.append({
                    'module_id': int(module_id_str),
                    'score': score,
                    'source': source,
                    'priority': 'critical',
                    **module_info
                })
            elif score < 0.7:
                partial_modules.append({
                    'module_id': int(module_id_str),
                    'score': score,
                    'source': source,
                    'priority': 'reinforcement',
                    **module_info
                })
            else:
                known_modules.append({
                    'module_id': int(module_id_str),
                    'score': score,
                    'source': source,
                    'priority': 'review',
                    **module_info
                })
        else:
            # Новый модуль
            new_modules.append({
                'module_id': int(module_id_str),
                'score': 0.0,
                'source': 'new',
                'priority': 'new_topic',
                **module_info
            })

    # ========================================================================
    # ЭТАП 3: Упорядочивание модулей
    # ========================================================================

    # Объединяем модули: слабые → частичные → новые → известные (для повторения)
    all_modules = weak_modules + partial_modules + new_modules + known_modules

    # Сортируем с учетом prerequisites и уровня
    sorted_modules = sort_modules_by_prerequisites(all_modules, all_modules_db)

    # ========================================================================
    # ЭТАП 4: Извлечение тем из топиков
    # ========================================================================

    high_interest_topics = []
    for topic_id, rating in interests_ratings.items():
        if rating >= 4:
            high_interest_topics.append({'topic_id': topic_id, 'rating': rating})

    high_interest_topics.sort(key=lambda x: x['rating'], reverse=True)
    top_topics = [t['topic_id'] for t in high_interest_topics[:5]]

    context_themes = await extract_themes_from_topics(pool_base, top_topics)

    # ========================================================================
    # ЭТАП 5: Сохранение программы в БД
    # ========================================================================

    # Очищаем старую программу
    var_query = f"DELETE FROM t_lp_module_user WHERE c_user_id = {user_id}"
    await pgDB.fExec_UpdateQuery(pool_base, var_query)

    # Сохраняем модули
    order = 1
    for module in sorted_modules:
        # Персонализация для модуля
        module_personalization = {
            'applied_topics': top_topics,
            'context_themes': context_themes,
            'priority': module['priority'],
            'knowledge_score': module['score'],
            'knowledge_source': module['source']
        }

        var_query = f"""
            INSERT INTO t_lp_module_user 
            (c_user_id, c_module_id, c_order_in_program, 
             c_personalization_data, c_status)
            VALUES (
                {user_id}, 
                {module['module_id']}, 
                {order},
                '{json.dumps(module_personalization)}',
                'not_started'
            )
        """
        await pgDB.fExec_UpdateQuery(pool_base, var_query)
        order += 1

    # ========================================================================
    # ЭТАП 6: Активация первого модуля
    # ========================================================================

    if sorted_modules:
        first_module_id = sorted_modules[0]['module_id']

        var_query = f"""
            UPDATE t_lp_module_user
            SET c_status = 'in_progress',
                c_start_date = CURRENT_TIMESTAMP
            WHERE c_user_id = {user_id} AND c_module_id = {first_module_id}
        """
        await pgDB.fExec_UpdateQuery(pool_base, var_query)

    # ========================================================================
    # Возврат результата
    # ========================================================================

    estimated_weeks = len(sorted_modules) // 2  # ~2 модуля в неделю

    return {
        'total_modules': len(sorted_modules),
        'estimated_weeks': estimated_weeks,
        'themes': context_themes,
        'weak_modules': len(weak_modules),
        'partial_modules': len(partial_modules),
        'new_modules': len(new_modules),
        'known_modules': len(known_modules)
    }


def calculate_knowledge_score(stats: dict) -> float:
    """Рассчитать балл знания модуля"""
    attempts = stats.get('attempts', 0)

    if attempts == 0:
        return stats.get('inference_score', 0.0)

    weight_sum = stats.get('weight_sum', 1.0)
    correct = stats.get('correct', 0.0)

    if weight_sum == 0:
        return 0.0

    return correct / weight_sum


def sort_modules_by_prerequisites(modules: list, all_modules_db: dict) -> list:
    """
    Топологическая сортировка модулей с учетом prerequisites
    """
    # Строим граф зависимостей
    module_map = {m['module_id']: m for m in modules}
    graph = {m['module_id']: [] for m in modules}
    in_degree = {m['module_id']: 0 for m in modules}

    # Заполняем граф
    for module in modules:
        module_id = module['module_id']
        prereqs = module['content'].get('prerequisites', [])

        for prereq_id in prereqs:
            if prereq_id in module_map:
                graph[prereq_id].append(module_id)
                in_degree[module_id] += 1

    # Топологическая сортировка (Kahn's algorithm)
    queue = [m_id for m_id in in_degree if in_degree[m_id] == 0]
    sorted_ids = []

    while queue:
        # Сортируем queue по уровню и порядку для стабильности
        queue.sort(key=lambda m_id: (module_map[m_id]['qlvl'], module_map[m_id]['order']))
        current = queue.pop(0)
        sorted_ids.append(current)

        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Если есть циклы - добавляем оставшиеся по уровню
    remaining = [m_id for m_id in in_degree if in_degree[m_id] > 0]
    remaining.sort(key=lambda m_id: (module_map[m_id]['qlvl'], module_map[m_id]['order']))
    sorted_ids.extend(remaining)

    return [module_map[m_id] for m_id in sorted_ids]


async def extract_themes_from_topics(pool_base, topic_ids: list) -> list:
    """Извлечь темы из топиков интересов"""
    if not topic_ids:
        return ['general']

    topic_ids_str = ','.join(map(str, topic_ids))

    var_query = f"""
        SELECT c_topic_name
        FROM t_lp_topics
        WHERE c_topic_id IN ({topic_ids_str})
    """
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

    themes = []
    for row in var_Arr:
        topic_name = row[0]
        # Извлекаем ключевые слова
        topic_lower = topic_name.lower()

        if 'technology' in topic_lower or 'it' in topic_lower:
            themes.append('Technology')
        elif 'business' in topic_lower or 'professional' in topic_lower:
            themes.append('Business')
        elif 'travel' in topic_lower:
            themes.append('Travel')
        elif 'finance' in topic_lower:
            themes.append('Finance')
        elif 'marketing' in topic_lower:
            themes.append('Marketing')
        else:
            themes.append('General')

    return list(set(themes)) if themes else ['General']