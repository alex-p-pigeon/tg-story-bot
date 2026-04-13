from aiogram import Router, F, types, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
import re

from aiogram.types import BufferedInputFile

from aiogram.types import Message, ReplyKeyboardRemove, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup

from datetime import datetime, date, timezone, timedelta
import hashlib
import os, sys


import json

import random

# custom
import mynaming as myN
from states import myState
import selfFunctions as myF
import prompt as myP
import fpgDB as pgDB
import fPayment as myPay

from aiogram import types

from config_reader import config

import logging

logger = logging.getLogger(__name__)

# Create router for tech handlers
r_start = Router()

#d = gender.Detector()


# ------------------------------------------------------------------------------------- Команда start
@r_start.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext, pool, dp):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    nlp_tools = dp.workflow_data["nlp_tools"]
    gender_detector = nlp_tools.gender_detector




    isExist = await f_create_user(vUserID, pool, message)  # проверка, есть ли пользователь в БД, если нет, то создание
    if isExist:
        await myF.fRemoveReplyKB(message_obj=message)  # удаление ReplyKB
    else:

        await state.update_data(discount=1)     # запись в redis discount = 1
        await state.update_data(menu_command_disabled=True)  # статус для работы кнопки команды menu




    #await vA_st0___f_init(message, state, pool, gender_detector)  # отправка сообщения
    await vB_st1___story(message, state, pool)  # отправка сообщения


async def f_create_user(vUserID, pool, message: types.Message):
    pool_base, pool_log = pool
    vMark = 0
    if len(message.text.split()) > 1:
        parameter = message.text.split()[1]
        vMark = await myF.vGetcMark(pool_base, parameter)
        # print('vMark - ', vMark)

    # проверка, есть ли пользователь в БД, если нет, то создание
    # ---------------------------------------------------------------------
    var_query = (
        f"SELECT c_user_id, c_subscription_status "
        f"FROM t_user "
        f"WHERE c_user_id = '{vUserID}'"
    )
    v_queryRes = await pgDB.fExec_SelectQuery(pool_base, var_query)
    # print('message.chat.id = ', message.chat.id, ' v_queryRes = ', v_queryRes)
    if (v_queryRes is None) or len(v_queryRes) <= 0:  # ajrm не вызовет ли ошибку?
        isExist = False
        arrQuery = []
        var_query = (
            f"INSERT INTO t_user (c_user_id, c_subscription_status, c_balance, c_mark, c_discount) "
            f"VALUES ('{vUserID}', 3, 1000, {vMark}, 1) "
            f"ON CONFLICT (c_user_id) DO NOTHING"
        )  # запись в таблицу t_user
        arrQuery.append(var_query)  # накопление массива запросов для транзакции
        v_DateToday = date.today().strftime("%Y%m%d")
        var_query = (
            f"INSERT INTO t_daily (c_user_id, c_date, c_pick_out, c_repeat, c_lnr, c_retell, c_dial_news, c_dial_situation, c_monolog, c_oxford3, c_edu) "
            f"VALUES ('{vUserID}', '{v_DateToday}', 0, 0, 0, 0, 0, 0, 0, 0, 1) "
            f"ON CONFLICT (c_user_id) DO NOTHING"
        )  # запись в таблицу t_daily
        arrQuery.append(var_query)  # накопление массива запросов для транзакции
        # запись в БД уровня по умолчанию -B
        var_query = (
            f"INSERT INTO t_user_paramssingle (c_ups_user_id, c_ups_eng_level, c_timezone)  "
            f"VALUES ('{vUserID}', 2, 180) "
            f"ON CONFLICT (c_ups_user_id) DO NOTHING"
        )  # запись в таблицу t_user_paramssingle
        arrQuery.append(var_query)  # накопление массива запросов для транзакции
        var_query = (
            f"INSERT INTO t_user_paramsplural (c_upp_user_id, c_upp_type, c_upp_value, c_upp_value_date_change) "
            f"VALUES ('{vUserID}', '1', '09:00', CURRENT_TIMESTAMP::timestamp)"
        )  # запись в таблицу t_user_paramsplural
        # f"VALUES ('{message.chat.id}', '1', '09:00'), ('{message.chat.id}', '1', '19:00')"
        arrQuery.append(var_query)  # накопление массива запросов для транзакции
        var_query = (
            f"INSERT INTO t_msg_id (c_user_id, c_msg_id) "
            f"VALUES ('{vUserID}', 0) "
            f"ON CONFLICT (c_user_id) DO NOTHING"
        )  # запись в таблицу t_user
        arrQuery.append(var_query)  # накопление массива запросов для транзакции

        await pgDB.fExec_UpdateArrQuery(pool_base, arrQuery)  # выполнение транзакции
        arrQuery = []

    else:
        isExist = True

        # Проверяем, был ли пользователь заблокирован (статус 10)
        current_status = int(v_queryRes[0][1])  # c_subscription_status

        if current_status == 10:
            # Восстанавливаем статус при разблокировке  AJRM не хватает c_mark
            var_query = (
                f"UPDATE t_user "
                f"SET c_subscription_status = 3, "
                f"    c_free_actions_count = 0, "
                f"    c_free_actions_date = NULL, "
                f"    c_mark = $1"
                f"WHERE c_user_id = $2"
            )
            await pgDB.fExec_UpdateQuery_args(pool_base, var_query, vMark, vUserID)
    return isExist


def ______vB():
    pass

async def vB_st1___story(message, state, pool):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot

    story_id = 21

    str_Msg = '''
👋 <b>Welcome to LingoMojo!</b> 

Сейчас мы пройдем <b>обучающую</b> историю - 📍 <b>The Garden Encounter</b> (<i>Встреча в саду</i>):

You stand in your garden, watching Laura dig a large hole next door. The sun is shining, and birds chirp in the distance.
<blockquote expandable='true'><tg-spoiler>Вы стоите в своем саду и наблюдаете, как Laura копает большую яму рядом. Солнце светит, и птицы щебечут вдали.</tg-spoiler></blockquote>
    '''

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Далее ❱❱',callback_data=f"vB_st1_2"
    ))

    msg = await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

    await state.update_data(str_Msg=str_Msg)
    #from .oth_handlers import handle_story_start
    #await handle_story_start(None, state, pool, story_id, message = message)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'vB_st1___story|')


@r_start.callback_query(F.data == "vB_st1_2")
async def vB_st2___clbck_story_st2(callback, state, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    user_data = await state.get_data()
    str_Msg = user_data.get('str_Msg', '')

    await state.set_state(myState.task8_story_active)

    story_id = 21

    str_Msg = '''
📍 <b>The Garden Encounter</b> 
    
Теперь перейдем к 🎯 <b>целям</b> сцены.
    
🎯 <b>Objectives:</b> Have a conversation with Laura and learn what happened
<blockquote expandable='true'>Поговорите с Laura и узнайте, что случилось</blockquote>
⬜️ Greet Laura and ask what she is doing
⬜️ Ask why the hole is so big

Далее нажми кнопку 1️⃣ Laura и запиши голосовое или тексовое сообщение - <b>Hi! What are you doing?</b>
        '''

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='1️⃣ Laura', callback_data=f"talk:73"))

    msg_p = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)



    #создание обязательных реквизитов сцены для пользователя
    #-------------------------------------------------------------------------------------------------------------------
    from .oth_handlers import reset_user_story_progress
    await reset_user_story_progress(pool, vUserID, story_id)
    try:
        # Создаем engine
        from .learnpath.story.engines.interactive_story_engine import InteractiveStoryEngine
        engine = InteractiveStoryEngine(pool, vUserID)

        # Получаем ID первой сцены (минимальный запрос)
        query = """
            SELECT c_scene_id
            FROM t_story_scenes
            WHERE c_story_id = $1
            ORDER BY c_scene_number
            LIMIT 1
        """

        result = await pgDB.fExec_SelectQuery_args(pool_base, query, story_id)

        scene_id = result[0][0]

        # ✅ Создать прогресс с инициализацией инвентаря
        await engine._create_user_progress(story_id, scene_id, state)

        # ✅ Загрузить созданный прогресс (с инвентарем!)
        user_progress = await engine._get_user_progress(story_id)

        # ✅ Получить полные данные сцены через generate_scene_description
        # (он сам сделает SELECT и парсинг всех JSONB полей)
        scene_data = await engine.dialogue_engine.generate_scene_description(
            scene_id=scene_id,
            story_id=story_id,
            user_progress=user_progress  # ✅ С реальным инвентарем!
        )
        logger.info(f'-------------user_progress:{user_progress}')
        logger.info(f'--------------scene_data0:{scene_data}')
        # ✅ Обогатить NPC info (имена для кнопок)
        from .learnpath.handlers.story import _enrich_scene_with_npc_info
        scene_data = await _enrich_scene_with_npc_info(pool_base, scene_data)
        logger.info(f'--------------scene_data:{scene_data}')
        npcs_info = scene_data.get('npcs_info', [])

        #await show_scene(message, state, scene_data, pool)
        await state.update_data(
            msg_id=msg_p.message_id,
            npcs_info=npcs_info,
            # str_npc_list=str_npc_list,
            current_scene_id=scene_id,
            task8_story_id=story_id,
            task8_active_npc_id=None
        )

        # Переходим в режим активной истории
        await state.set_state(myState.task8_story_active)

    except Exception as e:
        logger.error(f"Error loading first scene: {e}", exc_info=True)

    #-------------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------

    # from .oth_handlers import handle_story_start
    # await handle_story_start(None, state, pool, story_id, message = message)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'vB_st1___clbck_story_st2|')



