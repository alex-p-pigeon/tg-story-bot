"""
Шаблоны сообщений для LearnPath модуля
"""

from typing import List, Dict


def format_learnpath_message(learnpath: List[Dict]) -> str:
    """
    Форматировать сообщение с программой обучения

    Args:
        learnpath: Список тем программы

    Returns:
        str: Отформатированное сообщение
    """
    if not learnpath:
        return "Программа не найдена. Создайте новую."

    status_emoji = {
        'not_started': '⚪',
        'in_progress': '🟡',
        'completed': '🟢',
        'skipped': '⚫'
    }

    topics_list = []
    total_progress = 0

    for topic in learnpath:
        emoji = status_emoji.get(topic['status'], '⚪')
        topics_list.append(
            f"{emoji} {topic['order']}. {topic['name_ru']} ({topic['progress']}%)"
        )
        total_progress += topic['progress']

    avg_progress = total_progress // len(learnpath) if learnpath else 0

    message = (
            f"📚 <b>Ваша программа обучения</b>\n\n"
            f"Общий прогресс: {avg_progress}%\n"
            f"Тем в программе: {len(learnpath)}\n\n"
            f"<b>Темы:</b>\n"
            + "\n".join(topics_list)
    )

    return message


def format_topic_overview_message(topic: Dict, modules: List[Dict]) -> str:
    """
    Форматировать сообщение с обзором темы

    Args:
        topic: Данные темы
        modules: Список модулей темы

    Returns:
        str: Отформатированное сообщение
    """
    modules_list = []
    for idx, module in enumerate(modules, start=1):
        status_icon = '✅' if module['status'] == 'completed' else \
            '🔄' if module['status'] == 'in_progress' else '⚪'
        modules_list.append(
            f"{status_icon} {idx}. {module['name']} (~{module['minutes']} мин)"
        )

    message = (
            f"📖 <b>{topic['name_ru']}</b>\n\n"
            f"{topic.get('description', '')}\n\n"
            f"Прогресс: {topic.get('progress', 0)}%\n"
            f"Примерное время: {topic.get('hours', 0)} ч\n\n"
            f"<b>Модули:</b>\n"
            + "\n".join(modules_list)
    )

    return message


def format_test_result_message(score: int, total: int, passed: bool) -> str:
    """
    Форматировать сообщение с результатами теста

    Args:
        score: Количество правильных ответов
        total: Общее количество вопросов
        passed: Тест пройден или нет

    Returns:
        str: Отформатированное сообщение
    """
    percentage = int((score / total * 100)) if total > 0 else 0

    if passed:
        message = (
            f"🎉 <b>Отлично!</b>\n\n"
            f"Результат: {score}/{total} ({percentage}%)\n"
            f"✅ Тест успешно пройден!"
        )
    else:
        message = (
            f"📚 <b>Попробуйте еще раз</b>\n\n"
            f"Результат: {score}/{total} ({percentage}%)\n"
            f"❌ Для прохождения требуется больше правильных ответов"
        )

    return message


def format_statistics_message(stats: Dict) -> str:
    """
    Форматировать сообщение со статистикой

    Args:
        stats: Словарь со статистикой

    Returns:
        str: Отформатированное сообщение
    """
    message = (
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

    return message