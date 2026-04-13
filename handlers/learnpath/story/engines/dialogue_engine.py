"""
Dialogue Engine - Генерация диалогов с NPC в реальном времени
"""

import logging
from typing import Dict, Any, Optional, List
import json
import selfFunctions as myF
import fpgDB as pgDB
from datetime import datetime
import re
import random

from ..managers.item_manager import ItemManager

#from ...handlers.story_helpers import (
    #get_revealed_facts,
    #mark_facts_revealed,
    #select_facts_for_response,
    #format_facts_for_prompt,
    #check_objective_by_facts,
    #get_npc_id_by_name
#)




logger = logging.getLogger(__name__)


class DialogueEngine:
    """Движок для генерации диалогов с NPC в реальном времени"""

    def __init__(self, pool, user_id: int):
        self.pool_base, self.pool_log = pool
        self.user_id = user_id

    async def generate_npc_response(
            self,
            user_input: str,
            npc_context: Dict[str, Any],
            scene_context: Dict[str, Any],
            story_context: Dict[str, Any],
            user_level: int
    ) -> Dict[str, Any]:
        """Сгенерировать ответ NPC"""

        npc_name = npc_context['name']
        npc_id = npc_context['npc_id']

        # Получить user_id и story_id
        user_id = self.user_id
        story_id = scene_context.get('story_id') or story_context.get('story_id')
        scene_id = scene_context.get('scene_id')

        # ---------------------------------------------------
        # Получить items objectives
        scene_items_needed = []
        if scene_context.get('detailed_objectives'):
            objectives = scene_context['detailed_objectives'].get('objectives', [])
            scene_items_needed = [
                obj['target'] for obj in objectives
                if obj.get('type') == 'item'
            ]

        # Получить items у NPC
        npc_items_available = npc_context.get('items_to_give', [])
        npc_item_names = [item['name'] for item in npc_items_available]

        # Флаг: есть ли items
        has_items_to_give = len(npc_items_available) > 0

        logger.info(f'--------------------scene_items_needed:{scene_items_needed}')
        logger.info(f'--------------------npc_items_available:{npc_items_available}')
        logger.info(f'--------------------npc_item_names:{npc_item_names}')
        logger.info(f'--------------------has_items_to_give:{has_items_to_give}')
        #---------------------------------------------------

        prompt, facts_to_reveal = await self._create_user_prompt(
            user_input=user_input,
            npc_context=npc_context,
            scene_context=scene_context,
            story_context=story_context,
            #user_level=user_level,
            user_id=user_id,
            story_id=story_id
        )

        '''
        npc_name = npc_context['name']
        npc_role = npc_context.get('role_description', 'a character')
        personality = npc_context.get('personality', {})
        personality_traits = ', '.join(personality.get('traits', ['friendly']))
        base_mood = personality.get('base_mood', 'neutral')
        '''

        systemPrompt = await self._create_system_prompt(
            npc_context,
            user_level,
            has_items_to_give=has_items_to_give
        )


        try:
            # Запрос к AI
            logger.info(f">>>>>>>>>>>>user prompt:{prompt}")
            logger.info(f">>>>>>>>>>>>system prompt:{systemPrompt}")
            content = await myF.afSendMsg2AI(
                prompt,
                self.pool_base,
                self.user_id,
                iModel=0,  # GPT-4o для качественных диалогов
                toggleParam=3,  # Temperature 0.7
                systemPrompt=systemPrompt
            )

            # Убираем markdown если есть
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            content = content.strip()

            content = re.sub(r',(\s*[}\]])', r'\1', content)

            # Парсим JSON
            response_data = json.loads(content)


            # Валидируем структуру
            self._validate_response_structure(response_data)

            # Добавляем метаданные
            response_data['npc_id'] = npc_context['npc_id']
            response_data['npc_name'] = npc_context['name']

            # Обработка given_items
            given_items = response_data.get('given_items', [])

            logger.info(f'--------------------given_items:{given_items}')

            if given_items and isinstance(given_items, list) and len(given_items) > 0:
                logger.info(f"NPC reported giving items: {given_items}")

                from handlers.learnpath.story.managers.item_manager import ItemManager
                item_manager = ItemManager((self.pool_base, self.pool_log))

                for item_name in given_items:
                    # Найти item в items_to_give
                    matching_item = None
                    for npc_item in npc_items_available:
                        if npc_item['name'].lower().strip() == item_name.lower().strip():
                            matching_item = npc_item
                            break

                    if not matching_item:
                        logger.warning(f"AI hallucination: '{item_name}' not in items_to_give")
                        continue

                    # Проверить что item еще не в inventory
                    has_item = await item_manager.check_item_in_inventory(
                        user_id, story_id, matching_item['item_id']
                    )

                    if has_item:
                        logger.info(f"User already has '{item_name}', skipping")
                        continue

                    # Добавить в inventory
                    await item_manager.add_item_to_inventory(
                        user_id, story_id, matching_item['item_id']
                    )

                    logger.info(f"✅ Added '{item_name}' to user inventory")

                    # Добавить метаданные
                    response_data['item_given'] = True
                    response_data['item_name'] = item_name
                    response_data['item_id'] = matching_item['item_id']

            advanse_status = response_data['advance']
            classification = response_data['classification']
            logger.info(f'---------------advanse_status:{advanse_status}')
            logger.info(f'---------------classification:{classification}')

            if facts_to_reveal and user_id and story_id and scene_id:
                try:
                    facts_used = response_data.get('facts_used', [])

                    if facts_used:
                        logger.info(f"AI reported using facts: {facts_used}")

                        success = await self.mark_facts_revealed(
                            user_id=user_id,
                            story_id=story_id,
                            scene_id=scene_id,
                            npc_id=npc_id,
                            fact_indexes=facts_used  # ← Только реально использованные!
                        )

                        if success:
                            logger.info(f"Marked facts {facts_used} as revealed")
                        else:
                            logger.error(f"Failed to mark facts")
                    else:
                        logger.info("AI used no facts (emotional/greeting response)")

                except Exception as e:
                    logger.error(f"Error marking facts as revealed: {e}", exc_info=True)



            logger.info(f"Generated response for NPC {npc_context['name']}")

            # Проверить и обновить dialogue stage
            npc_overrides = {}
            if 'npc_behavior_overrides' in scene_context:
                npc_overrides = scene_context['npc_behavior_overrides'].get(npc_name, {})
            if npc_overrides.get('dialogue_flow') and scene_id:
                logger.info(f"=" * 80)
                logger.info(f"DIALOGUE FLOW DETECTED for {npc_name}")
                logger.info(f"User input: {user_input}")

                new_stage = await self._advance_dialogue_stage(
                    user_id=user_id,
                    story_id=story_id,
                    scene_id=scene_id,
                    npc_id=npc_id,
                    user_input=user_input,
                    npc_behavior_overrides=npc_overrides
                )
                logger.info(f"Current dialogue stage for {npc_name}: {new_stage}")
                logger.info(f"=" * 80)

                logger.info(f"Dialogue stage for {npc_name}: {new_stage}")


            return response_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Response content: {content[:500]}")

            #  НОВОЕ: Попытка 2 - более агрессивная очистка
            try:
                # Убрать ВСЕ trailing commas агрессивно
                content_fixed = re.sub(r',(\s*[}\]])', r'\1', content)
                # Убрать комментарии если есть
                content_fixed = re.sub(r'//.*$', '', content_fixed, flags=re.MULTILINE)

                response_data = json.loads(content_fixed)
                logger.warning(" Fixed JSON on second attempt by removing trailing commas")

                self._validate_response_structure(response_data)
                response_data['npc_id'] = npc_context['npc_id']
                response_data['npc_name'] = npc_context['name']
                return response_data


            except json.JSONDecodeError as e2:
                logger.error(f"Second parse attempt also failed: {e2}")
                # Возвращаем fallback ответ
                return self._create_fallback_response(npc_context)

        except Exception as e:
            logger.error(f"Error generating NPC response: {e}", exc_info=True)
            return self._create_fallback_response(npc_context)





    async def _create_system_prompt(
            self,
            npc_context,
            user_level,
            has_items_to_give: bool = False
    ):
        npc_name = npc_context['name']
        npc_role = npc_context.get('role_description', 'a character')
        personality = npc_context.get('personality', {})
        personality_traits = ', '.join(personality.get('traits', ['friendly']))
        base_mood = personality.get('base_mood', 'neutral')