@r_start.callback_query(F.data == "vB_st2")
async def vB_st2___clbck_anketa_ICP(callback, state, pool):
    """Инициализация анкеты выбора ICP с toggle кнопками"""
    await state.set_state(myState.varB_st2)

    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    # Инициализация toggle для ICP (только эмодзи в кнопках)
    toggle = {
        '1': {'ind': "0", 'emoji': '🌍', 'desc': 'Нужен для жизни в другой стране'},
        '2': {'ind': "0", 'emoji': '💼', 'desc': 'Хочу лучшую работу или повышение'},
        '3': {'ind': "0", 'emoji': '✈️', 'desc': 'Свободно общаться в путешествиях'},
        '4': {'ind': "0", 'emoji': '🎬', 'desc': 'Фильмы, игры, книги в оригинале'},
    }

    # Формируем текст с описаниями
    descriptions = "\n".join([
        f"{data['emoji']} {data['desc']}"
        for key, data in sorted(toggle.items(), key=lambda x: int(x[0]))
    ])

    str_Msg = f'''🎯 Здорово! Чтобы подобрать лучшие истории для тебя, ответь:

<b>Зачем тебе английский прямо сейчас?</b>

{descriptions}

<i>Выбери 1-2 варианта:</i>'''

    await state.update_data(
        toggle_icp=toggle,
        selected_icp=[]
    )

    builder = vB_st2___f_builder(toggle)

    msg = await callback.message.answer(
        str_Msg,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await pgDB.fExec_LogQuery(pool_log, vUserID, 'vB_st2___clbck_anketa_ICP|init')



@r_start.callback_query(F.data.startswith("vB_st2_"))
async def vB_st2___clbck_toggle(callback: types.CallbackQuery, state: FSMContext, pool):
    """Обработка toggle нажатий на кнопки ICP"""
    await state.set_state(myState.varB_st2)

    vUserID = callback.message.chat.id
    pool_base, pool_log = pool

    # Извлекаем номер кнопки из callback data
    button_num = callback.data.split("_")[-1]

    # Получаем текущее состояние toggle
    user_data = await state.get_data()
    toggle = user_data.get('toggle_icp', {})

    # Переключаем выбранную кнопку
    if button_num in toggle:
        current_state = toggle[button_num].get('ind', '0')
        new_state = '1' if current_state == '0' else '0'

        # Проверяем лимит выбора (максимум 2)
        selected_count = sum(1 for v in toggle.values() if v.get('ind') == '1')

        if new_state == '1' and selected_count >= 2:
            # Если пытаемся выбрать 3-й вариант - показываем предупреждение
            await callback.answer('⚠️ Можно выбрать максимум 2 варианта', show_alert=True)
            return

        # Переключаем состояние
        toggle[button_num]['ind'] = new_state

    # Сохраняем список выбранных ICP для следующего этапа
    selected_icp = [key for key, val in toggle.items() if val.get('ind') == '1']

    # Обновляем state
    await state.update_data(
        toggle_icp=toggle,
        selected_icp=selected_icp
    )

    # Регенерируем клавиатуру
    builder = vB_st2___f_builder(toggle)

    # Обновляем сообщение
    try:
        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    except Exception as e:
        logger.error(f"Error updating markup: {e}")

    await pgDB.fExec_LogQuery(
        pool_log,
        vUserID,
        f'vB_st2___clbck_toggle|button:{button_num}|selected:{selected_icp}'
    )


def vB_st2___f_builder(toggle):
    """Создаёт клавиатуру с ICP selection toggles - только эмодзи"""
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки - только эмодзи
    for key in sorted(toggle.keys(), key=int):
        button_data = toggle[key]
        emoji = button_data['emoji']
        is_selected = button_data['ind'] == '1'

        # Добавляем галочку если выбрано
        text = f"✅ {emoji}" if is_selected else emoji

        builder.add(types.InlineKeyboardButton(
            text=text,
            callback_data=f"vB_st2_{key}"
        ))

    # Добавляем кнопку "Далее"
    builder.add(types.InlineKeyboardButton(
        text="Далее →",
        callback_data="vB_st3"
    ))

    # Layout: 4 кнопки в одну строку + кнопка "Далее"
    builder.adjust(4, 1)

    return builder


# Словарь с болями для каждого ICP (в порядке приоритета)
PAIN_POINTS = {
    '1': [  # Нужен для жизни в другой стране
        'Познакомился с классными людьми, но не смог пообщаться',
        'Уже здесь 3 месяца, но до сих пор заказываю еду жестами',
        'Чувствую себя как ребенок — зависим от тех кто переводит',
        'Коллеги шутят, а я просто улыбаюсь — не понимаю',
        'Звонки по телефону — это кошмар, ничего не понимаю',
        'Скоро переезжаю, боюсь не справиться',
    ],
    '2': [  # Хочу лучшую работу или повышение
        'Читаю тех доки легко, но на созвонах теряюсь',
        'Знаю ответ на интервью, но не могу сформулировать',
        'Сверстники уже работают в FAANG, а я застрял',
        'Молчу на встречах, хотя есть что сказать',
        'Видел вакансию мечты, но требуют fluent English',
        'Коллеги берут интересные проекты — мне не предлагают',
    ],
    '3': [  # Свободно общаться в путешествиях
        'В последней поездке весь отпуск показывал пальцем',
        'Хочу узнать местные места, но не могу спросить',
        'Учу фразы перед поездкой — через неделю всё забыл',
        'Не понимаю таксиста — в итоге везет не туда',
        'Экскурсии на английском дешевле, но я не понимаю',
        'Боюсь потеряться — не смогу объяснить адрес',
    ],
    '4': [  # Просто интересно (фильмы, игры, книги)
        'Читаю книги с переводчиком — это не то',
        'В сериалах шутки не смешные в переводе',
        'Субтитры закрывают половину кадра',
        'Мемы не понимаю — пропускаю культурный контекст',
        'Слышу переводчика, а не настоящий голос актёра',
        'Смотрю только то, что перевели — выбора нет',
    ]
}

# Заголовки вопросов для каждого ICP
PAIN_QUESTIONS = {
    '1': '🤔 Что сейчас беспокоит больше всего?',
    '2': '💼 Что мешает твоему карьерному росту?',
    '3': '✈️ Что портит удовольствие от поездок?',
    '4': '🎬 Что бесит больше всего?',
}


def vB_st3___get_pain_distribution(selected_icp):
    """
    Распределяет боли в зависимости от количества выбранных ICP

    Args:
        selected_icp: список выбранных ICP (например ['1', '3'])

    Returns:
        list: список кортежей (icp_id, pain_text) в нужном порядке
    """
    num_selected = len(selected_icp)
    pains_to_show = []

    if num_selected == 0:
        return []

    elif num_selected == 1:
        # 1 ICP → 6 болей
        icp_id = selected_icp[0]
        for pain in PAIN_POINTS.get(icp_id, [])[:6]:
            pains_to_show.append((icp_id, pain))

    elif num_selected == 2:
        # 2 ICP → по 3 боли от каждого
        for icp_id in selected_icp:
            for pain in PAIN_POINTS.get(icp_id, [])[:3]:
                pains_to_show.append((icp_id, pain))

    elif num_selected == 3:
        # 3 ICP → по 2 боли от каждого
        for icp_id in selected_icp:
            for pain in PAIN_POINTS.get(icp_id, [])[:2]:
                pains_to_show.append((icp_id, pain))

    elif num_selected == 4:
        # 4 ICP → 2+2+1+1
        distribution = [2, 2, 1, 1]
        for idx, icp_id in enumerate(selected_icp):
            count = distribution[idx]
            for pain in PAIN_POINTS.get(icp_id, [])[:count]:
                pains_to_show.append((icp_id, pain))

    return pains_to_show


def vB_st3___get_question_text(selected_icp):
    """
    Формирует текст вопроса на основе выбранных ICP

    Args:
        selected_icp: список выбранных ICP

    Returns:
        str: текст вопроса
    """
    if len(selected_icp) == 1:
        # Если один ICP - используем его специфичный вопрос
        return PAIN_QUESTIONS.get(selected_icp[0], '🤔 Что откликается больше всего?')
    else:
        # Если несколько - общий вопрос
        return '🤔 Что откликается больше всего?'


@r_start.callback_query(F.data == "vB_st3")
async def vB_st3___clbck_anketa_pain(callback, state, pool):
    """Этап выбора болей на основе выбранных ICP"""
    await state.set_state(myState.varB_st3)

    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    user_data = await state.get_data()
    selected_icp = user_data.get('selected_icp', [])

    # Проверяем что хоть что-то выбрано
    if not selected_icp:
        await callback.answer('⚠️ Выбери хотя бы один вариант', show_alert=True)
        return

    # Получаем распределение болей
    pains_to_show = vB_st3___get_pain_distribution(selected_icp)

    if not pains_to_show:
        await callback.answer('⚠️ Ошибка загрузки вопросов', show_alert=True)
        return

    # Создаём toggle для болей с номерами
    toggle_pains = {}
    for idx, (icp_id, pain_text) in enumerate(pains_to_show, start=1):
        toggle_pains[str(idx)] = {
            'ind': '0',
            'desc': pain_text,
            'icp_id': icp_id,
            'number': f'{idx}️⃣'  # эмодзи с номером
        }

    # Формируем текст вопроса
    question_text = vB_st3___get_question_text(selected_icp)

    # Формируем список болей в тексте
    pains_list = "\n".join([
        f"{data['number']} {data['desc']}"
        for key, data in sorted(toggle_pains.items(), key=lambda x: int(x[0]))
    ])

    str_Msg = f'''{question_text}

{pains_list}

<i>Выбери что откликается (1-3 варианта):</i>'''

    await state.update_data(
        toggle_pains=toggle_pains,
        selected_pains=[]
    )

    builder = vB_st3___f_builder(toggle_pains)

    await callback.message.answer(
        str_Msg,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await pgDB.fExec_LogQuery(
        pool_log,
        vUserID,
        f'vB_st3___init|selected_icp:{selected_icp}|pains_count:{len(pains_to_show)}'
    )


@r_start.callback_query(F.data.startswith("vB_st3_"))
async def vB_st3___clbck_toggle(callback: types.CallbackQuery, state: FSMContext, pool):
    """Обработка toggle нажатий на кнопки болей"""
    await state.set_state(myState.varB_st3)

    vUserID = callback.message.chat.id
    pool_base, pool_log = pool

    # Извлекаем номер кнопки
    button_num = callback.data.split("_")[-1]

    # Получаем текущее состояние toggle
    user_data = await state.get_data()
    toggle_pains = user_data.get('toggle_pains', {})

    # Переключаем выбранную кнопку
    if button_num in toggle_pains:
        current_state = toggle_pains[button_num].get('ind', '0')
        new_state = '1' if current_state == '0' else '0'

        # Проверяем лимит выбора (максимум 3)
        selected_count = sum(1 for v in toggle_pains.values() if v.get('ind') == '1')

        if new_state == '1' and selected_count >= 3:
            await callback.answer('⚠️ Можно выбрать максимум 3 варианта', show_alert=True)
            return

        # Переключаем состояние
        toggle_pains[button_num]['ind'] = new_state

    # Сохраняем список выбранных болей
    selected_pains = [
        {
            'pain': val['desc'],
            'icp_id': val.get('icp_id')
        }
        for key, val in toggle_pains.items()
        if val.get('ind') == '1'
    ]

    # Обновляем state
    await state.update_data(
        toggle_pains=toggle_pains,
        selected_pains=selected_pains
    )

    # Регенерируем клавиатуру
    builder = vB_st3___f_builder(toggle_pains)

    # Обновляем сообщение
    try:
        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    except Exception as e:
        logger.error(f"Error updating markup: {e}")

    await pgDB.fExec_LogQuery(
        pool_log,
        vUserID,
        f'vB_st3___toggle|button:{button_num}|selected_count:{len(selected_pains)}'
    )


def vB_st3___f_builder(toggle_pains):
    """Создаёт клавиатуру с pain points selection toggles - только номера"""
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки - только номера
    for key in sorted(toggle_pains.keys(), key=int):
        button_data = toggle_pains[key]
        number = button_data['number']
        is_selected = button_data['ind'] == '1'

        # Добавляем галочку если выбрано
        text = f"✅ {number}" if is_selected else number

        builder.add(types.InlineKeyboardButton(
            text=text,
            callback_data=f"vB_st3_{key}"
        ))

    # Добавляем кнопку "Далее"
    builder.add(types.InlineKeyboardButton(
        text="Далее →",
        callback_data="vB_st4"
    ))

    # Layout: 3 кнопки в ряд (для 6 болей = 2 ряда) + кнопка "Далее"
    # Адаптируем под количество болей
    num_pains = len(toggle_pains)
    if num_pains == 6:
        builder.adjust(3, 3, 1)  # 2 ряда по 3 + Далее
    elif num_pains == 4:
        builder.adjust(2, 2, 1)  # 2 ряда по 2 + Далее
    else:
        builder.adjust(3, 1)  # по умолчанию

    return builder


# Список ценностей LingoMojo
VALUES_LIST = [
    '⚡ Чтобы затягивало, не было скучно',
    '🎭 Как в реальной жизни, не по учебникам',
    '🗣️ Больше говорить, меньше зубрить',
    '📈 Видеть свой прогресс',
    '⏱️ В любое время, когда удобно',
    '💎 Не переплачивать',
]


@r_start.callback_query(F.data == "vB_st4")
async def vB_st4___clbck_anketa_values(callback, state, pool):
    """Этап 4 - вопросы про ценности LingoMojo"""
    await state.set_state(myState.varB_st4)

    pool_base, pool_log = pool
    vUserID = callback.message.chat.id

    user_data = await state.get_data()
    selected_pains = user_data.get('selected_pains', [])

    # Проверяем что хоть что-то выбрано на предыдущем этапе
    if not selected_pains:
        await callback.answer('⚠️ Выбери хотя бы один вариант', show_alert=True)
        return

    # Создаём toggle для ценностей с номерами и эмодзи
    toggle_values = {}
    values_with_emoji = [
        ('⚡', 'Чтобы затягивало, не было скучно'),
        ('🎭', 'Как в реальной жизни, не по учебникам'),
        ('🗣️', 'Больше говорить, меньше зубрить'),
        ('📈', 'Видеть свой прогресс'),
        ('⏱️', 'В любое время, когда удобно'),
        ('💎', 'Не переплачивать'),
    ]

    for idx, (emoji, desc) in enumerate(values_with_emoji, start=1):
        toggle_values[str(idx)] = {
            'ind': '0',
            'emoji': emoji,
            'desc': desc,
            'number': f'{idx}️⃣'
        }

    # Формируем список ценностей в тексте
    values_list = "\n".join([
        f"{data['number']} {data['emoji']} {data['desc']}"
        for key, data in sorted(toggle_values.items(), key=lambda x: int(x[0]))
    ])

    str_Msg = f'''💡 Понял! Теперь главное:

<b>Как ты хочешь учить английский?</b>

{values_list}

<i>Выбери всё что важно:</i>'''

    await state.update_data(
        toggle_values=toggle_values,
        selected_values=[]
    )

    builder = vB_st4___f_builder(toggle_values)

    await callback.message.answer(
        str_Msg,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await pgDB.fExec_LogQuery(
        pool_log,
        vUserID,
        f'vB_st4___init|selected_pains:{len(selected_pains)}'
    )


@r_start.callback_query(F.data.startswith("vB_st4_"))
async def vB_st4___clbck_toggle(callback: types.CallbackQuery, state: FSMContext, pool):
    """Обработка toggle нажатий на кнопки ценностей"""
    await state.set_state(myState.varB_st4)

    vUserID = callback.message.chat.id
    pool_base, pool_log = pool

    # Извлекаем номер кнопки
    button_num = callback.data.split("_")[-1]

    # Получаем текущее состояние toggle
    user_data = await state.get_data()
    toggle_values = user_data.get('toggle_values', {})

    # Переключаем выбранную кнопку
    if button_num in toggle_values:
        current_state = toggle_values[button_num].get('ind', '0')
        new_state = '1' if current_state == '0' else '0'

        # УБРАЛИ ПРОВЕРКУ ЛИМИТА - можно выбрать все 6 ценностей

        # Переключаем состояние
        toggle_values[button_num]['ind'] = new_state

    # Сохраняем список выбранных ценностей
    selected_values = [
        val['desc']
        for key, val in toggle_values.items()
        if val.get('ind') == '1'
    ]

    # Обновляем state
    await state.update_data(
        toggle_values=toggle_values,
        selected_values=selected_values
    )

    # Регенерируем клавиатуру
    builder = vB_st4___f_builder(toggle_values)

    # Обновляем сообщение
    try:
        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    except Exception as e:
        logger.error(f"Error updating markup: {e}")

    await pgDB.fExec_LogQuery(
        pool_log,
        vUserID,
        f'vB_st4___toggle|button:{button_num}|selected_count:{len(selected_values)}'
    )

def vB_st4___f_builder(toggle_values):
    """Создаёт клавиатуру с values selection toggles - только номера"""
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки - только номера
    for key in sorted(toggle_values.keys(), key=int):
        button_data = toggle_values[key]
        number = button_data['number']
        is_selected = button_data['ind'] == '1'

        # Добавляем галочку если выбрано
        text = f"✅ {number}" if is_selected else number

        builder.add(types.InlineKeyboardButton(
            text=text,
            callback_data=f"vB_st4_{key}"
        ))

    # Добавляем кнопку "Показать мой план"
    builder.add(types.InlineKeyboardButton(
        text="✨ Показать мой план →",
        callback_data="vB_st5"
    ))

    # Layout: 3 кнопки в ряд (для 6 ценностей = 2 ряда) + кнопка "Показать план"
    builder.adjust(3, 3, 1)

    return builder


@r_start.callback_query(F.data == "vB_st5")
async def vB_st5___clbck_offer(callback: types.CallbackQuery, state: FSMContext, pool):
    """Этап 5 - показ предложения с тарифами"""
    await state.set_state(myState.varB_st5)
    await state.update_data(menu_command_disabled=False)

    vUserID = callback.message.chat.id
    pool_base, pool_log = pool
    bot = callback.bot

    # Получаем данные анкеты
    user_data = await state.get_data()
    selected_icp = user_data.get('selected_icp', [])
    selected_pains = user_data.get('selected_pains', [])
    selected_values = user_data.get('selected_values', [])
    discount = user_data.get('discount', 0)

    # ========================================
    # ЛОГИКА СКИДОК (аналогично старому коду)
    # ========================================

    if discount == 1:
        # Первый раз показываем скидку - активируем на 2 дня
        await state.update_data(discount=2)
        var_query = """
            UPDATE t_user 
            SET c_discount = 2, c_discountdue = CURRENT_TIMESTAMP + INTERVAL '2 days'     
            WHERE c_user_id = $1 
        """
        await pgDB.fExec_UpdateQuery_args(pool_base, var_query, vUserID)
        discount_validdate = (datetime.now() + timedelta(days=2)).strftime("%Y.%m.%d %H:%M")

        price_y = myPay.PRICE_YD
        price_m = myPay.PRICE_MD
        price_w = myPay.PRICE_W

    elif discount == 2:
        # Проверяем не истекла ли скидка
        var_query = (
            f"SELECT COALESCE(CURRENT_DATE < c_discountdue::date, false), c_discountdue "
            f"FROM public.t_user "
            f"WHERE c_user_id = {vUserID};"
        )
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
        bIs_discount_valid = var_Arr[0][0]

        if bIs_discount_valid:
            # Скидка еще действует
            price_y = myPay.PRICE_YD
            price_m = myPay.PRICE_MD
            price_w = myPay.PRICE_W
            date_obj = var_Arr[0][1]
            discount_validdate = date_obj.strftime("%Y.%m.%d %H:%M") if date_obj else ''
        else:
            # Скидка истекла
            price_y = myPay.PRICE_Y
            price_m = myPay.PRICE_M
            price_w = myPay.PRICE_W
            discount_validdate = ''

            await state.update_data(discount=3)
            var_query = """
                UPDATE t_user 
                SET c_discount = 3 
                WHERE c_user_id = $1 
            """
            await pgDB.fExec_UpdateQuery_args(pool_base, var_query, vUserID)

    else:
        # discount = 0 или 3 - проверяем есть ли активная скидка в БД
        var_query = (
            f"SELECT COALESCE(CURRENT_DATE < c_discountdue::date, false), c_discountdue "
            f"FROM public.t_user "
            f"WHERE c_user_id = {vUserID};"
        )
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
        bIs_discount_valid = var_Arr[0][0]

        if bIs_discount_valid:
            price_y = myPay.PRICE_YD
            price_m = myPay.PRICE_MD
            price_w = myPay.PRICE_W
            date_obj = var_Arr[0][1]
            discount_validdate = date_obj.strftime("%Y.%m.%d %H:%M") if date_obj else ''
        else:
            price_y = myPay.PRICE_Y
            price_m = myPay.PRICE_M
            price_w = myPay.PRICE_W
            discount_validdate = ''

    # Сохраняем цены в state для дальнейшего использования
    await state.update_data(
        price_y=price_y,
        price_m=price_m,
        price_w=price_w
    )

    # ========================================
    # СОХРАНЕНИЕ РЕЗУЛЬТАТОВ АНКЕТЫ В БД
    # ========================================

    import json
    survey_data = {
        'selected_icp': selected_icp,
        'selected_pains': selected_pains,
        'selected_values': selected_values,
        'completed_at': datetime.now().isoformat()
    }

    var_query = """
        UPDATE t_user 
        SET c_goals = $1
        WHERE c_user_id = $2
    """
    await pgDB.fExec_UpdateQuery_args(pool_base, var_query, json.dumps(survey_data), vUserID)

    # ========================================
    # ФОРМИРОВАНИЕ ТЕКСТА ПРЕДЛОЖЕНИЯ
    # ========================================

    # Конвертируем цены из строк в числа для математических операций
    price_y_int = int(price_y)
    price_m_int = int(price_m)
    price_w_int = int(price_w)

    # Добавляем строку о скидке если она активна
    strDiscount = f'\n\n🔥 <b>Скидка 50%</b>\nДействует до: <b>{discount_validdate}</b>' if discount_validdate else ''

    # Рассчитываем отображаемые цены
    if discount_validdate:
        # Со скидкой - используем константы из myPay
        price_y_old_int = int(myPay.PRICE_Y)
        price_m_old_int = int(myPay.PRICE_M)

        str_price_y = f'<s>{price_y_old_int}₽</s> → {price_y_int}₽/год (всего {price_y_int // 12}₽/мес)'
        str_price_m = f'<s>{price_m_old_int}₽</s> → {price_m_int}₽/мес'
        str_benefit = f'💎 Выгода {price_y_old_int - price_y_int}₽'
    else:
        # Без скидки
        str_price_y = f'{price_y_int}₽/год (всего {price_y_int // 12}₽/мес)'
        str_price_m = f'{price_m_int}₽/мес'
        str_benefit = f'💎 Экономия {(price_m_int * 12) - price_y_int}₽ по сравнению с месячной'

    str_Msg = f'''<b>LingoMojo</b> — это не учебники и не зубрёжка.

Ты будешь:
- Проходить истории как в реальной жизни (аэропорт, ресторан, работа...)
- Разговаривать с AI-персонажами без стыда за ошибки
- Видеть свой прогресс после каждой истории

─────────────────────────

<u>💰 Выбери свой план:</u>

<b>🏆 Годовая подписка — экономь 50%</b>
{str_price_y}
{str_benefit}

<b>⚡ Месячная подписка</b>
{str_price_m}
Отменить в любой момент

<b>🎯 Неделя погружения</b>
{price_w_int}₽ за 7 дней
Попробуй все возможности (разово, без подписки){strDiscount}'''

    # ========================================
    # СОЗДАНИЕ КНОПОК
    # ========================================

    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(
        text=f"🔥 Годовая {price_y}₽/год",
        callback_data="buy_c_y"
    ))

    builder.add(types.InlineKeyboardButton(
        text=f"⚡ Месячная {price_m}₽/мес",
        callback_data="buy_c_m"
    ))

    builder.add(types.InlineKeyboardButton(
        text=f"🎯 Неделя {price_w}₽",
        callback_data="buy_c_w"
    ))

    builder.adjust(1, 1, 1)

    # ========================================
    # ОТПРАВКА СООБЩЕНИЯ
    # ========================================

    await callback.message.answer(
        str_Msg,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    # Логирование
    await pgDB.fExec_LogQuery(
        pool_log,
        vUserID,
        f'vB_st5___offer|icp:{len(selected_icp)}|pains:{len(selected_pains)}|values:{len(selected_values)}|price_y:{price_y}|price_m:{price_m}|price_w:{price_w}'
    )


"""
async def vB_st2___clbck_offer(callback, state, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot



    str_Msg = '''
😢 Рыбку жалко... но это была отличная практика английского!

🎭Что ты получишь с подпиской:
✅ Полные истории (15-30 мин) 
✅ Unlimited диалоги с AI-персонажами 
✅ Новые истории каждую неделю

🔥 Стоимость подписки: <s>1000₽</s><b>499₽/мес</b>
    '''

    str_Msg = '''
😅 Теперь ты точно знаешь, как по-английски объяснить "рыбка внутри кота"!

Но Laura — только начало!

Тебя ждут:
🕵️ Детективные расследования
🗺️ Приключенческие сюжеты
✈️ Реальные жизненные ситуации (аэропорт, ресторан, скорая)

💎 С подпиской получаешь:
✅ Безлимитное общение с AI-персонажами 24/7
✅ Разбор КАЖДОЙ твоей ошибки с объяснениями
✅ Грамматику в контексте (без скучных учебников)
✅ Новые истории каждую неделю

💰 Цена: 499₽/мес
(Меньше чем 1 час с репетитором!)

👉 ПРОДОЛЖИТЬ ПРИКЛЮЧЕНИЕ →
    '''

    #проверка почты,
    #   если есть, то сразу формировать ссыль на оплату,
    #   если нет, то направлять на страницу ввода email
    # проверка наличия email----------------------------------------------------------------
    var_query = (
        f"SELECT c_email "
        f"FROM t_user "
        f"WHERE c_user_id = '{vUserID}'"
    )
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
    vEmail = var_Arr[0][0]
    if vEmail:
        clb_data = 'buy_c_m'
    else:
        clb_data = 'vB_st3'


    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=f"{myN.fCSS('vB_st3')}", callback_data=clb_data))        #buy_c_m    vB_st3
    #builder.add(types.InlineKeyboardButton(text=f"{myN.fCSS('vB_st3_rub')}", callback_data=clb_data))        #buy_c_m    vB_st3
    #builder.add(types.InlineKeyboardButton(text=f"{myN.fCSS('vB_st3_usd')}", callback_data='ppbuy'))        #buy_c_m    vB_st3

    msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'vB_st2___clbck_offer|')
"""

@r_start.callback_query(F.data == "ppbuy")
async def vB_st3___clbck_paypal(callback, state, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    PAYPAL_MODE = "sandbox"  # или "live"
    PAYPAL_CLIENT_ID_SANDBOX = "AVQ-KXG9pMrFKhnqoFnnRN89agXzN5HrJII_pJxSWtXuVu6jKOOLM2YnSnsl_ni-FxHtz0opwb6tRS_C"
    PAYPAL_SECRET_SANDBOX = "EKLnQxUIaC_p1bkE3NF4BmjsabHIJD7D4NNiDc0ssVMjikkk1nKNnbem9giYxvfU3ftVTVTzn2jz1AfP"
    PAYPAL_API_SANDBOX = "https://api-m.sandbox.paypal.com"

    PAYPAL_CLIENT_ID = PAYPAL_CLIENT_ID_SANDBOX
    PAYPAL_SECRET = PAYPAL_SECRET_SANDBOX
    PAYPAL_API = PAYPAL_API_SANDBOX

    import requests

    """Создать тестовый PayPal платеж"""

    # 1. Получить токен
    auth = (PAYPAL_CLIENT_ID, PAYPAL_SECRET)
    token_response = requests.post(
        f"{PAYPAL_API}/v1/oauth2/token",
        auth=auth,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "client_credentials"}
    )
    token = token_response.json()["access_token"]

    # 2. Создать order
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": "9.99"
            },
            "description": "LingoMojo Subscription"
        }],
        "application_context": {
            "landing_page": "BILLING",
            "return_url": "https://t.me/LingoMojo_bot",
            "cancel_url": "https://t.me/LingoMojo_bot",
            "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
            "brand_name": "LingoMojo",
            "shipping_preference": "NO_SHIPPING",
            "user_action": "PAY_NOW"
        }
    }

    response = requests.post(
        f"{PAYPAL_API}/v2/checkout/orders",
        headers=headers,
        json=payload
    )

    data = response.json()

    # 3. Найти approval URL
    approval_url = next(
        link["href"] for link in data["links"]
        if link["rel"] == "approve"
    )

    logger.info(f"✅ Order created!")
    logger.info(f"Order ID: {data['id']}")
    logger.info(f"Approval URL: {approval_url}")
    logger.info(f"\nOpen this URL in browser to test payment:")
    logger.info(approval_url)

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Оплатить', url=approval_url))
    #builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data=f'buy_v_{payment_id}'))

    '''
    if response.status_code == 200:
        token = response.json()["access_token"]
        str_Msg = f"✅ Connection successful!\n\nAccess Token: {token[:50]}..."
    else:
        str_Msg = f"❌ Error: {response.status_code}\n\nResponse: {response.text}"
    logger.info(f'------------------str_Msg:{str_Msg}')
    '''
    str_Msg = 'Pay'
    msg = await callback.message.answer(str_Msg, reply_markup = builder.as_markup(), parse_mode=ParseMode.HTML)



