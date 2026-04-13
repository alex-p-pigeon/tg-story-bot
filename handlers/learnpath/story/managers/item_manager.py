"""
Item Manager - Управление предметами в интерактивных историях
"""

import logging
from typing import Dict, Any, Optional, List
import fpgDB as pgDB
import json

logger = logging.getLogger(__name__)


class ItemManager:
    """Управление предметами в интерактивных историях"""

    def __init__(self, pool):
        self.pool_base, self.pool_log = pool

    async def create_item(
            self,
            story_id: int,
            name: str,
            description: str,
            purpose: str = None,
            initial_location: str = None,
            is_key_item: bool = False,
            name_trs: dict = None,
            description_trs: dict = None
    ) -> int:
        """
        Создать предмет

        Args:
            story_id: ID истории
            name: Название предмета (English)
            description: Описание предмета (English)
            purpose: Зачем нужен предмет
            initial_location: 'npc:John', 'scene:1', 'inventory'
            is_key_item: Ключевой предмет для прогресса?
            name_trs: {"ru": "Название на русском"}
            description_trs: {"ru": "Описание на русском"}

        Returns:
            item_id нового предмета
        """

        query = """
            INSERT INTO t_story_items 
                (c_story_id, c_name, c_description, c_purpose,
                 c_initial_location, c_is_key_item, 
                 c_name_trs, c_description_trs)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING c_item_id
        """

        result = await pgDB.fFetch_InsertQuery_args(
            self.pool_base,
            query,
            story_id,
            name,
            description,
            purpose,
            initial_location,
            is_key_item,
            json.dumps(name_trs) if name_trs else None,
            json.dumps(description_trs) if description_trs else None
        )

        if not result:
            raise Exception(f"Failed to create item {name}")

        item_id = result[0][0] if isinstance(result[0], tuple) else result[0]

        logger.info(f"Created item {name} (ID: {item_id}) for story {story_id}")

        return item_id

    async def can_acquire_item(
            self,
            item_id: int,
            user_id: int,
            story_id: int,
            scene_id: int
    ) -> tuple[bool, str]:
        """
        Проверить может ли пользователь получить item

        Returns:
            (can_acquire: bool, reason: str)
        """

        # Получаем item
        query = """
            SELECT c_acquisition_conditions
            FROM t_story_items
            WHERE c_item_id = $1
        """

        result = await pgDB.fExec_SelectQuery_args(self.pool_base, query, item_id)

        if not result:
            return False, "Item not found"

        conditions = result[0][0]
        if isinstance(conditions, str):
            conditions = json.loads(conditions)

        condition_type = conditions.get('type')
        requirements = conditions.get('requirements', {})

        if condition_type == 'search':
            # Для search items - всегда можно получить
            return True, "OK"

        elif condition_type == 'automatic':
            # Items с automatic уже в инвентаре с начала
            return True, "OK"


        elif condition_type == 'npc_gives':

            # Items которые NPC отдаёт через диалог

            # Проверить выполнены ли условия диалога

            npc_name = requirements.get('npc_name')

            min_interactions = requirements.get('min_interactions', 0)

            keywords = requirements.get('keywords', [])

            if not npc_name:
                return True, "OK"  # Нет требований - можно взять

            # Проверить количество сообщений

            from handlers.learnpath.story.engines.dialogue_engine import DialogueEngine

            dialogue_engine = DialogueEngine((self.pool_base, self.pool_log), user_id)

            messages_count = await dialogue_engine._count_messages_with_npc(

                user_id, story_id, scene_id, npc_name

            )

            if messages_count < min_interactions:
                return False, f"You need to talk more with {npc_name}"

            # Если есть keywords - проверить их наличие в диалоге

            if keywords:

                full_dialogue = await dialogue_engine._get_full_dialogue_text(

                    user_id, story_id, scene_id

                )

                keywords_found = sum(1 for kw in keywords if kw.lower() in full_dialogue.lower())

                threshold = len(keywords) * 0.3  # 30% keywords достаточно

                if keywords_found < threshold:
                    return False, f"Discuss more with {npc_name} about this topic"

            return True, "OK"

        elif condition_type == 'npc_dialogue':
            # Проверить выполнены ли условия диалога
            npc_name = requirements.get('npc')
            keywords = requirements.get('keywords', [])
            min_messages = requirements.get('min_messages', 0)

            # Проверить количество сообщений
            from handlers.learnpath.story.engines.dialogue_engine import DialogueEngine
            dialogue_engine = DialogueEngine((self.pool_base, self.pool_log), user_id)

            messages_count = await dialogue_engine._count_messages_with_npc(
                user_id, story_id, scene_id, npc_name
            )

            if messages_count < min_messages:
                return False, f"Need to talk more with {npc_name}"

            # Проверить keywords в диалоге
            full_dialogue = await dialogue_engine._get_full_dialogue_text(
                user_id, story_id, scene_id
            )

            keywords_found = sum(1 for kw in keywords if kw.lower() in full_dialogue.lower())
            threshold = len(keywords) * 0.5

            if keywords_found < threshold:
                return False, f"Need to discuss specific topics with {npc_name}"

            return True, "OK"

        elif condition_type == 'container':
            # Контейнеры нельзя взять, их можно только открыть/использовать
            required_item = requirements.get('required_item', 'key')
            return False, f"This is a locked container. You need to use {required_item} on it."

        return False, "Unknown acquisition type"

    async def get_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Получить информацию о предмете"""

        query = """
            SELECT 
                c_item_id,
                c_story_id,
                c_name,
                c_name_trs,
                c_description,
                c_description_trs,
                c_purpose,
                c_initial_location,
                c_is_key_item
            FROM t_story_items
            WHERE c_item_id = $1
        """

        result = await pgDB.fExec_SelectQuery_args(self.pool_base, query, item_id)

        if not result:
            return None

        row = result[0]

        # Парсим JSONB поля
        name_trs = row[3]
        if isinstance(name_trs, str):
            name_trs = json.loads(name_trs) if name_trs else {}

        description_trs = row[5]
        if isinstance(description_trs, str):
            description_trs = json.loads(description_trs) if description_trs else {}

        return {
            'item_id': row[0],
            'story_id': row[1],
            'name': row[2],
            'name_trs': name_trs,
            'description': row[4],
            'description_trs': description_trs,
            'purpose': row[6],
            'initial_location': row[7],
            'is_key_item': row[8]
        }

    async def get_items_in_scene(
            self,
            story_id: int,
            scene_id: int
    ) -> List[Dict[str, Any]]:
        """
        Получить список предметов доступных в сцене

        Args:
            story_id: ID истории
            scene_id: ID сцены

        Returns:
            Список предметов с их данными
        """

        # Получаем список item ID из сцены
        scene_query = """
            SELECT c_items_available
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

        item_ids = result[0][0]
        if isinstance(item_ids, str):
            item_ids = json.loads(item_ids)

        if not item_ids:
            return []

        # Получаем полную информацию о каждом предмете
        items = []
        for item_id in item_ids:
            item = await self.get_item(item_id)
            if item:
                items.append(item)

        return items

    async def get_user_inventory(
            self,
            user_id: int,
            story_id: int
    ) -> List[Dict[str, Any]]:
        """
        Получить инвентарь пользователя

        Args:
            user_id: ID пользователя
            story_id: ID истории

        Returns:
            Список предметов в инвентаре с полной информацией
        """

        # Получаем список item ID из прогресса
        query = """
            SELECT c_inventory
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
            return []

        inventory = result[0][0]
        if isinstance(inventory, str):
            inventory = json.loads(inventory) if inventory else []

        if not inventory:
            return []

        # Получаем полную информацию о каждом предмете
        items = []
        for item_id in inventory:
            item = await self.get_item(item_id)
            if item:
                items.append(item)

        return items

    async def add_item_to_inventory(
            self,
            user_id: int,
            story_id: int,
            item_id: int
    ) -> bool:
        """
        Добавить предмет в инвентарь пользователя

        Args:
            user_id: ID пользователя
            story_id: ID истории
            item_id: ID предмета

        Returns:
            True если успешно добавлено
        """

        # Получаем текущий инвентарь
        query = """
            SELECT c_inventory
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
            return False

        inventory = result[0][0]
        if isinstance(inventory, str):
            inventory = json.loads(inventory) if inventory else []

        # Проверяем что предмет еще не в инвентаре
        if item_id in inventory:
            logger.warning(f"Item {item_id} already in inventory for user {user_id}")
            return False

        # Добавляем предмет
        inventory.append(item_id)

        # Обновляем в БД
        update_query = """
            UPDATE t_story_user_progress
            SET c_inventory = $1
            WHERE c_user_id = $2 AND c_story_id = $3
        """

        await pgDB.fExec_UpdateQuery_args(
            self.pool_base,
            update_query,
            json.dumps(inventory),
            user_id,
            story_id
        )

        # Получаем название предмета для лога
        item = await self.get_item(item_id)
        item_name = item['name'] if item else f"Item#{item_id}"

        logger.info(f"Added item {item_name} to user {user_id} inventory")

        return True

    async def remove_item_from_inventory(
            self,
            user_id: int,
            story_id: int,
            item_id: int
    ) -> bool:
        """
        Удалить предмет из инвентаря (использован/потерян)

        Args:
            user_id: ID пользователя
            story_id: ID истории
            item_id: ID предмета

        Returns:
            True если успешно удалено
        """

        # Получаем текущий инвентарь
        query = """
            SELECT c_inventory
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
            return False

        inventory = result[0][0]
        if isinstance(inventory, str):
            inventory = json.loads(inventory) if inventory else []

        # Проверяем что предмет в инвентаре
        if item_id not in inventory:
            logger.warning(f"Item {item_id} not in inventory for user {user_id}")
            return False

        # Удаляем предмет
        inventory.remove(item_id)

        # Обновляем в БД
        update_query = """
            UPDATE t_story_user_progress
            SET c_inventory = $1
            WHERE c_user_id = $2 AND c_story_id = $3
        """

        await pgDB.fExec_UpdateQuery_args(
            self.pool_base,
            update_query,
            json.dumps(inventory),
            user_id,
            story_id
        )

        logger.info(f"Removed item {item_id} from user {user_id} inventory")

        return True

    async def check_item_in_inventory(
            self,
            user_id: int,
            story_id: int,
            item_id: int
    ) -> bool:
        """
        Проверить есть ли предмет в инвентаре

        Args:
            user_id: ID пользователя
            story_id: ID истории
            item_id: ID предмета

        Returns:
            True если предмет есть в инвентаре
        """

        query = """
            SELECT c_inventory
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
            return False

        inventory = result[0][0]
        if isinstance(inventory, str):
            inventory = json.loads(inventory) if inventory else []

        return item_id in inventory

    async def use_item(
            self,
            user_id: int,
            story_id: int,
            item_id: int,
            target: str,  # 'npc:John' или 'scene_object:door'
            remove_after_use: bool = True
    ) -> Dict[str, Any]:
        """
        Использовать предмет

        Args:
            user_id: ID пользователя
            story_id: ID истории
            item_id: ID предмета
            target: На что используется ('npc:name' или 'scene_object:name')
            remove_after_use: Удалить предмет после использования?

        Returns:
            {
                'success': True/False,
                'message': 'описание результата',
                'item_removed': True/False
            }
        """

        # Проверяем есть ли предмет у пользователя
        has_item = await self.check_item_in_inventory(user_id, story_id, item_id)

        if not has_item:
            return {
                'success': False,
                'message': "You don't have this item",
                'item_removed': False
            }

        # Получаем информацию о предмете
        item = await self.get_item(item_id)

        if not item:
            return {
                'success': False,
                'message': "Item not found",
                'item_removed': False
            }

        # Логируем использование предмета
        logger.info(f"User {user_id} used item {item['name']} on {target}")

        # Удаляем предмет если нужно
        item_removed = False
        if remove_after_use:
            item_removed = await self.remove_item_from_inventory(
                user_id,
                story_id,
                item_id
            )

        return {
            'success': True,
            'message': f"Used {item['name']} on {target}",
            'item': item,
            'item_removed': item_removed
        }

    async def get_items_by_location(
            self,
            story_id: int,
            location: str
    ) -> List[Dict[str, Any]]:
        """
        Получить предметы по их начальному расположению

        Args:
            story_id: ID истории
            location: 'npc:John', 'scene:1', etc

        Returns:
            Список предметов
        """

        query = """
            SELECT c_item_id
            FROM t_story_items
            WHERE c_story_id = $1 AND c_initial_location = $2
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            query,
            story_id,
            location
        )

        items = []
        for row in result:
            item = await self.get_item(row[0])
            if item:
                items.append(item)

        return items

    async def transfer_items_from_npc(
            self,
            user_id: int,
            story_id: int,
            npc_name: str
    ) -> List[Dict[str, Any]]:
        """
        Передать все предметы от NPC пользователю

        Используется когда NPC дает предметы пользователю

        Args:
            user_id: ID пользователя
            story_id: ID истории
            npc_name: Имя NPC

        Returns:
            Список переданных предметов
        """

        location = f"npc:{npc_name}"

        # Получаем предметы у NPC
        items = await self.get_items_by_location(story_id, location)

        transferred = []

        for item in items:
            # Добавляем в инвентарь пользователя
            success = await self.add_item_to_inventory(
                user_id,
                story_id,
                item['item_id']
            )

            if success:
                transferred.append(item)

        if transferred:
            logger.info(
                f"Transferred {len(transferred)} items from {npc_name} "
                f"to user {user_id}"
            )

        return transferred

    async def can_use_item_on_container(
            self,
            container_id: int,
            user_id: int,
            story_id: int
    ) -> tuple[bool, str, Optional[int]]:
        """
        Проверить можно ли использовать требуемый item на контейнере

        Args:
            container_id: ID контейнера
            user_id: ID пользователя
            story_id: ID истории

        Returns:
            (can_use: bool, message: str, required_item_id: Optional[int])
        """

        # Получить информацию о контейнере
        query = """
            SELECT c_acquisition_conditions, c_name
            FROM t_story_items
            WHERE c_item_id = $1
        """

        result = await pgDB.fExec_SelectQuery_args(self.pool_base, query, container_id)

        if not result:
            return False, "Container not found", None

        conditions = result[0][0]
        container_name = result[0][1]

        if isinstance(conditions, str):
            conditions = json.loads(conditions) if conditions else {}

        condition_type = conditions.get('type')
        requirements = conditions.get('requirements', {})

        # Проверить что это контейнер
        if condition_type != 'container':
            return False, f"{container_name} is not a container", None

        # Получить требуемый item
        required_item_id = requirements.get('required_item_id')
        required_item_name = requirements.get('required_item', 'key')

        if not required_item_id:
            return False, "Container requirements not configured properly", None

        # Проверить есть ли требуемый item в инвентаре
        has_required_item = await self.check_item_in_inventory(
            user_id, story_id, required_item_id
        )

        if not has_required_item:
            return False, f"You need {required_item_name} to open this container", required_item_id

        # ✅ Все проверки пройдены
        return True, "OK", required_item_id

    async def get_container_contents(
            self,
            container_id: int,
            story_id: int
    ) -> Dict[str, Any]:
        """
        Получить содержимое контейнера (what happens on_open)

        Args:
            container_id: ID контейнера
            story_id: ID истории

        Returns:
            {
                'revelation_text': str or None,
                'revelation_text_trs': dict or None,
                'items_inside': List[int],  # item_ids
                'trigger_scene_reveal': bool,
                'trigger_final_message': bool,
                'custom_message': str or None
            }
        """

        # Получить acquisition_conditions контейнера
        query = """
            SELECT c_acquisition_conditions
            FROM t_story_items
            WHERE c_item_id = $1 AND c_story_id = $2
        """

        result = await pgDB.fExec_SelectQuery_args(self.pool_base, query, container_id, story_id)

        if not result:
            return {}

        conditions = result[0][0]
        if isinstance(conditions, str):
            conditions = json.loads(conditions) if conditions else {}

        # Получить on_open configuration
        on_open = conditions.get('on_open', {})

        return {
            'revelation_text': on_open.get('revelation_text'),
            'revelation_text_trs': on_open.get('revelation_text_trs', {}),
            'items_inside': on_open.get('items_inside', []),
            'trigger_scene_reveal': on_open.get('trigger_scene_reveal', False),
            'trigger_final_message': on_open.get('trigger_final_message', False),
            'custom_message': on_open.get('custom_message')
        }

    async def add_items_from_container(
            self,
            user_id: int,
            story_id: int,
            item_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Добавить несколько items из контейнера в инвентарь пользователя

        Args:
            user_id: ID пользователя
            story_id: ID истории
            item_ids: Список ID items для добавления

        Returns:
            Список добавленных items с их информацией:
            [
                {
                    'item_id': int,
                    'name': str,
                    'description': str,
                    'added': bool
                }
            ]
        """

        added_items = []

        for item_id in item_ids:
            # Проверить что item еще не в инвентаре
            already_has = await self.check_item_in_inventory(user_id, story_id, item_id)

            if already_has:
                logger.info(f"User {user_id} already has item {item_id}, skipping")
                continue

            # Получить информацию об item
            item = await self.get_item(item_id)

            if not item:
                logger.warning(f"Item {item_id} not found, skipping")
                continue

            # Добавить в инвентарь
            try:
                await self.add_item_to_inventory(user_id, story_id, item_id)

                added_items.append({
                    'item_id': item_id,
                    'name': item['name'],
                    'description': item.get('description', ''),
                    'added': True
                })

                logger.info(f"Added item {item['name']} (id={item_id}) to user {user_id} inventory")

            except Exception as e:
                logger.error(f"Error adding item {item_id} to inventory: {e}")
                added_items.append({
                    'item_id': item_id,
                    'name': item.get('name', 'Unknown'),
                    'description': '',
                    'added': False
                })

        return added_items