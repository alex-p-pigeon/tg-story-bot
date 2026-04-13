"""
Сервис для работы с прогрессом обучения
"""

from typing import Dict, Optional
import fpgDB as pgDB


class ProgressService:
    """Работа с прогрессом пользователя"""

    def __init__(self, pool):
        self.pool_base, self.pool_log = pool

    async def update_topic_progress(self, user_id: int, topic_id: int):
        """
        Обновить прогресс по теме на основе завершенных модулей

        Args:
            user_id: ID пользователя
            topic_id: ID темы
        """
        var_query = f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN COALESCE(ump.c_status, 'not_started') = 'completed' THEN 1 ELSE 0 END) as completed
            FROM t_lp_module m
            LEFT JOIN t_lp_user_module_progress ump 
                ON m.c_module_id = ump.c_module_id AND ump.c_user_id = {user_id}
            WHERE m.c_topic_id = {topic_id}
        """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        if var_Arr:
            total, completed = var_Arr[0]
            progress = int((completed / total * 100)) if total > 0 else 0

            var_query = f"""
                UPDATE t_lp_module_user 
                SET c_progress_percent = {progress}
                WHERE c_user_id = {user_id} AND c_topic_id = {topic_id}
            """
            await pgDB.fExec_UpdateQuery(self.pool_base, var_query)

    async def update_module_progress(
            self,
            user_id: int,
            module_id: int,
            status: str,
            score: Optional[float] = None
    ):
        """
        Обновить прогресс по модулю

        Args:
            user_id: ID пользователя
            module_id: ID модуля
            status: Статус ('in_progress', 'completed')
            score: Оценка (опционально)
        """
        score_str = f", c_score = {score}" if score is not None else ""
        completed_str = ", c_completed_at = CURRENT_TIMESTAMP" if status == 'completed' else ""

        var_query = f"""
            INSERT INTO t_lp_user_module_progress 
            (c_user_id, c_module_id, c_status, c_attempts{', c_score' if score is not None else ''})
            VALUES ({user_id}, {module_id}, '{status}', 1{f', {score}' if score is not None else ''})
            ON CONFLICT (c_user_id, c_module_id) 
            DO UPDATE SET 
                c_status = '{status}',
                c_attempts = t_lp_user_module_progress.c_attempts + 1
                {score_str}
                {completed_str}
        """
        await pgDB.fExec_UpdateQuery(self.pool_base, var_query)

    async def get_statistics(self, user_id: int) -> Optional[Dict]:
        """
        Получить статистику пользователя

        Returns:
            Dict: Статистика или None
        """
        # Статистика по темам
        var_query = f"""
            SELECT 
                COUNT(*) as total_topics,
                SUM(CASE WHEN c_status = 'completed' THEN 1 ELSE 0 END) as completed_topics,
                SUM(CASE WHEN c_status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                AVG(c_progress_percent) as avg_progress
            FROM t_lp_module_user
            WHERE c_user_id = {user_id}
        """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        if not var_Arr:
            return None

        total_topics, completed, in_progress, avg_progress = var_Arr[0]
        avg_progress = int(avg_progress) if avg_progress else 0

        # Статистика по тестам
        var_query = f"""
                    SELECT 
                        COUNT(*) as total_tests,
                        AVG(c_score / c_max_score * 100) as avg_score,
                        SUM(CASE WHEN c_passed THEN 1 ELSE 0 END) as passed_tests
                    FROM t_lp_init_assess_user_results
                    WHERE c_user_id = {user_id}
                """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        total_tests, avg_score, passed_tests = var_Arr[0] if var_Arr else (0, 0, 0)
        avg_score = int(avg_score) if avg_score else 0

        # Время обучения
        var_query = f"""
                    SELECT SUM(c_time_spent_minutes)
                    FROM t_lp_user_module_progress
                    WHERE c_user_id = {user_id}
                """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)
        total_minutes = var_Arr[0][0] if var_Arr and var_Arr[0][0] else 0
        hours = total_minutes // 60
        minutes = total_minutes % 60

        return {
            'total_topics': total_topics,
            'completed_topics': completed,
            'in_progress_topics': in_progress,
            'avg_progress': avg_progress,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'avg_score': avg_score,
            'hours': hours,
            'minutes': minutes
        }