@r_start.callback_query(F.data == "vB_st3")
async def vB_st3___clbck_buy(callback, state, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    await state.update_data(menu_command_disabled=False)  # статус для работы кнопки команды menu

    from aiogram.types import ForceReply
    await callback.message.answer(
        "📧 Введите email для отправки чека:",
        reply_markup=ForceReply(
            input_field_placeholder="example@mail.com",
            selective=True
        )
    )
    await state.set_state(myState.buy_m)

    '''
    YOOKASSA_PROVIDER_TOKEN = '381764678:TEST:91857'

    await bot.send_invoice(
        chat_id=vUserID,
        title="Магазин",
        description="Подписка",
        payload="order_001",
        provider_token=YOOKASSA_PROVIDER_TOKEN,
        currency="RUB",
        prices=[
            types.LabeledPrice(
                label="Premium",
                amount=50000  # 500.00 ₽
            )
        ]
    )
    '''



def _____stage0_welcome_msg(): pass


async def vA_st0___f_init(message: types.Message, state: FSMContext, pool, gender_detector):  # отправка сообщения
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot
    await state.set_state(myState.varA_st0)


    webapp = WebAppInfo(url=config.URL_HELP)

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=f"{myF.fCSS('vA_st0')}", callback_data=f"vA_st0_1"))
    builder.add(types.InlineKeyboardButton(text='Help', web_app=webapp))
    builder.add(types.InlineKeyboardButton(text="Tell me ... ❱❱", callback_data=f"vA_st1"))
    #builder.add(types.InlineKeyboardButton(text="Plans", callback_data=f"vA_st5_2"))
    builder.adjust(2,1)
    toggle_audiotext = 0
    await state.update_data(toggle_audiotext=toggle_audiotext)

    # builder.add(types.InlineKeyboardButton(text="Указать ", callback_data=f"vA_st1_1" ))
    gender_result, relevant_name = myF.detect_gender(message.chat.first_name, gender_detector)
    python_folder = os.path.dirname(sys.executable)
    if os.path.basename(python_folder) == 'bin':
        python_folder = os.path.dirname(python_folder)
    logger.info(f'--------------------python_folder:{python_folder}')
    file = 'hello_m.ogg' if gender_result == 'female' else 'hello_f.ogg'
    pathFile = os.path.join(python_folder, 'storage', 'speak', 'start', file)

    base_text = (
        f'👋 Привет, {relevant_name}! Добро пожаловать в LingoMojo — твой AI-tutor!\n\n'
        f'❓ О чем это всё?\n\n'
        f'Ты пройдёшь несколько простых ознакомительных шагов.\n\n'
        f'📌 Шаг 1/9. Прослушай сообщение. \n'
        f'Для просмотра его текстовой версии — нажми {myF.fCSS("vA_st0")}.\n\n'
        f'Подробная инструкция по чат-боту - нажми Help'
        f'Далее переходи к следующему шагу - <b>жми "Tell me ... ❱❱"</b>\n\n'
    )

    str_Msg = base_text

    with open(pathFile, 'rb') as ogg:
        msg = await message.answer_voice(
            BufferedInputFile(ogg.read(), filename="hello.ogg"),
            caption=str_Msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    await state.update_data(
        gender_result=gender_result,
        base_text=base_text,
        relevant_name=relevant_name,
    )

    await pgDB.fExec_LogQuery(pool_log, vUserID, f'vA_st0___f_init|gender:{gender_result}')

#varA


@r_start.message((F.voice | (F.text & ~F.text.startswith('/'))), StateFilter(myState.varA_st0, myState.varA_st1))
async def vA_st0___media_plug(message: types.Message, bot: Bot, state: FSMContext, pool, dp):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot
    #await state.set_state(myState.varA_init)
    curState = await state.get_state()
    if curState == myState.varA_st0.state:
        str_button = "Tell me ... ❱❱"
        clbck_data = "vA_st1"
    else:
        str_button = "✨ Done! ⚡ Let's continue ❱❱"
        clbck_data = "vA_st2"

    str_Msg = f'Ваше сообщение не обработается.\n Пожалуйста нажмите "{str_button}"'
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=str_button, callback_data=clbck_data))


    await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

    await pgDB.fExec_LogQuery(pool_log, vUserID, f'vA_st0___media_plug|curState:{curState}|voice:{message.voice}|text:{message.text}')