#CRITICAL: If you see "CRITICAL DIALOGUE STAGE SYSTEM" in your instructions below, you MUST follow those stage instructions EXACTLY. They override everything else.

        #AJRM
        systemPrompt = f'''
ROLES:
    You act in two separate roles:
    1. You are a character in an ESL interactive story, who provides natural response to user's phrase.
    2. You are an English tutor, who checks user's phrase
    
CRITICAL - Never mix the roles

DETAILS for English tutor role:
    - You are an experienced and friendly English tutor having a natural conversation with your student
    - Check if the text is grammatically correct for Standard English
    - If the student makes language errors, gently correct them in a natural, conversational way
    - Focus only on 1-2 most important issues to avoid overwhelming
    - Respond in natural academic Russian
    
DETAILS for story character role:
    Your name: {npc_name}
    Your personality: {personality_traits}
    Your role: {npc_role}
    Your mood: {base_mood}
    English level to use: {self._format_user_level(user_level)}

    IMPORTANT INTERACTION RULES:
    - The USER is talking to {npc_name} directly
    - Address the USER directly using "you" (NOT any character name)
    - Stay in character based on your personality and role


    You may internally classify the user's intent, but NEVER mention this process or react to it:
    STEP 1 — Classify the user's message as ONE of the following INTENTS:
    - GREETING
      (opening, closing, politeness, acknowledgement)
    - SOCIAL_BONDING
      (emotions, impressions, reactions, agreement, empathy, atmosphere, compliments, small talk)
    - INFORMATION_REQUEST
      (questions about events, facts, motives, past actions, plans, explanations)
    - ACTION_OR_DECISION
      (requests to do something, choices, suggestions, commands, toasts, invitations)
    - OFFTOPIC
      (content clearly unrelated to current scene or narrative)
    
    STEP 2 — RESPONSE MODE:
    IF intent is GREETING:
    - Warm, short emotional response
    - Optional simple question
    - DO NOT reveal facts from information pool
    - facts_used: []
    GREETING RULE (CRITICAL):
        - A greeting like "Hi", "Hello", or "Hi, Dave" is ALWAYS valid.
        - NEVER ask the user to repeat or clarify a greeting.
        - NEVER comment on the user's choice of addressing.
        - ALWAYS respond with a greeting in character.
    For GREETING responses, use patterns like:
        - "Hey. Good to see you."
        - "Hi. What can I do for you?"
        - "Hey there. You alright?"
    IF intent is SOCIAL_BONDING:
    - Mirror emotion
    - Deepen relationship or tension
    - Progress scene socially
    - NO forced facts
    IF intent is INFORMATION_REQUEST:
    - Provide information if available
    - Choose facts based on scene state
    - Respect withholding rules if applicable
    IF intent is ACTION_OR_DECISION:
    - React in character
    - Accept / resist / negotiate based on personality
    - Move scene forward
    IF intent is OFFTOPIC:
    - Brief acknowledgement
    - Soft redirect to scene
    
    STEP 3 - CHECK ADVANCE SCENE MODE
    Analyse the dialogue progression - should it be moved to the next stage?

ANTI-REPETITION RULES:
    1. Look at PREVIOUS CONVERSATION
    2. If you said "Sarah needs help" ONCE -> NEVER say it again
    3. If you said "I can't leave right now" ONCE -> NEVER say it again  
    4. If you said "She is scared" ONCE -> NEVER say it again
    5. Every INVESTIGATIVE response must introduce NEW information from MUST MENTION list
    6. If user is insistent (mentions danger/urgency multiple times) -> STOP resisting and AGREE
        
    VIOLATION EXAMPLES (what NOT to do):
        Message 1: "Sarah needs help"
        Message 2: "Sarah needs help" (FORBIDDEN - already said this!)
           
        Message 1: "I can't leave"
        Message 2: "I can't leave right now" (FORBIDDEN - same meaning!)
        
    CORRECT EXAMPLE:
        Message 1: "I'm at Sara's house. Her neighbors are making a mess."
        Message 2: "There are people covered in red paint everywhere."
        Message 3: "You're scaring me. Are you serious?"

RESPONSE FORMAT:
- You MUST respond ONLY with valid JSON, no additional text or markdown
- NO trailing commas (NO comma before closing }} or ]])
- NO comments in JSON
- ALWAYS use double quotes for strings

JSON SCTRUCTURE (mandatory):
- "response": Story character role response
- "correction": English tutor role response
- "facts_used": Array of fact indexes
- "npc_action": Action description
- "text_trs": Translation for story character role response into natural academic Russian
- "classification": The user's message classification from Step 1 (GREETING, SOCIAL_BONDING, INFORMATION_REQUEST, ACTION_OR_DECISION or OFFTOPIC)
- "advance": true/false
- "given_items": Array of item names given to user (empty array [] if none)


OUTPUT EXAMPLES:
Example 1 - User made a grammar mistake:
{{
  "response": "Hi! I'm burying my goldfish.",
  "facts_used": [0],
  "correction": "Хорошая попытка! Скажите 'How are you?' вместо 'How is you?'",
  "npc_action": "continues digging",
  "text_trs": {{
    "ru": "Привет! Я хороню мою золотую рыбку."
  }},
  "classification": "INFORMATION_REQUEST",
  "advance": true
}}

Example 2 - User doesn't have languages errors:
{{
  "response": "That is because the fish is inside your damn cat!",
  "facts_used": [1, 2],
  "correction": "",
  "npc_action": "stares at you deadpan",
  "text_trs": {{
    "ru": "Потому что рыбка внутри твоего проклятого кота!"
  }},
  "classification": "INFORMATION_REQUEST",
  "advance": true
}}
        '''

        if has_items_to_give:
            systemPrompt += '''

ITEM GIVING INSTRUCTIONS:
You have items that you can give to the user (see YOUR ITEMS TO GIVE in user prompt).

When user explicitly requests an item (e.g., "give me X", "can I have X", "I need X"):
1. Check if you have this item
2. Use giving phrases in your response like:
    - "Here is the {item_name}"
    - "Here are the {item_name}"  
    - "Take the {item_name}"
    - "Here you go - {item_name}"
3. Fill "given_items" field with item names:
    "given_items": ["matches"]          // if gave one item
    "given_items": ["ice cream", "soda"] // if gave multiple
    "given_items": []                    // if gave nothing

IMPORTANT:
    - Item name in "given_items" must EXACTLY match name from YOUR ITEMS TO GIVE list
    - Only add items you explicitly gave using phrases above
    - If user just mentions item but you don't give it → "given_items": []

    Examples:
    User: "Give me matches"
    Your response: "Here are the matches."
    "given_items": ["matches"]

    User: "Do you have ice cream?"
    Your response: "Yes, we have ice cream in the freezer."
    "given_items": []
            '''
        else:
            systemPrompt += '''

ITEM GIVING INSTRUCTIONS:
    You have no items to give. Always use:
    "given_items": []
            '''

        return systemPrompt





    async def _create_user_prompt(
            self,
            user_input: str,
            npc_context: Dict[str, Any],
            scene_context: Dict[str, Any],
            story_context: Dict[str, Any],
            #user_level: int,
            user_id: int = None,
            story_id: int = None
    ) -> str:
        """Создать промпт для генерации диалога"""
        #AJRM
        npc_name = npc_context['name']
        scene_id = scene_context.get('scene_id')
        npc_id = npc_context.get('npc_id')
        # Получить npc_behavior_overrides
        npc_overrides = {}
        if 'npc_behavior_overrides' in scene_context:
            npc_overrides = scene_context['npc_behavior_overrides'].get(npc_name, {})


        facts_to_reveal = []
        revealed_indexes = []
        facts_prompt_text = ""


        info_pool = npc_overrides.get('information_pool')

        # ========================================
        # ДИАГНОСТИКА
        # ========================================
        logger.info("=" * 80)
        logger.info("DIAGNOSTIC INFO")
        logger.info(f"   npc_name: {npc_name}")
        logger.info(f"   user_id: {user_id}")
        logger.info(f"   story_id: {story_id}")
        logger.info(f"   scene_id: {scene_id}")
        logger.info(f"   npc_overrides keys: {list(npc_overrides.keys())}")
        logger.info(f"   Has info_pool: {info_pool is not None}")

        if 'npc_behavior_overrides' in scene_context:
            logger.info(f"   scene_context HAS npc_behavior_overrides")
            logger.info(f"   Available NPCs: {list(scene_context['npc_behavior_overrides'].keys())}")
        else:
            logger.info(f"   scene_context MISSING npc_behavior_overrides")
            logger.info(f"   scene_context keys: {list(scene_context.keys())}")

        logger.info("=" * 80)
        # ========================================

        if info_pool and user_id and story_id and scene_id:
            logger.info(f"=" * 80)
            logger.info(f"INFORMATION POOL DETECTED for {npc_name}")

            try:
                max_facts = info_pool.get('reveal_strategy', {}).get('facts_per_response', 3)

                # Выбрать факты для раскрытия
                facts_to_reveal = await self.select_facts_for_response(
                    user_id=user_id,
                    story_id=story_id,
                    scene_id=scene_id,
                    npc_id=npc_id,
                    information_pool=info_pool,
                    max_facts=max_facts
                )

                # Получить уже раскрытые
                revealed_indexes = await self.get_revealed_facts(
                    user_id=user_id,
                    story_id=story_id,
                    scene_id=scene_id,
                    npc_id=npc_id
                )

                # Форматировать для промпта
                if facts_to_reveal or revealed_indexes:
                    from ...handlers.story import get_scene_objectives_status
                    pool = self.pool_base, self.pool_log
                    _, _, uncompleted_obj = await get_scene_objectives_status(
                        pool, user_id, story_id, scene_id
                    )

                    facts_prompt_text = self.format_facts_for_prompt(
                        facts_to_reveal,
                        revealed_indexes,
                        info_pool['facts'],
                        uncompleted_obj
                    )

                logger.info(f"Selected {len(facts_to_reveal)} facts to reveal")
                logger.info(f"   Indexes: {[f['index'] for f in facts_to_reveal]}")
                logger.info(f"   Already revealed: {revealed_indexes}")




            except Exception as e:
                logger.error(f"Facts selection error: {e}", exc_info=True)



        current_scene_number = scene_context.get('scene_number', 0)
        logger.info(f"Current scene: {current_scene_number}")

        npc_description = npc_context.get('description', '')

        # Фильтровать role_description
        role_description = npc_context.get('role_description', '')
        role_description = self._filter_scene_specific_text(role_description, current_scene_number)

        # Фильтровать secondary goals
        secondary_goals_raw = npc_context.get('goals', {}).get('secondary', [])
        secondary_goals_filtered = [
            self._filter_scene_specific_text(g, current_scene_number)
            for g in secondary_goals_raw
        ]
        secondary_goals_filtered = [g for g in secondary_goals_filtered if g.strip()]  # Только непустые


        #level_desc = self._format_user_level(user_level)

        # Получаем историю предыдущих взаимодействий
        recent_interactions = npc_context.get('recent_interactions', [])
        interactions_text = ""

        if recent_interactions:
            interactions_text = "\n\nPREVIOUS CONVERSATION:\n"
            for interaction in recent_interactions[-3:]:  # Последние 3
                interactions_text += f"User: {interaction['user_input']}\n"
                interactions_text += f"You: {interaction['ai_response']}\n"

        # Добавить информацию о items если они есть
        npc_items_text = ""
        if npc_context.get('items_to_give'):
            npc_items_text = "\n\nYOUR ITEMS TO GIVE:\n"
            for item in npc_context.get('items_to_give', []):
                npc_items_text += f"- {item['name']}: {item['description']}\n"

            npc_items_text += """
CRITICAL ITEM GIVING RULES:
    1. When user explicitly asks for an item:
        -> Give it using phrases like:
          - "Here is the {item_name}"
          - "Here are the {item_name}"
          - "Take the {item_name}"

    2. Fill "given_items" array with item names you gave:
       - Gave matches: "given_items": ["matches"]
       - Gave nothing: "given_items": []

    3. Item names must EXACTLY match list above
    4. Only give items user explicitly requested
            """

        # Добавить вопрос в конце фразы npc
        npc_question_ending = ''
        booleanVar = False if random.random() < 0.6 else True
        if booleanVar:
            npc_question_ending = 'End your response with a simple question to the user'

        # CHECK FOR SCENE-SPECIFIC NPC BEHAVIOR OVERRIDES

        behavior_override_text = ""

        dialogue_stage_text = ""
        if npc_overrides:
            dialogue_flow = npc_overrides.get('dialogue_flow')

            if dialogue_flow:
                # Получить текущий stage
                current_stage = await self._get_current_dialogue_stage(
                    user_id=user_id,
                    story_id=story_id,
                    scene_id=scene_id,
                    npc_id=npc_id,
                    npc_behavior_overrides=npc_overrides
                )

                if current_stage and current_stage in dialogue_flow:
                    stage_info = dialogue_flow[current_stage]

                    must_mention = stage_info.get('must_mention', [])
                    must_not_mention = stage_info.get('must_not_mention', [])
                    tone = stage_info.get('tone', 'natural')
                    trigger = stage_info.get('trigger', 'user continues conversation')

                    #AJRM
                    dialogue_stage_text = f"""
CRITICAL DIALOGUE STAGE SYSTEM:
Current stage: {current_stage}

If the user's message is NOT classified as GREETING or OFFTOPIC:
    - MENTION these topics in this response (naturally, not all at once):
    {chr(10).join('- ' + item for item in must_mention)}
            
    - NOT MENTION yet (save for later stages):
    {chr(10).join('- ' + item for item in must_not_mention) if must_not_mention else '(no restrictions)'}
            
    Tone for this stage: {tone}
    
    STAGE RULES:
    - Incorporate topics from MENTION naturally into your response
    - Pick 1-2 topics from MENTION per response (don't dump everything at once)
    - DO NOT reveal information from NOT MENTION list
    - Stay in character with the specified tone
    - Progress conversation naturally toward stage completion
                    """

                    # ========================================
                    # ДОБАВИТЬ: Relevance Check
                    # ========================================
                    relevance_check = stage_info.get('relevance_check')

                    if relevance_check:
                        expected_topic = relevance_check.get('expected_topic', 'the current topic')
                        off_topic_response = relevance_check.get('off_topic_response', 'I need to focus on this.')

                        dialogue_stage_text += f"\n{'=' * 80}\n"
                        dialogue_stage_text += f"️ RESPONSE MODE SYSTEM (OVERRIDES 'MUST MENTION') ️\n"
                        dialogue_stage_text += f"{'=' * 80}\n\n"

                        dialogue_stage_text += f"CLASSIFY USER MESSAGE AS ONE OF TWO CATEGORIES:\n\n"

                        # === OFF-TOPIC ===
                        dialogue_stage_text += f"OFF-TOPIC (user NOT asking about: {expected_topic})\n"
                        dialogue_stage_text += f"   This includes:\n"
                        dialogue_stage_text += f"   • Greetings (Hi, Hello, Hey, etc.)\n"
                        dialogue_stage_text += f"   • Small talk (weather, feelings, generic questions)\n"
                        dialogue_stage_text += f"   • Unrelated topics (shopping, other activities)\n\n"

                        dialogue_stage_text += f"   RESPONSE MODE = EMOTIONAL_ONLY\n"
                        dialogue_stage_text += f"   CRITICAL: IGNORE all 'MUST MENTION' rules above!\n\n"

                        # Специальная обработка для first_contact
                        if trigger == 'first_contact':
                            dialogue_stage_text += f"   Special case for GREETINGS on first contact:\n"
                            dialogue_stage_text += f"   → Brief greeting + mention ONLY 1 topic from MUST MENTION\n"
                            dialogue_stage_text += f"   → Example: 'Hi. I\\'m burying my goldfish.'\n"
                            dialogue_stage_text += f"   → Keep it SHORT (1-2 sentences)\n\n"

                            dialogue_stage_text += f"   For all other OFF-TOPIC messages:\n"
                            dialogue_stage_text += f"   → Respond with: '{off_topic_response}'\n"
                            dialogue_stage_text += f"   → Brief and dismissive\n\n"
                        else:
                            dialogue_stage_text += f"   → Respond with: '{off_topic_response}'\n"
                            dialogue_stage_text += f"   → Brief and dismissive\n"
                            dialogue_stage_text += f"   → DO NOT reveal any MUST MENTION information\n\n"

                        # === ON-TOPIC ===
                        dialogue_stage_text += f"ON-TOPIC (user IS asking about: {expected_topic})\n"
                        dialogue_stage_text += f"   Examples: 'Why is the hole big?', 'What are you digging?'\n\n"

                        dialogue_stage_text += f"   RESPONSE MODE = FACT_REVEAL\n"
                        dialogue_stage_text += f"   → Reveal 1-2 topics from MUST MENTION\n"
                        dialogue_stage_text += f"   → Choose most relevant to user's question\n"
                        dialogue_stage_text += f"   → Use tone: {tone}\n\n"

                        dialogue_stage_text += f"{'=' * 80}\n"
                    # ========================================

        # Check if scene_context has behavior overrides for this NPC
        if 'npc_behavior_overrides' in scene_context:
            npc_overrides = scene_context['npc_behavior_overrides'].get(npc_name, {})
            if npc_overrides:
                behavior_override_text = "\n\n CRITICAL SCENE-SPECIFIC BEHAVIOR FOR THIS SCENE:\n"
                behavior_override_text += f"{npc_overrides.get('scene_specific_behavior', '')}\n"
                if 'first_message_must_be' in npc_overrides:
                    behavior_override_text += f"\nYOUR FIRST MESSAGE MUST BE EXACTLY: \"{npc_overrides['first_message_must_be']}\"\n"
                if 'second_message_must_start_with' in npc_overrides:
                    behavior_override_text += f"YOUR SECOND MESSAGE MUST START WITH: \"{npc_overrides['second_message_must_start_with']}\"\n"
                if 'after_prank' in npc_overrides:
                    behavior_override_text += f"AFTER PRANK: {npc_overrides['after_prank']}\n"
                behavior_override_text += "\n️ THIS OVERRIDES ALL OTHER INSTRUCTIONS ABOVE ️\n"

                logger.info(f"BEHAVIOR OVERRIDE ACTIVATED for {npc_name}!")
                #logger.info(f"Override text:\n{behavior_override_text}")

        # Формируем промпт
        prompt = f"""
            You are roleplaying as an NPC in an ESL interactive story.

            NPC IDENTITY:
            - Name: {npc_context['name']}
            - Description: {npc_description}

            SCENE CONTEXT:
            - Situation: {scene_context.get('current_situation', '')}
            
            Respond using the JSON format defined in the system instructions
            
            {npc_question_ending}
        """

        #- Location: {scene_context.get('location_name', 'Unknown location')}

        scene_story_context = scene_context.get('scene_story_context', {})

        if scene_story_context:
            prompt += "\n    DEEP STORY CONTEXT:\n"

            if scene_story_context.get('summary'):
                prompt += f"    - Summary: {scene_story_context['summary']}\n"

            if scene_story_context.get('key_mystery'):
                prompt += f"    - Key Mystery: {scene_story_context['key_mystery']}\n"

            if scene_story_context.get('timeline'):
                prompt += f"    - Timeline: {scene_story_context['timeline']}\n"

            if scene_story_context.get('location_details'):
                prompt += f"    - Location Details: {scene_story_context['location_details']}\n"

            # Important characters
            important_chars = scene_story_context.get('important_characters', {})
            if important_chars:
                prompt += "    - Important Characters:\n"
                for char_name, char_desc in important_chars.items():
                    prompt += f"      • {char_name}: {char_desc}\n"

            # Evidence items
            evidence = scene_story_context.get('evidence_items', {})
            if evidence:
                prompt += "    - Evidence Items:\n"
                for item_name, item_desc in evidence.items():
                    prompt += f"      • {item_name}: {item_desc}\n"


        # ========================================

        prompt += f"""

        {behavior_override_text}
        {dialogue_stage_text}
        {facts_prompt_text}
        
        
        PREVIOUS CONVERSATION:
        {interactions_text}

        USER'S CURRENT MESSAGE:
        "{user_input}"

        
        
        DIALOGUE PROGRESSION RULES:
        - If DIALOGUE STAGE SYSTEM is defined above -> follow CURRENT STAGE instructions
        - Pick 1-2 NEW topics from MENTION per response
        - NEVER repeat what you already said
        - If user mentions danger/pickup 2+ times -> move to next stage emotionally

        YOUR TASK:
        Respond to the user as {npc_name}.
        - Stay in character
        - Follow stage instructions if present
        - Avoid repetition
        - Progress the conversation naturally
        
       
        
        """

        logger.info(f" NPC Context keys: {list(npc_context.keys())}")
        logger.info(f" Scene Context keys: {list(scene_context.keys())}")

        # Логируем только важные поля, безопасно
        logger.info(f"  - NPC name: {npc_context.get('name')}")
        logger.info(f"  - NPC role: {npc_context.get('role_description', 'N/A')[:100]}...")  # Первые 100 символов
        logger.info(f"  - NPC goals: {npc_context.get('goals', {}).get('primary', 'N/A')}")

        if 'npc_behavior_overrides' in scene_context:
            logger.info(f" Found npc_behavior_overrides in scene_context!")
            # Безопасно логируем JSON (без datetime)
            try:
                overrides_json = json.dumps(scene_context['npc_behavior_overrides'], indent=2, ensure_ascii=False)
                logger.info(f" Overrides:\n{overrides_json}")
            except TypeError as e:
                logger.info(f" Overrides (raw): {scene_context['npc_behavior_overrides']}")
        else:
            logger.warning(f"️ NO npc_behavior_overrides found in scene_context!")

        return prompt, facts_to_reveal

    def _format_user_level(self, user_level: int) -> str:
        """Форматировать уровень для промпта"""
        levels = {
            1: "A1-A2 (Beginner) - Use very simple sentences and basic vocabulary",
            2: "A2-B1 (Elementary) - Use simple sentences and common words",
            3: "B1 (Intermediate) - Mix simple and complex sentences, moderate vocabulary",
            4: "B1-B2 (Upper-Intermediate) - Use varied sentences and wider vocabulary",
            5: "B2-C1 (Advanced) - use sophisticated language, advanced grammar"
        }
        return levels.get(user_level, levels[3])

    def _filter_scene_specific_text(self, text: str, current_scene: int) -> str:
        """Убирает инструкции для других сцен"""
        import re
        lines = text.split('\n')
        filtered = []

        for line in lines:
            match = re.search(r'SCENE\s+(\d+)(\s+ONLY)?:', line, re.IGNORECASE)
            if match:
                scene_num = int(match.group(1))
                if scene_num == current_scene:
                    # Убираем "SCENE X:" префикс
                    cleaned = re.sub(r'SCENE\s+\d+(\s+ONLY)?:', '', line, flags=re.IGNORECASE).strip()
                    filtered.append(cleaned)
            else:
                filtered.append(line)  # Нет указания сцены - оставляем

        return '\n'.join(filtered)

    def _validate_response_structure(self, response_data: Dict[str, Any]):
        """Валидировать структуру ответа AI"""

        required_fields = ['response', 'correction']
        for field in required_fields:
            if field not in response_data:
                raise ValueError(f"Missing required field: {field}")

        #
        # Добавить facts_used с default
        if 'facts_used' not in response_data:
            response_data['facts_used'] = []
            logger.warning("AI didn't provide facts_used, defaulting to []")

        # Проверяем что response не пустой
        if not response_data['response'] or not response_data['response'].strip():
            raise ValueError("response cannot be empty")




    def _create_fallback_response(self, npc_context: Dict[str, Any]) -> Dict[str, Any]:
        """Создать fallback ответ если AI не сработал"""

        return {
            'response': f"I'm {npc_context['name']}. Could you say that again?",
            'correction': "No corrections needed.",
            'npc_action': "looks confused",
            'text_trs': {
                'ru': f"Я {npc_context['name']}. Не могли бы вы повторить?"
            },
            'correction_trs': {
                'ru': "Исправлений не требуется."
            },
            'npc_id': npc_context['npc_id'],
            'npc_name': npc_context['name']
        }

    async def mark_facts_revealed(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,
            npc_id: int,
            fact_indexes: List[int]
    ) -> bool:
        """
        Пометить факты как раскрытые

        Args:
            pool_base: Database connection pool
            user_id: ID пользователя
            story_id: ID истории
            scene_id: ID сцены
            npc_id: ID NPC
            fact_indexes: Список индексов фактов для пометки [0, 1, 2]

        Returns:
            bool: True если успешно, False если ошибка

        Example:
            success = await mark_facts_revealed(
                pool, 372671079, 23, 75, 89, [0, 1, 2]
            )
        """

        if not fact_indexes:
            logger.warning("No fact indexes provided to mark_facts_revealed")
            return True  # Технически успех, просто нечего делать

        try:
            # Получить progress_id
            progress_query = """
                SELECT c_progress_id
                FROM t_story_user_progress
                WHERE c_user_id = $1 AND c_story_id = $2
            """

            progress_result = await pgDB.fExec_SelectQuery_args(
                self.pool_base, progress_query, user_id, story_id
            )

            if not progress_result or not progress_result[0][0]:
                logger.error(
                    f"Cannot mark facts: no progress found for "
                    f"user {user_id} story {story_id}"
                )
                return False

            progress_id = progress_result[0][0]

            # Вставить revealed facts
            insert_query = """
                INSERT INTO t_story_user_revealed_facts 
                    (c_progress_id, c_user_id, c_story_id, c_scene_id, 
                     c_npc_id, c_fact_index)
                SELECT $1, $2, $3, $4, $5, unnest($6::int[])
                ON CONFLICT (c_progress_id, c_scene_id, c_npc_id, c_fact_index) 
                DO NOTHING
            """

            await pgDB.fExec_SelectQuery_args(
                self.pool_base,
                insert_query,
                progress_id,
                user_id,
                story_id,
                scene_id,
                npc_id,
                fact_indexes
            )

            logger.info(
                f"Marked facts {fact_indexes} as revealed for "
                f"user {user_id} story {story_id} scene {scene_id} NPC {npc_id}"
            )

            return True

        except Exception as e:
            logger.error(
                f"Error marking facts as revealed for user {user_id} "
                f"story {story_id} scene {scene_id} NPC {npc_id}: {e}",
                exc_info=True
            )
            return False

    def __________info_pool(self): pass

    async def select_facts_for_response(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,
            npc_id: int,
            information_pool: Dict[str, Any],
            max_facts: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Выбрать факты для раскрытия в ответе NPC

        Логика:
        1. Получить revealed facts
        2. Отфильтровать unrevealed facts
        3. Проверить условия (conditions)
        4. Отсортировать по priority (DESC)
        5. Выбрать top N

        Args:
            pool: Database connection pool
            user_id: ID пользователя
            story_id: ID истории
            scene_id: ID сцены
            npc_id: ID NPC
            information_pool: Dict с ключом 'facts'
            max_facts: Максимальное количество фактов для возврата

        Returns:
            List[Dict]: Список фактов с индексами
            [
                {"index": 0, "text": "...", "priority": 10, ...},
                {"index": 1, "text": "...", "priority": 10, ...},
                ...
            ]

        Example:
            info_pool = scene_context['npc_behavior_overrides']['Davies']['information_pool']
            facts = await select_facts_for_response(
                pool, user_id, story_id, scene_id, npc_id, info_pool, max_facts=3
            )
        """
        try:
            facts_array = information_pool.get('facts', [])

            if not facts_array:
                logger.warning(
                    f"No facts found in information_pool for NPC {npc_id}"
                )
                return []

            # 1. Получить revealed facts
            revealed_indexes = await self.get_revealed_facts(
                user_id, story_id, scene_id, npc_id
            )

            logger.info(
                f"Selecting facts for NPC {npc_id}. "
                f"Total facts: {len(facts_array)}, "
                f"Already revealed: {revealed_indexes}"
            )

            # 2. Отфильтровать unrevealed + проверить conditions
            available_facts = []

            for idx, fact in enumerate(facts_array):
                # Skip if already revealed
                if idx in revealed_indexes:
                    logger.debug(f"Fact {idx} already revealed, skipping")
                    continue

                # Check condition if exists
                if 'condition' in fact:
                    condition_met = await self.check_fact_condition(
                        user_id, story_id, fact['condition']
                    )

                    if not condition_met:
                        logger.debug(
                            f"Fact {idx} condition not met: {fact['condition']}"
                        )
                        continue

                # Add to available with index
                available_facts.append({
                    'index': idx,
                    **fact
                })

            logger.info(
                f"Available facts after filtering: {len(available_facts)}"
            )

            if not available_facts:
                logger.warning(
                    f"No available facts for NPC {npc_id} "
                    f"(all revealed or conditions not met)"
                )
                return []

            # 3. Сортировать по priority (DESC)
            available_facts.sort(
                key=lambda f: f.get('priority', 0),
                reverse=True
            )

            # 4. Выбрать top N
            selected = available_facts[:max_facts]

            logger.info(
                f"Selected {len(selected)} facts for response: "
                f"indexes {[f['index'] for f in selected]}, "
                f"priorities {[f.get('priority') for f in selected]}"
            )

            return selected

        except Exception as e:
            logger.error(
                f"Error selecting facts for response: {e}",
                exc_info=True
            )
            return []

    async def check_fact_condition(
            self,
            user_id: int,
            story_id: int,
            condition: Dict[str, Any]
    ) -> bool:
        """
        Проверить условие для раскрытия факта

        Args:
            pool_base: Database connection pool
            user_id: ID пользователя
            story_id: ID истории
            condition: Словарь с условием
                {"type": "user_has_item", "item_name": "Blackmail Note"}
                {"type": "user_gave_item", "item_name": "Glass Fragments"}
                {"type": "user_has_not_given_item", "item_name": "Glass Fragments"}

        Returns:
            bool: True если условие выполнено, False иначе

        Example:
            condition = {"type": "user_has_item", "item_name": "Blackmail Note"}
            is_met = await check_fact_condition(pool, user_id, story_id, condition)
        """

        try:
            condition_type = condition.get('type')

            if condition_type == 'user_has_item':
                # Проверить есть ли item в inventory
                item_name = condition.get('item_name')

                # Используем правильную архитектуру:
                # c_inventory в t_story_user_progress (JSONB массив item_id)
                query = """
                    SELECT EXISTS (
                        SELECT 1
                        FROM t_story_user_progress p
                        WHERE p.c_user_id = $1
                          AND p.c_story_id = $2
                          AND p.c_inventory @> (
                              SELECT jsonb_build_array(c_item_id)
                              FROM t_story_items
                              WHERE c_story_id = $2
                                AND c_name = $3
                              LIMIT 1
                          )
                    )
                """

                result = await pgDB.fExec_SelectQuery_args(
                    self.pool_base, query, user_id, story_id, item_name
                )

                has_item = result[0][0] if result else False

                logger.debug(
                    f"Condition user_has_item '{item_name}': {has_item}"
                )

                return has_item

            elif condition_type == 'user_gave_item':
                # TODO: Функционал "отдать предмет NPC" не реализован
                item_name = condition.get('item_name')

                logger.warning(
                    f"Condition 'user_gave_item' NOT IMPLEMENTED. "
                    f"Item: '{item_name}'. Returning False."
                )

                return False

            elif condition_type == 'user_has_not_given_item':
                # TODO: Функционал "отдать предмет NPC" не реализован
                # Инверсия user_gave_item (который всегда False)
                item_name = condition.get('item_name')

                logger.debug(
                    f"Condition user_has_not_given_item '{item_name}': True "
                    f"(NOT IMPLEMENTED - always returns True)"
                )

                return True

            else:
                logger.warning(
                    f"Unknown condition type: {condition_type}"
                )
                return False

        except Exception as e:
            logger.error(
                f"Error checking fact condition {condition}: {e}",
                exc_info=True
            )
            return False

    async def get_revealed_facts(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,
            npc_id: int
    ) -> List[int]:
        """
        Получить список индексов раскрытых фактов для NPC

        Args:
            pool: Database connection pool
            user_id: ID пользователя
            story_id: ID истории
            scene_id: ID сцены
            npc_id: ID NPC

        Returns:
            List[int]: Список индексов фактов [0, 1, 2, 3, ...]
            Пустой список если ничего не раскрыто

        Example:
            revealed = await get_revealed_facts(pool, 372671079, 23, 75, 89)
            # → [0, 1, 2]
        """

        try:
            # Сначала получить progress_id
            progress_query = """
                SELECT c_progress_id
                FROM t_story_user_progress
                WHERE c_user_id = $1 AND c_story_id = $2
            """

            progress_result = await pgDB.fExec_SelectQuery_args(
                self.pool_base, progress_query, user_id, story_id
            )

            if not progress_result or not progress_result[0][0]:
                logger.warning(
                    f"No progress found for user {user_id} story {story_id}"
                )
                return []

            progress_id = progress_result[0][0]

            # Получить revealed facts
            facts_query = """
                SELECT c_fact_index
                FROM t_story_user_revealed_facts
                WHERE c_progress_id = $1
                  AND c_scene_id = $2
                  AND c_npc_id = $3
                ORDER BY c_revealed_at
            """

            result = await pgDB.fExec_SelectQuery_args(
                self.pool_base, facts_query, progress_id, scene_id, npc_id
            )

            if not result:
                return []

            # Извлечь индексы из результата
            revealed_indexes = [row[0] for row in result]

            logger.info(
                f"Retrieved {len(revealed_indexes)} revealed facts for "
                f"user {user_id} story {story_id} scene {scene_id} NPC {npc_id}: "
                f"{revealed_indexes}"
            )

            return revealed_indexes

        except Exception as e:
            logger.error(
                f"Error getting revealed facts for user {user_id} "
                f"story {story_id} scene {scene_id} NPC {npc_id}: {e}",
                exc_info=True
            )
            return []

    def format_facts_for_prompt(
            self,
            facts_to_reveal: List[Dict[str, Any]],
            revealed_facts_indexes: List[int],
            all_facts: List[Dict[str, Any]],
            uncompleted_obj=''
    ) -> str:
        """
        Форматировать facts для AI промпта

        Args:
            facts_to_reveal: Список фактов для раскрытия (из select_facts_for_response)
            revealed_facts_indexes: Индексы уже раскрытых фактов
            all_facts: Все факты из information_pool['facts']

        Returns:
            str: Отформатированный текст для промпта

        Example:
            prompt_text = format_facts_for_prompt(
                selected_facts,
                revealed_indexes,
                all_facts
            )
        """
        prompt_parts = []

        # FACTS TO REVEAL
        if facts_to_reveal:
            varStr = '''

            FACTS TO REVEAL IN THIS RESPONSE (if user asks):
            Only reveal facts when user asks questions or shows specific interest.
            For GREETING intent: Use NO facts (facts_used: [])
            For INFORMATION_REQUEST: Choose 1-2 relevant facts
            CRITICAL: When you use a fact, you MUST include its INDEX in 'facts_used' array.

            '''
            prompt_parts.append(varStr)

            for fact in facts_to_reveal:
                # prompt_parts.append(f"• {fact['text']}")
                prompt_parts.append(f"- [INDEX {fact['index']}] {fact['text']}")

        # FACTS ALREADY REVEALED
        if revealed_facts_indexes:
            prompt_parts.append("\n\nFACTS ALREADY REVEALED (do NOT repeat):\n")

            for idx in revealed_facts_indexes:
                if idx < len(all_facts):
                    fact_text = all_facts[idx].get('text', '')
                    prompt_parts.append(f"• {fact_text}")

        uncompleted_obj_str = ''
        if uncompleted_obj:
            uncompleted_obj_str = ' '.join(uncompleted_obj)
            uncompleted_obj_str = f'''
            SCENE OBJECTIVES (for internal guidance only):
            {uncompleted_obj_str}

            Use objectives ONLY to:
            - classify OBJECTIVE_PROGRESS vs OFFTOPIC
            - choose natural topics to continue
            - NEVER mention objectives explicitly

            '''

        prompt_parts.append(uncompleted_obj_str)

        return "\n".join(prompt_parts)

    def __________ext_f(self): pass

    async def generate_scene_description(
            self,
            scene_id: int,
            story_id: int,
            user_progress: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Сгенерировать описание сцены с учетом прогресса пользователя

        Args:
            scene_id: ID сцены
            story_id: ID истории
            user_progress: Прогресс пользователя

        Returns:
            {
                'location_description': "Dynamic description based on progress",
                'location_description_trs': {"ru": "Russian translation"},
                'npcs_present': [...],
                'items_available': [...]
            }
        """

        # Получаем базовое описание сцены из БД
        query = """
            SELECT 
                c_scene_name,
                c_location_description,
                c_location_description_trs,
                c_objective,
                c_objective_trs,
                c_npcs_present,
                c_items_available, 
                c_scene_id,
                c_scene_name_trs, 
                c_detailed_objectives,
                c_scene_context,
                c_is_ending,
                c_ending_type
            FROM t_story_scenes
            WHERE c_scene_id = $1 AND c_story_id = $2
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            query,
            scene_id,
            story_id
        )

        if not result:
            logger.error(f"Scene {scene_id} not found")
            return None

        row = result[0]

        # Парсим JSONB поля
        location_description_trs = row[2]
        if isinstance(location_description_trs, str):
            location_description_trs = json.loads(location_description_trs) if location_description_trs else {}

        objective_trs = row[4]
        if isinstance(objective_trs, str):
            objective_trs = json.loads(objective_trs) if objective_trs else {}

        npcs_present = row[5]
        if isinstance(npcs_present, str):
            npcs_present = json.loads(npcs_present) if npcs_present else []

        items_available = row[6]
        if isinstance(items_available, str):
            items_available = json.loads(items_available) if items_available else []

        detailed_objectives = row[9]
        if isinstance(detailed_objectives, str):
            detailed_objectives = json.loads(detailed_objectives)

        scene_context = row[10]
        if isinstance(scene_context, str):
            scene_context = json.loads(scene_context)

        # Получаем инвентарь пользователя
        user_inventory = user_progress.get('inventory', [])

        # Фильтруем items - показываем только те, которых еще нет в инвентаре
        items_to_show = [item_id for item_id in items_available if item_id not in user_inventory]

        return {
            'scene_name': row[0],
            'location_description': row[1],
            'location_description_trs': location_description_trs,
            'objective': row[3],
            'objective_trs': objective_trs,
            'npcs_present': npcs_present,
            'items_available': items_to_show,
            'user_inventory': user_inventory,
            'scene_id': row[7],     #new
            'story_id': story_id,
            'scene_name_trs': row[8],       #new
            'detailed_objectives': detailed_objectives, #new
            'scene_context': scene_context, #new
            'is_ending': row[11], #new
            'ending_type': row[12]  #new
        }

    async def save_interaction(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,
            interaction_type: str,
            user_input: str,
            user_input_type: str,
            target_npc_id: Optional[int],
            ai_response: str,
            correction: str,
            ai_response_trs: dict = None,
            correction_trs: dict = None,
            audio_filename: str = None,
            target_item_id: Optional[int] = None  #  ДОБАВИТЬ только это
    ):
        """
        Сохранить взаимодействие в БД

        Args:
            ...existing args...
            target_item_id: ID item (для interaction_type='item_use')
        """

        query = """
            INSERT INTO t_story_user_interactions
                (c_user_id, c_story_id, c_scene_id, c_interaction_type,
                 c_user_input, c_user_input_type, c_target_npc_id, c_target_item_id,
                 c_ai_response, c_ai_response_trs, c_correction, c_correction_trs,
                 c_audio_filename)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            RETURNING c_interaction_id
        """

        result = await pgDB.fFetch_InsertQuery_args(
            self.pool_base,
            query,
            user_id,
            story_id,
            scene_id,
            interaction_type,
            user_input,
            user_input_type,
            target_npc_id,
            target_item_id,  #  Добавлено в правильную позицию
            ai_response,
            json.dumps(ai_response_trs) if ai_response_trs else None,
            correction,
            json.dumps(correction_trs) if correction_trs else None,
            audio_filename
        )

        if result:
            interaction_id = result[0][0] if isinstance(result[0], tuple) else result[0]
            logger.info(f"Saved interaction {interaction_id} for user {user_id}")
        else:
            logger.error("Failed to save interaction")

    def __________check_completion(self): pass

    async def check_objective_completion(
            self,
            scene_id: int,
            story_id: int,
            user_id: int,
            recent_interaction: Dict[str, Any]
    ) -> bool:
        """
        Проверить выполнена ли цель сцены

        Новая логика с поддержкой detailed_objectives!
        """

        # Получаем сцену с objectives
        query = """
            SELECT c_success_conditions, c_detailed_objectives, c_scene_context 
            FROM t_story_scenes
            WHERE c_scene_id = $1 AND c_story_id = $2
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            query,
            scene_id,
            story_id
        )

        #logger.info(f'------------check_objective_completion>>>>result:{result}')

        if not result:
            return False

        success_conditions = result[0][0]
        detailed_objectives = result[0][1]
        scene_context_json = result[0][2]

        if isinstance(success_conditions, str):
            success_conditions = json.loads(success_conditions)
        if isinstance(detailed_objectives, str):
            detailed_objectives = json.loads(detailed_objectives)

        # Parse scene_context
        if isinstance(scene_context_json, str):
            scene_context_json = json.loads(scene_context_json) if scene_context_json else {}
        elif scene_context_json is None:
            scene_context_json = {}

        # Создать scene_context dict для fact-based checking
        scene_context_for_facts = {
            'scene_id': scene_id,
            'npc_behavior_overrides': scene_context_json.get('npc_behavior_overrides', {}),
            'objective_completion_hints': scene_context_json.get('objective_completion_hints', {}),
        }

        condition_type = success_conditions.get('type')

        # === НОВАЯ ЛОГИКА: objectives_complete ===
        if condition_type == 'objectives_complete':
            objectives = detailed_objectives.get('objectives', [])
            min_objectives = success_conditions.get('min_objectives', len(objectives))

            logger.info(f"=== CHECK_OBJECTIVE_COMPLETION: scene_id={scene_id} ===")
            logger.info(f"Total objectives: {len(objectives)}")
            for obj in objectives:
                logger.info(f"  - {obj.get('id')}: type={obj.get('type')}, target={obj.get('target')}")

            # Подсчитываем сколько objectives выполнено
            completed_count = 0

            for obj in objectives:
                logger.info(f"\n=== Checking objective: {obj.get('id')} ===")
                if await self._check_single_objective(
                        obj, scene_id, story_id, user_id, recent_interaction, scene_context_for_facts
                ):
                    completed_count += 1
                    logger.info(f"+++ Objective {obj.get('id')} is COMPLETED")
                else:
                    logger.info(f"--- Objective {obj.get('id')} is NOT completed")

            # Проверяем выполнено ли достаточно objectives
            if completed_count >= min_objectives:
                logger.info(f"Scene {scene_id}: {completed_count}/{len(objectives)} objectives completed")
                return True

            # FALLBACK: Проверяем количество сообщений с target NPC
            min_messages = success_conditions.get('min_messages_with_target', 10)
            target_npc = success_conditions.get('target')

            if target_npc:
                messages_count = await self._count_messages_with_npc(
                    user_id, story_id, scene_id, target_npc
                )

                if messages_count >= min_messages:
                    logger.info(f"Scene {scene_id}: Fallback - {messages_count} messages with {target_npc}")
                    return True

            return False

        # === СТАРАЯ ЛОГИКА (для backwards compatibility) ===
        elif condition_type == 'dialogue_complete':
            keywords = success_conditions.get('keywords', [])
            target_npc = success_conditions.get('target')

            if not keywords:
                return True

            # Получаем весь текст диалога в сцене
            full_dialogue = await self._get_full_dialogue_text(
                user_id, story_id, scene_id
            )

            keywords_found = sum(1 for kw in keywords if kw.lower() in full_dialogue.lower())
            return keywords_found >= len(keywords) / 2

        elif condition_type == 'item_obtained':
            target_item_name = success_conditions.get('target')

            item_manager = ItemManager((self.pool_base, self.pool_log))
            inventory = await item_manager.get_user_inventory(user_id, story_id)

            for item in inventory:
                if item['name'] == target_item_name:
                    return True
            return False

        elif condition_type == 'item_use':
            return recent_interaction.get('interaction_type') == 'item_use'

        elif condition_type == 'action_performed':
            return recent_interaction.get('interaction_type') == 'action'

        return False

    async def _check_single_objective(
            self,
            objective: Dict[str, Any],
            scene_id: int,
            story_id: int,
            user_id: int,
            recent_interaction: Dict[str, Any],
            scene_context: Dict[str, Any] = None,
            force_recheck: bool = False
    ) -> bool:
        """
        Проверить выполнение одного objective

        Args:
            objective: Данные objective
            scene_id: ID сцены
            story_id: ID истории
            user_id: ID пользователя
            recent_interaction: Последнее взаимодействие
            force_recheck: Принудительно перепроверить (игнорировать кэш)

        Returns:
            True если objective выполнен
        """

        obj_id = objective.get('id')
        obj_type = objective.get('type')

        # === ШАГ 1: Проверить кэш в БД ===
        if not force_recheck:
            cached_status = await self._get_objective_status_from_db(
                user_id, story_id, scene_id, obj_id
            )

            if cached_status is not None:
                logger.debug(f"Objective {obj_id} status from cache: {cached_status}")
                return cached_status

        # === ШАГ 2: Вычислить статус (если нет в кэше) ===
        is_completed = False
        completion_method = "unknown"

        if obj_type == 'dialogue':
            # Простая проверка - был ли диалог
            target = objective.get('target')
            messages_count = await self._count_messages_with_npc(
                user_id, story_id, scene_id, target
            )
            is_completed = messages_count >= 1
            completion_method = "dialogue_count"



        elif obj_type == 'information':
            keywords = objective.get('keywords', [])
            keywords_lower = [kw.lower() for kw in keywords]

            logger.info(f'-----------keywords:{keywords}')

            # ========================================
            # FAST PATH: Keyword check
            # ========================================
            keyword_check = False

            if scene_context:
                keyword_check = await self._check_keyword_completion(
                    objective=objective,
                    recent_interaction=recent_interaction,  # ← Передаем recent_interaction!
                    scene_context=scene_context
                )
            logger.info(f'-----------keyword_check:{keyword_check}')
            # ========================================

            # ========================================
            # Fact-based check
            # ========================================
            fact_check = False

            if not keyword_check and scene_context:
                fact_check = await self.check_objective_by_facts(
                    user_id=user_id,
                    story_id=story_id,
                    scene_id=scene_id,
                    objective_id=obj_id,
                    scene_context=scene_context
                )
            logger.info(f'-----------fact_check:{fact_check}')
            # ========================================

            # ========================================
            # SLOW PATH: AI check
            # ========================================
            ai_check = False

            if not keyword_check and not fact_check:

                if recent_interaction.get('interaction_type') == 'item_use':
                    item_used = recent_interaction.get('item_name', '').lower()
                    if item_used and item_used in keywords_lower:
                        logger.info(f"Information objective completed via item_use: '{item_used}'")
                        ai_check = True
                        completion_method = "item_use_action"
                    else:
                        ai_check = await self._check_information_objective_with_ai(
                            objective, user_id, story_id, scene_id
                        )
                        completion_method = "ai_analysis"
                else:
                    ai_check = await self._check_information_objective_with_ai(
                        objective, user_id, story_id, scene_id
                    )
                    completion_method = "ai_analysis"
            # ========================================

            # ========================================
            # OR logic: keyword OR facts OR AI
            # ========================================
            if keyword_check:
                is_completed = True
                completion_method = "keyword_match"
                logger.info(f"Objective {obj_id} completed by KEYWORD")
            elif fact_check:
                is_completed = True
                completion_method = "fact_based"
                logger.info(f"Objective {obj_id} completed by FACTS")
            elif ai_check:
                is_completed = True
                logger.info(f"Objective {obj_id} completed by AI")
            else:
                is_completed = False
                logger.info(
                    f"Objective {obj_id} NOT completed "
                    f"(keyword={keyword_check}, fact={fact_check}, ai={ai_check})"
                )
            # ========================================

        elif obj_type == 'item':

            target = objective.get('target')

            logger.info(f"=== ITEM OBJECTIVE CHECK ===")
            logger.info(f"Objective ID: {obj_id}")
            logger.info(f"Target item name: {target}")

            #  ИСПРАВЛЕНИЕ: Для type='item' достаточно иметь в инвентаре
            is_completed = await self._check_item_in_inventory(user_id, story_id, target)
            completion_method = "inventory_check"

            logger.info(f"Item in inventory: {is_completed}")
            logger.info(f"Will save to DB: {is_completed}")


        elif obj_type == 'item_use':

            # Проверить использование

            target = objective.get('target')

            # Поддержка обоих форматов: старый (item_name) и новый (target для контейнеров)

            item_used_on = recent_interaction.get('target')  # На что используем

            item_used_name = recent_interaction.get('item_name') or recent_interaction.get(
                'item_used')  # Что используем

            is_completed = (
                    recent_interaction.get('interaction_type') == 'item_use' and
                    (item_used_on == target or item_used_name == target)            # target может быть либо контейнер, либо сам item
            )

            completion_method = "interaction_check"


        elif obj_type == 'action':
            #is_completed = recent_interaction.get('interaction_type') == 'action'
            #completion_method = "interaction_check"

            # Explicit action (like look_around, search, etc.)
            if recent_interaction.get('interaction_type') == 'action':
                is_completed = True
                completion_method = "interaction_check"

            #  НОВОЕ: Item use тоже может быть action (атака оружием, использование ключа)
            elif recent_interaction.get('interaction_type') == 'item_use':
                # Проверить, что это действие
                obj_description = objective.get('description', '').lower()
                user_input = recent_interaction.get('user_input', '').lower()

                # Ключевые слова для действий
                action_keywords = ['attack', 'hit', 'fight', 'use', 'open', 'unlock', 'break', 'strike']

                # Если в описании objective или действии есть action keywords
                if any(keyword in obj_description for keyword in action_keywords) or \
                        any(keyword in user_input for keyword in action_keywords):
                    is_completed = True
                    completion_method = "item_use_as_action"
                    logger.info(f" Action objective via item_use: {user_input}")
                else:
                    is_completed = False
                    completion_method = "item_use_not_action"

            # Dialogue-based action (like "note down", "remember", etc.)
            elif recent_interaction.get('interaction_type') == 'dialogue':
                # Use AI to check if action was accomplished through dialogue
                is_completed = await self._check_information_objective_with_ai(
                    objective, user_id, story_id, scene_id
                )
                completion_method = "ai_analysis"
            else:
                is_completed = False
                completion_method = "no_match"

        # === ШАГ 3: Сохранить результат в БД ===
        if is_completed:
            await self._save_objective_status_to_db(
                user_id, story_id, scene_id, obj_id,
                completed=True,
                completion_method=completion_method
            )

            # ⭐ НОВОЕ: Раскрыть связанный item если есть reveals_item
            reveals_item = objective.get('reveals_item')
            if reveals_item:
                await self._reveal_item_for_user(
                    user_id,
                    story_id,
                    scene_id,
                    reveals_item
                )
                logger.info(f"Revealed item '{reveals_item}' for user {user_id} in scene {scene_id}")

        return is_completed




    async def _get_objective_status_from_db(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,
            obj_id: str
    ) -> Optional[bool]:
        """
        Получить статус objective из БД (кэш)

        Returns:
            True/False если есть в кэше, None если нет
        """

        query = """
            SELECT c_scene_progress
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
            return None

        scene_progress = result[0][0]
        if isinstance(scene_progress, str):
            scene_progress = json.loads(scene_progress)

        # Формат: {"scene_9": {"objectives": {"obj_1": {"completed": true}}}}
        scene_key = f"scene_{scene_id}"
        scene_data = scene_progress.get(scene_key, {})
        objectives_data = scene_data.get('objectives', {})
        obj_data = objectives_data.get(obj_id, {})

        return obj_data.get('completed')

    async def _save_objective_status_to_db(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,
            obj_id: str,
            completed: bool,
            completion_method: str
    ):
        """
        Сохранить статус objective в БД
        """

        # Получаем текущий scene_progress
        query = """
            SELECT c_scene_progress
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
            logger.warning(f"No progress record for user {user_id}, story {story_id}")
            return

        scene_progress = result[0][0]
        if isinstance(scene_progress, str):
            scene_progress = json.loads(scene_progress)

        # Обновляем структуру
        scene_key = f"scene_{scene_id}"

        if scene_key not in scene_progress:
            scene_progress[scene_key] = {"objectives": {}}

        if "objectives" not in scene_progress[scene_key]:
            scene_progress[scene_key]["objectives"] = {}

        # Сохраняем статус objective
        scene_progress[scene_key]["objectives"][obj_id] = {
            "completed": completed,
            "completed_at": datetime.now().isoformat() if completed else None,
            "completion_method": completion_method
        }

        # Обновляем в БД
        update_query = """
            UPDATE t_story_user_progress
            SET c_scene_progress = $1::jsonb,
                c_last_interaction_at = CURRENT_TIMESTAMP
            WHERE c_user_id = $2 AND c_story_id = $3
        """

        await pgDB.fExec_UpdateQuery_args(
            self.pool_base,
            update_query,
            json.dumps(scene_progress),
            user_id,
            story_id
        )

        logger.info(f"Saved objective {obj_id} status: {completed} (method: {completion_method})")

    async def _check_keyword_completion(
            self,
            objective: Dict[str, Any],
            recent_interaction: Dict[str, Any],  # ← Используем это вместо npc_name!
            scene_context: Dict[str, Any]
    ) -> bool:
        """
        FAST PATH: Проверить завершение objective через keywords

        Returns:
            True если keyword найден (objective completed)
            False если keyword не найден (нужен AI analysis)
        """

        obj_id = objective.get('id')

        logger.info(f'----------obj_id:{obj_id}')

        # Получить hints из scene_context
        completion_hints = scene_context.get('objective_completion_hints', {})

        logger.info(f'----------completion_hints:{completion_hints}')

        if obj_id not in completion_hints:
            # Нет hints → пропустить Fast Path
            return False

        hint = completion_hints[obj_id]
        logger.info(f'----------hint:{hint}')

        if hint.get('type') != 'keyword_match':
            # Не keyword_match → пропустить
            return False

        logger.info(f"[FAST PATH] Checking keywords for {obj_id}")

        keywords = hint.get('keywords', [])
        logger.info(f'----------keywords:{keywords}')
        match_type = hint.get('match_type', 'any')
        case_sensitive = hint.get('case_sensitive', False)

        # Получить последний AI response из recent_interaction
        last_ai_response = recent_interaction.get('ai_response', '')

        logger.info(f'----------recent_interaction:{recent_interaction}')
        logger.info(f'----------last_ai_response:{last_ai_response}')

        if not last_ai_response:
            logger.info(f"[FAST PATH] No AI response in recent_interaction")
            return False

        # Подготовить текст
        if case_sensitive:
            message_text = last_ai_response
            keywords_to_check = keywords
        else:
            message_text = last_ai_response.lower()
            keywords_to_check = [kw.lower() for kw in keywords]

        # Проверить keywords
        if match_type == 'any':
            matches = [kw for kw in keywords_to_check if kw in message_text]
            if matches:
                logger.info(f"[FAST PATH SUCCESS] Keyword found: {matches[0]}")
                return True

        elif match_type == 'all':
            matches = [kw for kw in keywords_to_check if kw in message_text]
            if len(matches) == len(keywords_to_check):
                logger.info(f"[FAST PATH SUCCESS] All keywords found")
                return True

        logger.info(f"[FAST PATH MISS] No keyword match")
        return False



    async def _check_information_objective_with_ai(
            self,
            objective: Dict[str, Any],
            user_id: int,
            story_id: int,
            scene_id: int
    ) -> bool:
        """
        Проверить information/dialogue objective через AI анализ

        ВАЖНО: AI должен быть СТРОГИМ - objective выполнен только если
        пользователь РЕАЛЬНО достиг описанной цели, не просто начал диалог.
        """

        obj_description = objective.get('description', '')
        obj_type = objective.get('type', 'information')
        target_npc = objective.get('target')



        # Получить весь диалог в сцене
        full_dialogue = await self._get_full_dialogue_text(
            user_id, story_id, scene_id
        )

        if not full_dialogue:
            return False

        # Промпт для AI

        logger.info(f'------obj_description:{obj_description}')
        logger.info(f'------target_npc:{target_npc}')
        logger.info(f'------obj_type:{obj_type}')
        logger.info(f'------full_dialogue:{full_dialogue}')

        prompt_old = f"""You are a STRICT objective completion checker for an ESL learning game.

        OBJECTIVE TO CHECK:
        - Description: "{obj_description}"
        - Expected NPC: {target_npc if target_npc else "any"}
        - Type: {obj_type}

        DIALOGUE TRANSCRIPT:
        {full_dialogue}

        TASK:
        Determine if the user FULLY COMPLETED this objective.

        CRITICAL RULES:
        1. Greetings alone DO NOT complete objectives
           - "Hi Anna" ≠ "arrange a date"
           - "Hello Ben" ≠ "refuse to work"

        2. Pay attention to MEANINGFUL INFORMATION EXCHANGE
           - Asking "How are you?" ≠ discussing specific topic
           - Starting conversation ≠ completing objective
           - Brief mention without explanation ≠ detailed discussion

        3. Objective is completed if:
           - User explicitly addressed the objective's goal
           - Conversation provided the specific information requested
           - Clear outcome matching what was asked for
           - Repetition of same phrase ≠ detailed explanation

       
        EXAMPLES:

        Objective: "Arrange a date with Anna"
        - "Hi Anna, how are you?" -> NO (just greeting)
        - "Anna, want to grab coffee on Saturday?" -> YES (specific plan)
        - "We should meet up sometime" -> NO (too vague)

        Objective: "Refuse to work with Ben"
        - "Hi Ben" -> NO (just greeting)
        - "Ben, I can't work this weekend" -> YES (clear refusal)

        Objective: "Ask Lenny about his plans"
        - "Hi Lenny" -> NO (just greeting)
        - "Lenny, what are you doing this weekend?" -> YES (asked about plans)
        - "How are you Lenny?" -> NO (general question)

        Objective: "Ask Davies about locked room and learn how it was secured"
        - Davies: "The room is locked" (repeated 5 times) -> NO (mentioned but not explained HOW)
        - Davies: "Door secured from inside, key in lock, windows sealed" -> YES (detailed explanation of HOW)
        
        NOW ANALYZE:
        Based on the dialogue, did the user FULLY COMPLETE the objective?
        
        RESPONSE FORMAT (MANDATORY):
        <YES or NO>;<Brief explanation in 1 sentence>
        
        EXAMPLES:
        YES;User asked about weekend plans and received detailed response about hiking
        NO;Only greeted NPC without discussing the objective topic
        YES;NPC explained the locked room mechanism with specific details
        NO;Topic mentioned but no actual information exchange occurred
        
        """


        prompt = f"""
        You are an objective completion checker for an ESL learning game.
        
        OBJECTIVE TO CHECK:
        - Description: "{obj_description}"
        - Expected NPC: {target_npc if target_npc else "any"}
        - Type: {obj_type}
        
        DIALOGUE TRANSCRIPT:
        {full_dialogue}
        
        TASK:
        Determine if the user COMPLETED this objective through meaningful conversation.
        
        CRITICAL PRINCIPLES:
        
        1. FOCUS ON OUTCOME, NOT DIRECTNESS
           - Did user GET the information requested?
           - Did user ACHIEVE the goal stated in objective?
           - Natural conversation flow is ACCEPTABLE
        
        2. NATURAL CONVERSATION IS VALID
           - Small talk before main topic = OK
           - Brief diversions (news, weather) = OK
           - Multiple exchanges to reach goal = OK
           - User confirming understanding = POSITIVE signal
        
        3. ESL-FRIENDLY INTERPRETATION
           - Focus on INTENT over perfect grammar
           - "what you do today?" = valid question about plans
           - "you plans?" = valid (simplified but clear)
           - Grammar errors DO NOT disqualify objective completion
        
        4. GREETINGS ALONE ARE NOT ENOUGH
           - "Hi Anna" alone ≠ "arrange a date"
           - BUT "Hi Anna, coffee Saturday?" = arranging date ✓
        
        COMPLETION CRITERIA:
        
        For INFORMATION objectives (asking/learning):
        ✓ User asked question related to objective topic
        ✓ NPC provided relevant information
        ✓ Information exchange occurred (even through natural conversation flow)
        
        For ACTION objectives (arrange/refuse/convince):
        ✓ User made request/statement related to objective
        ✓ Clear outcome achieved (even if through multiple exchanges)
        
        EXAMPLES:
        
        Example 1 - Natural Conversation Flow (SHOULD PASS):
        Objective: "Ask Lenny about his plans"
        Dialogue:
        - User: "what are the plans for today?"
        - Lenny: "Did you see the news? Explosion... Anyway, wanna play Call of Duty?"
        - User: "No, what explosion?"
        - Lenny: "Don't know much. Jack's party tonight!"
        - User: "Cool! So console then Jack's?"
        - Lenny: "Yeah! And beers, gaming session with Mike and Tom"
        
        Analysis: YES
        Reason: User asked about plans (line 1), received multiple plans through natural conversation (Call of Duty, Jack's party, beers, gaming session), and confirmed understanding (line 5). Diversion to news is natural conversation flow, not failure.
        
        Example 2 - Just Greeting (SHOULD FAIL):
        Objective: "Arrange a date with Anna"
        Dialogue:
        - User: "Hi Anna, how are you?"
        - Anna: "I'm fine, thanks"
        - User: "That's good"
        
        Analysis: NO
        Reason: Only greeting, no attempt to arrange date.
        
        Example 3 - ESL Grammar Errors (SHOULD PASS):
        Objective: "Ask Ben about work project"
        Dialogue:
        - User: "Ben, you can tell about project?" (grammar error but clear intent)
        - Ben: "Sure! We're building new API for mobile app..."
        - User: "when finish?" (simplified but understandable)
        - Ben: "Should be done by March"
        
        Analysis: YES
        Reason: Despite grammar errors, user clearly asked about project and received information. Intent clear, objective achieved.
        
        Example 4 - Multiple Exchanges (SHOULD PASS):
        Objective: "Refuse to work with Ben"
        Dialogue:
        - User: "Hi Ben"
        - Ben: "Can you work Saturday?"
        - User: "Sorry, I have plans"
        - Ben: "I'll pay overtime?"
        - User: "No, I really can't"
        
        Analysis: YES
        Reason: User successfully refused work through multiple exchanges. Natural negotiation, clear outcome.
        
        Example 5 - Vague Response (SHOULD FAIL):
        Objective: "Learn how the room was locked"
        Dialogue:
        - User: "How was room locked?"
        - Davies: "It was locked"
        - Davies: "Yes, the room was locked"
        - Davies: "Locked from inside"
        
        Analysis: NO
        Reason: Repetition without EXPLANATION. User asked HOW but didn't learn the mechanism/method.
        
        NOW ANALYZE:
        
        Based on dialogue, did user COMPLETE the objective?
        
        Consider:
        1. Did user make attempt related to objective? (even with errors)
        2. Did meaningful information exchange occur?
        3. Was goal achieved? (even through natural conversation)
        4. Did user show understanding? (confirmations, follow-ups)
        
        RESPONSE FORMAT (MANDATORY):
        <YES or NO>;<Brief explanation focusing on outcome>
        
        Good explanations:
        - YES;User asked about plans and learned about Call of Duty, party, beers, and gaming session
        - YES;User refused work through multiple exchanges, clear refusal achieved despite negotiation
        - NO;Only greeting occurred, no information about plans discussed
        - YES;Despite grammar errors, user clearly asked about project and received detailed response
        
        Bad explanations:
        - NO;Conversation diverted to unrelated topics
        - NO;User did not explicitly use exact words from objective
        - NO;Grammar errors in user messages

        """


        #backup
        '''
        CRITICAL RULES:
        1. Greetings alone DO NOT complete objectives
           - "Hi Anna" ≠ "arrange a date"
           - "Hello Ben" ≠ "refuse to work"

        2. Mentioning a topic is NOT enough - require MEANINGFUL INFORMATION EXCHANGE
           - Asking "How are you?" ≠ discussing specific topic
           - Starting conversation ≠ completing objective
           - Brief mention without explanation ≠ detailed discussion

        3. Objective is ONLY completed if:
           - User explicitly addressed the objective's goal
           - Conversation provided the specific information requested
           - Clear outcome matching what was asked for

        4. For complex objectives with "and learn" or "and understand":
           - Check if the information was actually EXPLAINED, not just mentioned
           - Repetition of same phrase ≠ detailed explanation
           - If in doubt, answer NO (be conservative)
        '''


        try:
            # Вызов AI (используй свою функцию)
            response = await myF.afSendMsg2AI(
                prompt,
                self.pool_base,
                user_id,
                iModel=0,  # GPT-4 для точного анализа
                toggleParam=1,  # Low temperature
                systemPrompt="You are a STRICT objective completion analyzer for an educational game. Be conservative - only answer YES if the objective was truly completed with specific evidence. Respond only with YES or NO."
            )

            response = response.strip().upper()

            # Проверка формата
            if ';' not in response:
                logger.warning(f"AI response in wrong format (missing ';'): {response}")
                # Fallback на старую логику
                if "YES" in response.upper():
                    logger.info(f"AI confirmed (fallback parsing): {obj_description}")
                    return True
                else:
                    logger.info(f"AI denied (fallback parsing): {obj_description}")
                    return False

            # Парсинг формата "YES;explanation" или "NO;explanation"
            parts = response.split(';', 1)  # Разделить максимум на 2 части
            decision = parts[0].strip().upper()
            explanation = parts[1].strip() if len(parts) > 1 else "No explanation provided"

            if "YES" in decision:
                logger.info(f"AI confirmed objective completion: {obj_description}")
                logger.info(f"   Reason: {explanation}")
                return True
            else:
                logger.info(f"AI denied objective completion: {obj_description}")
                logger.info(f"   Reason: {explanation}")
                return False



        except Exception as e:
            logger.error(f"Error in AI objective check: {e}")
            logger.warning(f"Objective '{obj_description}' marked NOT COMPLETED (AI check failed)")
            return False  # Conservative approach - лучше false negative чем false positive

    async def check_objective_by_facts(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,
            objective_id: str,
            scene_context: Dict[str, Any]
    ) -> Optional[bool]:
        """
        Проверить objective по revealed facts

        Логика:
        1. Найти все facts с required_for_objectives = [objective_id]
        2. Для каждого NPC получить revealed_facts
        3. Проверить все ли required facts revealed
        4. Return True если все раскрыты

        Args:
            pool: Database connection pool
            user_id: ID пользователя
            story_id: ID истории
            scene_id: ID сцены
            objective_id: ID objective (например, "obj_2")
            scene_context: Контекст сцены (из _get_scene_context)

        Returns:
            True - если все required facts revealed
            False - если не все required facts revealed
            None - если objective не использует facts

        Example:
            # objective "obj_2" требует facts [0, 1, 3] от Davies
            result = await check_objective_by_facts(
                pool, user_id, story_id, scene_id, "obj_2", scene_context
            )
            # → True если user раскрыл facts 0, 1 и 3 с Davies
        """
        try:
            # Получить npc_behavior_overrides
            npc_overrides = scene_context.get('npc_behavior_overrides', {})

            if not npc_overrides:
                logger.debug(f"No npc_behavior_overrides in scene_context")
                return None

            # Найти required facts для objective
            required_facts = []  # [(npc_id, fact_index), ...]

            for npc_name, npc_data in npc_overrides.items():
                info_pool = npc_data.get('information_pool', {})

                if not info_pool:
                    continue  # NPC не использует information_pool

                facts = info_pool.get('facts', [])

                for idx, fact in enumerate(facts):
                    objectives_list = fact.get('required_for_objectives', [])

                    if objective_id in objectives_list:
                        # Этот fact required для objective
                        npc_id = await self.get_npc_id_by_name(npc_name, scene_id)

                        if npc_id:
                            required_facts.append((npc_id, idx))
                            logger.debug(
                                f"Objective {objective_id} requires fact {idx} "
                                f"from {npc_name} (npc_id={npc_id})"
                            )

            if not required_facts:
                logger.debug(
                    f"Objective {objective_id} has no required facts "
                    f"(not fact-based)"
                )
                return None  # Objective не использует facts

            logger.info(
                f"Checking objective {objective_id}: "
                f"requires {len(required_facts)} facts"
            )

            # Проверить все ли required facts revealed
            for npc_id, fact_idx in required_facts:
                revealed = await self.get_revealed_facts(
                    user_id, story_id, scene_id, npc_id
                )

                if fact_idx not in revealed:
                    logger.info(
                        f"Objective {objective_id}: fact {fact_idx} "
                        f"from NPC {npc_id} NOT revealed yet"
                    )
                    return False  # Не все required facts revealed

            logger.info(
                f"Objective {objective_id}: all {len(required_facts)} "
                f"required facts revealed!"
            )
            return True  # Все required facts revealed

        except Exception as e:
            logger.error(
                f"Error checking objective {objective_id} by facts: {e}",
                exc_info=True
            )
            return None  # Ошибка - вернуть None (fallback на AI)

    async def get_npc_id_by_name(
            self,
            npc_name: str,
            scene_id: int
    ) -> Optional[int]:
        """
        Получить NPC ID по имени

        Args:
            pool: Database connection pool
            npc_name: Имя NPC (например, "Davies")
            scene_id: ID сцены

        Returns:
            int: NPC ID или None если не найден
        """

        try:
            query = """
                SELECT c_npc_id
                FROM t_story_npcs
                WHERE c_name = $1
                  AND c_npc_id = ANY(
                      SELECT (jsonb_array_elements(c_npcs_present))::text::int
                      FROM t_story_scenes
                      WHERE c_scene_id = $2
                  )
            """

            result = await pgDB.fExec_SelectQuery_args(
                self.pool_base, query, npc_name, scene_id
            )

            if result and result[0][0]:
                return result[0][0]

            logger.warning(f"NPC '{npc_name}' not found in scene {scene_id}")
            return None

        except Exception as e:
            logger.error(f"Error getting NPC ID for {npc_name}: {e}", exc_info=True)
            return None

    def _______stage(self): pass

    async def _advance_dialogue_stage(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,  # ← ДОБАВИТЬ!
            npc_id: int,
            user_input: str,
            npc_behavior_overrides: Dict[str, Any]
    ) -> Optional[str]:
        """Проверить триггеры и переключить stage"""

        user_input_lower = user_input.lower()

        dialogue_flow = npc_behavior_overrides.get('dialogue_flow')
        if not dialogue_flow:
            return None

        current_stage = await self._get_current_dialogue_stage(
            user_id, story_id, scene_id, npc_id, npc_behavior_overrides
        )

        if not current_stage:
            return None

        #stages_list = sorted(dialogue_flow.keys())
        stages_list = sorted(
            dialogue_flow.keys(),
            key=lambda x: int(x.split('_')[1])
        )
        current_index = stages_list.index(current_stage)

        if current_index < len(stages_list) - 1:
            next_stage_name = stages_list[current_index + 1]
            next_stage = dialogue_flow[next_stage_name]
            trigger = next_stage.get('trigger', '').lower()

            # Упрощенная логика триггеров
            trigger_matched = False

            if trigger == 'first_contact':
                # Не переключаем со stage_1 - это начальный stage
                trigger_matched = False
            elif trigger == 'any_user_message':
                # Переключить на следующий stage при любом сообщении
                trigger_matched = True
            else:
                # Старая логика для кастомных триггеров (если нужна)
                if 'danger' in trigger or 'pickup' in trigger:
                    keywords = ['pick you up', 'pick up', 'come get you', 'zombie', 'danger', 'outbreak', 'disease',
                                'terrible']
                    trigger_matched = any(kw in user_input_lower for kw in keywords)
                elif 'zombies' in trigger or 'blood' in trigger:
                    keywords = ['zombie', 'blood', 'not drunk', 'dead people', 'dangerous', 'attack']
                    trigger_matched = any(kw in user_input_lower for kw in keywords)
                elif 'insist' in trigger or 'urgent' in trigger:
                    keywords = ['serious', 'please', 'must', 'now', 'hurry', 'urgent', 'need you']
                    trigger_matched = any(kw in user_input_lower for kw in keywords)

            if trigger_matched:
                await self._save_dialogue_stage(
                    user_id, story_id, scene_id, npc_id, next_stage_name
                )
                logger.info(f"Dialogue stage advanced: {current_stage} -> {next_stage_name}")
                return next_stage_name

        return current_stage

    async def _get_current_dialogue_stage(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,  # ← ДОБАВИТЬ!
            npc_id: int,
            npc_behavior_overrides: Dict[str, Any]
    ) -> Optional[str]:
        """Получить текущий stage диалога"""

        dialogue_flow = npc_behavior_overrides.get('dialogue_flow')
        if not dialogue_flow:
            return None

        query = """
            SELECT c_scene_progress
            FROM t_story_user_progress
            WHERE c_user_id = $1 AND c_story_id = $2
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base, query, user_id, story_id
        )

        if not result or not result[0][0]:
            stages = sorted(dialogue_flow.keys())
            return stages[0] if stages else None

        scene_progress = result[0][0]
        if isinstance(scene_progress, str):
            scene_progress = json.loads(scene_progress)

        scene_key = f"scene_{scene_id}"
        npc_states = scene_progress.get(scene_key, {}).get('npc_states', {})
        npc_state = npc_states.get(str(npc_id), {})

        current_stage = npc_state.get('dialogue_stage')
        if current_stage and current_stage in dialogue_flow:
            return current_stage

        stages = sorted(dialogue_flow.keys())
        return stages[0] if stages else None

    async def _save_dialogue_stage(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,  # ← ДОБАВИТЬ!
            npc_id: int,
            stage: str
    ):
        """Сохранить текущий stage"""

        query = """
            SELECT c_scene_progress
            FROM t_story_user_progress
            WHERE c_user_id = $1 AND c_story_id = $2
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base, query, user_id, story_id
        )

        if not result:
            logger.warning(f"No progress for user {user_id}, story {story_id}")
            return

        scene_progress = result[0][0]
        if isinstance(scene_progress, str):
            scene_progress = json.loads(scene_progress)

        if not scene_progress:
            scene_progress = {}

        scene_key = f"scene_{scene_id}"

        if scene_key not in scene_progress:
            scene_progress[scene_key] = {}

        if 'npc_states' not in scene_progress[scene_key]:
            scene_progress[scene_key]['npc_states'] = {}

        if str(npc_id) not in scene_progress[scene_key]['npc_states']:
            scene_progress[scene_key]['npc_states'][str(npc_id)] = {}

        scene_progress[scene_key]['npc_states'][str(npc_id)]['dialogue_stage'] = stage

        update_query = """
            UPDATE t_story_user_progress
            SET c_scene_progress = $1::jsonb,
                c_last_interaction_at = CURRENT_TIMESTAMP
            WHERE c_user_id = $2 AND c_story_id = $3
        """

        await pgDB.fExec_UpdateQuery_args(
            self.pool_base,
            update_query,
            json.dumps(scene_progress),
            user_id,
            story_id
        )

        logger.info(f"Saved dialogue stage '{stage}' for NPC {npc_id}")


    async def _count_messages_with_npc(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,
            npc_name: str
    ) -> int:
        """
        Подсчитать количество сообщений с определённым NPC
        """

        # Получаем NPC ID по имени
        npc_query = """
            SELECT c_npc_id
            FROM t_story_npcs
            WHERE c_story_id = $1 AND c_name = $2
            LIMIT 1
        """

        npc_result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            npc_query,
            story_id,
            npc_name
        )

        if not npc_result:
            return 0

        npc_id = npc_result[0][0]

        # Считаем сообщения
        count_query = """
            SELECT COUNT(*)
            FROM t_story_user_interactions
            WHERE c_user_id = $1 
              AND c_story_id = $2
              AND c_scene_id = $3
              AND c_target_npc_id = $4
              AND c_interaction_type = 'dialogue'
        """

        count_result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            count_query,
            user_id,
            story_id,
            scene_id,
            npc_id
        )

        return count_result[0][0] if count_result else 0

    async def _get_full_dialogue_text(
            self,
            user_id: int,
            story_id: int,
            scene_id: int
    ) -> str:
        """
        Получить весь текст диалога в сцене (user + AI)
        """

        #<old>
        query = """
            SELECT c_user_input, c_ai_response
            FROM t_story_user_interactions
            WHERE c_user_id = $1 
              AND c_story_id = $2
              AND c_scene_id = $3
              AND c_interaction_type = 'dialogue'
            ORDER BY c_timestamp ASC
        """
        #</old>

        query = '''
        SELECT t1.c_user_input, t1.c_ai_response, t2.c_name 
        FROM t_story_user_interactions t1
        JOIN t_story_npcs t2 ON t1.c_target_npc_id = t2.c_npc_id
        WHERE t1.c_user_id = $1
            AND t1.c_story_id = $2
            AND t1.c_scene_id = $3
            AND t1.c_interaction_type = 'dialogue'
        ORDER BY t1.c_timestamp ASC
        '''


        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            query,
            user_id,
            story_id,
            scene_id
        )

        if not result:
            return ""

        # Объединяем весь текст
        full_text = []
        for i, row in enumerate(result):
            user_input = row[0] or ""
            ai_response = row[1] or ""
            npc_name = row[2] or ""

            full_text.append(f'|{i}. User - {user_input} : {npc_name} - {ai_response}\n')
            #full_text.append(user_input)
            #full_text.append(ai_response)

        return " ".join(full_text).lower()

    async def _check_item_in_inventory(
            self,
            user_id: int,
            story_id: int,
            target: str  # ← Переименовал для ясности (objective target)
    ) -> bool:
        """
        Проверить есть ли item в инвентаре

        Логика:
        1. Точное совпадение name == target
        2. Fuzzy поиск target в (name + description)
        """

        item_manager = ItemManager((self.pool_base, self.pool_log))
        inventory = await item_manager.get_user_inventory(user_id, story_id)

        target_lower = target.lower().strip()

        for item in inventory:
            item_name = item['name']
            item_name_lower = item_name.lower()

            # 1. Точное совпадение (приоритет)
            if item_name_lower == target_lower:
                logger.debug(f"v Exact match: '{target}'")
                return True

            # 2. ⭐ FUZZY: поиск в name + description
            if len(target_lower) > 3:  # Защита от "cat" -> "catalogue"
                item_description = item.get('description', '').lower()
                search_text = f"{item_name_lower} {item_description}"

                if target_lower in search_text:
                    logger.info(f"v Fuzzy match: '{target}' found in '{item_name}'")
                    return True

        logger.debug(f"x Not found: '{target}'")
        return False





    async def _reveal_item_for_user(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,
            item_name: str
    ):
        """
        Раскрыть item для пользователя после получения информации от NPC

        Когда пользователь спрашивает "Where can I find milk?" и NPC отвечает,
        objective с reveals_item="milk" завершается и этот метод добавляет
        "milk" в revealed_items, делая его видимым в Look around.

        Args:
            user_id: ID пользователя
            story_id: ID истории
            scene_id: ID сцены
            item_name: Название item который нужно раскрыть

        Example:
            User: "Where can I find milk?"
            NPC: "Milk is in the dairy refrigerator"
            -> objective.reveals_item = "milk"
            -> this method adds "milk" to scene_progress["scene_X"]["revealed_items"]
            -> now "milk" is visible in Look around
        """

        # Получить текущий scene_progress
        query = """
            SELECT c_scene_progress
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
            logger.warning(f"No progress found for user {user_id}, story {story_id}")
            return

        scene_progress = result[0][0]
        if isinstance(scene_progress, str):
            scene_progress = json.loads(scene_progress)

        if not scene_progress:
            scene_progress = {}

        # Получить или создать секцию для текущей сцены
        scene_key = f"scene_{scene_id}"
        if scene_key not in scene_progress:
            scene_progress[scene_key] = {}

        # Получить или создать список revealed_items
        if 'revealed_items' not in scene_progress[scene_key]:
            scene_progress[scene_key]['revealed_items'] = []

        # Добавить item если его еще нет
        if item_name not in scene_progress[scene_key]['revealed_items']:
            scene_progress[scene_key]['revealed_items'].append(item_name)
            logger.info(f"v Added '{item_name}' to revealed_items for user {user_id}, scene {scene_id}")
        else:
            logger.debug(f"Item '{item_name}' already revealed for user {user_id}")

        # Обновить БД
        update_query = """
            UPDATE t_story_user_progress
            SET c_scene_progress = $1::jsonb,
                c_last_interaction_at = CURRENT_TIMESTAMP
            WHERE c_user_id = $2 AND c_story_id = $3
        """

        await pgDB.fExec_UpdateQuery_args(
            self.pool_base,
            update_query,
            json.dumps(scene_progress),
            user_id,
            story_id
        )

        logger.info(f"Item '{item_name}' is now discoverable for user {user_id}")


    def _____dummy(self):
        pass

    async def _get_npc_items_to_give(
            self,
            npc_id: int,
            story_id: int
    ) -> List[Dict[str, Any]]:
        """
        Получить список items которые NPC может отдать пользователю

        Args:
            npc_id: ID NPC
            story_id: ID истории

        Returns:
            Список items с их описанием
        """

        # Получить имя NPC
        npc_query = """
            SELECT c_name
            FROM t_story_npcs
            WHERE c_npc_id = $1
        """

        npc_result = await pgDB.fExec_SelectQuery_args(self.pool_base, npc_query, npc_id)

        if not npc_result:
            return []

        npc_name = npc_result[0][0]

        # Найти items у этого NPC
        items_query = """
            SELECT c_item_id, c_name, c_description, c_location_details
            FROM t_story_items
            WHERE c_story_id = $1
              AND c_location_type = 'npc'
        """

        items_result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            items_query,
            story_id
        )

        if not items_result:
            return []

        npc_items = []
        for row in items_result:
            item_id = row[0]
            item_name = row[1]
            item_description = row[2]
            location_details = row[3]

            # Парсим JSON если нужно
            if isinstance(location_details, str):
                location_details = json.loads(location_details) if location_details else {}

            # Проверить что этот item относится к данному NPC
            if location_details.get('npc_name') == npc_name:
                npc_items.append({
                    'item_id': item_id,
                    'name': item_name,
                    'description': item_description
                })

        return npc_items

    async def _check_npc_gives_item(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,
            npc_id: int,
            response_data: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Check if NPC should give an item to user based on dialogue"""

        logger.info(
            f"!!! _check_npc_gives_item CALLED: user={user_id}, story={story_id}, scene={scene_id}, npc={npc_id}")

        # Если given_items уже обработаны - пропустить AI analyzer
        if response_data and response_data.get('item_given'):
            logger.info("Items already processed via given_items field")
            return {
                'item_given': True,
                'item_name': response_data.get('item_name'),
                'item_id': response_data.get('item_id')
            }

        # FALLBACK: AI analyzer
        logger.info("Fallback: using AI analyzer (given_items was empty)")

        # Получить имя NPC
        npc_query = """
            SELECT c_name 
            FROM t_story_npcs 
            WHERE c_npc_id = $1
        """

        npc_result = await pgDB.fExec_SelectQuery_args(self.pool_base, npc_query, npc_id)

        if not npc_result:
            logger.warning(f"NPC {npc_id} not found")
            return None

        npc_name = npc_result[0][0]

        logger.info(f"=== _check_npc_gives_item: NPC={npc_name}, npc_id={npc_id} ===")

        # Найти items у этого NPC
        items_query = """
            SELECT c_item_id, c_name, c_description, c_location_details, 
                   c_acquisition_conditions, c_initial_location
            FROM t_story_items
            WHERE c_story_id = $1
              AND c_location_type = 'npc'
        """

        items_result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            items_query,
            story_id
        )

        logger.info(f"Found {len(items_result) if items_result else 0} items with location_type='npc'")

        if not items_result:
            return None

        from handlers.learnpath.story.managers.item_manager import ItemManager
        item_manager = ItemManager((self.pool_base, self.pool_log))

        # Получить 2 последние реплики диалога
        last_dialogues_query = """
            SELECT c_user_input, c_ai_response
            FROM t_story_user_interactions
            WHERE c_user_id = $1
              AND c_story_id = $2
              AND c_scene_id = $3
              AND c_target_npc_id = $4
            ORDER BY c_timestamp DESC
            LIMIT 2
        """

        last_dialogues_result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            last_dialogues_query,
            user_id,
            story_id,
            scene_id,
            npc_id
        )

        if not last_dialogues_result:
            logger.info(f"No dialogue found with {npc_name}")
            return None

        # Формируем строку диалога из 2 последних реплик (в обратном порядке - от старой к новой)
        dialogue_text = ""
        for i in reversed(range(len(last_dialogues_result))):
            user_input = last_dialogues_result[i][0] or ""
            npc_response = last_dialogues_result[i][1] or ""
            dialogue_text += f"User: {user_input}\n{npc_name}: {npc_response}\n\n"

        logger.info(f"Last 2 dialogues:\n{dialogue_text}")

        for row in items_result:
            item_id = row[0]
            item_name = row[1]
            item_description = row[2]
            location_details = row[3]
            acquisition_conditions = row[4]
            initial_location = row[5]

            logger.info(f"\n=== Checking item: {item_name} (id={item_id}) ===")
            logger.info(f"initial_location: {initial_location}")

            # Парсим JSON
            if isinstance(location_details, str):
                location_details = json.loads(location_details) if location_details else {}
            if isinstance(acquisition_conditions, str):
                acquisition_conditions = json.loads(acquisition_conditions) if acquisition_conditions else {}

            # Проверить что этот item у нужного NPC
            if initial_location != f"npc:{npc_name}":
                logger.info(f"SKIP: initial_location '{initial_location}' != 'npc:{npc_name}'")
                continue

            logger.info(f"OK: Item belongs to {npc_name}")

            # Проверить что item еще не выдан
            has_item = await item_manager.check_item_in_inventory(user_id, story_id, item_id)
            if has_item:
                logger.info(f"SKIP: User already has this item")
                continue

            logger.info(f"OK: User doesn't have item yet")

            # AI АНАЛИЗ: Дал ли NPC item пользователю?
            ai_prompt = f"""Analyze this dialogue between a user and NPC named {npc_name}.

DIALOGUE:
{dialogue_text}

QUESTION: Did {npc_name} give or hand the item "{item_name}" to the user in this dialogue?

Answer YES if you find ANY of these patterns:
- "Here is the {item_name}" (with or without "your")
- "Here is your {item_name}"
- "Here are the {item_name}"
- "Here's the {item_name}"
- "Take the {item_name}"
- "{item_name} for you"
- "You have {item_name}"
- "I'm giving you the {item_name}"
- "Hands/gives/offers you the {item_name}"
- ANY clear indication of {npc_name} transferring {item_name} to the user

IMPORTANT EXAMPLES:
- "Here is the menu" -> YES (even without "your")
- "Here is your menu" -> YES
- "We have a nice menu" -> NO (just mentioning, not giving)
- "The menu is on the table" -> NO (not giving to user)

Answer ONLY: YES or NO
            """

            try:
                logger.info(f"Asking AI: Did {npc_name} give '{item_name}' to user?")


                ai_response = await myF.afSendMsg2AI(
                    ai_prompt,
                    self.pool_base,
                    user_id,
                    iModel=0,
                    toggleParam=1,  # Low temperature
                    systemPrompt="You are an assistant that analyzes dialogues. Answer only YES or NO."
                )


                ai_answer = ai_response.strip().upper()
                logger.info(f"AI answer: {ai_answer}")

                if "YES" not in ai_answer:
                    logger.info(f"SKIP: AI says item was not given")
                    continue

                logger.info(f"OK: AI confirmed: {npc_name} gave '{item_name}' to user")

            except Exception as e:
                logger.error(f"AI analysis error: {e}")
                logger.info(f"SKIP: AI analysis failed")
                continue

            # Все условия выполнены - выдать item
            logger.info(f"GIVING ITEM '{item_name}' to user!")

            await item_manager.add_item_to_inventory(user_id, story_id, item_id)

            return {
                'item_given': True,
                'item_name': item_name,
                'item_id': item_id,
                'description': item_description
            }

        logger.info(f"=== No items to give ===")
        return None

    async def _get_objectives_with_status(
            self,
            user_id: int,
            story_id: int,
            scene_id: int,
            detailed_objectives: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Получить objectives с их текущими статусами из БД

        Args:
            user_id: ID пользователя
            story_id: ID истории
            scene_id: ID сцены
            detailed_objectives: Структура с objectives из БД

        Returns:
            List objectives с добавленным полем 'completed'
        """

        objectives_list = detailed_objectives.get('objectives', [])

        if not objectives_list:
            return []

        # Получить статусы из БД
        query = """
            SELECT c_scene_progress
            FROM t_story_user_progress
            WHERE c_user_id = $1 AND c_story_id = $2
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            query,
            user_id,
            story_id
        )

        if not result or not result[0][0]:
            # Нет прогресса - все objectives не выполнены
            for obj in objectives_list:
                obj['completed'] = False
            return objectives_list

        scene_progress = result[0][0]
        if isinstance(scene_progress, str):
            scene_progress = json.loads(scene_progress)

        # Получить статусы для текущей сцены
        scene_status = scene_progress.get(str(scene_id), {})
        objectives_status = scene_status.get('objectives', {})

        # Добавить статусы к objectives
        for obj in objectives_list:
            obj_id = obj['id']
            obj['completed'] = objectives_status.get(obj_id, False)

        return objectives_list