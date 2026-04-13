"""
Unit-тесты для DialogueEngine
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json

import sys

sys.path.append('..')
from engines.dialogue_engine import DialogueEngine


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
def dialogue_engine(mock_pool):
    """DialogueEngine с моком БД"""
    return DialogueEngine(mock_pool, user_id=123)


@pytest.fixture
def sample_npc_context():
    """Пример контекста NPC"""
    return {
        'npc_id': 1,
        'name': 'John',
        'gender': 'male',
        'age_group': 'middle',
        'personality': {
            'traits': ['friendly', 'helpful'],
            'base_mood': 'calm'
        },
        'role_description': 'Local guide',
        'goals': {
            'primary': 'Help user find the key',
            'secondary': ['Give directions', 'Share local knowledge']
        },
        'user_state': {
            'met': True,
            'current_mood': 'friendly'
        },
        'recent_interactions': [
            {
                'user_input': 'Hello!',
                'ai_response': 'Hi there! How can I help you?'
            }
        ]
    }


@pytest.fixture
def sample_scene_context():
    """Пример контекста сцены"""
    return {
        'scene_id': 1,
        'location_name': 'Central Park',
        'location_description': 'A beautiful park in the city center.',
        'objective': 'Talk to John and get information about the key'
    }


@pytest.fixture
def sample_story_context():
    """Пример контекста истории"""
    return {
        'story_id': 1,
        'story_name': 'The Lost Key',
        'grammar_context': 'Present Simple',
        'difficulty_level': 3
    }


@pytest.fixture
def sample_ai_response():
    """Пример корректного ответа от AI"""
    return {
        'teacher': "I know where the key is! It's in the old house on the hill.",
        'correction': "Great job! Your English is very good.",
        'npc_action': "smiles warmly",
        'text_trs': {
            'ru': "Я знаю где ключ! Он в старом доме на холме."
        },
        'correction_trs': {
            'ru': "Отлично! Ваш английский очень хорош."
        }
    }


# ============================================================================
# Tests для DialogueEngine
# ============================================================================

class TestDialogueEngine:

    @pytest.mark.asyncio
    async def test_generate_npc_response_success(
            self,
            dialogue_engine,
            sample_npc_context,
            sample_scene_context,
            sample_story_context,
            sample_ai_response
    ):
        """Тест успешной генерации ответа NPC"""

        with patch('selfFunctions.afSendMsg2AI', new_callable=AsyncMock) as mock_ai:
            # Мокаем ответ AI
            mock_ai.return_value = json.dumps(sample_ai_response)

            result = await dialogue_engine.generate_npc_response(
                user_input="Where is the key?",
                npc_context=sample_npc_context,
                scene_context=sample_scene_context,
                story_context=sample_story_context,
                user_level=3
            )

            # Проверяем структуру результата
            assert 'teacher' in result
            assert 'correction' in result
            assert result['npc_name'] == 'John'
            assert result['npc_id'] == 1

            # Проверяем что AI был вызван правильно
            mock_ai.assert_called_once()
            call_args = mock_ai.call_args
            assert call_args[1]['iModel'] == 4  # GPT-4o

    @pytest.mark.asyncio
    async def test_generate_npc_response_with_markdown(
            self,
            dialogue_engine,
            sample_npc_context,
            sample_scene_context,
            sample_story_context,
            sample_ai_response
    ):
        """Тест удаления markdown из ответа AI"""

        with patch('selfFunctions.afSendMsg2AI', new_callable=AsyncMock) as mock_ai:
            # AI возвращает JSON в markdown
            mock_ai.return_value = f"```json\n{json.dumps(sample_ai_response)}\n```"

            result = await dialogue_engine.generate_npc_response(
                user_input="Hello",
                npc_context=sample_npc_context,
                scene_context=sample_scene_context,
                story_context=sample_story_context,
                user_level=2
            )

            # Парсинг должен пройти успешно
            assert 'teacher' in result
            assert 'correction' in result

    @pytest.mark.asyncio
    async def test_generate_npc_response_invalid_json(
            self,
            dialogue_engine,
            sample_npc_context,
            sample_scene_context,
            sample_story_context
    ):
        """Тест обработки невалидного JSON (fallback)"""

        with patch('selfFunctions.afSendMsg2AI', new_callable=AsyncMock) as mock_ai:
            # AI возвращает невалидный JSON
            mock_ai.return_value = "This is not JSON!"

            result = await dialogue_engine.generate_npc_response(
                user_input="Test",
                npc_context=sample_npc_context,
                scene_context=sample_scene_context,
                story_context=sample_story_context,
                user_level=1
            )

            # Должен вернуть fallback ответ
            assert result['teacher'] == f"I'm {sample_npc_context['name']}. Could you say that again?"
            assert result['npc_name'] == 'John'

    @pytest.mark.asyncio
    async def test_validate_response_structure_success(
            self,
            dialogue_engine,
            sample_ai_response
    ):
        """Тест успешной валидации структуры ответа"""

        # Не должно быть исключений
        dialogue_engine._validate_response_structure(sample_ai_response)

    @pytest.mark.asyncio
    async def test_validate_response_missing_field(
            self,
            dialogue_engine
    ):
        """Тест валидации с отсутствующим полем"""

        invalid_response = {
            'teacher': 'Hello'
            # Нет 'correction'
        }

        with pytest.raises(ValueError) as exc_info:
            dialogue_engine._validate_response_structure(invalid_response)

        assert "Missing required field" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_response_empty_teacher(
            self,
            dialogue_engine
    ):
        """Тест валидации с пустым teacher"""

        invalid_response = {
            'teacher': '',
            'correction': 'Good job'
        }

        with pytest.raises(ValueError) as exc_info:
            dialogue_engine._validate_response_structure(invalid_response)

        assert "cannot be empty" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_fallback_response(
            self,
            dialogue_engine,
            sample_npc_context
    ):
        """Тест создания fallback ответа"""

        result = dialogue_engine._create_fallback_response(sample_npc_context)

        assert 'teacher' in result
        assert 'correction' in result
        assert result['npc_id'] == 1
        assert result['npc_name'] == 'John'
        assert 'Could you say that again?' in result['teacher']

    @pytest.mark.asyncio
    async def test_save_interaction(self, dialogue_engine):
        """Тест сохранения взаимодействия в БД"""

        with patch('fpgDB.fFetch_InsertQuery_args', new_callable=AsyncMock) as mock_insert:
            mock_insert.return_value = [(100,)]  # interaction_id

            await dialogue_engine.save_interaction(
                user_id=123,
                story_id=1,
                scene_id=1,
                interaction_type='dialogue',
                user_input='Hello',
                user_input_type='text',
                target_npc_id=1,
                ai_response='Hi there!',
                correction='Great job!',
                ai_response_trs={'ru': 'Привет!'},
                correction_trs={'ru': 'Отлично!'}
            )

            # Проверяем что insert был вызван
            mock_insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_objective_completion_dialogue_with_keywords(
            self,
            dialogue_engine
    ):
        """Тест проверки завершения диалоговой цели с ключевыми словами"""

        success_conditions = {
            'type': 'dialogue_complete',
            'target': 'John',
            'keywords': ['help', 'key', 'find']
        }

        with patch('fpgDB.fExec_SelectQuery_args', new_callable=AsyncMock) as mock_select:
            mock_select.return_value = [(json.dumps(success_conditions),)]

            recent_interaction = {
                'user_input': 'Can you help me find the key?',
                'interaction_type': 'dialogue'
            }

            result = await dialogue_engine.check_objective_completion(
                scene_id=1,
                story_id=1,
                user_id=123,
                recent_interaction=recent_interaction
            )

            # Все 3 ключевых слова найдены
            assert result == True

    @pytest.mark.asyncio
    async def test_check_objective_completion_dialogue_no_keywords(
            self,
            dialogue_engine
    ):
        """Тест проверки завершения диалоговой цели без ключевых слов"""

        success_conditions = {
            'type': 'dialogue_complete',
            'target': 'John',
            'keywords': []
        }

        with patch('fpgDB.fExec_SelectQuery_args', new_callable=AsyncMock) as mock_select:
            mock_select.return_value = [(json.dumps(success_conditions),)]

            recent_interaction = {
                'user_input': 'Hello',
                'interaction_type': 'dialogue'
            }

            result = await dialogue_engine.check_objective_completion(
                scene_id=1,
                story_id=1,
                user_id=123,
                recent_interaction=recent_interaction
            )

            # Без ключевых слов считаем выполненным сразу
            assert result == True

    @pytest.mark.asyncio
    async def test_check_objective_completion_item_use(
            self,
            dialogue_engine
    ):
        """Тест проверки завершения цели использования предмета"""

        success_conditions = {
            'type': 'item_use',
            'target': 'Key',
            'keywords': ['door']
        }

        with patch('fpgDB.fExec_SelectQuery_args', new_callable=AsyncMock) as mock_select:
            mock_select.return_value = [(json.dumps(success_conditions),)]

            recent_interaction = {
                'interaction_type': 'item_use'
            }

            result = await dialogue_engine.check_objective_completion(
                scene_id=1,
                story_id=1,
                user_id=123,
                recent_interaction=recent_interaction
            )

            assert result == True


# ============================================================================
# Запуск тестов
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])