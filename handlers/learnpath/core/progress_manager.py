"""
Core модуль для управления прогрессом студента
Работает с таблицей: t_lp_lesson_user_progress
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import fpgDB as pgDB


class ProgressManager:
    """Менеджер прогресса - отслеживание выполнения уроков"""

    def __init__(self, pool):
        self.pool_base, self.pool_log = pool

    async def get_or_create_lesson_progress(
            self,
            user_id: int,
            lesson_id: int
    ) -> Dict[str, Any]:
        """
        Получить или создать прогресс по уроку

        Returns:
            {
                'progress_id': int,
                'lesson_id': int,
                'status': str,
                'current_activity_id': int,
                'completed_activities': list,
                'start_date': datetime,
                'lesson_data': dict
            }
        """
        # Сначала пытаемся получить существующий прогресс
        query = f"""
            SELECT 
                c_progress_id,
                c_status,
                c_current_activity_id,
                c_completed_activities,
                c_start_date,
                c_lesson_data
            FROM t_lp_lesson_user_progress
            WHERE c_user_id = {user_id} AND c_lesson_id = {lesson_id}
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        if result:
            row = result[0]
            return {
                'progress_id': row[0],
                'lesson_id': lesson_id,
                'status': row[1],
                'current_activity_id': row[2],
                'completed_activities': row[3] if row[3] else [],
                'start_date': row[4],
                'lesson_data': row[5] if row[5] else {}
            }

        # Если прогресса нет - создаем новый
        insert_query = f"""
            INSERT INTO t_lp_lesson_user_progress (
                c_user_id,
                c_lesson_id,
                c_status,
                c_start_date,
                c_completed_activities,
                c_lesson_data
            ) VALUES (
                {user_id},
                {lesson_id},
                'not_started',
                CURRENT_TIMESTAMP,
                ARRAY[]::integer[],
                '{{}}'::jsonb
            )
            RETURNING c_progress_id
        """

        progress_id = await pgDB.fExec_UpdateQuery(self.pool_base, insert_query)   #fExec_InsertQuery


        return {
            'progress_id': progress_id,
            'lesson_id': lesson_id,
            'status': 'not_started',
            'current_activity_id': None,
            'completed_activities': [],
            'start_date': datetime.now(),
            'lesson_data': {}
        }

    async def update_progress_status(
            self,
            user_id: int,
            lesson_id: int,
            status: str
    ) -> None:
        """
        Обновить статус прогресса урока

        Args:
            status: 'not_started', 'in_progress', 'completed', 'failed'
        """
        completion_field = ""
        if status == 'completed':
            completion_field = ", c_completion_date = CURRENT_TIMESTAMP"

        query = f"""
            UPDATE t_lp_lesson_user_progress
            SET c_status = '{status}',
                c_updated_at = CURRENT_TIMESTAMP
                {completion_field}
            WHERE c_user_id = {user_id} AND c_lesson_id = {lesson_id}
        """

        await pgDB.fExec_UpdateQuery(self.pool_base, query)

    async def set_current_activity(
            self,
            user_id: int,
            lesson_id: int,
            activity_id: int
    ) -> None:
        """Установить текущее задание"""
        query = f"""
            UPDATE t_lp_lesson_user_progress
            SET c_current_activity_id = {activity_id},
                c_status = 'in_progress',
                c_updated_at = CURRENT_TIMESTAMP
            WHERE c_user_id = {user_id} AND c_lesson_id = {lesson_id}
        """

        await pgDB.fExec_UpdateQuery(self.pool_base, query)

    async def reset_lesson_progress(self, user_id: int, lesson_id: int) -> None:
        """Сбросить прогресс урока"""
        query = f"""
            UPDATE t_lp_lesson_user_progress
            SET 
                c_status = 'not_started',
                c_current_activity_id = NULL,
                c_completed_activities = ARRAY[]::integer[],
                c_lesson_data = '{{}}'::jsonb,
                c_score = NULL
            WHERE c_user_id = {user_id} AND c_lesson_id = {lesson_id}
        """
        await pgDB.fExec_UpdateQuery(self.pool_base, query)

    async def mark_activity_completed(
            self,
            user_id: int,
            lesson_id: int,
            activity_id: int
    ) -> None:
        """Отметить задание как выполненное"""
        query = f"""
            UPDATE t_lp_lesson_user_progress
            SET c_completed_activities = array_append(c_completed_activities, {activity_id}),
                c_updated_at = CURRENT_TIMESTAMP
            WHERE c_user_id = {user_id} 
                AND c_lesson_id = {lesson_id}
                AND NOT ({activity_id} = ANY(c_completed_activities))
        """

        await pgDB.fExec_UpdateQuery(self.pool_base, query)

    async def is_activity_completed(
            self,
            user_id: int,
            lesson_id: int,
            activity_id: int
    ) -> bool:
        """Проверить, выполнено ли задание"""
        query = f"""
            SELECT {activity_id} = ANY(c_completed_activities)
            FROM t_lp_lesson_user_progress
            WHERE c_user_id = {user_id} AND c_lesson_id = {lesson_id}
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        if not result:
            return False

        return result[0][0] if result[0][0] is not None else False

    async def save_lesson_data(
            self,
            user_id: int,
            lesson_id: int,
            data: Dict[str, Any]
    ) -> None:
        """
        Сохранить персонализированные данные урока (контент заданий)

        Args:
            data: Словарь с данными урока (сгенерированные задания и т.д.)
        """
        json_data = json.dumps(data, ensure_ascii=False)

        query = f"""
            UPDATE t_lp_lesson_user_progress
            SET c_lesson_data = c_lesson_data || '{json_data}'::jsonb,
                c_updated_at = CURRENT_TIMESTAMP
            WHERE c_user_id = {user_id} AND c_lesson_id = {lesson_id}
        """

        await pgDB.fExec_UpdateQuery(self.pool_base, query)

    async def get_lesson_data(
            self,
            user_id: int,
            lesson_id: int
    ) -> Dict[str, Any]:
        """Получить сохраненные данные урока"""
        query = f"""
            SELECT c_lesson_data
            FROM t_lp_lesson_user_progress
            WHERE c_user_id = {user_id} AND c_lesson_id = {lesson_id}
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        if not result or not result[0][0]:
            return {}

        return result[0][0]

    async def get_completed_lessons(
            self,
            user_id: int,
            module_id: int
    ) -> List[int]:
        """Получить список ID завершенных уроков модуля"""
        query = f"""
            SELECT lp.c_lesson_id
            FROM t_lp_lesson_user_progress lp
            JOIN t_lp_lesson l ON lp.c_lesson_id = l.c_lesson_id
            WHERE lp.c_user_id = {user_id}
                AND l.c_module_id = {module_id}
                AND lp.c_status = 'completed'
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        return [row[0] for row in result]

    async def get_pending_remedial_lessons(
            self,
            user_id: int,
            module_id: int
    ) -> List[int]:
        """Получить список ID незавершенных remedial уроков"""
        query = f"""
            SELECT l.c_lesson_id
            FROM t_lp_lesson l
            LEFT JOIN t_lp_lesson_user_progress lp 
                ON l.c_lesson_id = lp.c_lesson_id AND lp.c_user_id = {user_id}
            WHERE l.c_module_id = {module_id}
                AND l.c_lesson_type = 'remedial'
                AND l.c_is_active = TRUE
                AND (lp.c_status IS NULL OR lp.c_status != 'completed')
            ORDER BY l.c_created_at
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        return [row[0] for row in result]

    async def get_lesson_by_status(
            self,
            user_id: int,
            module_id: int,
            status: str
    ) -> Optional[int]:
        """Найти урок с определенным статусом"""
        query = f"""
            SELECT l.c_lesson_id
            FROM t_lp_lesson l
            JOIN t_lp_lesson_user_progress lp ON l.c_lesson_id = lp.c_lesson_id
            WHERE l.c_module_id = {module_id}
                AND lp.c_user_id = {user_id}
                AND lp.c_status = '{status}'
                AND l.c_is_active = TRUE
            LIMIT 1
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        if not result:
            return None

        return result[0][0]

    async def update_score(
            self,
            user_id: int,
            lesson_id: int,
            score: int,
            max_score: int
    ) -> None:
        """Обновить баллы за урок"""
        query = f"""
            UPDATE t_lp_lesson_user_progress
            SET c_score = {score},
                c_max_score = {max_score},
                c_updated_at = CURRENT_TIMESTAMP
            WHERE c_user_id = {user_id} AND c_lesson_id = {lesson_id}
        """

        await pgDB.fExec_UpdateQuery(self.pool_base, query)

    async def increment_attempts(
            self,
            user_id: int,
            lesson_id: int
    ) -> int:
        """
        Увеличить счетчик попыток

        Returns:
            Новое количество попыток
        """
        query = f"""
            UPDATE t_lp_lesson_user_progress
            SET c_attempts = c_attempts + 1,
                c_updated_at = CURRENT_TIMESTAMP
            WHERE c_user_id = {user_id} AND c_lesson_id = {lesson_id}
            RETURNING c_attempts
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        if not result:
            return 0

        return result[0][0]