@r_start.callback_query(F.data == "vA_st0_1")
async def vA_st0___clbck_toggle(callback: types.CallbackQuery, state: FSMContext, pool):
    await state.set_state(myState.varA_st0)
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    # Audio text to add when button '1' is pressed
    audio_text = '''
🎵 Audio text:
<blockquote expandable="true">Hi! You're at LingoMojo, an English language AI chatbot.
We can chat through both voice and text messages.
Let's get to know each other better — tell me your English level and what goals brought you here</blockquote>
    '''


    user_data = await state.get_data()
    toggle_audiotext = user_data.get('toggle_audiotext')
    base_text = user_data.get('base_text', '')

    builder = InlineKeyboardBuilder()
    if toggle_audiotext == 0:   #отображаем текст
        toggle_audiotext = 1
        str_Msg = f'{base_text}\n{audio_text}'

        builder.add(types.InlineKeyboardButton(text=f"✅ {myF.fCSS('vA_st0')}", callback_data=f"vA_st0_1"))
    else:
        toggle_audiotext = 0
        str_Msg = base_text
        builder.add(types.InlineKeyboardButton(text=f"{myF.fCSS('vA_st0')}", callback_data=f"vA_st0_1"))
    builder.add(types.InlineKeyboardButton(text="Tell me ... ❱❱", callback_data=f"vA_st1"))
    builder.adjust(2)

    await state.update_data(toggle_audiotext=toggle_audiotext)

    await callback.message.edit_caption(
        caption=str_Msg,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await pgDB.fExec_LogQuery(pool_log, vUserID, f'vA_st0___clbck_toggle|toggle_audiotext:{toggle_audiotext}')

def _____stage1_get_englevel_n_stats(): pass

#stage 1 - get englevel and stats
@r_start.callback_query(F.data == "vA_st1")
async def vA_st1___clbck_init(callback: types.CallbackQuery, state: FSMContext, pool, dp):
    await state.set_state(myState.varA_st1)

    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    nlp_tools = dp.workflow_data["nlp_tools"]
    gender_detector = nlp_tools.gender_detector
    # toggle init
    toggle = {
        '1': {'ind': "0", 'desc': '🔴 A'},
        '2': {'ind': "1", 'desc': '🟡 B'},
        '3': {'ind': "0", 'desc': '🟢 C'},
        '4': {'ind': "0", 'desc': '1️⃣ Career'},
        '5': {'ind': "0", 'desc': '2️⃣ Study'},
        '6': {'ind': "0", 'desc': '3️⃣ Travel'},
        '7': {'ind': "0", 'desc': '4️⃣ Live abroad'},
        '8': {'ind': "0", 'desc': '5️⃣ Fluency'},
        '9': {'ind': "0", 'desc': '6️⃣ Culture'},
    }
    user_data = await state.get_data()
    relevant_name = user_data.get('relevant_name', '')
    if not relevant_name:
        gender_result, relevant_name = myF.detect_gender(callback.message.chat.first_name, gender_detector)
        await state.update_data(
            gender_result=gender_result,
            relevant_name=relevant_name
        )
    str_Msg = f'{myF.fCSS("vA_st1")}'

    await state.update_data(
        toggle=toggle,
        corrections_text=''
    )
    builder = vA_st1___f_builder(toggle)

    msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

    await pgDB.fExec_LogQuery(pool_log, vUserID, f'vA_st1___clbck_init|relevant_name:{relevant_name}')

@r_start.callback_query(F.data.startswith("vA_st1_"))
async def vA_st1___clbck_toggle(callback: types.CallbackQuery, state: FSMContext, pool):
    await state.set_state(myState.varA_st1)

    vUserID = callback.message.chat.id
    pool_base, pool_log = pool
    bot = callback.bot

    """Handle toggle button presses"""

    # Extract button number from callback data
    button_num = callback.data.split("_")[-1]

    # Get current toggle state
    user_data = await state.get_data()
    toggle = user_data.get('toggle', {})




    if button_num in ['1', '2', '3']:
        # ABC buttons - only one can be selected
        for i in ['1', '2', '3']:
            toggle[i]['ind'] = '1' if i == button_num else '0'

    elif button_num in [str(i) for i in range(4, 10)]:
        # Number buttons - multiple can be selected
        current_state = toggle.get(button_num, {}).get('ind', '0')
        toggle[button_num]['ind'] = '1' if current_state == '0' else '0'

    # Update state
    await state.update_data(toggle=toggle)

    # Regenerate keyboard
    builder = vA_st1___f_builder(toggle)

    # Update message
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())

    #await callback.answer('Updated')
    await pgDB.fExec_LogQuery(pool_log, vUserID,f'vA_st1___clbck_toggle|toggle:{toggle}')


def vA_st1___f_builder(toggle):
    builder = InlineKeyboardBuilder()

    # Generate all buttons dynamically
    for key in sorted(toggle.keys(), key=int):  # Sort by numeric key
        button_data = toggle.get(key, {})
        desc = button_data.get('desc', '')
        is_selected = button_data.get('ind') == '1'

        # Add checkmark if selected
        text = f"✅ {desc}" if is_selected else desc

        builder.add(types.InlineKeyboardButton(
            text=text,
            callback_data=f"vA_st1_{key}"
        ))

    # Add Submit button at the bottom
    builder.add(types.InlineKeyboardButton(text="✨ Done! ⚡ Let's continue ❱❱", callback_data="vA_st2"))#

    # Layout: ABC (3) + Numbers 1-2 (2) + Numbers 3-4 (2) + Numbers 5-6 (2) + Submit (1)
    builder.adjust(3, 2, 2, 2, 1)

    return builder

def _____stage2_chat(): pass

