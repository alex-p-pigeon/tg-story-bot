"""
Interactive Story Engine - Основной движок интерактивной истории
"""

import logging
from typing import Dict, Any, Optional, List
import json
import fpgDB as pgDB
import selfFunctions as myF

from aiogram.fsm.context import FSMContext

from handlers.learnpath.story.managers.npc_manager import NPCManager
from handlers.learnpath.story.managers.item_manager import ItemManager
from handlers.learnpath.story.engines.dialogue_engine import DialogueEngine
from handlers.learnpath.story.systems.narrator_system import NarratorSystem

from handlers.learnpath.handlers.story_helpers import (
    generate_npc_voices_for_story,
    save_npc_voices_to_progress,
    check_voice_override,
    generate_sfx_response
)


logger = logging.getLogger(__name__)


class InteractiveStoryEngine:
    """Основной движок интерактивной истории"""

    def __init__(self, pool, user_id: int):
        self.pool_base, self.pool_log = pool
        self.user_id = user_id

        # Инициализируем компоненты
        self.npc_manager = NPCManager(pool)
        self.item_manager = ItemManager(pool)
        self.dialogue_engine = DialogueEngine(pool, user_id)
        self.narrator = NarratorSystem(pool, user_id)

    async def start_story(
            self,
            story_id: int
    ) -> Dict[str, Any]:
        """
        Начать историю - показать первую сцену

        Args:
            story_id: ID истории

        Returns:
            {
                'story_info': {...},
                'scene': {...},
                'message': 'Welcome message'
            }
        """

        logger.info(f"Starting story {story_id} for user {self.user_id}")

        # Получаем информацию об истории
        story_info = await self._get_story_info(story_id)

        if not story_info:
            raise ValueError(f"Story {story_id} not found")

        # Получаем первую сцену
        first_scene = await self._get_first_scene(story_id)

        if not first_scene:
            raise ValueError(f"No scenes found for story {story_id}")

        # Создаём прогресс пользователя
        await self._create_user_progress(story_id, first_scene['scene_id'])

        #Загружаем созданный прогресс
        user_progress = await self._get_user_progress(story_id)

        # Получаем полную информацию о сцене
        scene_data = await self.dialogue_engine.generate_scene_description(
            scene_id=first_scene['scene_id'],
            story_id=story_id,
            user_progress=user_progress
        )

        # Получаем информацию о NPC в сцене
        npcs_info = []
        for npc_id in scene_data.get('npcs_present', []):
            npc = await self.npc_manager.get_npc(npc_id)
            if npc:
                npcs_info.append({
                    'npc_id': npc['npc_id'],
                    'name': npc['name'],
                    'personality': npc['personality']
                })

        # Получаем информацию о предметах
        items_info = []
        for item_id in scene_data.get('items_available', []):
            item = await self.item_manager.get_item(item_id)
            if item:
                items_info.append({
                    'item_id': item['item_id'],
                    'name': item['name'],
                    'description': item['description']
                })

        return {
            'story_info': {
                'story_id': story_info['story_id'],
                'story_name': story_info['story_name'],
                'description': story_info.get('description'),
                'grammar_context': story_info['grammar_context']
            },
            'scene': {
                **scene_data,
                'npcs_info': npcs_info,
                'items_info': items_info
            },
            'message': f"Welcome to {story_info['story_name']}!"
        }

    async def process_user_input(
            self,
            story_id: int,
            input_type: str,
            input_data: str,
            target_npc_id: Optional[int] = None,
            target_item_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Обработать ввод пользователя

        Args:
            story_id: ID истории
            input_type: 'text', 'voice', 'action', 'item_use', 'look_around'
            input_data: Текст или данные от пользователя
            target_npc_id: ID NPC для взаимодействия (для диалогов)
            target_item_id: ID предмета (для использования)

        Returns:
            {
                'npc_response': {...} or None,
                'scene_update': {...} or None,
                'narrator_hint': {...} or None,
                'scene_completed': bool,
                'next_scene_id': int or None,
                'story_completed': bool
            }
        """

        logger.info(
            f"Processing input for user {self.user_id}, story {story_id}, "
            f"type: {input_type}"
        )

        recent_interaction = None

        # Получаем текущий прогресс
        user_progress = await self._get_user_progress(story_id)

        logger.info(f'------------>>>>user_progress:{user_progress}')

        if not user_progress:
            raise ValueError(f"No progress found for user {self.user_id}, story {story_id}")

        current_scene_id = user_progress['current_scene_id']

        logger.info(f'------------>>>>current_scene_id:{current_scene_id}')

        # Получаем контекст сцены
        scene_context = await self._get_scene_context(story_id, current_scene_id)
        logger.info(f'------------>>>>scene_context:{scene_context}')

        # Получаем контекст истории
        story_context = await self._get_story_context(story_id)

        logger.info(f'------------>>>>story_context:{story_context}')

        result = {
            'npc_response': None,
            'scene_update': None,
            'narrator_hint': None,
            'scene_completed': False,
            'next_scene_id': None,
            'story_completed': False
        }

        # Обрабатываем в зависимости от типа
        if input_type in ['text', 'voice']:
            # Диалог с NPC
            if not target_npc_id:
                # Нужно указать NPC
                result['error'] = "Please specify which NPC to talk to"
                return result, recent_interaction

            # Получаем контекст NPC
            npc_context = await self.npc_manager.get_npc_context(
                npc_id=target_npc_id,
                user_id=self.user_id,
                story_id=story_id
            )
            logger.info(f'------------>>>>npc_context:{npc_context}')

            if not npc_context:
                result['error'] = f"NPC {target_npc_id} not found"
                return result, recent_interaction


            # ✅ ШАГ 1: Проверяем, нужен ли voice override


            should_override, voice_override_config = check_voice_override(
                npc_name=npc_context['name'],
                scene_context=scene_context
            )

            if should_override:
                # ✅ ПУТЬ A: Генерируем ответ алгоритмически (БЕЗ AI)
                logger.info(f"Using voice override for {npc_context['name']}, skipping AI call")

                npc_response = generate_sfx_response(
                    voice_override=voice_override_config,
                    npc_name=npc_context['name'],
                    user_input=input_data
                )

                # Добавляем метаданные
                npc_response['npc_id'] = npc_context['npc_id']
                npc_response['npc_name'] = npc_context['name']

            else:
                # ✅ ПУТЬ B: Генерируем ответ через AI (обычный диалог)
                logger.info(f"Generating AI response for {npc_context['name']}")

                # Генерируем ответ NPC
                npc_response = await self.dialogue_engine.generate_npc_response(
                    user_input=input_data,
                    npc_context=npc_context,
                    scene_context=scene_context,
                    story_context=story_context,
                    user_level=story_context['difficulty_level']
                )
            logger.info(f'------------>>>>npc_response:{npc_response}')

            result['npc_response'] = npc_response

            # Сохраняем взаимодействие
            await self.dialogue_engine.save_interaction(
                user_id=self.user_id,
                story_id=story_id,
                scene_id=current_scene_id,
                interaction_type='dialogue',
                user_input=input_data,
                user_input_type=input_type,
                target_npc_id=target_npc_id,
                ai_response=npc_response['response'],
                correction=npc_response['correction'],
                ai_response_trs=npc_response.get('text_trs'),
                correction_trs=npc_response.get('correction_trs')
            )

            # Обновляем состояние NPC
            await self.npc_manager.update_npc_state(
                user_id=self.user_id,
                story_id=story_id,
                npc_id=target_npc_id,
                state_updates={'met': True}
            )

            logger.info(f"!!! BEFORE calling _check_npc_gives_item")
            # Проверяем, дает ли NPC какой-то item пользователю
            npc_gives_item = await self.dialogue_engine._check_npc_gives_item(
                user_id=self.user_id,
                story_id=story_id,
                scene_id=current_scene_id,
                npc_id=target_npc_id,
                response_data=npc_response
            )

            if npc_gives_item:
                result['npc_gives_item'] = npc_gives_item
                logger.info(f"NPC gave item to user: {npc_gives_item}")


            '''
            # Проверяем выполнение цели
            scene_completed = await self.dialogue_engine.check_objective_completion(
                scene_id=current_scene_id,
                story_id=story_id,
                user_id=self.user_id,
                recent_interaction={
                    'interaction_type': 'dialogue',
                    'user_input': input_data,
                    'ai_response': npc_response['response'],
                    'target_npc_id': target_npc_id
                }
            )
            
            logger.info(f'------------>>>>scene_completed:{scene_completed}')

            result['scene_completed'] = scene_completed
            '''

            recent_interaction = {
                'interaction_type': 'dialogue',
                'user_input': input_data,
                'ai_response': npc_response['response'],
                'target_npc_id': target_npc_id
            }

        elif input_type == 'item_use':
            # Использование предмета
            # input_data содержит: {'item_name', 'item_id', 'target', 'action'}

            item_name = input_data.get('item_name')
            item_id = input_data.get('item_id')  # ✅ Получаем item_id
            target = input_data.get('target')  # Имя NPC
            action = input_data.get('action', f'used {item_name}')

            logger.info(f"Item use: {item_name} on {target}")

            # ✅ НОВОЕ: Если target - это NPC, генерируем NPC response
            if target_npc_id:
                # Получаем контекст NPC
                npc_context = await self.npc_manager.get_npc_context(
                    npc_id=target_npc_id,
                    user_id=self.user_id,
                    story_id=story_id
                )

                if not npc_context:
                    result['error'] = f"NPC {target_npc_id} not found"
                    return result, recent_interaction

                # ✅ Создаём user_input для NPC как описание действия
                user_input_for_npc = f"*{action}*"  # "showed Passport to Officer Martinez"

                '''
                # ✅ Генерируем ответ NPC на действие с item
                npc_response = await self.dialogue_engine.generate_npc_response(
                    user_input=user_input_for_npc,
                    npc_context=npc_context,
                    scene_context=scene_context,
                    story_context=story_context,
                    user_level=story_context['difficulty_level']
                )

                result['npc_response'] = npc_response
                '''
                # ✅ НОВОЕ: Проверяем voice override перед генерацией ответа
                should_override, voice_override_config = check_voice_override(
                    npc_name=npc_context['name'],
                    scene_context=scene_context
                )

                if should_override:
                    # Генерируем ответ алгоритмически (БЕЗ AI)
                    logger.info(f"Using voice override for item_use with {npc_context['name']}")

                    npc_response = generate_sfx_response(
                        voice_override=voice_override_config,
                        npc_name=npc_context['name'],
                        user_input=user_input_for_npc
                    )

                    npc_response['npc_id'] = npc_context['npc_id']
                    npc_response['npc_name'] = npc_context['name']
                else:
                    # ✅ Генерируем ответ NPC через AI
                    logger.info(f"Generating AI response for item_use with {npc_context['name']}")

                    npc_response = await self.dialogue_engine.generate_npc_response(
                        user_input=user_input_for_npc,
                        npc_context=npc_context,
                        scene_context=scene_context,
                        story_context=story_context,
                        user_level=story_context['difficulty_level']
                    )

                result['npc_response'] = npc_response


                # ✅ Сохраняем взаимодействие с правильными полями
                await self.dialogue_engine.save_interaction(
                    user_id=self.user_id,
                    story_id=story_id,
                    scene_id=current_scene_id,
                    interaction_type='item_use',
                    user_input=action,
                    user_input_type='action',
                    target_npc_id=target_npc_id,  # ✅ ID NPC
                    target_item_id=item_id,  # ✅ ID item
                    ai_response=npc_response['response'],
                    correction=npc_response.get('correction', ''),
                    ai_response_trs=npc_response.get('text_trs'),
                    correction_trs=npc_response.get('correction_trs')
                )

                # Обновляем состояние NPC
                await self.npc_manager.update_npc_state(
                    user_id=self.user_id,
                    story_id=story_id,
                    npc_id=target_npc_id,
                    state_updates={'met': True}
                )

                '''
                # ✅ Проверяем выполнение целей с правильным interaction
                scene_completed = await self.dialogue_engine.check_objective_completion(
                    scene_id=current_scene_id,
                    story_id=story_id,
                    user_id=self.user_id,
                    recent_interaction={
                        'interaction_type': 'item_use',
                        'item_name': item_name,
                        'item_id': item_id,
                        'target': target,
                        'target_npc_id': target_npc_id,
                        'user_input': action
                    }
                )

                result['scene_completed'] = scene_completed
                '''
                recent_interaction = {
                    'interaction_type': 'item_use',
                    'item_name': item_name,
                    'item_id': item_id,
                    'target': target,
                    'target_npc_id': target_npc_id,
                    'user_input': action
                }


            else:
                # Старая логика для использования item НЕ на NPC (контейнеры и т.д.)
                if not target_item_id:
                    result['error'] = "Please specify which item to use"
                    return result, recent_interaction

                # Используем предмет
                use_result = await self.item_manager.use_item(
                    user_id=self.user_id,
                    story_id=story_id,
                    item_id=target_item_id,
                    target=input_data  # На что используем
                )

                result['item_use_result'] = use_result

                if use_result['success']:
                    # Сохраняем взаимодействие
                    await self.dialogue_engine.save_interaction(
                        user_id=self.user_id,
                        story_id=story_id,
                        scene_id=current_scene_id,
                        interaction_type='item_use',
                        user_input=f"Used item: {use_result['item']['name']}",
                        user_input_type='action',
                        target_npc_id=None,
                        target_item_id=target_item_id,  # ✅ Передаём ID
                        ai_response=use_result['message'],
                        correction='N/A'
                    )

                    '''
                    # Проверяем выполнение цели
                    scene_completed = await self.dialogue_engine.check_objective_completion(
                        scene_id=current_scene_id,
                        story_id=story_id,
                        user_id=self.user_id,
                        recent_interaction={
                            'interaction_type': 'item_use',
                            'target_item_id': target_item_id,
                            'user_input': input_data
                        }
                    )

                    result['scene_completed'] = scene_completed
                    '''
                    recent_interaction = {
                        'interaction_type': 'item_use',
                        'target_item_id': target_item_id,
                        'user_input': input_data
                    }


        elif input_type == 'look_around':
            # Осмотреться - обновляем описание сцены
            scene_data = await self.dialogue_engine.generate_scene_description(
                scene_id=current_scene_id,
                story_id=story_id,
                user_progress=user_progress
            )

            result['scene_update'] = scene_data

            '''
            # Проверяем objectives после look_around
            scene_completed = await self.dialogue_engine.check_objective_completion(
                scene_id=current_scene_id,
                story_id=story_id,
                user_id=self.user_id,
                recent_interaction={
                    'interaction_type': 'action',  # look_around считается как action
                    'action': 'look_around'
                }
            )
            logger.info(f'---------->>>>>>>>>scene_completed:{scene_completed}')

            result['scene_completed'] = scene_completed
            '''

            recent_interaction = {
                'interaction_type': 'action',  # look_around считается как action
                'action': 'look_around'
            }

        # Обновляем счетчик действий
        new_actions_count = user_progress['actions_count'] + 1
        await self._update_actions_count(story_id, new_actions_count)


        '''
        # Проверяем нужна ли подсказка
        hint_needed = await self.narrator.check_if_hint_needed(
            user_id=self.user_id,
            story_id=story_id,
            scene_id=current_scene_id,
            actions_count=new_actions_count
        )

        logger.info(f'------------>>>>>>>>>>>hint_needed:{hint_needed}')

        # ✅ НОВОЕ: Подготовить информацию о текущем взаимодействии для narrator
        recent_interaction_for_hint = None

        if input_type in ['text', 'voice'] and target_npc_id:
            # Получить имя NPC для проверки
            npc = await self.npc_manager.get_npc(target_npc_id)
            recent_interaction_for_hint = {
                'interaction_type': 'dialogue',
                'npc_id': target_npc_id,
                'npc_name': npc['name'] if npc else 'Unknown',
                'user_input': input_data
            }
            logger.info(f"Recent interaction for hint: dialogue with {npc['name'] if npc else 'Unknown'}")
        elif input_type == 'item_use' and input_data:
            recent_interaction_for_hint = {
                'interaction_type': 'item_use',
                'item_name': input_data.get('item_name'),
                'target': input_data.get('target')
            }
            logger.info(f"Recent interaction for hint: item_use {input_data.get('item_name')}")

        if hint_needed:     #and not result['scene_completed']
            # Анализируем причину застревания
            stuck_reason = await self.narrator.analyze_stuck_reason(
                user_id=self.user_id,
                story_id=story_id,
                scene_id=current_scene_id,
                scene_context=scene_context,
                user_progress=user_progress
            )

            #Добавить detailed objectives
            detailed_objectives_query = """
                SELECT c_detailed_objectives
                FROM t_story_scenes
                WHERE c_scene_id = $1
            """
            detailed_result = await pgDB.fExec_SelectQuery_args(
                self.pool_base,
                detailed_objectives_query,
                current_scene_id
            )

            if detailed_result and detailed_result[0][0]:
                detailed_objs = detailed_result[0][0]
                if isinstance(detailed_objs, str):
                    detailed_objs = json.loads(detailed_objs)

                # ✅ Получить статусы из БД
                objectives_with_status = await self.dialogue_engine._get_objectives_with_status(
                    self.user_id, story_id, current_scene_id, detailed_objs
                )

                scene_context['detailed_objectives'] = {'objectives': objectives_with_status}

            # Генерируем подсказку с информацией о текущем действии
            hint = await self.narrator.generate_hint(
                user_id=self.user_id,
                story_id=story_id,
                scene_id=current_scene_id,
                scene_context=scene_context,
                user_progress=user_progress,
                stuck_reason=stuck_reason,
                recent_interaction=recent_interaction_for_hint  # ⬅️ ДОБАВЛЕНО!
            )

            # ✅ ИЗМЕНЕНО: Hint может быть None если narrator решил что он не нужен
            if hint:
                result['narrator_hint'] = hint

                # Сохраняем подсказку
                await self.narrator.save_hint(
                    user_id=self.user_id,
                    story_id=story_id,
                    scene_id=current_scene_id,
                    hint_text=hint['text'],
                    hint_text_trs=hint.get('text_trs', {})
                )
                logger.info(f"v Narrator hint generated and saved")
            else:
                logger.info(f" >> Narrator hint skipped (user is making progress)")
        '''

        # Если сцена завершена, переходим к следующей
        '''
        if result['scene_completed']:
            next_scene_info = await self.advance_to_next_scene(
                story_id=story_id,
                current_scene_id=current_scene_id
            )

            result['next_scene_id'] = next_scene_info.get('next_scene_id')
            result['story_completed'] = next_scene_info.get('is_ending', False)
            result['ending_type'] = next_scene_info.get('ending_type')
        '''

        return result, recent_interaction

    async def proceed_to_next_scene(
            self,
            user_id: int,
            story_id: int,
            current_scene_id: int
    ) -> Dict[str, Any]:
        """
        Перейти к следующей сцене

        Returns:
            {
                'success': bool,
                'next_scene_id': int | None,
                'next_scene_data': dict | None,  # ← Уже с npcs_info!
                'is_story_ending': bool,
                'ending_type': str | None
            }
        """

        logger.info(f"User {user_id} proceeding to next scene from {current_scene_id}")

        try:
            # 1. Получаем информацию о следующей сцене и обновляем БД
            next_scene_info = await self.advance_to_next_scene(
                story_id=story_id,
                current_scene_id=current_scene_id
            )

            if not next_scene_info:
                return {'success': False, 'error': 'Failed to advance scene'}

            next_scene_id = next_scene_info.get('next_scene_id')
            is_ending = next_scene_info.get('is_ending', False)
            ending_type = next_scene_info.get('ending_type')

            # 2. Если концовка - возвращаем без загрузки сцены
            if is_ending:
                return {
                    'success': True,
                    'next_scene_id': None,
                    'next_scene_data': None,
                    'is_story_ending': True,
                    'ending_type': ending_type
                }

            # 3. Загружаем данные следующей сцены
            next_scene_data = await self.dialogue_engine.generate_scene_description(
                scene_id=next_scene_id,
                story_id=story_id,
                user_progress=await self._get_user_progress(story_id)
            )

            # 4. ✅ Обогащаем NPC информацией ЗДЕСЬ
            npcs_info = []
            for npc_id in next_scene_data.get('npcs_present', []):
                npc = await self.npc_manager.get_npc(npc_id)
                if npc:
                    npcs_info.append({
                        'npc_id': npc['npc_id'],
                        'name': npc['name']
                    })

            next_scene_data['npcs_info'] = npcs_info

            return {
                'success': True,
                'next_scene_id': next_scene_id,
                'next_scene_data': next_scene_data,  # ← Уже обогащена!
                'is_story_ending': False,
                'ending_type': None
            }

        except Exception as e:
            logger.error(f"Error proceeding to next scene: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}



    async def get_scene(self, story_id: int, scene_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить данные сцены

        Args:
            story_id: ID истории
            scene_id: ID сцены

        Returns:
            Dict с данными сцены или None
        """

        query = """
            SELECT 
                c_scene_id,
                c_scene_name,
                c_scene_name_trs,
                c_location_description,
                c_location_description_trs,
                c_objective,
                c_objective_trs,
                c_npcs_present,
                c_items_available,
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
            return None

        row = result[0]

        # Парсим JSONB поля
        npcs_present = row[7]
        if isinstance(npcs_present, str):
            npcs_present = json.loads(npcs_present)

        items_available = row[8]
        if isinstance(items_available, str):
            items_available = json.loads(items_available)

        detailed_objectives = row[9]
        if isinstance(detailed_objectives, str):
            detailed_objectives = json.loads(detailed_objectives)

        scene_context = row[10]
        if isinstance(scene_context, str):
            scene_context = json.loads(scene_context)

        return {
            'scene_id': row[0],
            'scene_name': row[1],
            'scene_name_trs': row[2],
            'location_description': row[3],
            'location_description_trs': row[4],
            'objective': row[5],
            'objective_trs': row[6],
            'npcs_present': npcs_present,
            'items_available': items_available,
            'detailed_objectives': detailed_objectives,
            'scene_context': scene_context,
            'is_ending': row[11],
            'ending_type': row[12]
        }

    async def advance_to_next_scene(
            self,
            story_id: int,
            current_scene_id: int
    ) -> Dict[str, Any]:
        """
        Перейти к следующей сцене

        Args:
            story_id: ID истории
            current_scene_id: ID текущей сцены

        Returns:
            {
                'next_scene_id': int or None,
                'is_ending': bool,
                'ending_type': str or None,
                'scene_data': {...} or None
            }
        """

        logger.info(f"Advancing from scene {current_scene_id} for user {self.user_id}")

        # Получаем информацию о следующей сцене
        query = """
            SELECT c_next_scene_id, c_is_ending, c_ending_type
            FROM t_story_scenes
            WHERE c_scene_id = $1 AND c_story_id = $2
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            query,
            current_scene_id,
            story_id
        )

        if not result:
            return {'next_scene_id': None, 'is_ending': True, 'ending_type': 'unknown'}

        next_scene_id = result[0][0]
        is_ending = result[0][1]
        ending_type = result[0][2]

        if is_ending:
            # История завершена
            await self._mark_story_completed(story_id, ending_type)
            return {
                'next_scene_id': None,
                'is_ending': True,
                'ending_type': ending_type,
                'scene_data': None
            }

        if not next_scene_id:
            # Нет следующей сцены (тупик или ошибка)
            logger.warning(f"No next scene for scene {current_scene_id}")
            return {'next_scene_id': None, 'is_ending': True, 'ending_type': 'unknown'}

        # Обновляем прогресс на следующую сцену
        await self._update_current_scene(story_id, next_scene_id)

        # Получаем данные новой сцены
        user_progress = await self._get_user_progress(story_id)

        scene_data = await self.dialogue_engine.generate_scene_description(
            scene_id=next_scene_id,
            story_id=story_id,
            user_progress=user_progress
        )

        return {
            'next_scene_id': next_scene_id,
            'is_ending': False,
            'ending_type': None,
            'scene_data': scene_data
        }

    async def _get_story_info(self, story_id: int) -> Optional[Dict[str, Any]]:
        """Получить информацию об истории"""

        query = """
            SELECT 
                c_story_id,
                c_story_name,
                c_description,
                c_grammar_context,
                c_difficulty_level
            FROM t_story_interactive_stories
            WHERE c_story_id = $1
        """

        result = await pgDB.fExec_SelectQuery_args(self.pool_base, query, story_id)

        if not result:
            return None

        row = result[0]

        return {
            'story_id': row[0],
            'story_name': row[1],
            'description': row[2],
            'grammar_context': row[3],
            'difficulty_level': row[4]
        }

    async def _get_first_scene(self, story_id: int) -> Optional[Dict[str, Any]]:
        """Получить первую сцену истории"""

        query = """
            SELECT c_scene_id, c_scene_name
            FROM t_story_scenes
            WHERE c_story_id = $1
            ORDER BY c_chapter_number ASC, c_scene_number ASC
            LIMIT 1
        """

        result = await pgDB.fExec_SelectQuery_args(self.pool_base, query, story_id)

        if not result:
            return None

        return {
            'scene_id': result[0][0],
            'scene_name': result[0][1]
        }

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

    async def _create_user_progress(self, story_id: int, first_scene_id: int, state: FSMContext):
        """
        Создать/обновить запись прогресса пользователя для истории

        Args:
            story_id: ID истории
            first_scene_id: ID первой сцены
            state: FSMContext для получения уровня пользователя
        """

        # 1. Получить уровень пользователя
        import selfFunctions as myF
        englevel_num, user_level = await myF.fGetUserEngLevel(state, self.user_id, self.pool_base)

        logger.info(f"User {self.user_id} level: {user_level} ({englevel_num})")

        # 2. Сформировать lesson_context
        lesson_context = {
            'grammar_focus': 'General grammar practice',
            'cefr_level': user_level
        }

        # 3. Получить initial inventory
        initial_inventory = await self._get_initial_inventory_items(story_id)
        logger.info(f"Initial inventory items: {initial_inventory}")

        # 4. Создать запись прогресса
        query = """
                INSERT INTO t_story_user_progress
                    (c_user_id, c_story_id, c_current_scene_id, c_actions_count,
                     c_current_module_context, c_inventory,
                     c_npc_states, c_scene_progress, c_is_completed)
                VALUES ($1, $2, $3, 0, $4, $5, '{}'::jsonb, '{}'::jsonb, false)
                ON CONFLICT (c_user_id, c_story_id) 
                DO UPDATE SET
                    c_current_scene_id = $3,
                    c_actions_count = 0,
                    c_current_module_context = $4,
                    c_inventory = $5,
                    c_npc_states = '{}'::jsonb,
                    c_scene_progress = '{}'::jsonb,
                    c_is_completed = false,
                    c_last_interaction_at = NOW()
            """

        await pgDB.fExec_UpdateQuery_args(
            self.pool_base,
            query,
            self.user_id,
            story_id,
            first_scene_id,
            json.dumps(lesson_context, ensure_ascii=False),
            json.dumps(initial_inventory)
        )

        logger.info(f"Created/updated progress for user {self.user_id}, story {story_id}")

        # 5. ✅ Генерация голосов NPC
        is_premium, sub_stat = await myF.getSubscription_from_DB(self.user_id, (self.pool_base, self.pool_log))

        # Импорт функций генерации голосов


        npc_voices = await generate_npc_voices_for_story(
            pool=(self.pool_base, self.pool_log),
            story_id=story_id,
            user_id=self.user_id,
            is_premium=is_premium
        )

        await save_npc_voices_to_progress(
            pool=(self.pool_base, self.pool_log),
            user_id=self.user_id,
            story_id=story_id,
            npc_voices=npc_voices
        )

        logger.info(f"✅ Created progress with NPC voices for user {self.user_id}, story {story_id}")

    async def _get_user_progress(self, story_id: int) -> Optional[Dict[str, Any]]:
        """Получить прогресс пользователя"""

        query = """
            SELECT 
                c_current_scene_id,
                c_actions_count,
                c_inventory,
                c_npc_states,
                c_is_completed
            FROM t_story_user_progress
            WHERE c_user_id = $1 AND c_story_id = $2
        """

        result = await pgDB.fExec_SelectQuery_args(
            self.pool_base,
            query,
            self.user_id,
            story_id
        )

        if not result:
            return None

        row = result[0]

        inventory = row[2]
        if isinstance(inventory, str):
            inventory = json.loads(inventory) if inventory else []

        npc_states = row[3]
        if isinstance(npc_states, str):
            npc_states = json.loads(npc_states) if npc_states else {}

        return {
            'current_scene_id': row[0],
            'actions_count': row[1],
            'inventory': inventory,
            'npc_states': npc_states,
            'is_completed': row[4]
        }

    async def _get_scene_context(
            self,
            story_id: int,
            scene_id: int
    ) -> Dict[str, Any]:
        """Получить контекст сцены"""

        query = """
            SELECT 
                c_scene_name,
                c_location_description,
                c_objective,
                c_npcs_present,
                c_items_available,
                c_success_conditions, 
                c_scene_number, 
                c_scene_context
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
            return {}

        row = result[0]

        npcs_present = row[3]
        if isinstance(npcs_present, str):
            npcs_present = json.loads(npcs_present) if npcs_present else []

        items_available = row[4]
        if isinstance(items_available, str):
            items_available = json.loads(items_available) if items_available else []

        success_conditions = row[5]
        if isinstance(success_conditions, str):
            success_conditions = json.loads(success_conditions) if success_conditions else {}

        scene_context_json = row[7]
        if isinstance(scene_context_json, str):
            scene_context_json = json.loads(scene_context_json) if scene_context_json else {}
        elif scene_context_json is None:
            scene_context_json = {}

        return {
            'scene_id': scene_id,
            'scene_number': row[6],
            'location_name': row[0],
            'location_description': row[1],
            'objective': row[2],
            'npcs_present': npcs_present,
            'items_available': items_available,
            'success_conditions': success_conditions,
            'npc_behavior_overrides': scene_context_json.get('npc_behavior_overrides', {}),
            'atmosphere': scene_context_json.get('atmosphere', ''),
            'what_should_happen': scene_context_json.get('what_should_happen', ''),
            'scene_story_context': scene_context_json.get('scene_story_context', {}),
            'important_reveals': scene_context_json.get('important_reveals', []),
            'current_situation': scene_context_json.get('current_situation', '')
        }

    async def _get_story_context(self, story_id: int) -> Dict[str, Any]:
        """Получить контекст истории"""

        story_info = await self._get_story_info(story_id)

        return {
            'story_id': story_id,
            'story_name': story_info['story_name'],
            'grammar_context': story_info['grammar_context'],
            'difficulty_level': story_info['difficulty_level']
        }

    async def _update_actions_count(self, story_id: int, new_count: int):
        """Обновить счетчик действий"""

        query = """
            UPDATE t_story_user_progress
            SET c_actions_count = $1,
                c_last_interaction_at = NOW()
            WHERE c_user_id = $2 AND c_story_id = $3
        """

        await pgDB.fExec_UpdateQuery_args(
            self.pool_base,
            query,
            new_count,
            self.user_id,
            story_id
        )

    async def _update_current_scene(self, story_id: int, new_scene_id: int):
        """Обновить текущую сцену и сбросить счетчик действий"""

        query = """
            UPDATE t_story_user_progress
            SET c_current_scene_id = $1,
                c_actions_count = 0,
                c_last_interaction_at = NOW()
            WHERE c_user_id = $2 AND c_story_id = $3
        """

        await pgDB.fExec_UpdateQuery_args(
            self.pool_base,
            query,
            new_scene_id,
            self.user_id,
            story_id
        )

        logger.info(f"Updated scene to {new_scene_id} for user {self.user_id}")

    async def _mark_story_completed(self, story_id: int, ending_type: str):
        """Отметить историю как завершенную"""

        query = """
            UPDATE t_story_user_progress
            SET c_is_completed = true,
                c_last_interaction_at = NOW()
            WHERE c_user_id = $1 AND c_story_id = $2
        """

        await pgDB.fExec_UpdateQuery_args(
            self.pool_base,
            query,
            self.user_id,
            story_id
        )

        logger.info(
            f"Story {story_id} completed for user {self.user_id}, "
            f"ending: {ending_type}"
        )