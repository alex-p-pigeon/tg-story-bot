"""
Unit-тесты для NPCManager и ItemManager
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import json

# Импортируем менеджеры
import sys

sys.path.append('..')
from managers.npc_manager import NPCManager
from managers.item_manager import ItemManager


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_pool():
    """Мок pool для БД"""
    pool_base = Mock()
    pool_log = Mock()
    return (pool_base, pool_log)


@pytest.fixture
def npc_manager(mock_pool):
    """NPCManager с моком БД"""
    return NPCManager(mock_pool)


@pytest.fixture
def item_manager(mock_pool):
    """ItemManager с моком БД"""
    return ItemManager(mock_pool)


# ============================================================================
# Tests для NPCManager
# ============================================================================

class TestNPCManager:

    @pytest.mark.asyncio
    async def test_create_npc_success(self, npc_manager, mock_pool):
        """Тест успешного создания NPC"""

        # Мокаем ответ БД
        with patch('fpgDB.fFetch_InsertQuery_args', new_callable=AsyncMock) as mock_insert:
            mock_insert.return_value = [(123,)]  # npc_id = 123

            npc_id = await npc_manager.create_npc(
                story_id=1,
                name="John",
                gender="male",
                age_group="middle",
                personality={"traits": ["friendly"], "base_mood": "happy"},
                role_description="Guide the user",
                goals={"primary": "Help user find key"}
            )

            assert npc_id == 123
            mock_insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_npc_existing(self, npc_manager):
        """Тест получения существующего NPC"""

        mock_row = (
            1,  # npc_id
            1,  # story_id
            "John",  # name
            "male",  # gender
            "middle",  # age_group
            json.dumps({"traits": ["friendly"]}),  # personality
            "voice_123",  # voice_id
            "Guide",  # role_description
            json.dumps({"primary": "Help"}),  # goals
            json.dumps([1, 2])  # appears_in_scenes
        )

        with patch('fpgDB.fExec_SelectQuery_args', new_callable=AsyncMock) as mock_select:
            mock_select.return_value = [mock_row]

            npc = await npc_manager.get_npc(1)

            assert npc is not None
            assert npc['name'] == "John"
            assert npc['gender'] == "male"
            assert npc['personality']['traits'] == ["friendly"]

    @pytest.mark.asyncio
    async def test_get_npc_not_found(self, npc_manager):
        """Тест получения несуществующего NPC"""

        with patch('fpgDB.fExec_SelectQuery_args', new_callable=AsyncMock) as mock_select:
            mock_select.return_value = []

            npc = await npc_manager.get_npc(999)

            assert npc is None

    @pytest.mark.asyncio
    async def test_update_npc_state(self, npc_manager):
        """Тест обновления состояния NPC"""

        # Мокаем текущее состояние
        current_state = json.dumps({"1": {"met": False}})

        with patch('fpgDB.fExec_SelectQuery_args', new_callable=AsyncMock) as mock_select, \
                patch('fpgDB.fExec_UpdateQuery_args', new_callable=AsyncMock) as mock_update:
            mock_select.return_value = [(current_state,)]

            await npc_manager.update_npc_state(
                user_id=100,
                story_id=1,
                npc_id=1,
                state_updates={"met": True, "info_given": True}
            )

            # Проверяем что update был вызван
            mock_update.assert_called_once()

            # Проверяем что состояние обновилось
            call_args = mock_update.call_args[0]
            updated_state = json.loads(call_args[2])
            assert updated_state["1"]["met"] == True
            assert updated_state["1"]["info_given"] == True

    @pytest.mark.asyncio
    async def test_get_interaction_history(self, npc_manager):
        """Тест получения истории взаимодействий"""

        # Мок возвращает в порядке DESC (новые первые)
        mock_interactions = [
            (2, "How are you?", "I'm good!", "2024-01-02"),
            (1, "Hello", "Hi there!", "2024-01-01")
        ]

        with patch('fpgDB.fExec_SelectQuery_args', new_callable=AsyncMock) as mock_select:
            mock_select.return_value = mock_interactions

            history = await npc_manager.get_interaction_history(
                user_id=100,
                story_id=1,
                npc_id=1,
                limit=5
            )

            assert len(history) == 2
            # После reverse() первым должен быть "Hello" (старый)
            assert history[0]['user_input'] == "Hello"
            assert history[1]['user_input'] == "How are you?"


# ============================================================================
# Tests для ItemManager
# ============================================================================

class TestItemManager:

    @pytest.mark.asyncio
    async def test_create_item_success(self, item_manager):
        """Тест успешного создания предмета"""

        with patch('fpgDB.fFetch_InsertQuery_args', new_callable=AsyncMock) as mock_insert:
            mock_insert.return_value = [(456,)]  # item_id = 456

            item_id = await item_manager.create_item(
                story_id=1,
                name="Key",
                description="Old rusty key",
                purpose="Opens the door",
                initial_location="npc:John",
                is_key_item=True
            )

            assert item_id == 456
            mock_insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_item_existing(self, item_manager):
        """Тест получения существующего предмета"""

        mock_row = (
            1,  # item_id
            1,  # story_id
            "Key",  # name
            json.dumps({"ru": "Ключ"}),  # name_trs
            "Old key",  # description
            json.dumps({"ru": "Старый ключ"}),  # description_trs
            "Opens door",  # purpose
            "npc:John",  # initial_location
            True  # is_key_item
        )

        with patch('fpgDB.fExec_SelectQuery_args', new_callable=AsyncMock) as mock_select:
            mock_select.return_value = [mock_row]

            item = await item_manager.get_item(1)

            assert item is not None
            assert item['name'] == "Key"
            assert item['is_key_item'] == True
            assert item['name_trs']['ru'] == "Ключ"

    @pytest.mark.asyncio
    async def test_add_item_to_inventory(self, item_manager):
        """Тест добавления предмета в инвентарь"""

        current_inventory = json.dumps([])

        with patch('fpgDB.fExec_SelectQuery_args', new_callable=AsyncMock) as mock_select, \
                patch('fpgDB.fExec_UpdateQuery_args', new_callable=AsyncMock) as mock_update, \
                patch.object(item_manager, 'get_item', new_callable=AsyncMock) as mock_get_item:
            mock_select.return_value = [(current_inventory,)]
            mock_get_item.return_value = {'item_id': 1, 'name': 'Key'}

            success = await item_manager.add_item_to_inventory(
                user_id=100,
                story_id=1,
                item_id=1
            )

            assert success == True
            mock_update.assert_called_once()

            # Проверяем что предмет добавлен в инвентарь
            call_args = mock_update.call_args[0]
            updated_inventory = json.loads(call_args[2])
            assert 1 in updated_inventory

    @pytest.mark.asyncio
    async def test_check_item_in_inventory_true(self, item_manager):
        """Тест проверки предмета в инвентаре (есть)"""

        inventory = json.dumps([1, 2, 3])

        with patch('fpgDB.fExec_SelectQuery_args', new_callable=AsyncMock) as mock_select:
            mock_select.return_value = [(inventory,)]

            has_item = await item_manager.check_item_in_inventory(
                user_id=100,
                story_id=1,
                item_id=2
            )

            assert has_item == True

    @pytest.mark.asyncio
    async def test_check_item_in_inventory_false(self, item_manager):
        """Тест проверки предмета в инвентаре (нет)"""

        inventory = json.dumps([1, 2, 3])

        with patch('fpgDB.fExec_SelectQuery_args', new_callable=AsyncMock) as mock_select:
            mock_select.return_value = [(inventory,)]

            has_item = await item_manager.check_item_in_inventory(
                user_id=100,
                story_id=1,
                item_id=999
            )

            assert has_item == False

    @pytest.mark.asyncio
    async def test_use_item_success(self, item_manager):
        """Тест успешного использования предмета"""

        with patch.object(item_manager, 'check_item_in_inventory', new_callable=AsyncMock) as mock_check, \
                patch.object(item_manager, 'get_item', new_callable=AsyncMock) as mock_get, \
                patch.object(item_manager, 'remove_item_from_inventory', new_callable=AsyncMock) as mock_remove:
            mock_check.return_value = True
            mock_get.return_value = {'item_id': 1, 'name': 'Key'}
            mock_remove.return_value = True

            result = await item_manager.use_item(
                user_id=100,
                story_id=1,
                item_id=1,
                target="npc:John"
            )

            assert result['success'] == True
            assert result['item_removed'] == True
            mock_remove.assert_called_once()

    @pytest.mark.asyncio
    async def test_use_item_not_in_inventory(self, item_manager):
        """Тест использования предмета которого нет в инвентаре"""

        with patch.object(item_manager, 'check_item_in_inventory', new_callable=AsyncMock) as mock_check:
            mock_check.return_value = False

            result = await item_manager.use_item(
                user_id=100,
                story_id=1,
                item_id=1,
                target="npc:John"
            )

            assert result['success'] == False
            assert "don't have" in result['message']

    @pytest.mark.asyncio
    async def test_transfer_items_from_npc(self, item_manager):
        """Тест передачи предметов от NPC"""

        mock_items = [
            {'item_id': 1, 'name': 'Key'},
            {'item_id': 2, 'name': 'Map'}
        ]

        with patch.object(item_manager, 'get_items_by_location', new_callable=AsyncMock) as mock_get_items, \
                patch.object(item_manager, 'add_item_to_inventory', new_callable=AsyncMock) as mock_add:
            mock_get_items.return_value = mock_items
            mock_add.return_value = True

            transferred = await item_manager.transfer_items_from_npc(
                user_id=100,
                story_id=1,
                npc_name="John"
            )

            assert len(transferred) == 2
            assert mock_add.call_count == 2


# ============================================================================
# Запуск тестов
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])