# Handler for Submit button
@r_start.callback_query(F.data == "vA_st2")
async def vA_st2___clbck_init(callback: types.CallbackQuery, state: FSMContext, pool):
    await state.set_state(myState.varA)
    """Handle Submit button press"""
    vUserID = callback.message.chat.id
    pool_base, pool_log = pool
    bot = callback.bot

    user_data = await state.get_data()
    toggle = user_data.get('toggle', {})
    relevant_name = user_data.get('relevant_name')

    await vA_st2___f_set_eng_lvl(state, pool, vUserID, toggle)
    await vA_st2___f_save_goals(state, pool, vUserID, toggle)


    # Continue to next step
    await callback.answer("Submitted")

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=f"{myF.fCSS('vA_st0')}", callback_data=f"vA_st2_1"))
    builder.add(types.InlineKeyboardButton(text=f"{myF.fCSS('hint')}", callback_data=f"vA_st2_2"))
    builder.adjust(2)
    # toggle init
    toggle = {
        '1': {'ind': "0", 'desc': f"{myF.fCSS('vA_st0')}"},
        '2': {'ind': "0", 'desc': f"{myF.fCSS('hint')}"},
    }
    #logger.info(f'-----------toggle:{toggle}')

    base_text = (
        f'📌 Шаг 3/9 \n\n'
        f'Теперь пообщаемся:\n'
        f'- прослушай аудио\n'
        f'- нажми на кнопку {myF.fCSS("vA_st0")} и проверь, что все услышал правильно\n'
        f'- запиши голосовое или введи с клавиатуры текст приветствия (можно что-то простое - "Hi!", "How are you doing?")\n\n'
        f'Вперед!'
    )
    str_Msg = base_text

    gender_result = user_data.get('gender_result')
    file = 'chat_m.ogg' if gender_result == 'female' else 'chat_f.ogg'
    python_folder = os.path.dirname(sys.executable)
    if os.path.basename(python_folder) == 'bin':
        python_folder = os.path.dirname(python_folder)
    logger.info(f'--------------------python_folder:{python_folder}')
    pathFile = os.path.join(python_folder, 'storage', 'speak', 'start', file)
    with open(pathFile, 'rb') as ogg:
        msg = await callback.message.answer_voice(
            BufferedInputFile(ogg.read(), filename="chat.ogg"),
            caption=str_Msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    await state.update_data(
        toggle=toggle,
        audiotext="Let’s chat a bit. How’s your day going? Got any news or thoughts to share?",
        usertext = '',
        corrections_text = '',
        base_text = base_text,
    )

    await pgDB.fExec_LogQuery(pool_log, vUserID, f'vA_st2___clbck_init|toggle:{toggle}')
    # Call next step function or redirect
    #msg = await callback.message.answer("all's done", parse_mode=ParseMode.HTML)


async def vA_st2___f_set_eng_lvl(state: FSMContext, pool, vUserID, toggle):
    """
    Returns chosen English level in numerical format (A=1, B=2, C=3)

    Args:
        toggle (dict): Toggle structure with keys '1'-'3' for English levels

    Returns:
        int or None: English level number (1, 2, or 3) or None if none selected
    """
    pool_base, pool_log = pool
    # Map keys to level numbers
    level_map = {'1': {'i': 1, 'c': "A"}, '2': {'i': 2, 'c': "B"}, '3': {'i': 3, 'c': "C"}}  # A=1, B=2, C=3

    # Check which English level is selected (ind = "1")
    for key in ['1', '2', '3']:
        if key in toggle and toggle[key]['ind'] == "1":
            var_query = '''
                UPDATE t_user_paramssingle 
                SET c_ups_eng_level = $1 
                WHERE c_ups_user_id = $2 
            '''
            await pgDB.fExec_UpdateQuery_args(pool_base, var_query, level_map[key]['i'], vUserID)
            await state.update_data(englevel=level_map[key]['c'])   #string A B C




async def vA_st2___f_save_goals(state: FSMContext, pool, vUserID, toggle):
    """
    Saves selected goals (keys '4'-'9') to database as JSON

    Args:
        toggle (dict): Toggle structure with keys '4'-'9' for goals
        vUserID (int): User ID
        pool: Database connection
    """
    pool_base, pool_log = pool
    # Extract selected goals (ind = "1") from keys '4' to '9'
    selected_goals = []

    # Goal mapping for cleaner JSON storage
    goal_map = {
        '4': 'career',
        '5': 'study',
        '6': 'travel',
        '7': 'live_abroad',
        '8': 'fluency',
        '9': 'culture'
    }

    # Check which goals are selected
    for key in ['4', '5', '6', '7', '8', '9']:
        if key in toggle and toggle[key]['ind'] == "1":
            selected_goals.append(goal_map[key])

    # Convert to JSON string
    goals_json = json.dumps(selected_goals)

    # Update database
    var_query = """
    UPDATE t_user 
    SET c_goals = $1 
    WHERE c_user_id = $2
    """
    await pgDB.fExec_UpdateQuery_args(pool_base, var_query, goals_json, vUserID)
    await state.update_data(goals_json=goals_json)



@r_start.callback_query(F.data.startswith("vA_st2_"))
async def vA_st2___clbck_toggle(callback: types.CallbackQuery, state: FSMContext, pool):
    await state.set_state(myState.varA)
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    # Extract button number from callback data
    button_num = callback.data.split("_")[-1]

    # Get current toggle state
    user_data = await state.get_data()
    toggle = user_data.get('toggle', {})
    usertext = user_data.get('usertext', '')
    corrections_text = user_data.get('corrections_text', '')
    base_text = user_data.get('base_text', '')

    #logger.info(f'--------2|toggle:{toggle}')

    if button_num in ['1', '2']:
        # ABC buttons - handle toggle behavior
        current_state = toggle.get(button_num, {}).get('ind', '0')
        #logger.info(f'--------3|button_num:{button_num}|current_state:{current_state}')
        if current_state == '1':
            # Button is currently selected - deselect it
            toggle[button_num]['ind'] = '0'
            #logger.info(f"--------4|button_num:{button_num}|current_state:{current_state}|x:{toggle.get(button_num, {}).get('ind', '0')}'")
        else:
            # Button is not selected - select it and deselect others
            for i in ['1', '2']:
                toggle[i]['ind'] = '1' if i == button_num else '0'
                #logger.info(f"--------5|x:{toggle.get(i, {}).get('ind', '0')}")

    # Update state
    await state.update_data(toggle=toggle)

    # Regenerate keyboard
    builder = InlineKeyboardBuilder()

    # Generate all buttons dynamically

    str_Msg = ''
    any_selected = False
    aux_text = f'<blockquote expandable="true">{corrections_text}</blockquote>\n\n'

    for key in sorted(toggle.keys(), key=int):  # Sort by numeric key
        button_data = toggle.get(key, {})
        desc = button_data.get('desc', '')
        is_selected = button_data.get('ind') == '1'

        # Add checkmark if selected
        text = f"✅ {desc}" if is_selected else desc

        if is_selected and key in ['1', '2']:  # Only handle message for audio/hint buttons
            any_selected = True
            if key == '1':

                audiotext = user_data.get('audiotext', '')
                str_Msg = (
                    f"{base_text}\n\n{aux_text}"
                    f"🎵 Audio text:\n"
                    f"<blockquote expandable='true'>{audiotext}</blockquote>"
                )
            elif key == '2':
                str_Msg = (
                    f"{base_text}\n\n{aux_text}"
                    f"{myF.fCSS('hint')}\n"
                    f"<blockquote expandable='true'>{myF.fCSS('vA_d_skip')}</blockquote>"
                )

        builder.add(types.InlineKeyboardButton(text=text, callback_data=f"vA_st2_{key}"))
    if usertext:
        builder.add(types.InlineKeyboardButton(text='Check grammar', callback_data=f"vA_st2g"))
        builder.add(types.InlineKeyboardButton(text='Skip', callback_data=f"vA_st3"))
        builder.adjust(2,2)
    else:
        builder.adjust(2)

    # If no ABC button is selected, clear the message
    if not any_selected:
        str_Msg = f"{base_text}\n\n{aux_text}"

    await callback.message.edit_caption(
        caption=str_Msg,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await pgDB.fExec_LogQuery(pool_log, vUserID, f'vA_st2___clbck_toggle')







@r_start.message((F.voice | (F.text & ~F.text.startswith('/'))), StateFilter(myState.varA))         #(F.voice | F.text), StateFilter(myState.varA)
async def vA_st2___media(message: types.Message, bot: Bot, state: FSMContext, pool, dp):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot
    nlp_tools = dp.workflow_data["nlp_tools"]
    gender_detector = nlp_tools.gender_detector
    await state.set_state(myState.varA)

    user_data = await state.get_data()
    #toggle = user_data.get('toggle', {})       не нужен, требуется переопределение тоггла
    toggle = {
        '1': {'ind': "0", 'desc': f"{myF.fCSS('vA_st0')}"},
        '2': {'ind': "0", 'desc': f"{myF.fCSS('hint')}"},
    }
    gender_result = user_data.get('gender_result', '')
    gender_result = user_data.get('gender_result', '')
    if not gender_result:
        gender_result, relevant_name = myF.detect_gender(callback.message.chat.first_name, gender_detector)
        await state.update_data(
            gender_result=gender_result,
            relevant_name=relevant_name
        )
    if gender_result == 'female':
        arrVoiceParams = ['en-US', 'en-US-Chirp3-HD-Algieba', 'MALE']
    else:
        arrVoiceParams = ['en-US', 'en-US-Chirp3-HD-Autonoe', 'FEMALE']
    #logger.info(f'-------------->>>arrVoiceParams - {arrVoiceParams}')

    base_text = f'''
📌 Шаг 4/9. Отлично!

Теперь:
- прослушай ответ
- посмотри {myF.fCSS("vA_st0")}
- нажми "Check grammar" и посмотри разбор грамматики твоего ответа
- Далее ты можешь продолжить общаться, либо нажать "Skip" и перейти к следующему шагу
		
Вперед! 
    '''


    # -------------------processing both voice and text
    usertext = ''
    #logger.info('--------------------0')
    if message.voice != None:  # voice
        # ---------------------------------------перевод user voice -> text
        usertext = await myF.afVoiceToTxt(message, pool, vUserID)  # транскрипция голоса в текст    , bot
    elif message.text != None:
        usertext = ' '.join(message.text.split())   #message.text
    #logger.info('--------------------1')
    usertext = usertext.rstrip()        # Remove trailing spaces first, then check for dot
    if usertext.endswith('.'): usertext = usertext[:-1]         # Remove trailing dot if it exists
    usertext = usertext.rstrip()            # Remove any remaining trailing spaces after dot removal
    #logger.info('--------------------2')

    if usertext != '':
        goals_json = user_data.get('goals_json')
        englevel = user_data.get('englevel')

        promptSys, promptUser = myP.fPromptStart(usertext, englevel, goals_json)
        #logger.info(f'--------------------3|sysLen:{len(promptSys)}|lenUser:{promptUser}')
        audiotext = await myF.afSendMsg2AI(promptUser, pool_base, vUserID, toggleParam = 2, systemPrompt = promptSys)
        corrections_text, teacher_text = myF.parse_ai_fs_response(audiotext)
        #logger.info(f'--------------------4|AI length:{len(audiotext)}')
        #logger.info(f'audiotext:{audiotext}|corrections_text:{corrections_text}|teacher_text:{teacher_text}|')
        str_Msg = f'{base_text}\n\nПредложения по улучшению текста:\n<blockquote expandable="true">{corrections_text}</blockquote>\n\n'      #audiotext


        nm_ogg = await myF.afTxtToOGG(teacher_text, arrVoiceParams)
        #logger.info('--------------------5|afTxtToOGG')
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('vA_st0'), callback_data=f"vA_st2_1"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('hint'), callback_data=f"vA_st2_2"))
        builder.add(types.InlineKeyboardButton(text='Check grammar', callback_data=f"vA_st2g"))
        builder.add(types.InlineKeyboardButton(text='Skip', callback_data=f"vA_st3"))
        builder.adjust(2, 2)

        #logger.info('--------------------6')
        with open(nm_ogg, 'rb') as ogg:
            msg = await message.answer_voice(
                BufferedInputFile(ogg.read(), filename="chat.ogg"),
                caption=str_Msg,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )


        #logger.info('--------------------7')
        await state.update_data(
            audiotext=teacher_text,
            corrections_text=corrections_text,
            usertext=usertext,
            toggle=toggle,
            base_text=base_text,
        )
    #logger.info('--------------------8')
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'vA_st2___media|usertext:{usertext}|audiotext:{audiotext}')
    #logger.info('--------------------9')


@r_start.callback_query(F.data == "vA_st2g")
async def gen___clbck_grammarcheck(callback: types.CallbackQuery, state: FSMContext, pool, dp):
    #await state.set_state(myState.varA)        #as a gen purpose function it should be state independent
    vUserID = callback.message.chat.id
    pool_base, pool_log = pool
    bot = callback.bot

    nlp_tools = dp.workflow_data["nlp_tools"]
    user_data = await state.get_data()
    usertext = user_data.get('usertext', '')



    # -----------------------проверка грамматики и формирование тоггла для списка ошибка
    str_Msg, index_rule_pairs, var_ImprovedLine = await myF.fGrammarCheck_txt(
        nlp_tools.tool, usertext, pool, vUserID
    )
    # Generate toggleButtonStatus dictionary dynamically
    toggleButtonStatus = {str(emoji_index): 0 for emoji_index, _ in index_rule_pairs}
    #logger.info(f'-------------toggleButtonStatus:{toggleButtonStatus}')
    builder = await myF.fSetGrammarBuilder(toggleButtonStatus, index_rule_pairs, state)

    curState = await state.get_state()
    if curState == myState.fs.state:
        auxMsg = f'<b>{myF.fCSS("fs_finish")}</b>'
    elif curState == myState.task8_story_active:
        auxMsg = ''
    else:
        auxMsg = f'<b>{myF.fCSS("vA_d_skip")}</b>'

    str_Msg = (
        f'{str_Msg}\n\n{auxMsg}'

    )

    # -----------------------отправка проверки грамматики пользователю
    msg = await callback.message.answer(str_Msg, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())
    await state.update_data(
        str_Msg=str_Msg,
        toggleButtonStatus=toggleButtonStatus,
        index_rule_pairs=index_rule_pairs,
    )
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'gen___clbck_grammarcheck|toggleButtonStatus:{toggleButtonStatus}|index_rule_pairs:{index_rule_pairs}')


def _____stage3_BAS(): pass

