from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
import re
import hashlib
import string
import hmac

from states import myState
import selfFunctions as myF
import prompt as myP
import fpgDB as pgDB
from datetime import datetime

import logging

# Get logger for this specific module
logger = logging.getLogger(__name__)

# Create router for tech handlers
tech_router = Router()





# Tech menu function
async def f_techmenu(message_obj=None, callback_obj=None):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="register link", callback_data="tech_link"))
    builder.add(types.InlineKeyboardButton(text="slang quiz", callback_data="tech_quiz"))
    builder.add(types.InlineKeyboardButton(text="🆕 New Quest", callback_data="story_new"))
    builder.add(types.InlineKeyboardButton(text="Menu", callback_data="menu"))
    builder.adjust(2, 1, 1)
    str_Msg = 'choose'
    if callback_obj:
        await callback_obj.message.answer(str_Msg, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())
    else:
        await message_obj.answer(str_Msg, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())

@tech_router.message(Command("remin"))
async def cmd_tech(message: types.Message, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = message.chat.id

    if vUserID == 372671079:
        await f_techmenu(message_obj=message)

@tech_router.callback_query(F.data.startswith('tech_'))
async def callback_tech(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    if vUserID == 372671079:
        if callback.data == 'tech_menu':
            await state.set_state(myState.common)
            await f_techmenu(callback_obj=callback)
        elif callback.data == 'tech_link':
            await state.set_state(myState.techlink)
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text="Tech menu", callback_data="tech_menu"))
            builder.add(types.InlineKeyboardButton(text="Menu", callback_data="menu"))
            builder.adjust(1, 1)
            str_Msg = 'Введи наименование канала привлечения'
            # Fix: use callback.message instead of message
            await callback.message.answer(str_Msg, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())
        elif callback.data == 'tech_quiz':
            await state.set_state(myState.genreminder)
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text="Tech menu", callback_data="tech_menu"))
            builder.add(types.InlineKeyboardButton(text="Menu", callback_data="menu"))
            builder.adjust(1, 1)
            str_Msg = (
                'Ввести в формате - 1:idiom text:date\n'
                '1 - idiom\n'
                '2 - slang'
            )
            # Fix: use callback.message instead of message
            await callback.message.answer(str_Msg, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())


@tech_router.message(F.text, StateFilter(myState.genreminder))
async def text_genReminder(message: types.Message, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = message.chat.id

    vText = message.text
    arrText = vText.split(':')
    #print("arrText - ", arrText)
    vNum = int(arrText[0])
    vObj = arrText[1]
    vDate = arrText[2]
    #print('vNum - ', vNum, '|vObj - ', vObj, '|vDate - ', vDate)
    prompt = myP.fPromptReminder(vNum, vObj, 1)
    v_comment = await myF.afSendMsg2AI(prompt, pool_base, vUserID)  #, iModel = 4
    #print('v_comment - ', v_comment)
    prompt = myP.fPromptReminder(vNum, vObj, 2)
    v_res = await myF.afSendMsg2AI(prompt, pool_base, vUserID)  #{1} True {2} false1 {3} false2 {4} false3 {5} example
    #print('v_res - ', v_res)
    parts = re.split(r"\{\d+\}", v_res) # Split on the markers like {1}, {2}, etc.
    varArr = [part.strip() for part in parts if part.strip()]       # Remove any empty strings and strip whitespace
    #print('varArr - ', varArr)

    var_query = (
        "INSERT INTO t_quiz (c_example, c_true, c_false1, c_false2, c_false3, c_comment, c_topic, c_obj) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7, $8) "
        "RETURNING c_id"
    )
    varResp = await pgDB.fFetch_InsertQuery_args(
        pool_base, var_query, varArr[4], varArr[0], varArr[1], varArr[2], varArr[3], v_comment, vNum, vObj
    )
    #print('varResp - ', varResp)
    vDateObj = datetime.strptime(vDate, "%d.%m.%Y").date()
    quiz_id = varResp['c_id']
    var_query = (
        "INSERT INTO t_quiz_reminder (c_date, c_quiz_id) "
        "VALUES ($1, $2) "
        "RETURNING c_id"
    )
    varRes = await pgDB.fFetch_InsertQuery_args(pool_base, var_query, vDateObj, quiz_id)
    #ajrm
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Tech menu", callback_data="tech_menu"))
    builder.add(types.InlineKeyboardButton(text="Menu", callback_data="menu"))
    builder.adjust(1, 1)

    str_Msg = f'''
        <b>Example:</b> {varArr[4]}\n\n
        <b>True:</b> {varArr[0]}\n
        <b>False1:</b> {varArr[1]}\n
        <b>False2:</b> {varArr[2]}\n
        <b>False3:</b> {varArr[3]}\n
        <b>Main desc:</b> {v_comment}\n\n
        If you need one more just text
    '''
    await message.answer(str_Msg, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())

@tech_router.message(F.text, StateFilter(myState.techlink))
async def text_techlink(message: types.Message, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    if vUserID == 372671079:
        SECRET_KEY = '5jf7735i46ji8e787835h4kkr873'
        vCode = generate_channel_code(message.text, SECRET_KEY)
        var_query = '''
            INSERT INTO t_user_mark (c_desc, c_link)  
            VALUES ($1, $2) 
            ON CONFLICT (c_desc) DO NOTHING
        '''
        await pgDB.fExec_UpdateQuery_args(pool_base, var_query, message.text, vCode)
        str_Msg= (
            f'DB updated\n\n'
            f'Link:\n'
            f'<code>https://t.me/LingoMojo_bot?start={vCode}</code>'
        )
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="Tech menu", callback_data="tech_menu"))
        builder.add(types.InlineKeyboardButton(text="Menu", callback_data="menu"))
        builder.adjust(1, 1)
        await message.answer(str_Msg, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())


