"""
Story Skeleton Generator V2 - Улучшенная генерация с детализацией и валидацией

Изменения:
1. Двухэтапная генерация: базовый скелет → детализация
2. Генерация c_story_elaboration, c_mystery_solution
3. Детальные objectives для каждой сцены
4. Scene context для AI
"""

import logging
from typing import Dict, Any, List, Optional
import json
import selfFunctions as myF
import fpgDB as pgDB

logger = logging.getLogger(__name__)


class StorySkeletonGeneratorV2:
    """
    Генератор каркаса интерактивной истории (версия 2)
    
    Новое:
    - Двухэтапная генерация для лучшего качества
    - Детальная проработка сюжета (elaboration)
    - Mystery solution для детективных историй
    - Детальные objectives по каждой сцене
    """

    def __init__(self, pool, user_id):
        self.pool_base, self.pool_log = pool
        self.user_id = user_id

    async def generate_skeleton(
            self,
            genre: str,
            mood: str,
            realism: str,
            complexity: List[str],
            goal: str,
            #initial_lesson_context: Dict[str, Any],
            num_chapters: int = 2,
            scenes_structure: List[int] = [2, 2],
            user_description: Optional[str] = None  # ✅ Новый параметр!
    ) -> Dict[str, Any]:
        """
        Генерировать каркас истории через AI (двухэтапный процесс)

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
            Dict с каркасом истории и детализацией
        """

        logger.info(f"Generating story skeleton V2 for user {self.user_id}")

        # ========================================
        # ЭТАП 1: Генерация базового скелета
        # ========================================
        
        basic_skeleton = await self._generate_basic_skeleton(
            genre=genre,
            mood=mood,
            realism=realism,
            complexity=complexity,
            goal=goal,
            #grammar_focus=initial_lesson_context['grammar_focus'],
            cefr_level='B1',
            num_chapters=num_chapters,
            scenes_structure=scenes_structure,
            user_description=user_description  # ✅ Передаём дальше
        )

        logger.info(f"Basic skeleton generated: {basic_skeleton['story_name']}")

        # ========================================
        # ЭТАП 2: Детализация и elaboration
        # ========================================
        
        elaboration = await self._generate_story_elaboration(
            basic_skeleton=basic_skeleton,
            genre=genre,
            goal=goal,
            #grammar_focus=initial_lesson_context['grammar_focus'],
            cefr_level='B1'     #initial_lesson_context['cefr_level']
        )

        logger.info(f"Story elaboration completed")

        # ========================================
        # ЭТАП 3: Генерация detailed objectives
        # ========================================
        
        detailed_objectives = await self._generate_detailed_objectives(
            basic_skeleton=basic_skeleton,
            elaboration=elaboration,
            cefr_level='B1'     #initial_lesson_context['cefr_level']
        )

        logger.info(f"Detailed objectives generated for {len(detailed_objectives)} scenes")

        # ✅ ЭТАП 3.5: Обогащение items из objectives
        basic_skeleton = self._enrich_items_from_objectives(
            basic_skeleton,
            detailed_objectives
        )

        # ✅ ЭТАП 3.6: Корректировка success_conditions
        basic_skeleton = self._fix_success_conditions(
            basic_skeleton,
            detailed_objectives
        )

        # ========================================
        # ЭТАП 4: Сохранение в БД
        # ========================================

        try:
            story_id = await self._save_skeleton_to_db(
                skeleton_data=basic_skeleton,
                elaboration=elaboration,
                detailed_objectives=detailed_objectives,
                generation_params={
                    'genre': genre,
                    'mood': mood,
                    'realism': realism,
                    'complexity': complexity,
                    'goal': goal,
                    #'initial_grammar': initial_lesson_context['grammar_focus'],
                    'initial_cefr': 'B1'         #initial_lesson_context['cefr_level']
                }#,
                #initial_lesson_context=initial_lesson_context
            )

            basic_skeleton['story_id'] = story_id
            basic_skeleton['elaboration'] = elaboration
            basic_skeleton['detailed_objectives'] = detailed_objectives

            logger.info(f"Story {story_id} saved to database successfully")

            return basic_skeleton

        except Exception as e:
            logger.error(f"Error saving story to database: {e}", exc_info=True)
            raise

    # ========================================
    # ЭТАП 1: Базовый скелет
    # ========================================

    async def _generate_basic_skeleton(
            self,
            genre: str,
            mood: str,
            realism: str,
            complexity: List[str],
            goal: str,
            #grammar_focus: str,
            cefr_level: str,
            num_chapters: int,
            scenes_structure: List[int],
            user_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Сгенерировать базовый скелет истории"""

        system_prompt = self._build_system_prompt_basic()
        user_prompt = self._build_user_prompt_basic(
            genre=genre,
            mood=mood,
            realism=realism,
            complexity=complexity,
            goal=goal,
            #grammar_focus=grammar_focus,
            cefr_level=cefr_level,
            num_chapters=num_chapters,
            scenes_structure=scenes_structure,
            user_description=user_description
        )

        try:
            ai_response = await myF.afSendMsg2AI(
                user_prompt,
                self.pool_base,
                self.user_id,
                iModel=4,  # GPT-4o
                toggleParam=3,  # Temperature 0.7
                systemPrompt=system_prompt
            )

            skeleton_data = self._parse_ai_response(ai_response)
            return skeleton_data

        except Exception as e:
            logger.error(f"Error generating basic skeleton: {e}", exc_info=True)
            raise

    def _build_system_prompt_basic(self) -> str:
        """Системный промпт для базового скелета"""

        return """You are an expert ESL story architect specialized in creating interactive educational stories.

Your task is to create a SKELETON (framework) for an interactive story that will be used for English language learning.

Key principles:
1. The story should be ADAPTABLE - it will continue through multiple lessons/modules
2. NPCs should have clear personalities and goals
3. Each scene should have a clear objective for the user
4. The story should naturally incorporate the target grammar
5. Difficulty should match the CEFR level
6. Create logical flow between scenes
7. If mystery genre - plan a reveal-worthy solution

CRITICAL: Ensure NPC appearances are consistent (if NPC is in scene 3, they must be introduced earlier)
CRITICAL: Items should have logical locations (don't put key item at end if needed at start)
CRITICAL: Success conditions must be ACHIEVABLE with the NPCs/items present in that scene

RESPOND ONLY WITH VALID JSON in the exact format specified in the user prompt.
"""

    def _build_user_prompt_basic(
            self,
            genre: str,
            mood: str,
            realism: str,
            complexity: List[str],
            goal: str,
            #grammar_focus: str,
            cefr_level: str,
            num_chapters: int,
            scenes_structure: List[int],
            user_description: Optional[str] = None  # ✅ Новый параметр!
    ) -> str:
        """Промпт для генерации базового скелета"""

        complexity_str = ', '.join(complexity)
        total_scenes = sum(scenes_structure)

        goal_descriptions = {
            'reach_destination': 'The user must reach a specific destination, overcoming obstacles along the way.',
            'find_lost_treasure': 'The user must find a lost item, artifact, or treasure by following clues.',
            'rescue_someone': 'The user must rescue someone who is missing or in danger.',
            'escape_danger': 'The user must escape from a dangerous situation or location.',
            'solve_crime': 'The user must solve a crime or mystery by gathering evidence and interviewing people.',
            'find_missing_person': 'The user must locate a missing person by following leads and clues.',
            'reveal_culprit': 'The user must identify and expose the person responsible for the mystery.',
            'decode_clues': 'The user must decode mysterious clues and piece together what happened.',
            'complete_routine': 'The user must successfully complete daily routine tasks within time constraints.',
            'handle_situation': 'The user must handle an important life situation (interview, appointment, meeting, etc.).',
            'achieve_personal_goal': 'The user must achieve a specific personal objective through planning and interaction.',
            'solve_problem': 'The user must solve a practical everyday problem that requires help from others.',
            'uncover_truth': 'The user must uncover a hidden truth or secret.',
        }

        goal_description = goal_descriptions.get(goal, 'The user must accomplish their objective.')
        #- Grammar Focus: {grammar_focus}
        # ✅ Секция с пользовательским описанием
        user_description_section = ""
        if user_description:
            user_description_section = f"""
USER'S STORY DESCRIPTION:
The user provided this story description:
"{user_description}"

⚠️ IMPORTANT:
- Use this description as PRIMARY INSPIRATION for the story
- Build setting, characters, objectives, and plot around this description
- The selected goal ({goal}) should guide how you structure the story
- Combine the user's description with the goal to create a cohesive narrative
            """

        '''
        EDUCATIONAL CONTEXT:
        - CEFR Level: {cefr_level}
        '''
        return f"""Create an interactive story SKELETON with the following parameters:

{user_description_section}

STORY PARAMETERS:
- Genre: {genre}
- Mood: {mood}
- Realism: {realism}
- Complexity/Style: {complexity_str}
- Main Goal: {goal}
  → {goal_description}

EDUCATIONAL CONTEXT:
- CEFR Level: {cefr_level}

STRUCTURE:
- {num_chapters} chapters
- {total_scenes} total scenes ({', '.join([str(x) for x in scenes_structure])} per chapter)

CRITICAL STORY STRUCTURE:
⚠️ The USER is the MAIN CHARACTER (first-person/second-person perspective)
⚠️ The user is an English learner exploring the story world
⚠️ NPCs are OTHER CHARACTERS that the user interacts with
⚠️ DO NOT create an NPC as the main protagonist
⚠️ Location descriptions must use "You" (second person): "You arrive on the island..."
⚠️ Objectives must use "You" or imperative: "Find the map", "Talk to the locals"

CREATE THE FOLLOWING:

1. STORY NAME AND DESCRIPTION
- Short, engaging name (e.g., "The Island of Secrets")
- Brief description (2-3 sentences) using second person
- GOOD examples: "Explore a mysterious island and uncover its secrets. Can you solve the puzzles?"
- BAD examples: "Join Emma on her adventure..." (third person - wrong!)

2. NPCS (2-6 characters):
⚠️ IMPORTANT: These are NPCs that the USER will interact with, NOT the main character!
⚠️ DO NOT create NPCs with protagonist names like "Emma", "Hero", "Player", "Protagonist"
⚠️ Create supporting characters: guides, locals, researchers, mysterious strangers, etc.

For each NPC provide:
- name: string (international name, not Russian, not protagonist names)
- gender: "male" or "female"
- age_group: "young" (18-30), "middle" (31-55), "old" (56+)
- personality: object with "traits" (list of 2-3 traits) and "base_mood" (string)
- role_description: string (their role - e.g., "A local guide", "A mysterious researcher")
- goals: object with "primary" (string) and "secondary" (list of strings)
- appears_in_scenes: list of scene numbers (1-indexed)

GOOD NPC examples:
- "Lucas" - A local islander who knows the secrets
- "Dr. Martinez" - A researcher studying the island
- "Old Thomas" - The lighthouse keeper

BAD NPC examples (DO NOT CREATE):
- "Hero" - meta name
- "The Traveler" - too generic for main character

3. ITEMS (0-5 key items):
For each item provide:
- name: string
- name_trs: object with "ru" translation
- description: string
- description_trs: object with "ru" translation
- purpose: string (why it's needed)
- initial_location: "npc:NAME" or "scene:NUMBER" or "inventory"
- is_key_item: boolean

- location_details: object with:
    * location_description: string (where item is physically located)
    * location_description_trs: object with "ru" translation
    * search_keywords: list of strings (words to find item)
    * visible_on_look_around: boolean (true if shown in "Look around", false if needs search)

- acquisition_conditions: object with:
    * type: "search" | "container" | "npc_gives" | "automatic"
    * requirements: object with:
        - action: string (e.g. "search", "open")
        - keywords: list of strings (acceptable user actions)
        - required_item: string or null (item needed to acquire)
        - min_interactions: int (default 0)

4. SCENES:
For each scene provide:
- chapter_number: int (1-indexed)
- scene_number: int (1-indexed within story)
- scene_name: string
- location_description: string (2-3 sentences in SECOND PERSON)
    * GOOD: "You arrive on a mysterious island surrounded by dense jungle."
    * GOOD: "The ancient library stretches before you, filled with dusty books."
    * BAD: "Emma arrives on the island..." (third person - wrong!)
    * BAD: "The hero finds a library..." (should be "You find...")
- location_description_trs: object with "ru" translation (also in second person)
- objective: string (what USER must accomplish, use "you" or imperative)
    * GOOD: "Meet the locals and gather information"
    * GOOD: "Find the hidden map"
    * GOOD: "Talk to the researcher about their findings"
    * BAD: "Help Emma find the map" (third person)
- objective_trs: object with "ru" translation
- npcs_present: list of NPC names (companions, locals, etc. - NOT the main character!)
- items_available: list of item names (if any)
- success_conditions: object with:
    * "type": "objectives_complete"
    * "target": string (main NPC name to interact with)
    * "min_objectives": int (minimum objectives to complete)
    * "min_messages_with_target": int (minimum messages with main NPC)
- next_scene_number: int or null (if last scene)
- is_ending: boolean
- ending_type: "happy" | "sad" | "open" | null

CRITICAL REQUIREMENTS:
- NO Russian names, cities, or references
- Use international names (John, Maria, David, Sofia, etc.) - but NOT protagonist names
- Use international cities (London, Paris, New York, Tokyo, etc.)
- CEFR level ({cefr_level}) should match vocabulary and sentence complexity
- The story should be adaptable to continue in future lessons
- NPCs should appear logically (introduce before they become important)
- Items should be accessible BEFORE they are needed
- Success conditions should use "objectives_complete" type
- ALL location descriptions and objectives MUST use second person ("You...")

RESPOND WITH JSON ONLY (no markdown, no explanations):
{{
    "story_name": "...",
    "description": "...",
    "npcs": [...],
    "items": [...],
    "scenes": [...]
}}
        """

    # ========================================
    # ЭТАП 2: Elaboration (детализация)
    # ========================================

    async def _generate_story_elaboration(
            self,
            basic_skeleton: Dict[str, Any],
            genre: str,
            goal: str,
            #grammar_focus: str,
            cefr_level: str
    ) -> Dict[str, Any]:
        """
        Сгенерировать детализацию истории
        
        Returns:
            {
                'npc_knowledge': {...},
                'scene_connections': {...},
                'key_plot_points': [...],
                'mystery_solution': {...}  # если mystery жанр
            }
        """

        system_prompt = """You are a story consistency expert. Your task is to create detailed elaboration 
that ensures the story flows logically and NPCs behave consistently."""

        # Специальный промпт для mystery жанра
        mystery_section = ""
        if genre in ['mystery', 'detective']:
            mystery_section = """
4. MYSTERY_SOLUTION (CRITICAL for mystery genre):
   - mystery: string (what is the mystery?)
   - solution: string (what is the answer?)
   - final_message: string (revelation message for user)
   - revelation_scene: int (which scene reveals it)
   
   Example:
   {
     "mystery": "Who stole the ancient artifact?",
     "solution": "The museum curator was the thief - they needed money for debts",
     "final_message": "As you piece together the clues, you realize the curator had access and motive...",
     "revelation_scene": 4
   }
"""

        #- Grammar: {grammar_focus}
        #- Keep grammar focus ({grammar_focus}) integrated naturally

        user_prompt = f"""Based on this story skeleton, create detailed ELABORATION:

        STORY SKELETON:
        {json.dumps(basic_skeleton, indent=2, ensure_ascii=False)}

        PARAMETERS:
        - Genre: {genre}
        - Goal: {goal}
        - Level: {cefr_level}

        ⚠️ IMPORTANT: The USER is the main character (not an NPC)
        ⚠️ All NPC knowledge should be about what THEY know to share with the USER

        CREATE:

        1. NPC_KNOWLEDGE: What each NPC knows and can share with the USER
           For EACH NPC in the story, specify:
           - knows_about: list of what they know (facts, locations, secrets)
           - hints_to_give: list of hints they can provide to the USER
           - key_info_to_share: string (the most important info for the USER)

           Example:
           {{
             "Lucas": {{
               "knows_about": ["island history", "hidden paths", "ancient secrets"],
               "hints_to_give": ["You should explore the northern beach", "The old lighthouse holds secrets"],
               "key_info_to_share": "The island has been hiding a treasure for centuries. Only those who seek truly will find it."
             }},
             "Dr. Martinez": {{
               "knows_about": ["research findings", "island legends", "scientific data"],
               "hints_to_give": ["The data supports the legends", "You need to check the research camp"],
               "key_info_to_share": "My research proves the legends are based on real events."
             }}
           }}

        2. SCENE_CONNECTIONS: How scenes flow together
           Describe progression from the USER's perspective:

           Example:
           {{
             "1": "You arrive and meet Lucas → he tells you about the hidden paths",
             "2": "You find the old library → discover ancient records",
             "3": "You visit the research camp → Dr. Martinez shares findings",
             "4": "You piece together clues → uncover the truth"
           }}

        3. KEY_PLOT_POINTS: Critical story beats from USER perspective (ordered list)
           Example:
           [
             "You arrive on the island and meet Lucas",
             "Lucas gives you a map to hidden locations",
             "You discover the ancient library",
             "You find the Old Journal with crucial information",
             "You gather data from researchers",
             "You solve the mystery and learn the truth"
           ]

        {mystery_section if genre in ['mystery', 'detective'] else ''}

        IMPORTANT:
        - All descriptions should be from USER's perspective ("You...", not "Emma...")
        - NPCs are helpers/informants for the USER
        - Ensure logical progression for the USER's journey
        - Match CEFR level ({cefr_level})

        RESPOND WITH JSON ONLY:
        {{
          "npc_knowledge": {{}},
          "scene_connections": {{}},
          "key_plot_points": [],
          "mystery_solution": {{}} or null
        }}
        """

        try:
            ai_response = await myF.afSendMsg2AI(
                user_prompt,
                self.pool_base,
                self.user_id,
                iModel=4,
                toggleParam=3,
                systemPrompt=system_prompt
            )

            elaboration = self._parse_ai_response(ai_response)
            
            # Если не mystery, убираем mystery_solution
            if genre not in ['mystery', 'detective']:
                elaboration['mystery_solution'] = None
                
            return elaboration

        except Exception as e:
            logger.error(f"Error generating elaboration: {e}", exc_info=True)
            # Возвращаем базовую структуру при ошибке
            return {
                'npc_knowledge': {},
                'scene_connections': {},
                'key_plot_points': [],
                'mystery_solution': None
            }

    # ========================================
    # ЭТАП 3: Detailed Objectives
    # ========================================

    async def _generate_detailed_objectives(
            self,
            basic_skeleton: Dict[str, Any],
            elaboration: Dict[str, Any],
            cefr_level: str
    ) -> Dict[int, Dict[str, Any]]:
        """
        Сгенерировать детальные objectives для каждой сцены
        
        Returns:
            {
                1: {  # scene_number
                    'objectives': [...],
                    'scene_context': {...}
                },
                2: {...}
            }
        """

        system_prompt = """You are an expert educational game designer specializing in ESL interactive stories.

        YOUR ROLE:
        - Create clear, achievable learning objectives for language learners
        - Design objectives that guide students through meaningful interactions
        - Ensure every objective has a clear purpose and measurable outcome

        YOUR TASK:
        Generate detailed objectives and scene context for an interactive story scene.

        CRITICAL PRINCIPLES:
        1. Objectives must be SPECIFIC and ACTIONABLE (not generic "talk to X")
        2. Information objectives need RICH keywords (5-7 words minimum)
        3. Keywords must match NATURAL student question phrasing
        4. Scene context must provide clear guidance for AI dialogue generation
        5. Every objective must be achievable with the NPCs/items present in the scene

        QUALITY STANDARDS:
        ✅ GOOD objective: "Ask Lenny about his weekend plans"
        ❌ BAD objective: "Talk to Lenny"

        ✅ GOOD keywords: ["plans", "weekend", "Saturday", "doing", "activities", "free time"]
        ❌ BAD keywords: ["plans", "information"]

        RESPOND ONLY with valid JSON in the exact format specified."""

        detailed_objectives_all = {}

        # Генерируем objectives для каждой сцены отдельно
        for scene in basic_skeleton['scenes']:
            scene_num = scene['scene_number']

            user_prompt = f"""Create DETAILED OBJECTIVES and SCENE CONTEXT for this scene:

            ═══════════════════════════════════════════════════════════════════════════════
            SCENE INFORMATION
            ═══════════════════════════════════════════════════════════════════════════════

            Scene #{scene_num}: {scene['scene_name']}
            Location: {scene['location_description']}
            Main Objective: {scene['objective']}

            NPCs present: {', '.join(scene['npcs_present']) if scene['npcs_present'] else 'None'}
            Items available: {', '.join(scene.get('items_available', [])) if scene.get('items_available', []) else 'None'}

            ═══════════════════════════════════════════════════════════════════════════════
            STORY CONTEXT (for understanding scene flow)
            ═══════════════════════════════════════════════════════════════════════════════

            Scene connections:
            {json.dumps(elaboration.get('scene_connections', {}), indent=2, ensure_ascii=False)}

            NPC knowledge available:
            {json.dumps(elaboration.get('npc_knowledge', {}), indent=2, ensure_ascii=False)}

            ═══════════════════════════════════════════════════════════════════════════════
            YOUR TASK: Generate TWO sections
            ═══════════════════════════════════════════════════════════════════════════════

            SECTION 1: OBJECTIVES
            SECTION 2: SCENE_CONTEXT

            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            SECTION 1: OBJECTIVES (3-5 specific sub-objectives)
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            Each objective must have:
            - id: "obj_1", "obj_2", etc
            - type: one of the types below
            - description: SPECIFIC action with verb + details
            - description_trs: {{"ru": "Russian translation"}}
            - Additional fields depending on type

            ───────────────────────────────────────────────────────────────────────────────
            OBJECTIVE TYPES AND REQUIREMENTS
            ───────────────────────────────────────────────────────────────────────────────

            TYPE 1: "dialogue" - Simple requirement to talk to an NPC
            ───────────────────────────────────────────────────────────────────────────────
            Purpose: User needs to START a conversation with specific NPC
            Required fields: target (NPC name)

            Example:
            {{
              "id": "obj_1",
              "type": "dialogue",
              "description": "Talk to Mia",
              "description_trs": {{"ru": "Поговорите с Мией"}},
              "target": "Mia"
            }}

            ───────────────────────────────────────────────────────────────────────────────
            TYPE 2: "information" - Learning specific information through dialogue
            ───────────────────────────────────────────────────────────────────────────────
            Purpose: User needs to ASK SPECIFIC QUESTIONS to obtain information
            Required fields: target (NPC name), keywords (5-7 specific words)
            Optional fields: reveals_item (if asking reveals hidden item location)

            ⚠️ CRITICAL DESCRIPTION RULES:
            Use VERBS + SPECIFICS, not generic phrases!

            ❌ BAD descriptions (too generic):
            - "Talk to Lenny" (no specific goal)
            - "Get information from Dave" (what information?)
            - "Learn about the island" (too vague)
            - "Ask about plans" (ask WHO?)

            ✅ GOOD descriptions (specific action):
            - "Ask Lenny about his weekend plans"
            - "Ask Dave where the strange customer went"
            - "Find out what Mom saw on TV about the outbreak"
            - "Ask the clerk where to find milk in the store"

            Structure: "Ask [NPC name] about/where/what [specific topic/question]"
                      "Find out [specific info] from [NPC name]"

            ⚠️ CRITICAL KEYWORD RULES:
            Keywords must match NATURAL question phrasing that students will use.
            Think: "What exact WORDS would a student SAY when asking this question?"

            Include:
            1. Main topic nouns (plans, customer, milk, TV)
            2. Action verbs (saw, went, doing, find)
            3. Variations (weekend/Saturday, TV/television, where/location)
            4. Question words (where, what, when, who)
            5. Context words (strange, outbreak, store)

            Minimum: 5 keywords
            Optimal: 7 keywords

            ❌ BAD keywords examples:
            - ["plans"] → Too few (only 1)
            - ["information", "question", "ask"] → Too generic
            - ["weekend"] → Missing variations
            - ["customer", "person"] → Too vague, missing context

            ✅ GOOD keywords examples:

            For "Ask Lenny about his weekend plans":
            ["plans", "weekend", "Saturday", "Sunday", "doing", "activities", "free time"]
            Why good: Has variations (weekend/Saturday), verbs (doing), context (activities)

            For "Ask Dave where the strange customer went":
            ["strange", "customer", "woman", "went", "where", "direction", "left", "saw"]
            Why good: Descriptive (strange), question words (where), verbs (went, left, saw)

            For "Find out what Mom saw on TV about the outbreak":
            ["TV", "television", "saw", "news", "broadcast", "watched", "show", "outbreak", "program"]
            Why good: Has variations (TV/television), verbs (saw/watched), topic (outbreak)

            For "Ask the clerk where to find milk":
            ["milk", "where", "find", "dairy", "section", "aisle", "location"]
            Why good: Item (milk), question words (where), location words (section/aisle)

            ⭐ REVEALS_ITEM feature (optional):
            If asking about an item reveals its location, add reveals_item field.
            This makes the item discoverable after the dialogue completes.

            When to use reveals_item:
            - Shopping scenarios: "Ask clerk where milk is" → reveals_item: "milk"
            - Quest scenarios: "Ask guard about the key" → reveals_item: "old key"
            - Exploration: "Ask researcher about artifacts" → reveals_item: "ancient tablet"

            Example with reveals_item:
            {{
              "id": "obj_2",
              "type": "information",
              "description": "Ask the clerk where to find milk",
              "description_trs": {{"ru": "Спросите продавца где найти молоко"}},
              "target": "Clerk",
              "keywords": ["milk", "where", "find", "dairy", "section", "aisle", "location"],
              "reveals_item": "milk"
            }}

            Pattern: Ask NPC about item → reveals_item → then user can search/collect it

            Example without reveals_item (pure information):
            {{
              "id": "obj_1",
              "type": "information",
              "description": "Ask Lenny about his weekend plans",
              "description_trs": {{"ru": "Спросите Ленни о его планах на выходные"}},
              "target": "Lenny",
              "keywords": ["plans", "weekend", "Saturday", "Sunday", "doing", "activities", "free time"]
            }}

            ───────────────────────────────────────────────────────────────────────────────
            TYPE 3: "item" - Obtaining or finding a physical item
            ───────────────────────────────────────────────────────────────────────────────
            Purpose: User needs to FIND and PICK UP a physical object
            Required fields: target (item name - must match item in scene's items_available!)

            ⚠️ CRITICAL RULE:
            For EVERY item in scene's items_available list, you MUST create an "item" objective!

            If scene has items_available: ["Tom's homework", "Lisa's backpack"]
            You MUST create:
            {{
              "id": "obj_1",
              "type": "item",
              "target": "Tom's homework",
              "description": "Find Tom's homework",
              "description_trs": {{"ru": "Найдите домашнюю работу Тома"}}
            }},
            {{
              "id": "obj_2",
              "type": "item",
              "target": "Lisa's backpack",
              "description": "Find Lisa's backpack",
              "description_trs": {{"ru": "Найдите рюкзак Лизы"}}
            }}

            Examples:
            - "Get the Ancient Map"
            - "Find car keys on the desk"
            - "Pick up the flashlight"
            - "Collect the research notes"

            ⚠️ DO NOT use "information" type for physical items!
            "Find milk" → type: "item", not "information"

            ───────────────────────────────────────────────────────────────────────────────
            TYPE 4: "action" - Physical actions ONLY
            ───────────────────────────────────────────────────────────────────────────────
            Purpose: User needs to perform a PHYSICAL ACTION (not dialogue, not item-related)

            Examples:
            - "Look around the room"
            - "Search the chest"
            - "Open the locked door"
            - "Examine the strange markings"

            ⚠️ DO NOT use "action" for:
            - Talking to NPCs → use "information"
            - Finding items → use "item"
            - Learning through dialogue → use "information"

            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            SECTION 2: SCENE_CONTEXT (for AI dialogue generation)
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            Provide rich context to guide AI during runtime dialogue generation:

            Required fields:
            - atmosphere: string (mood/feeling of the scene)
            - what_happened_before: string (summary of previous events)
            - current_situation: string (what's happening right now)
            - what_should_happen: string (DETAILED sequence of expected NPC behavior)
            - important_reveals: array of strings (key information to reveal during scene)

            Optional fields:
            - npc_behavior_overrides: object (special behavior for specific NPCs)

            ───────────────────────────────────────────────────────────────────────────────
            ATMOSPHERE examples:
            ───────────────────────────────────────────────────────────────────────────────
            - "mysterious and tense"
            - "professional and efficient"
            - "casual and friendly"
            - "urgent and chaotic"
            - "suspenseful with growing danger"

            ───────────────────────────────────────────────────────────────────────────────
            WHAT_SHOULD_HAPPEN - CRITICAL for realistic scenarios:
            ───────────────────────────────────────────────────────────────────────────────
            Describe step-by-step what NPCs should do naturally in this situation.

            For procedural scenarios (airport, store, office):
            Break down the exact sequence of NPC actions.

            Example - Immigration control:
            "Officer Martinez should: 1) Greet you professionally, 2) Ask to see your passport, 
            3) Check your visa stamp, 4) Ask about purpose and duration of visit, 5) Ask about 
            accommodation, 6) Stamp your passport, 7) Welcome you and direct to baggage claim"

            Example - Grocery store checkout:
            "Cashier should: 1) Greet you, 2) Scan each item, 3) Tell you the total, 
            4) Process your payment, 5) Give you the receipt, 6) Thank you and wish good day"

            Example - Restaurant:
            "Waiter should: 1) Greet and seat you, 2) Offer menu, 3) Take drink order, 
            4) Return with drinks, 5) Take food order, 6) Check on you during meal, 7) Bring bill"

            For story scenarios:
            Describe the emotional progression and key revelations.

            Example - Mystery scene:
            "Detective should start skeptical, then notice inconsistencies in your story, 
            press harder with questions, finally reveal they know about the missing artifact"

            ───────────────────────────────────────────────────────────────────────────────
            EXAMPLES OF COMPLETE SCENE_CONTEXT:
            ───────────────────────────────────────────────────────────────────────────────

            Example 1 - Airport immigration:
            {{
              "atmosphere": "professional and efficient",
              "what_happened_before": "You just landed at the international airport after a long flight",
              "current_situation": "You are standing at immigration control desk with Officer Martinez",
              "what_should_happen": "Officer Martinez should greet you professionally, ask to see your passport, verify your visa, ask standard questions about purpose and duration of visit, ask where you're staying, then stamp your passport and allow you to proceed to baggage claim",
              "important_reveals": [
                "Immigration is required for all international arrivals",
                "You need passport and valid visa",
                "Officer will ask about accommodation and visit purpose"
              ]
            }}

            Example 2 - Grocery store:
            {{
              "atmosphere": "busy and practical",
              "what_happened_before": "You've selected items from the shelves and are ready to pay",
              "current_situation": "You're at the checkout counter with Cashier Anna",
              "what_should_happen": "Anna should greet you, scan each item one by one, tell you the total price, ask how you want to pay, process the payment, give you the receipt, and thank you",
              "important_reveals": [
                "Payment happens at checkout counter",
                "Cashier scans items to calculate total",
                "You can pay with cash or card"
              ]
            }}

            Example 3 - Mystery investigation:
            {{
              "atmosphere": "tense and suspenseful",
              "what_happened_before": "You discovered clues pointing to the museum curator's involvement",
              "current_situation": "Confronting the curator in their office with evidence",
              "what_should_happen": "Curator should initially deny everything, then become defensive when you present evidence, try to justify their actions citing financial desperation, finally break down and confess to stealing the artifact to pay off debts",
              "important_reveals": [
                "Curator had exclusive access to the artifact",
                "They were deeply in debt",
                "The theft was motivated by financial desperation, not greed"
              ],
              "npc_behavior_overrides": {{
                "Curator": {{
                  "emotional_arc": "Defensive → Desperate → Defeated → Confesses",
                  "key_dialogue": "Initially: 'I don't know what you're talking about.' Then: 'You don't understand, I had no choice!' Finally: 'I needed the money... I was desperate...'"
                }}
              }}
            }}

            ═══════════════════════════════════════════════════════════════════════════════
            VALIDATION CHECKLIST
            ═══════════════════════════════════════════════════════════════════════════════

            Before submitting, verify:

            FOR OBJECTIVES:
            ✅ Every description is SPECIFIC (has verb + details, not generic)
            ✅ Every "information" objective has 5-7 keywords
            ✅ Keywords match natural student question phrasing
            ✅ Every item in items_available has an "item" objective
            ✅ Objectives are achievable with NPCs/items present in this scene
            ✅ Descriptions match CEFR {cefr_level} level

            FOR SCENE_CONTEXT:
            ✅ "what_should_happen" has step-by-step NPC actions
            ✅ "important_reveals" lists key information for this scene
            ✅ "atmosphere" sets appropriate mood
            ✅ All context helps AI generate realistic, educational dialogue

            ═══════════════════════════════════════════════════════════════════════════════
            RESPONSE FORMAT
            ═══════════════════════════════════════════════════════════════════════════════

            Respond with VALID JSON ONLY (no markdown, no explanations):

            {{
              "objectives": [
                {{
                  "id": "obj_1",
                  "type": "information",
                  "description": "Ask Lenny about his weekend plans",
                  "description_trs": {{"ru": "Спросите Ленни о его планах на выходные"}},
                  "target": "Lenny",
                  "keywords": ["plans", "weekend", "Saturday", "Sunday", "doing", "activities", "free time"]
                }},
                {{
                  "id": "obj_2",
                  "type": "item",
                  "target": "car keys",
                  "description": "Find car keys on the messy desk",
                  "description_trs": {{"ru": "Найдите ключи от машины на грязном столе"}}
                }}
              ],
              "scene_context": {{
                "atmosphere": "casual and friendly",
                "what_happened_before": "You just woke up on Saturday morning",
                "current_situation": "You're talking with Lenny about weekend plans",
                "what_should_happen": "Lenny should share his plans, ask about yours, suggest activities together",
                "important_reveals": [
                  "Lenny wants to go hiking this weekend",
                  "There's a new trail he wants to try"
                ]
              }}
            }}
            """

            try:
                ai_response = await myF.afSendMsg2AI(
                    user_prompt,
                    self.pool_base,
                    self.user_id,
                    iModel=4,
                    toggleParam=3,
                    systemPrompt=system_prompt
                )

                scene_objectives = self._parse_ai_response(ai_response)
                detailed_objectives_all[scene_num] = scene_objectives

                logger.debug(f"Generated objectives for scene {scene_num}")

            except Exception as e:
                logger.error(f"Error generating objectives for scene {scene_num}: {e}")
                # Fallback к простым objectives
                detailed_objectives_all[scene_num] = {
                    'objectives': [],
                    'scene_context': {
                        'atmosphere': scene.get('location_description', ''),
                        'current_situation': scene.get('objective', ''),
                        'what_should_happen': f"Complete: {scene.get('objective', '')}",
                        'important_reveals': []
                    }
                }

        return detailed_objectives_all

    def _enrich_items_from_objectives(
            self,
            skeleton_data: Dict[str, Any],
            detailed_objectives: Dict[int, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Автоматически создать items для всех objectives типа "item"

        Извлекаем все item objectives, создаем недостающие items,
        добавляем их в соответствующие сцены.
        """

        # 1. Получить существующие item names
        existing_item_names = {item['name'].lower() for item in skeleton_data.get('items', [])}

        # 2. Найти все item objectives
        items_to_create = {}

        for scene_num, objectives_data in detailed_objectives.items():
            objectives = objectives_data.get('objectives', [])

            for obj in objectives:
                if obj.get('type') == 'item':
                    item_name = obj.get('target', '').strip()

                    if item_name.lower() not in existing_item_names:
                        # Нужно создать этот item!
                        if scene_num not in items_to_create:
                            items_to_create[scene_num] = []

                        items_to_create[scene_num].append({
                            'name': item_name,
                            'description': obj.get('description', f'A {item_name}'),
                            'scene_num': scene_num
                        })

        # 3. Создать недостающие items
        for scene_num, items_list in items_to_create.items():
            for item_data in items_list:
                new_item = {
                    'name': item_data['name'],
                    'description': item_data['description'],
                    'initial_location': f'scene:{scene_num}',
                    'is_key_item': False,
                    'location_details': {
                        'visible_on_look_around': False,
                        'location_description': f'You can find {item_data["name"]} here'
                    },
                    'acquisition_conditions': {
                        'type': 'search',
                        'requirements': {
                            'keywords': ['search', 'look', 'find']
                        }
                    }
                }

                # Добавить в список items
                skeleton_data['items'].append(new_item)

                # Добавить в items_available сцены
                for scene in skeleton_data['scenes']:
                    if scene['scene_number'] == scene_num:
                        scene['items_available'].append(item_data['name'])
                        break

        skeleton_data = self._configure_item_visibility(skeleton_data, detailed_objectives)

        return skeleton_data

    def _fix_success_conditions(
            self,
            skeleton_data: Dict[str, Any],
            detailed_objectives: Dict[int, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Исправить min_objectives и min_messages_with_target в success_conditions

        Args:
            skeleton_data: Базовый скелет истории с scenes
            detailed_objectives: Словарь {scene_number: {objectives: [...]}}

        Returns:
            Исправленный skeleton_data
        """

        for scene in skeleton_data.get('scenes', []):
            scene_num = scene['scene_number']
            success_conditions = scene.get('success_conditions', {})

            # Проверяем тип условия
            if success_conditions.get('type') == 'objectives_complete':

                # 1. Пересчитать min_objectives
                scene_objectives = detailed_objectives.get(scene_num, {})
                objectives_list = scene_objectives.get('objectives', [])

                if objectives_list:
                    # min_objectives = общее количество objectives
                    success_conditions['min_objectives'] = len(objectives_list)

                    logger.info(
                        f"Scene {scene_num}: Set min_objectives = {len(objectives_list)} "
                        f"(was {success_conditions.get('min_objectives')})"
                    )

                # 2. Установить min_messages_with_target = 20
                success_conditions['min_messages_with_target'] = 20

                logger.info(
                    f"Scene {scene_num}: Set min_messages_with_target = 20 "
                    f"(was {success_conditions.get('min_messages_with_target')})"
                )

                # Обновить в сцене
                scene['success_conditions'] = success_conditions

        return skeleton_data

    # ========================================
    # Сохранение в БД
    # ========================================

    async def _save_skeleton_to_db(
            self,
            skeleton_data: Dict[str, Any],
            elaboration: Dict[str, Any],
            detailed_objectives: Dict[int, Dict[str, Any]],
            generation_params: Dict[str, Any]#,
            #initial_lesson_context: Dict[str, Any]
    ) -> int:
        """
        Сохранить каркас истории в БД с детализацией

        Returns:
            story_id
        """

        # Определяем difficulty_level из CEFR
        #cefr_to_level = {
        #    'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5
        #}
        difficulty_level = 3    #cefr_to_level.get('B1', 1)   #initial_lesson_context['cefr_level']

        # Подсчитываем главы и сцены
        total_chapters = max([s['chapter_number'] for s in skeleton_data['scenes']])
        total_scenes = len(skeleton_data['scenes'])
        estimated_minutes = total_scenes * 5

        # 1. Создаем запись в t_story_interactive_stories
        story_query = """
            INSERT INTO t_story_interactive_stories
                (c_created_by_user_id, c_story_name, c_description, c_genre, c_mood, 
                 c_realism, c_main_goal, c_grammar_context, c_difficulty_level,
                 c_total_chapters, c_total_scenes, c_estimated_minutes,
                 c_story_skeleton, c_generation_params, c_story_elaboration, 
                 c_mystery_solution, c_is_active)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, true)
            RETURNING c_story_id
        """

        result = await pgDB.fFetch_InsertQuery_args(
            self.pool_base,
            story_query,
            self.user_id,
            skeleton_data['story_name'],
            skeleton_data['description'],
            generation_params['genre'],
            generation_params['mood'],
            generation_params['realism'],
            generation_params['goal'],
            '',   #initial_lesson_context['grammar_focus']
            difficulty_level,
            total_chapters,
            total_scenes,
            estimated_minutes,
            json.dumps(skeleton_data, ensure_ascii=False),
            json.dumps(generation_params, ensure_ascii=False),
            json.dumps(elaboration, ensure_ascii=False),  # NEW!
            json.dumps(elaboration.get('mystery_solution'), ensure_ascii=False) if elaboration.get('mystery_solution') else None  # NEW!
        )

        # Извлекаем story_id
        if hasattr(result, 'get'):
            story_id = result['c_story_id']
        elif hasattr(result, '__getitem__'):
            story_id = result[0]
        else:
            story_id = int(result)

        logger.info(f"Created story {story_id} in catalog (user {self.user_id})")

        # 1.5. Создаем связь пользователь-история
        user_story_query = """
            INSERT INTO t_story_user_stories
                (c_user_id, c_story_id, c_started_at)
            VALUES ($1, $2, CURRENT_TIMESTAMP)
            ON CONFLICT (c_user_id, c_story_id) DO NOTHING
        """

        await pgDB.fExec_UpdateQuery_args(
            self.pool_base,
            user_story_query,
            self.user_id,
            story_id
        )

        # 2. Создаем NPCs
        npc_name_to_id = await self._create_npcs(story_id, skeleton_data['npcs'])

        # 3. Создаем Items
        item_name_to_id = await self._create_items(story_id, skeleton_data['items'])

        # 4. Создаем Scenes с detailed objectives
        await self._create_scenes(
            story_id,
            skeleton_data['scenes'],
            npc_name_to_id,
            item_name_to_id,
            detailed_objectives  # NEW!
        )



        return story_id

    async def _create_npcs(self, story_id: int, npcs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Создать NPCs в БД"""

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
                json.dumps(npc['personality'], ensure_ascii=False),
                npc['role_description'],
                json.dumps(npc['goals'], ensure_ascii=False),
                json.dumps(npc['appears_in_scenes'])
            )

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
    ) -> Dict[str, int]:
        """Создать Items в БД"""

        item_name_to_id = {}

        if not items:
            return item_name_to_id

        query = """
            INSERT INTO t_story_items
                (c_story_id, c_name, c_name_trs, c_description, 
                    c_description_trs, c_purpose, c_initial_location, c_is_key_item,
                    c_location_type, c_location_details, c_acquisition_conditions)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING c_item_id
        """

        for item in items:
            initial_location = item.get('initial_location', 'scene:1')


            '''
            # ✅ Определяем location_type
            location_details = item.get('location_details', {})
            visible = location_details.get('visible_on_look_around', True)
            location_type = 'visible' if visible else 'hidden'
            '''

            if initial_location == 'inventory':
                location_type = 'inventory'
                # ✅ Переопределить location_details для inventory items
                location_details = {
                    "search_keywords": [],
                    "location_description": "In your inventory",
                    "visible_on_look_around": False,  # ← НЕ показывать в Look Around
                    "location_description_trs": {"ru": "В вашем инвентаре"}
                }
                acquisition_conditions = {
                    "type": "automatic",
                    "requirements": {},
                    "description": f"You already have {item['name']}",
                    "description_trs": {"ru": f"У вас уже есть {item['name']}"}
                }
            elif initial_location.startswith('npc:'):
                location_type = 'npc'
                npc_name = initial_location.split(':')[1]
                location_details = item.get('location_details', {})
                location_details['visible_on_look_around'] = False
                acquisition_conditions = {
                    "type": "npc_gives",
                    "requirements": {
                        "npc_name": npc_name,
                        "min_interactions": 1,
                        "keywords": []
                    }
                }
            else:
                location_type = 'visible'
                location_details = item.get('location_details', {})
                location_details['visible_on_look_around'] = True  # ✅ Всегда true для items в сцене
                acquisition_conditions = item.get('acquisition_conditions', {
                    "type": "search",
                    "requirements": {
                        "action": "search",
                        "keywords": ["search", "look", "find"],
                        "required_item": None,
                        "min_interactions": 0
                    }
                })


            result = await pgDB.fFetch_InsertQuery_args(
                self.pool_base,
                query,
                story_id,
                item['name'],
                json.dumps(item.get('name_trs', {}), ensure_ascii=False),
                item['description'],
                json.dumps(item.get('description_trs', {}), ensure_ascii=False),
                item.get('purpose', ''),
                initial_location,
                item.get('is_key_item', False),
                location_type,  # ✅
                json.dumps(location_details, ensure_ascii=False),  # ✅
                json.dumps(acquisition_conditions, ensure_ascii=False)  # ✅
            )

            if hasattr(result, 'get'):
                item_id = result['c_item_id']
            elif hasattr(result, '__getitem__'):
                item_id = result[0]
            else:
                item_id = int(result)

            item_name_to_id[item['name']] = item_id
            logger.debug(f"Created item '{item['name']}' with ID {item_id}")

        return item_name_to_id

    def _add_voice_overrides_to_scene_context(
            self,
            scene_context: Dict[str, Any],
            npc_names: List[str]
    ) -> Dict[str, Any]:
        """
        Автоматически добавить voice_override для зомби и монстров в scene_context

        Args:
            scene_context: Контекст сцены (из detailed_objectives)
            npc_names: Список имён NPCs в этой сцене

        Returns:
            Обновлённый scene_context с voice_override
        """

        # Проверяем, есть ли npc_behavior_overrides
        if 'npc_behavior_overrides' not in scene_context:
            # Если нет - не добавляем ничего
            return scene_context

        npc_overrides = scene_context['npc_behavior_overrides']

        for npc_name in npc_names:
            # Проверяем, есть ли override для этого NPC
            if npc_name not in npc_overrides:
                continue

            override = npc_overrides[npc_name]

            # Если уже есть voice_override - пропускаем
            if 'voice_override' in override:
                continue

            npc_lower = npc_name.lower()

            # Автоматически добавляем voice_override для зомби
            if 'zombie' in npc_lower:
                override['voice_override'] = {
                    'mode': 'sfx_only',
                    'available_sounds': [
                        'zombie_growl'
                    ],
                    'fallback_pattern': 'GRRRAAAHHHH'
                }
                logger.info(f"Auto-added voice_override for zombie: {npc_name}")

            # Для монстров - гибридный режим
            elif any(word in npc_lower for word in ['monster', 'creature', 'beast']):
                override['voice_override'] = {
                    'mode': 'hybrid',
                    'available_sounds': ['monster_roar', 'monster_hiss'],
                    'fallback_pattern': 'ROOOAAAR!'
                }
                logger.info(f"Auto-added voice_override for monster: {npc_name}")

        return scene_context

    async def _create_scenes(
            self,
            story_id: int,
            scenes: List[Dict[str, Any]],
            npc_name_to_id: Dict[str, int],
            item_name_to_id: Dict[str, int],
            detailed_objectives: Dict[int, Dict[str, Any]]  # NEW!
    ):
        """Создать Scenes в БД с detailed objectives"""

        # Проход 1: Создать все сцены
        scene_ids = {}

        for scene in scenes:
            scene_num = scene['scene_number']
            
            # Конвертируем имена NPC в ID
            npc_names = scene.get('npcs_present', [])
            npc_ids = [
                npc_name_to_id[name]
                for name in npc_names
                if name in npc_name_to_id
            ]

            # Конвертируем имена ITEMS в ID
            item_names = scene.get('items_available', [])
            item_ids = [
                item_name_to_id[name]
                for name in item_names
                if name in item_name_to_id
            ]

            # Получаем detailed objectives для этой сцены
            scene_objectives = detailed_objectives.get(scene_num, {})
            objectives_list = scene_objectives.get('objectives', [])
            scene_context = scene_objectives.get('scene_context', {})
            scene_context = self._add_voice_overrides_to_scene_context(
                scene_context=scene_context,
                npc_names=scene.get('npcs_present', [])
            )

            query = """
                INSERT INTO t_story_scenes
                    (c_story_id, c_chapter_number, c_scene_number, c_scene_name,
                    c_location_description, c_location_description_trs,
                    c_objective, c_objective_trs, c_npcs_present, c_items_available,
                    c_success_conditions, c_is_ending, c_ending_type,
                    c_detailed_objectives, c_scene_context)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
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
                json.dumps(scene.get('location_description_trs', {}), ensure_ascii=False),
                scene['objective'],
                json.dumps(scene.get('objective_trs', {}), ensure_ascii=False),
                json.dumps(npc_ids),
                json.dumps(item_ids),
                json.dumps(scene['success_conditions'], ensure_ascii=False),
                scene.get('is_ending', False),
                scene.get('ending_type'),
                json.dumps({'objectives': objectives_list}, ensure_ascii=False),  # NEW!
                json.dumps(scene_context, ensure_ascii=False)  # NEW!
            )

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



    async def _get_initial_inventory_items(self, story_id: int) -> List[int]:
        """
        Получить список item_id для items с initial_location='inventory'

        Returns:
            List of item IDs
        """
        query = """
            SELECT c_item_id
            FROM t_story_items
            WHERE c_story_id = $1 
            AND c_initial_location = 'inventory'
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            query,
            story_id
        )

        if not result:
            return []

        return [row[0] for row in result]

    def _configure_item_visibility(
            self,
            skeleton_data: Dict[str, Any],
            detailed_objectives: Dict[int, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Настроить видимость items на основе reveals_item"""

        logger.info("=== Configuring item visibility ===")

        # Собрать все reveals_item из objectives
        revealed_items = set()

        for scene_num, objectives_data in detailed_objectives.items():
            objectives = objectives_data.get('objectives', [])

            for obj in objectives:
                if obj.get('type') == 'information':
                    reveals_item = obj.get('reveals_item')
                    if reveals_item:
                        revealed_items.add(reveals_item.lower())
                        logger.info(f"Scene {scene_num}: '{reveals_item}' will be revealed by dialogue")

        logger.info(f"Found {len(revealed_items)} items with reveals_item: {revealed_items}")

        # Обновить visible_on_look_around для items
        items_modified = 0
        for item in skeleton_data.get('items', []):
            item_name = item['name']
            item_name_lower = item_name.lower()

            # ⭐ ДОБАВИТЬ: Проверка наличия location_details
            if 'location_details' not in item:
                logger.warning(f"Item '{item_name}' has no location_details, skipping")
                continue

            # ⭐ ДОБАВИТЬ: Логирование до изменения
            old_visible = item['location_details'].get('visible_on_look_around', True)

            if item_name_lower in revealed_items:
                # Item раскрывается через диалог → скрыт
                item['location_details']['visible_on_look_around'] = False
                new_visible = False
            else:
                # Item не имеет reveals_item → виден сразу
                item['location_details']['visible_on_look_around'] = True
                new_visible = True

            # ⭐ ДОБАВИТЬ: Логирование изменения
            if old_visible != new_visible:
                logger.info(f"v Changed '{item_name}': visible {old_visible} → {new_visible}")
                items_modified += 1
            else:
                logger.debug(f"Item '{item_name}': visible={new_visible} (no change)")

        logger.info(f"Modified visibility for {items_modified}/{len(skeleton_data.get('items', []))} items")

        return skeleton_data


    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Парсить ответ AI и валидировать структуру"""

        try:
            # Убираем markdown блоки если есть
            cleaned = ai_response.strip()
            if cleaned.startswith('```'):
                lines = cleaned.split('\n')
                # Убираем первую строку (```json) и последнюю (```)
                cleaned = '\n'.join(lines[1:-1]) if len(lines) > 2 else cleaned

            data = json.loads(cleaned)
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"AI response: {ai_response[:500]}...")
            raise ValueError("AI returned invalid JSON")
