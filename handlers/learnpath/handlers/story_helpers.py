"""
Story Helpers - Вспомогательные функции для работы с историями
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
import json
import re
import fpgDB as pgDB
from datetime import datetime
import selfFunctions as myF
import random
from pathlib import Path


logger = logging.getLogger(__name__)


def get_action_verb_for_item(item_name: str, item_purpose: str, npc_name: str = None) -> str:
    """
    Определить глагол действия в зависимости от назначения item

    Args:
        item_name: Название item
        item_purpose: Назначение item (из c_purpose)
        npc_name: Имя NPC (опционально)

    Returns:
        Строка с действием (без "You")

    Examples:
        "attacked Zombie with Kitchen knife"
        "showed Passport to Officer"
        "used Bandage on Injured person"
    """

    purpose_lower = item_purpose.lower() if item_purpose else ""

    # ⚔️ WEAPON - атаковать
    if any(keyword in purpose_lower for keyword in ['weapon', 'attack', 'fight', 'combat', 'defense']):
        return f"attacked {npc_name} with {item_name}"

    # 🩹 MEDICAL - использовать на
    elif any(keyword in purpose_lower for keyword in ['medical', 'heal', 'bandage', 'medicine', 'first aid']):
        return f"used {item_name} on {npc_name}"

    # 🍞 FOOD - предложить
    elif any(keyword in purpose_lower for keyword in ['food', 'drink', 'eat', 'consume', 'nutrition']):
        return f"offered {item_name} to {npc_name}"

    # 📋 DOCUMENT - показать
    elif any(keyword in purpose_lower for keyword in
             ['document', 'paper', 'id', 'passport', 'certificate', 'proof', 'show']):
        return f"showed {item_name} to {npc_name}"

    # 🔑 KEY - использовать
    elif any(keyword in purpose_lower for keyword in ['key', 'unlock', 'open']):
        return f"used {item_name} near {npc_name}"

    # 🧪 TOOL - применить
    elif any(keyword in purpose_lower for keyword in ['tool', 'repair', 'fix']):
        return f"applied {item_name} to {npc_name}"  # ⬅️ Вот где "apply" уместен!

    # 💰 MONEY - предложить
    elif any(keyword in purpose_lower for keyword in ['money', 'bribe', 'payment', 'currency']):
        return f"offered {item_name} to {npc_name}"

    # 🎁 DEFAULT - показать (универсальный fallback)
    else:
        return f"showed {item_name} to {npc_name}"

async def get_story_final_message(pool, story_id: int) -> Optional[str]:
    """
    Получить финальное сообщение истории из mystery_solution

    Args:
        pool: Database connection pool
        story_id: ID истории

    Returns:
        Финальное сообщение или None
    """
    pool_base, _ = pool
    query = """
        SELECT c_mystery_solution
        FROM t_story_interactive_stories
        WHERE c_story_id = $1
    """

    try:
        result = await pgDB.fExec_SelectQuery_args(pool_base, query, story_id)

        if not result or not result[0][0]:
            logger.warning(f"No mystery_solution found for story {story_id}")
            return None

        mystery_solution = result[0][0]

        # Парсим JSON если нужно
        if isinstance(mystery_solution, str):
            mystery_solution = json.loads(mystery_solution)

        final_message = mystery_solution.get('final_message')

        logger.info(f"Retrieved final_message for story {story_id}")

        return final_message

    except Exception as e:
        logger.error(f"Error getting final message for story {story_id}: {e}", exc_info=True)
        return None


async def get_scene_important_reveals(pool, scene_id: int) -> List[str]:
    """
    Получить important_reveals из scene_context

    Args:
        pool: Database connection pool
        scene_id: ID сцены

    Returns:
        Список reveals или пустой список
    """
    pool_base, _ = pool

    query = """
        SELECT c_scene_context
        FROM t_story_scenes
        WHERE c_scene_id = $1
    """

    try:
        result = await pgDB.fExec_SelectQuery_args(pool_base, query, scene_id)

        if not result or not result[0][0]:
            logger.warning(f"No scene_context found for scene {scene_id}")
            return []

        scene_context = result[0][0]

        # Парсим JSON если нужно
        if isinstance(scene_context, str):
            scene_context = json.loads(scene_context)

        reveals = scene_context.get('important_reveals', [])

        logger.info(f"Retrieved {len(reveals)} reveals for scene {scene_id}")

        return reveals

    except Exception as e:
        logger.error(f"Error getting reveals for scene {scene_id}: {e}", exc_info=True)
        return []


async def get_mystery_solution(pool, story_id: int) -> Optional[Dict[str, Any]]:
    """
    Получить полное mystery_solution для истории

    Args:
        pool: Database connection pool
        story_id: ID истории

    Returns:
        Dictionary с mystery, solution, final_message или None
    """
    pool_base, _ = pool

    query = """
        SELECT c_mystery_solution
        FROM t_story_interactive_stories
        WHERE c_story_id = $1
    """

    try:
        result = await pgDB.fExec_SelectQuery_args(pool_base, query, story_id)

        if not result or not result[0][0]:
            return None

        mystery_solution = result[0][0]

        if isinstance(mystery_solution, str):
            mystery_solution = json.loads(mystery_solution)

        return mystery_solution

    except Exception as e:
        logger.error(f"Error getting mystery_solution for story {story_id}: {e}", exc_info=True)
        return None


async def mark_story_completed(
        pool,
        user_id: int,
        story_id: int,
        completion_time_minutes: Optional[int] = None
) -> bool:
    """
    Отметить историю как завершенную пользователем

    Args:
        pool: Database connection pool
        user_id: ID пользователя
        story_id: ID истории
        completion_time_minutes: Время прохождения в минутах (опционально)

    Returns:
        True если успешно, False если ошибка
    """
    pool_base, _ = pool

    # Обновить user progress
    update_progress_query = """
        UPDATE t_story_user_progress
        SET 
            c_is_completed = true,
            c_last_interaction_at = CURRENT_TIMESTAMP
        WHERE c_user_id = $1 
            AND c_story_id = $2
    """

    # Обновить статистику истории (times_completed)
    update_stats_query = """
        UPDATE t_story_interactive_stories
        SET c_times_completed = c_times_completed + 1
        WHERE c_story_id = $1
    """

    try:
        # Обновить progress
        await pgDB.fExec_UpdateQuery_args(pool_base, update_progress_query, user_id, story_id)

        # Обновить статистику
        await pgDB.fExec_UpdateQuery_args(pool_base, update_stats_query, story_id)

        logger.info(f"Marked story {story_id} as completed for user {user_id}")

        return True

    except Exception as e:
        logger.error(f"Error marking story as completed: {e}", exc_info=True)
        return False


async def check_if_story_ending(pool, scene_id: int) -> bool:
    """
    Проверить является ли сцена финальной (ending scene)

    Args:
        pool: Database connection pool
        scene_id: ID сцены

    Returns:
        True если это ending scene, False иначе
    """
    pool_base, _ = pool

    query = """
        SELECT c_is_ending
        FROM t_story_scenes
        WHERE c_scene_id = $1
    """

    try:
        result = await pgDB.fExec_SelectQuery_args(pool_base, query, scene_id)

        if not result:
            return False

        is_ending = result[0][0]

        return bool(is_ending)

    except Exception as e:
        logger.error(f"Error checking if scene {scene_id} is ending: {e}", exc_info=True)
        return False


async def get_scene_ending_type(pool, scene_id: int) -> Optional[str]:
    """
    Получить тип окончания сцены (happy, sad, neutral, etc.)

    Args:
        pool: Database connection pool
        scene_id: ID сцены

    Returns:
        Тип окончания или None
    """
    pool_base, _ = pool

    query = """
        SELECT c_ending_type
        FROM t_story_scenes
        WHERE c_scene_id = $1
    """

    try:
        result = await pgDB.fExec_SelectQuery_args(pool_base, query, scene_id)

        if not result:
            return None

        ending_type = result[0][0]

        return ending_type

    except Exception as e:
        logger.error(f"Error getting ending type for scene {scene_id}: {e}", exc_info=True)
        return None


async def format_revelation_message(
        revelation_text: Optional[str] = None,
        items_obtained: Optional[List[Dict[str, Any]]] = None,
        scene_reveals: Optional[List[str]] = None,
        final_message: Optional[str] = None,
        custom_message: Optional[str] = None
) -> str:
    """
    Форматировать сообщение с revelation (что обнаружено в контейнере)

    Args:
        revelation_text: Текст revelation из контейнера
        items_obtained: Список полученных items
        scene_reveals: Список reveals из сцены
        final_message: Финальное сообщение истории
        custom_message: Кастомное сообщение

    Returns:
        Отформатированное HTML сообщение
    """

    parts = []

    # Custom message (если есть)
    if custom_message:
        parts.append(f"📜 <i>{custom_message}</i>")

    # Revelation text (из контейнера)
    if revelation_text:
        parts.append(f"📜 <i>{revelation_text}</i>")

    # Items obtained
    if items_obtained:
        items_text = "💎 <b>You obtained:</b>\n"
        for item in items_obtained:
            if item.get('added'):
                items_text += f"• <b>{item['name']}</b>\n"
        parts.append(items_text)

    # Scene reveals
    if scene_reveals:
        reveals_text = "🔮 <b>The Truth Revealed:</b>\n"
        for reveal in scene_reveals:
            reveals_text += f"• <i>{reveal}</i>\n"
        parts.append(reveals_text)

    # Final message
    if final_message:
        parts.append(f"📖 {final_message}")

    # Объединить все части
    return "\n\n".join(parts)


async def generate_npc_voices_for_story(
        pool,
        story_id: int,
        user_id: int,
        is_premium: bool = False
) -> Dict[int, Dict[str, str]]:
    """
    Сгенерировать и сохранить привязку голосов для всех NPC истории

    Args:
        pool: Database pool
        story_id: ID истории
        user_id: ID пользователя
        is_premium: Премиум пользователь или нет

    Returns:
        {
            npc_id: {
                'npc_name': 'Emma',
                'language': 'en-US',
                'voice_id': 'en-US-Standard-C',
                'gender': 'FEMALE'
            }
        }
    """

    pool_base, pool_log = pool

    # 1. Получить всех NPC истории с предопределенными голосами
    query = """
        SELECT 
            c_npc_id, 
            c_name, 
            c_gender,
            c_voice->0 as language,      -- первый элемент массива
            c_voice->1 as voice_id,      -- второй элемент
            c_voice->2 as gender_voice   -- третий элемент
        FROM t_story_npcs
        WHERE c_story_id = $1
        ORDER BY c_npc_id
    """

    result = await pgDB.fExec_SelectQuery_args(pool_base, query, story_id)

    if not result:
        logger.warning(f"No NPCs found for story {story_id}")
        return {}

    npcs = []
    for row in result:
        # Если c_voice NULL, то language/voice_id/gender_voice будут None
        predefined_voice = None
        if row[3] is not None:  # language не None
            # Удаляем кавычки из JSON строк: '"en-US"' -> 'en-US'
            predefined_voice = [
                row[3].strip('"') if row[3] else None,  # language
                row[4].strip('"') if row[4] else None,  # voice_id
                row[5].strip('"') if row[5] else None  # gender
            ]
        npcs.append({
            'npc_id': row[0],
            'name': row[1],
            'gender': row[2],  # 'male' or 'female'
            'predefined_voice': predefined_voice  # JSONB: ['en-AU', 'voice_id', 'MALE'] или None
        })

    # 2. Получить доступные голоса
    all_voices = myF.fGetAllVoices(isPremium=is_premium)

    # Разделить по гендеру
    male_voices = [v for v in all_voices if v[2] == 'MALE']
    female_voices = [v for v in all_voices if v[2] == 'FEMALE']

    # 3. Распределить голоса БЕЗ повторов (пока возможно)
    npc_voices = {}
    used_male_voices = []
    used_female_voices = []

    for npc in npcs:
        npc_gender = npc['gender'].upper()  # 'MALE' or 'FEMALE'
        predefined_voice = npc.get('predefined_voice')  # может быть list или None

        # ✅ Если есть предопределенный голос - использовать его
        if predefined_voice:
            # predefined_voice это уже list: ['en-AU', 'en-AU-Chirp-HD-D', 'MALE']
            npc_voices[npc['npc_id']] = {
                'npc_name': npc['name'],
                'language': predefined_voice[0],
                'voice_id': predefined_voice[1],
                'gender': predefined_voice[2]
            }

            # Добавить в список использованных для избегания повторов
            if predefined_voice[2] == 'MALE':
                used_male_voices.append(predefined_voice)
            else:
                used_female_voices.append(predefined_voice)

            logger.info(f"✅ Using predefined voice '{predefined_voice[1]}' for NPC {npc['name']}")
            continue

        # ❌ Случайный выбор голоса
        if npc_gender == 'MALE':
            # Выбрать из male_voices, избегая повторов
            available = [v for v in male_voices if v not in used_male_voices]
            if not available:
                # Все голоса использованы - начать заново
                available = male_voices
                used_male_voices = []

            voice = random.choice(available)
            used_male_voices.append(voice)
        else:  # FEMALE
            available = [v for v in female_voices if v not in used_female_voices]
            if not available:
                available = female_voices
                used_female_voices = []

            voice = random.choice(available)
            used_female_voices.append(voice)

        npc_voices[npc['npc_id']] = {
            'npc_name': npc['name'],
            'language': voice[0],
            'voice_id': voice[1],
            'gender': voice[2]
        }

    logger.info(f"Generated voices for {len(npc_voices)} NPCs in story {story_id}")

    return npc_voices


async def save_npc_voices_to_progress(
        pool,
        user_id: int,
        story_id: int,
        npc_voices: Dict[int, Dict[str, str]]
):
    """
    Сохранить привязку голосов в t_story_user_progress

    Args:
        pool: Database pool
        user_id: ID пользователя
        story_id: ID истории
        npc_voices: Словарь {npc_id: {voice_params}}
    """

    pool_base, pool_log = pool

    # Конвертируем ключи в строки для JSON
    npc_voices_json = {str(k): v for k, v in npc_voices.items()}

    query = """
        UPDATE t_story_user_progress
        SET c_npc_voices = $1::jsonb
        WHERE c_user_id = $2 AND c_story_id = $3
    """

    await pgDB.fExec_UpdateQuery_args(
        pool_base,
        query,
        json.dumps(npc_voices_json, ensure_ascii=False),
        user_id,
        story_id
    )

    logger.info(f"Saved NPC voices for user {user_id}, story {story_id}")




async def get_npc_voice_params(
        pool,
        user_id: int,
        story_id: int,
        npc_id: int
) -> Optional[List[str]]:
    """
    Получить параметры голоса для NPC в формате для afTxtToOGG

    Returns:
        [language, voice_id, gender] или None
    """

    pool_base, pool_log = pool

    query = """
        SELECT c_npc_voices
        FROM t_story_user_progress
        WHERE c_user_id = $1 AND c_story_id = $2
    """

    result = await pgDB.fExec_SelectQuery_args(pool_base, query, user_id, story_id)

    if not result or not result[0][0]:
        logger.warning(f"No NPC voices found for user {user_id}, story {story_id}")
        return None

    npc_voices = result[0][0]
    if isinstance(npc_voices, str):
        npc_voices = json.loads(npc_voices)

    # Получить голос для конкретного NPC
    npc_voice = npc_voices.get(str(npc_id))

    if not npc_voice:
        logger.warning(f"No voice assigned for NPC {npc_id}")
        return None

    # Вернуть в формате [language, voice_id, gender]
    return [
        npc_voice['language'],
        npc_voice['voice_id'],
        npc_voice['gender']
    ]


async def generate_npc_voice_message(
        pool,
        user_id: int,
        story_id: int,
        npc_id: int,
        text: str
) -> Optional[str]:
    """
    Сгенерировать голосовое сообщение для NPC

    ЛОГИКА:
    1. Анализируем текст на наличие звуковых паттернов (GRRRAAAHHHH и т.д.)
    2. Если найден паттерн -> используем предзаписанный звук
    3. Иначе -> генерируем через TTS

    Args:
        pool: Database pool
        user_id: ID пользователя
        story_id: ID истории
        npc_id: ID NPC
        text: Текст для озвучки (ответ от AI)

    Returns:
        Путь к .ogg файлу или None
    """

    # 0. Проверяем, есть ли в тексте звуковые эффекты
    should_use_sfx, sfx_path, cleaned_text = detect_sound_effect(text)

    if should_use_sfx and sfx_path:
        logger.info(f"Using pre-recorded sound effect for NPC {npc_id}: {sfx_path}")

        # TODO: В будущем можно комбинировать SFX + TTS для оставшегося текста
        # if len(cleaned_text) > 10:
        #     tts_path = await generate_tts(cleaned_text, ...)
        #     return combine_audio(sfx_path, tts_path)

        return sfx_path

    # 1: Паттерны не найдены - используем обычный TTS
    logger.info(f"Using TTS for NPC {npc_id}: '{text[:50]}...'")

    # Получить параметры голоса
    voice_params = await get_npc_voice_params(pool, user_id, story_id, npc_id)

    if not voice_params:
        logger.error(f"Cannot generate voice: no params for NPC {npc_id}")
        return None

    # 2. Генерировать аудио через существующую функцию
    try:


        # Вызов вашей функции
        audio_file_path = await myF.afTxtToOGG(text, voice_params)

        logger.info(f"Generated voice for NPC {npc_id}: {audio_file_path}")
        return audio_file_path

    except Exception as e:
        logger.error(f"Error generating voice for NPC {npc_id}: {e}", exc_info=True)
        return None



# ============================================================================
# SOUND EFFECTS CONFIGURATION
# ============================================================================

# Глобальная карта паттернов звуковых эффектов
SOUND_EFFECT_PATTERNS = {
    # Zombie sounds
    'zombie_growl': {
        'patterns': [r'GR+A+H+', r'GR+'],
        'files': ['zombie_growl_1.ogg', 'zombie_growl_2.ogg']
    },
    'zombie_moan': {
        'patterns': [r'U+H+'],
        'files': ['zombie_moan_1.ogg']
    },
}

# Путь к звуковым эффектам
SFX_BASE_PATH = Path("handlers/learnpath/audio/sfx")


# ============================================================================
# SOUND EFFECT DETECTION
# ============================================================================

def detect_sound_effect(text: str) -> Tuple[bool, Optional[str], str]:
    """
    Анализирует текст на наличие звуковых паттернов

    Args:
        text: Текст ответа NPC от AI

    Returns:
        (should_use_sfx, sfx_file_path, cleaned_text)
        - should_use_sfx: True если нужен звуковой эффект
        - sfx_file_path: Путь к звуку или None
        - cleaned_text: Текст без звуковых паттернов
    """

    text_upper = text.upper()

    # Проверяем все паттерны
    for sound_name, sound_data in SOUND_EFFECT_PATTERNS.items():
        for pattern in sound_data['patterns']:
            match = re.search(pattern, text_upper, re.IGNORECASE)

            if match:
                # Нашли паттерн!
                logger.info(f"Found sound pattern: {pattern} -> {sound_name}")

                # Выбираем случайный звуковой файл
                sound_file = random.choice(sound_data['files'])

                # Определяем категорию (zombie/human/etc) по префиксу
                #category = sound_file.split('_')[0]  # zombie_growl_1.ogg -> zombie
                #не используется, пока все в одной папке лежит

                sfx_file_path = SFX_BASE_PATH / sound_file #category / sound_file

                if sfx_file_path.exists():
                    # Убираем паттерн из текста
                    cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
                    cleaned_text = re.sub(r'[.\s]+', ' ', cleaned_text).strip()

                    logger.info(f"Original: '{text}'")
                    logger.info(f"SFX file: {sfx_file_path}")
                    if cleaned_text:
                        logger.info(f"Remaining text: '{cleaned_text}'")

                    return True, str(sfx_file_path), cleaned_text
                else:
                    logger.warning(f"Sound file not found: {sfx_file_path}")

    # Паттерны не найдены
    return False, None, text


def apply_voice_override(
        npc_response: Dict[str, Any],
        npc_name: str,
        scene_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Применить voice override если он определён в scene_context

    Args:
        npc_response: Ответ от AI
        npc_name: Имя NPC
        scene_context: Контекст сцены (с npc_behavior_overrides)

    Returns:
        Обновлённый npc_response (или оригинальный если override нет)
    """

    # Проверяем, есть ли override для этого NPC
    npc_overrides = scene_context.get('npc_behavior_overrides', {})
    npc_override = npc_overrides.get(npc_name, {})
    voice_override = npc_override.get('voice_override')

    if not voice_override:
        # Нет override - возвращаем как есть
        return npc_response

    mode = voice_override.get('mode', 'normal')

    if mode == 'normal':
        # Обычная речь
        return npc_response

    elif mode == 'sfx_only':
        # Полная замена на звуковой эффект
        available_sounds = voice_override.get('available_sounds', [])
        fallback_pattern = voice_override.get('fallback_pattern', 'GRRRAAAHHHH')

        # Выбираем случайный звук
        if available_sounds:
            # Комбинируем 1-2 случайных звука
            num_sounds = random.randint(1, 2)
            selected = random.sample(available_sounds, min(num_sounds, len(available_sounds)))

            # Преобразуем в текстовые паттерны
            sound_map = {
                'zombie_growl': 'GRRRAAAHHHH',
                'zombie_moan': 'UUUHHHHH',
                'zombie_groan': 'GROOOAN',
                'zombie_gurgle': '*gurgling*',
                'zombie_attack': 'AARRGGHHH',
                'zombie_brains': 'BRAAAINS'
            }

            patterns = [sound_map.get(s, 'GRRRAAAHHHH') for s in selected]
            new_text = '... '.join(patterns) + '...'
        else:
            new_text = fallback_pattern

        # Сохраняем оригинальный текст для логирования
        original_text = npc_response.get('response', '')

        logger.info(f"Voice override applied for {npc_name}:")
        logger.info(f"  Original: '{original_text}'")
        logger.info(f"  Replaced: '{new_text}'")

        # Заменяем текст
        npc_response['response'] = new_text

        # Опционально: добавить action если его не было
        if not npc_response.get('npc_action'):
            npc_response['npc_action'] = 'advances slowly, arms reaching'

        return npc_response

    elif mode == 'hybrid':
        # Гибридный режим - AI может комбинировать текст и звуки
        # Ничего не делаем, AI сам решил
        return npc_response

    return npc_response