# Handler for step3 init
@r_start.callback_query(F.data == "vA_st3")
async def vA_st3___clbck_init(callback: types.CallbackQuery, state: FSMContext, pool, dp):
    await state.set_state(myState.varA)
    vUserID = callback.message.chat.id
    pool_base, pool_log = pool

    bot = callback.bot

    nlp_tools = dp.workflow_data["nlp_tools"]
    gender_detector = nlp_tools.gender_detector

    user_data = await state.get_data()
    gender_result = user_data.get('gender_result', '')
    if not gender_result:
        gender_result, relevant_name = myF.detect_gender(callback.message.chat.first_name, gender_detector)
        await state.update_data(
            gender_result=gender_result,
            relevant_name=relevant_name,
        )


    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('vA_st0'), callback_data=f"vA_st3_1"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('vA_st3_2'), callback_data=f"vA_st3_2"))
    builder.adjust(2)
    toggle_audiotext = 0




    python_folder = os.path.dirname(sys.executable)
    if os.path.basename(python_folder) == 'bin':
        python_folder = os.path.dirname(python_folder)
    logger.info(f'--------------------python_folder:{python_folder}')
    file = 'bas_m_1.ogg' if gender_result == 'female' else 'bas_f_1.ogg'
    pathFile = os.path.join(python_folder, 'storage', 'speak', 'start', file)

    base_text = f'''
📌 Шаг 5/9.
Мы на верном пути.
Прослушай сообщение и нажми "{myF.fCSS('vA_st3_2')}"
        '''

    with open(pathFile, 'rb') as ogg:
        msg = await callback.message.answer_voice(
            BufferedInputFile(ogg.read(), filename="chat.ogg"),
            caption=base_text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    audiotext = "Okay. Now let's play a short word game, shall we?"

    await state.update_data(
        toggle_audiotext=toggle_audiotext,
        audiotext=audiotext,
        base_text=base_text,
    )
    await pgDB.fExec_LogQuery(pool_log, vUserID,f'vA_st3___clbck_init|toggle_audiotext:{toggle_audiotext}')


@r_start.callback_query(F.data == "vA_st3_1")
async def vA_st3___clbck_toggle(callback: types.CallbackQuery, state: FSMContext, pool):
    await state.set_state(myState.varA)
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    # Audio text to add when button '1' is pressed
    user_data = await state.get_data()
    audiotext = user_data.get('audiotext', '')
    toggle_audiotext = user_data.get('toggle_audiotext', '')
    base_text = user_data.get('base_text', '')
    str_Msg = f'{base_text}\n\n🎵 Audio text:\n<blockquote expandable="true">{audiotext}</blockquote>'


    builder = InlineKeyboardBuilder()
    if toggle_audiotext == 0:   #отображаем текст
        toggle_audiotext = 1
        builder.add(types.InlineKeyboardButton(text=f"✅ {myF.fCSS('vA_st0')}", callback_data=f"vA_st3_1"))
    else:
        toggle_audiotext = 0
        str_Msg = base_text
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('vA_st0'), callback_data=f"vA_st3_1"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('vA_st3_2'), callback_data=f"vA_st3_2"))
    builder.adjust(2)

    await state.update_data(toggle_audiotext=toggle_audiotext)

    await callback.message.edit_caption(
        caption=str_Msg,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'vA_st3___clbck_toggle|toggle_audiotext:{toggle_audiotext}')

@r_start.callback_query(F.data == "vA_st3_2")
async def vA_st3___clbck_bas(callback: types.CallbackQuery, state: FSMContext, pool):
    await state.set_state(myState.varA_bas)
    vUserID = callback.message.chat.id
    pool_base, pool_log = pool

    bot = callback.bot

    user_data = await state.get_data()
    englevel = user_data.get('englevel', 'B')


    if englevel == 'A':
        words = random.choice(
            [
                'cat (кот), book (книга), sun (солнце), chair (стул)',
                'dog (собака), apple (яблоко), house (дом), car (машина)',
                'book (книга), cat (кот), chair (стул), water (вода)',
            ]
        )


    elif englevel == 'B':
        words = random.choice(
            [
                'journey (путешествие), advice (совет), mountain (гора), success (успех)',
                'bridge (мост), freedom (свобода), mistake (ошибка), neighbor (сосед)',
                'dream (мечта), experience (опыт), health (здоровье), forest (лес)',
            ]
        )
    elif englevel == 'C':
        words = random.choice(
            [
            'perseverance (настойчивость), scrutinize (тщательно изучать), eloquent (красноречивый), mitigate (смягчать)',
            'ambiguous (двусмысленный), resilience (устойчивость), contemplate (размышлять), deteriorate (ухудшаться)',
            'meticulous (дотошный), substantiate (обосновывать), ubiquitous (вездесущий), unprecedented (беспрецедентный)',
            ]
        )

    str_Msg = (
        f"{myF.fCSS('bas')}\n\n"
        f'📌 Шаг 6/9. Придумайте предложение или короткую историю из 4х слов:\n'
        f'<b>{words}</b>\n\n'
        f'{myF.fCSS("vA_t_skip")}'
    )
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Skip', callback_data="vA_st4"))

    # send a message
    msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await state.update_data(bas_words=words)

    await pgDB.fExec_LogQuery(pool_log, vUserID, f'vA_st3___clbck_bas|words:{words}')


@r_start.message((F.voice | (F.text & ~F.text.startswith('/'))), StateFilter(myState.varA_bas))         #(F.voice | F.text), StateFilter(myState.varA)
async def vA_st3___media(message: types.Message, bot: Bot, state: FSMContext, pool, dp):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot
    nlp_tools = dp.workflow_data["nlp_tools"]
    gender_detector = nlp_tools.gender_detector
    await state.set_state(myState.varA_bas)
    vLangCode = message.from_user.language_code

    user_data = await state.get_data()
    bas_words = user_data.get('bas_words', '')

    # +++++++++++++++++отправка и получение голосового сообщения ChatGPT++++++++++++++++++++++++++++
    # -------------------processing both voice and text
    usertext = ''

    usertext
    if message.voice != None:  # voice
        # ---------------------------------------перевод user voice -> text
        usertext = await myF.afVoiceToTxt(message, pool, vUserID)  # транскрипция голоса в текст    , bot
    elif message.text != None:
        usertext = ' '.join(message.text.split())   #message.text

    if usertext:
        vStr = myF.fCheckWords_BAS(usertext, bas_words, nlp_tools.nlp)

        # -----------------------проверка грамматики и формирование тоггла для списка ошибок
        str_Msg, index_rule_pairs, var_ImprovedLine = await myF.fGrammarCheck_txt(
            nlp_tools.tool, usertext, pool, vUserID
        )

        str_Msg = f'{vStr}\n\n{str_Msg}'

        # Generate toggleButtonStatus dictionary dynamically
        toggleButtonStatus = {str(emoji_index): 0 for emoji_index, _ in index_rule_pairs}
        #logger.info(f'-----------toggleButtonStatus:{toggleButtonStatus}|index_rule_pairs:{index_rule_pairs}')
        builder = await myF.fSetGrammarBuilder(toggleButtonStatus, index_rule_pairs, state)
        await state.update_data(str_Msg=str_Msg)  # сохранение для вкладок грамматики
        await state.update_data(index_rule_pairs=index_rule_pairs)  # сохранение для вкладок грамматики
        await state.update_data(toggleButtonStatus=toggleButtonStatus)  # сохранение для вкладок грамматики



    msg = await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await state.update_data(bas_words='')
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"vA_st3___media|usertext:{usertext}|index_rule_pairs:{index_rule_pairs}")


def _____stage4_news(): pass

# Handler for step4 init
@r_start.callback_query(F.data == "vA_st4")
async def vA_st4___clbck_init(callback: types.CallbackQuery, state: FSMContext, pool, dp):
    await state.set_state(myState.varA_news)
    vUserID = callback.message.chat.id
    pool_base, pool_log = pool
    bot = callback.bot

    nlp_tools = dp.workflow_data["nlp_tools"]
    gender_detector = nlp_tools.gender_detector

    user_data = await state.get_data()
    gender_result = user_data.get('gender_result', '')
    if not gender_result:
        gender_result, relevant_name = myF.detect_gender(callback.message.chat.first_name, gender_detector)
        await state.update_data(
            gender_result=gender_result,
            relevant_name=relevant_name,
        )

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('vA_st0'), callback_data=f"vA_st4_1"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('vA_st4_2'), callback_data=f"vA_st4_2"))

    builder.adjust(2)
    toggle_audiotext = 0

    python_folder = os.path.dirname(sys.executable)
    if os.path.basename(python_folder) == 'bin':
        python_folder = os.path.dirname(python_folder)
    logger.info(f'--------------------python_folder:{python_folder}')
    file = 'news_m.ogg' if gender_result == 'female' else 'news_f.ogg'
    pathFile = os.path.join(python_folder, 'storage', 'speak', 'start', file)
    base_text = (
        f'📌 Шаг 7/9.\n\n'
        f'С чатботом можно читать новости. \n'
        f'Прослушай аудио и жми {myF.fCSS("vA_st4_2")}'
    )
    with open(pathFile, 'rb') as ogg:
        msg = await callback.message.answer_voice(
            BufferedInputFile(ogg.read(), filename="chat.ogg"),
            caption=base_text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    audiotext = "Great work so far! Here's your next level unlock: authentic newspaper articles. This is where English learners transform into confident readers. These aren't textbook exercises - this is the real deal that native speakers read every day. Ready to join them?"
    await state.update_data(
        toggle_audiotext=toggle_audiotext,
        audiotext=audiotext,
        base_text=base_text,
    )
    await pgDB.fExec_LogQuery(pool_log, vUserID,f"vA_st4___clbck_init")


@r_start.callback_query(F.data == "vA_st4_1")
async def vA_st4___clbck_toggle(callback: types.CallbackQuery, state: FSMContext, pool):
    await state.set_state(myState.varA_news)
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    # Audio text to add when button '1' is pressed
    user_data = await state.get_data()
    audiotext = user_data.get('audiotext', '')
    toggle_audiotext = user_data.get('toggle_audiotext', '')
    base_text = user_data.get('base_text', '')
    str_Msg = f'{base_text}\n\n🎵 Audio text:\n<blockquote expandable="true">{audiotext}</blockquote>'


    builder = InlineKeyboardBuilder()
    if toggle_audiotext == 0:   #отображаем текст
        toggle_audiotext = 1
        builder.add(types.InlineKeyboardButton(text=f"✅ {myF.fCSS('vA_st0')}", callback_data=f"vA_st4_1"))
    else:
        toggle_audiotext = 0
        str_Msg = base_text
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('vA_st0'), callback_data=f"vA_st4_1"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('vA_st4_2'), callback_data=f"vA_st4_2"))
    builder.adjust(2)



    await state.update_data(toggle_audiotext=toggle_audiotext)

    await callback.message.edit_caption(
        caption=str_Msg,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await pgDB.fExec_LogQuery(pool_log, vUserID, f"vA_st4___clbck_toggle|toggle_audiotext:{toggle_audiotext}")



@r_start.callback_query(F.data == "vA_st4_2")
async def vA_st4___clbck_news(callback: types.CallbackQuery, state: FSMContext, pool):
    await state.set_state(myState.varA_news)
    vUserID = callback.message.chat.id
    pool_base, pool_log = pool
    bot = callback.bot

    user_data = await state.get_data()
    englevel = user_data.get('englevel', 'B')

    vLevel = 2 if englevel == 'A' else 3

    var_query = (
        f"SELECT t1.c_title, t1.c_id, t1.c_summary, t2.c_emoji, t1.c_date, t1.c_title_ru, t1.c_text, t1.c_web, t1.c_trans "
        f"FROM t_news AS t1 LEFT JOIN t_news_topic AS t2 ON t1.c_topic = t2.c_id "
        f"WHERE c_englvl = {vLevel} "
        f"ORDER BY c_id DESC "
        f"LIMIT 1 "
    )
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)    #c_word

    vIndex  = 1
    vID = var_Arr[0][1]  # получение ID статьи
    vDate = var_Arr[0][4]  # получение даты статьи
    vTitle_ru = var_Arr[0][5]  # получение названия статьи на русском
    vTitle = var_Arr[0][0]  # получение названия статьи
    vText = var_Arr[0][6]  # содержание
    vWeb = var_Arr[0][7]  # ссылка
    vTrans = var_Arr[0][8]  # перевод
    arrText = vText.split('\n')  # преобразование в массив
    arrTrans = vTrans.split('\n')  # преобразование в массив

    vCnt = 0

    arrPages_Txt, arrPages_Trans = myF.fProcessArr_News(arrText, arrTrans)  # очистка от нумерации и пустых записей

    num = len(arrPages_Txt)  # получение кол-ва страниц

    subArrText = arrPages_Txt[vCnt]
    subArrTrans = arrPages_Trans[vCnt]

    str_Msg = ''
    for i, text in enumerate(subArrText):
        str_Msg = (
            f'{str_Msg}'
            f'{text}\n'
            f'<blockquote expandable="true">{subArrTrans[i]}</blockquote>\n\n'
        )

    str_Msg = myF.fShapeNews1Page(vDate, vTitle, vTitle_ru, vCnt, num, vWeb, str_Msg)


    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="vA_st5"))

    msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

    #await state.update_data()
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"vA_st4___clbck_news")


    #await pgDB.fExec_LogQuery(pool_log, vUserID, f'newsppr|{callback.data}')


