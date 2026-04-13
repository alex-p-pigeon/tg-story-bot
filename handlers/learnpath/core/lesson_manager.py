"""
Core модуль для управления уроками
Работает с таблицами: t_lp_lesson, t_lp_lesson_activity
"""

from typing import Optional, List, Dict, Any
import fpgDB as pgDB


class LessonManager:
    """Менеджер уроков - получение информации об уроках и заданиях"""

    def __init__(self, pool):
        self.pool_base, self.pool_log = pool

    def _parse_config(self, config) -> dict:
        """Парсит config из JSON или возвращает dict"""
        if isinstance(config, str):
            import json
            try:
                return json.loads(config) if config else {}
            except:
                return {}
        return config if config else {}

    async def get_lesson(self, lesson_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить информацию об уроке

        Returns:
            {
                'lesson_id': int,
                'module_id': int,
                'lesson_number': int,
                'lesson_name': str,
                'lesson_type': str,  # 'regular' или 'remedial'
                'grammar_article_code': str,
                'description': str,
                'estimated_minutes': int,
                'difficulty_level': int
            }
        """
        query = f"""
            SELECT 
                c_lesson_id,
                c_module_id,
                c_lesson_number,
                c_lesson_name,
                c_lesson_type,
                c_grammar_article_code,
                c_description,
                c_estimated_minutes,
                c_difficulty_level
            FROM t_lp_lesson
            WHERE c_lesson_id = {lesson_id} AND c_is_active = TRUE
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        if not result:
            return None

        row = result[0]
        return {
            'lesson_id': row[0],
            'module_id': row[1],
            'lesson_number': row[2],
            'lesson_name': row[3],
            'lesson_type': row[4],
            'grammar_article_code': row[5],
            'description': row[6],
            'estimated_minutes': row[7],
            'difficulty_level': row[8]
        }

    async def get_lesson_activities(self, lesson_id: int) -> List[Dict[str, Any]]:
        """
        Получить все задания урока в порядке выполнения

        Returns:
            [
                {
                    'activity_id': int,
                    'activity_type': str,
                    'activity_order': int,
                    'is_required': bool,
                    'template_id': int,
                    'questions_count': int,
                    'config': dict
                },
                ...
            ]
        """
        query = f"""
            SELECT 
                c_activity_id,
                c_activity_type,
                c_activity_order,
                c_is_required,
                c_template_id,
                c_questions_count,
                c_config
            FROM t_lp_lesson_activity
            WHERE c_lesson_id = {lesson_id}
            ORDER BY c_activity_order
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        activities = []

        for row in result:
            activities.append({
                'activity_id': row[0],
                'activity_type': row[1],
                'activity_order': row[2],
                'is_required': row[3],
                'template_id': row[4],
                'questions_count': row[5],
                'config': self._parse_config(row[6])
            })

        return activities

    async def get_lesson_activities(self, lesson_id: int) -> List[Dict[str, Any]]:
        """Получить все задания урока в порядке выполнения"""
        query = f"""
            SELECT 
                c_activity_id,
                c_activity_type,
                c_activity_order,
                c_is_required,
                c_template_id,
                c_questions_count,
                c_config
            FROM t_lp_lesson_activity
            WHERE c_lesson_id = {lesson_id}
            ORDER BY c_activity_order
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        activities = []
        for row in result:
            activities.append({
                'activity_id': row[0],
                'activity_type': row[1],
                'activity_order': row[2],
                'is_required': row[3],
                'template_id': row[4],
                'questions_count': row[5],
                'config': self._parse_config(row[6])  # ← теперь всегда словарь
            })

        return activities

    async def get_first_activity(self, lesson_id: int) -> Optional[Dict[str, Any]]:
        """Получить первое задание урока"""
        query = f"""
            SELECT 
                c_activity_id,
                c_activity_type,
                c_activity_order,
                c_is_required,
                c_template_id,
                c_questions_count,
                c_config
            FROM t_lp_lesson_activity
            WHERE c_lesson_id = {lesson_id}
            ORDER BY c_activity_order
            LIMIT 1
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        if not result:
            return None

        row = result[0]
        return {
            'activity_id': row[0],
            'lesson_id': lesson_id,
            'activity_type': row[1],
            'activity_order': row[2],
            'is_required': row[3],
            'template_id': row[4],
            'questions_count': row[5],
            'config': self._parse_config(row[6]) #row[6] if row[6] else {}
        }

    async def get_activity(self, activity_id: int) -> Optional[Dict[str, Any]]:
        """Получить информацию об одном задании"""
        query = f"""
            SELECT 
                c_activity_id,
                c_lesson_id,
                c_activity_type,
                c_activity_order,
                c_is_required,
                c_template_id,
                c_questions_count,
                c_config
            FROM t_lp_lesson_activity
            WHERE c_activity_id = {activity_id}
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        if not result:
            return None

        row = result[0]

        # Парсим config если это строка JSON
        config = row[7]
        if isinstance(config, str):
            import json
            config = json.loads(config) if config else {}
        elif config is None:
            config = {}

        return {
            'activity_id': row[0],
            'lesson_id': row[1],
            'activity_type': row[2],
            'activity_order': row[3],
            'is_required': row[4],
            'template_id': row[5],
            'questions_count': row[6],
            'config': config
        }

    async def get_next_activity(self, lesson_id: int, current_activity_order: int) -> Optional[Dict[str, Any]]:
        """Получить следующее задание после текущего"""
        query = f"""
            SELECT 
                c_activity_id,
                c_activity_type,
                c_activity_order,
                c_is_required,
                c_template_id,
                c_questions_count,
                c_config
            FROM t_lp_lesson_activity
            WHERE c_lesson_id = {lesson_id}
                AND c_activity_order > {current_activity_order}
            ORDER BY c_activity_order
            LIMIT 1
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        if not result:
            return None

        row = result[0]
        return {
            'activity_id': row[0],
            'lesson_id': lesson_id,
            'activity_type': row[1],
            'activity_order': row[2],
            'is_required': row[3],
            'template_id': row[4],
            'questions_count': row[5],
            'config': self._parse_config(row[6])
        }

    async def get_lessons_by_module(self, module_id: int, lesson_type: str = 'regular') -> List[Dict[str, Any]]:
        """
        Получить все уроки модуля

        Args:
            module_id: ID модуля
            lesson_type: 'regular' или 'remedial'
        """
        query = f"""
            SELECT 
                c_lesson_id,
                c_lesson_number,
                c_lesson_name,
                c_grammar_article_code,
                c_estimated_minutes
            FROM t_lp_lesson
            WHERE c_module_id = {module_id}
                AND c_lesson_type = '{lesson_type}'
                AND c_is_active = TRUE
            ORDER BY c_lesson_number
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        lessons = []
        for row in result:
            lessons.append({
                'lesson_id': row[0],
                'lesson_number': row[1],
                'lesson_name': row[2],
                'grammar_article_code': row[3],
                'estimated_minutes': row[4]
            })

        return lessons

    async def get_lesson_by_grammar_code(self, grammar_code: str) -> Optional[Dict[str, Any]]:
        """Найти урок по коду грамматической статьи"""
        query = f"""
            SELECT 
                c_lesson_id,
                c_module_id,
                c_lesson_name
            FROM t_lp_lesson
            WHERE c_grammar_article_code = '{grammar_code}'
                AND c_is_active = TRUE
            LIMIT 1
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        if not result:
            return None

        row = result[0]
        return {
            'lesson_id': row[0],
            'module_id': row[1],
            'lesson_name': row[2]
        }