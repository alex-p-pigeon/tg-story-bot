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
        # запись в redis discount = 1
        await state.update_data(discount=1)


    #await state.set_state(myState.varA_st0)  # установка статуса

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
            # Восстанавливаем статус при разблокировке
            var_query = (
                f"UPDATE t_user "
                f"SET c_subscription_status = 3, "
                f"    c_free_actions_count = 0, "
                f"    c_free_actions_date = NULL "
                f"WHERE c_user_id = $1"
            )
            await pgDB.fExec_UpdateQuery_args(pool_base, var_query, vUserID)
    return isExist


def ______vB():
    pass

async def vB_st1___story(message, state, pool):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot

    story_id = 21
    from .oth_handlers import handle_story_start
    await handle_story_start(None, state, pool, story_id, message = message)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'vB_st1___story|')



@r_start.callback_query(F.data == "vB_st2")
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

    msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'vB_st2___clbck_offer|')


@r_start.callback_query(F.data == "vB_st3")
async def vB_st3___clbck_buy(callback, state, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

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
        if (callback.data[-1] == 'q'):
            await state.set_state(myState.buy_q)
        elif (callback.data[-1] == 'm'):
            await state.set_state(myState.buy_m)

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
@r_start.message((F.text & ~F.text.startswith('/')), StateFilter(myState.buy_m, myState.buy_q))
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
    price_m = 499#user_data.get('price_m', '')
    price_q = 499#user_data.get('price_q', '')

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


    # сохранение в БД инфо для последующих оплат
    var_query = """
        UPDATE t_user 
        SET c_email = $1 
        WHERE c_user_id = $2 
    """
    await pgDB.fExec_UpdateQuery_args(pool_base, var_query, v_email, vUserID)
    # выставление счета
    if varAmount != 0:
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