def _____stage5_purchase(): pass

@r_start.callback_query(F.data == "vA_st5")
async def vA_st5___clbck_init(callback: types.CallbackQuery, state: FSMContext, pool, dp):
    await state.set_state(myState.varA_pay)
    vUserID = callback.message.chat.id
    pool_base, pool_log = pool
    bot = callback.bot
    nlp_tools = dp.workflow_data["nlp_tools"]
    gender_detector = nlp_tools.gender_detector

    user_data = await state.get_data()
    englevel = user_data.get('englevel', 'B')
    audiotext = user_data.get('audiotext', '')
    gender_result = user_data.get('gender_result', '')
    if not gender_result:
        gender_result, relevant_name = myF.detect_gender(callback.message.chat.first_name, gender_detector)
        await state.update_data(
            gender_result=gender_result,
            relevant_name=relevant_name,
        )


    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('vA_st0'), callback_data=f"vA_st5_1"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('vA_st5_2'), callback_data=f"vA_st5_2"))
    builder.adjust(2)


    python_folder = os.path.dirname(sys.executable)
    if os.path.basename(python_folder) == 'bin':
        python_folder = os.path.dirname(python_folder)
    logger.info(f'--------------------python_folder:{python_folder}')
    file = 'buy_m.ogg' if gender_result == 'female' else 'buy_f.ogg'
    pathFile = os.path.join(python_folder, 'storage', 'speak', 'start', file)
    base_text = (
        f'📌 Шаг 8/9.\n\n'
        f'Мы приближаемся к финишу\n\n'
        f'Прослушай сообщение и нажми {myF.fCSS("vA_st5_2")}'
    )
    with open(pathFile, 'rb') as ogg:
        msg = await callback.message.answer_voice(
            BufferedInputFile(ogg.read(), filename="chat.ogg"),
            caption=base_text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )

    await state.update_data(
        toggle_audiotext=0,
        base_text=base_text,
        audiotext="Ready to accelerate your progress? Premium access unlocks your full potential - click the button below to explore your options",
    )
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"vA_st5___clbck_init")


@r_start.callback_query(F.data == "vA_st5_1")
async def vA_st5___clbck_toggle(callback: types.CallbackQuery, state: FSMContext, pool):
    await state.set_state(myState.varA_pay)
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    # Audio text to add when button '1' is pressed
    user_data = await state.get_data()
    audiotext = user_data.get('audiotext', '')
    toggle_audiotext = user_data.get('toggle_audiotext', '')
    base_text = user_data.get('base_text', '')
    str_Msg = f'{base_text}\n\n🎵 Audio text:\n<blockquote expandable="true">{audiotext}</blockquote>'


    builder = InlineKeyboardBuilder()
    if toggle_audiotext == 0:   #отображаем текст
        toggle_audiotext = 1
        builder.add(types.InlineKeyboardButton(text=f"✅ {myF.fCSS('vA_st0')}", callback_data=f"vA_st5_1"))
    else:
        toggle_audiotext = 0
        str_Msg = base_text
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('vA_st0'), callback_data=f"vA_st5_1"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('vA_st5_2'), callback_data=f"vA_st5_2"))
    builder.adjust(2)



    await state.update_data(toggle_audiotext=toggle_audiotext)

    await callback.message.edit_caption(
        caption=str_Msg,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await pgDB.fExec_LogQuery(pool_log, vUserID, f"vA_st5___clbck_toggle|toggle_audiotext:{toggle_audiotext}")


@r_start.callback_query(F.data == "vA_st5_2")
async def vA_st5___clbck_plans(callback: types.CallbackQuery, state: FSMContext, pool):
    await state.set_state(myState.varA_news)
    vUserID = callback.message.chat.id
    pool_base, pool_log = pool
    bot = callback.bot

    user_data = await state.get_data()
    englevel = user_data.get('englevel', 'B')
    discount = user_data.get('discount', 0)

    #logger.info(f'-----------------------------------discount:{discount}')



    if discount == 1:
        await state.update_data(discount=2)
        var_query = """
            UPDATE t_user 
            SET c_discount = 2, c_discountdue = CURRENT_TIMESTAMP + INTERVAL '2 days'     
            WHERE c_user_id = $1 
        """
        await pgDB.fExec_UpdateQuery_args(pool_base, var_query, vUserID)
        discount_validdate = (datetime.now() + timedelta(days=2)).strftime("%Y.%m.%d %H:%M")
        nm_Img = myF.fGetImg('plans_d')
        price_m = myPay.PRICE_MD
        price_q = myPay.PRICE_QD
    elif discount == 2:
        var_query = (
            f"SELECT COALESCE(CURRENT_DATE < c_discountdue::date, false), c_discountdue "
            f"FROM public.t_user "
            f"WHERE c_user_id = {vUserID};"
        )
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
        bIs_discount_valid = var_Arr[0][0]
        if bIs_discount_valid:
            #logger.info(f'bIs_discount_valid:{bIs_discount_valid}')
            nm_Img = myF.fGetImg('plans_d')
            price_m = myPay.PRICE_MD
            price_q = myPay.PRICE_QD
            date_obj = var_Arr[0][1]
            discount_validdate = date_obj.strftime("%Y.%m.%d %H:%M") if date_obj else ''

        else:
            #logger.info(f'bIs_discount_valid:{bIs_discount_valid}')
            nm_Img = myF.fGetImg('plans_n')
            price_m = myPay.PRICE_M
            price_q = myPay.PRICE_Q
            discount_validdate=''
            await state.update_data(discount=3)
            var_query = """
                UPDATE t_user 
                SET c_discount = 3 
                WHERE c_user_id = $1 
            """
            await pgDB.fExec_UpdateQuery_args(pool_base, var_query, vUserID)
    else:
        var_query = (
            f"SELECT COALESCE(CURRENT_DATE < c_discountdue::date, false), c_discountdue "
            f"FROM public.t_user "
            f"WHERE c_user_id = {vUserID};"
        )
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
        bIs_discount_valid = var_Arr[0][0]

        if bIs_discount_valid:
            price_m = myPay.PRICE_MD
            price_q = myPay.PRICE_QD
            nm_Img = myF.fGetImg('plans_d')
            date_obj = var_Arr[0][1]
            discount_validdate = date_obj.strftime("%Y.%m.%d %H:%M") if date_obj else ''
        else:
            price_m = myPay.PRICE_M
            price_q = myPay.PRICE_Q
            nm_Img = myF.fGetImg('plans_n')
            discount_validdate=''



    await state.update_data(price_m=price_m)
    await state.update_data(price_q=price_q)





    strDiscount = f'\n\nСкидка <b>50%</b>\nСкидка действует до: <b>{discount_validdate}</b>' if discount_validdate else ''

    str_Msg = (
        f'📌 Шаг 9/9.\n'
        f'🌱 Выбери план, который лучше тебе подходит 👇'
        f'{strDiscount}'
    )

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=f"☘️Take a month ({price_m}₽)", callback_data="buy_c_m"))     # price_edu_c_m
    builder.add(types.InlineKeyboardButton(text=f"🌳️ Take a quarter  ({price_q}₽)", callback_data="buy_c_q"))      #price_edu_c_q
    builder.adjust(1,1)
    #await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    #nm_Img = myF.fGetImg('plans')
    #nm_updImg = myF.fImageAddQuote(nm_Img)
    with open(nm_Img, "rb") as image_In:
        msg = await callback.message.answer_photo(
            BufferedInputFile(image_In.read(), filename="plans.jpg"),
            caption=str_Msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"vA_st5___clbck_plans|price_m:{price_m}|price_q:{price_q}")

@r_start.callback_query(F.data.startswith("buy_"))      #       price_
async def gen___clbck_buy(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    await state.update_data(menu_command_disabled=False)  # статус для работы кнопки команды menu

    #проверка наличия email----------------------------------------------------------------
    var_query = (
        f"SELECT c_email "
        f"FROM t_user "
        f"WHERE c_user_id = '{vUserID}'"
    )
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
    vEmail = var_Arr[0][0]
    #logger.info(f'vEmail:{vEmail}')

    if (callback.data[:6] == 'buy_c_'):
        if (callback.data[-1] == 'y'):
            await state.set_state(myState.buy_y)
        elif (callback.data[-1] == 'm'):
            await state.set_state(myState.buy_m)
        elif (callback.data[-1] == 'w'):
            await state.set_state(myState.buy_w)

        if vEmail:
            #формирование счета
            await gen___f_buy(state, pool, vEmail, callback_obj = callback)
            await pgDB.fExec_LogQuery(pool_log, vUserID, f"gen___clbck_buy|bill|vEmail:{vEmail}")
        else:
            # запрос на ввод email----------------------------------------------------------------
            str_Msg = (
                f'Договор-оферта доступен по ссылке ниже \n\n'
                f'Для регистрации введите, пожалуйста, ваш e-mail с клавиатуры (example@example.com)\n\n'
            )
            builder = InlineKeyboardBuilder()
            webapp = WebAppInfo(url=config.URL_AGR)
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('agrmnt'), web_app=webapp))
            await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)  #
            # await pgDB.fExec_LogQuery(pool_log, vUserID, f'|price_edu_c_||edu08')

            await pgDB.fExec_LogQuery(pool_log, vUserID, f"gen___clbck_buy|buy_c_|email")



    # проверка запроса на оплату---------------------------------------------------------------
    if (callback.data[:6] == 'buy_v_'):

        curState = await state.get_state()

        payment_id = callback.data.split('v_')[-1]
        vStatus, vPaid, vSaved, vCardID, vAmount, vMeta = myPay.fCheck(payment_id)
        vPeriod = vMeta['period']
        isToken = 0
        if vPeriod == '1 month':
            strPeriod = 'm'
            valToken = 1000
        elif vPeriod == '3 month':
            strPeriod = 'q'
            valToken = 3000
        elif vPeriod == '1 year':
            strPeriod = 'y'
            valToken = 36000
        elif vPeriod == '7 days':
            strPeriod = 'w'
            valToken = 800

        qBalance = f'c_balance + {valToken}'
        #logger.info(f'vUserID:{vUserID}|vStatus:{vStatus}|vPaid:{vPaid}|vSaved:{vSaved}|vCardID:{vCardID}|qBalance:{qBalance}')


        #handler of payment status
        if vStatus == 'succeeded':
            # запись в таблицу t_user
            var_query = (
                f"UPDATE t_user "
                f"SET "
                f"  c_amount = '{vAmount}', "
                f"  c_saved_payment = '{vSaved}', "
                f"  c_card_id = '{vCardID}', "
                f"  c_subscription_status = '1', "
                f"  c_next_payment_date = GREATEST("
                f"      COALESCE(c_next_payment_date, current_date), "
                f"      current_date"
                f"  ) + INTERVAL '{vPeriod}', "
                f"  c_sub_period = '{strPeriod}', "
                f"  c_balance = {qBalance} "
                f"WHERE c_user_id = '{vUserID}'"
            )
            await pgDB.fExec_UpdateQuery(pool_base, var_query)
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="menu"))
            str_Msg = (
                f'Ваша подписка активна. Спасибо за то, что Вы с нами!\n\n'
                f"<b>Перейдите {myF.fCSS('fw')}</b>\n"
            )
            await state.update_data(sub_stat=None)

            await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)  #
            await pgDB.fExec_LogQuery(pool_log, vUserID, f'gen___clbck_buy|buy_v_|succeded')
        else:
            #ajrm
            var_query = (
                f"SELECT c_payment_link FROM t_payment WHERE c_payment_id = '{payment_id}'"
            )
            var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
            payment_url = var_Arr[0][0]
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text='Оплатить', url=payment_url))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data=f'buy_v_{payment_id}'))
            builder.adjust(2)

            str_Msg = 'Необходимо завершить оплату'
            await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
            await pgDB.fExec_LogQuery(pool_log, vUserID, f'gen___clbck_buy|buy_v_|failure')




# ----------------------------------------------------------------------
@r_start.message((F.text & ~F.text.startswith('/')), StateFilter(myState.buy_m, myState.buy_q, myState.buy_y, myState.buy_w))
async def gen___text_buy(message: types.Message, state: FSMContext, pool):
    '''
    обработка ввода email текстом
    выставление платежа
    '''
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot


    isEmail = is_email(message.text)


    if isEmail:
        # формирование счета
        await gen___f_buy(state, pool, message.text, message_obj = message)
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'gen___text_buy|gen___f_buy|recieved email:{message.text}')

    else:
        '''
        str_Msg = (
            f'Введены некорректные данные\n'
            f'Пожалуйста, укажите корректный email\n\n'
            f'Формат: example@example.com'
        )
        '''
        #await message.answer(str_Msg, parse_mode=ParseMode.HTML)  # reply_markup=builder.as_markup(),


        from aiogram.types import ForceReply
        await message.answer(
            "📧 Введены некорректные данные\nПожалуйста, укажите корректный email:",
            reply_markup=ForceReply(
                input_field_placeholder="example@mail.com",
                selective=True
            )
        )
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'gen___text_buy|email text input|failure')


