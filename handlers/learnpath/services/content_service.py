"""
Сервис для работы с контентом обучения
"""

from typing import Optional, List, Dict
import json
import fpgDB as pgDB


class ContentService:
    """Работа с контентом модулей и тем"""

    def __init__(self, pool):
        self.pool_base, self.pool_log = pool

    async def get_module(self, module_id: int) -> Optional[Dict]:
        """
        Получить модуль по ID

        Args:
            module_id: ID модуля

        Returns:
            Dict: Данные модуля или None
        """
        var_query = f"""
            SELECT 
                m.c_module_name,
                m.c_content_type,
                m.c_content,
                m.c_topic_id
            FROM t_lp_module m
            WHERE m.c_module_id = {module_id}
        """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        if not var_Arr:
            return None

        module_name, content_type, content_json, topic_id = var_Arr[0]
        content = json.loads(content_json) if content_json else {}

        return {
            'id': module_id,
            'name': module_name,
            'type': content_type,
            'content': content,
            'topic_id': topic_id
        }

    async def get_topic_modules(self, topic_id: int, user_id: Optional[int] = None) -> List[Dict]:
        """
        Получить все модули темы

        Args:
            topic_id: ID темы
            user_id: ID пользователя (для получения прогресса)

        Returns:
            List[Dict]: Список модулей
        """
        var_query = f"""
            SELECT 
                m.c_module_id,
                m.c_module_name,
                m.c_content_type,
                m.c_estimated_minutes,
                COALESCE(ump.c_status, 'not_started') as status
            FROM t_lp_module m
            LEFT JOIN t_lp_user_module_progress ump 
                ON m.c_module_id = ump.c_module_id 
                {f'AND ump.c_user_id = {user_id}' if user_id else ''}
            WHERE m.c_topic_id = {topic_id}
            ORDER BY m.c_module_order
        """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        modules = []
        for row in var_Arr:
            modules.append({
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'minutes': row[3],
                'status': row[4]
            })

        return modules

    async def get_next_module(self, user_id: int, topic_id: int) -> Optional[int]:
        """
        Получить следующий незавершенный модуль темы

        Args:
            user_id: ID пользователя
            topic_id: ID темы

        Returns:
            int: ID следующего модуля или None
        """
        var_query = f"""
            SELECT m.c_module_id
            FROM t_lp_module m
            LEFT JOIN t_lp_user_module_progress ump 
                ON m.c_module_id = ump.c_module_id AND ump.c_user_id = {user_id}
            WHERE m.c_topic_id = {topic_id}
                AND COALESCE(ump.c_status, 'not_started') != 'completed'
            ORDER BY m.c_module_order
            LIMIT 1
        """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        return var_Arr[0][0] if var_Arr else None

    async def get_topic_info(self, topic_id: int) -> Optional[Dict]:
        """
        Получить информацию о теме

        Args:
            topic_id: ID темы

        Returns:
            Dict: Информация о теме или None
        """
        var_query = f"""
            SELECT 
                c_topic_name,
                c_topic_name_ru,
                c_description,
                c_estimated_hours,
                c_eng_level,
                c_category
            FROM t_lp_topics
            WHERE c_topic_id = {topic_id}
        """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        if not var_Arr:
            return None

        return {
            'id': topic_id,
            'name': var_Arr[0][0],
            'name_ru': var_Arr[0][1],
            'description': var_Arr[0][2],
            'hours': var_Arr[0][3],
            'level': var_Arr[0][4],
            'category': var_Arr[0][5]
        }