def check_voice_override(
        npc_name: str,
        scene_context: Dict[str, Any]
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Проверить, нужен ли voice override для этого NPC

    Args:
        npc_name: Имя NPC
        scene_context: Контекст сцены

    Returns:
        (should_override, voice_override_config)
        - should_override: True если нужен override
        - voice_override_config: Конфиг или None
    """

    npc_overrides = scene_context.get('npc_behavior_overrides', {})
    npc_override = npc_overrides.get(npc_name, {})
    voice_override = npc_override.get('voice_override')

    if not voice_override:
        return False, None

    mode = voice_override.get('mode', 'normal')

    if mode == 'sfx_only':
        return True, voice_override

    return False, None


def generate_sfx_response(
        voice_override: Dict[str, Any],
        npc_name: str,
        user_input: str
) -> Dict[str, Any]:
    """
    Сгенерировать ответ со звуковыми эффектами БЕЗ AI

    Args:
        voice_override: Конфиг voice override
        npc_name: Имя NPC
        user_input: Что сказал пользователь

    Returns:
        Структура npc_response (как от AI)
    """

    available_sounds = voice_override.get('available_sounds', [])
    fallback_pattern = voice_override.get('fallback_pattern', 'GRRRAAAHHHH')

    # Выбираем 1-2 случайных звука
    if available_sounds:
        num_sounds = random.randint(1, 2)
        selected = random.sample(available_sounds, min(num_sounds, len(available_sounds)))

        # Преобразуем в текстовые паттерны
        sound_map = {
            'zombie_growl': 'GRRRAAAHHHH',
            'zombie_moan': 'UUUHHHHH',
            'zombie_groan': 'GROOOAN',
            'zombie_gurgle': '*gurgling*',
            'zombie_attack': 'AARRGGHHH',
            'zombie_brains': 'BRAAAINS',
            'monster_roar': 'ROOOAAAR',
            'monster_hiss': 'HSSSSS'
        }

        patterns = [sound_map.get(s, 'GRRRAAAHHHH') for s in selected]
        sfx_text = '... '.join(patterns) + '...'
    else:
        sfx_text = fallback_pattern

    # Выбираем случайное действие
    actions = [
        'advances slowly, arms reaching',
        'lurches forward menacingly',
        'staggers toward you, groaning',
        'turns toward you with dead eyes',
        'shambles closer, mouth open'
    ]

    action = random.choice(actions)

    logger.info(f"Generated SFX response for {npc_name}: {sfx_text}")

    return {
        'response': sfx_text,
        'correction': '',  # Нет коррекции для звуков
        'npc_action': action,
        'text_trs': {
            'ru': f'[звуки зомби: {sfx_text}]'
        },
        'correction_trs': {},
        'npc_id': None,  # Будет добавлено позже
        'npc_name': npc_name
    }

def ________report():
    pass


async def generate_story_report(user_id: int, story_id: int, pool) -> dict:
    """
    Генерирует отчет по результатам прохождения истории

    Args:
        user_id: ID пользователя
        story_id: ID истории
        pool: Database connection pool (pool_base, pool_log)

    Returns:
        dict: {
            'text': str,  # Форматированный HTML текст отчета
            'metrics': dict,  # Сырые метрики для сохранения в БД
        }
    """
    pool_base, pool_log = pool

    try:
        # 1. Получаем все сообщения пользователя из истории
        user_messages = await get_user_story_messages(user_id, story_id, pool_base)

        if not user_messages or len(user_messages) == 0:
            raise ValueError("No messages found for this story")

        # 2. БОНУС: Получаем исправления AI-тьютора
        corrections = await get_user_corrections(user_id, story_id, pool_base)

        # 3. Объединяем все ответы в один текст
        full_text = " ".join(user_messages)

        # 4. Считаем базовые метрики (быстро, без AI)
        basic_metrics = calculate_basic_metrics(full_text)

        # 5. Получаем AI-анализ (грамматика, конструкции, уровень)
        # Передаем corrections для более точного анализа
        ai_analysis = await get_ai_analysis(full_text, user_messages, corrections, pool, user_id)

        # 6. Формируем текст отчета
        report_text = format_report(basic_metrics, ai_analysis)

        # 6b костыль для стартовой истории
        report_text = (
            f'😢 Рыбку жалко... но это была отличная практика английского!\n\n'
            f'{report_text}'
        )

        # 7. Логируем в БД
        await log_report_generation(pool_log, user_id, story_id)

        # 8. (Опционально) Сохраняем метрики для еженедельных отчетов
        # await save_report_metrics(user_id, story_id, basic_metrics, ai_analysis, pool_base)

        return {
            'text': report_text,
            'metrics': {**basic_metrics, **ai_analysis}
        }

    except Exception as e:
        logger.error(f"Error generating story report for user {user_id}, story {story_id}: {e}")
        raise


async def get_user_story_messages(user_id: int, story_id: int, pool_base) -> List[str]:
    """
    Получает все текстовые сообщения пользователя в конкретной истории

    Использует таблицу t_story_user_interactions:
    - c_user_input: текст сообщения пользователя (уже транскрибированный если был voice)
    - c_user_id, c_story_id: фильтры
    - c_timestamp: сортировка
    """

    async with pool_base.acquire() as conn:
        query = """
            SELECT c_user_input 
            FROM t_story_user_interactions 
            WHERE c_user_id = $1 AND c_story_id = $2 
              AND c_user_input IS NOT NULL
              AND c_user_input != ''
            ORDER BY c_timestamp
        """

        try:
            rows = await conn.fetch(query, user_id, story_id)

            # Извлекаем текст сообщений
            messages = [row['c_user_input'] for row in rows if row['c_user_input']]

            logger.info(f"Found {len(messages)} messages for user {user_id}, story {story_id}")

            return messages

        except Exception as e:
            logger.error(f"Error fetching user messages from t_story_user_interactions: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"user_id={user_id}, story_id={story_id}")
            # Возвращаем пустой список вместо ошибки для graceful fallback
            return []


async def get_user_corrections(user_id: int, story_id: int, pool_base) -> List[str]:
    """
    БОНУС: Получает исправления AI-тьютора для более точного анализа ошибок

    Использует поле c_correction из t_story_user_interactions
    """

    async with pool_base.acquire() as conn:
        query = """
            SELECT c_correction 
            FROM t_story_user_interactions 
            WHERE c_user_id = $1 AND c_story_id = $2 
              AND c_correction IS NOT NULL
              AND c_correction != ''
              AND c_correction NOT IN ('Great job!', 'N/A', 'No corrections')
            ORDER BY c_timestamp
        """

        try:
            rows = await conn.fetch(query, user_id, story_id)
            corrections = [row['c_correction'] for row in rows if row['c_correction']]

            logger.info(f"Found {len(corrections)} corrections for user {user_id}, story {story_id}")

            return corrections

        except Exception as e:
            logger.error(f"Error fetching corrections: {e}")
            return []


def calculate_basic_metrics(text: str) -> dict:
    """
    Считает простые метрики без использования AI

    Args:
        text: Весь текст сообщений пользователя

    Returns:
        dict: Базовые метрики
    """

    # Очистка текста
    words = text.split()
    words = [w.strip('.,!?;:') for w in words if w.strip()]

    # Разделение на предложения (упрощенно)
    sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]

    # Уникальные слова (lowercase для корректности)
    unique_words = set(w.lower() for w in words)

    # Средняя длина предложения
    avg_sentence_length = len(words) / len(sentences) if sentences else 0

    # Lexical diversity (Type-Token Ratio)
    lexical_diversity = len(unique_words) / len(words) if words else 0

    return {
        'total_words': len(words),
        'unique_words': len(unique_words),
        'total_sentences': len(sentences),
        'avg_sentence_length': round(avg_sentence_length, 1),
        'lexical_diversity': round(lexical_diversity, 2)
    }


async def get_ai_analysis(full_text: str, messages: List[str], corrections: List[str], pool, user_id: int) -> dict:
    """
    Отправляет текст в OpenAI для детального анализа

    Args:
        full_text: Весь текст пользователя
        messages: Список отдельных сообщений
        corrections: Список исправлений от AI-тьютора
        pool: Database pool для логирования токенов
        user_id: ID пользователя

    Returns:
        dict: Результаты AI-анализа
    """

    pool_base, _ = pool

    # Импортируем функцию из selfFunctions
    import selfFunctions as myF

    # Формируем дополнительный контекст из corrections
    corrections_context = ""
    if corrections:
        corrections_context = f"\n\nAI TUTOR CORRECTIONS DURING DIALOGUE:\n" + "\n".join(f"- {c}" for c in corrections)

    # Формируем промпт для анализа
    user_prompt = f"""
Analyze the following English text from a user who practiced English in an interactive story.

USER'S TEXT:
{full_text}
{corrections_context}

Evaluate these parameters and respond ONLY in JSON format:

1. **grammar_accuracy** (0-100): How grammatically correct is the text overall. Put 100 if there were no grammar mistakes.
2. **verb_tenses**: List of verb tenses used (e.g., ["Present Simple", "Past Simple", "Present Perfect"])
3. **modal_verbs**: List of modal verbs used (e.g., ["can", "should", "must"])
4. **conditionals**: Type of conditionals used (e.g., "Type 1", "Type 2", "not used")
5. **complex_structures**: List of complex structures used (e.g., ["passive_voice", "phrasal_verbs", "relative_clauses"])
6. **cefr_level**: Estimated CEFR level (A1, A2, B1, B1+, B2, B2+, C1, C2)
7. **top_errors**: Top 3 error types based on corrections (e.g., ["articles", "prepositions", "verb_tenses"])
8. **recommendation**: Brief recommendation for next practice (in Russian, 1-2 sentences)
9. **explanation**: Explanation for chosen level of grammar_accuracy parameter 

JSON FORMAT:
{{
  "grammar_accuracy": 85,
  "verb_tenses": ["Present Simple", "Past Simple"],
  "modal_verbs": ["can", "would"],
  "conditionals": "Type 1",
  "complex_structures": ["phrasal_verbs"],
  "cefr_level": "B1",
  "top_errors": ["articles", "prepositions"],
  "recommendation": "Попробуй использовать Present Perfect в следующей истории для описания опыта",
  "explanation": Необходимо использовать is с news, например, What is the news? Слово news — это неисчисляемое существительное в английском. Оно выглядит как множественное (на -s), но грамматически — единственное число.
}}

IMPORTANT: Respond ONLY with valid JSON, no additional text.
"""

    system_prompt = "You are an expert English language teacher specialized in CEFR assessment and grammar analysis."

    try:
        # Вызываем OpenAI через функцию из selfFunctions
        # iModel=0 означает gpt-4o-mini
        # toggleParam=2 означает использовать system prompt
        response = await myF.afSendMsg2AI(user_prompt, pool_base, user_id, toggleParam=2, systemPrompt=system_prompt)

        # Парсим JSON ответ
        # Убираем возможные markdown backticks
        response_clean = response.strip()
        if response_clean.startswith('```json'):
            response_clean = response_clean[7:]
        if response_clean.startswith('```'):
            response_clean = response_clean[3:]
        if response_clean.endswith('```'):
            response_clean = response_clean[:-3]
        response_clean = response_clean.strip()

        analysis = json.loads(response_clean)

        # Валидация структуры
        required_keys = ['grammar_accuracy', 'verb_tenses', 'modal_verbs',
                         'conditionals', 'complex_structures', 'cefr_level',
                         'top_errors', 'recommendation', 'explanation']

        for key in required_keys:
            if key not in analysis:
                logger.warning(f"Missing key in AI response: {key}")
                analysis[key] = _get_fallback_value(key)

        return analysis

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        logger.error(f"Response was: {response}")
        return _get_fallback_analysis()

    except Exception as e:
        logger.error(f"Error in AI analysis: {e}")
        return _get_fallback_analysis()


def _get_fallback_value(key: str) -> Any:
    """Возвращает fallback значение для ключа"""
    fallbacks = {
        'grammar_accuracy': 75,
        'verb_tenses': ['Present Simple'],
        'modal_verbs': [],
        'conditionals': 'не использовал',
        'complex_structures': [],
        'cefr_level': 'B1',
        'top_errors': [],
        'recommendation': 'Продолжай практиковаться!',
        'explanation': ''
    }
    return fallbacks.get(key, None)


def _get_fallback_analysis() -> dict:
    """Возвращает полный fallback анализ если AI не ответил"""
    return {
        'grammar_accuracy': 75,
        'verb_tenses': ['Present Simple'],
        'modal_verbs': [],
        'conditionals': 'не использовал',
        'complex_structures': [],
        'cefr_level': 'B1',
        'top_errors': [],
        'recommendation': 'Продолжай практиковаться с историями!',
        'explanation': ''
    }


def format_report(basic: dict, ai: dict) -> str:
    """
    Формирует красивый HTML отчет

    Args:
        basic: Базовые метрики
        ai: AI-анализ

    Returns:
        str: HTML-форматированный отчет
    """

    # Эмодзи для уровня
    level_emoji = {
        'A1': '🌱', 'A2': '🌿',
        'B1': '🌳', 'B1+': '🌳',
        'B2': '🌲', 'B2+': '🌲',
        'C1': '🏆', 'C2': '👑'
    }
    emoji = level_emoji.get(ai['cefr_level'], '📊')

    # Конвертируем списки в читаемый формат
    tenses_str = ", ".join(ai['verb_tenses']) if ai['verb_tenses'] else "—"
    modals_str = ", ".join(ai['modal_verbs']) if ai['modal_verbs'] else "—"
    structures_list = ai['complex_structures'] if ai['complex_structures'] else []

    # Переводим структуры на русский
    structure_translations = {
        'passive_voice': 'пассивный залог',
        'phrasal_verbs': 'фразовые глаголы',
        'relative_clauses': 'придаточные предложения',
        'complex_sentences': 'сложноподчинённые предложения'
    }
    structures_ru = [structure_translations.get(s, s) for s in structures_list]
    structures_str = ", ".join(structures_ru) if structures_ru else "пока не использовал"

    # Определяем сложность предложений
    sentence_complexity = _get_sentence_complexity(basic['avg_sentence_length'])

    # Формируем отчет
    report = f"""
<b>📊 Твой результат за эту историю</b>

• Слов использовано: <b>{basic['total_words']}</b> (уникальных: {basic['unique_words']})
• Средняя сложность предложений: <b>{sentence_complexity}</b> ({basic['avg_sentence_length']} слов)
• Грамматическая точность: <b>{ai['grammar_accuracy']}%</b> {'✅' if ai['grammar_accuracy'] >= 80 else '⚠️'}

<i>{ai['explanation']}</i>

<b>🎯 Что ты использовал</b>

• Времена глаголов: {tenses_str}
• Модальные глаголы: {modals_str}
• Условные предложения: {ai['conditionals']}
• Сложные конструкции: {structures_str}

<b>{emoji} Твой уровень: {ai['cefr_level']}</b>

<b>💡 Что улучшить</b>

{ai['recommendation']}
"""

    return report.strip()


def _get_sentence_complexity(avg_length: float) -> str:
    """Определяет уровень сложности по длине предложений"""
    if avg_length < 8:
        return "A2 (простые предложения)"
    elif avg_length < 12:
        return "B1 (средней сложности)"
    elif avg_length < 16:
        return "B2 (сложные)"
    else:
        return "C1+ (очень сложные)"


async def log_report_generation(pool_log, user_id: int, story_id: int):
    """Логирует факт генерации отчета"""
    import fpgDB as pgDB
    await pgDB.fExec_LogQuery(pool_log, user_id, f"story_report_generated|story:{story_id}")


async def save_report_metrics(user_id: int, story_id: int,
                              basic: dict, ai: dict, pool_base):
    """
    Сохраняет метрики в БД для еженедельных отчетов

    TODO: ОПЦИОНАЛЬНО - создать таблицу story_reports если нужно

    CREATE TABLE IF NOT EXISTS story_reports (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        story_id INTEGER NOT NULL,
        total_words INTEGER,
        unique_words INTEGER,
        grammar_accuracy INTEGER,
        cefr_level VARCHAR(5),
        created_at TIMESTAMP DEFAULT NOW()
    );
    """

    async with pool_base.acquire() as conn:
        query = """
            INSERT INTO story_reports 
            (user_id, story_id, total_words, unique_words, 
             grammar_accuracy, cefr_level, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW())
        """
        try:
            await conn.execute(
                query,
                user_id, story_id,
                basic['total_words'], basic['unique_words'],
                ai['grammar_accuracy'], ai['cefr_level']
            )
        except Exception as e:
            logger.warning(f"Could not save report metrics (table may not exist): {e}")
            # Не падаем если таблицы нет - это опциональная функция


def _______new():
    pass