#формирование счета
async def gen___f_buy(state: FSMContext, pool, v_email, message_obj=None, callback_obj=None):
    pool_base, pool_log = pool

    msgObject = callback_obj.message if callback_obj else message_obj
    vUserID = msgObject.chat.id
    bot = msgObject.bot

    user_data = await state.get_data()
    price_m = user_data.get('price_m', '')
    price_q = user_data.get('price_q', '')
    price_y = user_data.get('price_y', '')
    price_w = user_data.get('price_w', '')

    curState = await state.get_state()
    varAmount = 0
    if curState == myState.buy_m.state:
        varAmount = price_m
        vPeriod = '1 month'
        item_desc = 'Ежемесячная подписка LingoMojo'
    elif curState == myState.buy_q.state:
        varAmount = price_q
        vPeriod = '3 month'
        item_desc = 'Ежеквартальная подписка LingoMojo'
    elif curState == myState.buy_y.state:
        varAmount = price_y
        vPeriod = '1 year'
        item_desc = 'Годовая подписка LingoMojo'
    elif curState == myState.buy_w.state:
        varAmount = price_w
        vPeriod = '7 days'
        item_desc = 'Недельное погружение с LingoMojo'


    # сохранение в БД инфо для последующих оплат
    var_query = """
        UPDATE t_user 
        SET c_email = $1 
        WHERE c_user_id = $2 
    """
    await pgDB.fExec_UpdateQuery_args(pool_base, var_query, v_email, vUserID)
    # выставление счета
    if varAmount != 0:
        logger.info(f'-----------------------varAmount:{varAmount}|vPeriod:{vPeriod}|item_desc:{item_desc}')
        payment_url, payment_id = await myPay.fCreatePayment(varAmount, vUserID, False, pool_base, vPeriod, item_desc)

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text='Оплатить', url=payment_url))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data=f'buy_v_{payment_id}'))
        str_Msg = f'Счет сформирован\nНажмите "Оплатить"\nПосле оплаты нажмите {myF.fCSS("fw")}'
        await msgObject.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)  #

        var_query = (
            f"INSERT INTO t_payment (c_date, c_payment_id, c_payment_link, c_payment_status, c_user_id) "
            f"VALUES (CURRENT_TIMESTAMP::timestamp, '{payment_id}', '{payment_url}', 2, {vUserID}) "
        )
        await pgDB.fExec_UpdateQuery(pool_base, var_query)

        await pgDB.fExec_LogQuery(pool_log, vUserID, f'gen___f_buy|invoice text||{curState}')

def is_email(text):
    """
    Check if a text is a valid email address using regex.

    Args:
        text (str): The text to validate

    Returns:
        bool: True if text is a valid email, False otherwise
    """
    if not text or not isinstance(text, str):
        return False

    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    return bool(re.match(pattern, text.strip()))





def _______________dummy():
    pass



def assign_variant(user_id: int, test_name: str, stepN: str, variants: dict = {"A": 50, "B": 30, "C": 20}):
    """
    Assigns user to variant using cryptographic hash with weighted distribution

    Args:
        user_id: User identifier
        test_name: Test name for consistent hashing
        variants: Dict with variant names and their percentage weights
                 Example: {"A": 50, "B": 30, "C": 20}

    Returns:
        str: Variant name (e.g., "A", "B", or "C")
    """
    # Validate that percentages sum to 100
    total_weight = sum(variants.values())
    if total_weight != 100:
        raise ValueError(f"Variant weights must sum to 100, got {total_weight}")

    # Generate hash
    hash_input = f"{user_id}_{stepN}_{test_name}".encode('utf-8')
    hash_digest = hashlib.md5(hash_input).hexdigest()
    # Use first 8 characters to avoid integer overflow
    hash_val = int(hash_digest[:8], 16) % 100  # Get percentage (0-99)

    # Assign based on cumulative percentages
    cumulative = 0
    for variant, weight in variants.items():
        cumulative += weight
        if hash_val < cumulative:
            return variant

    # Fallback (shouldn't happen if weights sum to 100)
    return list(variants.keys())[-1]




# chapter----------------------------------------------------------------------------------------------------------------------------------------------- qstart callback
@r_start.callback_query(F.data.startswith("qstart"))
async def callback_qstart(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    await state.set_state(myState.qstart)
    bot = callback.bot
    builder = InlineKeyboardBuilder()

    if callback.data == 'qstart_lvl':
        builder.add(types.InlineKeyboardButton(text='A', callback_data="qstart_t1"))
        builder.add(types.InlineKeyboardButton(text="B", callback_data="qstart_t2"))
        builder.add(types.InlineKeyboardButton(text="C", callback_data="qstart_t3"))
        builder.adjust(3)
        str_Msg = (
            f"Укажите свой примерный уровень английского:\n"
            f"Ａ. Beginner\n"
            f"Ｂ. Intermediate\n"
            f"Ｃ. Advanced"
        )
    if callback.data[:8] == 'qstart_t':
        vLvl = int(callback.data[-1])
        var_query = (
            f"UPDATE t_user_paramssingle "
            f"SET c_ups_eng_level = '{vLvl}' "
            f"WHERE c_ups_user_id = '{vUserID}'"
        )
        await pgDB.fExec_UpdateQuery(pool_base, var_query)

        builder.add(types.InlineKeyboardButton(text='A', callback_data="qstart_i1"))  # qstart_i1
        builder.add(types.InlineKeyboardButton(text="B", callback_data="qstart_i2"))
        builder.add(types.InlineKeyboardButton(text="C", callback_data="qstart_i3"))
        builder.add(types.InlineKeyboardButton(text="D", callback_data="qstart_i4"))
        builder.adjust(2, 2)
        str_Msg = (
            f"Какая у Вас цель изучения английского?\n"
            f"Ａ. карьерные перспективы\n"
            f"Ｂ. личностный рост\n"
            f"Ｃ. сертификация\n"
            f"Ｄ. адаптация"
        )

    if callback.data[:8] == 'qstart_i':
        '''
        vTarget = int(callback.data[-1])

        var_query = (
            f"UPDATE t_user_paramssingle "
            f"SET c_ups_target = '{vTarget}' "
            f"WHERE c_ups_user_id = '{vUserID}'"
        )
        await pgDB.fExec_UpdateQuery(pool_base, var_query)
        '''

        builder.add(types.InlineKeyboardButton(text=myF.fCSS('qstart'), callback_data="qstart_1"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="menu"))
        builder.adjust(2)
        str_Msg = (
            f"В целом Вы можете уже пользоваться ботом, он интуитивно понятен, нажимайте далее и вперед ❱❱  \n\n"
            f"При нажатии на <b>Quick start</b> Вы получите краткую инструкцию по интерфейсу бота \n\n"
            f"Также рекомендую пройти обучение (см. соответствующий раздел меню)\n"
        )
    if callback.data == 'qstart_1':
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="qstart_2"))
        str_Msg = (
            f"<i>Quick start| 1 из 5</i>\n\n"
            f"Содержание <b>Меню</b>:\n"
            f"<b><i>{myF.fCSS('daily')}</i></b> - основной и наиболее посещаемый пункт, здесь Вы найдете список ежедневных заданий\n"
            f"<b><i>{myF.fCSS('speak')}</i></b> - раздел с разговорными заданиями <i>(подробнее см. далее)</i>\n"
            f"<b><i>{myF.fCSS('repeat')}</i></b> - раздел изучения новых слов\n"
            f"<b><i>{myF.fCSS('settings')}</i></b> - собственно, настройки"
        )
    if callback.data == 'qstart_2':
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="qstart_3"))
        str_Msg = (
            f"<i>Quick start| 2 из 5</i>\n\n"
            f"Разговорные задания собраны в разделе <b>{myF.fCSS('speak')}</b>:\n"
            f"<b><i>Диалог</i></b> - поддержание разговора с ботом <i>(подробнее см. далее)</i>\n"
            f"<b><i>Монолог</i></b> - небольшой спич на заданную тему\n"
            f"<b><i>Listen and repeat</i></b> - прослушать и воспроизвести как можно ближе к оригиналу \n"
            f"<b><i>Retelling</i></b> - пересказ текста \n"
        )
    if callback.data == 'qstart_3':
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="qstart_4"))
        str_Msg = (
            f"<i>Quick start| 3 из 5</i>\n\n"
            f"<b>Диалоги</b>\n\n"
            f"<b><i>Какие новости, small talk, ситуации</i></b> - диалоги на повседневные темы. \n"
            f"<b><i>Собеседование</i></b> - более сложный диалог, в котором сначала необходимо загрузить описание вакансии, свое резюме или выбрать из преднастроенных.\n"
            f"На основе вакансии и резюме будет подготовлен план собеседования\n"
        )
    if callback.data == 'qstart_4':
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="qstart_5"))
        str_Msg = (
            f"<i>Quick start| 4 из 5</i>\n\n"
            f"Работа с новыми словами \n"
            f"<b><i>{myF.fCSS('PickOut')}</i></b> - после некоторых заданий Вам будут рекомендованы слова к изучению. "
            f"В данном разделе можно просмотреть каждое слово и добавить его к изучаемым\n"
            f"<b><i>{myF.fCSS('repeat')}</i></b> - повтор изучаемых слов\n"
            f"<b><i>{myF.fCSS('oxford3')}</i></b> - добавление случайных слов из 3000 наиболее употребляемых к списку рекомендованных\n"
        )
    if callback.data == 'qstart_5':
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="menu"))
        str_Msg = (
            f"<i>Quick start| 5 из 5</i>\n\n"
            f"<b>{myF.fCSS('settings')}</b> \n"
            f"<b><i>Уровни английского</i></b> - Предусмотрено 3 уровня - A, B, C. "
            f"Первоначально Вам присваивается уровень A. Поменять его можно в разделе настроек\n"
            f"<b><i>Напоминания</i></b> - ежедневно Вам будут приходить напоминания о занятиях. В настройках можно изменить параметры уведомлений"
        )

    nm_updImg = myF.fImageAddQuote(myF.fGetImg('menu'))
    with open(nm_updImg, "rb") as image_In:
        msg = await callback.message.answer_photo(
            BufferedInputFile(image_In.read(), filename="menu.jpg"),
            caption=str_Msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    # myF.fDelFile(nm_updImg)
    await myF.afDelFile(nm_updImg)
    await callback.message.delete()
    await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)


'''
builder = InlineKeyboardBuilder()
    #builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
    #builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="qstart"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="qstart_lvl"))
    #builder.adjust(2)


    nm_updImg = myF.fGetImg('start')
    str_Msg = (
        f'✋ Приветствуем! \n'
        f'Спасибо за интерес! 🙏 \n\n'
        f'Это бот для <b>практики</b> английского 💬.\n'
        f'С ним Вы будете обсуждать Ваши последние новости, обыгрывать ситуации, проходить собеседования...\n'
        f'Он проанализирует фразы, предложить альтернативы и порекомендует слова к изучению\n\n'
        f'На текущий момент это полностью бесплатно. \n\n'
        f'Попробуете?\n\n'
        f'Нажимайте далее'
    )

    with open(nm_updImg, "rb") as img:
        msg = await message.answer_photo(BufferedInputFile(img.read(), filename="start.jpg"), caption=str_Msg, reply_markup=builder.as_markup(),parse_mode=ParseMode.HTML)
    #await callback.message.delete()
    await myF.fSubMsgDel(state, pool, vUserID, message.message_id, msg.message_id, bot, 2)      #
    await pgDB.fExec_LogQuery(pool_log, message.chat.id, 'start')
'''



'''
toggle = {
        '1': {
            'ind': "0",
            'desc': "🎵 текст аудио"
        },
        '2': {
            'ind': "0",
            'desc': f"{myF.fCSS('trs_on')}"
        },
        '3': {
            'ind': "0",
            'desc': '🔴 A'
        },
        '4': {
            'ind': "1",
            'desc': '🟡 B'
        },
        '5': {
            'ind': "0",
            'desc': '🟢 C'
        },
        '6': {'ind': "0", 'desc': '1️⃣ Career'},
        '7': {'ind': "0", 'desc': '2️⃣ Study'},
        '8': {'ind': "0", 'desc': '3️⃣ Travel'},
        '9': {'ind': "0", 'desc': '4️⃣ Live abroad'},
        '10': {'ind': "0", 'desc': '5️⃣ Fluency'},
        '11': {'ind': "0", 'desc': '6️⃣ Culture'},
        # '12': {'ind': "0", 'desc': '7️⃣'},
        # '13': {'ind': "0", 'desc': '8️⃣'},
    }
'''