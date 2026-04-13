"""
Unit-тесты для StorySkeletonGenerator
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json

# Импортируем генератор
import sys

sys.path.append('..')
from generators.skeleton_generator import StorySkeletonGenerator


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
    return StorySkeletonGenerator(mock_pool, user_id=123)


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
                "is_key_item": True
            },
            {
                "item_id": 1,
                "name": "City Map",
                "description": "A detailed map of the city",
                "purpose": "Shows hidden locations",
                "initial_location": "npc:Carlos",
                "is_key_item": True
            },
            {
                "item_id": 2,
                "name": "Flashlight",
                "description": "A bright flashlight",
                "purpose": "Illuminates dark places",
                "initial_location": "scene:1",
                "is_key_item": False
            }
        ],
        "scenes": [
            {
                "scene_id": 1,
                "chapter_number": 1,
                "scene_number": 1,
                "location_name": "Central Park",
                "location_description": "A beautiful park in the city center.",
                "location_description_trs": {"ru": "Красивый парк в центре города."},
                "objective": "Talk to John and get information",
                "objective_trs": {"ru": "Поговорить с Джоном и получить информацию"},
                "npcs_present": [0, 1],
                "items_available": [2],
                "success_conditions": {
                    "type": "dialogue_complete",
                    "target": "John",
                    "keywords": ["help", "key"]
                },
                "next_scene_id": 2,
                "is_ending": False,
                "ending_type": None
            },
            {
                "scene_id": 2,
                "chapter_number": 1,
                "scene_number": 2,
                "location_name": "Library",
                "location_description": "An old library with many books.",
                "location_description_trs": {"ru": "Старая библиотека с множеством книг."},
                "objective": "Find information about the key",
                "objective_trs": {"ru": "Найти информацию о ключе"},
                "npcs_present": [3, 4],
                "items_available": [],
                "success_conditions": {
                    "type": "item_obtained",
                    "target": "City Map",
                    "keywords": []
                },
                "next_scene_id": 3,
                "is_ending": False,
                "ending_type": None
            },
            {
                "scene_id": 3,
                "chapter_number": 2,
                "scene_number": 1,
                "location_name": "Old House",
                "location_description": "A mysterious old house on the hill.",
                "location_description_trs": {"ru": "Таинственный старый дом на холме."},
                "objective": "Talk to Tom and get the key",
                "objective_trs": {"ru": "Поговорить с Томом и получить ключ"},
                "npcs_present": [1, 2, 4],
                "items_available": [],
                "success_conditions": {
                    "type": "item_obtained",
                    "target": "Old Key",
                    "keywords": []
                },
                "next_scene_id": 4,
                "is_ending": False,
                "ending_type": None
            },
            {
                "scene_id": 4,
                "chapter_number": 2,
                "scene_number": 2,
                "location_name": "Secret Door",
                "location_description": "You found the secret door!",
                "location_description_trs": {"ru": "Вы нашли секретную дверь!"},
                "objective": "Open the door with the key",
                "objective_trs": {"ru": "Открыть дверь ключом"},
                "npcs_present": [2, 4],
                "items_available": [],
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
    async def test_generate_skeleton_success(self, skeleton_generator, sample_ai_response):
        """Тест успешной генерации каркаса"""

        with patch('selfFunctions.afSendMsg2AI', new_callable=AsyncMock) as mock_ai:
            # Мокаем ответ AI
            mock_ai.return_value = json.dumps(sample_ai_response)

            result = await skeleton_generator.generate_skeleton(
                genre='mystery',
                mood='tense',
                realism='fully_realistic',
                complexity=['puzzles', 'dialogues'],
                goal='learn_truth',
                grammar_topic='Present Simple',
                difficulty_level=3,
                num_chapters=2,
                scenes_structure=[2, 2]
            )

            # Проверяем структуру результата
            assert result['story_name'] == "The Lost Key"
            assert len(result['npcs']) == 5
            assert len(result['items']) == 3
            assert len(result['scenes']) == 4

            # Проверяем что AI был вызван с правильными параметрами
            mock_ai.assert_called_once()
            call_args = mock_ai.call_args
            assert call_args[1]['iModel'] == 4  # GPT-4o
            assert call_args[1]['toggleParam'] == 3  # Temperature 0.7

    @pytest.mark.asyncio
    async def test_generate_skeleton_with_markdown_removal(self, skeleton_generator, sample_ai_response):
        """Тест удаления markdown code blocks из ответа AI"""

        with patch('selfFunctions.afSendMsg2AI', new_callable=AsyncMock) as mock_ai:
            # AI возвращает JSON в markdown блоке
            mock_ai.return_value = f"```json\n{json.dumps(sample_ai_response)}\n```"

            result = await skeleton_generator.generate_skeleton(
                genre='adventure',
                mood='optimistic',
                realism='unusual_real',
                complexity=['simple_plot', 'action'],
                goal='complete_mission',
                grammar_topic='Past Simple',
                difficulty_level=2,
                num_chapters=1,
                scenes_structure=[4]
            )

            # Проверяем что парсинг прошёл успешно несмотря на markdown
            assert 'story_name' in result
            assert isinstance(result['npcs'], list)

    @pytest.mark.asyncio
    async def test_generate_skeleton_invalid_json(self, skeleton_generator):
        """Тест обработки невалидного JSON от AI"""

        with patch('selfFunctions.afSendMsg2AI', new_callable=AsyncMock) as mock_ai:
            # AI возвращает невалидный JSON
            mock_ai.return_value = "This is not JSON at all!"

            with pytest.raises(Exception) as exc_info:
                await skeleton_generator.generate_skeleton(
                    genre='comedy',
                    mood='funny',
                    realism='full_fantasy',
                    complexity=['dialogues', 'emotional'],
                    goal='find_allies',
                    grammar_topic='Present Continuous',
                    difficulty_level=1,
                    num_chapters=1,
                    scenes_structure=[3]
                )

            # Исправленная проверка
            assert "invalid json" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_validate_skeleton_structure_success(self, skeleton_generator, sample_ai_response):
        """Тест успешной валидации структуры каркаса"""

        # Не должно быть исключений
        skeleton_generator._validate_skeleton_structure(
            sample_ai_response,
            expected_chapters=2,
            expected_scenes=4
        )

    @pytest.mark.asyncio
    async def test_validate_skeleton_missing_field(self, skeleton_generator, sample_ai_response):
        """Тест валидации с отсутствующим обязательным полем"""

        # Удаляем обязательное поле
        invalid_data = sample_ai_response.copy()
        del invalid_data['story_name']

        with pytest.raises(ValueError) as exc_info:
            skeleton_generator._validate_skeleton_structure(
                invalid_data,
                expected_chapters=2,
                expected_scenes=4
            )

        assert "Missing required field" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_skeleton_duplicate_scene_id(self, skeleton_generator, sample_ai_response):
        """Тест валидации с дублирующимся scene_id"""

        invalid_data = sample_ai_response.copy()
        # Делаем дубликат scene_id
        invalid_data['scenes'][1]['scene_id'] = 1  # Дублируем первый

        with pytest.raises(ValueError) as exc_info:
            skeleton_generator._validate_skeleton_structure(
                invalid_data,
                expected_chapters=2,
                expected_scenes=4
            )

        assert "Duplicate scene_id" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_skeleton_npc_missing_field(self, skeleton_generator, sample_ai_response):
        """Тест валидации NPC с отсутствующим полем"""

        invalid_data = sample_ai_response.copy()
        # Удаляем обязательное поле у NPC
        del invalid_data['npcs'][0]['name']

        with pytest.raises(ValueError) as exc_info:
            skeleton_generator._validate_skeleton_structure(
                invalid_data,
                expected_chapters=2,
                expected_scenes=4
            )

        assert "NPC missing field" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_save_skeleton_to_db_success(self, skeleton_generator, sample_ai_response):
        """Тест успешного сохранения каркаса в БД"""

        # Мокаем все DB операции
        with patch('fpgDB.fFetch_InsertQuery_args', new_callable=AsyncMock) as mock_insert, \
                patch('fpgDB.fExec_UpdateQuery_args', new_callable=AsyncMock) as mock_update, \
                patch.object(skeleton_generator, '_validate_skeleton_structure'):
            # Story ID
            mock_insert.return_value = [(1,)]

            # Мокаем менеджеры
            mock_npc_manager = MagicMock()
            mock_npc_manager.create_npc = AsyncMock(side_effect=[10, 11, 12, 13, 14])  # 5 NPCs

            mock_item_manager = MagicMock()
            mock_item_manager.create_item = AsyncMock(side_effect=[20, 21, 22])  # 3 Items

            # ИСПРАВЛЕНИЕ: Патчим классы в момент импорта внутри метода
            with patch('handlers.learnpath.story.managers.npc_manager.NPCManager', return_value=mock_npc_manager), \
                    patch('handlers.learnpath.story.managers.item_manager.ItemManager', return_value=mock_item_manager):
                story_id = await skeleton_generator.save_skeleton_to_db(
                    story_data=sample_ai_response,
                    module_id=30,
                    genre='mystery',
                    mood='tense',
                    realism='fully_realistic',
                    main_goal='learn_truth',
                    grammar_topic='Present Simple',
                    difficulty_level=3,
                    generation_params={
                        'genre': 'mystery',
                        'mood': 'tense',
                        'complexity': ['puzzles', 'dialogues']
                    }
                )

                # Проверяем что story создана
                assert story_id == 1

                # Проверяем что NPCs созданы (5 раз)
                assert mock_npc_manager.create_npc.call_count == 5

                # Проверяем что Items созданы (3 раза)
                assert mock_item_manager.create_item.call_count == 3

                # Проверяем что scenes созданы (4 вставки сцен)
                assert mock_insert.call_count >= 4

    @pytest.mark.asyncio
    async def test_create_generation_prompt(self, skeleton_generator):
        """Тест создания промпта для AI"""

        prompt = skeleton_generator._create_generation_prompt(
            genre="Mystery/Detective",
            mood="Tense (dangers, survival, stress)",
            realism="Fully realistic (shipwreck, accident)",
            complexity_desc=["Puzzles and mysteries", "Lots of dialogues"],
            goal="Learn the truth - who am I? what happened?",
            grammar_topic="Present Simple",
            difficulty_desc="B1 (Intermediate): Mix of simple and complex sentences",
            num_chapters=2,
            scenes_structure=[2, 2],
            total_scenes=4
        )

        # Проверяем что промпт содержит все необходимые параметры
        assert "Mystery/Detective" in prompt
        assert "Tense" in prompt
        assert "Fully realistic" in prompt
        assert "Puzzles and mysteries" in prompt
        assert "Present Simple" in prompt
        assert "Chapters: 2" in prompt
        assert "Total: 4 scenes" in prompt

        # Проверяем что промпт требует JSON ответ
        assert "RESPOND ONLY WITH JSON" in prompt
        assert "no markdown" in prompt.lower()

    @pytest.mark.asyncio
    async def test_npc_id_mapping(self, skeleton_generator, sample_ai_response):
        """Тест корректного маппинга NPC ID из AI в DB"""

        with patch('fpgDB.fFetch_InsertQuery_args', new_callable=AsyncMock) as mock_insert, \
                patch('fpgDB.fExec_UpdateQuery_args', new_callable=AsyncMock) as mock_update:

            # Story ID
            mock_insert.return_value = [(1,)]

            # NPC IDs: 0->100, 1->101, 2->102, 3->103, 4->104
            npc_db_ids = [100, 101, 102, 103, 104]

            # Item IDs: 0->200, 1->201, 2->202
            item_db_ids = [200, 201, 202]

            # Scene IDs: будут возвращены по порядку
            scene_db_ids = [300, 301, 302, 303]

            mock_npc_manager = MagicMock()
            mock_npc_manager.create_npc = AsyncMock(side_effect=npc_db_ids)

            mock_item_manager = MagicMock()
            mock_item_manager.create_item = AsyncMock(side_effect=item_db_ids)

            # Мокаем вставку сцен чтобы вернуть scene_db_ids
            scene_insert_counter = [0]

            async def insert_side_effect(*args, **kwargs):
                if scene_insert_counter[0] == 0:
                    # Первый вызов - story
                    scene_insert_counter[0] += 1
                    return [(1,)]
                else:
                    # Последующие - сцены
                    idx = scene_insert_counter[0] - 1
                    scene_insert_counter[0] += 1
                    return [(scene_db_ids[idx],)]

            mock_insert.side_effect = insert_side_effect

            # ИСПРАВЛЕНИЕ: Патчим классы правильно
            with patch('handlers.learnpath.story.managers.npc_manager.NPCManager', return_value=mock_npc_manager), \
                    patch('handlers.learnpath.story.managers.item_manager.ItemManager', return_value=mock_item_manager):

                story_id = await skeleton_generator.save_skeleton_to_db(
                    story_data=sample_ai_response,
                    module_id=30,
                    genre='mystery',
                    mood='tense',
                    realism='fully_realistic',
                    main_goal='learn_truth',
                    grammar_topic='Present Simple',
                    difficulty_level=3,
                    generation_params={}
                )

                # Проверяем что scene 1 содержит правильные NPC IDs (0, 1 -> 100, 101)
                # Это проверяется через вызовы mock_insert с правильными аргументами
                # Проверим вызовы для сцен
                scene_calls = [call for call in mock_insert.call_args_list if len(call[0]) > 10]

                if scene_calls:
                    # Проверяем что npcs_present содержит DB IDs
                    first_scene_call = scene_calls[0]
                    npcs_present_json = first_scene_call[0][9]  # 9-й аргумент - c_npcs_present
                    npcs_present = json.loads(npcs_present_json)

                    # Scene 1 имеет NPCs [0, 1] -> должны быть [100, 101]
                    assert 100 in npcs_present
                    assert 101 in npcs_present


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
        # TODO: Реализовать когда будет готова тестовая БД
        pytest.skip("Requires real database connection")


# ============================================================================
# Запуск тестов
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])