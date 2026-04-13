"""
Сервис для работы с персональной программой обучения
Версия 2.0 - Обновлено для работы с модулями и сессиями
"""

from typing import Optional, List, Dict
import fpgDB as pgDB


class LearnPathService:
    """Бизнес-логика работы с программой обучения"""

    def __init__(self, pool):
        self.pool_base, self.pool_log = pool

    async def get_user_learnpath(self, user_id: int) -> List[Dict]:
        """
        Получить программу пользователя

        Returns:
            List[Dict]: Список модулей с прогрессом
        """
        var_query = f"""
            SELECT 
                uc.c_module_id,
                uc.c_status, 
                uc.c_progress_percent,
                uc.c_order_in_program,
                m.c_module_name,
                m.c_content->>'name_ru' as name_ru,
                uc.c_sessions_completed,
                uc.c_total_sessions,
                uc.c_module_type,
                uc.c_knowledge_score,
                m.c_estimated_minutes
            FROM t_lp_module_user uc
            JOIN t_lp_module m ON uc.c_module_id = m.c_module_id
            WHERE uc.c_user_id = {user_id}
            ORDER BY uc.c_order_in_program
        """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        if not var_Arr:
            return []

        learnpath = []
        for row in var_Arr:
            learnpath.append({
                'module_id': row[0],
                'status': row[1],
                'progress': row[2],
                'order': row[3],
                'name': row[4],
                'name_ru': row[5],
                'sessions_completed': row[6],
                'total_sessions': row[7],
                'module_type': row[8],
                'knowledge_score': row[9],
                'estimated_minutes': row[10]
            })

        return learnpath

    async def has_learnpath(self, user_id: int) -> bool:
        """Проверить наличие программы у пользователя"""
        var_query = f"SELECT COUNT(*) FROM t_lp_module_user WHERE c_user_id = {user_id}"
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)
        return var_Arr[0][0] > 0 if var_Arr else False


    async def delete_learnpath(self, user_id: int):
        """Удалить всю программу пользователя"""
        queries = [
            #f"DELETE FROM t_lp_user_session_progress WHERE c_user_id = {user_id}",
            f"DELETE FROM t_lp_module_user WHERE c_user_id = {user_id}",
            f"DELETE FROM t_lp_topics_user WHERE c_user_id = {user_id}",
        ]

        for query in queries:
            await pgDB.fExec_UpdateQuery(self.pool_base, query)


    async def get_current_module(self, user_id: int) -> Optional[Dict]:
        """
        Получить текущий модуль в процессе

        Returns:
            Optional[Dict]: Информация о текущем модуле или None
        """
        var_query = f"""
            SELECT 
                uc.c_module_id,
                m.c_module_name,
                m.c_content->>'name_ru' as name_ru,
                uc.c_current_session_id,
                uc.c_sessions_completed,
                uc.c_total_sessions,
                uc.c_progress_percent,
                uc.c_module_type
            FROM t_lp_module_user uc
            JOIN t_lp_module m ON uc.c_module_id = m.c_module_id
            WHERE uc.c_user_id = {user_id} AND uc.c_status = 'in_progress'
            ORDER BY uc.c_order_in_program
            LIMIT 1
        """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        if not var_Arr:
            return None

        row = var_Arr[0]
        return {
            'module_id': row[0],
            'name': row[1],
            'name_ru': row[2],
            'current_session_id': row[3],
            'sessions_completed': row[4],
            'total_sessions': row[5],
            'progress': row[6],
            'module_type': row[7]
        }

    '''
    async def get_current_session(self, user_id: int) -> Optional[Dict]:
        """
        Получить текущую сессию пользователя

        Returns:
            Optional[Dict]: Информация о текущей сессии или None
        """
        var_query = f"""
            SELECT 
                s.c_session_id,
                s.c_module_id,
                s.c_session_number,
                s.c_session_name,
                s.c_session_type,
                s.c_description,
                s.c_estimated_minutes,
                s.c_content,
                COALESCE(sp.c_status, 'not_started') as progress_status
            FROM t_lp_module_user uc
            JOIN t_lp_module_sessions s ON uc.c_current_session_id = s.c_session_id
            LEFT JOIN t_lp_user_session_progress sp 
                ON sp.c_session_id = s.c_session_id AND sp.c_user_id = {user_id}
            WHERE uc.c_user_id = {user_id} AND uc.c_status = 'in_progress'
            LIMIT 1
        """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        if not var_Arr:
            return None

        row = var_Arr[0]
        return {
            'session_id': row[0],
            'module_id': row[1],
            'session_number': row[2],
            'name': row[3],
            'type': row[4],
            'description': row[5],
            'estimated_minutes': row[6],
            'content': row[7],
            'progress_status': row[8]
        }
    '''
    #
    '''
    async def complete_session(self, user_id: int, session_id: int, score: Optional[int] = None):
        """
        Отметить сессию как завершенную

        Args:
            user_id: ID пользователя
            session_id: ID сессии
            score: Результат теста (если применимо)
        """
        # Обновляем прогресс сессии
        var_query = f"""
            INSERT INTO t_lp_user_session_progress 
            (c_user_id, c_session_id, c_status, c_completion_date, c_score)
            VALUES ({user_id}, {session_id}, 'completed', CURRENT_TIMESTAMP, {score if score else 'NULL'})
            ON CONFLICT (c_user_id, c_session_id)
            DO UPDATE SET 
                c_status = 'completed',
                c_completion_date = CURRENT_TIMESTAMP,
                c_score = {score if score else 'NULL'}
        """
        await pgDB.fExec_UpdateQuery(self.pool_base, var_query)

        # Получаем module_id для этой сессии
        var_query = f"""
            SELECT c_module_id 
            FROM t_lp_module_sessions 
            WHERE c_session_id = {session_id}
        """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        if not var_Arr:
            return

        module_id = var_Arr[0][0]

        # Обновляем счетчик завершенных сессий в модуле
        var_query = f"""
            UPDATE t_lp_module_user
            SET c_sessions_completed = c_sessions_completed + 1,
                c_last_activity_date = CURRENT_TIMESTAMP
            WHERE c_user_id = {user_id} AND c_module_id = {module_id}
        """
        await pgDB.fExec_UpdateQuery(self.pool_base, var_query)

        # Проверяем, все ли сессии завершены
        await self.check_module_completion(user_id, module_id)
    '''

    async def check_module_completion(self, user_id: int, module_id: int):
        """
        Проверить, завершен ли модуль, и обновить его статус

        Args:
            user_id: ID пользователя
            module_id: ID модуля
        """
        var_query = f"""
            SELECT c_sessions_completed, c_total_sessions
            FROM t_lp_module_user
            WHERE c_user_id = {user_id} AND c_module_id = {module_id}
        """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        if not var_Arr:
            return

        completed, total = var_Arr[0]

        if completed >= total:
            # Модуль завершен
            var_query = f"""
                UPDATE t_lp_module_user
                SET c_status = 'completed',
                    c_progress_percent = 100,
                    c_completion_date = CURRENT_TIMESTAMP
                WHERE c_user_id = {user_id} AND c_module_id = {module_id}
            """
            await pgDB.fExec_UpdateQuery(self.pool_base, var_query)

            # Активируем следующий модуль
            await self.activate_next_module(user_id)
        else:
            # Обновляем прогресс
            progress = int((completed / total) * 100) if total > 0 else 0

            var_query = f"""
                UPDATE t_lp_module_user
                SET c_progress_percent = {progress}
                WHERE c_user_id = {user_id} AND c_module_id = {module_id}
            """
            await pgDB.fExec_UpdateQuery(self.pool_base, var_query)

            # Переходим к следующей сессии в модуле
            await self.activate_next_session(user_id, module_id)

    '''
    async def activate_next_session(self, user_id: int, module_id: int):
        """
        Активировать следующую сессию в текущем модуле

        Args:
            user_id: ID пользователя
            module_id: ID модуля
        """
        # Получаем следующую незавершенную сессию
        var_query = f"""
            SELECT s.c_session_id
            FROM t_lp_module_sessions s
            LEFT JOIN t_lp_user_session_progress sp 
                ON s.c_session_id = sp.c_session_id AND sp.c_user_id = {user_id}
            WHERE s.c_module_id = {module_id}
                AND (sp.c_status IS NULL OR sp.c_status != 'completed')
            ORDER BY s.c_session_number
            LIMIT 1
        """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        if var_Arr:
            next_session_id = var_Arr[0][0]

            var_query = f"""
                UPDATE t_lp_module_user
                SET c_current_session_id = {next_session_id}
                WHERE c_user_id = {user_id} AND c_module_id = {module_id}
            """
            await pgDB.fExec_UpdateQuery(self.pool_base, var_query)
    '''

    async def activate_next_module(self, user_id: int):
        """
        Активировать следующий модуль в программе

        Args:
            user_id: ID пользователя
        """
        # Получаем следующий не начатый модуль
        var_query = f"""
            SELECT c_module_id
            FROM t_lp_module_user
            WHERE c_user_id = {user_id} AND c_status = 'not_started'
            ORDER BY c_order_in_program
            LIMIT 1
        """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        if var_Arr:
            next_module_id = var_Arr[0][0]

            # Получаем первую сессию следующего модуля
            var_query = f"""
                SELECT c_session_id
                FROM t_lp_module_sessions
                WHERE c_module_id = {next_module_id}
                ORDER BY c_session_number
                LIMIT 1
            """
            var_Arr2 = await pgDB.fExec_SelectQuery(self.pool_base, var_query)
            first_session_id = var_Arr2[0][0] if var_Arr2 else None

            # Активируем модуль
            var_query = f"""
                UPDATE t_lp_module_user
                SET c_status = 'in_progress',
                    c_start_date = CURRENT_TIMESTAMP,
                    c_current_session_id = {first_session_id if first_session_id else 'NULL'}
                WHERE c_user_id = {user_id} AND c_module_id = {next_module_id}
            """
            await pgDB.fExec_UpdateQuery(self.pool_base, var_query)

    '''
    async def get_module_progress(self, user_id: int, module_id: int) -> Dict:
        """
        Получить детальный прогресс по модулю

        Args:
            user_id: ID пользователя
            module_id: ID модуля

        Returns:
            Dict: Детальная информация о прогрессе
        """
        var_query = f"""
            SELECT 
                uc.c_status,
                uc.c_progress_percent,
                uc.c_sessions_completed,
                uc.c_total_sessions,
                uc.c_time_spent_minutes,
                m.c_module_name,
                m.c_content->>'name_ru' as name_ru
            FROM t_lp_module_user uc
            JOIN t_lp_module m ON uc.c_module_id = m.c_module_id
            WHERE uc.c_user_id = {user_id} AND uc.c_module_id = {module_id}
        """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        if not var_Arr:
            return {}

        row = var_Arr[0]

        # Получаем прогресс по сессиям
        var_query = f"""
            SELECT 
                s.c_session_number,
                s.c_session_name,
                COALESCE(sp.c_status, 'not_started') as status,
                sp.c_score
            FROM t_lp_module_sessions s
            LEFT JOIN t_lp_user_session_progress sp 
                ON s.c_session_id = sp.c_session_id AND sp.c_user_id = {user_id}
            WHERE s.c_module_id = {module_id}
            ORDER BY s.c_session_number
        """
        var_Arr2 = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        sessions = []
        for s_row in var_Arr2:
            sessions.append({
                'number': s_row[0],
                'name': s_row[1],
                'status': s_row[2],
                'score': s_row[3]
            })

        return {
            'status': row[0],
            'progress': row[1],
            'sessions_completed': row[2],
            'total_sessions': row[3],
            'time_spent': row[4],
            'name': row[5],
            'name_ru': row[6],
            'sessions': sessions
        }
    '''