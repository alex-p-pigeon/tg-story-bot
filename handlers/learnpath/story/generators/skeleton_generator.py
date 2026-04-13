"""
Story Skeleton Generator - Генератор каркаса истории через AI
"""

import logging
from typing import Dict, Any, List, Optional
import json
import selfFunctions as myF
import fpgDB as pgDB

logger = logging.getLogger(__name__)


class StorySkeletonGenerator:
    """
    Генератор каркаса интерактивной истории

    ВАЖНО: История НЕ привязывается к module_id!
    Она принадлежит user_id и может продолжаться через несколько модулей.
    """

    def __init__(self, pool):
        self.pool_base, self.pool_log = pool

    async def generate_skeleton(
            self,
            user_id: int,
            genre: str,
            mood: str,
            realism: str,
            complexity: List[str],
            goal: str,
            initial_lesson_context: Dict[str, Any],  # Для первого урока
            num_chapters: int = 2,
            scenes_structure: List[int] = [2, 2]
    ) -> Dict[str, Any]:
        """
        Генерировать каркас истории через AI

        Args:
            user_id: ID пользователя (владелец истории)
            genre: Жанр (adventure, mystery, etc)
            mood: Настроение (optimistic, tense, etc)
            realism: Реалистичность (full_fantasy, fully_realistic)
            complexity: Список особенностей ([simple_plot, dialogues])
            goal: Главная цель (return_home, learn_truth, etc)
            initial_lesson_context: Контекст первого урока для AI
            num_chapters: Количество глав
            scenes_structure: Сцены в главе [2, 2] = 2 главы по 2 сцены

        Returns:
            Dict с каркасом истории:
            {
                'story_name': str,
                'description': str,
                'npcs': [...],
                'items': [...],
                'scenes': [...]
            }
        """

        logger.info(f"Generating story skeleton for user {user_id}")

        # ========================================
        # 1. Формируем промпт для AI
        # ========================================

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            genre=genre,
            mood=mood,
            realism=realism,
            complexity=complexity,
            goal=goal,
            grammar_focus=initial_lesson_context['grammar_focus'],
            cefr_level=initial_lesson_context['cefr_level'],
            num_chapters=num_chapters,
            scenes_structure=scenes_structure
        )

        # ========================================
        # 2. Вызываем AI
        # ========================================

        try:
            ai_response = await myF.afSendMsg2AI(
                user_prompt,
                self.pool_base,
                user_id,
                iModel=4,  # GPT-4o
                toggleParam=3,  # Temperature 0.7
                systemPrompt=system_prompt
            )

            # Парсим JSON ответ
            skeleton_data = self._parse_ai_response(ai_response)

            logger.info(f"Story skeleton generated: {skeleton_data['story_name']}")

            # ========================================
            # 3. Сохраняем в БД
            # ========================================

            story_id = await self._save_skeleton_to_db(
                user_id=user_id,
                skeleton_data=skeleton_data,
                generation_params={
                    'genre': genre,
                    'mood': mood,
                    'realism': realism,
                    'complexity': complexity,
                    'goal': goal,
                    'initial_grammar': initial_lesson_context['grammar_focus'],
                    'initial_cefr': initial_lesson_context['cefr_level']
                },
                initial_lesson_context=initial_lesson_context
            )

            skeleton_data['story_id'] = story_id

            return skeleton_data

        except Exception as e:
            logger.error(f"Error generating story skeleton: {e}", exc_info=True)
            raise

    def _build_system_prompt(self) -> str:
        """Системный промпт для AI"""

        return """You are an expert ESL story architect specialized in creating interactive educational stories.

Your task is to create a SKELETON (framework) for an interactive story that will be used for English language learning.

Key principles:
1. The story should be ADAPTABLE - it will continue through multiple lessons/modules
2. NPCs should have clear personalities and goals
3. Each scene should have a clear objective for the user
4. The story should naturally incorporate the target grammar
5. Difficulty should match the CEFR level

RESPOND ONLY WITH VALID JSON in the exact format specified in the user prompt.
"""

    def _build_user_prompt(
            self,
            genre: str,
            mood: str,
            realism: str,
            complexity: List[str],
            goal: str,
            grammar_focus: str,
            cefr_level: str,
            num_chapters: int,
            scenes_structure: List[int]
    ) -> str:
        """Промпт для пользователя"""

        complexity_str = ', '.join(complexity)
        total_scenes = sum(scenes_structure)

        return f"""Create an interactive story SKELETON with the following parameters:

STORY PARAMETERS:
- Genre: {genre}
- Mood: {mood}
- Realism: {realism}
- Complexity/Style: {complexity_str}
- Main Goal: {goal}

EDUCATIONAL CONTEXT:
- Grammar Focus: {grammar_focus}
- CEFR Level: {cefr_level}

STRUCTURE:
- {num_chapters} chapters
- {total_scenes} total scenes ({', '.join([str(x) for x in scenes_structure])} per chapter)

CREATE THE FOLLOWING:

1. STORY NAME AND DESCRIPTION
   - Short, engaging name
   - Brief description (2-3 sentences)

2. NPCS (5-10 characters):
   For each NPC provide:
   - name: string (international name, not Russian)
   - gender: "male" or "female"
   - age_group: "young" (18-30), "middle" (31-55), "old" (56+)
   - personality: object with "traits" (list of 2-3 traits) and "base_mood" (string)
   - role_description: string (role in the story)
   - goals: object with "primary" (string) and "secondary" (list of strings)
   - appears_in_scenes: list of scene numbers (1-indexed)

3. ITEMS (0-5 key items):
   For each item provide:
   - name: string
   - name_trs: object with "ru" translation
   - description: string
   - description_trs: object with "ru" translation
   - purpose: string (why it's needed)
   - initial_location: "npc:NAME" or "scene:NUMBER" or "inventory"
   - is_key_item: boolean

4. SCENES:
   For each scene provide:
   - chapter_number: int (1-indexed)
   - scene_number: int (1-indexed within story)
   - scene_name: string
   - location_description: string (2-3 sentences)
   - location_description_trs: object with "ru" translation
   - objective: string (what user must accomplish)
   - objective_trs: object with "ru" translation
   - npcs_present: list of NPC names
   - items_available: list of item names (if any)
   - success_conditions: object with:
     * "type": "dialogue_complete" | "item_obtained" | "item_use" | "action_performed"
     * "target": string (NPC name or item name)
     * "keywords": list of key words/phrases (optional)
   - next_scene_number: int or null (if last scene)
   - is_ending: boolean
   - ending_type: "happy" | "sad" | "open" | null

CRITICAL REQUIREMENTS:
- NO Russian names, cities, or references
- Use international names (John, Maria, Emma, David, etc.)
- Use international cities (London, Paris, New York, Tokyo, etc.)
- Grammar focus ({grammar_focus}) should be naturally integrated
- CEFR level ({cefr_level}) should match vocabulary and sentence complexity
- The story should be adaptable to continue in future lessons

RESPOND WITH JSON ONLY (no markdown, no explanations):
{{
  "story_name": "...",
  "description": "...",
  "npcs": [...],
  "items": [...],
  "scenes": [...]
}}
"""

    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """
        Парсить ответ AI и валидировать структуру
        """

        try:
            # Убираем markdown блоки если есть
            cleaned = ai_response.strip()
            if cleaned.startswith('```'):
                lines = cleaned.split('\n')
                cleaned = '\n'.join(lines[1:-1])

            skeleton = json.loads(cleaned)

            # Валидация обязательных полей
            required_fields = ['story_name', 'description', 'npcs', 'items', 'scenes']
            for field in required_fields:
                if field not in skeleton:
                    raise ValueError(f"Missing required field: {field}")

            return skeleton

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"AI response: {ai_response}")
            raise ValueError("AI returned invalid JSON")

    async def _save_skeleton_to_db(
            self,
            user_id: int,
            skeleton_data: Dict[str, Any],
            generation_params: Dict[str, Any],
            initial_lesson_context: Dict[str, Any]
    ) -> int:
        """
        Сохранить каркас истории в БД

        ВАЖНО: История привязывается к user_id, НЕ к module_id!

        Returns:
            story_id
        """

        # 1. Создаем запись в t_story_interactive_stories
        story_query = """
            INSERT INTO t_story_interactive_stories
                (c_created_by_user_id, c_story_name, c_description, c_genre, c_mood, 
                 c_realism, c_main_goal, c_grammar_context, c_difficulty_level,
                 c_total_chapters, c_total_scenes, c_estimated_minutes,
                 c_story_skeleton, c_generation_params, c_is_active)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, true)
            RETURNING c_story_id
        """

        # Определяем difficulty_level из CEFR
        cefr_to_level = {
            'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5
        }
        difficulty_level = cefr_to_level.get(
            initial_lesson_context['cefr_level'], 1
        )

        # Подсчитываем главы и сцены
        total_chapters = max([s['chapter_number'] for s in skeleton_data['scenes']])
        total_scenes = len(skeleton_data['scenes'])
        estimated_minutes = total_scenes * 5

        result = await pgDB.fFetch_InsertQuery_args(
            self.pool_base,
            story_query,
            user_id,
            skeleton_data['story_name'],
            skeleton_data['description'],
            generation_params['genre'],
            generation_params['mood'],
            generation_params['realism'],
            generation_params['goal'],
            initial_lesson_context['grammar_focus'],
            difficulty_level,
            total_chapters,
            total_scenes,
            estimated_minutes,
            json.dumps(skeleton_data),
            json.dumps(generation_params)
        )

        # Извлекаем story_id из Record
        if hasattr(result, 'get'):
            story_id = result['c_story_id']
        elif hasattr(result, '__getitem__'):
            story_id = result[0]
        else:
            story_id = int(result)

        logger.info(f"Created story in catalog (created by user {user_id}")

        # 1.5. Создаем связь пользователь-история в t_story_user_stories
        user_story_query = """
            INSERT INTO t_story_user_stories
                (c_user_id, c_story_id, c_started_at)
            VALUES ($1, $2, CURRENT_TIMESTAMP)
            ON CONFLICT (c_user_id, c_story_id) DO NOTHING
        """

        await pgDB.fExec_InsertQuery_args(
            self.pool_base,
            user_story_query,
            user_id,
            story_id
        )

        logger.info(f"Created user-story link: user {user_id} → story {story_id}")

        # 2. Создаем NPCs и получаем маппинг имён -> ID
        npc_name_to_id = await self._create_npcs(story_id, skeleton_data['npcs'])

        # 3. Создаем Items
        item_name_to_id = await self._create_items(story_id, skeleton_data['items'])

        # 4. Создаем Scenes с маппингом NPC имён -> ID
        await self._create_scenes(
            story_id,
            skeleton_data['scenes'],
            npc_name_to_id,
            item_name_to_id  # ← Передать маппинг
        )

        # 5. Создаем начальный прогресс для пользователя
        await self._create_initial_progress(
            user_id, story_id, initial_lesson_context
        )

        return story_id

    async def _create_npcs(self, story_id: int, npcs: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Создать NPCs в БД

        Returns:
            Dict с маппингом {name: npc_id}
        """

        query = """
            INSERT INTO t_story_npcs
                (c_story_id, c_name, c_gender, c_age_group, c_personality,
                 c_role_description, c_goals, c_appears_in_scenes)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING c_npc_id
        """

        npc_name_to_id = {}

        for npc in npcs:
            result = await pgDB.fFetch_InsertQuery_args(
                self.pool_base,
                query,
                story_id,
                npc['name'],
                npc['gender'],
                npc['age_group'],
                json.dumps(npc['personality']),
                npc['role_description'],
                json.dumps(npc['goals']),
                json.dumps(npc['appears_in_scenes'])
            )

            # Извлекаем npc_id из Record
            if hasattr(result, 'get'):
                npc_id = result['c_npc_id']
            elif hasattr(result, '__getitem__'):
                npc_id = result[0]
            else:
                npc_id = int(result)

            npc_name_to_id[npc['name']] = npc_id
            logger.debug(f"Created NPC '{npc['name']}' with ID {npc_id}")

        return npc_name_to_id

    async def _create_items(
            self,
            story_id: int,
            items: List[Dict[str, Any]]
    ) -> Dict[str, int]:  # ← Добавить возвращаемый тип
        """
        Создать Items в БД

        Returns:
            Dict с маппингом {name: item_id}
        """

        item_name_to_id = {}  # ← Создать маппинг

        if not items:
            return item_name_to_id  # ← Вернуть пустой dict

        query = """
            INSERT INTO t_story_items
                (c_story_id, c_name, c_name_trs, c_description, 
                 c_description_trs, c_purpose, c_initial_location, c_is_key_item)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING c_item_id  -- ← ВАЖНО: вернуть ID
        """

        for item in items:
            result = await pgDB.fFetch_InsertQuery_args(  # ← fFetch вместо fExec
                self.pool_base,
                query,
                story_id,
                item['name'],
                json.dumps(item.get('name_trs', {})),
                item['description'],
                json.dumps(item.get('description_trs', {})),
                item.get('purpose', ''),
                item.get('initial_location', 'scene:1'),
                item.get('is_key_item', False)
            )

            # Извлекаем item_id из Record
            if hasattr(result, 'get'):
                item_id = result['c_item_id']
            elif hasattr(result, '__getitem__'):
                item_id = result[0]
            else:
                item_id = int(result)

            item_name_to_id[item['name']] = item_id  # ← Сохранить маппинг
            logger.debug(f"Created item '{item['name']}' with ID {item_id}")

        return item_name_to_id  # ← Вернуть маппинг

    async def _create_scenes(
            self,
            story_id: int,
            scenes: List[Dict[str, Any]],
            npc_name_to_id: Dict[str, int],
            item_name_to_id: Dict[str, int]  # ← ДОБАВИТЬ параметр
    ):
        """
        Создать Scenes в БД

        Args:
            story_id: ID истории
            scenes: Список сцен из AI
            npc_name_to_id: Маппинг {name: npc_id}
            item_name_to_id: Маппинг {name: item_id}  ← ДОБАВИТЬ
        """

        # Проход 1: Создать все сцены без next_scene_id
        scene_ids = {}

        for scene in scenes:
            # ✅ Конвертируем имена NPC в ID
            npc_names = scene.get('npcs_present', [])
            npc_ids = [
                npc_name_to_id[name]
                for name in npc_names
                if name in npc_name_to_id
            ]

            # ✅ Конвертируем имена ITEMS в ID
            item_names = scene.get('items_available', [])
            item_ids = [
                item_name_to_id[name]
                for name in item_names
                if name in item_name_to_id
            ]

            query = """
                INSERT INTO t_story_scenes
                    (c_story_id, c_chapter_number, c_scene_number, c_scene_name,
                    c_location_description, c_location_description_trs,
                    c_objective, c_objective_trs, c_npcs_present, c_items_available,
                    c_success_conditions, c_is_ending, c_ending_type)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                RETURNING c_scene_id
            """

            result = await pgDB.fFetch_InsertQuery_args(
                self.pool_base,
                query,
                story_id,
                scene['chapter_number'],
                scene['scene_number'],
                scene['scene_name'],
                scene['location_description'],
                json.dumps(scene.get('location_description_trs', {})),
                scene['objective'],
                json.dumps(scene.get('objective_trs', {})),
                json.dumps(npc_ids),  # ✅ ID вместо имён
                json.dumps(item_ids),  # ✅ ID вместо имён (ИСПРАВЛЕНО!)
                json.dumps(scene['success_conditions']),
                scene.get('is_ending', False),
                scene.get('ending_type')
            )

            # Извлекаем scene_id из Record
            if hasattr(result, 'get'):
                scene_id = result['c_scene_id']
            elif hasattr(result, '__getitem__'):
                scene_id = result[0]
            else:
                scene_id = int(result)

            scene_ids[scene['scene_number']] = scene_id
            logger.debug(f"Created scene {scene['scene_number']} with ID {scene_id}")

        # Проход 2: Обновить next_scene_id
        for scene in scenes:
            if scene.get('next_scene_number'):
                next_id = scene_ids.get(scene['next_scene_number'])
                current_id = scene_ids.get(scene['scene_number'])

                if next_id and current_id:
                    await pgDB.fExec_UpdateQuery_args(
                        self.pool_base,
                        "UPDATE t_story_scenes SET c_next_scene_id = $1 WHERE c_scene_id = $2",
                        next_id,
                        current_id
                    )
                    logger.debug(f"Linked scene {current_id} -> {next_id}")

    async def _create_initial_progress(
            self,
            user_id: int,
            story_id: int,
            initial_lesson_context: Dict[str, Any]
    ):
        """Создать начальный прогресс для пользователя"""

        # Получаем первую сцену
        first_scene_query = """
            SELECT c_scene_id
            FROM t_story_scenes
            WHERE c_story_id = $1
            ORDER BY c_scene_number
            LIMIT 1
        """

        scene_result = await pgDB.fExec_SelectQuery_args(
            self.pool_base, first_scene_query, story_id
        )

        first_scene_id = scene_result[0][0] if scene_result else None

        # Создаем прогресс
        progress_query = """
            INSERT INTO t_story_user_progress
                (c_user_id, c_story_id, c_current_scene_id, c_actions_count,
                 c_current_lesson_id, c_current_module_context, c_inventory,
                 c_npc_states, c_is_completed)
            VALUES ($1, $2, $3, 0, $4, $5, '[]'::jsonb, '{}'::jsonb, false)
        """

        module_context = {
            'module_id': initial_lesson_context['module_id'],
            'module_name': initial_lesson_context['module_name'],
            'lesson_name': initial_lesson_context['lesson_name'],
            'cefr_level': initial_lesson_context['cefr_level'],
            'grammar_focus': initial_lesson_context['grammar_focus']
        }

        await pgDB.fExec_UpdateQuery_args(
            self.pool_base,
            progress_query,
            user_id,
            story_id,
            first_scene_id,
            initial_lesson_context['lesson_id'],
            json.dumps(module_context)
        )

        logger.info(
            f"Created initial progress for user {user_id}, "
            f"story {story_id}, scene {first_scene_id}"
        )