def generate_channel_code(channel_name, secret_key, campaign_num = 1, length=10):
    """

    Generate code using HMAC-SHA256 with secret key.
    Cannot be reversed without knowing the secret key.

    Generate a deterministic code based on channel name using hash function.
    Same channel name will always produce the same code.

    Args:
        channel_name (str): The channel name to base the code on
        length (int): Length of the generated code (default 8)

    Returns:
        str: Deterministic alphanumeric code
    """
    combined_input = f"{channel_name}_v{campaign_num}"
    # Use HMAC with secret key
    hmac_hash = hmac.new(
        secret_key.encode(),
        combined_input.encode(),
        hashlib.sha256
    ).digest()



    # Convert to alphanumeric (lowercase + digits)
    characters = string.ascii_lowercase + string.digits
    code = ""

    for i in range(length):
        byte_value = hmac_hash[i]
        char_index = byte_value % len(characters)
        code += characters[char_index]

    return code



#------------------------------------------------------------------------------------- Команда gram
@tech_router.message(Command("allgram"))
async def cmd_gram(message: types.Message, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot
    await state.set_state(myState.common)

    var_query = "SELECT c_ldesc FROM t_grammar WHERE c_ldesc IS NOT NULL;"
    arrGrammar = await pgDB.fExec_SelectQuery(pool_base, var_query)

    c_cnt = 0
    total = len(arrGrammar)

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="<<", callback_data="allgram-l"))
    builder.add(types.InlineKeyboardButton(text=">>", callback_data="allgram-r"))
    builder.adjust(2)

    str_Msg = (
        f"{c_cnt+1} / {total}\n\n"
        f"{arrGrammar[c_cnt][0]}"
    )

    await message.answer(str_Msg, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())

    await state.update_data(arrGrammar=arrGrammar)
    await state.update_data(c_cnt=c_cnt)
    print('allgram0')

    #cmd - get c_id, c_ldesc list
    #c_cnt
    #callback
    #bck and fw through the list

#------------------------------- gram callback
@tech_router.callback_query(F.data.startswith("allgram-"))
async def callback_allgram(callback: types.CallbackQuery, state: FSMContext, pool):
    print('allgram1')
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    print('allgram1_1')
    #curState = await state.get_state()
    data = await state.get_data()
    arrGrammar = data['arrGrammar']
    c_cnt = data['c_cnt']
    total = len(arrGrammar)

    if callback.data == "allgram-r":
        c_cnt = (c_cnt + 1) % total
    elif callback.data == "allgram-l":
        c_cnt = (c_cnt - 1) % total



    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="<<", callback_data="allgram-l"))
    builder.add(types.InlineKeyboardButton(text=">>", callback_data="allgram-r"))
    builder.adjust(2)

    str_Msg = (
        f"{c_cnt} / {total}\n\n"
        f"{arrGrammar[c_cnt][0]}"
    )
    await callback.message.edit_text(str_Msg, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())
    await callback.answer()
    await state.update_data(c_cnt=c_cnt)
    print('allgram2')


