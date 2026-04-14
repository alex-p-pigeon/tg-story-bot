"""
Unit-тесты для StorySkeletonGenerator
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from handlers.learnpath.story.generators.skeleton_generator import StorySkeletonGenerator


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
def skeleton_generator(mock_pool):
    """StorySkeletonGenerator с моком БД"""
    return StorySkeletonGenerator(mock_pool)


@pytest.fixture
def sample_lesson_context():
    """Контекст первого урока"""
    return {
        'grammar_focus': 'Present Simple',
        'cefr_level': 'B1',
        'module_id': 30,
        'module_name': 'Test Module',
        'lesson_name': 'Lesson 1',
        'lesson_id': 100
    }


@pytest.fixture
def sample_ai_response():
    """Пример корректного ответа от AI"""
    return {
        "story_name": "The Lost Key",
        "description": "A mystery adventure in the city",
        "npcs": [
            {
                "npc_id": 0,
                "name": "John",
                "gender": "male",
                "age_group": "middle",
                "personality": {"traits": ["helpful", "friendly"], "base_mood": "calm"},
                "role_description": "Local guide",
                "goals": {"primary": "Help find the key", "secondary": ["Give directions"]},
                "appears_in_scenes": [1, 2]
            },
            {
                "npc_id": 1,
                "name": "Maria",
                "gender": "female",
                "age_group": "young",
                "personality": {"traits": ["energetic", "curious"], "base_mood": "excited"},
                "role_description": "Friend",
                "goals": {"primary": "Encourage user", "secondary": []},
                "appears_in_scenes": [1, 3]
            },
            {
                "npc_id": 2,
                "name": "Tom",
                "gender": "male",
                "age_group": "old",
                "personality": {"traits": ["wise", "patient"], "base_mood": "thoughtful"},
                "role_description": "Keeper of secrets",
                "goals": {"primary": "Test user's knowledge", "secondary": ["Give final clue"]},
                "appears_in_scenes": [3, 4]
            },
            {
                "npc_id": 3,
                "name": "Sarah",
                "gender": "female",
                "age_group": "middle",
                "personality": {"traits": ["mysterious", "clever"], "base_mood": "neutral"},
                "role_description": "Information broker",
                "goals": {"primary": "Trade information for items", "secondary": []},
                "appears_in_scenes": [2]
            },
            {
                "npc_id": 4,
                "name": "Carlos",
                "gender": "male",
                "age_group": "young",
                "personality": {"traits": ["adventurous", "brave"], "base_mood": "confident"},
                "role_description": "Fellow explorer",
                "goals": {"primary": "Join user's quest", "secondary": ["Share map"]},
                "appears_in_scenes": [2, 3, 4]
            }
        ],
        "items": [
            {
                "item_id": 0,
                "name": "Old Key",
                "description": "A rusty old key with strange markings",
                "purpose": "Opens the secret door",
                "initial_location": "npc:Tom",
                "obtain_condition": "Talk to Tom and ask about the key"
            },
            {
                "item_id": 1,
                "name": "Map",
                "description": "An old city map with X marks",
                "purpose": "Shows location of the key",
                "initial_location": "npc:Carlos",
                "obtain_condition": "Ask Carlos for directions"
            },
            {
                "item_id": 2,
                "name": "Note",
                "description": "A cryptic note",
                "purpose": "Provides clue about the lock",
                "initial_location": "npc:Sarah",
                "obtain_condition": "Trade information with Sarah"
            }
        ],
        "scenes": [
            {
                "scene_id": 1,
                "chapter_number": 1,
                "scene_name": "The Beginning",
                "scene_number": 1,
                "location_name": "City Square",
                "location_description": "A busy city square with a fountain",
                "objective": "Find out what happened to the key",
                "npcs_present": [0, 1],
                "items_available": [],
                "success_conditions": {
                    "type": "dialogue_complete",
                    "target": "John",
                    "keywords": ["key", "lost"]
                },
                "next_scene_id": 2,
                "is_ending": False,
                "ending_type": None
            },
            {
                "scene_id": 2,
                "chapter_number": 1,
                "scene_name": "The Market",
                "scene_number": 2,
                "location_name": "City Market",
                "location_description": "A colorful market with many stalls",
                "objective": "Get the map from Carlos",
                "npcs_present": [3, 4],
                "items_available": [1],
                "success_conditions": {
                    "type": "item_obtained",
                    "target": "Map",
                    "keywords": []
                },
                "next_scene_id": 3,
                "is_ending": False,
                "ending_type": None
            },
            {
                "scene_id": 3,
                "chapter_number": 2,
                "scene_name": "The Library",
                "scene_number": 1,
                "location_name": "Old Library",
                "location_description": "A dusty library full of old books",
                "objective": "Decode the map",
                "npcs_present": [1, 2, 4],
                "items_available": [2],
                "success_conditions": {
                    "type": "item_use",
                    "target": "Map",
                    "keywords": ["door", "secret"]
                },
                "next_scene_id": 4,
                "is_ending": False,
                "ending_type": None
            },
            {
                "scene_id": 4,
                "chapter_number": 2,
                "scene_name": "The Secret Room",
                "scene_number": 2,
                "location_name": "Hidden Room",
                "location_description": "A hidden room behind a secret door",
                "objective": "Unlock the final door",
                "npcs_present": [2],
                "items_available": [0],
                "success_conditions": {
                    "type": "item_use",
                    "target": "Old Key",
                    "keywords": ["door"]
                },
                "next_scene_id": None,
                "is_ending": True,
                "ending_type": "good"
            }
        ]
    }


# ============================================================================
# Tests для StorySkeletonGenerator
# ============================================================================

class TestStorySkeletonGenerator:

    @pytest.mark.asyncio
    async def test_generate_skeleton_success(self, skeleton_generator, sample_ai_response, sample_lesson_context):
        """Тест успешной генерации каркаса"""

        with patch('selfFunctions.afSendMsg2AI', new_callable=AsyncMock) as mock_ai, \
                patch.object(skeleton_generator, '_save_skeleton_to_db', new_callable=AsyncMock) as mock_save:
            mock_ai.return_value = json.dumps(sample_ai_response)
            mock_save.return_value = 42  # story_id

            result = await skeleton_generator.generate_skeleton(
                user_id=123,
                genre='mystery',
                mood='tense',
                realism='fully_realistic',
                complexity=['puzzles', 'dialogues'],
                goal='learn_truth',
                initial_lesson_context=sample_lesson_context,
                num_chapters=2,
                scenes_structure=[2, 2]
            )

            assert result['story_name'] == "The Lost Key"
            assert len(result['npcs']) == 5
            assert len(result['items']) == 3
            assert len(result['scenes']) == 4
            assert result['story_id'] == 42

            mock_ai.assert_called_once()
            call_args = mock_ai.call_args
            assert call_args[1]['iModel'] == 4  # GPT-4o
            assert call_args[1]['toggleParam'] == 3  # Temperature 0.7

    @pytest.mark.asyncio
    async def test_generate_skeleton_with_markdown_removal(self, skeleton_generator, sample_ai_response, sample_lesson_context):
        """Тест удаления markdown code blocks из ответа AI"""

        with patch('selfFunctions.afSendMsg2AI', new_callable=AsyncMock) as mock_ai, \
                patch.object(skeleton_generator, '_save_skeleton_to_db', new_callable=AsyncMock) as mock_save:
            mock_ai.return_value = f"```json\n{json.dumps(sample_ai_response)}\n```"
            mock_save.return_value = 42

            result = await skeleton_generator.generate_skeleton(
                user_id=123,
                genre='adventure',
                mood='optimistic',
                realism='unusual_real',
                complexity=['simple_plot', 'action'],
                goal='complete_mission',
                initial_lesson_context=sample_lesson_context,
                num_chapters=1,
                scenes_structure=[4]
            )

            assert 'story_name' in result
            assert isinstance(result['npcs'], list)

    @pytest.mark.asyncio
    async def test_generate_skeleton_invalid_json(self, skeleton_generator, sample_lesson_context):
        """Тест обработки невалидного JSON от AI"""

        with patch('selfFunctions.afSendMsg2AI', new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = "This is not JSON at all!"

            with pytest.raises(Exception) as exc_info:
                await skeleton_generator.generate_skeleton(
                    user_id=123,
                    genre='comedy',
                    mood='funny',
                    realism='full_fantasy',
                    complexity=['dialogues', 'emotional'],
                    goal='find_allies',
                    initial_lesson_context=sample_lesson_context,
                    num_chapters=1,
                    scenes_structure=[3]
                )

            assert "invalid json" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_parse_ai_response_success(self, skeleton_generator, sample_ai_response):
        """Тест успешного парсинга ответа AI"""

        result = skeleton_generator._parse_ai_response(json.dumps(sample_ai_response))

        assert result['story_name'] == "The Lost Key"
        assert 'npcs' in result
        assert 'items' in result
        assert 'scenes' in result

    @pytest.mark.asyncio
    async def test_parse_ai_response_missing_field(self, skeleton_generator, sample_ai_response):
        """Тест валидации с отсутствующим обязательным полем"""

        invalid_data = sample_ai_response.copy()
        del invalid_data['story_name']

        with pytest.raises(ValueError) as exc_info:
            skeleton_generator._parse_ai_response(json.dumps(invalid_data))

        assert "Missing required field" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_parse_ai_response_with_markdown(self, skeleton_generator, sample_ai_response):
        """Тест парсинга ответа с markdown блоками"""

        markdown_response = f"```json\n{json.dumps(sample_ai_response)}\n```"
        result = skeleton_generator._parse_ai_response(markdown_response)

        assert result['story_name'] == "The Lost Key"

    @pytest.mark.asyncio
    async def test_parse_ai_response_invalid_json(self, skeleton_generator):
        """Тест парсинга невалидного JSON"""

        with pytest.raises(ValueError) as exc_info:
            skeleton_generator._parse_ai_response("not valid json")

        assert "invalid json" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_build_user_prompt(self, skeleton_generator):
        """Тест создания промпта для AI"""

        prompt = skeleton_generator._build_user_prompt(
            genre="Mystery/Detective",
            mood="Tense (dangers, survival, stress)",
            realism="Fully realistic (shipwreck, accident)",
            complexity=["Puzzles and mysteries", "Lots of dialogues"],
            goal="Learn the truth - who am I? what happened?",
            grammar_focus="Present Simple",
            cefr_level="B1",
            num_chapters=2,
            scenes_structure=[2, 2]
        )

        assert "Mystery/Detective" in prompt
        assert "Tense" in prompt
        assert "Fully realistic" in prompt
        assert "Puzzles and mysteries" in prompt
        assert "Present Simple" in prompt


# ============================================================================
# Интеграционные тесты (требуют реальной БД)
# ============================================================================

@pytest.mark.integration
class TestStorySkeletonGeneratorIntegration:
    """
    Интеграционные тесты с реальной БД
    Запускать только при наличии тестовой БД
    """

    @pytest.mark.asyncio
    async def test_full_generation_and_save_cycle(self):
        """Полный цикл генерации и сохранения (требует реальную БД)"""
        pytest.skip("Requires real database connection")


# ============================================================================
# Запуск тестов
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
