"""
NPC Manager - Управление NPC персонажами
"""

import logging
from typing import Dict, Any, Optional, List
import fpgDB as pgDB

logger = logging.getLogger(__name__)


class NPCManager:
    """Управление NPC персонажами в интерактивных историях"""

    def __init__(self, pool):
        self.pool_base, self.pool_log = pool

    async def create_npc(
            self,
            story_id: int,
            name: str,
            gender: str,
            age_group: str,
            personality: dict,
            role_description: str,
            goals: dict,
            appears_in_scenes: list = None,
            voice_id: str = None
    ) -> int:
        """
        Создать NPC персонажа

        Args:
            story_id: ID истории
            name: Имя NPC
            gender: 'male', 'female', 'neutral'
            age_group: 'young', 'middle', 'old'
            personality: {"traits": ["friendly", "energetic"], "base_mood": "happy"}
            role_description: Роль в истории
            goals: {"primary": "Tell user about X", "secondary": ["Give item Y"]}
            appears_in_scenes: [scene_id1, scene_id2] или None
            voice_id: ID голоса для TTS

        Returns:
            npc_id нового NPC
        """

        query = """
            INSERT INTO t_story_npcs 
                (c_story_id, c_name, c_gender, c_age_group, 
                 c_personality, c_voice_id, c_role_description, 
                 c_goals, c_appears_in_scenes)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING c_npc_id
        """

        import json

        result = await pgDB.fFetch_InsertQuery_args(
            self.pool_base,
            query,
            story_id,
            name,
            gender,
            age_group,
            json.dumps(personality),
            voice_id,
            role_description,
            json.dumps(goals),
            json.dumps(appears_in_scenes) if appears_in_scenes else None
        )

        if not result:
            raise Exception(f"Failed to create NPC {name}")

        npc_id = result[0][0] if isinstance(result[0], tuple) else result[0]

        logger.info(f"Created NPC {name} (ID: {npc_id}) for story {story_id}")

        return npc_id

    async def get_npc(self, npc_id: int) -> Optional[Dict[str, Any]]:
        """Получить информацию об NPC"""

        query = """
            SELECT 
                c_npc_id,
                c_story_id,
                c_name,
                c_gender,
                c_age_group,
                c_personality,
                c_voice_id,
                c_role_description,
                c_goals,
                c_appears_in_scenes
            FROM t_story_npcs
            WHERE c_npc_id = $1
        """

        result = await pgDB.fExec_SelectQuery_args(self.pool_base, query, npc_id)

        if not result:
            return None

        row = result[0]

        import json

        # Парсим JSONB поля
        personality = row[5]
        if isinstance(personality, str):
            personality = json.loads(personality)

        goals = row[8]
        if isinstance(goals, str):
            goals = json.loads(goals)

        appears_in_scenes = row[9]
        if isinstance(appears_in_scenes, str):
            appears_in_scenes = json.loads(appears_in_scenes)

        return {
            'npc_id': row[0],
            'story_id': row[1],
            'name': row[2],
            'gender': row[3],
            'age_group': row[4],
            'personality': personality,
            'voice_id': row[6],
            'role_description': row[7],
            'goals': goals,
            'appears_in_scenes': appears_in_scenes
        }

    async def get_npcs_by_role(
            self,
            story_id: int,
            role: str  # 'companion', 'local', 'antagonist', 'neutral'
    ) -> List[Dict[str, Any]]:
        """
        Получить всех NPC определённой роли
        """

        query = """
            SELECT 
                c_npc_id,
                c_name,
                c_gender,
                c_age_group,
                c_personality,
                c_role_description,
                c_goals,
                c_npc_role
            FROM t_story_npcs
            WHERE c_story_id = $1 AND c_npc_role = $2
            ORDER BY c_npc_id
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            query,
            story_id,
            role
        )

        if not result:
            return []

        npcs = []
        for row in result:
            npcs.append({
                'npc_id': row[0],
                'name': row[1],
                'gender': row[2],
                'age_group': row[3],
                'personality': row[4],
                'role_description': row[5],
                'goals': row[6],
                'npc_role': row[7]
            })

        return npcs

    async def get_companions(self, story_id: int) -> List[Dict[str, Any]]:
        """Получить всех companions (путешествуют с пользователем)"""
        return await self.get_npcs_by_role(story_id, 'companion')

    async def get_locals(self, story_id: int) -> List[Dict[str, Any]]:
        """Получить всех locals (местные жители)"""
        return await self.get_npcs_by_role(story_id, 'local')

    async def get_npcs_in_scene(
            self,
            story_id: int,
            scene_id: int
    ) -> List[Dict[str, Any]]:
        """
        Получить список NPC присутствующих в сцене

        Args:
            story_id: ID истории
            scene_id: ID сцены

        Returns:
            Список NPC с их данными
        """

        # Сначала получаем список NPC ID из сцены
        scene_query = """
            SELECT c_npcs_present
            FROM t_story_scenes
            WHERE c_scene_id = $1 AND c_story_id = $2
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            scene_query,
            scene_id,
            story_id
        )

        if not result or not result[0][0]:
            return []

        import json
        npc_ids = result[0][0]
        if isinstance(npc_ids, str):
            npc_ids = json.loads(npc_ids)

        if not npc_ids:
            return []

        # Получаем полную информацию о каждом NPC
        npcs = []
        for npc_id in npc_ids:
            npc = await self.get_npc(npc_id)
            if npc:
                npcs.append(npc)

        return npcs

    async def get_npc_context(
            self,
            npc_id: int,
            user_id: int,
            story_id: int
    ) -> Dict[str, Any]:
        """
        Получить полный контекст NPC для генерации диалога

        Включает:
        - Базовые данные NPC
        - Текущее состояние для пользователя (встречали ли, что обсуждали)
        - История взаимодействий

        Args:
            npc_id: ID NPC
            user_id: ID пользователя
            story_id: ID истории

        Returns:
            Словарь с полным контекстом NPC
        """

        # Получаем базовые данные
        npc = await self.get_npc(npc_id)

        if not npc:
            return None

        # Получаем состояние NPC для пользователя
        npc_state = await self.get_npc_state(user_id, story_id, npc_id)

        # Получаем историю взаимодействий
        interactions = await self.get_interaction_history(
            user_id,
            story_id,
            npc_id,
            limit=5  # последние 5 взаимодействий
        )

        return {
            **npc,  # Все базовые данные NPC
            'user_state': npc_state,  # Состояние для пользователя
            'recent_interactions': interactions  # История взаимодействий
        }

    async def get_npc_state(
            self,
            user_id: int,
            story_id: int,
            npc_id: int
    ) -> Dict[str, Any]:
        """
        Получить состояние NPC для конкретного пользователя

        Returns:
            {"met": True, "info_given": False, "current_mood": "happy"}
        """

        query = """
            SELECT c_npc_states
            FROM t_story_user_progress
            WHERE c_user_id = $1 AND c_story_id = $2
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            query,
            user_id,
            story_id
        )

        if not result:
            return {"met": False}

        import json
        npc_states = result[0][0]

        if isinstance(npc_states, str):
            npc_states = json.loads(npc_states) if npc_states else {}

        # Возвращаем состояние для конкретного NPC
        return npc_states.get(str(npc_id), {"met": False})

    async def update_npc_state(
            self,
            user_id: int,
            story_id: int,
            npc_id: int,
            state_updates: dict
    ):
        """
        Обновить состояние NPC для пользователя

        Args:
            user_id: ID пользователя
            story_id: ID истории
            npc_id: ID NPC
            state_updates: {"met": True, "info_given": True, "current_mood": "friendly"}
        """

        # Получаем текущие состояния
        query = """
            SELECT c_npc_states
            FROM t_story_user_progress
            WHERE c_user_id = $1 AND c_story_id = $2
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            query,
            user_id,
            story_id
        )

        if not result:
            logger.error(f"No progress found for user {user_id}, story {story_id}")
            return

        import json
        npc_states = result[0][0]

        if isinstance(npc_states, str):
            npc_states = json.loads(npc_states) if npc_states else {}

        # Обновляем состояние конкретного NPC
        npc_key = str(npc_id)

        if npc_key not in npc_states:
            npc_states[npc_key] = {}

        npc_states[npc_key].update(state_updates)

        # Сохраняем обратно в БД
        update_query = """
            UPDATE t_story_user_progress
            SET c_npc_states = $1
            WHERE c_user_id = $2 AND c_story_id = $3
        """

        await pgDB.fExec_UpdateQuery_args(
            self.pool_base,
            update_query,
            json.dumps(npc_states),
            user_id,
            story_id
        )

        logger.info(f"Updated NPC {npc_id} state for user {user_id}: {state_updates}")

    async def get_interaction_history(
            self,
            user_id: int,
            story_id: int,
            npc_id: int,
            limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Получить историю взаимодействий с NPC

        Returns:
            Список последних взаимодействий
        """

        query = """
            SELECT 
                c_interaction_id,
                c_user_input,
                c_ai_response,
                c_timestamp
            FROM t_story_user_interactions
            WHERE c_user_id = $1 
              AND c_story_id = $2
              AND c_target_npc_id = $3
            ORDER BY c_timestamp DESC
            LIMIT $4
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            query,
            user_id,
            story_id,
            npc_id,
            limit
        )

        interactions = []
        for row in result:
            interactions.append({
                'interaction_id': row[0],
                'user_input': row[1],
                'ai_response': row[2],
                'timestamp': row[3]
            })

        # Reverse чтобы были от старых к новым
        interactions.reverse()

        return interactions