"""
Валидаторы для LearnPath модуля
"""

from typing import Dict, Any, Optional


def validate_rating(rating: int) -> bool:
    """
    Валидация оценки интереса

    Args:
        rating: Оценка (1-5)

    Returns:
        bool: Валидна ли оценка
    """
    return 1 <= rating <= 5


def validate_module_content(content_type: str, content: Dict) -> tuple[bool, Optional[str]]:
    """
    Валидация контента модуля

    Args:
        content_type: Тип контента (lesson, practice, test)
        content: Содержимое модуля

    Returns:
        tuple: (is_valid, error_message)
    """
    if content_type == 'lesson':
        if 'text' not in content:
            return False, "Lesson must contain 'text' field"
        if not isinstance(content.get('examples', []), list):
            return False, "Lesson 'examples' must be a list"
        return True, None

    elif content_type == 'practice':
        if 'task' not in content:
            return False, "Practice must contain 'task' field"
        if 'type' not in content:
            return False, "Practice must contain 'type' field"
        if content['type'] not in ['text', 'voice', 'dialogue']:
            return False, "Practice type must be 'text', 'voice', or 'dialogue'"
        return True, None

    elif content_type == 'test':
        if 'questions' not in content:
            return False, "Test must contain 'questions' field"
        if not isinstance(content['questions'], list):
            return False, "Test 'questions' must be a list"

        for idx, question in enumerate(content['questions']):
            if 'question' not in question:
                return False, f"Question {idx} must contain 'question' field"
            if 'options' not in question:
                return False, f"Question {idx} must contain 'options' field"
            if 'correct' not in question:
                return False, f"Question {idx} must contain 'correct' field"
            if not isinstance(question['options'], list):
                return False, f"Question {idx} 'options' must be a list"
            if not (0 <= question['correct'] < len(question['options'])):
                return False, f"Question {idx} 'correct' index is out of range"

        return True, None

    return False, f"Unknown content type: {content_type}"

def validate_test_answer(answer_idx: int, options_count: int) -> bool:
    """
        Валидация индекса ответа на тест

        Args:
            answer_idx: Индекс выбранного ответа
            options_count: Количество вариантов ответа

        Returns:
            bool: Валиден ли индекс
    """
    return 0 <= answer_idx < options_count

def validate_level(level: int) -> bool:
    """
        Валидация уровня английского

        Args:
            level: Уровень (1-3)

        Returns:
            bool: Валиден ли уровень
    """
    return 1 <= level <= 3

def validate_topic_id(topic_id: Any) -> bool:
    """
        Валидация ID темы

        Args:
            topic_id: ID темы

        Returns:
            bool: Валиден ли ID
    """
    try:
        return isinstance(topic_id, int) and topic_id > 0
    except:
        return False

def validate_module_id(module_id: Any) -> bool:
    """
        Валидация ID модуля

        Args:
            module_id: ID модуля

        Returns:
            bool: Валиден ли ID
    """
    try:
        return isinstance(module_id, int) and module_id > 0
    except:
        return False