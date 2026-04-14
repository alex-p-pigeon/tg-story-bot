"""
Unit-тесты для NarratorSystem
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from handlers.learnpath.story.systems.narrator_system import NarratorSystem


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
def narrator_system(mock_pool):
    """NarratorSystem с моком БД"""
    return NarratorSystem(mock_pool, user_id=123)


@pytest.fixture
def sample_scene_context():
    """Пример контекста сцены"""
    return {
        'scene_id': 1,
        'location_name': 'Central Park',
        'objective': 'Talk to John and get information about the key',
        'success_conditions': {
            'type': 'dialogue_complete',
            'target': 'John',
            'keywords': ['help', 'key']
        }
    }


@pytest.fixture
def sample_user_progress():
    """Пример прогресса пользователя"""
    return {
        'actions_count': 7,
        'inventory': [1, 2],
        'npc_states': {
            '1': {'met': True}
        }
    }


@pytest.fixture
def sample_hint_response():
    """Пример ответа подсказки от AI"""
    return {
        'hint_type': 'inner_thought',
        'text': "I thought, maybe I should talk to John about the key.",
        'text_trs': {
            'ru': "Я подумал, возможно мне стоит поговорить с Джоном о ключе."
        }
    }


# ============================================================================
# Tests для NarratorSystem
# ============================================================================

class TestNarratorSystem:

    @pytest.mark.asyncio
    async def test_check_if_hint_needed_by_actions(self, narrator_system):
        """Тест проверки необходимости подсказки по количеству действий"""

        # Много действий = нужна подсказка
        result = await narrator_system.check_if_hint_needed(
            user_id=123,
            story_id=1,
            scene_id=1,
            actions_count=5
        )

        assert result == True

    @pytest.mark.asyncio
    async def test_check_if_hint_needed_not_enough_actions(self, narrator_system):
        """Тест когда действий мало - подсказка не нужна"""

        result = await narrator_system.check_if_hint_needed(
            user_id=123,
            story_id=1,
            scene_id=1,
            actions_count=2
        )

        assert result == False

    @pytest.mark.asyncio
    async def test_generate_hint_success(
            self,
            narrator_system,
            sample_scene_context,
            sample_user_progress,
            sample_hint_response
    ):
        """Тест успешной генерации подсказки"""

        with patch('selfFunctions.afSendMsg2AI', new_callable=AsyncMock) as mock_ai, \
                patch.object(narrator_system, '_get_recent_actions', new_callable=AsyncMock) as mock_actions, \
                patch('selfFunctions.fGetUserEngLevel', new_callable=AsyncMock, return_value=3):
            mock_ai.return_value = json.dumps(sample_hint_response)
            mock_actions.return_value = []

            result = await narrator_system.generate_hint(
                user_id=123,
                story_id=1,
                scene_id=1,
                scene_context=sample_scene_context,
                user_progress=sample_user_progress,
                stuck_reason='no_progress'
            )

            assert 'text' in result
            assert 'text_trs' in result
            assert 'hint_type' in result

            # Проверяем что AI был вызван
            mock_ai.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_hint_with_markdown(
            self,
            narrator_system,
            sample_scene_context,
            sample_user_progress,
            sample_hint_response
    ):
        """Тест генерации подсказки с удалением markdown"""

        with patch('selfFunctions.afSendMsg2AI', new_callable=AsyncMock) as mock_ai, \
                patch.object(narrator_system, '_get_recent_actions', new_callable=AsyncMock) as mock_actions, \
                patch('selfFunctions.fGetUserEngLevel', new_callable=AsyncMock, return_value=3):
            # AI возвращает JSON в markdown
            mock_ai.return_value = f"```json\n{json.dumps(sample_hint_response)}\n```"
            mock_actions.return_value = []

            result = await narrator_system.generate_hint(
                user_id=123,
                story_id=1,
                scene_id=1,
                scene_context=sample_scene_context,
                user_progress=sample_user_progress
            )

            assert 'text' in result

    @pytest.mark.asyncio
    async def test_generate_hint_invalid_json(
            self,
            narrator_system,
            sample_scene_context,
            sample_user_progress
    ):
        """Тест генерации подсказки с невалидным JSON (fallback)"""

        with patch('selfFunctions.afSendMsg2AI', new_callable=AsyncMock) as mock_ai, \
                patch.object(narrator_system, '_get_recent_actions', new_callable=AsyncMock) as mock_actions, \
                patch('selfFunctions.fGetUserEngLevel', new_callable=AsyncMock, return_value=3):
            mock_ai.return_value = "This is not JSON!"
            mock_actions.return_value = []

            result = await narrator_system.generate_hint(
                user_id=123,
                story_id=1,
                scene_id=1,
                scene_context=sample_scene_context,
                user_progress=sample_user_progress
            )

            # Должен вернуть fallback
            assert 'text' in result
            assert sample_scene_context['objective'] in result['text']

    @pytest.mark.asyncio
    async def test_create_fallback_hint(
            self,
            narrator_system,
            sample_scene_context
    ):
        """Тест создания fallback подсказки"""

        result = narrator_system._create_fallback_hint(sample_scene_context)

        assert 'hint_type' in result
        assert 'text' in result
        assert 'text_trs' in result
        assert sample_scene_context['objective'] in result['text']

    @pytest.mark.asyncio
    async def test_save_hint(self, narrator_system):
        """Тест сохранения подсказки в БД"""

        with patch('fpgDB.fFetch_InsertQuery_args', new_callable=AsyncMock) as mock_insert:
            mock_insert.return_value = [(1,)]  # hint_id

            await narrator_system.save_hint(
                user_id=123,
                story_id=1,
                scene_id=1,
                hint_text="Maybe you should talk to John.",
                hint_text_trs={'ru': 'Возможно стоит поговорить с Джоном.'}
            )

            # Проверяем что insert был вызван
            mock_insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_recent_actions(self, narrator_system):
        """Тест получения последних действий"""

        # Мок возвращает в порядке DESC (новые первые)
        mock_actions = [
            ('action', 'Look around', datetime.now()),  # Самое новое
            ('dialogue', 'Help me', datetime.now()),
            ('dialogue', 'Hello', datetime.now())  # Самое старое
        ]

        with patch('fpgDB.fExec_SelectQuery_args', new_callable=AsyncMock) as mock_select:
            mock_select.return_value = mock_actions

            result = await narrator_system._get_recent_actions(
                user_id=123,
                story_id=1,
                scene_id=1,
                limit=5
            )

            assert len(result) == 3
            # После reverse() первым должен быть 'Hello' (самый старый)
            assert result[0]['interaction_type'] == 'dialogue'
            assert result[0]['user_input'] == 'Hello'
            # Последним должен быть 'Look around' (самый новый)
            assert result[2]['interaction_type'] == 'action'
            assert result[2]['user_input'] == 'Look around'

    @pytest.mark.asyncio
    async def test_create_hint_prompt(
            self,
            narrator_system,
            sample_scene_context,
            sample_user_progress
    ):
        """Тест создания промпта для подсказки"""

        recent_actions = [
            {'interaction_type': 'dialogue', 'user_input': 'Hello', 'timestamp': datetime.now()}
        ]

        prompt = narrator_system._create_hint_prompt(
            scene_context=sample_scene_context,
            user_progress=sample_user_progress,
            recent_actions=recent_actions,
            stuck_reason='no_progress'
        )

        # Проверяем что промпт содержит необходимую информацию
        assert sample_scene_context['objective'] in prompt
        assert 'RESPOND WITH JSON' in prompt
        assert 'subtle hint' in prompt.lower()


# ============================================================================
# Запуск тестов
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])