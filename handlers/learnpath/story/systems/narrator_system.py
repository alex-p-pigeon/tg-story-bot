"""
Narrator System - Система подсказок и направления сюжета
"""

import logging
from typing import Dict, Any, Optional
import json
import selfFunctions as myF
import fpgDB as pgDB
from datetime import datetime, timedelta



logger = logging.getLogger(__name__)


class NarratorSystem:
    """Система подсказок narrator/god/admin для помощи застрявшим пользователям"""

    def __init__(self, pool, user_id: int):
        self.pool_base, self.pool_log = pool
        self.user_id = user_id

        # Пороги для определения "застревания"
        self.STUCK_ACTIONS_THRESHOLD = 5  # Действий без прогресса
        self.STUCK_TIME_THRESHOLD = 180  # 3 минуты без прогресса (секунды)

    async def check_if_hint_needed(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,
            actions_count: int
    ) -> bool:
        """
        Проверить нужна ли подсказка пользователю

        Args:
            user_id: ID пользователя
            story_id: ID истории
            scene_id: ID текущей сцены
            actions_count: Количество действий в текущей сцене

        Returns:
            True если нужна подсказка
        """

        # Проверка 1: Много действий без прогресса
        if actions_count >= self.STUCK_ACTIONS_THRESHOLD:
            logger.info(f"User {user_id} stuck by actions count: {actions_count}")
            return True

        # Проверка 2: Долгое время без прогресса
        last_hint_time = await self._get_last_hint_time(user_id, story_id, scene_id)

        if last_hint_time:
            time_since_hint = datetime.now() - last_hint_time
            if time_since_hint.total_seconds() < 60:  # Не чаще раза в минуту
                return False

        # Проверка 3: Время в сцене
        scene_entry_time = await self._get_scene_entry_time(user_id, story_id, scene_id)

        if scene_entry_time:
            time_in_scene = datetime.now() - scene_entry_time
            if time_in_scene.total_seconds() >= self.STUCK_TIME_THRESHOLD:
                logger.info(f"User {user_id} stuck by time: {time_in_scene.total_seconds()}s")
                return True

        return False

    async def generate_hint(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,
            scene_context: Dict[str, Any],
            user_progress: Dict[str, Any],
            stuck_reason: str = 'no_progress',
            recent_interaction: Optional[Dict[str, Any]] = None  # ⬅️ НОВЫЙ параметр
    ) -> Optional[Dict[str, Any]]:  # ⬅️ ИЗМЕНЕНО: может вернуть None
        """
        Сгенерировать подсказку для пользователя

        Args:
            user_id: ID пользователя
            story_id: ID истории
            scene_id: ID сцены
            scene_context: Контекст сцены
            user_progress: Прогресс пользователя
            stuck_reason: Причина застревания
                'no_progress' - нет прогресса
                'wrong_npc' - говорит не с тем NPC
                'missing_item' - нужен предмет которого нет
                'wrong_approach' - неправильный подход
            recent_interaction: Информация о текущем взаимодействии
                {'interaction_type': 'dialogue', 'npc_name': 'Anna', ...}

        Returns:
            {
                'hint_type': 'inner_thought',
                'text': "I thought, maybe I should...",
                'text_trs': {"ru": "Я подумал, возможно мне стоит..."}
            }
            или None если hint не нужен (пользователь делает правильное действие)
        """

        logger.info(f"Generating hint for user {user_id}, reason: {stuck_reason}")

        # ====================================================================
        # ✅ ПРОВЕРКА: Не показывать hint если пользователь УЖЕ делает правильное действие
        # ====================================================================
        if recent_interaction:
            logger.info(f"Checking if recent interaction is correct action: {recent_interaction}")

            current_npc = recent_interaction.get('npc_name', '').lower()
            current_item = recent_interaction.get('item_name', '').lower()
            interaction_type = recent_interaction.get('interaction_type')

            # Получить objectives из scene_context
            detailed_objectives = scene_context.get('detailed_objectives', {})
            objectives_list = detailed_objectives.get('objectives', [])

            logger.info(f"Checking against {len(objectives_list)} objectives")

            for obj in objectives_list:
                # Пропускаем уже завершенные objectives
                if obj.get('completed', False):
                    continue

                obj_type = obj.get('type')
                obj_target = obj.get('target', '').lower()

                # ✅ Проверка для dialogue objectives
                if obj_type == 'dialogue' and interaction_type == 'dialogue':
                    if current_npc and obj_target in current_npc:
                        logger.info(f"User is talking to correct NPC ({current_npc})")
                        return None

                # ✅ Проверка для item objectives
                if obj_type == 'item' and interaction_type in ['item_pickup', 'item_use']:
                    if current_item and obj_target in current_item:
                        logger.info(f"User is working with correct item ({current_item})")
                        return None

            logger.info("v Recent interaction doesn't match incomplete objectives, proceeding with hint")

        # ====================================================================
        # Продолжаем генерацию hint как обычно
        # ====================================================================

        # Получаем историю последних действий
        recent_actions = await self._get_recent_actions(user_id, story_id, scene_id, limit=5)



        # Создаём промпт для AI
        user_level = await myF.fGetUserEngLevel(None, self.user_id, self.pool_base)

        prompt = self._create_hint_prompt(
            scene_context=scene_context,
            user_progress=user_progress,
            recent_actions=recent_actions,
            stuck_reason=stuck_reason,
            recent_interaction=recent_interaction,
            user_level=user_level
        )

        systemPrompt = '''You are the narrator/guide in an ESL interactive story.
You provide subtle hints to help stuck students without giving away the solution.
You MUST respond ONLY with valid JSON, no additional text or markdown.'''

        try:
            # Запрос к AI
            content = await myF.afSendMsg2AI(
                prompt,
                self.pool_base,
                self.user_id,
                iModel=4,  # GPT-4o
                toggleParam=3,  # Temperature 0.7
                systemPrompt=systemPrompt
            )

            # Убираем markdown
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            content = content.strip()

            # Парсим JSON
            hint_data = json.loads(content)

            # Валидируем
            if 'text' not in hint_data:
                raise ValueError("Missing 'text' field in hint")

            logger.info(f"Generated hint for user {user_id}")

            return hint_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse hint JSON: {e}")
            return self._create_fallback_hint(scene_context)

        except Exception as e:
            logger.error(f"Error generating hint: {e}", exc_info=True)
            return self._create_fallback_hint(scene_context)

    def _create_hint_prompt(
            self,
            scene_context: Dict[str, Any],
            user_progress: Dict[str, Any],
            recent_actions: list,
            stuck_reason: str,
            recent_interaction: Optional[Dict[str, Any]] = None,
            user_level: int = 3
    ) -> str:
        """Создать промпт для генерации подсказки"""

        # Форматируем недавние действия
        actions_text = ""
        if recent_actions:
            actions_text = "\n\nUSER'S RECENT ACTIONS:\n"
            for action in recent_actions:
                interaction_type = action['interaction_type']
                user_input = action['user_input'][:100]
                ai_response = action.get('ai_response', '')[:200]

                actions_text += f"- User ({interaction_type}): {user_input}\n"
                if ai_response:
                    actions_text += f"  NPC responded: {ai_response}\n"

        # Detailed objectives status
        detailed_objectives = scene_context.get('detailed_objectives', {})
        objectives_list = detailed_objectives.get('objectives', [])

        objectives_text = "\n\nOBJECTIVES STATUS:\n"
        if objectives_list:
            for obj in objectives_list:
                obj_id = obj.get('id')
                obj_type = obj.get('type')
                obj_desc = obj.get('description')
                obj_target = obj.get('target', '')
                obj_keywords = obj.get('keywords', [])
                obj_completed = obj.get('completed', False)

                status = "COMPLETED" if obj_completed else "NOT COMPLETED"
                objectives_text += f"- [{status}] {obj_desc} (type: {obj_type}"
                if obj_target:
                    objectives_text += f", target: {obj_target}"
                if obj_keywords:
                    objectives_text += f", keywords: {', '.join(obj_keywords)}"
                objectives_text += ")\n"
        else:
            objectives_text += "No detailed objectives available\n"

        # NPCs и Items в сцене
        npcs_present = scene_context.get('npcs_present', [])
        items_available = scene_context.get('items_available', [])

        scene_elements = "\n\nSCENE ELEMENTS:\n"
        scene_elements += f"- NPCs in scene: {', '.join([str(npc) for npc in npcs_present]) if npcs_present else 'None'}\n"
        scene_elements += f"- Items available: {', '.join([str(item) for item in items_available]) if items_available else 'None'}\n"

        # Текущий NPC контекст
        current_npc_text = ""
        if recent_interaction and recent_interaction.get('npc_name'):
            current_npc = recent_interaction['npc_name']
            current_npc_text = f"\n\nCURRENT INTERACTION:\n"
            current_npc_text += f"User is CURRENTLY talking to: {current_npc}\n"

            # Проверить есть ли objective для этого NPC
            related_objs = [
                obj for obj in objectives_list
                if not obj.get('completed', False)
                   and obj.get('target', '').lower() == current_npc.lower()
            ]

            if related_objs:
                current_npc_text += f"There IS an incomplete objective related to {current_npc}:\n"
                current_npc_text += f"  - {related_objs[0]['description']}\n"
                current_npc_text += f"IMPORTANT: Hint about THIS objective with {current_npc}!\n"
            else:
                current_npc_text += f"No incomplete objectives for {current_npc}.\n"
                current_npc_text += f"IMPORTANT: Suggest user finish with {current_npc} and move to next objective.\n"

        # Следующий невыполненный objective
        next_obj_text = "\n\nNEXT INCOMPLETE OBJECTIVE:\n"
        next_obj = None
        for obj in objectives_list:
            if not obj.get('completed', False):
                next_obj = obj
                break

        if next_obj:
            next_obj_text += f"Description: {next_obj['description']}\n"
            next_obj_text += f"Type: {next_obj['type']}\n"
            if next_obj.get('target'):
                next_obj_text += f"Target: {next_obj['target']}\n"
            if next_obj.get('keywords'):
                next_obj_text += f"Keywords: {', '.join(next_obj['keywords'])}\n"
        else:
            next_obj_text += "All objectives completed!\n"

        # Причины застревания
        stuck_reasons = {
            'no_progress': "User hasn't made progress toward the objective",
            'wrong_npc': "User is talking to the wrong NPC",
            'missing_item': "User needs an item they don't have",
            'wrong_approach': "User is trying the wrong approach"
        }

        stuck_desc = stuck_reasons.get(stuck_reason, "User seems stuck")

        prompt = f"""
    You are the narrator in an ESL interactive story. The student is stuck and needs a subtle hint.

    CURRENT SITUATION:
    - Location: {scene_context.get('location_name', 'Unknown')}
    - Main Objective: {scene_context.get('objective', 'Continue the story')}
    - Stuck reason: {stuck_desc}

    USER'S PROGRESS:
    - Actions taken: {user_progress.get('actions_count', 0)}
    - Inventory: {len(user_progress.get('inventory', []))} items
    - English level: {self._format_level(user_level)}
    {actions_text}
    {objectives_text}
    {scene_elements}
    {current_npc_text}
    {next_obj_text}

    SUCCESS CONDITIONS:
    {json.dumps(scene_context.get('success_conditions', {}), indent=2)}

    OBJECTIVE TYPES AND HOW TO HINT:

    1. type='dialogue':
       - User needs to start conversation with specific NPC
       - If user is ALREADY talking to that NPC, no hint needed
       - If talking to different NPC, hint to talk to the correct one
       - Hint format: suggest calling or talking to the target NPC

    2. type='information':
       - User needs to ASK SPECIFIC QUESTION to obtain information
       - Look at keywords field to understand what topic to ask about
       - Hint format: suggest asking the target NPC about specific topic from keywords
       - More specific than type='dialogue' - not just "talk" but "ask about X"

    3. type='action':
       - User needs to use ACTION button to perform physical action
       - Hint format: suggest using action or doing something active based on description

    4. type='item':
       - User needs to FIND and PICK UP a specific item
       - Check if item is in scene elements
       - Hint format: suggest looking around or searching the location

    YOUR TASK:
    Generate a subtle hint as an "inner thought" of the main character.

    CRITICAL RULES:
    1. NEVER suggest objectives that are already COMPLETED
    2. Focus ONLY on NOT COMPLETED objectives
    3. Look at NEXT INCOMPLETE OBJECTIVE section - hint toward that specific objective
    4. Consider objective TYPE and provide appropriate hint style
    5. If user is talking to correct NPC, hint about what to achieve with that NPC
    6. If user is talking to wrong NPC, hint to switch to the correct one
    7. Be subtle - don't give away exact solution
    8. Use language appropriate for {self._format_level(user_level)} level

    Format: "I thought, maybe I should..." or "Suddenly I realized..."

    RESPOND WITH JSON:
    {{
      "hint_type": "inner_thought",
      "text": "Your hint in English (1-2 sentences)",
      "text_trs": {{
        "ru": "Russian translation"
      }}
    }}

    IMPORTANT:
    - Be subtle and encouraging
    - Focus on the NEXT incomplete objective
    - Match hint style to objective type
    - Respond ONLY with JSON, no markdown
        """

        return prompt

    def _format_level(self, level: int) -> str:
        """Форматировать уровень для промпта"""
        levels = {
            1: "A1-A2 (Beginner) - use very simple sentences and basic vocabulary",
            2: "A2-B1 (Elementary) - use simple sentences and common words",
            3: "B1 (Intermediate) - use clear sentences with moderate vocabulary",
            4: "B1-B2 (Upper-Intermediate) - use varied sentences and wider vocabulary",
            5: "B2-C1 (Advanced) - use sophisticated language"
        }
        return levels.get(level, levels[3])

    def _create_fallback_hint(self, scene_context: Dict[str, Any]) -> Dict[str, Any]:
        """Создать fallback подсказку"""

        objective = scene_context.get('objective', 'continue exploring')

        return {
            'hint_type': 'inner_thought',
            'text': f"I thought, maybe I should focus on: {objective}",
            'text_trs': {
                'ru': f"Я подумал, возможно мне стоит сосредоточиться на: {objective}"
            }
        }

    async def save_hint(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,
            hint_text: str,
            hint_text_trs: dict
    ):
        """
        Сохранить подсказку в БД

        Args:
            user_id: ID пользователя
            story_id: ID истории
            scene_id: ID сцены
            hint_text: Текст подсказки
            hint_text_trs: Переводы подсказки
        """

        query = """
            INSERT INTO t_story_narrator_hints
                (c_user_id, c_story_id, c_scene_id, c_hint_text, c_hint_text_trs)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING c_hint_id
        """

        result = await pgDB.fFetch_InsertQuery_args(
            self.pool_base,
            query,
            user_id,
            story_id,
            scene_id,
            hint_text,
            json.dumps(hint_text_trs)
        )

        if result:
            hint_id = result[0][0] if isinstance(result[0], tuple) else result[0]
            logger.info(f"Saved hint {hint_id} for user {user_id}")
        else:
            logger.error("Failed to save hint")

    async def _get_last_hint_time(
            self,
            user_id: int,
            story_id: int,
            scene_id: int
    ) -> Optional[datetime]:
        """Получить время последней подсказки в сцене"""

        query = """
            SELECT c_shown_at
            FROM t_story_narrator_hints
            WHERE c_user_id = $1 AND c_story_id = $2 AND c_scene_id = $3
            ORDER BY c_shown_at DESC
            LIMIT 1
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            query,
            user_id,
            story_id,
            scene_id
        )

        if result:
            return result[0][0]

        return None

    async def _get_scene_entry_time(
            self,
            user_id: int,
            story_id: int,
            scene_id: int
    ) -> Optional[datetime]:
        """Получить время входа в сцену"""

        query = """
            SELECT c_timestamp
            FROM t_story_user_interactions
            WHERE c_user_id = $1 AND c_story_id = $2 AND c_scene_id = $3
            ORDER BY c_timestamp ASC
            LIMIT 1
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            query,
            user_id,
            story_id,
            scene_id
        )

        if result:
            return result[0][0]

        return None

    async def _get_recent_actions(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,
            limit: int = 5
    ) -> list:
        """Получить последние действия пользователя в сцене"""

        query = """
            SELECT 
                c_interaction_type,
                c_user_input,
                c_timestamp
            FROM t_story_user_interactions
            WHERE c_user_id = $1 AND c_story_id = $2 AND c_scene_id = $3
            ORDER BY c_timestamp DESC
            LIMIT $4
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            query,
            user_id,
            story_id,
            scene_id,
            limit
        )

        actions = []
        for row in result:
            actions.append({
                'interaction_type': row[0],
                'user_input': row[1],
                'timestamp': row[2]
            })

        # Reverse чтобы были от старых к новым
        actions.reverse()

        return actions

    async def analyze_stuck_reason(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,
            scene_context: Dict[str, Any],
            user_progress: Dict[str, Any]
    ) -> str:
        """
        Проанализировать почему пользователь застрял

        Args:
            user_id: ID пользователя
            story_id: ID истории
            scene_id: ID сцены
            scene_context: Контекст сцены
            user_progress: Прогресс пользователя

        Returns:
            'no_progress', 'wrong_npc', 'missing_item', 'wrong_approach'
        """

        success_conditions = scene_context.get('success_conditions', {})
        condition_type = success_conditions.get('type')

        # Анализ по типу условия
        if condition_type == 'item_obtained':
            # Проверяем есть ли предмет
            target_item = success_conditions.get('target')
            user_inventory = user_progress.get('inventory', [])

            # Получаем информацию о предмете
            from handlers.learnpath.story.managers.item_manager import ItemManager
            item_manager = ItemManager((self.pool_base, self.pool_log))

            has_item = False
            for item_id in user_inventory:
                item = await item_manager.get_item(item_id)
                if item and item['name'] == target_item:
                    has_item = True
                    break

            if not has_item:
                return 'missing_item'

        elif condition_type == 'dialogue_complete':
            # Проверяем говорит ли с правильным NPC
            target_npc = success_conditions.get('target')
            recent_actions = await self._get_recent_actions(user_id, story_id, scene_id, limit=3)

            # Получаем список NPC в сцене
            npcs_present = scene_context.get('npcs_present', [])

            from handlers.learnpath.story.managers.npc_manager import NPCManager
            npc_manager = NPCManager((self.pool_base, self.pool_log))

            target_npc_id = None
            for npc_id in npcs_present:
                npc = await npc_manager.get_npc(npc_id)
                if npc and npc['name'] == target_npc:
                    target_npc_id = npc_id
                    break

            # Проверяем взаимодействовал ли с правильным NPC
            talked_to_target = False
            for action in recent_actions:
                if action.get('target_npc_id') == target_npc_id:
                    talked_to_target = True
                    break

            if not talked_to_target and len(recent_actions) >= 3:
                return 'wrong_npc'

        # По умолчанию
        return 'no_progress'