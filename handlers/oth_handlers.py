from aiogram import Router, F, types, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, ReplyKeyboardRemove, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
import random
import requests
import json
#from telegram.constants import ParseMode

import math, os, sys
from ctypes import *
from typing import Dict, Any, Optional, List
from contextlib import suppress
import uuid
import re
from googleapiclient.discovery import build
import schedule
from typing import Any, Callable, Dict, Awaitable

import aiohttp

import librosa
import soundfile as sf
from pydub import AudioSegment


from aiogram.enums import ParseMode

from aiogram.utils.keyboard import InlineKeyboardBuilder

from datetime import datetime, date, timezone, timedelta

from aiogram.filters.command import Command
from aiogram.filters import Command, StateFilter
from aiogram.filters.callback_data import CallbackData
#from aiogram.filters.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

#from aiogram.enums import ParseMode
from aiogram.methods.send_audio import SendAudio
from aiogram import html
from aiogram.utils.formatting import Text, Bold
from aiogram.utils.formatting import (
    Bold, as_list, as_marked_section, as_key_value, HashTag
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile

#custom
from states import myState
import selfFunctions as myF
import mynaming as myN
import prompt as myP
import fpgDB as pgDB
import fPayment as myPay
from config_reader import config
from .learnpath.handlers.story import load_and_show_first_scene


import logging

# Get logger for this specific module
logger = logging.getLogger(__name__)

# Create router for tech handlers
r_oth = Router()







'''
#блок уведомлений о повторе по времени
#   нужно предварительно выставить настройки - по умолчанию в 9 утра и 18 вечера
curtime = datetime.now().time()
if ((curtime.hour == 17) and (curtime.minute == 56)):
    print('test3')
'''

'''
ajarm0
#working:
❎ ❰ ❮ 🐧 📃 💾


◼
#dialog
🗪
💭

#repeat
🔁
🔄

#alarm
⏰

🔸
💬
📌📌


-->
⮌
⮊
⮈
👉
👈

#no
❌

#question
❓
❗
✨
⏳
⏳
⮜
⮝

⚡
☕

📌

📍
👌
✅

✔️
🇬🇪
ℹ️
📌
❗️
➡️
💬
💤
💡

💡
💾
📤

📥

🧿
⚙

IsNull = 0
if resQuery[0][1] is None: IsNull = 1
else: if resQuery[0][1] == '': IsNull = 1
'''


#
# chapter========================================================================================================================================================general sync functions


def fGetMsgFromWordArr(gp_Cnt, var_Arr: list):
    arr_Len = len(var_Arr)
    vExample = var_Arr[gp_Cnt][6]
    vOrigin = var_Arr[gp_Cnt][7]
    vDict = var_Arr[gp_Cnt][8]

    vStr = myF.fShapeWordCard(
        var_Arr[gp_Cnt][1],  # lemma
        var_Arr[gp_Cnt][3],  # Rus
        # var_Arr[gp_Cnt][4], #Alt
        var_Arr[gp_Cnt][2],  # strIPA
        vExample,  # WordCard     var_Arr[gp_Cnt][5]  vWordCard
        vOrigin,
        vDict
    )
    varStr = (
        f"{gp_Cnt + 1} из {arr_Len} \n"
        f"{vStr}"
    )
    '''
    strAlt_fin = var_Arr[gp_Cnt][4] or ''  #альтенативный перевод
    #strWordCard = f'🔍 🇬🇧 <b>Толковый словарь:</b>\n<blockquote expandable="true">{var_Arr[gp_Cnt][5]}</blockquote>' or ''  #word card
    strWordCard = var_Arr[gp_Cnt][5] or ''  #word card

    transcription = var_Arr[gp_Cnt][2] or ''    #транскрипция
    transcription_str = f"      <code>[{transcription}] </code>\n" if transcription else ""

    varStr = (
        f"{gp_Cnt + 1} из {arr_Len} \n"
        f"📖 <b>{var_Arr[gp_Cnt][1]}</b> \n"
        f"{transcription_str}"
        f"      {var_Arr[gp_Cnt][3]} (<i>{strAlt_fin}</i>)\n\n"
        f"{strWordCard}"
    )
    '''

    return varStr


# обработка ответа ИИ с анализом монолога
async def fMonologCheckProcessing(var_StrX, strOriginal, pool_base, vUserID, nlp_tools):
    # response from AI has {1} {2] {3] and - symbols
    # we sequentially cut necessary parts from response to form return string
    # - part with mask '{1} - Y {2]' gives Y to put into variable str_Improved
    var_Str = fInStr(var_StrX, '{1}', '{2}')
    str_Improved = ''
    if var_Str is not None:
        str_Improved = fInStr(var_Str, ':', )
    # print('1|str_Improved = ', str_Improved)

    # - part with mask '{2} - Y {3]' gives Y to put into variable str_Err
    var_Str = fInStr(var_StrX, '{2}', '{3}')
    str_Err = ''
    if var_Str is not None:
        str_Err = fInStr(var_Str, ':', )
    # print('2|str_Err = ', str_Err)

    # - part with mask '{3} - Y ' gives Y to put into variable str_Synonyms
    var_Str = fInStr(var_StrX, '{3}', )
    str_Synonyms = ''
    if var_Str is not None:
        str_Synonyms = fInStr(var_Str, ':', )
    # print('3|str_Synonyms = ', str_Synonyms)
    varArr = myF.fArrSynonyms(str_Synonyms, strOriginal)  # фунция формирования очищенного массива синонимов

    arrSyn2DB, varStr2 = await myF.fLemmatizeWordList(varArr, pool_base, vUserID, nlp_tools)

    '''
    # выделенние лемм
    lemmatizer = WordNetLemmatizer()
    varStr2_list = []
    arrSyn2DB = []

    #varArrTmp = []
    for strWord in varArr:
        # Get POS tagging and lemmatization
        tagged_word = pos_tag([strWord])[0]
        wordnet_pos = myF.get_wordnet_pos(tagged_word[1]) or wordnet.NOUN
        lemma = lemmatizer.lemmatize(strWord, pos=wordnet_pos)

        # Get translation
        v_Rus = await myF.fDBTranslate(lemma, pool_base)
        flag2db = 0

        if v_Rus is None:
            v_Rus = await myF.afGoogleTrans(lemma, pool_base, vUserID)  # Google Translate
            flag2db = 1
        arrSyn2DB.append([lemma, v_Rus, flag2db])  # Store in DB list
        varStr2_list.append(f'{lemma} - {v_Rus}\n')  # Store for user output
    # Final formatted string
    varStr2 = ''.join(varStr2_list)
    '''

    return str_Improved, str_Err, varStr2, arrSyn2DB


# ajar
async def f_isDailyDB(vUserID, pool_base):
    #
    fTimer()
    # проверка статусов
    var_query = (
        f"SELECT c_user_id, c_date, c_pick_out, c_repeat, c_lnr, c_retell, c_dial_news, c_dial_situation, c_monolog, c_oxford3, c_edu FROM t_daily WHERE c_user_id = '{vUserID}'"
    )
    resQuery = await pgDB.fExec_SelectQuery(pool_base, var_query)
    print(resQuery)
    vDateToday = date.today().strftime("%Y%m%d")
    if int(resQuery[0][1]) < int(vDateToday):  # в начале нового дня принудительное очищение статусов
        var_query = (
            f"UPDATE t_daily "
            f"SET c_date = '{vDateToday}', c_pick_out = 0, c_repeat = 0, c_lnr = 0, c_retell = 0, c_dial_news = 0, c_dial_situation = 0, c_monolog = 0, c_oxford3 = 0 "
            f"WHERE c_user_id = '{vUserID}'"
        )  # не изменяется c_edu
        await pgDB.fExec_UpdateQuery(pool_base, var_query)
        resDict = {
            'isDaily': 0, 'c_date': vDateToday, 'c_pick_out': 0, 'c_repeat': 0, 'c_lnr': 0,
            'c_retell': 0, 'c_dial_news': 0, 'c_dial_situation': 0, 'c_monolog': 0, 'c_oxford3': 0,
            'c_edu': resQuery[0][10]
        }
    else:
        resDict = {
            'isDaily': 0, 'c_date': resQuery[0][1], 'c_pick_out': resQuery[0][2], 'c_repeat': resQuery[0][3],
            'c_lnr': resQuery[0][4], 'c_retell': resQuery[0][5], 'c_dial_news': resQuery[0][6],
            'c_dial_situation': resQuery[0][7],
            'c_monolog': resQuery[0][8], 'c_oxford3': resQuery[0][9], 'c_edu': resQuery[0][10]
        }
    fTimer('isDailyDB')
    return resDict


def f_isDaily(vElement, resDict):
    #
    fTimer()
    dictDailyLimit = {'c_pick_out': 1, 'c_repeat': 1, 'c_lnr': 7, 'c_retell': 2, 'c_dial_news': 1,
                      'c_dial_situation': 2, 'c_monolog': 1, 'c_oxford3': 1}

    isDaily = 0
    limitCnt = 0
    limit = 0

    if vElement == 'c_pick_out' and (resDict['c_pick_out'] < dictDailyLimit['c_pick_out']): isDaily = 1; limitCnt = \
    resDict['c_pick_out']; limit = dictDailyLimit['c_pick_out']
    if vElement == 'c_repeat' and (resDict['c_repeat'] < dictDailyLimit['c_repeat']): isDaily = 1; limitCnt = resDict[
        'c_repeat']; limit = dictDailyLimit['c_repeat']
    if vElement == 'c_lnr' and (resDict['c_lnr'] < dictDailyLimit['c_lnr']): isDaily = 1; limitCnt = resDict[
        'c_lnr']; limit = dictDailyLimit['c_lnr']
    if vElement == 'c_retell' and (resDict['c_retell'] < dictDailyLimit['c_retell']): isDaily = 1; limitCnt = resDict[
        'c_retell']; limit = dictDailyLimit['c_retell']
    if vElement == 'c_dial_news' and (resDict['c_dial_news'] < dictDailyLimit['c_dial_news']): isDaily = 1; limitCnt = \
    resDict['c_dial_news']; limit = dictDailyLimit['c_dial_news']
    if vElement == 'c_dial_situation' and (
            resDict['c_dial_situation'] < dictDailyLimit['c_dial_situation']): isDaily = 1; limitCnt = resDict[
        'c_dial_situation']; limit = dictDailyLimit['c_dial_situation']
    if vElement == 'c_monolog' and (resDict['c_monolog'] < dictDailyLimit['c_monolog']): isDaily = 1; limitCnt = \
    resDict['c_monolog']; limit = dictDailyLimit['c_monolog']
    if vElement == 'c_oxford3' and (resDict['c_oxford3'] < dictDailyLimit['c_oxford3']): isDaily = 1; limitCnt = \
    resDict['c_oxford3']; limit = dictDailyLimit['c_oxford3']
    if vElement == 'menu':
        if (resDict['c_pick_out'] < dictDailyLimit['c_pick_out']) or (
                resDict['c_repeat'] < dictDailyLimit['c_repeat']) or \
                (resDict['c_lnr'] < dictDailyLimit['c_lnr']) or (resDict['c_retell'] < dictDailyLimit['c_retell']) or \
                (resDict['c_dial_news'] < dictDailyLimit['c_dial_news']) or (
                resDict['c_dial_situation'] < dictDailyLimit['c_dial_situation']) or \
                (resDict['c_monolog'] < dictDailyLimit['c_monolog']) or (
                resDict['c_oxford3'] < dictDailyLimit['c_oxford3']):
            isDaily = 1;
            limitCnt = 0;
            limit = 0
    fTimer('daily' + vElement)
    return isDaily, str(limitCnt), str(limit)




def f_BuiderAdjust(index, builder):
    if index == 0:
        return builder.adjust(1)
    elif index == 1:
        return builder.adjust(1, 1)
    elif index == 2:
        return builder.adjust(1, 1, 1)
    elif index == 3:
        return builder.adjust(1, 1, 1, 1)
    elif index == 4:
        return builder.adjust(1, 1, 1, 1, 1)
    elif index == 5:
        return builder.adjust(1, 1, 1, 1, 1, 1)
    elif index == 6:
        return builder.adjust(1, 1, 1, 1, 1, 1, 1)
    elif index == 7:
        return builder.adjust(1, 1, 1, 1, 1, 1, 1, 1)
    elif index == 8:
        return builder.adjust(1, 1, 1, 1, 1, 1, 1, 1, 1)


# ajar

# myF.fCSS('PickOut')








def fTimer(vMark=''):
    global gcTime
    varDate = datetime.now()
    if vMark == '':  # start
        # print("OUT| time Start:", varDate.time().strftime("%H:%M:%S:%f"))
        gcTime = float(varDate.time().strftime("%S%f"))
    if vMark != '':  # end
        # print("OUT| time End:", varDate.time().strftime("%H:%M:%S:%f"))
        varEnd = float(varDate.time().strftime("%S%f"))
        print('-------', vMark, '---->', varEnd - gcTime)
        gcTime = 0





'''
# Example usage:
word = "hello"
transcription = get_word_transcription(word)
if transcription:
    print(f"Transcriptions of '{word}': {transcription}")
else:
    print(f"No transcriptions found for '{word}'.")
'''


# function that cuts and returns a substring from a string between two specified symbols
def fInStr(text, symbolA, symbolB=None):
    start_index = text.find(symbolA)
    if start_index != -1:
        if symbolB is None:
            return text[start_index + 1:]
        else:
            end_index = text.find(symbolB, start_index + 1)
            if end_index != -1:
                return text[start_index + 1:end_index]
    return None




def fGetSubArr_News(vCnt, arrText, arrTrans):
    global gDivider
    vCntL = int(vCnt) * gDivider
    vCntR = vCntL + gDivider
    subArrText = arrText[vCntL:vCntR]  # выделение диапазона текста для отображения
    subArrTrans = arrTrans[vCntL:vCntR]  # выделение диапазона перевода

    return subArrText, subArrTrans






def fGetEmodjiNum(index):
    response = {
        1: '1️⃣', 2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣',
        6: '6️⃣', 7: '7️⃣', 8: '8️⃣', 9: '9️⃣', 10: '🔟'
    }
    '''
    response = {
        1: '1️⃣',
        2: '2️⃣',
        3: '3️⃣',
        4: '4️⃣',
        5: '5️⃣',
        6: '6️⃣',
        7: '7️⃣',
        8: '8️⃣',
        9: '9️⃣'
    }
    '''
    return response.get(index)


def escape_md(text: str) -> str:
    """
    Escapes special characters for MarkdownV2 formatting.
    """
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return ''.join(f"\\{char}" if char in escape_chars else char for char in text)


def mdReplace(vTxt):
    vTxt = vTxt.replace('.', '\\.')
    vTxt = vTxt.replace(')', '\\)')
    vTxt = vTxt.replace('(', '\\(')
    return vTxt




async def fRetellProcess(var_StrX, pool_base, vUserID, nlp_tools):
    str_Cut = ''
    arrSyn2DB = []
    varStr2 = ''
    try:
        str_Cut = var_StrX.split('{3}')[1].split('[')[1].split(']')[0]
        print('str_Cut = ', str_Cut)
    except Exception as e:
        logger.error(f'fRetellProcess |var_StrX.split| err - {e}')
        str_Cut = ''
        # print(str_Cut)
    if str_Cut != '':
        arr_Words = []
        try:
            arr_Words = str_Cut.split(',')
        except Exception as e:
            logger.error(f'fRetellProcess |str_Cut.split|err - {e}')
            arr_Words = []
        if len(arr_Words) > 0:
            arrSyn2DB, varStr2 = await myF.fLemmatizeWordList(arr_Words, pool_base, vUserID, nlp_tools)

    return arrSyn2DB, varStr2



def __________commands____________():
    pass

# ------------------------------------------------------------------------------------- Команда test
@r_oth.message(Command("test0"))
async def cmd_test(message: Message, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot

    logger.info('1---------------------')
    # await state.set_state(myState.test)
    promptUser='''
    
Video: Trump Iran War Address Cold Open - SNL

Subtitles:
[1:33] America's favorite\ntime-traveling R-word. | [1:32] Gump! | [1:30] Forrest Gump! | [1:29] you never know what\nyou're gonna get. | [1:27] I'm like a box of chocolates -- | [1:25] Nobody knows.\nI'm unpredictable. | [1:23] Like, what the hell was that,\nright? | [1:21] Hello from the year 5000. | [1:18] Even I don't know what\nI'm gonna do next. | [1:16] I'm me. | [1:14] well, you did.\nDon't you know who I am? | [1:13] \"This is not what I voted for,\" | [1:10] To all my MAGA voters\nwho are upset and saying, | [1:05] Do one foreign war\nand possibly one civil. | [1:03] I'm allowed to do one. | [1:00] But listen, wars --\nplural, right? | [0:55] And I know on the campaign trail\nI promised no new foreign wars. | [0:51] ♪ Distracting\nfrom the Epstein files ♪ | [0:48] War!\n♪ What is it good for? ♪ | [0:46] And we're doing war. | [0:41] the last 15 years or something,\nso we had to act now. | [0:39] from developing\na nuclear weapon for like | [0:36] As we all know,\nIran has been two weeks away | [0:33] Little wordplay there.\nDid you catch it? | [0:30] decided that we were\nbored of peace. | [0:26] I launched this attack after me\nand my Board of Peace | [0:24] Yoink!\nRemember when I did that? | [0:20] FIFA Peace Prize winner\nand Nobel Peace Prize taker. | [0:18] It's me, Donald Trump. | [0:17] to all who celebrate. | [0:14] Good evening\nand happy World War III | [0:12] -Hello. Hi.

Analyze the provided subtitles only.
    '''

    promptSys= '''
    You are a language and cultural reference explainer for non-native English speakers 
watching English-language content.
Assume the viewer has B1 English and limited knowledge of US/UK politics and pop culture.

Your task: analyse the provided content and return TWO separate lists:

1. JOKES (items) — jokes, satire, wordplay, cultural references, musical references, memes, 
and allusions that require background knowledge to understand.
   - One joke = one item, even if it spans multiple lines
   - "phrase" = the exact line that completes or delivers the joke
   - Explain WHY it's funny or culturally significant, not just what it means
   - Skip globally obvious facts and well-known historical events

2. SLANG & IDIOMS (slang_items) — slang words, idioms, phrasal verbs, fixed expressions, 
and informal collocations that a B1 learner might not know.
   - One term = one item
   - "term" = the slang word or idiom in its base form
   - "phrase" = the exact line where it appears
   - "meaning" = what it means in plain language
   - "register" = one of: formal | neutral | informal | vulgar
   - Do NOT include terms that are in standard dictionaries as primary meanings
   - Do NOT duplicate items that already appear in jokes (items)

SHARED RULES for both lists:
- "timing" = timestamp of the line (for video), or empty string (for text)
- "context_lines" = list of the specific source lines directly related to this item
- Be concise: max 2-3 sentences per explanation
- Only include items you are confident about — skip ambiguous cases

The content comes from a video. 
Subtitles are provided in REVERSED order — the most recent line is first. 
Keep this in mind when reading context.

Write all explanations strictly in Russian

EXAMPLE INPUT:
[0:48] War! ♪ What is it good for? ♪
[0:51] Absolutely nothing, man. That's a bridge too far.

EXAMPLE OUTPUT:
{
  "items": [
    {
      "title": "War (What Is It Good For) — Edwin Starr",
      "phrase": "♪ What is it good for? ♪",
      "timing": "0:48",
      "context_lines": ["[0:48] War! ♪ What is it good for? ♪"],
      "meaning": "Отсылка к антивоенному хиту Эдвина Старра 1970 года. Полная строчка: 'War, what is it good for? Absolutely nothing.' Ирония в том, что персонаж объявляет войну, цитируя антивоенную песню.",
      "type": "joke"
    }
  ],
  "slang_items": [
    {
      "term": "a bridge too far",
      "phrase": "That's a bridge too far.",
      "timing": "0:51",
      "context_lines": ["[0:51] Absolutely nothing, man. That's a bridge too far."],
      "meaning": "Идиома: 'зайти слишком далеко', сделать что-то чрезмерное или неразумное. Происходит от операции времён Второй мировой войны.",
      "register": "neutral",
      "type": "idiom"
    }
  ]
}

Output valid JSON only. No markdown. Schema:
{
  "items": [
    {
      "title": "short label",
      "phrase": "exact line that delivers the joke",
      "timing": "M:SS or empty string",
      "context_lines": ["line1", "line2"],
      "meaning": "explanation including why it's funny or culturally significant",
      "type": "joke"
    }
  ],
  "slang_items": [
    {
      "term": "the slang word or idiom",
      "phrase": "exact line where it appears",
      "timing": "M:SS or empty string",
      "context_lines": ["line1"],
      "meaning": "plain explanation of what it means",
      "register": "formal | neutral | informal | vulgar",
      "type": "slang or idiom"
    }
  ]
}
    
    '''
    audiotext = await myF.afSendMsg2AI(promptUser, pool_base, vUserID, toggleParam=2, systemPrompt=promptSys)
    logger.info('2---------------------')
    await message.answer(audiotext)


async def test():

    var_StrX = '''
    Ready to accelerate your progress? Premium access unlocks your full potential - click the button below to explore your options
    '''


    var_StrX1 = '''
Great work so far! Here's your next level unlock: authentic newspaper articles. This is where English learners transform into confident readers. These aren't textbook exercises - this is the real deal that native speakers read every day. Ready to join them?
    
Okay. Now let's play a short word game, shall we?

Let’s chat a bit. How’s your day going? Got any news or thoughts to share?

    Hi! You’re at LingoMojo, an English language AI chatbot.
    We can chat through both voice and text messages.
    Let’s get to know each other better — tell me your English level and what goals brought you here.

    '''

    arrVoiceParams = [
        ['en-US', 'en-US-Chirp3-HD-Autonoe', 'FEMALE'],
        ['en-US', 'en-US-Chirp3-HD-Algieba', 'MALE'],

        ['en-AU', 'en-AU-Chirp-HD-D', 'MALE'],
        ['en-AU', 'en-AU-Chirp3-HD-Achernar', 'FEMALE'],
        ['en-AU', 'en-AU-Chirp3-HD-Achird', 'MALE'],
        ['en-AU', 'en-AU-Chirp3-HD-Aoede', 'FEMALE'],
        ['en-IN', 'en-IN-Chirp3-HD-Fenrir', 'MALE'],
        ['en-IN', 'en-IN-Chirp3-HD-Gacrux', 'FEMALE'],
        ['en-GB', 'en-GB-Chirp3-HD-Algenib', 'MALE'],
        ['en-GB', 'en-GB-Chirp3-HD-Aoede', 'FEMALE'],
        ['en-GB', 'en-GB-Chirp3-HD-Callirrhoe', 'FEMALE'],
        ['en-GB', 'en-GB-Chirp3-HD-Despina', 'FEMALE'],
        ['en-US', 'en-US-Chirp3-HD-Achird', 'MALE'],
        ['en-US', 'en-US-Chirp3-HD-Charon', 'MALE'],
        ['en-US', 'en-US-Chirp3-HD-Despina', 'FEMALE'],
        ['en-US', 'en-US-Chirp3-HD-Callirrhoe', 'FEMALE'],
        ['en-US', 'en-US-Chirp3-HD-Algieba', 'MALE'],
        ['en-US', 'en-US-Chirp3-HD-Autonoe', 'FEMALE'],
    ]

    arr_Msg = [
        ['Hi there, what would you like to chat about?', 1],
        ['Hey! Anything you feel like talking about today?', 2],
        ['Hey, what’s up? What do you wanna talk about?', 3],
        ['Hey, what do you want to talk about today?', 4],
    ]

    arr_Msg = [
        ["Hi! What's new since the last time we met?", 1],
        ["Hey! What’s been going on since our last chat?", 2],
        ["Hi! What’s been happening since we last connected?", 3],
    ]




    arrVoiceParams = [
        ['en-AU', 'en-AU-Standard-A', 'FEMALE'],
        ['en-AU', 'en-AU-Standard-B', 'MALE'],
        ['en-AU', 'en-AU-Standard-C', 'FEMALE'],
        ['en-AU', 'en-AU-Standard-D', 'MALE'],
        ['en-GB', 'en-GB-Standard-A', 'FEMALE'],
        ['en-GB', 'en-GB-Standard-B', 'MALE'],
        ['en-GB', 'en-GB-Standard-C', 'FEMALE'],
        ['en-GB', 'en-GB-Standard-D', 'MALE'],
        ['en-GB', 'en-GB-Standard-F', 'FEMALE'],
        ['en-US', 'en-US-Standard-A', 'MALE'],
        ['en-US', 'en-US-Standard-B', 'MALE'],
        ['en-US', 'en-US-Standard-C', 'FEMALE'],
        ['en-US', 'en-US-Standard-D', 'MALE'],
        ['en-US', 'en-US-Standard-E', 'FEMALE'],
        ['en-US', 'en-US-Standard-F', 'FEMALE'],
        ['en-US', 'en-US-Standard-G', 'FEMALE'],
        ['en-US', 'en-US-Standard-H', 'FEMALE'],
        ['en-US', 'en-US-Standard-I', 'MALE'],
        ['en-US', 'en-US-Standard-J', 'MALE'],
    ]




    output = []
    for arrvoice in arrVoiceParams:
        sub_arr = random.choice(arr_Msg)
        var_StrX = sub_arr[0]
        index = sub_arr[1]


        #nm_OGG = await myF.afTxtToOGG(var_StrX, arrvoice, True)
        nm_OGG, nm_OGG_short  = await myF.afTxtToOGG(var_StrX, arrvoice)

        output.append([nm_OGG_short, arrvoice, var_StrX])

        logger.info(f"OGG path - {nm_OGG}")
    logger.info(f"output:{output}")
    #
    '''
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('tz'), web_app=webapp))
    sent_message = await message.answer("Click to open MiniApp:", reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    '''


# обработка ввода ----------------------------------------------------------------------
@r_oth.message(F.text, StateFilter(myState.test))
async def text_test(message: types.Message, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('speak'), callback_data="speak"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('repeat'), callback_data="words"))
    builder.adjust(2)
    vDate = message.text
    print(vDate)
    # vDate = '250112'
    arrRes = await myF.getRmndrPost(vDate, pool)
    markAud = arrRes[2]  # ссылка на аудио
    vText = arrRes[0]
    markImg = arrRes[1]  # ссылка на изображение
    str_Msg = vText
    if markImg != '':
        python_folder = os.path.dirname(sys.executable)
        if os.path.basename(python_folder) == 'bin':
            python_folder = os.path.dirname(python_folder)
        logger.info(f'--------------------python_folder:{python_folder}')
        pathFile = os.path.join(python_folder, 'storage', 'remainder', markImg)
        with open(pathFile, "rb") as img:
            sent_message = await message.answer_photo(
                BufferedInputFile(img.read(), filename="reminder.jpg"),
                caption=str_Msg,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )

        # with open(pathFile, 'rb') as vFile:
        #    sent_message = await bot.send_file(user_entity, vFile, caption=str_Msg, buttons=buttonArr, parse_mode='html')
    elif markAud != "":
        python_folder = os.path.dirname(sys.executable)
        if os.path.basename(python_folder) == 'bin':
            python_folder = os.path.dirname(python_folder)
        logger.info(f'--------------------python_folder:{python_folder}')
        pathFile = os.path.join(python_folder, 'storage', 'remainder', markAud)

        with open(pathFile, 'rb') as mp3:
            sent_message = await message.answer_audio(
                BufferedInputFile(mp3.read(), filename="reminder.mp3"),
                caption=str_Msg,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )

        # with open(pathFile, 'rb') as vFile:
        #    sent_message = await bot.send_file(user_entity, vFile, caption=str_Msg, buttons=buttonArr, parse_mode='html')

    else:
        sent_message = await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        # sent_message = await bot.send_message(user_entity, str_Msg, buttons=buttonArr, parse_mode='html')
    await myF.fSubMsgDel(state, pool, vUserID, message.message_id, sent_message.message_id, bot, 3)
    await state.set_state(myState.common)


# ------------------------------------------------------------------------------------- Команда menu
@r_oth.message(Command("menu"))
async def cmd_menu(message: types.Message, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot
    await state.set_state(myState.common)

    data = await state.get_data()
    menu_command_disabled = data.get('menu_command_disabled', False)

    if menu_command_disabled:
        str_Msg = "Кнопка Menu пока недоступна.\nНеобходимо завершить обучающую историю"
        msg = await message.answer(str_Msg, parse_mode=ParseMode.HTML)
    else:
        vSubscriptionStatus = 2  # всегда активно

        #await myF.fRemoveReplyKB(message_obj=message)  # удаление ReplyKB
        webapp = WebAppInfo(url=config.URL_HELP)
        builder = InlineKeyboardBuilder()
        if vSubscriptionStatus > 0:
            #builder.add(types.InlineKeyboardButton(text=myN.fCSS('learnpath'), callback_data="continue_learn"))
            builder.add(types.InlineKeyboardButton(text=myN.fCSS('story'), callback_data="story"))  # story
            #builder.add(types.InlineKeyboardButton(text=myN.fCSS('daily'), callback_data="daily"))
            builder.add(types.InlineKeyboardButton(text=myN.fCSS('speak'), callback_data="speak"))
            builder.add(types.InlineKeyboardButton(text=myN.fCSS('repeat'), callback_data="words"))
            builder.add(types.InlineKeyboardButton(text=myN.fCSS('newsppr'), callback_data="news_s1_3-0"))
            builder.add(types.InlineKeyboardButton(text=myN.fCSS('native'), callback_data="native"))
            builder.add(types.InlineKeyboardButton(text=myN.fCSS('settings'), callback_data="settings"))  # service
            #builder.add(types.InlineKeyboardButton(text='Help', web_app=webapp))
            #   builder.add(types.InlineKeyboardButton(text=myF.fCSS('donate'), callback_data="donate"))
            builder.adjust(1, 3, 1, )
            #builder.adjust(1, 1, 1, 3, 1, 2)

            str_Msg = "Выберите раздел:"
        else:
            builder.add(types.InlineKeyboardButton(text=myN.fCSS('repeat'), callback_data="words"))
            builder.add(types.InlineKeyboardButton(text=myN.fCSS('settings'), callback_data="settings"))  # service
            builder.adjust(1, 1)
            str_Msg = "Выберите раздел:"
            # f'Ваша подписка неактивна.\n'
            # f'Активировать ее можно в разделе {myF.fCSS("settings")} - {myF.fCSS("prices")}'

        nm_updImg = myF.fImageAddQuote(myF.fGetImg('menu'))
        with open(nm_updImg, "rb") as img:
            msg = await message.answer_photo(BufferedInputFile(img.read(), filename="menu.jpg"), caption=str_Msg,
                                             reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await myF.afDelFile(nm_updImg)
        print('cmd|msg_id - ', msg.message_id)
        await pgDB.fExec_LogQuery(pool_log, message.chat.id, 'menu command')

        await myF.fSubMsgDel(state, pool, vUserID, message.message_id, msg.message_id, bot, 3)


# =================================================================================================================================callbacks
def f_______callbacks__________________():
    pass


# legend for occupied symbols:
#       2 - for voice theme selector
# ---------------------------------------------------------------------------------------------------------------- menu callback
@r_oth.callback_query(F.data == "menu")
async def callback_menu(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    #await state.clear()
    curState = await state.get_state()
    if curState == myState.edu01.state:
        flagEdu = 1
    else:
        flagEdu = 0
        await state.set_state(myState.common)
    print(f'menu|curState = {curState}')

    #await state.update_data(sub_stat=None)      #ajrm

    vSubscriptionStatus = 2  # всегда активно

    #await myF.fRemoveReplyKB(callback_obj=callback)  # удаление ReplyKB
    webapp = WebAppInfo(url=config.URL_HELP)

    builder = InlineKeyboardBuilder()
    if flagEdu == 1:
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('daily'), callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('speak'), callback_data="menu"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('repeat'), callback_data="menu"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('settings'), callback_data="menu"))
        str_Msg = (
            f"Главной страницей бота является меню, из которого можно попасть в любой требуемый раздел\n\n"
            f"<b>Меню состоит из:</b>\n"
            f"<i>{myF.fCSS('daily')}</i> - как следует из названия cодержит список ежедневных заданий\n"
            f"<i>{myF.fCSS('speak')}</i> - основной раздел с разговорными заданиями\n"
            f"<i>{myF.fCSS('repeat')}</i> - задания на изучение слов\n"
            f"<i>{myF.fCSS('settings')}</i> - собственно, настройки\n\n"
            f"<b>Выберите раздел Ежедневные задания...</b>\n"
        )
        '''f"<i>{myF.fCSS('edu')}</i> - при необходимости можно пройти обучение повторно\n"
            f"<i>{myF.fCSS('prices')}</i> - финансовая информация\n"

            f"   💡 <i> обращаем внимание, что меню также доступно из списка команд чата телеграм по кнопке Menu внизу слева</i>\n\n"

            '''

        builder.adjust(1, 1, 1, 1)
    elif vSubscriptionStatus > 0:
        #builder.add(types.InlineKeyboardButton(text=myN.fCSS('learnpath'), callback_data="vB_st2")) #learnpath_start      continue_learn
        builder.add(types.InlineKeyboardButton(text=myN.fCSS('story'), callback_data="story")) #story
        #builder.add(types.InlineKeyboardButton(text=myN.fCSS('daily'), callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text=myN.fCSS('speak'), callback_data="speak"))
        builder.add(types.InlineKeyboardButton(text=myN.fCSS('repeat'), callback_data="words"))
        builder.add(types.InlineKeyboardButton(text=myN.fCSS('newsppr'), callback_data="news_s1_3-0"))
        builder.add(types.InlineKeyboardButton(text=myN.fCSS('native'), callback_data="native"))
        builder.add(types.InlineKeyboardButton(text=myN.fCSS('settings'), callback_data="settings"))  # service
        #builder.add(types.InlineKeyboardButton(text='Help', web_app=webapp))
        #   builder.add(types.InlineKeyboardButton(text=myF.fCSS('donate'), callback_data="donate"))
        builder.adjust(1, 3, 1, 1)
        #builder.adjust(1, 1, 1, 3, 1, 2)

        str_Msg = 'Выберите раздел:'
    else:

        builder.add(types.InlineKeyboardButton(text=myN.fCSS('repeat'), callback_data="words"))
        builder.add(types.InlineKeyboardButton(text=myN.fCSS('settings'), callback_data="settings"))  # service
        builder.adjust(1, 1)
        str_Msg = "Выберите раздел:"
        # f'Ваша подписка неактивна.\n'
        # f'Активировать ее можно в разделе {myF.fCSS("settings")} - {myF.fCSS("prices")}'

    nm_updImg = myF.fImageAddQuote(myF.fGetImg('menu'))
    with open(nm_updImg, "rb") as img:
        msg = await callback.message.answer_photo(BufferedInputFile(img.read(), filename="menu.jpg"), caption=str_Msg,
                                                  reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await myF.afDelFile(nm_updImg)
    print('callbck|msg_id - ', msg.message_id)
    await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

    await pgDB.fExec_LogQuery(pool_log, vUserID, f'menu|{curState}')


@r_oth.callback_query(F.data.startswith('story'))
async def callback_story(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    user_id = callback.message.chat.id
    from .learnpath.handlers.activity import check_user_active_story, show_continue_or_restart_choice, start_story_questionnaire

    if callback.data == 'story':
        existing_story = await check_user_active_story(pool_base, user_id)

        if existing_story:
            await show_continue_or_restart_choice(
                message=callback.message,
                state=state,
                story_id=existing_story['story_id'],
                story_name=existing_story['story_name'],
                scene_name=existing_story['scene_name']
            )
            await state.update_data(task8_existing_story_id=existing_story['story_id'])
        else:
            await show_story_list(callback, state, pool, filter_type='unf', offset=0)

    elif callback.data == 'story_new':
        await state.update_data(task8_actions_count=0)
        await start_story_questionnaire(
            message=callback.message,
            state=state,
            lesson_context=''
        )

    # НОВЫЙ ОБРАБОТЧИК для пагинации и фильтрации
    elif callback.data.startswith('story_list:'):
        # Формат: story_list:filter_type-offset
        # Примеры: story_list:all-0, story_list:unf-6
        params = callback.data.split(':')[1]
        filter_type, offset_str = params.split('-')
        offset = int(offset_str)
        await show_story_list(callback, state, pool, filter_type=filter_type, offset=offset)
        await state.update_data(
            filter_type=filter_type,
            offset=offset
        )

    elif callback.data.startswith('story_st:'):
        story_id = int(callback.data.split(':')[1])
        await handle_story_start(callback, state, pool, story_id)

    elif callback.data.startswith('story_reset_yes:'):
        story_id = int(callback.data.split(':')[1])
        await reset_user_story_progress(pool, user_id, story_id)
        await load_and_show_first_scene(callback.message, state, pool, story_id)

    else:
        await callback.message.answer("Wasn't handled", parse_mode=ParseMode.HTML)





async def handle_story_start(callback, state, pool, story_id, message = None):
    """Обработка запуска конкретной истории"""
    pool_base, pool_log = pool
    if callback:
        message_obj = callback.message
        bot = callback.bot
    else:
        message_obj = message
        bot = message.bot

    # user_id = callback.message.chat.id
    # bot = callback.bot
    user_id = message_obj.chat.id


    # Проверяем существует ли прогресс для этой истории
    check_query = """
        SELECT c_current_scene_id, c_actions_count, c_is_completed
        FROM t_story_user_progress
        WHERE c_user_id = $1 AND c_story_id = $2
    """
    progress = await pgDB.fExec_SelectQuery_args(pool_base, check_query, user_id, story_id)

    if not progress:
        # История не проходилась - создаем прогресс и запускаем
        #await create_story_progress_and_start(callback, state, pool, story_id)


        await load_and_show_first_scene(message_obj, state, pool, story_id)

        #await myF.fSubMsgDel(state, pool, user_id, callback.message.message_id, None, bot, 1)

    else:
        # История уже проходилась - показываем диалог подтверждения
        current_scene = progress[0][0]
        actions_count = progress[0][1]
        is_completed = progress[0][2]

        await show_reset_confirmation(
            callback=callback,
            state=state,
            story_id=story_id,
            current_scene=current_scene,
            actions_count=actions_count,
            is_completed=is_completed,
            pool = pool,
            message = message
        )




async def show_reset_confirmation(callback, state, story_id, current_scene, actions_count, is_completed, pool, message=None):
    """Показать диалог подтверждения сброса прогресса"""
    if callback:
        message_obj = callback.message
        bot = callback.bot
    else:
        message_obj = message
        bot = message.bot

    # user_id = callback.message.chat.id
    user_id = message_obj.chat.id



    user_data = await state.get_data()
    filter_type = user_data.get('filter_type', 'unf')
    offset = user_data.get('offset', '0')
    #offset = user_data['offset']


    if is_completed:
        status_text = "✅ Completed"
    else:
        status_text = f"⏸️ In Progress"

    message_text = f"""
🎭 <b>Story Already Started</b>

Status: {status_text}

Do you want to continue story or reset your progress?
"""

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=myN.fCSS('st_reset'),callback_data=f"story_reset_yes:{story_id}"))
    builder.add(InlineKeyboardButton(text=myN.fCSS('st_cont'), callback_data=f"task8_continue:{story_id}"))
    builder.add(types.InlineKeyboardButton(text=myN.fCSS('back'),callback_data=f"story_list:{filter_type}-{offset}"))
    builder.adjust(1)

    msg = await message_obj.answer(
        message_text,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

    await myF.fSubMsgDel(state, pool, user_id, message_obj.message_id, msg.message_id, bot, 2)


async def reset_user_story_progress(pool, user_id: int, story_id: int):
    pool_base, pool_log = pool

    queries_with_args = [
        ("DELETE FROM t_story_user_progress WHERE c_user_id = $1 AND c_story_id = $2", user_id, story_id),
        ("DELETE FROM t_story_user_stories WHERE c_user_id = $1 AND c_story_id = $2", user_id, story_id),
        ("DELETE FROM t_story_user_interactions WHERE c_user_id = $1 AND c_story_id = $2", user_id, story_id),
        ("DELETE FROM t_story_narrator_hints WHERE c_user_id = $1 AND c_story_id = $2", user_id, story_id),
        ("DELETE FROM t_story_module_history WHERE c_user_id = $1 AND c_story_id = $2", user_id, story_id)
    ]

    try:
        await pgDB.fExec_TransactionQueries(pool_base, queries_with_args)
        logging.info(f"v Successfully reset progress for user {user_id}, story {story_id}")
    except Exception as e:
        logging.error(f"An error occurred while executing delete transaction: {e}")
        logging.error(f"        ---->tables: {tables}")
        logging.error(f"        ---->args: {args}")
        raise


async def show_story_list(callback, state, pool, filter_type='unf', offset=0):
    """
    Показать список историй с пагинацией и фильтрацией

    Args:
        filter_type: 'all' или 'unf' - unfinished
        offset: смещение для пагинации (по 6 историй на страницу)
    """
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    STORIES_PER_PAGE = 6

    # Запрос с учетом фильтра
    if filter_type == 'unf':
        var_query = '''
            SELECT DISTINCT
                s.c_story_id, 
                s.c_story_name, 
                s.c_description,
                COALESCE(p.c_is_completed, false) as is_completed, 
                t3.c_emoji 
            FROM t_story_interactive_stories s
            LEFT JOIN t_story_user_progress p 
                ON s.c_story_id = p.c_story_id 
                AND p.c_user_id = $1
            JOIN t_story_genre t3 ON s.c_genre_id = t3.c_id
            WHERE s.c_is_active = true
                AND (p.c_is_completed = false OR p.c_is_completed IS NULL) AND s.is_prod = true
            ORDER BY s.c_story_id DESC
            LIMIT $2 OFFSET $3
        '''
        var_arr = await pgDB.fExec_SelectQuery_args(
            pool_base, var_query, vUserID, STORIES_PER_PAGE + 1, offset
        )
    else:  # 'all'
        var_query = '''
            SELECT 
                s.c_story_id, 
                s.c_story_name, 
                s.c_description,
                COALESCE(p.c_is_completed, false) as is_completed,
                t3.c_emoji 
            FROM t_story_interactive_stories s
            LEFT JOIN t_story_user_progress p 
                ON s.c_story_id = p.c_story_id 
                AND p.c_user_id = $1
            JOIN t_story_genre t3 ON t3.c_id = s.c_genre_id
            WHERE s.c_is_active = true AND s.is_prod = true
            ORDER BY s.c_story_id DESC
            LIMIT $2 OFFSET $3
        '''
        var_arr = await pgDB.fExec_SelectQuery_args(
            pool_base, var_query, vUserID, STORIES_PER_PAGE + 1, offset
        )

    # Проверяем есть ли следующая страница
    isNext = len(var_arr) > STORIES_PER_PAGE
    if isNext:
        var_arr = var_arr[:STORIES_PER_PAGE]  # Берем только 6 историй

    if var_arr:
        list_msg = ''
        builder = InlineKeyboardBuilder()

        '''
        # Кнопка создания новой истории
        builder.add(types.InlineKeyboardButton(
            text="🆕 New Quest",
            callback_data="story_new"
        ))
        '''

        # Тоггл-кнопка фильтра
        if filter_type == 'all':
            builder.add(types.InlineKeyboardButton(
                text="Unfinished / ✅ All",
                callback_data=f"story_list:unf-0"
            ))
        else:
            builder.add(types.InlineKeyboardButton(
                text="✅ Unfinished / All",
                callback_data=f"story_list:all-0"
            ))

        # Кнопки историй (по 6 штук, в 2 ряда по 3)
        for i, v_story in enumerate(var_arr):
            story_id = v_story[0]
            v_name = v_story[1]
            v_desc = v_story[2]
            is_completed = v_story[3] if len(v_story) > 3 else False
            v_emoji = ''
            if v_story[4]:
                v_emoji = f' {v_story[4]}'

            # Добавляем статус в название
            status_emoji = " ✅" if is_completed else ""  #▸

            button_text = fGetEmodjiNum(i + 1) or f"{i + 1}."
            builder.add(types.InlineKeyboardButton(
                text=button_text,
                callback_data=f"story_st:{story_id}"
            ))

            list_msg = f'{list_msg}{button_text}{status_emoji}{v_emoji} <b>{v_name}</b>\n<i>{v_desc}</i>\n\n'

        # Кнопки навигации (вперед-назад)
        if offset > 0:
            builder.add(types.InlineKeyboardButton(
                text="❰❰",
                callback_data=f"story_list:{filter_type}-{offset - STORIES_PER_PAGE}"
            ))
        if isNext:
            builder.add(types.InlineKeyboardButton(
                text="❱❱",
                callback_data=f"story_list:{filter_type}-{offset + STORIES_PER_PAGE}"
            ))



        # Кнопка меню
        builder.add(types.InlineKeyboardButton(
            text=myN.fCSS('menu'),
            callback_data="menu"
        ))

        # Layout:
        # 1 - New Quest
        # 3, 3 - истории (2 ряда по 3)
        # 1 или 2 - навигация (в зависимости от того, есть ли обе кнопки)
        # 1 - тоггл фильтра
        # 1 - меню
        nav_buttons = (1 if offset > 0 else 0) + (1 if isNext else 0)

        layout = [1]  # Toggle              -New Quest

        # Истории - по 3 в ряд
        stories_count = len(var_arr)
        if stories_count <= 3:
            layout.append(stories_count)
        else:
            layout.extend([3, stories_count - 3])

        # Навигация
        if nav_buttons > 0:
            layout.append(nav_buttons)

        # Фильтр и меню
        #layout.extend([1, 1])
        layout.append(1)        #меню

        builder.adjust(*layout)

        # Заголовок сообщения
        #filter_text = "🔹 Showing: Uncompleted only" if filter_type == 'uncompleted' else "🔹 Showing: All quests"
        page_info = f"Page {offset // STORIES_PER_PAGE + 1}" if offset > 0 or isNext else ""

        str_Msg = (
            f'<u><b>🎭 Available Stories</b></u>\n\n'    #🗡️       {myN.fCSS("story")}
            #f'{filter_text}\n'
            f'{list_msg}'
            f'<i>{page_info}</i>'
        )

        msg = await callback.message.answer(
            str_Msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)
    else:
        # Нет историй для отображения
        no_stories_msg = (
            "📭 No uncompleted quests found.\n\n"
            "Try viewing all quests or create a new one!"
        ) if filter_type == 'unf' else (
            "📭 No quests available yet.\n\n"
            "Create your first quest!"
        )

        builder = InlineKeyboardBuilder()
        #builder.add(types.InlineKeyboardButton(text="🆕 New Quest", callback_data="story_new"))

        if filter_type == 'unf':
            builder.add(types.InlineKeyboardButton(
                text="✅ Show all",
                callback_data="story_list:all-0"
            ))

        builder.add(types.InlineKeyboardButton(text=myN.fCSS('menu'), callback_data="menu"))
        builder.adjust(1)

        msg = await callback.message.answer(
            no_stories_msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)


# chapter----------------------------------------------------------------------------------------------------------------------------------------------- daily callback
@r_oth.callback_query(F.data == "daily")
async def callback_daily(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    curState = await state.get_state()
    if curState == myState.edu01.state:  # Какие новости
        flagEdu = 1
    elif curState == myState.edu02.state:  # monolog
        flagEdu = 2
    elif curState == myState.edu03.state:  # LnR
        flagEdu = 3
    elif curState == myState.edu04.state:  # retell
        flagEdu = 4
    elif curState == myState.edu05.state:  # add 20 words
        flagEdu = 5
    elif curState == myState.edu06.state:  # PickOut words
        flagEdu = 6
    elif curState == myState.edu07.state:  # repeat words
        flagEdu = 7
    else:
        flagEdu = 0
        await state.set_state(myState.daily)
    print(f'daily|curState = {curState}')
    resDict = await f_isDailyDB(callback.message.chat.id, pool_base)
    builder = InlineKeyboardBuilder()
    index = 0
    if flagEdu == 1:
        builder.add(types.InlineKeyboardButton(text='Какие новости? (0/1)', callback_data="d_intro_news"))
        builder.add(types.InlineKeyboardButton(text='Ситуации (0/2)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text='Monologue (0/1)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text='Listen and Repeat (0/7)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text='Retelling (0/2)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text=''.join([myF.fCSS('oxford3'), ' (0/1)']), callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text=''.join([myF.fCSS('PickOut'), ' (0/1)']), callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text=''.join([myF.fCSS('repeat'), ' (0/1)']), callback_data="daily"))
        builder.adjust(1, 1, 1, 1, 1, 1, 1, 1)
        str_Msg = (
            f'Раздел cодержит список ежедневных заданий\n'
            f'После выполнения требуемого количество заданий строка пропадает\n\n'
            f'<b>Выберите пункт "Какие новости?"...</b>'
        )
    elif flagEdu == 2:
        builder.add(types.InlineKeyboardButton(text='Ситуации (0/2)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text='Monologue (0/1)', callback_data="monolog"))
        builder.add(types.InlineKeyboardButton(text='Listen and Repeat (0/7)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text='Retelling (0/2)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text=''.join([myF.fCSS('oxford3'), ' (0/1)']), callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text=''.join([myF.fCSS('PickOut'), ' (0/1)']), callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text=''.join([myF.fCSS('repeat'), ' (0/1)']), callback_data="daily"))
        builder.adjust(1, 1, 1, 1, 1, 1, 1)
        str_Msg = (
            f'Раздел "Ситуации" также является диалогом, в котором тема формируется случайным образом. На нем мы останавливаться не будем\n'
            f'Рассмотрим раздел Монолог\n'
            f'В данном режиме Вы получаете вопрос, на который Вам нужно дать ответ на английском\n\n'
            f'Перейдем к практике\n'
            f'<b>Выберите пункт "Монолог"...</b>'
        )
    elif flagEdu == 3:
        builder.add(types.InlineKeyboardButton(text='Ситуации (0/2)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text='Listen and Repeat (0/7)', callback_data="listen"))
        builder.add(types.InlineKeyboardButton(text='Retelling (0/2)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text=''.join([myF.fCSS('oxford3'), ' (0/1)']), callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text=''.join([myF.fCSS('PickOut'), ' (0/1)']), callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text=''.join([myF.fCSS('repeat'), ' (0/1)']), callback_data="daily"))
        builder.adjust(1, 1, 1, 1, 1, 1)
        str_Msg = (
            f'Следующим идет раздел "Прослушай и повтори"\n'
            f'В данном режиме Вам необходимо повторить как можно ближе к оригиналу услышанную фразу\n'
            f'<b>Выберите пункт "Listen and Repeat"...</b>'
        )
    elif flagEdu == 4:
        builder.add(types.InlineKeyboardButton(text='Ситуации (0/2)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text='Listen and Repeat (1/7)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text='Retelling (0/2)', callback_data="retell"))
        builder.add(types.InlineKeyboardButton(text=''.join([myF.fCSS('oxford3'), ' (0/1)']), callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text=''.join([myF.fCSS('PickOut'), ' (0/1)']), callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text=''.join([myF.fCSS('repeat'), ' (0/1)']), callback_data="daily"))
        builder.adjust(1, 1, 1, 1, 1, 1)
        str_Msg = (
            f'Следующим идет раздел "Пересказ"\n'
            f'В данном режиме Вам необходимо пересказать прочитанный текст\n'
            f'<b>Выберите пункт "Retelling"...</b>'
        )
    elif flagEdu == 5:
        builder.add(types.InlineKeyboardButton(text='Ситуации (0/2)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text='Listen and Repeat (1/7)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text='Retelling (1/2)', callback_data="daily"))
        builder.add(
            types.InlineKeyboardButton(text=''.join([myF.fCSS('oxford3'), ' (0/1)']), callback_data="w_oxford3"))
        builder.add(types.InlineKeyboardButton(text=''.join([myF.fCSS('PickOut'), ' (0/1)']), callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text=''.join([myF.fCSS('repeat'), ' (0/1)']), callback_data="daily"))
        builder.adjust(1, 1, 1, 1, 1, 1)
        str_Msg = (
            f'Бот хранит словарь наиболее употребимых английских слов\n'
            f'Ежедневно Вам предлагается добавить 20 случайных слов для дальнейшего разбора \n'
            f'<b>Выберите пункт "{myF.fCSS("oxford3")}"...</b>'
        )
    elif flagEdu == 6:
        builder.add(types.InlineKeyboardButton(text='Ситуации (0/2)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text='Listen and Repeat (1/7)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text='Retelling (1/2)', callback_data="daily"))
        builder.add(
            types.InlineKeyboardButton(text=''.join([myF.fCSS('PickOut'), ' (0/1)']), callback_data="w_pickout:0"))
        builder.add(types.InlineKeyboardButton(text=''.join([myF.fCSS('repeat'), ' (0/1)']), callback_data="daily"))
        builder.adjust(1, 1, 1, 1, 1)
        str_Msg = (
            f'Далее необходимо перейти в карточки добавленных слов и отметить те слова, которые Вы будете учить\n'
            f'<b>Выберите пункт "{myF.fCSS("PickOut")}"...</b>'
        )
    elif flagEdu == 7:
        builder.add(types.InlineKeyboardButton(text='Ситуации (0/2)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text='Listen and Repeat (1/7)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text='Retelling (1/2)', callback_data="daily"))
        builder.add(types.InlineKeyboardButton(text=''.join([myF.fCSS('repeat'), ' (0/1)']), callback_data="w_repeat"))
        builder.adjust(1, 1, 1, 1)
        str_Msg = (
            f'Изучаемые слова необходимо регулярно повторять \n\n'
            f'<b>Для этого выберите пункт "{myF.fCSS("repeat")}"...</b>'
        )
    else:
        isDaily, limitCnt, limit = f_isDaily('c_dial_news', resDict)
        if isDaily == 1: builder.add(
            types.InlineKeyboardButton(text=''.join(['Какие новости?', ' (', limitCnt, '/', limit, ')']),
                                       callback_data="d_intro_news"));index = index + 1
        isDaily, limitCnt, limit = f_isDaily('c_dial_situation', resDict)
        if isDaily == 1: builder.add(
            types.InlineKeyboardButton(text=''.join(['Ситуации', ' (', limitCnt, '/', limit, ')']),
                                       callback_data="d_intro_situation"));index = index + 1
        isDaily, limitCnt, limit = f_isDaily('c_monolog', resDict)
        if isDaily == 1: builder.add(
            types.InlineKeyboardButton(text=''.join(['Monologue', ' (', limitCnt, '/', limit, ')']),
                                       callback_data="monolog"));index = index + 1
        isDaily, limitCnt, limit = f_isDaily('c_lnr', resDict)
        if isDaily == 1: builder.add(
            types.InlineKeyboardButton(text=''.join(['Listen and Repeat', ' (', limitCnt, '/', limit, ')']),
                                       callback_data="listen"));index = index + 1
        isDaily, limitCnt, limit = f_isDaily('c_retell', resDict)
        if isDaily == 1: builder.add(
            types.InlineKeyboardButton(text=''.join(['Retelling', ' (', limitCnt, '/', limit, ')']),
                                       callback_data="retell"));index = index + 1
        isDaily, limitCnt, limit = f_isDaily('c_oxford3', resDict)
        if isDaily == 1: builder.add(
            types.InlineKeyboardButton(text=''.join([myF.fCSS('oxford3'), ' (', limitCnt, '/', limit, ')']),
                                       callback_data="w_oxford3"));index = index + 1
        isDaily, limitCnt, limit = f_isDaily('c_pick_out', resDict)
        if isDaily == 1: builder.add(
            types.InlineKeyboardButton(text=''.join([myF.fCSS('PickOut'), ' (', limitCnt, '/', limit, ')']),
                                       callback_data="w_pickout:0"));index = index + 1
        isDaily, limitCnt, limit = f_isDaily('c_repeat', resDict)
        if isDaily == 1: builder.add(
            types.InlineKeyboardButton(text=''.join([myF.fCSS('repeat'), ' (', limitCnt, '/', limit, ')']),
                                       callback_data="w_repeat"));index = index + 1
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
        f_BuiderAdjust(index, builder)
        str_Msg = (
            f"Выберите раздел:"
        )
    nm_Img = myF.fGetImg('menu')
    nm_updImg = myF.fImageAddQuote(nm_Img)
    with open(nm_updImg, "rb") as image_In:
        msg = await callback.message.answer_photo(
            BufferedInputFile(image_In.read(), filename="menu.jpg"),
            caption=str_Msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    # myF.fDelFile(nm_updImg)
    await myF.afDelFile(nm_updImg)
    # await callback.message.delete()
    await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

    await pgDB.fExec_LogQuery(pool_log, vUserID, f'|daily|{curState}')


def f________cb______newsppr():
    pass


# chapter----------------------------------------------------------------------------------------------------------------------------------------------- newspaper callback
@r_oth.callback_query(F.data.startswith('news'))
async def callback_newsppr(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    # выбрать статьи из списка
    # -----------------------------------------------------------------------------------
    if callback.data[:8] == 'news_s1_':  # выбор статьи.       news_s1_3-0 news_s1_1-0
        await state.set_state(myState.newstransOn)  # статус перевод включен

        arr_cb_data = callback.data.split('-')
        cb_data = arr_cb_data[0]
        vOffset = int(arr_cb_data[1])
        vLevel = int(cb_data[-1])
        # вытащить названия очередных Х статей из базы
        var_Arr, isNext = await myF.fGetNewsQuery(pool_base, vLevel, vOffset)

        # print('var_Arr - ', var_Arr)
        # сформировать строку со списком статей
        vLen = len(var_Arr)
        if vLevel == 3:
            str_Lvl = '🟢 Original'  #🔵
        elif vLevel == 2:
            str_Lvl = '🟡 Intermediate abridged'
        else:
            str_Lvl = '🔴 Beginner abridged' #🟢
        varStr = ''
        builder = InlineKeyboardBuilder()
        for i, vRec in enumerate(var_Arr):
            vTitle = vRec[0]
            vEmoji = vRec[3]
            vDate = vRec[4]
            vTitle_ru = vRec[5]
            # vDate = vDate.split('-')
            # vDate = f'{vDate[2]}.{vDate[1]}.{vDate[0]}'   #формирование даты
            vSummary = vRec[2]
            # varStr = f'{varStr}{fGetEmodjiNum(i+1)} {vEmoji} <i>{vDate}</i> || <b>{vTitle}</b> || <i>{vTitle_ru}</i>\n<blockquote expandable="true">{vSummary}</blockquote>\n\n'
            varStr = f'{varStr}{fGetEmodjiNum(i + 1)} {vEmoji} <b>{vTitle}</b>\n<blockquote expandable="true">{vSummary}</blockquote>\n\n'
            builder.add(
                types.InlineKeyboardButton(text=f"{fGetEmodjiNum(i + 1)}", callback_data=f"newsppr_st2_{i + 1}"))

        str_Msg = (
            f'<b><u>📚 Выберите статью:</u></b>\n\n'
            f'{varStr}\n'
            f'Выбранный уровень статей - <u>{str_Lvl}</u>'
        )

        logger.info(f'---str_Msg:{str_Msg}')


        # builder.add(types.InlineKeyboardButton(text="2️⃣", callback_data="newsppr_st2_2"))
        # builder.add(types.InlineKeyboardButton(text="3️⃣", callback_data="newsppr_st2_3"))
        # builder.add(types.InlineKeyboardButton(text="4️⃣", callback_data="newsppr_st2_4"))
        if vOffset > 0: builder.add(
            types.InlineKeyboardButton(text="❰❰", callback_data=f"news_s1_{vLevel}-{vOffset - 4}"))
        if isNext: builder.add(
            types.InlineKeyboardButton(text="❱❱", callback_data=f"news_s1_{vLevel}-{vOffset + 4}"))  # if vLen == 4:
        # print('vLen - ', vLen)
        # print('vOffset - ', vOffset)

        if vLevel != 1: builder.add(types.InlineKeyboardButton(text="🔴", callback_data="news_s1_1-0"))
        if vLevel != 2: builder.add(types.InlineKeyboardButton(text="🟡", callback_data="news_s1_2-0"))
        if vLevel != 3: builder.add(types.InlineKeyboardButton(text="🟢", callback_data="news_s1_3-0"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
        # if vLen == 4:
        builder.adjust(vLen, 1 if (vOffset == 0 or not (isNext)) else 2, 2, 1)  # or vLen != 4
        #    elif vLen == 3
        msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)
        await state.update_data(arrNewsTitle=var_Arr)
        await state.update_data(vLevel=vLevel)
        await state.update_data(vOffset=vOffset)

        await pgDB.fExec_LogQuery(pool_log, vUserID, f'newsppr|{callback.data}')
    # чтение статьи
    # -----------------------------------------------------------------------------------
    elif callback.data[:12] == 'newsppr_st2_':  # Первоначальное чтение статьи. По умолчанию перевод включен
        await state.set_state(myState.newstransOn)  # статус перевод включен
        data = await state.get_data()
        vLevel = data['vLevel']  # уровень английского (для возврата назад)
        vOffset = data['vOffset']  # сдвиг списка статей (для возврата назад)
        arrNewsTitle = data['arrNewsTitle']  # хранит ID 4х статей
        vIndex = int(callback.data[-1])  # номер выбранной статьи
        vID = arrNewsTitle[vIndex - 1][1]  # получение ID статьи
        vDate = arrNewsTitle[vIndex - 1][4]  # получение даты статьи
        vTitle_ru = arrNewsTitle[vIndex - 1][5]  # получение названия статьи на русском
        var_query = (
            f"SELECT c_title, c_web, c_text, c_trans, c_word "
            f"FROM t_news "
            f"WHERE c_id = {vID} "
        )
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)  # запрос получения текста статьи
        vTitle = var_Arr[0][0]  # название
        vText = var_Arr[0][2]  # содержание
        vWeb = var_Arr[0][1]  # содержание
        arrText = vText.split('\n')  # преобразование в массив
        vTrans = var_Arr[0][3]  # перевод
        vWord = var_Arr[0][4]  # список слов для изучения
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
        '''
        str_Msg = (
            f'<i>{vDate}</i>\n'
            f'<b>{vTitle}</b>\n'
            f'<i>{vTitle_ru}</i>\n'
            f'<i>{vCnt + 1}/{num}</i>\n'
            f'<b>Оригинал статьи <a href="{vWeb}">здесь</a></b>\n\n'
            f'{str_Msg}\n\n'
            f'<i>{vCnt + 1}/{num}</i>\n'
        )
        '''
        builder = InlineKeyboardBuilder()

        builder.add(types.InlineKeyboardButton(text="❱❱", callback_data="newsppr_st2:mov:fw"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data=f"news_s1_{vLevel}-{vOffset}"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('trs_off'), callback_data="newsppr_st2:TRS:OFF"))

        # проверка БД на наличие word_mark      # отправка слов в рекомендуемые
        # ----------------------------------------
        var_query = (
            f"SELECT c_word_mark "
            f"FROM t_news_user_status "
            f"WHERE c_user_id = '{vUserID}' AND c_news_id = '{vID}'"
        )
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
        print('var_Arr - ', var_Arr)
        IsFlag = not var_Arr or var_Arr[0][0] is None or int(var_Arr[0][0]) != 1
        if IsFlag:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('Add_words'), callback_data='newsppr_st2:words'))
            builder.adjust(1, 2, 1)
            toggleButtonStatus = {'<': 0, '>': 1, 'trs': 0, 'back': 1, 'w': 1}
        else:
            builder.adjust(1, 2)  # 1, 1)
            toggleButtonStatus = {'<': 0, '>': 1, 'trs': 0, 'back': 1, 'w': 0}
        await callback.message.edit_text(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

        if IsFlag:
            # создание word_mark 0 в БД
            var_query = (
                f"INSERT INTO t_news_user_status (c_user_id, c_word_mark, c_news_id, c_date_last_change) "
                f"VALUES ('{vUserID}', '0', '{vID}', CURRENT_TIMESTAMP::timestamp) "
                f"ON CONFLICT (c_user_id, c_news_id) DO UPDATE "
                f"SET c_word_mark = '0', c_date_last_change = CURRENT_TIMESTAMP::timestamp"
            )
            await pgDB.fExec_UpdateQuery(pool_base, var_query)  # сохранение статуса в БД

        await state.update_data(vCnt=vCnt)
        await state.update_data(arrNewsTitle=[])
        await state.update_data(arrText=arrText)
        await state.update_data(arrTrans=arrTrans)
        await state.update_data(arrPages_Txt=arrPages_Txt)
        await state.update_data(arrPages_Trans=arrPages_Trans)
        await state.update_data(subArrText=subArrText)
        await state.update_data(subArrTrans=subArrTrans)

        await state.update_data(num=num)
        await state.update_data(vTitle=vTitle)
        await state.update_data(vTitle_ru=vTitle_ru)
        await state.update_data(vDate=vDate)
        await state.update_data(vWeb=vWeb)
        await state.update_data(vID=vID)
        await state.update_data(vWord=vWord)
        await state.update_data(toggleButtonStatus=toggleButtonStatus)

        await pgDB.fExec_LogQuery(pool_log, vUserID, f'newsppr|{callback.data}')

    elif callback.data[:16] == 'newsppr_st2:TRS:':

        data = await state.get_data()
        arrPages_Txt = data['arrPages_Txt']
        arrPages_Trans = data['arrPages_Trans']
        vLevel = data['vLevel']  # уровень английского (для возврата назад)
        vOffset = data['vOffset']  # сдвиг списка статей (для возврата назад)

        vCnt = int(data['vCnt'])
        if vCnt == 0:
            vTitle_ru = data['vTitle_ru']
            vDate = data['vDate']
            vWeb = data['vWeb']
            vTitle = data['vTitle']
        else:
            vTitle_ru = ''
            vDate = ''
            vWeb = ''
            vTitle = ''

        num = int(data['num'])
        toggleButtonStatus = data['toggleButtonStatus']
        builder = InlineKeyboardBuilder()

        if vCnt != 0:
            builder.add(types.InlineKeyboardButton(text="❰❰", callback_data="newsppr_st2:mov:bc"))
            toggleButtonStatus['<'] = 1
        else:
            toggleButtonStatus['<'] = 0
        if (vCnt + 1) != num:
            builder.add(types.InlineKeyboardButton(text="❱❱", callback_data="newsppr_st2:mov:fw"))
            toggleButtonStatus['>'] = 1
        else:
            toggleButtonStatus['>'] = 0

        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data=f"news_s1_{vLevel}-{vOffset}"))
        toggleButtonStatus['back'] = 1
        if callback.data[-2:] == 'ON':
            await state.set_state(myState.newstransOn)  # статус для отражения отображения перевода
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('trs_off'), callback_data="newsppr_st2:TRS:OFF"))
            toggleButtonStatus['trs'] = 0
        else:
            await state.set_state(myState.newstransOff)  # статус для отражения скрытия перевода
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('trs_on'), callback_data="newsppr_st2:TRS:ON"))
            toggleButtonStatus['trs'] = 1

        # проверка БД на наличие word_mark      # отправка слов в рекомендуемые
        # ----------------------------------------
        vID = data['vID']
        var_query = (
            f"SELECT c_word_mark "
            f"FROM t_news_user_status "
            f"WHERE c_user_id = '{vUserID}' AND c_news_id = '{vID}'"
        )
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
        print('var_Arr - ', var_Arr)
        IsFlag = not var_Arr or var_Arr[0][0] is None or int(var_Arr[0][0]) != 1
        if IsFlag:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('Add_words'), callback_data='newsppr_st2:words'))
            builder.adjust(2 if (vCnt != 0 and (vCnt + 1) != num) else 1, 2, 1)
            toggleButtonStatus['w'] = 1
        else:
            builder.adjust(2 if (vCnt != 0 and (vCnt + 1) != num) else 1, 2)  # 1, 1)
            toggleButtonStatus['w'] = 0

        subArrText = arrPages_Txt[vCnt]
        subArrTrans = arrPages_Trans[vCnt]

        if callback.data[-2:] == 'ON':
            str_Msg = ''
            for i, text in enumerate(subArrText):
                str_Msg = (
                    f'{str_Msg}'
                    f'{text}\n'
                    f'<blockquote expandable="true">{subArrTrans[i]}</blockquote>\n\n'
                )

            str_Msg = myF.fShapeNews1Page(vDate, vTitle, vTitle_ru, vCnt, num, vWeb, str_Msg)

            '''
            str_Msg = (
                f'<b>{vTitle}</b>\n'
                f'<i>{vCnt + 1}/{num}</i>\n'
                f'{str_Web}'
                f'{str_Msg}\n\n'
                f'<i>{vCnt + 1}/{num}</i>\n'
            )
            '''
        else:
            str_Msg = ''
            for text in subArrText:
                str_Msg = f'{str_Msg}{text}\n\n'
            str_Msg = myF.fShapeNews1Page(vDate, vTitle, vTitle_ru, vCnt, num, vWeb, str_Msg)
            '''
            str_Msg = (
                f'<b>{vTitle}</b>\n'
                f'<i>{vCnt + 1}/{num}</i>\n'
                f'{str_Web}'
                f'{str_Msg}\n\n'
                f'<i>{vCnt + 1}/{num}</i>\n'
            )
            '''

        await callback.message.edit_text(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await state.update_data(toggleButtonStatus=toggleButtonStatus)

        await pgDB.fExec_LogQuery(pool_log, vUserID, f'newsppr|{callback.data}')

    elif callback.data[:16] == 'newsppr_st2:mov:':
        curState = await state.get_state()
        data = await state.get_data()

        arrPages_Txt = data['arrPages_Txt']
        arrPages_Trans = data['arrPages_Trans']
        vLevel = data['vLevel']  # уровень английского (для возврата назад)
        vOffset = data['vOffset']  # сдвиг списка статей (для возврата назад)

        toggleButtonStatus = data['toggleButtonStatus']

        vCnt = int(data['vCnt'])

        num = int(data['num'])
        if callback.data[-2:] == 'fw':
            vCnt = vCnt + 1
        else:
            vCnt = vCnt - 1

        if vCnt == 0:
            vTitle_ru = data['vTitle_ru']
            vDate = data['vDate']
            vWeb = data['vWeb']
            vTitle = data['vTitle']
        else:
            vTitle_ru = ''
            vDate = ''
            vWeb = ''
            vTitle = ''
        print('vDate - ', vDate)
        subArrText = arrPages_Txt[vCnt]
        subArrTrans = arrPages_Trans[vCnt]
        print('vCnt = ', vCnt)
        builder = InlineKeyboardBuilder()
        if (vCnt + 1) > 1:
            builder.add(types.InlineKeyboardButton(text="❰❰", callback_data="newsppr_st2:mov:bc"))
            toggleButtonStatus['<'] = 1
        else:
            toggleButtonStatus['<'] = 0
        if (vCnt + 1) != num:
            builder.add(types.InlineKeyboardButton(text="❱❱", callback_data="newsppr_st2:mov:fw"))
            toggleButtonStatus['>'] = 1
        else:
            toggleButtonStatus['>'] = 0

        str_Web = f'<b>Оригинал статьи <a href="{vWeb}">здесь</a></b>\n\n' if vCnt == 0 else ''

        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data=f"news_s1_{vLevel}-{vOffset}"))
        toggleButtonStatus['back'] = 1
        if curState == myState.newstransOff.state:
            str_Msg = ''
            for text in subArrText:
                str_Msg = f'{str_Msg}{text}\n\n'
            str_Msg = myF.fShapeNews1Page(vDate, vTitle, vTitle_ru, vCnt, num, vWeb, str_Msg)
            '''
            str_Msg = (
                f'<b>{vTitle}</b>\n'
                f'<i>{vCnt + 1}/{num}</i>\n'
                f'{str_Web}'
                f'{str_Msg}\n\n'
                f'<i>{vCnt + 1}/{num}</i>\n'
            )
            '''
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('trs_on'), callback_data="newsppr_st2:TRS:ON"))
            toggleButtonStatus['trs'] = 1
        else:
            str_Msg = ''
            for i, text in enumerate(subArrText):
                str_Msg = (
                    f'{str_Msg}'
                    f'{text}\n'
                    f'<blockquote expandable="true">{subArrTrans[i]}</blockquote>\n\n'
                )

            str_Msg = myF.fShapeNews1Page(vDate, vTitle, vTitle_ru, vCnt, num, vWeb, str_Msg)
            '''
            str_Msg = (
                f'<b>{vTitle}</b>\n'
                f'<i>{vCnt + 1}/{num}</i>\n'
                f'{str_Web}'
                f'{str_Msg}\n\n'
                f'<i>{vCnt + 1}/{num}</i>\n'
            )
            '''
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('trs_off'), callback_data="newsppr_st2:TRS:OFF"))
            toggleButtonStatus['trs'] = 0

        # проверка БД на наличие word_mark      # отправка слов в рекомендуемые
        # ----------------------------------------
        vID = data['vID']
        var_query = (
            f"SELECT c_word_mark "
            f"FROM t_news_user_status "
            f"WHERE c_user_id = '{vUserID}' AND c_news_id = '{vID}'"
        )
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
        # print('var_Arr - ', var_Arr)
        IsFlag = not var_Arr or var_Arr[0][0] is None or int(var_Arr[0][0]) != 1
        if IsFlag:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('Add_words'), callback_data='newsppr_st2:words'))
            builder.adjust(2 if ((vCnt + 1) != num and (vCnt > 0)) else 1, 2, 1)
            toggleButtonStatus['w'] = 1
        else:
            builder.adjust(2 if ((vCnt + 1) != num and (vCnt > 0)) else 1, 2)  # 1, 1)
            toggleButtonStatus['w'] = 0

        await callback.message.edit_text(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

        await state.update_data(toggleButtonStatus=toggleButtonStatus)
        await state.update_data(vCnt=vCnt)
        await state.update_data(subArrText=subArrText)
        await state.update_data(subArrTrans=subArrTrans)
        await state.update_data(num=num)

        await pgDB.fExec_LogQuery(pool_log, vUserID, f'newsppr|{callback.data}')

    elif callback.data[:17] == 'newsppr_st2:words':  # отправка слов в рекомендуемые
        print('newsppr_st2:words')
        data = await state.get_data()
        vWord = data['vWord']
        vLevel = data['vLevel']  # уровень английского (для возврата назад)
        vOffset = data['vOffset']  # сдвиг списка статей (для возврата назад)
        vID = data['vID']
        toggleButtonStatus = data['toggleButtonStatus']

        word_mark = 1
        await state.update_data(word_mark=word_mark)  # сохранение статуса в redis
        var_query = (
            f"INSERT INTO t_news_user_status (c_user_id, c_word_mark, c_news_id, c_date_last_change) "
            f"VALUES ('{vUserID}', '1', '{vID}', CURRENT_TIMESTAMP::timestamp) "
            f"ON CONFLICT (c_user_id, c_news_id) DO UPDATE "
            f"SET c_word_mark = '1', c_date_last_change = CURRENT_TIMESTAMP::timestamp"
        )
        await pgDB.fExec_UpdateQuery(pool_base, var_query)  # сохранение статуса в БД

        obj_ids = vWord.split(':')  # Split the input text into a list of obj_id values
        values_list = ", ".join(
            f"({obj_id}, ('{vUserID}' || {obj_id})::bigint, '{vUserID}', '1')" for obj_id in obj_ids
        )

        var_query = (
            f"INSERT INTO tw_userprogress (obj_id, userobj_id, user_id, status_id)  "
            f"VALUES {values_list} "
            f"ON CONFLICT (userobj_id) DO NOTHING"
        )
        await pgDB.fExec_UpdateQuery(pool_base, var_query)

        builder = InlineKeyboardBuilder()
        if toggleButtonStatus['<'] == 1: builder.add(
            types.InlineKeyboardButton(text="❰❰", callback_data="newsppr_st2:mov:bc"))
        if toggleButtonStatus['>'] == 1: builder.add(
            types.InlineKeyboardButton(text="❱❱", callback_data="newsppr_st2:mov:fw"))

        if toggleButtonStatus['back'] == 1: builder.add(
            types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data=f"news_s1_{vLevel}-{vOffset}"))

        if toggleButtonStatus['trs'] == 1:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('trs_on'), callback_data="newsppr_st2:TRS:ON"))
        else:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('trs_off'), callback_data="newsppr_st2:TRS:OFF"))

        builder.adjust(2 if (toggleButtonStatus['<'] == 1 and toggleButtonStatus['>'] == 1) else 1, 2)
        toggleButtonStatus['w'] = 0

        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
        await callback.answer("Слова добавлены в рекомендуемые!")
        await state.update_data(toggleButtonStatus=toggleButtonStatus)

        await pgDB.fExec_LogQuery(pool_log, vUserID, f'newsppr|{callback.data}')

        '''
    ①   ②   ③   ④   ⑤   ⑥

'''


#
def f________cb______words():
    pass


# chapter---------------------------------------------------------------------------------------------------------------------------------------- words callback
@r_oth.callback_query(F.data == "words")
async def callback_Words(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    sw_timer = myF.SWTimer()  # start
    vLangCode = callback.message.from_user.language_code

    sw_timer(f'1 - {vLangCode} - ')  # stopwatch
    sw_timer.close()  # del

    await state.set_state(myState.words)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=myF.fCSS("PickOut"), callback_data="w_pickout:0"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('Rep_words'), callback_data="w_repeat"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('oxford3'), callback_data="w_oxford3"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('wordlist'), callback_data="w_list"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('bas'), callback_data="w_bas"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
    builder.adjust(1, 1, 1, 1, 1)
    str_Msg = "Выберите раздел:"

    # msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    with open(myF.fGetImg('word'), "rb") as image_In:
        msg = await callback.message.answer_photo(
            BufferedInputFile(image_In.read(), filename="word.jpg"),
            caption=str_Msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    # await callback.message.delete()
    await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)
    # await callback.message.edit_text("Выберите раздел:", reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


# ---------------------------------------------------------------------     build-a-sentence callback
@r_oth.callback_query(F.data == "w_bas")
async def callback_w_bas(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    vLangCode = callback.message.from_user.language_code

    # get 4 words
    v_words = await myF.fGetLearnWords(vUserID, pool_base, 4)
    str_Msg = (
        f"{myF.fCSS('bas')}\n\n"
        f'Придумайте предложение или короткую историю из 4х изучаемых слов:\n'
        f'<b>{v_words}</b>\n\n'
        f'P.S. запишите голосовое или введите с клавиатуры текстом'
    )
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="words"))

    # send a message
    msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)
    await state.update_data(bas_words=v_words)


# ----------------------------------------------------------------- build-a-sentence media
@r_oth.message((F.voice | F.text), StateFilter(myState.words))
async def media_w_bas(message: types.Message, bot: Bot, state: FSMContext, pool, dp):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot
    vLangCode = message.from_user.language_code
    nlp_tools = dp.workflow_data["nlp_tools"]
    # user_entity = await bot.get_entity(vUserID)
    # vLangCode = user_entity.lang_code

    data = await state.get_data()
    bas_words = data['bas_words']

    # скопировать из войс получение и обработку звука
    # +++++++++++++++++отправка и получение голосового сообщения ChatGPT++++++++++++++++++++++++++++
    # -------------------processing both voice and text
    strUserVoice = ''
    if message.voice != None:  # voice
        # ---------------------------------------перевод user voice -> text
        strUserVoice = await myF.afVoiceToTxt(message, pool, vUserID)  # транскрипция голоса в текст    , bot
    elif message.text != None:
        #strUserVoice = message.text
        strUserVoice = ' '.join(message.text.split())

    if strUserVoice:
        # strUserVoice = myF.fRemoveLastBadSymbol(strUserVoice)
        vStr = myF.fCheckWords_BAS(strUserVoice, bas_words, nlp_tools.nlp)

        # str_Msg = vStr

        # -----------------------проверка грамматики и формирование тоггла для списка ошибка
        str_Msg, index_rule_pairs, var_ImprovedLine = await myF.fGrammarCheck_txt(
            nlp_tools.tool, strUserVoice, pool, vUserID
        )

        str_Msg = f'{vStr}\n\n{str_Msg}'

        # Generate toggleButtonStatus dictionary dynamically
        toggleButtonStatus = {str(emoji_index): 0 for emoji_index, _ in index_rule_pairs}
        builder = await myF.fSetGrammarBuilder(toggleButtonStatus, index_rule_pairs, state)
        await state.update_data(str_Msg=str_Msg)  # сохранение для вкладок грамматики
        await state.update_data(index_rule_pairs=index_rule_pairs)  # сохранение для вкладок грамматики
        await state.update_data(toggleButtonStatus=toggleButtonStatus)  # сохранение для вкладок грамматики

        # builder = InlineKeyboardBuilder()
        # builder.add(types.InlineKeyboardButton(text=myF.fCSS('bas'), callback_data="w_bas"))
        # builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="words"))
        # builder.adjust(1, 1)

    else:
        str_Msg = (
            f"Something went wrong\n"
            f"We are working on it..."
        )
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))

    msg = await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await myF.fSubMsgDel(state, pool, vUserID, message.message_id, msg.message_id, bot, 3)

    # await message.delete()
    await state.update_data(bas_words='')
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"BaS|{strUserVoice}")


# ----------------------------------------------------------------------------------------------------- список изучаемых слов
@r_oth.callback_query(F.data.startswith("w_list"))
async def callback_w_list(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    curState = await state.get_state()
    await state.set_state(myState.words)
    if callback.data == 'w_list':
        var_query = (
            f"SELECT t1.obj_id, t2.obj_eng, t2.obj_ipa, t2.obj_rus, t2.obj_rus_alt, t2.obj_desc1, t2.c_exa_ruen, t2.c_origin, t2.c_dict "
            f"FROM tw_userprogress as t1 LEFT JOIN tw_obj as t2 ON t1.obj_id = t2.obj_id "
            f"WHERE t1.user_id = '{vUserID}' AND t1.status_id > 1 AND t1.status_id < 8"
        )
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
        var_NoWords = 0
        if var_Arr is not None:
            arr_Len = len(var_Arr)
            if arr_Len > 0:
                gp_Cnt = 0

                varStr = fGetMsgFromWordArr(gp_Cnt, var_Arr)

                builder = InlineKeyboardBuilder()
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('<<'), callback_data="w_list_back"))
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('>>'), callback_data="w_list_fw"))
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="words"))
                builder.adjust(2, 1)

                await callback.message.answer(varStr, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
                await callback.message.delete()
                await state.update_data(wordArr=var_Arr)
                await state.update_data(wordCounter=gp_Cnt)
            else:
                var_NoWords = 1
        else:
            var_NoWords = 1
        if var_NoWords == 1:
            varStr = 'Нет изучаемых слов'
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="words"))
            await callback.message.answer(varStr, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
            await callback.message.delete()

        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|w_list|w_list|{curState}')
    elif callback.data == 'w_list_back':
        data = await state.get_data()
        gp_Cnt = data['wordCounter']
        var_Arr = data['wordArr']
        arr_Len = len(var_Arr)
        gp_Cnt = gp_Cnt - 1
        if gp_Cnt < 0: gp_Cnt = arr_Len - 1
        # print(gp_Cnt)
        varStr = fGetMsgFromWordArr(gp_Cnt, var_Arr)
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('<<'), callback_data="w_list_back"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('>>'), callback_data="w_list_fw"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="words"))
        builder.adjust(2, 1)

        await callback.message.edit_text(varStr, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        # await callback.message.delete()
        await state.update_data(wordArr=var_Arr)
        await state.update_data(wordCounter=gp_Cnt)
    elif callback.data == 'w_list_fw':
        data = await state.get_data()
        gp_Cnt = data['wordCounter']
        var_Arr = data['wordArr']
        arr_Len = len(var_Arr)
        gp_Cnt = gp_Cnt + 1
        if gp_Cnt == arr_Len: gp_Cnt = 0
        # print(gp_Cnt)
        varStr = fGetMsgFromWordArr(gp_Cnt, var_Arr)
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('<<'), callback_data="w_list_back"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('>>'), callback_data="w_list_fw"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="words"))
        builder.adjust(2, 1)

        await callback.message.edit_text(varStr, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        # await callback.message.delete()
        await state.update_data(wordArr=var_Arr)
        await state.update_data(wordCounter=gp_Cnt)


# ----------------------------------------------------------------------------------------------------------------------------- Разобрать новые слова
@r_oth.callback_query(F.data.startswith("w_pickout"))
async def callback_w_pickout(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    vX = 9

    curState = await state.get_state()
    if curState == myState.edu06.state:
        flagEdu = 6
    else:
        flagEdu = 0
        await state.set_state(myState.words)
    # print(f'w_pickout|curState = {curState}')

    if callback.data.startswith(
            'w_pickout:'):  # возможно фильтр пересмотреть, чтобы он остался один и сам на себя ссылался w_pickout:0 - первый, w_pickout:1 - последующие
        vIndex = int(callback.data.split(':')[1])
        # print('vIndex - ', vIndex)
        # первоначальное определение переменных для последующих циклов
        # ------------------------------------------------------------------------------
        if vIndex == 0:
            var_query = (
                f"SELECT t1.obj_id, obj_eng, obj_ipa, obj_rus, obj_rus_alt "
                f"FROM tw_userprogress as t1 LEFT JOIN tw_obj as t2 ON t1.obj_id = t2.obj_id "
                f"WHERE user_id = '{vUserID}' AND status_id = '1'"
            )
            arrWordListFull = await pgDB.fExec_SelectQuery(pool_base, var_query)  # выгрузка всего пула слов
            toggle = {'1': "0", '2': "0", '3': "0", '4': "0", '5': '0', '6': '0', '7': '0', '8': '0',
                      '9': '0'}  # toggle init
        # обработка toggle и запись слов к известным и изучаемым
        # ------------------------------------------------------------------------------
        else:
            data = await state.get_data()
            arrWordListFull = data['arrWordListFull']
            toggle = data['toggle']
            arrWordListX = data['arrWordListX']
            vLen = len(arrWordListX)

            #       1 - status =2, 0 - status = 9
            # разобрать toggle, сформировать массивы id слов для запросов на добавление и исключение
            arrAdd2Learn = []
            arrAdd2Known = []
            for key, value in toggle.items():
                print('key - ', key, '  |value - ', value)
                if int(key) <= vLen:
                    obj_id = arrWordListX[int(key) - 1][0]
                    if value == '1':
                        arrAdd2Learn.append(obj_id)  # добавление obj_id слова
                        print('     arrAdd2Learn - ', arrAdd2Learn)
                    else:
                        arrAdd2Known.append(obj_id)  # добавление obj_id слова
                        print('     arrAdd2Known - ', arrAdd2Known)
            # формирование запроса на добавление слов к изучению     arrAdd2Learn
            if arrAdd2Learn:
                str_obj_id = ", ".join(map(str, arrAdd2Learn))
                print('str_obj_id - ', str_obj_id)
                var_query = (
                    f"UPDATE tw_userprogress "
                    f"SET status_id = 2, date_last_change = CURRENT_TIMESTAMP::timestamp, date_repeat = CURRENT_DATE "
                    f"WHERE obj_id IN ({str_obj_id}) AND user_id = '{vUserID}'"
                )
                print('var_query - ', var_query)
                await pgDB.fExec_UpdateQuery(pool_base, var_query)

            # формирование запроса на исключение слов в известные     arrAdd2Known
            if arrAdd2Known:
                str_obj_id = ", ".join(map(str, arrAdd2Known))
                print('str_obj_id - ', str_obj_id)
                var_query = (
                    f"UPDATE tw_userprogress "
                    f"SET status_id = 9, date_last_change = NULL, date_repeat = NULL "
                    f"WHERE obj_id IN ({str_obj_id}) AND user_id = '{vUserID}'"
                )
                print('var_query - ', var_query)
                await pgDB.fExec_UpdateQuery(pool_base, var_query)
            toggle = {'1': "0", '2': "0", '3': "0", '4': "0", '5': '0', '6': '0', '7': '0', '8': '0',
                      '9': '0'}  # toggle init

        # ------------------------------------------------------------------------------

        var_NoWords = 0  # флаг отсутсвия слов к изучению
        if arrWordListFull is not None:
            arr_Len = len(arrWordListFull)
            print('arr_Len - ', arr_Len)
            if arr_Len > 0:
                arrWordListX = arrWordListFull[:vX]  # выделение субмассива для тоггла
                arrWordListFull = arrWordListFull[vX:]  # отрезание субмассива из основного массива
                print('arrWordListX - ', arrWordListX)
                # gp_Cnt = 0     ????
                vLenFull = len(arrWordListFull)

                vLen = len(arrWordListX)
                builder = InlineKeyboardBuilder()
                varStr = ''
                for i, vWord in enumerate(arrWordListX):
                    strAlt = f' (<i>{vWord[4]}</i>)' if vWord[
                        4] else ''  # формирование строки альтенативных переводов для вывода
                    strTranscr = f'[{vWord[2]}] - ' if vWord[2] else ''  # формирование строки транкрипции
                    varStr = f'{varStr}{fGetEmodjiNum(i + 1)} <b>{vWord[1]}</b> - {strTranscr}{vWord[3]}{strAlt}\n\n'  # выходная строка по слову
                    builder.add(types.InlineKeyboardButton(text=f'{fGetEmodjiNum(i + 1)}',
                                                           callback_data=f"w_pickout_t:{i + 1}"))  # кнопка под строку
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="words"))
                builder.add(types.InlineKeyboardButton(text="Submit", callback_data="w_pickout:1"))

                vOut = vLen % 3 or 3  # расчет остатка
                args = [3] * (vLen // 3) + [vOut, 2]  # формирование списка args
                builder.adjust(*args)  # формирование builder

                varStr = (
                    f'<b>Выберите слова, которые необходимо добавить к изучению:</b>\n\n'
                    f'<i>{vLen} / {arr_Len}</i>\n\n'
                    f'{varStr}'
                )
                # builder.add(types.InlineKeyboardButton(text="❌ Не учим", callback_data="w_pickout_no"))
                # if flagEdu == 6:
                #    builder.adjust(2)
                # else:
                #    builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
                #    builder.adjust(2, 1)

                await callback.message.answer(varStr, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
                await callback.message.delete()
                await state.update_data(arrWordListFull=arrWordListFull)
                await state.update_data(arrWordListX=arrWordListX)
                await state.update_data(toggle=toggle)

                await state.update_data(wordArr=arrWordListFull)

                # await state.update_data(wordCounter=gp_Cnt)
            else:
                var_NoWords = 1
                print('if arr_Len > 0:')
        else:
            var_NoWords = 1
            print('if arrWordListFull is not None:')
        if var_NoWords == 1:
            varStr = 'Нет новых слов'
            builder = InlineKeyboardBuilder()
            if flagEdu == 6:
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="daily"))
            else:
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="words"))

            await callback.message.answer(varStr, reply_markup=builder.as_markup(),
                                          parse_mode=ParseMode.HTML)
            await callback.message.delete()
            await myF.f_setDaily('c_pick_out', callback.message.chat.id, pool_base)
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|w_pickout|w_pickout|{curState}')
    # toggle
    # --------------------------------------------------------------------------------------------------------
    if callback.data.startswith('w_pickout_t:'):
        data = await state.get_data()
        arrWordListX = data['arrWordListX']
        vLen = len(arrWordListX)
        toggle = data['toggle']

        vIndex = callback.data.split(':')[1]
        toggle[str(vIndex)] = "1" if toggle.get(
            vIndex) == "0" else "0"  # переопределение/переключение значения элемента

        builder = InlineKeyboardBuilder()
        for i in range(1, vLen + 1, 1):
            label = f"{fGetEmodjiNum(i)} {'✅' if toggle.get(str(i)) == '1' else ''}"

            builder.button(text=label, callback_data=f"w_pickout_t:{i}")
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="words"))
        builder.add(types.InlineKeyboardButton(text="Submit", callback_data="w_pickout:1"))

        vOut = vLen % 3 or 3  # расчет остатка
        args = [3] * (vLen // 3) + [vOut, 2]  # формирование списка args
        builder.adjust(*args)  # формирование builder

        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
        await callback.answer("Option updated!")

        await state.update_data(toggle=toggle)


# ----------------------------------------------------------------------------------------------------------------------------- Повторить слова
@r_oth.callback_query(F.data.startswith("w_repeat"))
async def callback_w_repeat(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    curState = await state.get_state()
    if curState == myState.edu07.state:
        flagEdu = 7
    else:
        flagEdu = 0
        await state.set_state(myState.words)
    print(f'w_repeat|curState = {curState}')
    v_userID = callback.message.chat.id

    if callback.data == 'w_repeat':
        # 1.1 выбор слов к изучению
        # 1.2 под каждое слово формируется выборка из той же таблицы с 4 словами на выбор
        #   формат сообщения:
        #       в шапке русское слово
        #       в вариантах - английские
        #   пользователь выбирает слово
        # 1.3 по результатам:
        #   верно - нужно увеличит на 1 статус изучения слова и записать update в бд, если статус = 8, то репитдата обнуляется
        #   в случае "неверно" обратно в субд ничего не записывается, а в массив review_records в конец записывает текущее значение
        # 1.1

        if flagEdu == 7:  # добавление 3х слов к изучению

            var_query = (
                f"INSERT INTO tw_userprogress (obj_id, user_id, status_id, date_last_change, date_repeat, userobj_id) "
                f"VALUES "
                f"  ('233', '{v_userID}', 2, CURRENT_TIMESTAMP::timestamp, CURRENT_DATE, ('{v_userID}' || '233')::bigint), "
                f"  ('934', '{v_userID}', 2, CURRENT_TIMESTAMP::timestamp, CURRENT_DATE, ('{v_userID}' || '934')::bigint), "
                f"  ('1482', '{v_userID}', 2, CURRENT_TIMESTAMP::timestamp, CURRENT_DATE, ('{v_userID}' || '1482')::bigint) "
                f"ON CONFLICT (userobj_id) DO NOTHING"
            )
            await pgDB.fExec_UpdateQuery(pool_base, var_query)

        var_query = (
            f"SELECT t1.user_id, t1.obj_id, status_id, obj_eng, obj_rus, obj_ipa, obj_desc1, c_exa_ruen, c_origin, c_dict  "
            f"FROM tw_userprogress AS t1 LEFT JOIN tw_obj AS t2 ON t1.obj_id = t2.obj_id "
            f"WHERE t1.user_id = '{callback.message.chat.id}' AND t1.date_repeat <= CURRENT_DATE "
            f"  AND status_id > 1"
        )
        # cast(strftime('%Y%m%d', date_repeat) AS INTEGER) <= cast(strftime('%Y%m%d', 'now', 'localtime') AS INTEGER)

        # connection = create_connection(db_name)
        arr_Repeat = await pgDB.fExec_SelectQuery(pool_base, var_query)  # execute_query(connection, var_query)
        # print('arr_Repeat = ', arr_Repeat)
        var_len = len(arr_Repeat)
        if var_len > 0:
            var_Cnt = 0
            arr_Choice = await myF.fArrChoiceGen(arr_Repeat, var_Cnt, pool_base)
            # print('arr_Choice = ', arr_Choice)
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=arr_Choice[0], callback_data="w_repeat_0"))
            builder.add(types.InlineKeyboardButton(text=arr_Choice[1], callback_data="w_repeat_1"))
            builder.add(types.InlineKeyboardButton(text=arr_Choice[2], callback_data="w_repeat_2"))
            builder.add(types.InlineKeyboardButton(text=arr_Choice[3], callback_data="w_repeat_3"))
            builder.adjust(2, 2)
            str_Msg = (
                f"<i>{var_Cnt + 1} из {var_len}</i>\n"
                f"❓ {arr_Repeat[var_Cnt][4]}"
            )
            await callback.message.answer(str_Msg, reply_markup=builder.as_markup(),
                                          parse_mode=ParseMode.HTML)
            await callback.message.delete()
            await state.update_data(wordChoiceArr=arr_Choice)
            await state.update_data(wordCounter=var_Cnt)
            await state.update_data(wordArr=arr_Repeat)
        else:
            builder = InlineKeyboardBuilder()
            if flagEdu == 7:
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'),
                                                       callback_data="edu_xx"))  # окончание блока edu05  //ранее price01
                # await state.set_state(myState.edu08)
            else:
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="words"))
            await callback.message.answer("Сейчас нет слов к повтору", reply_markup=builder.as_markup(),
                                          parse_mode=ParseMode.HTML)
            await callback.message.delete()
            await state.update_data(wordChoiceArr=[])
            await state.update_data(wordCounter=0)
            await state.update_data(wordArr=[])
            await myF.f_setDaily('c_repeat', callback.message.chat.id, pool_base)
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|w_repeat|w_repeat|{curState}')
    if callback.data[:9] == 'w_repeat_':
        data = await state.get_data()
        arr_Repeat = data['wordArr']
        arr_Choice = data['wordChoiceArr']
        gp_Cnt = data['wordCounter']
        # print('arr_Repeat - ', arr_Repeat)
        # gp_Cnt = gp_Cnt+1
        # print('callback.data = ', callback.data, '  gp_Cnt = ', gp_Cnt)
        # --------в случае "верно" нужно увеличит на 1 статус изучения слова и записаться в бд
        # если статус = 8, то репитдата обнуляется
        # print('arr_Repeat[gp_Cnt][3]', arr_Repeat[gp_Cnt][3], ' arr_Choice[int(callback.data[-1])] = ', arr_Choice[int(callback.data[-1])])
        # ------------------------------------------------------------------------------------------------
        # формирование карточки слова
        vStr = myF.fShapeWordCard(
            arr_Repeat[gp_Cnt][3], arr_Repeat[gp_Cnt][4],
            arr_Repeat[gp_Cnt][5], arr_Repeat[gp_Cnt][7],
            arr_Repeat[gp_Cnt][8], arr_Repeat[gp_Cnt][9]
        )  # arr_Repeat[gp_Cnt][7],
        strWordCard = (
            f"\n<u>Карточка слова:</u>\n"
            f"{vStr}"
        )
        '''
        lemma = arr_Repeat[gp_Cnt][3]
        strIPA = arr_Repeat[gp_Cnt][5]
        transcription_str = f"      <code>[{strIPA}] </code>\n" if strIPA else ""

        v_Rus = arr_Repeat[gp_Cnt][4]
        v_Alt = f'(<i>{arr_Repeat[gp_Cnt][7]}</i>)' if arr_Repeat[gp_Cnt][7] else ''
        vWordCard = arr_Repeat[gp_Cnt][6] or ''
        strWordCard = (
            f"\n<u>Карточка слова:</u>\n"
            f"📖 <b>{lemma}</b> \n"
            f"{transcription_str}"
            f"      {v_Rus} {v_Alt}\n\n"
            f"{vWordCard}"
        )
        '''

        if arr_Repeat[gp_Cnt][3] == arr_Choice[int(callback.data[-1])]:
            varStr = (
                f"✅ Верно! \n"
                f"{strWordCard}"
            )

            # v_datetime = str(datetime.now())
            # v_today = date.today()
            v_dateRepeat = myF.getDateRepeatShift(arr_Repeat[gp_Cnt][2])
            v_obj_id = arr_Repeat[gp_Cnt][1]
            v_status_id = arr_Repeat[gp_Cnt][2] + 1
            if v_status_id == 8:
                v_dateRepeat = 'NULL'
            var_query = (
                f"UPDATE tw_userprogress "
                f"SET status_id = '{v_status_id}', date_last_change = CURRENT_TIMESTAMP::timestamp, date_repeat = {v_dateRepeat} "
                f"WHERE obj_id = '{v_obj_id}' AND user_id = '{vUserID}'"
            )

            await pgDB.fExec_UpdateQuery(pool_base, var_query)
        # --------в случае "неверно" обратно в субд ничего не записывается, а в массив review_records в конец записывает текущее значение
        else:
            varStr = (
                f"❌ Неверно! \n"
                f"{strWordCard}"
            )

            arr_Repeat.append(arr_Repeat[gp_Cnt])
        builder = InlineKeyboardBuilder()
        if flagEdu == 7:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('>>'), callback_data="w_repeatNext"))
        else:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="words"))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('>>'), callback_data="w_repeatNext"))
            builder.add(types.InlineKeyboardButton(text="🗑 Убрать из повтора", callback_data="w_repeatExcl"))
            builder.adjust(2, 1)
        await callback.message.edit_text(varStr, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await state.update_data(wordChoiceArr=[])
        await state.update_data(wordCounter=gp_Cnt)
        await state.update_data(wordArr=arr_Repeat)
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|w_repeat|w_repeat_|{curState}')
    if callback.data == 'w_repeatNext':
        data = await state.get_data()
        arr_Repeat = data['wordArr']
        # arr_Choice = data['wordChoiceArr']
        gp_Cnt = data['wordCounter']
        gp_Cnt = gp_Cnt + 1
        var_len = len(arr_Repeat)
        # print('callback.data = ', callback.data, '  gp_Cnt = ', gp_Cnt)
        if (gp_Cnt < len(arr_Repeat) and flagEdu == 0) or (
                gp_Cnt <= 2 and flagEdu == 7):  # ограничение на 3 слова повторе во время обучения
            arr_Choice = await myF.fArrChoiceGen(arr_Repeat, gp_Cnt, pool_base)
            # print('arr_Choice = ', arr_Choice)
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=arr_Choice[0], callback_data="w_repeat_0"))
            builder.add(types.InlineKeyboardButton(text=arr_Choice[1], callback_data="w_repeat_1"))
            builder.add(types.InlineKeyboardButton(text=arr_Choice[2], callback_data="w_repeat_2"))
            builder.add(types.InlineKeyboardButton(text=arr_Choice[3], callback_data="w_repeat_3"))
            builder.adjust(2, 2)
            str_Msg = (
                f"<i>{gp_Cnt + 1} из {var_len}</i>\n"
                f"❓ {arr_Repeat[gp_Cnt][4]}"
            )
            await callback.message.edit_text(str_Msg, reply_markup=builder.as_markup(),
                                             parse_mode=ParseMode.HTML)
            await state.update_data(wordChoiceArr=arr_Choice)
            await state.update_data(wordCounter=gp_Cnt)
            await state.update_data(wordArr=arr_Repeat)
        else:
            varEmoji = myF.getRandomEmoji('wd')
            builder = InlineKeyboardBuilder()
            if flagEdu == 7:
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'),
                                                       callback_data="edu_xx"))  # окончание блока edu05  //ранее price01
                # await state.set_state(myState.edu08)
                varStr = varEmoji + 'Отлично! Пока достаточно, двигаемся дальше'
                # удаление 3х слов из обучения
                var_query = (
                    f"UPDATE tw_userprogress "
                    f"SET status_id = '9', date_last_change = NULL, date_repeat = NULL "
                    f"WHERE obj_id in ('233', '934', '1482') AND user_id = '{v_userID}'"
                )
                # connection = create_connection(db_name)
                # execute_insert_query(connection, var_query)
                await pgDB.fExec_UpdateQuery(pool_base, var_query)
            else:
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="words"))
                varStr = varEmoji + 'Отлично! Все повторили'

            await callback.message.edit_text(varStr, reply_markup=builder.as_markup(),
                                             parse_mode=ParseMode.HTML)
            await state.update_data(wordChoiceArr=[])
            await state.update_data(wordCounter=0)
            await state.update_data(wordArr=[])
            await myF.f_setDaily('c_repeat', callback.message.chat.id, pool_base)
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|w_repeat|w_repeatNext|{curState}')
    if callback.data == 'w_repeatExcl':
        data = await state.get_data()
        arr_Repeat = data['wordArr']
        # arr_Choice = data['wordChoiceArr']
        gp_Cnt = data['wordCounter']
        v_obj_id = arr_Repeat[gp_Cnt][1]
        v_userID = callback.message.chat.id
        var_query = (
            f"UPDATE tw_userProgress "
            f"SET status_id = '9', date_last_change = NULL, date_repeat = NULL "
            f"WHERE obj_id = '{v_obj_id}' AND user_id = '{v_userID}'"
        )
        # connection = create_connection(db_name)
        # execute_insert_query(connection, var_query)
        await pgDB.fExec_UpdateQuery(pool_base, var_query)
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="words"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('>>'), callback_data="w_repeatNext"))

        builder.adjust(2)
        await callback.message.edit_text("Исключено из повтора", reply_markup=builder.as_markup(),
                                         parse_mode=ParseMode.HTML)
        await state.update_data(wordChoiceArr=[])
        await state.update_data(wordCounter=gp_Cnt)
        await state.update_data(wordArr=arr_Repeat)
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|w_repeat|w_repeatExcl|{curState}')


# ---------------------------------------------------------------------------------------------- Добавить слова Oxford 3000
@r_oth.callback_query(F.data == "w_oxford3")
async def callback_w_oxford3(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    curState = await state.get_state()
    if curState == myState.edu05.state:
        flagEdu = 5
    else:
        flagEdu = 0
        await state.set_state(myState.words)
    print(f'oxford3|curState = {curState}')

    # формирование
    var_query = (
        f"INSERT INTO tw_userprogress (obj_id, user_id, status_id, userobj_id) "
        f"SELECT t1.obj_id, '{callback.message.chat.id}', 1, ('{callback.message.chat.id}' || t1.obj_id)::bigint "
        f"FROM tw_obj as t1 LEFT JOIN tw_userprogress as t2 ON t1.obj_id = t2.obj_id "
        f"WHERE (t2.user_id != '{callback.message.chat.id}' OR t2.user_id IS NULL) AND t1.theme_id = 3 "
        f"ORDER BY RANDOM() "
        f"LIMIT 20 "
        f"ON CONFLICT (userobj_id) DO NOTHING"
    )
    # connection = create_connection(db_name)
    # execute_insert_query(connection, var_query)
    await pgDB.fExec_UpdateQuery(pool_base, var_query)
    builder = InlineKeyboardBuilder()
    if flagEdu == 5:
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="daily"))
        str_Msg = (
            f'Слова добавлены\n'
            f'<b>Нажмите далее...</b>'
        )
        await state.set_state(myState.edu06)
    else:
        builder.add(types.InlineKeyboardButton(text="Добавить еще слова", callback_data="w_oxford3"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="words"))
        builder.adjust(1, 1)
        str_Msg = (
            f'Добавлено'
        )
    await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await callback.message.delete()
    await myF.f_setDaily('c_oxford3', callback.message.chat.id, pool_base)
    # await pgDB.fExec_LogQuery(pool_log, callback.message.chat.id, 'oxford 3000')
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'|oxford 3000||{curState}')


#
def f________cb______speak():
    pass


# chapter---------------------------------------------------------------------------------------------------------------------------------------- speak callback
@r_oth.callback_query(F.data == "speak")
async def callback_Speak(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    await state.set_state(myState.speak)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('fs'), callback_data="fs"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('dia'), callback_data="dialog"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('mono'), callback_data="monolog"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('lnr'), callback_data="listen"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('retell'), callback_data="retell"))

    # builder.adjust(1, 1, 1, 1)
    builder.adjust(1, 2, 1, 2)
    with open(myF.fGetImg('speak'), "rb") as image_In:
        msg = await callback.message.answer_photo(
            BufferedInputFile(image_In.read(), filename="speak.jpg"),
            caption="Выберите тему:",
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    # await callback.message.delete()
    await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)
    # await callback.message.edit_text("Выберите тему:", reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


@r_oth.callback_query(F.data.startswith("fs"))
async def callback_fs(callback: types.CallbackQuery, state: FSMContext, pool):
    message_obj = callback.message
    pool_base, pool_log = pool
    vUserID = message_obj.chat.id
    bot = message_obj.bot
    #bot = callback.bot
    logger.info(f"-------------------bot:{bot}")


    if callback.data == 'fs':
        await state.set_state(myState.fs)
        str_Msg = (
            f'Вы можете начать диалог первым на любую тему - направьте голосовое или текст\n\n'
            f'или же выбрать пункт "Получить сообщение", в таком случае первым начнет бот'
        )
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text='Получить сообщение', callback_data="fs_ai1"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
        builder.adjust(1,1)
        msg = await message_obj.edit_caption(
            caption=str_Msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
        await myF.fSubMsgDel(state, pool, vUserID, message_obj.message_id, msg.message_id, bot, 2)
    elif callback.data == 'fs_ai1':     #mode ai starts first
        await state.set_state(myState.fs)

        #mode = 1
        #await gen___fs_answer(mode)

        isPremium, sub_stat = await myF.getSubscription(state, vUserID, pool)
        pathFile, arrVoiceParams, var_StrX = myF.fGetFS1L(isPremium)
        logger.info(f'---------------isPremium:{isPremium}|arrVoiceParams:{arrVoiceParams}')

        toggle = {
            '1': {'ind': "0", 'desc': f"{myF.fCSS('vA_st0')}"},
            '2': {'ind': "0", 'desc': f"{myF.fCSS('hint')}"},
        }
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=f"{myF.fCSS('vA_st0')}", callback_data=f"fs_t_1"))      #t for toggle
        builder.add(types.InlineKeyboardButton(text=f"{myF.fCSS('hint')}", callback_data=f"fs_t_2"))
        builder.adjust(2)

        with open(pathFile, 'rb') as ogg:
            msg = await message_obj.answer_voice(
                BufferedInputFile(ogg.read(), filename="voice.ogg"),
                caption='',
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )
        await myF.fSubMsgDel(state, pool, vUserID, message_obj.message_id, msg.message_id, bot, 2)
        await state.update_data(
            audiotext=var_StrX,
            arrVoiceParams=arrVoiceParams,
            toggle=toggle,
            usertext='',
        )
    elif callback.data[:5] == 'fs_t_':      #t for toggle
        # Extract button number from callback data
        button_num = callback.data.split("_")[-1]

        # Get current toggle state
        user_data = await state.get_data()
        toggle = user_data.get('toggle', {})
        usertext = user_data.get('usertext', '')

        if button_num in ['1', '2']:
            # ABC buttons - handle toggle behavior
            current_state = toggle.get(button_num, {}).get('ind', '0')

            if current_state == '1':
                # Button is currently selected - deselect it
                toggle[button_num]['ind'] = '0'
            else:
                # Button is not selected - select it and deselect others
                for i in ['1', '2']:
                    toggle[i]['ind'] = '1' if i == button_num else '0'

        # Update state
        await state.update_data(toggle=toggle)

        # Regenerate keyboard
        builder = InlineKeyboardBuilder()

        # Generate all buttons dynamically
        str_Msg = ''
        any_selected = False

        for key in sorted(toggle.keys(), key=int):  # Sort by numeric key
            button_data = toggle.get(key, {})
            desc = button_data.get('desc', '')
            is_selected = button_data.get('ind') == '1'

            # Add checkmark if selected
            text = f"✅ {desc}" if is_selected else desc

            if is_selected and key in ['1', '2']:  # Only handle message for ABC buttons
                any_selected = True
                if key == '1':
                    audiotext = user_data.get('audiotext', '')
                    str_Msg = (
                        f"🎵 Audio text:\n"
                        f"<blockquote expandable='true'>{audiotext}</blockquote>"
                    )
                elif key == '2':
                    str_Msg = (
                        f"{myF.fCSS('hint')}\n"
                        f"<blockquote expandable='true'>{myF.fCSS('fs_hint')}</blockquote>"
                    )

            builder.add(types.InlineKeyboardButton(text=text, callback_data=f"fs_t_{key}"))
        if usertext:    #
            builder.add(types.InlineKeyboardButton(text='Check grammar', callback_data=f"vA_st2g"))    #g for grammar
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('finish'), callback_data=f"speak"))           #finish
            builder.adjust(2, 2)
        else:           #первое сообщение
            builder.adjust(2)

        # If no ABC button is selected, clear the message
        if not any_selected:
            str_Msg = ''

        await message_obj.edit_caption(
            caption=str_Msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )


@r_oth.message((F.voice | F.text), StateFilter(myState.fs))  # myState.listenSend)
async def media_fs_voice(message: types.Message, bot: Bot, state: FSMContext, pool):
    message_obj = message
    pool_base, pool_log = pool
    vUserID = message_obj.chat.id
    bot = message_obj.bot

    user_data = await state.get_data()
    #toggle = user_data.get('toggle', {})   каждое новое сообщение требует обнуления тоггла
    toggle = {
        '1': {'ind': "0", 'desc': f"{myF.fCSS('vA_st0')}"},
        '2': {'ind': "0", 'desc': f"{myF.fCSS('hint')}"},
    }

    arrVoiceParams = user_data.get('arrVoiceParams', [])
    strHistory = user_data.get('strHistory', '')
    if not arrVoiceParams:
        isPremium, sub_stat = await myF.getSubscription(state, vUserID, pool)
        arrVoiceParams = myF.fGenerateVoiceParams(isPremium)

    logger.info('--------------------0')
    # -------------------processing both voice and text
    usertext = ''
    if message_obj.voice != None:  # voice
        # ---------------------------------------перевод user voice -> text
        usertext = await myF.afVoiceToTxt(message_obj, pool, vUserID)  # транскрипция голоса в текст    , bot
    elif message_obj.text != None:
        usertext = ' '.join(message_obj.text.split())  # message.text
    logger.info(f'--------------------1|usertextLen:{len(usertext)}')
    if usertext != '':
        #goals_json = user_data.get('goals_json')
        englevel_num, englevel = await myF.fGetUserEngLevel(state, vUserID, pool_base)        #ajrm
        logger.info(f'-------------------englevel_num:{englevel_num}|englevel:{englevel}')

        promptSys, promptUser = myP.fPromptFS(usertext, englevel, strHistory)
        audiotext = await myF.afSendMsg2AI(promptUser, pool_base, vUserID, toggleParam=2, systemPrompt=promptSys)
        logger.info(f'--------------------2|audiotext|Len:{len(audiotext)}')
        logger.info(f'--------------------2.1|promptSys:{promptSys}|promptUser:{promptUser}|audiotext:{audiotext}')

        #logger.info(f'audiotext - {audiotext}')
        str_Msg = audiotext     #AI responce

        nm_ogg = await myF.afTxtToOGG(audiotext, arrVoiceParams)

        logger.info(f'--------------------3|afTxtToOGG|')

        strHistory = (      #сохранять 1 сообщение
            #f'{strHistory}\n'
            f'student: {usertext}\n'
            f'teacher: {audiotext}'
        )


        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('vA_st0'), callback_data=f"fs_t_1"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('hint'), callback_data=f"fs_t_2"))
        builder.add(types.InlineKeyboardButton(text='Check grammar', callback_data=f"vA_st2g"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('finish'), callback_data=f"speak"))
        builder.adjust(2, 2)

        with open(nm_ogg, 'rb') as ogg:
            msg = await message.answer_voice(
                BufferedInputFile(ogg.read(), filename="chat.ogg"),
                caption='',
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )
        await state.update_data(
            audiotext=audiotext,
            usertext=usertext,
            toggle=toggle,
            strHistory=strHistory,
        )
        logger.info(f'--------------------4')

#
# chapter---------------------------------------------------------------------------------------------------------------------- Listen and Repeat
# ----------------------------------------------------------------- LR. start form
@r_oth.callback_query(F.data == "listen")
async def callback_Listen(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    curState = await state.get_state()
    if curState == myState.edu03.state:
        flagEdu = 3
    else:
        flagEdu = 0
        await state.set_state(myState.listen)
    print(f'listen|curState = {curState}')

    builder = InlineKeyboardBuilder()
    if flagEdu == 3:
        builder.add(types.InlineKeyboardButton(text="✅ Да", callback_data="listen_send"))
        builder.adjust(2)
        str_Msg = (
            f"Сейчас вы получите файл для прослушивания, ваша задача прослушать и в обратном голосовом сообщении воспроизвести наиболее близко к оригиналу.\n\n"
            f"Вы готовы? \n\n<b>Нажмите Да</b>"
        )

    else:
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="speak"))
        builder.add(types.InlineKeyboardButton(text="✅ Да", callback_data="listen_send"))
        builder.adjust(2)
        str_Msg = (
            f"Сейчас вы получите файл для прослушивания, ваша задача прослушать и в обратном голосовом сообщении воспроизвести наиболее близко к оригиналу.\n\n"
            f"<b>Вы готовы?</b>"
        )
    with open(myF.fGetImg('speak'), "rb") as image_In:
        msg = await callback.message.answer_photo(
            BufferedInputFile(image_In.read(), filename="speak.jpg"),
            caption=str_Msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)  # 1

    await callback.message.delete()
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'|listen|intro|{curState}')


# ----------------------------------------------------------------- LR. send audio
@r_oth.callback_query(F.data == "listen_send")
async def callback_ListenSend(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    curState = await state.get_state()
    if curState == myState.edu03.state:
        flagEdu = 3
    else:
        flagEdu = 0
        await state.set_state(myState.listenSend)
    print(f'listen|listenSend|curState = {curState}')

    varLvlNum, varLvl = await myF.fGetUserEngLevel(state, callback.message.chat.id, pool_base)

    # выбрать рандомно сообщение и ссылку на аудио
    var_query = (
        f"SELECT c_phrase, c_translation, c_audio, c_id "
        f"FROM ts_questions as t1 LEFT JOIN ts_user_question as t2 ON t1.c_id = t2.c_uq_question_id "
        f"WHERE c_cat = 50 AND c_level = {varLvlNum} AND (t2.c_uq_user_id != '{callback.message.chat.id}' OR t2.c_uq_user_id IS NULL) "
        f"ORDER BY RANDOM() "
        f"LIMIT 1"
    )
    # fTimer()
    tmp_Var = await pgDB.fExec_SelectQuery(pool_base, var_query)
    txtListen = [tmp_Var[0][0], tmp_Var[0][1], tmp_Var[0][2], tmp_Var[0][3]]
    # ссылку на аудио открыть и направить в чат
    builder = InlineKeyboardBuilder()
    if flagEdu == 3:
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('spd05x'), callback_data="listen_send_05x"))
        str_Msg = (
            f'<b>Воспроизведите наиболее близко к оригиналу</b>, нажав на иконку микрофона в правом нижнем углу, или введя ответ текстом\n\n'
            f'Если необходимо прослушать сообщение в замедленном темпе, то лучше всего использовать функциональность телеграм, '
            f'если по каким-то причинам это не получается сделать, нажмите на кнопку "{myF.fCSS("spd05x")}"\n'
        )
    else:
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="speak"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('spd05x'), callback_data="listen_send_05x"))
        builder.adjust(1, 1)
        str_Msg = (
            f'Воспроизведите наиболее близко к оригиналу (запишите головое или введите текстом)'
        )
    python_folder = os.path.dirname(sys.executable)
    if os.path.basename(python_folder) == 'bin':
        python_folder = os.path.dirname(python_folder)
    logger.info(f'--------------------python_folder:{python_folder}')
    pathAudio = os.path.join(python_folder, 'storage', 'speak', 'listen', str(txtListen[2]))
    # pathAudio = ''.join(['storage/speak/listen/', str(txtListen[2])])
    print(pathAudio)
    fTimer()
    with open(pathAudio, 'rb') as mp3:
        msg = await callback.message.answer_audio(
            BufferedInputFile(mp3.read(), filename="audio_message_from_bot.mp3"),
            caption=str_Msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    # await pgDB.fExec_LogQuery(pool_log, callback.message.chat.id, f"LnR|listen_send")
    fTimer('mp3 send| LnR')
    # await callback.message.delete()
    # сообщение сохранить в память
    await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

    await state.update_data(txtListen=txtListen)
    await state.update_data(pathAudio=pathAudio)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'|LnR|listen_send|{curState}')


@r_oth.callback_query(F.data == "listen_send_05x")
async def callback_ListenSend_05x(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    curState = await state.get_state()
    if curState == myState.edu03.state:
        flagEdu = 3
    else:
        flagEdu = 0
        await state.set_state(myState.listenSend)
    print(f'listen|listen_send_05x|curState = {curState}')
    data = await state.get_data()
    varLvlNum, varLvl = await myF.fGetUserEngLevel(state, callback.message.chat.id, pool_base)
    pathAudio = data['pathAudio']
    python_folder = os.path.dirname(sys.executable)
    if os.path.basename(python_folder) == 'bin':
        python_folder = os.path.dirname(python_folder)
    logger.info(f'--------------------python_folder:{python_folder}')
    pathAudio = os.path.join(python_folder, 'storage', 'speak', 'listen', '50',
                             f"{pathAudio.split(os.sep)[-1].split('.')[0]}_50.mp3")
    # pathAudio = f"storage/speak/listen/50/{pathAudio.split('/')[-1].split('.')[0]}_50.mp3"
    print(pathAudio)
    # ссылку на аудио открыть и направить в чат
    if flagEdu == 3:
        str_Msg = (
            f'<b>Воспроизведите наиболее близко к оригиналу</b>, нажав на иконку микрофона в правом нижнем углу, или введя ответ текстом'
        )
        with open(pathAudio, 'rb') as mp3:
            msg = await callback.message.answer_audio(
                BufferedInputFile(mp3.read(), filename="audio_message_from_bot.mp3"),
                caption=str_Msg,
                parse_mode=ParseMode.HTML
            )
    else:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="speak"))
        builder.adjust(1)
        str_Msg = (
            f'Воспроизведите наиболее близко к оригиналу (запишите головое или введите текстом)'
        )
        with open(pathAudio, 'rb') as mp3:
            msg = await callback.message.answer_audio(
                BufferedInputFile(mp3.read(), filename="audio_message_from_bot.mp3"),
                caption=str_Msg,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )
    await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"LnR|listen_send_05x")
    await state.update_data(pathAudio='')


# ----------------------------------------------------------------- LR. voice receive and process
@r_oth.message((F.voice | F.text), StateFilter(myState.listenSend, myState.edu03))  # myState.listenSend)
async def media_ListenSendVoice(message: types.Message, bot: Bot, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot

    curState = await state.get_state()
    if curState == myState.edu03.state:
        flagEdu = 3
    else:
        flagEdu = 0
        await state.set_state(myState.listenReceived)
    print(f'listen|listenReceived|curState = {curState}')

    # скопировать из войс получение и обработку звука
    # +++++++++++++++++отправка и получение голосового сообщения ChatGPT++++++++++++++++++++++++++++
    # -------------------processing both voice and text
    strUserVoice = ''
    if message.voice != None:  # voice
        # ---------------------------------------перевод user voice -> text
        strUserVoice = await myF.afVoiceToTxt(message, pool, vUserID)  # транскрипция голоса в текст    , bot
    elif message.text != None:
        #strUserVoice = message.text
        strUserVoice = ' '.join(message.text.split())

    # if strUserVoice != '':

    if strUserVoice != '':
        strUserVoice = myF.fRemoveLastBadSymbol(strUserVoice)
        print(strUserVoice)

        # сравнить текст с изначальным
        data = await state.get_data()
        txtListen = data['txtListen']
        str1, str2, strBool = myF.fGetCompare(txtListen[0], strUserVoice)
        str_Msg = (
            f"{strBool}\n\n"
            f"Изначальная фраза:\n {str1}\n\n"
            f"Ваш ответ:\n {str2}\n\n"
            f"<i>*Перевод:\n {txtListen[1]}</i>"
        )
        builder = InlineKeyboardBuilder()
        if flagEdu == 3:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'),
                                                   callback_data="edu_xx"))  # окончание блока edu03 //ранее daily
            # await state.set_state(myState.edu04)
            str_Msg = (
                f'{str_Msg}\n\n'
                f'<b>Перейдите далее</b>'
            )
        else:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
            builder.add(types.InlineKeyboardButton(text="❕ Еще задание", callback_data="listen_send"))
            builder.adjust(2)
    else:
        str_Msg = (
            f"Something went wrong\n"
            f"We are working on it..."
        )
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))

    with open(myF.fGetImg('speak'), "rb") as image_In:
        msg = await message.answer_photo(
            BufferedInputFile(image_In.read(), filename="speak.jpg"),
            caption=str_Msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    # запись в бд 1, если ответ положительный
    if strBool == '✅':
        print('userID = ', message.chat.id)
        var_query = (
            f"INSERT INTO ts_user_question (c_uq_user_id, c_uq_question_id, c_uq_isused) "
            f"VALUES ('{vUserID}', '{txtListen[3]}', '1')"
        )
        # connection = create_connection(db_name)
        # execute_insert_query(connection, var_query)
        await pgDB.fExec_UpdateQuery(pool_base, var_query)
    # при любом исходе +/- запись в дейлик
    await myF.f_setDaily('c_lnr', message.chat.id, pool_base)
    await myF.fSubMsgDel(state, pool, vUserID, message.message_id, msg.message_id, bot, 3)

    # await message.delete()
    await state.update_data(txtListen=[])
    await pgDB.fExec_LogQuery(pool_log, message.chat.id, f"LnR|voice_receive")


#
# chapter---------------------------------------------------------------------------------------------------------------------- Dialog
@r_oth.callback_query(F.data == "dialog")
async def callback_Dialog(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    curState = await state.get_state()
    if curState == myState.edu09.state:
        flagEdu = 9
    else:
        flagEdu = 0
        await state.set_state(myState.dialog)
    print(f'dialog|curState = {curState}')

    builder = InlineKeyboardBuilder()
    if flagEdu == 9:
        builder.add(types.InlineKeyboardButton(text="Какие новости?", callback_data="dialog"))
        builder.add(types.InlineKeyboardButton(text="Small talk", callback_data="dialog"))
        builder.add(types.InlineKeyboardButton(text="Ситуации", callback_data="dialog"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('hr'), callback_data="dHR"))
        builder.adjust(2, 2)
        str_Msg = (
            f"Выберите раздел {myF.fCSS('hr')}:"
        )
    else:
        builder.add(types.InlineKeyboardButton(text="Какие новости?", callback_data="d_intro_news"))
        builder.add(types.InlineKeyboardButton(text="Small talk", callback_data="d_intro_st"))
        builder.add(types.InlineKeyboardButton(text="Ситуации", callback_data="d_intro_situation"))
        # builder.add(types.InlineKeyboardButton(text="Сгенерировать тему", callback_data="d_intro_custom"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('hr'), callback_data="dHR"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="speak"))
        builder.adjust(2, 2, 2)
        str_Msg = (
            f"Выберите тему:"
        )
    with open(myF.fGetImg('speak'), "rb") as img:
        msg = await callback.message.answer_photo(BufferedInputFile(img.read(), filename="speak.jpg"), caption=str_Msg,
                                                  reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    # await callback.message.delete()
    await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

    # await callback.message.edit_text("Выберите тему:", reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


# -------------------------------------------------------------------------------------------------------- Dialog intro
# -------------------------------------------------------------------------------------- data callbacks
@r_oth.callback_query(F.data.startswith("d_"))  # ,myState.dialog
async def callback_DialogNews(callback: types.CallbackQuery, state: FSMContext, pool, dp):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    nlp_tools = dp.workflow_data["nlp_tools"]

    # global db_name
    # ---------------------------------------------------------------------------- intro
    if callback.data[:8] == 'd_intro_':
        curState = await state.get_state()
        if curState == myState.edu01.state:
            flagEdu = 1
        else:
            flagEdu = 0
            await state.set_state(myState.dialog)
        print(f'dialog|intro|curState = {curState}')

        varLvlNum, dUserLevel = await myF.fGetUserEngLevel(state, callback.message.chat.id, pool_base)
        dThemeName = callback.data[8:]
        # тема диалога определяется переменной dDesc. Которые далее передаются в callback-обработчик сообщений
        if dThemeName == 'news': dDesc, str_Msg = myP.fGetDDesc('news')
        if dThemeName == 'st': dDesc, str_Msg = myP.fGetDDesc('st')
        if dThemeName == 'situation': dDesc, str_Msg = myP.fGetDDesc('situation')

        if flagEdu == 1 and dThemeName == 'news':
            str_Msg = (
                f'<b>"Какие новости?"</b> - регулярный диалог на тему, что случилось с последней встречи\n'
                f'При диалоге Вы с ботом обмениваетесь голосовыми сообщениями\n'
                f'Можно задать ограничение слов во фразе бота - 10 или 20\n'
                f'<b>Начните диалог, выбрав ограничение количества слов во фразах бота: </b>\n'
            )

        print(dDesc)

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="⑩ ❱❱", callback_data="d_first_10"))
        builder.add(types.InlineKeyboardButton(text="⑳ ❱❱", callback_data="d_first_20"))

        with open(myF.fGetImg('speak'), "rb") as image_In:
            msg = await callback.message.answer_photo(
                BufferedInputFile(image_In.read(), filename="speak.jpg"),
                caption=str_Msg,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )
        await callback.message.delete()
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)  # 1

        await state.update_data(dUserLevel=dUserLevel)
        await state.update_data(dThemeName=dThemeName)
        await state.update_data(dDesc=dDesc)
        await state.update_data(dHistory='')
        await state.update_data(dHistoryImprvd='')
        await state.update_data(dHistoryMe='')
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|dialog_news|{curState}')

    # ---------------------------------------------------------------------------- first message. bot->user
    if callback.data[:8] == 'd_first_':
        curState = await state.get_state()
        if curState == myState.edu01.state:
            flagEdu = 1
        else:
            flagEdu = 0
            await state.set_state(myState.dialog)
        print(f'dialog|first|curState = {curState}')

        data = await state.get_data()
        if 'dUserLevel' in data:
            dUserLevel = data['dUserLevel']
            varLvlNum = 0
        else:
            varLvlNum, dUserLevel = await myF.fGetUserEngLevel(state, callback.message.chat.id, pool_base)
        dDesc = data['dDesc']
        dThemeName = data['dThemeName']
        # -----------------------формирование промпта, отправка в ИИ, получение обратно
        dLine_Counter = 1
        dLineWordLimit = callback.data[-2:]

        isPremium, sub_stat = await myF.getSubscription(state, vUserID, pool)
        if dThemeName == 'news':  # для news нужно взять готовый mp3

            fileNm, arrVoiceParams, var_StrX = myF.fGetD1L(isPremium)
            python_folder = os.path.dirname(sys.executable)
            if os.path.basename(python_folder) == 'bin':
                python_folder = os.path.dirname(python_folder)
            logger.info(f'--------------------python_folder:{python_folder}')
            nm_mp3 = os.path.join(python_folder, 'storage', 'speak', 'dialog1line', fileNm)
            dHistory = f"AI: {var_StrX} \n"

        else:
            prompt = myP.fPrompt('start', dDesc, '', dLineWordLimit, vUserID, dUserLevel)  # формирование промпта
            var_StrX = await myF.afSendMsg2AI(prompt, pool_base, vUserID)  # получение текстового ответа от ИИ
            index = var_StrX.find(']:')
            if index >= 0: var_StrX = var_StrX[index + 3:]
            dHistory = f"AI: {var_StrX} \n"

            # -----------------------перевод в mp3

            arrVoiceParams = myF.fGenerateVoiceParams(isPremium)  # генерация параметров голоса
            nm_mp3 = await myF.afTxtToMp3(var_StrX, arrVoiceParams)  # перевод в mp3
        print('Dialog. start prompt. 3. nm_mp3 = ', nm_mp3)
        print('var_StrX - ', var_StrX)

        # -----------------------ссылку на аудио открыть и направить в чат
        builder = InlineKeyboardBuilder()

        if flagEdu == 1:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('audText'), callback_data="d_text_brkdn"))
            # builder.add(types.InlineKeyboardButton(text=myF.fCSS('spd05x'), callback_data="d_05x"))
            # builder.adjust(1,1)
            str_Msg = (
                f"Вы получили Ваше первое сообщение от бота. Давайте прослушаем его\n\n"
                f"   💡  <i>лучше на этом этапе в настройках голосового сообщения настроить однократный повтор сообщения в цикле</i>\n\n"
                f"При необходимости прочитать текст сообщения - нажмите на кнопку '{myF.fCSS('audText')}'\n\n"
                f"❗ <b>Теперь запишите аудио-ответ в продолжение диалога</b>, нажав на иконку микрофона в правом нижнем углу, или введите ответ текстом\n"
                f"{myF.fCSS('duolang')}\n"
            )
        else:
            str_Add = ''
            vWords = await myF.fGetLearnWords(vUserID, pool_base, 5)
            if vWords:
                str_Add = (
                    f'\n\n<i>🎓 Попробуйте использовать изучаемые слова - {vWords}'
                    f' - это полезно для запоминания</i>'
                )
            '''
            var_query = (
                f"SELECT t2.obj_eng, t2.obj_rus "
                f"FROM tw_userprogress AS t1 LEFT JOIN tw_obj AS t2 ON t1.obj_id = t2.obj_id "
                f"WHERE user_id = '{vUserID}' AND status_id < 8 AND status_id > 1 "
                f"ORDER BY RANDOM() "
                f"LIMIT 5"
            )
            queryRes = await pgDB.fExec_SelectQuery(pool_base, var_query)
            if queryRes is not None:
                if len(queryRes) > 0:
                    vOut = ''
                    print(queryRes)

                    for v in queryRes:
                        vOut = f'{vOut} <b>{v[0]}</b> ({v[1]}), '
                    vWords = vOut[:-2]
                    str_Add = (
                        f'\n\n<i>🎓 Попробуйте использовать изучаемые слова - {vWords}'
                        f' - это полезно для запоминания</i>'
                    )
            '''
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="dialog"))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('audText'), callback_data="d_text_brkdn"))
            # builder.add(types.InlineKeyboardButton(text=myF.fCSS('spd05x'), callback_data="d_05x"))
            builder.adjust(2)
            str_Msg = (
                f"❗ <b>Запишите аудио или текстовый ответ в продолжение диалога</b>\n"
                f"{myF.fCSS('duolang')}"
                f'{str_Add}'
            )
        with open(nm_mp3, 'rb') as mp3:
            msg = await callback.message.answer_audio(
                BufferedInputFile(mp3.read(), filename="audio_message_from_bot.mp3"),
                caption=str_Msg,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )
        # if dThemeName != 'news': myF.fDelFile(nm_mp3)   #delete file
        if dThemeName != 'news': await myF.afDelFile(nm_mp3)  # delete file

        # await callback.message.delete()
        # сообщение сохранить в память
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

        await state.update_data(dLine=var_StrX)  # сохранение для вывода текста реплики по callback= dialog_news_line
        await state.update_data(dHistory=dHistory)
        await state.update_data(dUserLevel=dUserLevel)
        await state.update_data(dLine_Counter=dLine_Counter)
        await state.update_data(arrVoiceParams=arrVoiceParams)  # для последующего использования в диалоге
        await state.update_data(dDesc=dDesc)
        await state.update_data(dLineWordLimit=dLineWordLimit)
        await state.update_data(dThemeName=dThemeName)
        await state.update_data(fileNm=nm_mp3)
        # await pgDB.fExec_LogQuery(pool_log, callback.message.chat.id, f"Dialog|AI_msg1|{dDesc}|{dThemeName}")
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|dialog_d_first_10-20|{curState}')

    # ---------------------------------------------------------------------------- voice speed 0.5x
    if callback.data == 'd_05x':
        curState = await state.get_state()
        if curState == myState.edu01.state:
            flagEdu = 1
        else:
            flagEdu = 0
            await state.set_state(myState.dialog)
        print(f'dialog|speed 0.5x|curState = {curState}')

        data = await state.get_data()
        fileNm = data['fileNm']
        dLine_Counter = data['dLine_Counter']

        # fTimer()
        y, sr = librosa.load(fileNm)
        # fTimer('load')
        # fTimer()
        slowed_down_y = librosa.effects.time_stretch(y, rate=0.5)  # 0.5 for 50% speed
        # fTimer('stretch')
        vTmp = fileNm.split('.')
        fileNm = f"{vTmp[0]}_50.{vTmp[1]}"
        # print(fileNm)
        sf.write(fileNm, slowed_down_y, sr)
        if flagEdu == 1:
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('audText'), callback_data="d_text_brkdn"))
            str_Msg = (
                f"❗ <b>Теперь запишите аудио-ответ в продолжение диалога</b>, нажав на иконку микрофона в правом нижнем углу, или введите ответ текстом\n"
                f"{myF.fCSS('duolang')}"
            )
        else:
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('audText'), callback_data="d_text_brkdn"))
            # builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="dialog"))
            if dLine_Counter >= 5:
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('dialEnd'), callback_data="d_end"))
            else:
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('XdialEnd'), callback_data="d_end"))
            builder.adjust(1, 1)

            str_Msg = (
                f"❗ <b>Запишите аудио или текстовый ответ в продолжение диалога</b>\n"
                f"{myF.fCSS('duolang')}"
            )
        with open(fileNm, 'rb') as mp3:
            msg = await callback.message.answer_audio(
                BufferedInputFile(mp3.read(), filename=f"audio_message_from_bot.{vTmp[1]}"),
                caption=str_Msg,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )
        await state.update_data(fileNm='')
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)
        await pgDB.fExec_LogQuery(pool_log, callback.message.chat.id, f"Dialog|AI_msg1|05x")

    # ---------------------------------------------------------------------------- line text brkdn
    if callback.data == 'd_text_brkdn':
        curState = await state.get_state()
        if curState == myState.edu01.state:
            flagEdu = 1
        else:
            flagEdu = 0
            await state.set_state(myState.dialog)
        print(f'dialog|d_text_brkdn|curState = {curState}')

        data = await state.get_data()
        dLine = data['dLine']
        dLine_Counter = data['dLine_Counter']
        if flagEdu == 1:
            str_Msg = (
                f"{dLine}\n\n"
                f"❗ <b>Теперь запишите аудио-ответ в продолжение диалога</b>, нажав на иконку микрофона в правом нижнем углу, или введите ответ текстом\n"
                f"{myF.fCSS('duolang')}"
            )
            msg = await callback.message.answer(dLine, parse_mode=ParseMode.HTML)
        else:
            str_Msg = (
                f"{dLine}\n\n"
            )
            # f"<i>*запишите аудио, нажав на иконку микрофона в правом нижнем углу</i>"
            # builder = InlineKeyboardBuilder()
            # builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="dialog"))
            '''
            if dLine_Counter >= 5:
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('dialEnd'), callback_data="d_end"))
            else:
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('XdialEnd'), callback_data="d_end"))
            builder.adjust(1)
            '''
            msg = await callback.message.answer(dLine,
                                                parse_mode=ParseMode.HTML)  # , reply_markup=builder.as_markup()
        # await state.update_data(dLine='')
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|dialog|d_text_brkdn|{curState}')

    # ---------------------------------------------------------------------------- dialog end
    if callback.data == 'd_end':
        curState = await state.get_state()
        if curState == myState.edu01.state:
            flagEdu = 1
        else:
            flagEdu = 0
            await state.set_state(myState.dialog)
        print(f'dialog|d_end|curState = {curState}')

        data = await state.get_data()
        dLine = data['dLine']
        dDesc = data['dDesc']
        dLineWordLimit = data['dLineWordLimit']
        if 'dUserLevel' in data:
            dUserLevel = data['dUserLevel']
            varLvlNum = 0
        else:
            varLvlNum, dUserLevel = await myF.fGetUserEngLevel(state, callback.message.chat.id, pool_base)
        # dUserLevel = data['dUserLevel']
        dHistory = data['dHistory']
        dHistoryImprvd = data['dHistoryImprvd']
        dHistoryMe = data['dHistoryMe']
        arrVoiceParams = data['arrVoiceParams']
        dLine_Counter = data['dLine_Counter']
        dThemeName = data['dThemeName']
        vUserID = callback.message.chat.id
        print('dHistoryImprvd - ', dHistoryImprvd)
        print('dHistoryMe - ', dHistoryMe)
        prompt = myP.fPrompt('end', dHistoryMe, dHistoryImprvd, dLineWordLimit, vUserID,
                             dUserLevel)  # формирование промпта
        fTimer()
        var_StrX = await myF.afSendMsg2AI(prompt, pool_base, vUserID)  # получение текстового ответа от ИИ
        fTimer('AI response|dialog ends')

        var_StrX = var_StrX.split('}')[1]  # var_StrX.replace('{','').replace('}','')
        print('var_StrX - ', var_StrX)
        str_Msg = (
            f"{var_StrX}\n\n"
            f"⏳ <i>слова будут добавлены в Ваш словарь</i>"
        )
        builder = InlineKeyboardBuilder()
        # builder.add(types.InlineKeyboardButton(text=myF.fCSS('dhistory'), callback_data="d_history"))
        if flagEdu == 1:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'),
                                                   callback_data="edu_xx"))  # окончание блока edu01  //ранее daily
            str_Msg = (
                f'По завершении диалога Вы получаете список слов к изучению\n'
                f'Историю диалога можно посмотреть по кнопке {myF.fCSS("dhistory")}\n\n'
                f'{str_Msg}\n\n'
                f'<b>Перейдите далее</b>'
            )
            # await state.set_state(myState.edu02)
        else:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="dialog"))
        # builder.adjust(1, 1)
        msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)  # delete msg

        await myF.fProcessRecommendedWord(var_StrX, dHistoryMe, pool, vUserID, nlp_tools)  #

        if dThemeName == 'news':
            await myF.f_setDaily('c_dial_news', vUserID, pool_base)
        elif dThemeName == 'situation':
            await myF.f_setDaily('c_dial_situation', vUserID, pool_base)
        await state.update_data(dLine='')
        await state.update_data(dLine_Counter=0)
        await state.update_data(arrVoiceParams=[])
        await state.update_data(dHistory=dHistory)
        await state.update_data(dHistoryImprvd='')
        await state.update_data(dHistoryMe='')
        await state.update_data(dUserLevel=dUserLevel)
        await state.update_data(dDesc='')
        await state.update_data(dLineWordLimit=10)
        await state.update_data(dThemeName='')
        # await pgDB.fExec_LogQuery(pool_log, callback.message.chat.id, f"Dialog|end|{dDesc}|{dThemeName}")
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|dialog|d_end|{curState}')

    # ---------------------------------------------------------------------------- dHistory breakdown
    if callback.data == 'd_history':

        curState = await state.get_state()
        if curState == myState.edu01.state:
            flagEdu = 1
        else:
            flagEdu = 0
            await state.set_state(myState.dialog)
        print(f'dialog|d_history|curState = {curState}')

        data = await state.get_data()
        dHistory = data['dHistory']
        # ------------------------------------------------------обработка для вывода пользователю в d_history
        dHistory = dHistory.replace('{', '').replace('}', '')
        arr = dHistory.split('AI:')
        dHistory = '<i><b>AI:</b>'.join(arr)
        arr = dHistory.split('me:')
        arr = [f"{varT}</i>" for varT in arr]
        dHistory = '<b>me:</b>'.join(arr)
        print(dHistory)

        str_Msg = (
            f"<b>Текст диалога:</b>\n"
            f"{dHistory}"
        )
        builder = InlineKeyboardBuilder()
        if flagEdu == 1:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'),
                                                   callback_data="edu_xx"))  # окончание блока edu01  //ранее daily
            # await state.set_state(myState.edu02)
        else:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="dialog"))

        msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await state.update_data(dHistory='')
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|dialog|d_history|{curState}')
    # ---------------------------------------------------------------------------- hint generation
    if callback.data == 'd_hint':

        curState = await state.get_state()
        if curState == myState.edu01.state:
            flagEdu = 1
        else:
            flagEdu = 0
            await state.set_state(myState.dialog)
        print(f'dialog|d_hint|curState = {curState}')

        data = await state.get_data()
        dHistory = data['dHistory']
        dLine_Counter = data['dLine_Counter']
        prompt = myP.fPrompt('hint', '', dHistory, '', '', '')  # формирование промпта
        var_StrX = await myF.afSendMsg2AI(prompt, pool_base, vUserID)  # получение текстового ответа от ИИ
        str_Msg = (
            f"<b>Варианты продолжения диалога:</b>\n"
            f"{var_StrX}\n\n"
            f"❗ <b>Запишите аудио или текстовый ответ в продолжение диалога</b>\n"
            f"{myF.fCSS('duolang')}"
        )
        '''
        builder = InlineKeyboardBuilder()
        #if flagEdu != 1:
            #builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="dialog"))
        if dLine_Counter >= 5:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('dialEnd'), callback_data="d_end"))
        else:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('XdialEnd'), callback_data="d_end"))
        #if flagEdu == 1:
            builder.adjust(1)
        #else:
        #    builder.adjust(2)
        '''
        msg = await callback.message.answer(str_Msg, parse_mode=ParseMode.HTML)  # , reply_markup=builder.as_markup()

        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|dialog|d_hint|{curState}')

    # ---------------------------------------------------------------------------- hint generation
    if callback.data == 'd_next':

        curState = await state.get_state()
        if curState == myState.edu01.state:
            flagEdu = 1
        else:
            flagEdu = 0
            await state.set_state(myState.dialog)
        print(f'dialog|voice|curState = {curState}')

        data = await state.get_data()
        dDesc = data['dDesc']
        dHistory = data['dHistory']
        dLineWordLimit = data['dLineWordLimit']
        dUserLevel = data['dUserLevel']
        dLine_Counter = data['dLine_Counter']
        arrVoiceParams = data['arrVoiceParams']
        nm_mp3 = data['nm_mp3']
        dLine = data['dLine']

        # -----------------------ссылку на аудио открыть и направить в чат
        str_Msg = (
            f'❗ <b>Прослушайте следующую реплику диалога</b>\n'
            f'  <b>Запишите аудио или текстовый ответ в продолжение диалога</b>\n'
            f"{myF.fCSS('duolang')}\n\n"
            f'💡<i> Если испытываете затруднения - выберите ниже пункт hint и получите варианты продолжения диалога</i>'
        )
        if flagEdu == 1:
            str_Msg = (
                f'{str_Msg}'
                f'\n\n🎓 <i>кнопка "Закончить диалог" имеет разную отрисовку в зависимости от количества реплик бота\n'
                f'Если количество меньше пяти, то цвет кнопки - красный, больше - зеленый </i>'
            )
        else:
            str_Add = ''
            var_query = (
                f"SELECT t2.obj_eng, t2.obj_rus "
                f"FROM tw_userprogress AS t1 LEFT JOIN tw_obj AS t2 ON t1.obj_id = t2.obj_id "
                f"WHERE user_id = '{vUserID}' AND status_id < 8 AND status_id > 1 "
                f"ORDER BY RANDOM() "
                f"LIMIT 5"
            )
            queryRes = await pgDB.fExec_SelectQuery(pool_base, var_query)
            if queryRes is not None:
                if len(queryRes) > 0:
                    vOut = ''
                    # print(queryRes)

                    for v in queryRes:
                        vOut = f'{vOut} <b>{v[0]}</b> ({v[1]}), '
                    vWords = vOut[:-2]
                    str_Add = (
                        f'\n\n<i>🎓 Попробуйте использовать изучаемые слова - {vWords}'
                        f' - это полезно для запоминания</i>'
                    )
            str_Msg = (
                f'{str_Msg}'
                f'{str_Add}'
            )

        builder = InlineKeyboardBuilder()
        # builder.add(types.InlineKeyboardButton(text=myF.fCSS('analysis'), callback_data="txt_analysis"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('audText'), callback_data="d_text_brkdn"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('hint'), callback_data="d_hint"))
        if dLine_Counter >= 5:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('dialEnd'), callback_data="d_end"))
        else:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('XdialEnd'), callback_data="d_end"))
        builder.adjust(1, 1, 1)

        with open(nm_mp3, 'rb') as mp3:
            msg = await callback.message.answer_audio(
                BufferedInputFile(mp3.read(), filename="audio_message_from_bot.mp3"),
                caption=str_Msg, reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML)

        # myF.fDelFile(nm_mp3)   #delete file
        await myF.afDelFile(nm_mp3)  # delete file
        # сообщение сохранить в память
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3,
                             flagPrevMsgDel=False)
        await state.update_data(dLine=dLine)  # сохранение для вывода текста реплики по callback= dialog_news_line
        await state.update_data(dLine_Counter=dLine_Counter)
        # await state.update_data(arrVoiceParams=arrVoiceParams)  # для последующего использования в диалоге
        await state.update_data(dHistory=dHistory)
        # await state.update_data(dHistoryImprvd=dHistoryImprvd)
        # await state.update_data(dHistoryMe=dHistoryMe)
        await state.update_data(dUserLevel=dUserLevel)
        await state.update_data(dDesc=dDesc)
        await state.update_data(dLineWordLimit=dLineWordLimit)
        # await state.update_data(dThemeName=dThemeName)
        # await state.update_data(toggleButtonStatus=toggleButtonStatus)
        # await state.update_data(index_rule_pairs=index_rule_pairs)
        # await pgDB.fExec_LogQuery(pool_log, message.chat.id, f"Dialog|voice|{dDesc}|{dThemeName}")
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|dialog|d_next|{curState}')


# -------------------------------------------------------------------------------------- voice callbacks. other lines. user->bot + bot->user
@r_oth.message((F.voice | F.text), StateFilter(myState.dialog, myState.edu01))
async def media_DialogVoice(message: types.Message, bot: Bot, state: FSMContext, pool, dp):  # ajrm
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot
    nlp_tools = dp.workflow_data["nlp_tools"]
    curState = await state.get_state()
    if curState == myState.edu01.state:
        flagEdu = 1
    else:
        flagEdu = 0
        await state.set_state(myState.dialog)
    print(f'dialog|voice|curState = {curState}')

    data = await state.get_data()
    dDesc = data['dDesc']
    dLineWordLimit = data['dLineWordLimit']
    if 'dUserLevel' in data:
        dUserLevel = data['dUserLevel']
        varLvlNum = 0
    else:
        varLvlNum, dUserLevel = await myF.fGetUserEngLevel(state, vUserID, pool_base)
    # dUserLevel = data['dUserLevel']
    dHistory = data['dHistory']
    arrVoiceParams = data['arrVoiceParams']
    dThemeName = data['dThemeName']
    dLine_Counter = data['dLine_Counter']
    dLine_Counter = dLine_Counter + 1
    if 'dHistoryImprvd' in data:
        dHistoryImprvd = data['dHistoryImprvd']
    else:
        dHistoryImprvd = ''
    if 'dHistoryMe' in data:
        dHistoryMe = data['dHistoryMe']
    else:
        dHistoryMe = ''

    # -------------------processing both voice and text
    strUserVoice = ''
    if message.voice != None:  # voice
        # ---------------------------------------перевод user voice -> text
        strUserVoice = await myF.afVoiceToTxt(message, pool, vUserID)  # транскрипция голоса в текст    , bot
        print('strUserVoice - ', strUserVoice)
    elif message.text != None:
        strUserVoice = ' '.join(message.text.split())
        #strUserVoice = message.text
    dHistory = f"{dHistory}{{me: {strUserVoice} }}\n"

    # ---------------------------------------user text improvement

    #    prompt = myP.fPrompt('improved', strUserVoice, '', '', '', '')  # формирование промпта
    #    var_ImprovedLine = await myF.afSendMsg2AI(prompt, pool_base, vUserID)  # получение текстового ответа от ИИ

    # формирование диалога с исправленными фразами
    #    dHistoryImprvd = f"{dHistoryImprvd}{{me: {var_ImprovedLine} }}\n"
    #    dHistoryMe = f"{dHistoryMe}{{me: {strUserVoice} }}\n"
    #    strOriginal, str_Improved, varBool = myF.fGetCompare(strUserVoice, var_ImprovedLine, False)
    # print('str_Improved - ', str_Improved, '|length - ', len(str_Improved))

    # -----------------------проверка грамматики и формирование тоггла для списка ошибка
    str_Msg, index_rule_pairs, var_ImprovedLine = await myF.fGrammarCheck_txt(
        nlp_tools.tool, strUserVoice, pool, vUserID
    )
    # Generate toggleButtonStatus dictionary dynamically
    toggleButtonStatus = {str(emoji_index): 0 for emoji_index, _ in index_rule_pairs}
    builder = await myF.fSetGrammarBuilder(toggleButtonStatus, index_rule_pairs, state)
    # print('index_rule_pairs - ', index_rule_pairs)

    # формирование диалога с исправленными фразами
    dHistoryImprvd = f"{dHistoryImprvd}{{me: {var_ImprovedLine} }}\n"
    dHistoryMe = f"{dHistoryMe}{{me: {strUserVoice} }}\n"

    # -----------------------отправка улучшенного сообщения пользователя
    msg = await message.answer(str_Msg, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())
    # no myF.fSubMsgDel because this shouldn't be deleted
    print('msg.message_id - ', msg.message_id)
    await state.update_data(str_Msg=str_Msg)

    await state.update_data(strUserVoice=strUserVoice)
    #    await state.update_data(dLine=var_StrX)  # сохранение для вывода текста реплики по callback= dialog_news_line
    await state.update_data(dLine_Counter=dLine_Counter)
    await state.update_data(arrVoiceParams=arrVoiceParams)  # для последующего использования в диалоге
    await state.update_data(dHistory=dHistory)
    await state.update_data(dHistoryImprvd=dHistoryImprvd)
    await state.update_data(dHistoryMe=dHistoryMe)
    await state.update_data(dUserLevel=dUserLevel)
    await state.update_data(dDesc=dDesc)
    await state.update_data(dLineWordLimit=dLineWordLimit)
    await state.update_data(dThemeName=dThemeName)
    await state.update_data(toggleButtonStatus=toggleButtonStatus)
    await state.update_data(index_rule_pairs=index_rule_pairs)
    # await pgDB.fExec_LogQuery(pool_log, message.chat.id, f"Dialog|voice|{dDesc}|{dThemeName}")
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'|dialog|voice|{curState}')

    # ----------------------------------------формирование следующей реплики диалога
    prompt = myP.fPrompt('loop', dDesc, dHistory, dLineWordLimit, vUserID, dUserLevel)  # формирование промпта
    var_StrX = await myF.afSendMsg2AI(prompt, pool_base, vUserID)  # получение текстового ответа от ИИ
    index = var_StrX.find('AI]:')
    if index >= 0: var_StrX = var_StrX[index + 5:]
    dHistory = f"{dHistory}AI: {var_StrX} \n"
    nm_mp3 = await myF.afTxtToMp3(var_StrX, arrVoiceParams)  # перевод в mp3
    print('vUserID = ', vUserID, '|nm_mp3 = ', nm_mp3)
    await state.update_data(nm_mp3=nm_mp3)
    await state.update_data(dLine=var_StrX)  # сохранение для вывода текста реплики по callback= dialog_news_line


'''

'''


# await callback.message.delete()


# -------------------------------------------------------------------------------------- grammar return
@r_oth.callback_query(F.data.startswith('gram:'))
async def callback_grammar(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    message = callback.message
    bot = callback.bot
    try:
        emoji_index, rule_id = callback.data.split("gram:")[1].split(";")
        data = await state.get_data()
        toggleButtonStatus = data.get('toggleButtonStatus', {})
        str_Msg = data.get('str_Msg', 'Описание отсутствует')
        index_rule_pairs = data.get('index_rule_pairs', [])
        logger.info(f'----------clbck--gram---toggleButtonStatus:{toggleButtonStatus}|index_rule_pairs:{index_rule_pairs}')
        # Return to original message
        if emoji_index == '0' and rule_id == '0':
            toggleButtonStatus = {key: 0 for key in toggleButtonStatus.keys()}
            await state.update_data(toggleButtonStatus=toggleButtonStatus)

            builder = await myF.fSetGrammarBuilder(toggleButtonStatus, index_rule_pairs, state)
            await message.edit_text(str_Msg, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())
            return

        # Update toggle dictionary
        toggleButtonStatus = {key: 1 if key == emoji_index else 0 for key in toggleButtonStatus.keys()}
        await state.update_data(toggleButtonStatus=toggleButtonStatus)

        # Query rule description
        var_query = f"SELECT c_ldesc FROM t_grammar WHERE c_ruleid = '{rule_id}'"
        queryRes = await pgDB.fExec_SelectQuery(pool_base, var_query)
        str_RuleDesc = queryRes[0][0] if queryRes else "Правило не найдено."
        # str_RuleDesc += f'||{rule_id}'

        builder = await myF.fSetGrammarBuilder(toggleButtonStatus, index_rule_pairs, state, switcher=True)
        await message.edit_text(str_RuleDesc, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())

    except Exception as e:
        logger.error(f"Error in callback_grammar: {e}")
        await callback.message.answer("Произошла ошибка при обработке запроса.")


# -------------------------------------------------------------------------------------- user line analysis
@r_oth.callback_query(F.data == 'txt_analysis')
async def callback_txt_analysis(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    curState = await state.get_state()
    print(f'{curState}|txt_analysis|curState = {curState}')

    data = await state.get_data()
    strUserVoice = data['strUserVoice']

    # -------------------------------------------------------------
    prompt = myP.fPrompt('line_analysis', strUserVoice, '', '', vUserID, '')  # формирование промпта
    var_Analysis = await myF.afSendMsg2AI(prompt, pool_base, vUserID)  # получение текстового ответа от ИИ
    str_Msg = (
        f'{var_Analysis}\n\n'
        f'❗️<b>Запишите аудио или текстовый ответ в продолжение диалога</b>\n'
        f"{myF.fCSS('duolang')}"
    )

    msg = await callback.message.answer(str_Msg, parse_mode=ParseMode.HTML)  # , reply_markup=builder.as_markup()
    # await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'|{curState}|d_hint|{curState}')


#
# chapter----------------------------------------------------------------------------------------------------------------- dialog HR
@r_oth.callback_query(F.data == 'dHR')
async def callback_dHR(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    # ------------------------------------------------------------------step 0.0 выбор ветки формирования вакансии и резюме (свое-типовое)
    # шаг1 загрузка описания вакансии
    # шаг2 загрузка резюме
    curState = await state.get_state()
    if curState == myState.edu09.state:
        flagEdu = 9
    elif curState == myState.edu09_job.state:
        flagEdu = 9
        await state.set_state(myState.edu09)
    elif curState == myState.edu09_CV2.state:
        flagEdu = 9
        await state.set_state(myState.edu09)
    else:
        flagEdu = 0
        await state.set_state(myState.dialogHR)
    print(f'HR|ID1|fork|curState = {curState}')

    builder = InlineKeyboardBuilder()
    if flagEdu == 9:
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('dHR_custom'), callback_data="dHR_custom"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('dHR_choose'), callback_data="dHR_choose"))
        builder.adjust(1, 1)
        str_Msg = (
            f'Если Вы подготовили текст вакансии и резюме, выберите {myF.fCSS("dHR_custom")}. \n\n'
            f'В противном случае выберите {myF.fCSS("dHR_choose")}'
        )
    else:
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('dHR_custom'), callback_data="dHR_custom"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('dHR_choose'), callback_data="dHR_choose"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="dialog"))
        builder.adjust(1, 1, 1)
        str_Msg = 'Выберите:'

    with open(myF.fGetImg('hr'), "rb") as img:
        msg = await callback.message.answer_photo(BufferedInputFile(img.read(), filename="speak.jpg"), caption=str_Msg,
                                                  reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

    await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)  # 1

    await callback.message.delete()


@r_oth.callback_query(F.data.startswith('dHR_'))
async def callback_dHR_branch(callback: types.CallbackQuery, state: FSMContext, pool, dp):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    nlp_tools = dp.workflow_data["nlp_tools"]
    # ------------------------------------------------------------------branch 1 загрузить свою вакансию
    if callback.data == 'dHR_custom':
        curState = await state.get_state()
        if curState == myState.edu09.state:
            flagEdu = 9
            await state.set_state(myState.edu09_job)
        elif curState == myState.edu09_job2.state:
            flagEdu = 9
            await state.set_state(myState.edu09_job)
        elif curState == myState.edu09_CV2.state:
            flagEdu = 9
            await state.set_state(myState.edu09_job)
        elif curState == myState.edu09_CV.state:
            flagEdu = 9
            await state.set_state(myState.edu09_job)
        else:
            flagEdu = 0
            await state.set_state(myState.dialogHR_job)
        print(f'HR|ID2_1|ask to load job|curState = {curState}')

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="dHR"))
        if flagEdu == 9:
            str_Msg = (
                f"В ответном текстовом сообщение направьте текст <b>вакансии</b>\n\n"
                f"На текущий момент количество символов текста ограничено 4000 знаками. Большее количество символов не будет обработано"
            )
        else:
            str_Msg = (
                f"В ответном текстовом сообщение направьте текст <b>вакансии</b>\n\n"
                f"На текущий момент количество символов текста ограничено 4000 знаками. Большее количество символов не будет обработано"
            )

        with open(myF.fGetImg('hr'), "rb") as image_In:
            msg = await callback.message.answer_photo(BufferedInputFile(image_In.read(), filename="speak.jpg"),
                                                      caption=str_Msg, reply_markup=builder.as_markup(),
                                                      parse_mode=ParseMode.HTML)
        # await callback.message.delete()
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

    # ------------------------------------------------------------------детализация полученного текста резюме
    if callback.data == 'dHR_txtbrk':
        curState = await state.get_state()

        data = await state.get_data()
        if ('dHR_vacancyDesc' in data) and (
                (curState == myState.dialogHR_job2.state) or (curState == myState.edu09_job2.state)):
            vTxt = data['dHR_vacancyDesc']
            vCallbackBCK = 'dHR_custom'
            vCallbackFW = 'dHR_CV'
            print(f'HR|ID2_T|job text view|curState = {curState}')
        elif ('dHR_CV' in data) and ((curState == myState.dialogHR_CV2.state) or (curState == myState.edu09_CV2.state)):
            vTxt = data['dHR_CV']
            vCallbackBCK = 'dHR_CV'
            vCallbackFW = 'dHR_choose_000'
            print(f'HR|ID2_T|CV text view|curState = {curState}')
        else:
            print(f'HR|ID2_T|error|curState = {curState}')

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data=vCallbackBCK))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data=vCallbackFW))
        builder.adjust(2)
        str_Msg = (
            f'{vTxt}'
        )
        msg = await callback.message.answer(str_Msg, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)

    # ------------------------------------------------------------------переход к вводу текста резюме
    if callback.data == 'dHR_CV':
        pool_base, pool_log = pool
        curState = await state.get_state()
        if curState == myState.edu09_job2.state:
            flagEdu = 9
            await state.set_state(myState.edu09_CV)
        elif curState == myState.edu09_CV2.state:
            flagEdu = 9
            await state.set_state(myState.edu09_CV)

        else:
            flagEdu = 0
            await state.set_state(myState.dialogHR_CV)
        print(f'HR|ID2_3|ask to load CV|curState = {curState}')

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="dHR_custom"))
        # builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="dHR"))
        str_Msg = (
            f"В ответном текстовом сообщение направьте текст <b>резюме</b>\n\n"
            f"На текущий момент количество символов текста ограничено 4000 знаками. Большее количество символов не будет обработано"
        )

        with open(myF.fGetImg('hr'), "rb") as img:
            msg = await callback.message.answer_photo(BufferedInputFile(img.read(), filename="hr.jpg"), caption=str_Msg,
                                                      reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        # await callback.message.delete()
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

        await pgDB.fExec_LogQuery(pool_log, vUserID, f"DialogHR|JOB_input")

    # ------------------------------------------------------------------branch 2.1 типовые вакансии. выбор
    if callback.data == 'dHR_choose':
        curState = await state.get_state()
        if curState == myState.edu09.state:
            flagEdu = 9
            await state.set_state(myState.edu09_CV2)
        else:
            flagEdu = 0
            await state.set_state(myState.dialogHR)
        print(f'HR|ID3_1|choose job title|curState = {curState}')

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="Business Analyst", callback_data="dHR_choose_BA_"))
        builder.add(types.InlineKeyboardButton(text="Data Scientist", callback_data="dHR_choose_DS_"))
        builder.add(types.InlineKeyboardButton(text="Database Administrator", callback_data="dHR_choose_DBA"))
        builder.add(types.InlineKeyboardButton(text="Financial Analyst", callback_data="dHR_choose_FA_"))
        builder.add(types.InlineKeyboardButton(text="Human Resources Manager", callback_data="dHR_choose_HR_"))
        builder.add(types.InlineKeyboardButton(text="IT Support Specialist", callback_data="dHR_choose_ITS"))
        builder.add(types.InlineKeyboardButton(text="Marketing Manager", callback_data="dHR_choose_MM_"))
        builder.add(types.InlineKeyboardButton(text="Project Manager", callback_data="dHR_choose_PM_"))
        builder.add(types.InlineKeyboardButton(text="Sales Representative", callback_data="dHR_choose_SLS"))
        builder.add(types.InlineKeyboardButton(text="Software Developer", callback_data="dHR_choose_DEV"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="dHR"))
        builder.adjust(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
        with open(myF.fGetImg('hr'), "rb") as img:
            msg = await callback.message.answer_photo(BufferedInputFile(img.read(), filename="hr.jpg"),
                                                      caption="Выберите специальность:",
                                                      reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        # await callback.message.delete()
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

    # ------------------------------------------------------------------branch 2.2 выбор способа ввода резюме
    if callback.data[:11] == 'dHR_choose_':

        curState = await state.get_state()
        if curState == myState.edu09_CV2.state:
            flagEdu = 9
            await state.set_state(myState.edu09_hr)
        else:
            flagEdu = 0
            await state.set_state(myState.dialogHR)
        print(f'HR|ID3_2|generate interview plan|curState = {curState}')

        data = await state.get_data()
        dHR_roleTitle = callback.data[-3:]
        print(dHR_roleTitle)

        if dHR_roleTitle == '000':
            dHR_vacancyDesc = data['dHR_vacancyDesc']  # получаем описание вакансии
            dHR_CV = data['dHR_CV']  # получаем резюме
        else:
            dHR_vacancyDesc = await myP.fHR_vacancy_desc(dHR_roleTitle, pool_base)  # получаем описание вакансии
            dHR_CV = await myP.fHR_vacancy_desc(f"{dHR_roleTitle}CV", pool_base)  # получаем резюме

        prompt = myP.fHR_PromptInit(dHR_vacancyDesc, dHR_CV)  # получаем первоначальный промпт для создания вопросов
        if 1 == 1:  # test
            var_StrX = await myF.afSendMsg2AI(prompt, pool_base, vUserID, 4)  # получение текстового ответа от ИИ
            arrHR_Questions = [' '.join(element.split()).split('} ', 1)[-1] for element in var_StrX.split('\n') if
                               element.strip()]  # очистка и формирование массива вопросов
        else:
            var_StrX = "{1} Could you please introduce yourself and give us a brief overview of your professional background? \n{2} Can you describe your key responsibilities and achievements in your current role at ABC?"
            arrHR_Questions = [
                "Could you please introduce yourself and give us a brief overview of your professional background?",
                "What motivated you to pursue a career as a Business Analyst?",
                "Could you elaborate on your experience at ABC and the types of projects you worked on during your tenure there?",
                "Can you provide details on how you identified and implemented improvements that resulted in a specific percentage increase in efficiency at ABC?",
                "Describe your role in gathering and documenting business requirements at XYZ. How did you ensure the requirements were comprehensive and accurate?",
                "What business analysis tools and techniques are you most proficient in, and how have you used them in your previous roles?",
                "Can you walk us through a time when you used data analysis to support a key business decision?",
                "What experience do you have with project management methodologies, specifically Agile or Scrum?",
                "How do you manage collaboration between stakeholders at different levels of the organization?",
                "Can you provide an example of a challenging problem you encountered and how you approached solving it?",
                "Have you used any specific business analysis software or tools such as JIRA, Confluence, or Tableau? If so, how did you leverage these tools in your analysis work?",
                "As a CBAP-certified professional, how do you ensure continuous professional development in your field?",
                "Describe a situation where your project did not meet its initial objectives. How did you handle it?",
                "Have you had any experience in the [specific industry, e.g., finance, healthcare, technology]? If so, could you share some examples of your work in that industry?",
                "Can you provide more details on your experience with SQL and data visualization? How did these skills benefit your projects?",
                "Why are you interested in working at DFE, and how do you envision contributing to our team?",
                "How do you ensure that end-users are properly trained and supported when new systems or processes are implemented?",
                "Can you share examples of your experience with creating use cases and process flow diagrams?",
                "Describe a time when you had to conduct a workshop or facilitate a meeting. How did you ensure it was productive?",
                "What aspects of DFE’s company culture and values resonate most with you, and why do you think you’d be a good fit here?"]
        vStr = arrHR_Questions[0]  # выбираем первый вопрос, для отправки в чат
        # преобразование в голосовое
        dHistory = f"HR: {vStr} \n"

        print(arrHR_Questions)
        # myDB.execute_log_query(callback.message.chat.id, '\n'.join(arrHR_Questions))

        # -----------------------перевод в mp3
        isPremium, sub_stat = await myF.getSubscription(state, vUserID, pool)
        arrVoiceParams = myF.fGenerateVoiceParams(isPremium)  # генерация параметров голоса
        nm_mp3 = await myF.afTxtToMp3(vStr, arrVoiceParams)  # перевод в mp3

        # -----------------------ссылку на аудио открыть и направить в чат
        builder = InlineKeyboardBuilder()
        if flagEdu == 9:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('audText'), callback_data="dHR_text_brkdn"))
            builder.add(types.InlineKeyboardButton(text="Список вопросов", callback_data="dHR_questions"))
            builder.adjust(1, 1)

            str_Msg = (
                f'Вы получили первый вопрос собеседования\n'
                f'Текст вопроса можно посмотреть по кнопке {myF.fCSS("audText")}\n'
                f'Общий перечень ключевых вопросов собеседования можно увидеть по кнопке "Список вопросов". Их порядка 20.\n'
                f'Обращаем внимание, что бот задаст два дополнительных уточняющих вопроса к каждому вопросу из Списка на основе Ваших ответов.\n'
                f'Таким образом общее количество вопросов увеличится, равно как и время прохождения собеседования\n'
                f'Если необходимо пропустить часть вопросов, то под списков вопросов отражаются номера вопросов для быстрого перехода\n'
                f'Посмотрим подробнее. Нажмите на кнопку "Список вопросов"'
            )
        else:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="dHR"))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('audText'), callback_data="dHR_text_brkdn"))
            builder.add(types.InlineKeyboardButton(text="Список вопросов", callback_data="dHR_questions"))
            builder.adjust(2, 1)
            str_Msg = (
                f"❗ <b>Запишите аудио или текстовый ответ в продолжение диалога</b>\n"
                f"{myF.fCSS('duolang')}"
            )
        with open(nm_mp3, 'rb') as mp3:
            msg = await callback.message.answer_audio(
                BufferedInputFile(mp3.read(), filename="audio_message_from_bot.mp3"), caption=str_Msg,
                reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        # myF.fDelFile(nm_mp3)   #delete file
        await myF.afDelFile(nm_mp3)  # delete file

        # await callback.message.delete()
        # сообщение сохранить в память
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

        await state.update_data(dLine=vStr)  # сохранение для вывода текста реплики по callback= dialog_news_line
        await state.update_data(dHistory=dHistory)
        await state.update_data(dHistoryImprvd='')  # new241109
        await state.update_data(dHistoryMe='')  # new241109
        await state.update_data(arrVoiceParams=arrVoiceParams)  # для последующего использования в диалоге
        await state.update_data(dHR_auxQ_cnt=0)
        del arrHR_Questions[0]  # удаление использованного вопроса из массива
        await state.update_data(arrHR_Questions=arrHR_Questions)
        #
        await state.update_data(dHR_roleTitle='')  # no need further
        await state.update_data(dHR_vacancyDesc=dHR_vacancyDesc)
        await state.update_data(dHR_CV=dHR_CV)
        varLog = '\n'.join(arrHR_Questions)
        await pgDB.fExec_LogQuery(pool_log, callback.message.chat.id, f"DialogHR|first|")

    # ---------------------------------------------------------------------------- line text brkdn
    if callback.data == 'dHR_text_brkdn':
        curState = await state.get_state()
        if curState == myState.edu09_hr.state:
            flagEdu = 9
        elif curState == myState.edu09_hr2.state:
            flagEdu = 10
        else:
            flagEdu = 0
            await state.set_state(myState.dialogHR)
        print(f'HR|IDV_T|question text brk|curState = {curState}')

        data = await state.get_data()
        dLine = data['dLine']

        if flagEdu == 9:
            # builder = InlineKeyboardBuilder()
            # builder.add(types.InlineKeyboardButton(text=myF.fCSS('dialEnd'), callback_data="dHR_end"))
            str_Msg = (
                f'{dLine}\n\n'
                f'<i>*Нажмите на кнопку "Список вопросов"</i>'
            )
            msg = await callback.message.answer(str_Msg, parse_mode=ParseMode.HTML)
        elif flagEdu == 10:
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('dialEnd'), callback_data="dHR_end"))
            str_Msg = (
                f"{dLine}\n\n"
                f"<i>*запишите аудио, нажав на иконку микрофона в правом нижнем углу, или введите ответ текстом</i>"
            )
            msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

        else:
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="dHR"))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('dialEnd'), callback_data="dHR_end"))
            builder.adjust(2)
            str_Msg = (
                f"{dLine}\n\n"
                f"<i>*запишите аудио, нажав на иконку микрофона в правом нижнем углу, или введите ответ текстом</i>"
            )
            msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)
        # await state.update_data(dLine='')
    # ---------------------------------------------------------------------------- line questions brkdn
    if callback.data == 'dHR_questions':
        curState = await state.get_state()
        if curState == myState.edu09_hr.state:
            flagEdu = 9
            await state.set_state(myState.edu09_hr2)
        elif curState == myState.edu09_hr2.state:
            flagEdu = 10
        else:
            flagEdu = 0
            await state.set_state(myState.dialogHR)
        print(f'HR|IDV_T|question list brk|curState = {curState}')
        data = await state.get_data()
        arrHR_Questions = data['arrHR_Questions']
        strLine = ''
        for i, vQuestion in enumerate(arrHR_Questions):
            strLine = (
                f"{strLine}"
                f"{i + 1}. {vQuestion}\n"
            )

        str_Msg = (
            f"{strLine}\n\n"
            f"<i>*запишите аудио, нажав на иконку микрофона в правом нижнем углу, или введите ответ текстом</i>\n"
            f"<i>*при необходимости быстрого перехода к вопросу выберите его номер ниже</i>"
        )
        if flagEdu == 9:
            str_Msg = (
                f'{str_Msg}\n\n'
                f'Обращаем внимание, что двигаться по вопросам можно только вперед.\n'
                f'Далее продолжайте диалог. При необходимости завершения выберите {myF.fCSS("dialEnd")}'
            )
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('dialEnd'), callback_data="dHR_end"))
        elif flagEdu == 10:
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('dialEnd'), callback_data="dHR_end"))
        else:
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="dHR"))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('dialEnd'), callback_data="dHR_end"))

        questCounter = len(arrHR_Questions)
        print(questCounter)
        vRemainder = questCounter % 5
        vOut = vRemainder
        if vRemainder == 0: vOut = 5
        for i in range(1, questCounter + 1, 1):
            str_CallBack = f"dHR_questions_{i}"
            builder.add(types.InlineKeyboardButton(text=str(i), callback_data=str_CallBack))
        if questCounter <= 5:
            builder.adjust(2, vOut)
        elif questCounter <= 10:
            builder.adjust(2, 5, vOut)
        elif questCounter <= 15:
            builder.adjust(2, 5, 5, vOut)
        elif questCounter <= 20:
            builder.adjust(2, 5, 5, 5, vOut)
        elif questCounter <= 25:
            builder.adjust(2, 5, 5, 5, 5, vOut)
        elif questCounter <= 30:
            builder.adjust(2, 5, 5, 5, 5, 5, vOut)

        msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)
        # await state.update_data(arrVoiceParams=arrVoiceParams)
        await state.update_data(arrHR_Questions=arrHR_Questions)
    # ---------------------------------------------------------------------------- fast move to # question
    if callback.data[:14] == 'dHR_questions_':
        curState = await state.get_state()
        if curState == myState.edu09_hr.state:
            flagEdu = 9
            await state.set_state(myState.edu09_hr2)
        elif curState == myState.edu09_hr2.state:
            flagEdu = 10
        else:
            flagEdu = 0
            await state.set_state(myState.dialogHR)

        data = await state.get_data()
        arrHR_Questions = data['arrHR_Questions']
        arrVoiceParams = data['arrVoiceParams']  # параметры голоса
        dHistory = data['dHistory']
        questNumber = int(callback.data[14:])
        print(questNumber)
        arrHR_Questions = arrHR_Questions[int(questNumber) - 1:]  # переформированный массив
        vStr = arrHR_Questions[0]  # выбираем первый вопрос, для отправки в чат
        dHistory = f"{dHistory}HR: {vStr} \n"
        print(arrHR_Questions)

        # -----------------------перевод в mp3
        nm_mp3 = await myF.afTxtToMp3(vStr, arrVoiceParams)  # перевод в mp3

        # -----------------------ссылку на аудио открыть и направить в чат
        builder = InlineKeyboardBuilder()
        if flagEdu > 0:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('audText'), callback_data="dHR_text_brkdn"))
            builder.add(types.InlineKeyboardButton(text="Список вопросов", callback_data="dHR_questions"))
            builder.adjust(1, 1)
        else:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="dHR"))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('audText'), callback_data="dHR_text_brkdn"))
            builder.add(types.InlineKeyboardButton(text="Список вопросов", callback_data="dHR_questions"))
            builder.adjust(2, 1)
        str_Msg = (
            f"❗ <b>Запишите аудио или текстовый ответ в продолжение диалога</b>\n"
            f"{myF.fCSS('duolang')}"
        )
        with open(nm_mp3, 'rb') as mp3:
            msg = await callback.message.answer_audio(
                BufferedInputFile(mp3.read(), filename="audio_message_from_bot.mp3"),
                caption=str_Msg,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )
        # myF.fDelFile(nm_mp3)   #delete file
        await myF.afDelFile(nm_mp3)  # delete file
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)
        del arrHR_Questions[0]  # удаление использованного вопроса из массива
        await state.update_data(arrHR_Questions=arrHR_Questions)
        await state.update_data(dHR_auxQ_cnt=0)

        await state.update_data(dLine=vStr)  # сохранение для вывода текста реплики по callback= dialog_news_line
        await state.update_data(dHistory=dHistory)
        await state.update_data(arrVoiceParams=arrVoiceParams)  # для последующего использования в диалоге
        varLog = '\n'.join(arrHR_Questions)
        await pgDB.fExec_LogQuery(pool_log, callback.message.chat.id, f"DialogHR|fastmove|")

    # ---------------------------------------------------------------------------- dHR_hint
    if callback.data == 'dHR_hint':
        curState = await state.get_state()
        print(f'dHR|dHR_hint|curState = {curState}')

        data = await state.get_data()
        dHistory = data['dHistory']
        vLastQuestion = data['dLine']
        fTimer()
        prompt = myP.fHR_PromptHint(dHistory, vLastQuestion)  # формирование промпта
        var_StrX = await myF.afSendMsg2AI(prompt, pool_base, vUserID)  # получение текстового ответа от ИИ
        fTimer('hint')
        str_Msg = (
            f"<b>Вариант ответа на вопрос:</b>\n"
            f"{var_StrX}\n\n"
            f"❗ <b>Запишите аудио или текстовый ответ в продолжение диалога</b>\n"
            f"{myF.fCSS('duolang')}"
        )
        # builder = InlineKeyboardBuilder()
        # builder.add(types.InlineKeyboardButton(text=myF.fCSS('dialEnd'), callback_data="dHR_end"))
        msg = await callback.message.answer(str_Msg, parse_mode=ParseMode.HTML)  # , reply_markup=builder.as_markup()
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|dHR|dHR_hint|{curState}')

    # ---------------------------------------------------------------------------- dHR_end
    if callback.data == 'dHR_end':
        curState = await state.get_state()
        if curState == myState.edu09_hr.state:
            flagEdu = 9
            await state.set_state(myState.edu09_hr2)
        elif curState == myState.edu09_hr2.state:
            flagEdu = 10
        else:
            flagEdu = 0
            await state.set_state(myState.dialogHR)
        print(f'HR|ID_end|end analysis|curState = {curState}')

        data = await state.get_data()
        dLine = data['dLine']
        dHR_auxQ_cnt = data['dHR_auxQ_cnt']
        arrVoiceParams = data['arrVoiceParams']
        dHistory = data['dHistory']
        dHistoryImprvd = data['dHistoryImprvd']
        dHistoryMe = data['dHistoryMe']
        arrHR_Questions = data['arrHR_Questions']
        # dHR_roleTitle=data['dHR_roleTitle']
        dHR_vacancyDesc = data['dHR_vacancyDesc']
        dHR_CV = data['dHR_CV']
        varLvlNum, dUserLevel = await myF.fGetUserEngLevel(state, callback.message.chat.id, pool_base)
        vUserID = callback.message.chat.id  # ???
        print('dHistoryImprvd - ', dHistoryImprvd)
        print('dHistoryMe - ', dHistoryMe)
        promptEng = myP.fPrompt('end', dHistoryMe, dHistoryImprvd, '', '', '')  # формирование промпта
        # promptEng = myP.fHR_PromptEnd_Eng(dHistory, vUserID, dUserLevel)     #формирование промпта для анализа английского
        promptHR = myP.fHR_PromptEnd_HR(dHistory, dHR_vacancyDesc,
                                        vUserID)  # формирование промпта для анализа с точки зрения HR
        print(dHistory)
        fTimer()
        var_StrX_Eng = await myF.afSendMsg2AI(promptEng, pool_base, vUserID)  # получение текстового ответа от ИИ
        var_StrX_HR = await myF.afSendMsg2AI(promptHR, pool_base, vUserID)  # получение текстового ответа от ИИ
        fTimer('AI response|dialog ends|ENG')
        var_StrX_Eng = var_StrX_Eng.split('}')[1]  # var_StrX.replace('{','').replace('}','')
        print('var_StrX_Eng - ', var_StrX_Eng)

        str_Msg = (
            f"<b>Анализ собеседования:</b>\n"
            f"{var_StrX_HR}\n\n"
            f"{var_StrX_Eng}\n\n"
            f'⏳ <i>слова будут добавлены в Ваш словарь</i>'
        )
        if flagEdu > 0:
            str_Msg = (
                f'{str_Msg}\n\n'
                f'🎓 На этом обучение завершено. Спасибо!'
            )
            await state.set_state(myState.dialogHR)
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="speak"))
        msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        '''
        if flagEdu > 0:

            # очистка c_edu         пока не нужна
            var_query = (
                f"UPDATE t_daily "
                f"SET c_edu = 0 "
                f"WHERE c_user_id = '{vUserID}'"
            )
            await pgDB.fExec_UpdateQuery(pool_base, var_query)
            '''

        # await callback.message.delete()
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

        await myF.fProcessRecommendedWord(var_StrX_Eng, dHistoryMe, pool, vUserID, nlp_tools)  #

        await state.update_data(dLine='')
        await state.update_data(dHR_auxQ_cnt=0)
        await state.update_data(arrVoiceParams=[])  # для последующего использования в диалоге
        await state.update_data(dHistory='')
        await state.update_data(dHistoryMe='')  # new241109
        await state.update_data(dHistoryImprvd='')  # new241109
        await state.update_data(arrHR_Questions=[])
        # await state.update_data(dHR_roleTitle='')
        await state.update_data(dHR_vacancyDesc='')
        await state.update_data(dHR_CV='')
        await pgDB.fExec_LogQuery(pool_log, callback.message.chat.id, f"DialogHR|end|")
        # myDB.execute_log_query(callback.message.chat.id, '\n'.join(['ENG analysis', var_StrX_Eng, 'HR analysis', var_StrX_HR, 'dHistory', dHistory]))


# -------------------------------------------------------------------------------------- HR voice reply
@r_oth.message((F.voice | F.text), StateFilter(myState.dialogHR, myState.edu09_hr, myState.edu09_hr2))
async def media_dHRVoice(message: types.Message, bot: Bot, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot
    # global db_name
    curState = await state.get_state()
    if curState == myState.edu09_hr.state:
        flagEdu = 9
        await state.set_state(myState.edu09_hr2)
    elif curState == myState.edu09_hr2.state:
        flagEdu = 10
    else:
        flagEdu = 0
        await state.set_state(myState.dialogHR)
    print(f'HR|IDV|handle voice|curState = {curState}')

    data = await state.get_data()

    dLine = data['dLine']
    dHistory = data['dHistory']
    dHR_auxQ_cnt = data['dHR_auxQ_cnt']
    arrVoiceParams = data['arrVoiceParams']
    arrHR_Questions = data['arrHR_Questions']
    # dHR_roleTitle=data['dHR_roleTitle']
    dHR_vacancyDesc = data['dHR_vacancyDesc']
    dHR_CV = data['dHR_CV']
    if 'dHistoryImprvd' in data:
        dHistoryImprvd = data['dHistoryImprvd']
    else:
        dHistoryImprvd = ''
    if 'dHistoryMe' in data:
        dHistoryMe = data['dHistoryMe']
    else:
        dHistoryMe = ''

    # ---------------------------------------перевод user voice -> text
    # -------------------processing both voice and text
    strUserVoice = ''
    if message.voice != None:  # voice
        # ---------------------------------------перевод user voice -> text
        strUserVoice = await myF.afVoiceToTxt(message, pool, vUserID)  # транскрипция голоса в текст    , bot
    elif message.text != None:
        strUserVoice = ' '.join(message.text.split())
        #strUserVoice = message.text

    dHistory = f"{dHistory}{{candidate: {strUserVoice} }}\n"
    # ---------------------------------------user text improvement
    fTimer()
    prompt = myP.fPrompt('improved', strUserVoice, '', '', '', '')  # формирование промпта
    var_ImprovedLine = await myF.afSendMsg2AI(prompt, pool_base, vUserID)  # получение текстового ответа от ИИ
    # формирование диалога с исправленными фразами
    dHistoryImprvd = f"{dHistoryImprvd}{{candidate: {var_ImprovedLine} }}\n"
    dHistoryMe = f"{dHistoryMe}{{candidate: {strUserVoice} }}\n"
    strOriginal, str_Improved, varBool = myF.fGetCompare(strUserVoice, var_ImprovedLine)
    fTimer('improved')
    print('str_Improved - ', str_Improved, '|length - ', len(str_Improved))

    # -----------------------отправка улучшенного сообщения пользователя
    str_Msg = (
        f'ℹ️Ниже <b>анализ</b> Вашего сообщения\n\n'
        f'<u>Текст изначального сообщения:</u>\n'
        f'<blockquote><i>{strOriginal}</i></blockquote>\n'
        f'<u>Предлагаемые изменения:</u>\n'
        f'<blockquote><i>{str_Improved}</i></blockquote>\n\n'
        f'💡<i> При необходимости более детального анализа фразы - выберите "Анализ текста"</i>'
    )
    msg = await message.answer(str_Msg, parse_mode=ParseMode.HTML)  # , reply_markup=builder.as_markup()
    # no myF.fSubMsgDel because this shouldn't be deleted
    # f'➡ <i>{str_Improved}</i>\n\n'

    # ----------------------------------------формирование следующей реплики диалога
    prompt = myP.fHR_PromptLoop(strUserVoice, dLine, dHistory)  # формирование промпта
    if 1 == 1:  # test
        if dHR_auxQ_cnt <= 1:
            var_StrX = await myF.afSendMsg2AI(prompt, pool_base, vUserID, 4)  # получение текстового ответа от ИИ
        else:
            var_StrX = '{{2}} 2'
    else:
        var_StrX = "{1} Could you provide some specific examples of the industries and companies you've worked in, as well as highlight some key projects or achievements during your time as a business analyst?"
    vAddQuestion = ''
    vErr = ''
    if var_StrX.find('{1}') > -1:
        vAddQuestion = var_StrX.split('}', 1)[-1]
        dHR_auxQ_cnt = dHR_auxQ_cnt + 1
    elif var_StrX.find('{2}') > -1:
        vAddQuestion = ''
    else:
        vErr = 'error'
        print(vErr, '  |var_StrX = ', var_StrX)
    print('dHR_auxQ_cnt = ', dHR_auxQ_cnt, ' |var_StrX = ', var_StrX, '  | arrHR_Questions = ', arrHR_Questions)
    flagEnd = 0
    if (vAddQuestion != '') and (dHR_auxQ_cnt <= 2):  # если есть доп вопрос и их количество не более 2
        vStr = vAddQuestion
    else:
        if len(arrHR_Questions) > 0:
            vStr = arrHR_Questions[0]
            del arrHR_Questions[0]
            dHR_auxQ_cnt = 0
        else:
            vStr = ''
            flagEnd = 1
            dHR_auxQ_cnt = 0

    dHistory = f"{dHistory}HR: {vStr} \n"
    if flagEnd == 0:
        nm_mp3 = await myF.afTxtToMp3(vStr, arrVoiceParams)  # перевод в mp3

        # -----------------------ссылку на аудио открыть и направить в чат
        builder = InlineKeyboardBuilder()
        if flagEdu > 0:  # 12.10.24 разница была только в callback_data="dHR". Если текущая версия останется, то if можно удалить
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('analysis'), callback_data="txt_analysis"))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('audText'), callback_data="dHR_text_brkdn"))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('hint'), callback_data="dHR_hint"))
            builder.add(types.InlineKeyboardButton(text="Список вопросов", callback_data="dHR_questions"))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('dialEnd'), callback_data="dHR_end"))
            builder.adjust(1, 2, 2)
        else:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('analysis'), callback_data="txt_analysis"))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('audText'), callback_data="dHR_text_brkdn"))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('hint'), callback_data="dHR_hint"))
            # builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="dHR"))
            builder.add(types.InlineKeyboardButton(text="Список вопросов", callback_data="dHR_questions"))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('dialEnd'), callback_data="dHR_end"))
            builder.adjust(1, 2, 2)

        str_Msg = (
            f'❗ <b>Прослушайте следующую реплику диалога</b>\n'
            f'  <b>Запишите аудио или текстовый ответ в продолжение диалога</b>\n'
            f"{myF.fCSS('duolang')}\n\n"
            f'💡<i> Если испытываете затруднения - выберите ниже пункт hint и получите варианты продолжения диалога</i>'
        )

        with open(nm_mp3, 'rb') as mp3:
            msg = await message.answer_audio(BufferedInputFile(mp3.read(), filename="audio_message_from_bot.mp3"),
                                             caption=str_Msg, reply_markup=builder.as_markup(),
                                             parse_mode=ParseMode.HTML)
        # myF.fDelFile(nm_mp3)   #delete file
        await myF.afDelFile(nm_mp3)  # delete file
    else:
        str_Msg = '👌 Диалог завершен'
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('dialEnd'), callback_data="dHR_end"))
        msg = await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

    # await callback.message.delete()
    # сообщение сохранить в память
    await myF.fSubMsgDel(state, pool, vUserID, message.message_id, msg.message_id, bot, 3)

    await state.update_data(strUserVoice=strUserVoice)
    await state.update_data(dLine=vStr)  # сохранение для вывода текста реплики по callback= dialog_news_line
    await state.update_data(dHR_auxQ_cnt=dHR_auxQ_cnt)
    await state.update_data(arrVoiceParams=arrVoiceParams)  # для последующего использования в диалоге
    await state.update_data(dHistory=dHistory)
    await state.update_data(dHistoryMe=dHistoryMe)  # new241109
    await state.update_data(dHistoryImprvd=dHistoryImprvd)  # new241109
    await state.update_data(arrHR_Questions=arrHR_Questions)
    # wait state.update_data(dHR_roleTitle=dHR_roleTitle)
    await state.update_data(dHR_vacancyDesc=dHR_vacancyDesc)
    await state.update_data(dHR_CV=dHR_CV)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f"DialogHR|voice")
    # myDB.execute_log_query(vUserID, f"me: {strUserVoice}\nHR: {vStr}")

    # ajarm2


# -------------------------------------------------------------------------------------- HR text reply load job
@r_oth.message(F.text, StateFilter(myState.dialogHR_job, myState.edu09_job))
async def text_dHR_job(message: types.Message, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot
    curState = await state.get_state()
    if curState == myState.edu09_job.state:
        flagEdu = 9
        await state.set_state(myState.edu09_job2)
    else:
        flagEdu = 0
        await state.set_state(myState.dialogHR_job2)
    print(f'HR|ID2_2|TEXT1|curState = {curState}')

    #
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="dHR_custom"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="dHR_CV"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('JB_txtbrk'), callback_data="dHR_txtbrk"))
    builder.adjust(2, 1)
    str_Msg = (
        f'Проверьте описание вакансии по кнопке ниже\n'
        f'Если все корректно, то нажмите Далее для загрузки резюме\n'
        f'Если требуется перезагрузить текст, выберите Назад'
    )
    # await message.answer(str_Msg, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())
    with open(myF.fGetImg('hr'), "rb") as image_In:
        msg = await message.answer_photo(
            BufferedInputFile(image_In.read(), filename="hr.jpg"),
            caption=str_Msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )

    # await message.delete()
    await myF.fSubMsgDel(state, pool, vUserID, message.message_id, msg.message_id, bot, 3)

    await state.update_data(dHR_vacancyDesc=message.text)
    await pgDB.fExec_LogQuery(pool_log, message.chat.id, f"DialogHR|JOB_input")


# -------------------------------------------------------------------------------------- HR text reply load CV
@r_oth.message(F.text, StateFilter(myState.dialogHR_CV, myState.edu09_CV))
async def text_dHR_CV(message: types.Message, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot
    curState = await state.get_state()
    if curState == myState.edu09_CV.state:
        flagEdu = 9
        await state.set_state(myState.edu09_CV2)
    else:
        flagEdu = 0
        await state.set_state(myState.dialogHR_CV2)
    print(f'HR|ID2_4|handle CV desc|curState = {curState}')

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="dHR_CV"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="dHR_choose_000"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('CV_txtbrk'), callback_data="dHR_txtbrk"))
    builder.adjust(2, 1)
    str_Msg = (
        f'Проверьте резюме по кнопке ниже\n'
        f'Если все корректно, то нажмите Далее для перехода к собеседованию\n'
        f'Если требуется перезагрузить текст, выберите Назад'
    )

    # await message.answer(str_Msg, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())
    with open(myF.fGetImg('hr'), "rb") as image_In:
        msg = await message.answer_photo(BufferedInputFile(image_In.read(), filename="speak.jpg"), caption=str_Msg,
                                         reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

    # await message.delete()
    await myF.fSubMsgDel(state, pool, vUserID, message.message_id, msg.message_id, bot, 3)

    await state.update_data(dHR_CV=message.text)
    await pgDB.fExec_LogQuery(pool_log, message.chat.id, f"DialogHR|JOB_input")


#
# chapter----------------------------------------------------------------------------------------------------------------------- Monolog
@r_oth.callback_query(F.data == "monolog")
async def callback_Monolog(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    curState = await state.get_state()
    if curState == myState.edu02.state:
        flagEdu = 2
    else:
        flagEdu = 0
        await state.set_state(myState.monolog)
    print(f'monolog|curState = {curState}')

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🧑‍ Личный опыт", callback_data="2_1"))
    builder.add(types.InlineKeyboardButton(text="✈️Путешествия", callback_data="2_2"))
    builder.add(types.InlineKeyboardButton(text="💻 Технологии", callback_data="2_3"))
    builder.add(types.InlineKeyboardButton(text="💼 Карьера", callback_data="2_4"))
    if flagEdu == 2:
        builder.adjust(2, 2)
    else:
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
        builder.adjust(2, 2, 1)
    str_Msg = (
        f'Выберите тему:'
    )
    with open(myF.fGetImg('speak'), "rb") as image_In:
        await callback.message.answer_photo(
            BufferedInputFile(image_In.read(), filename="speak.jpg"),
            caption=str_Msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    await callback.message.delete()
    # await callback.message.edit_text("Выберите тему:", reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'|monolog|choose theme|{curState}')


# ----------------------------------------------------------------------------------------------------------------------------- Выберите тему
@r_oth.callback_query(F.data.startswith('2_'))
async def callback_Theme_Choose(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    curState = await state.get_state()
    if curState == myState.edu02.state:
        flagEdu = 2
    else:
        flagEdu = 0
        await state.set_state(myState.monolog)
    print(f'monolog|generating question|curState = {curState}')

    varCat = callback.data[-1]
    # print(varCat)
    # получить уровень пользователя (50мс)
    var_query = (
        f"SELECT c_ups_eng_level "
        f"FROM t_user_paramssingle "
        f"WHERE c_ups_user_id = '{callback.message.chat.id}'"
    )
    tmp_Var = await pgDB.fExec_SelectQuery(pool_base, var_query)  # execute_query(connection, var_query)
    # print(tmp_Var)
    varLvl = tmp_Var[0][0]  # 2
    var_query = (
        f"SELECT c_id, c_phrase, c_cat, c_level, c_uq_user_id, c_uq_isused "
        f"FROM ts_questions as t1 LEFT JOIN ts_user_question as t2 ON t1.c_id = t2.c_uq_question_id "
        f"WHERE c_cat = '{varCat}' "
        f"   AND c_level = '{varLvl}' "
        f"   AND (c_uq_isused IS NULL OR c_uq_isused != TRUE);"
    )
    print(var_query)
    query_Result_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)  # execute_query(connection, var_query)
    print(query_Result_Arr)
    var_I = random.choice(query_Result_Arr)
    if flagEdu == 2:
        var_Str = (
            f'Ваш вопрос:\n\n'
            f' {var_I[1]} \n\n'
            f'<i>*запишите аудио, нажав на иконку микрофона в правом нижнем углу, или введите ответ текстом</i>'
        )
        print('speak msg_ID = ', var_I[0])
        msg = await callback.message.answer(var_Str, parse_mode=ParseMode.HTML)
    else:
        var_Str = (
            f"\n{var_I[1]} \n\n<i>*запишите аудио, нажав на иконку микрофона в правом нижнем углу, или введите ответ текстом</i>"
        )
        print('speak msg_ID = ', var_I[0])
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
        msg = await callback.message.answer(var_Str, reply_markup=builder.as_markup(),
                                            parse_mode=ParseMode.HTML)
    await callback.message.delete()
    await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)  # 1

    await state.update_data(var_c_qID=var_I[0])
    # await pgDB.fExec_LogQuery(pool_log, callback.message.chat.id, f"Monolog")
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'|monolog|2_* - receive question|{curState}')


# ----------------------------------------------------------------------------------------------------------------------------- прослушать улучшенный текст
@r_oth.callback_query(F.data == 'm_impr_aud')
async def callback_m_impr_aud(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    curState = await state.get_state()
    if curState == myState.edu02.state:
        flagEdu = 2
    else:
        flagEdu = 0
        await state.set_state(myState.monolog)
    print(f'monolog|m_impr_aud|curState = {curState}')

    data = await state.get_data()
    text_Improved = data['text_Improved']

    # -----------------------перевод в mp3
    isPremium, sub_stat = await myF.getSubscription(state, vUserID, pool)
    arrVoiceParams = myF.fGenerateVoiceParams(isPremium)  # генерация параметров голоса
    nm_mp3 = await myF.afTxtToMp3(text_Improved, arrVoiceParams)  # перевод в mp3
    # -----------------------ссылку на аудио открыть и направить в чат
    if flagEdu == 2:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'),
                                               callback_data="edu_xx"))  # окончание блока edu02  //ранее daily
        # await state.set_state(myState.edu03)
        str_Msg = (
            f"Прослушайте предлагаемые изменения текста\n"
            f"<b>После прослушивания нажмите Далее</b>"
        )
    else:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('PickOut'), callback_data="w_pickout:0"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
        builder.add(types.InlineKeyboardButton(text="🔄 Еще вопрос ❱❱", callback_data="monolog"))
        builder.adjust(1, 2)
        str_Msg = (
            f"Прослушайте предлагаемые изменения текста"
        )
    with open(nm_mp3, 'rb') as mp3:
        msg = await callback.message.answer_audio(
            BufferedInputFile(mp3.read(), filename="audio_message_from_bot.mp3"),
            caption=str_Msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

    await pgDB.fExec_LogQuery(pool_log, vUserID, f'|monolog|m_impr_aud|{curState}')


# -------------------------------------------------------------------------------------------------------  msg for voice
@r_oth.message((F.voice | F.text), StateFilter(myState.monolog, myState.edu02))  # myState.monolog)
async def msg_voice_monolog(message: types.Message, bot: Bot, state: FSMContext, pool, dp):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot
    nlp_tools = dp.workflow_data["nlp_tools"]

    curState = await state.get_state()
    if curState == myState.edu02.state:
        flagEdu = 2
    else:
        flagEdu = 0
        await state.set_state(myState.monolog)
    # print(f'monolog|voice|curState = {curState}')

    data = await state.get_data()

    var_c_qID = data['var_c_qID']

    # --------------------------------------------------------------------------------------------
    # -------------------processing both voice and text
    strOriginal = ''
    if message.voice != None:  # voice
        # ---------------------------------------перевод user voice -> text
        strOriginal = await myF.afVoiceToTxt(message, pool,
                                             vUserID)  # преобразование голосового в текст через ChatGPT voice API , bot
    elif message.text != None:
        strOriginal = ' '.join(message.text.split())
        #strOriginal = message.text

    var_Str = myP.fPromptMonologCheck(strOriginal)  # формирование промпта для анализа монолога
    var_StrX = await myF.afSendMsg2AI(var_Str, pool_base, vUserID)  # получение сообщения от ИИ с анализом монолога
    # print('lemma1 - ', var_StrX)
    str_Improved, str_Err, varStr2, arrSyn2DB = await fMonologCheckProcessing(var_StrX, strOriginal, pool_base, vUserID,
                                                                              nlp_tools)  # обработка ответа ИИ с анализом монолога

    # arrWordList_Full

    await state.update_data(text_Improved=str_Improved)  # сохранение в дата неизмененной записи
    strOriginal, str_Improved, varBool = myF.fGetCompare(strOriginal, str_Improved)
    # первое сообщение пользователю (до добавления синонимов БД)
    var_StrPre1 = (
        f'ℹ️Ниже <b>анализ</b> Вашего сообщения\n\n'
        f"<u>Первоначальное сообщение:</u>\n"
        f"<blockquote><i>{strOriginal}</i></blockquote>\n\n"
        f"<u>Предлагаемые изменения:</u>\n"
        f"<blockquote><i>{str_Improved}</i></blockquote>\n\n"
        f"Анализ текста:\n"
        f"<i>{str_Err}</i>"
    )

    var_StrPre2 = (
        f'\nРекомендуемые слова к изучению:\n'
        f'<i> {varStr2}</i>\n'
    )
    if flagEdu == 2:
        var_Str1 = (
            f"Бот анализирует Ваш ответ и возвращает результаты анализа:\n\n"
            f"{var_StrPre1}\n"
        )
        var_Str2 = (
            f"{var_StrPre2}\n"
            f"⏳ <i>слова будут добавлены в Ваш словарь</i>\n\n"
            f"Улучшенный текст можно прослушать\n"
            f"<b>Нажмите на 'Прослушать улучшенный текст'</b>"
        )
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="Прослушать улучшенный текст", callback_data="m_impr_aud"))
    else:
        var_Str1 = (
            f"{var_StrPre1}\n"
        )
        var_Str2 = (
            f"{var_StrPre2}\n"
            f"⏳ <i>Слова будут добавлены в Ваш словарь</i>"
        )
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="Прослушать улучшенный текст", callback_data="m_impr_aud"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('PickOut'), callback_data="w_pickout:0"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
        builder.add(types.InlineKeyboardButton(text="🔄 Еще вопрос ❱❱", callback_data="monolog"))
        builder.adjust(1, 1, 2)
    await message.answer(var_Str1, parse_mode=ParseMode.HTML)
    msg = await message.answer(var_Str2, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await myF.fSubMsgDel(state, pool, vUserID, message.message_id, msg.message_id, bot, 3)

    await myF.f_setDaily('c_monolog', message.chat.id, pool_base)
    # запись в бд 1, что вопрос был отвечен
    var_query = (
        f"INSERT INTO ts_user_question (c_uq_user_id, c_uq_question_id, c_uq_isused) "
        f"VALUES ('{message.chat.id}', '{var_c_qID}', '1') "
    )
    await pgDB.fExec_UpdateQuery(pool_base, var_query)

    # --------------------------------------------------------------------------------------------
    print('arrSyn2DB - ', arrSyn2DB)
    # запись синонимов в БД и обновление сообщения пользователю
    if len(arrSyn2DB) > 0:
        await myF.fProcWordList2Recommend(arrSyn2DB, pool_base, vUserID, nlp_tools)

    # сообщение пользователю  #AJRM поправить в дальнейшем
    '''
    if len(arrSyn2DB)>0:
        var_Str = (
            f"{var_StrPre}\n"
            f"⚡ <i>Слова <b>добавлены</b> в Ваш словарь</i>"
            )
    else:
        var_Str = (
            f"{var_StrPre}\n"
            f"⚡ <i>Обнаружены технические неполадки. Уже исправляем</i>"
            )
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🔄 Еще вопрос ❱❱", callback_data="monolog"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('PickOut'), callback_data="w_pickout:0"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
    builder.adjust(1, 1, 1)
    await message.edit_text(var_Str, reply_markup=builder.as_markup(),parse_mode=ParseMode.HTML)
    '''

    # await pgDB.fExec_LogQuery(pool_log, message.chat.id, f"Monolog|voice")
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'|monolog|voice|{curState}')


#
# chapter----------------------------------------------------------------------------------------------------------------------------- Retelling
@r_oth.callback_query(F.data.startswith("retell"))
async def callback_Retell(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    # ----------------------------------------------------------------- retell briefing and style choice
    if callback.data == 'retell':
        curState = await state.get_state()
        if curState == myState.edu04.state:
            flagEdu = 4
        else:
            flagEdu = 0
            await state.set_state(myState.retell)
        print(f'retell|curState = {curState}')
        varLvlNum, dUserLevel = await myF.fGetUserEngLevel(state, vUserID, pool_base)

        # выгрузка из базы подготовленных текстов (пока только для обучения)
        # --------------------------------------
        if flagEdu == 4:
            var_query = (
                f"SELECT c_Phrase FROM ts_questions WHERE c_cat = '104' "
                f"ORDER BY RANDOM() "
                f"LIMIT 1"
            )
            tmp_Var = await pgDB.fExec_SelectQuery(pool_base, var_query)
            print(tmp_Var)
            var_StrX = tmp_Var[0][0]
            print(var_StrX)

        # выгрузка из БД 5 повторяемых слов
        # --------------------------------------
        retellWords = ''
        if flagEdu == 0:
            vUserID = callback.message.chat.id

            var_query = (
                f"SELECT t1.obj_id, t2.obj_eng "
                f"FROM tw_userprogress AS t1 LEFT JOIN tw_obj AS t2 ON t1.obj_id = t2.obj_id "
                f"WHERE user_id = '{vUserID}' AND status_id < 8 AND status_id > 1 "
                f"ORDER BY RANDOM() "
                f"LIMIT 5"
            )
            queryRes = await pgDB.fExec_SelectQuery(pool_base, var_query)
            vOut = ''
            print(queryRes)
            # print(', '.join(queryRes))

            for v in queryRes:
                vOut = ', '.join([vOut, v[1]])
            retellWords = vOut[2:]
            print('retellWords = ', retellWords)

            # запрос к genAI для генерации истории
            # --------------------------------------
            prompt = myP.fPromptRetellGen(dUserLevel, retellWords)  # получаем промпт для генерации текста
            var_StrX = await myF.afSendMsg2AI(prompt, pool_base, vUserID)
            print('prompt - ', prompt)
            print('var_StrX = ', var_StrX)

        # формрование сообщения пользователю
        # --------------------------------------
        builder = InlineKeyboardBuilder()
        if flagEdu == 4:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="retell_Wait"))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('Trans'), callback_data="retell_Trans"))
            builder.adjust(1, 1)
        else:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="speak"))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="retell_Wait"))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('Trans'), callback_data="retell_Trans"))
            builder.adjust(2, 1)
        subStr = ''
        if retellWords != '': subStr = f"В тексте были использованы следующие изучаемые слова:\n{retellWords}\n\n"
        str_Msg = (
            f"Текст ниже требуется пересказать наиболее близко к оригиналу, направив голосовое\n"
            f"{subStr}"
            f"{var_StrX}\n\n"
            f"При необходимости перевод можно посмотреть по кнопке '{myF.fCSS('Trans')}' \n"
            f"Прочитали, готовы пересказать?\n"
            f"<b>Нажимайте далее</b>"
        )
        msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        '''with open(myF.fGetImg('speak'), "rb") as image_In:
            await callback.message.answer_photo(
                BufferedInputFile(image_In.read(),filename="speak.jpg"),
                caption=str_Msg,
                reply_markup=builder.as_markup(), 
                parse_mode=ParseMode.HTML
                )'''
        await callback.message.delete()
        await state.update_data(txtOriginal=var_StrX)
        await state.update_data(dUserLevel=dUserLevel)
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)  # 1

        # await pgDB.fExec_LogQuery(pool_log, callback.message.chat.id, f"Retell|msg")
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|Retell|msg|{curState}')

    # ----------------------------------------------------------------- retell Text breakdown
    if callback.data == 'retell_Trans':
        curState = await state.get_state()
        if curState == myState.edu04.state:
            flagEdu = 4
        else:
            flagEdu = 0
            await state.set_state(myState.retell)
        print(f'retell|curState = {curState}')

        data = await state.get_data()
        txtOriginal = data['txtOriginal']

        prompt = myP.fPromptSimpleTransText(txtOriginal)
        var_StrX_Ru = await myF.afSendMsg2AI(prompt, pool_base, vUserID)
        builder = InlineKeyboardBuilder()
        if flagEdu == 4:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="retell_Wait"))
        else:
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="speak"))
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="retell_Wait"))
            builder.adjust(2)
        msg = await callback.message.answer(var_StrX_Ru, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|Retell|retell_Trans|{curState}')
    # ----------------------------------------------------------------- retell wait for voice
    if callback.data == 'retell_Wait':
        curState = await state.get_state()
        if curState == myState.edu04.state:
            flagEdu = 4
            await state.set_state(myState.edu04_2)
        else:
            flagEdu = 0
            await state.set_state(myState.retell2)
        print(f'retell|curState = {curState}')

        str_Msg = (
            f"Запишите голосовое сообщение с пересказом"
        )
        if flagEdu == 4:
            with open(myF.fGetImg('speak'), "rb") as image_In:
                msg = await callback.message.answer_photo(
                    BufferedInputFile(image_In.read(), filename="speak.jpg"),
                    caption=str_Msg,
                    parse_mode=ParseMode.HTML
                )
        else:
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="speak"))
            # builder.adjust(2)

            with open(myF.fGetImg('speak'), "rb") as image_In:
                msg = await callback.message.answer_photo(
                    BufferedInputFile(image_In.read(), filename="speak.jpg"),
                    caption=str_Msg,
                    reply_markup=builder.as_markup(),
                    parse_mode=ParseMode.HTML
                )
        # await callback.message.delete()
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|Retell|retell_Wait|{curState}')


# -------------------------------------------------------------------------------------- Retell voice reply
@r_oth.message((F.voice | F.text), StateFilter(myState.retell2, myState.edu04_2))
async def media_retellVoice(message: types.Message, bot: Bot, state: FSMContext, pool, dp):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot

    nlp_tools = dp.workflow_data["nlp_tools"]

    curState = await state.get_state()
    if curState == myState.edu04_2.state:
        flagEdu = 4
        await state.set_state(myState.edu04)
    else:
        flagEdu = 0
        await state.set_state(myState.retell)
    print(f'retell|voice|curState = {curState}')

    data = await state.get_data()
    txtOriginal = data['txtOriginal']
    if 'dUserLevel' in data:
        dUserLevel = data['dUserLevel']
        varLvlNum = 0
    else:
        varLvlNum, dUserLevel = await myF.fGetUserEngLevel(state, vUserID, pool_base)

    # -------------------processing both voice and text
    strUserVoice = ''
    if message.voice != None:  # voice
        # ---------------------------------------перевод user voice -> text
        strUserVoice = await myF.afVoiceToTxt(message, pool, vUserID)  # транскрипция голоса в текст    , bot
    elif message.text != None:
        strUserVoice = ' '.join(message.text.split())
        #strUserVoice = message.text

    prompt = myP.fPromptRetellCheck(strUserVoice, txtOriginal, dUserLevel)  # формирование промпта
    var_StrX = await myF.afSendMsg2AI(prompt, pool_base, vUserID)  # получение текстового ответа от ИИ
    # обработка ответа GPT - разделение по {3}
    try:
        varArr = var_StrX.split('{3}')
        var_StrPre1 = (
            f'<b>Пересказ</b>\n'
            f'{varArr[0]}'
        )
        var_StrPre2 = varArr[1]
        str_Msg = var_StrPre1
        await message.answer(str_Msg, parse_mode=ParseMode.HTML)  # saved in chat history
        str_Msg = (
            f"{var_StrPre2}\n\n"
            f"⏳ <i>рекомендуемые слова будут добавлены в Ваш словарь</i>"
        )

    except Exception as e:
        logger.error(f"media_retellVoice| err: {e}")
        str_Msg = (
            f"{var_StrX}\n\n"
            f"⏳ <i>рекомендуемые слова будут добавлены в Ваш словарь</i>"
        )
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|Retell|voice-error|{e}')

    builder = InlineKeyboardBuilder()
    if flagEdu == 4:
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'),
                                               callback_data="edu_xx"))  # окончание блока edu04 //ранее daily
        str_Msg = (
            f'{str_Msg}\n\n'
            f'<b>Нажмите далее</b>'
        )
        # await state.set_state(myState.edu05)
    else:
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="speak"))
    # builder.adjust(2)
    msg = await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await myF.f_setDaily('c_retell', message.chat.id, pool_base)

    # сообщение сохранить в память
    await myF.fSubMsgDel(state, pool, vUserID, message.message_id, msg.message_id, bot, 3)

    # сохранение слов в БД-------------------------------------------
    # выделение перечня слов из ответа ИИ--------------------

    arrSyn2DB, varStr2 = await fRetellProcess(var_StrX, pool_base, vUserID, nlp_tools)
    if len(arrSyn2DB) > 0:
        await myF.fProcWordList2Recommend(arrSyn2DB, pool_base, vUserID, nlp_tools)
        # ajrm999

    '''
            strQuery_tObj = ""
            strQuery_tUserProgress = ""
            strAltTranslate = ""
            strARPA = ""
            strIPA = ""

                if wordDBTransRu is None:   #если слово не найдено и возвращен None, то нужно сделать перевод и добавить в СЕЛЕКТ записи в БД
                    v_Rus = await myF.afGoogleTrans(lemma, pool_base, vUserID)    #gogle translate
                    v_Rus, strAltTranslate = await myF.fAltTranslationLLM(lemma, v_Rus, pool_base, vUserID) #get alternative translations with AI
                    strARPA, strIPA = myF.getTranscriptionNltk(lemma)         #get transription with nltk
                    sub_strQuery = "', '".join([lemma, v_Rus, strAltTranslate, strARPA, strIPA, "1"])
                    strQuery_tObj = "".join([strQuery_tObj, "('", sub_strQuery, "'), "])
                    strQuery_tUserProgress = "".join([strQuery_tUserProgress, "'", lemma, "', "])       #строка для записи в польз таблицу tw_userprogress
            strQuery_tObj = strQuery_tObj[:-2]
            strQuery_tUserProgress = strQuery_tUserProgress[:-2]
            print('strQuery_tUserProgress = ', strQuery_tUserProgress)
            if len(strQuery_tObj) > 0:
                var_query = f"INSERT INTO tw_obj (obj_eng, obj_rus, obj_rus_alt, obj_arpa, obj_ipa, type_id) VALUES {strQuery_tObj} ON CONFLICT (obj_eng) DO NOTHING;"
                await pgDB.fExec_UpdateQuery(pool_base, var_query)
            if len(strQuery_tUserProgress) > 0:
                var_query = (
                    f"INSERT INTO tw_userprogress (obj_id, userobj_id, user_id, status_id)  "
                    f"SELECT obj_id, ('{message.chat.id}' || obj_id)::bigint, '{message.chat.id}', '1' "
                    f"FROM tw_obj WHERE obj_eng IN ({strQuery_tUserProgress}) "
                    f"ON CONFLICT (userobj_id) DO NOTHING"
                    )
                await pgDB.fExec_UpdateQuery(pool_base, var_query)

    '''

    await state.update_data(txtOriginal='')
    await state.update_data(dUserLevel=dUserLevel)
    await state.update_data(retellWords='')
    # await pgDB.fExec_LogQuery(pool_log, message.chat.id, f"Retell|voice")
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'|Retell|voice|{curState}')


def f___cb__________________service():
    pass


#

# ----------------------------------------------------------------------------------------------------------------   service
@r_oth.callback_query(F.data == "service")
async def callback_service(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    curState = await state.get_state()

    #await myF.fRemoveReplyKB(callback_obj=callback)  # удаление ReplyKB

    # msg = await callback.message.answer(".", reply_markup=ReplyKeyboardRemove())
    # await msg.delete()

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('settings'), callback_data="settings"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('edu'), callback_data="edu_xx"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('releasenotes'), callback_data="rn_intro"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="menu"))
    builder.adjust(1, 1, 1, 1)
    str_Msg = "Выберите раздел:"
    nm_updImg = myF.fImageAddQuote(myF.fGetImg('menu'))
    with open(nm_updImg, "rb") as img:
        msg = await callback.message.answer_photo(
            BufferedInputFile(
                img.read(), filename="menu.jpg"
            ),
            caption=str_Msg,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )

    await myF.afDelFile(nm_updImg)
    await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

    await pgDB.fExec_LogQuery(pool_log, vUserID, f'menu|{curState}')


# chapter---------------------------------------------------------------------------------------------------------------- settings callback
@r_oth.callback_query(F.data.startswith("sett"))
async def callback_settings(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    # global db_name
    await state.set_state(myState.settings)
    if callback.data == 'settings':
        # Create a Web App button instead of a callback button
        # webapp = types.WebAppInfo(url="https://pigeoncorner.github.io/tg_app_lingo/index.html")

        await fShow_settings_menu(vUserID, state, pool, callback_obj=callback)

    # -------------------------------------------------------------------------------------------------------------  callback settings EngLevel
    if callback.data == 'settEng':
        #await myF.fRemoveReplyKB(callback_obj=callback)  # удаление ReplyKB
        var_query = (
            f"SELECT c_qlvl_name "
            f"FROM t_user_paramssingle as t1 LEFT JOIN ts_qlvl as t2 ON t1.c_ups_eng_level = t2.c_qlvl_id "
            f"WHERE c_ups_user_id = '{callback.message.chat.id}'"
        )
        # connection = create_connection(db_name)
        tmp_Var = await pgDB.fExec_SelectQuery(pool_base, var_query)  # execute_query(connection, var_query)
        # print('tmp_Var = ', tmp_Var, 'tmp_Var[0] = ', tmp_Var[0], 'tmp_Var[0][0] = ', tmp_Var[0][0])
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="A - начальный", callback_data="settEng_1"))
        builder.add(types.InlineKeyboardButton(text="B - продвинутый", callback_data="settEng_2"))
        builder.add(types.InlineKeyboardButton(text="C - беглый", callback_data="settEng_3"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="settings"))
        builder.adjust(1, 1, 1, 1)
        strMsg = (
            f"Выберите уровень английского\n"
            f"<i>* текущий уровень - {tmp_Var[0][0]}</i>"
        )
        msg = await callback.message.answer(strMsg, reply_markup=builder.as_markup(),
                                            parse_mode=ParseMode.HTML)
        # await callback.message.delete()
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)
    if callback.data[:8] == 'settEng_':
        # запись в БД уровня по умолчанию -А
        tmpVar = callback.data[-1]
        print('tmpVar = ', tmpVar)
        var_query = (
            f"UPDATE t_user_paramssingle "
            f"SET c_ups_eng_level = '{tmpVar}' "
            f"WHERE c_ups_user_id = '{vUserID}'"
        )
        # connection = create_connection(db_name)
        # execute_insert_query(connection, var_query)
        await pgDB.fExec_UpdateQuery(pool_base, var_query)
        var_query = (
            f"SELECT c_qlvl_name "
            f"FROM t_user_paramssingle as t1 LEFT JOIN ts_qlvl as t2 ON t1.c_ups_eng_level = t2.c_qlvl_id "
            f"WHERE c_ups_user_id = '{callback.message.chat.id}'"
        )
        # connection = create_connection(db_name)
        tmp_Var = await pgDB.fExec_SelectQuery(pool_base, var_query)  # execute_query(connection, var_query)
        strMsg = (
            f"Данные обновлены\n"
            f"<i>* текущий уровень - {tmp_Var[0][0]}</i>"
        )
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="settEng"))
        # builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
        # builder.adjust(2)
        await callback.message.edit_text(strMsg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    # --------------------------------------------------------------------------------------------------------------------  callback settings Alarm
    if callback.data == 'settAlarm':
        #await myF.fRemoveReplyKB(callback_obj=callback)  # удаление ReplyKB
        var_query = (
            f"SELECT c_upp_value "
            f"FROM t_user_paramsplural "
            f"WHERE c_upp_user_id = '{callback.message.chat.id}' AND c_upp_type = '1' "
            f" ORDER BY c_upp_value DESC"
        )
        # connection = create_connection(db_name)
        varArr = await pgDB.fExec_SelectQuery(pool_base, var_query)  # execute_query(connection, var_query)
        varStr = ''
        # print('! - ', varArr)
        if len(varArr) == 0:
            varStr = 'не задано'
        else:
            for varTime in varArr:
                varStr = ''.join([varTime[0], '\n', varStr])
                # print('varTime = ', varTime, '! varTime[0] = ', varTime[0], '| varTime[0][0] = ', varTime[0][0])
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('alarm_add'), callback_data="settAlarm_Add"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('alarm_del'), callback_data="settAlarm_Del"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('alarm_delall'), callback_data="settAlarm_DelAll"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="settings"))
        # builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
        builder.adjust(1, 1, 1, 1)
        strMsg = (
            f"Выберите действие                                                                         \n"
            f"<i>* текущие записи: \n{varStr}</i>"
        )
        msg = await callback.message.answer(strMsg, reply_markup=builder.as_markup(),
                                            parse_mode=ParseMode.HTML)
        # await callback.message.delete()
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)
        await state.update_data(AlarmRecords=varArr)

    # ------------------------------------------------------------------------------------------добавление записи
    if callback.data == 'settAlarm_Add':
        # 1 шаг 4х6 таблица 1-24
        builder = InlineKeyboardBuilder()
        for i in range(0, 24, 1):
            if i < 10:
                tmpVar = ''.join(['0', str(i)])
            else:
                tmpVar = str(i)
            str_CallBack = ''.join(['settAlarm_Add_H', tmpVar])
            builder.add(types.InlineKeyboardButton(text=str(i), callback_data=str_CallBack))
        builder.adjust(4, 4, 4, 4, 4, 4)
        strMsg = (
            f"Укажите час\n"
            f"<i>*время московское</i>"
        )
        await callback.message.edit_text(strMsg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    if callback.data[:15] == 'settAlarm_Add_H':
        # 2шаг - 4 кнопки 00 15 30 45
        # print(callback.data, "   ", str(callback.data)[:-2], "    ", callback.data[-2:])
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="00", callback_data="settAlarm_Add_MM00"))
        builder.add(types.InlineKeyboardButton(text="15", callback_data="settAlarm_Add_MM15"))
        builder.add(types.InlineKeyboardButton(text="30", callback_data="settAlarm_Add_MM30"))
        builder.add(types.InlineKeyboardButton(text="45", callback_data="settAlarm_Add_MM45"))
        builder.adjust(2, 2)
        await callback.message.edit_text("Укажите минуты", reply_markup=builder.as_markup(),
                                         parse_mode=ParseMode.HTML)
        await state.update_data(AlarmHour=callback.data[-2:])
    if callback.data[:16] == 'settAlarm_Add_MM':
        # 3шаг - запись в бд
        data = await state.get_data()
        str_Hour = str(data['AlarmHour'])
        varArr = data['AlarmRecords']
        str_Time = ''.join([str_Hour, ':', str(callback.data[-2:])])
        # проверить существование записи с тем же временем
        isDbWriteOn = 0
        if len(varArr) > 0:
            varExist = 0
            for varTime in varArr:
                print('varTime = ', varTime, '   str_Time = ', str_Time)
                if varTime[0] == str_Time:
                    varExist = 1
            if varExist == 1:
                builder = InlineKeyboardBuilder()
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="settAlarm"))
                # builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
                # builder.adjust(1, 1)
                await callback.message.edit_text("Запись уже существует", reply_markup=builder.as_markup(),
                                                 parse_mode=ParseMode.HTML)
                await state.update_data(AlarmHour='')
                await state.update_data(AlarmRecords=[])
            else:
                isDbWriteOn = 1
        else:
            isDbWriteOn = 1
        if isDbWriteOn == 1:
            # запись в бд
            var_query = (
                f"INSERT INTO t_user_paramsplural (c_upp_user_id, c_upp_type, c_upp_value) "
                f"VALUES ('{callback.message.chat.id}', '1', '{str_Time}')"
            )
            # connection = create_connection(db_name)
            # execute_insert_query(connection, var_query)
            await pgDB.fExec_UpdateQuery(pool_base, var_query)
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="settAlarm"))
            # builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
            # builder.adjust(1, 1)
            await callback.message.edit_text("Запись добавлена", reply_markup=builder.as_markup(),
                                             parse_mode=ParseMode.HTML)
            await state.update_data(AlarmHour='')
            await state.update_data(AlarmRecords=[])
    # ------------------------------------------------------------------------------------------удалить все
    if callback.data == 'settAlarm_DelAll':
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="❌ Нет", callback_data="settAlarm"))
        builder.add(types.InlineKeyboardButton(text="✅ Да", callback_data="settAlarm_DelAllTrue"))
        builder.adjust(2)
        await callback.message.edit_text("Точно удалить все?", reply_markup=builder.as_markup(),
                                         parse_mode=ParseMode.HTML)
    if callback.data == 'settAlarm_DelAllTrue':
        var_query = (
            f"DELETE FROM t_user_paramsplural "
            f"WHERE c_upp_user_id = '{callback.message.chat.id}' AND c_upp_type = '1'"
        )
        # connection = create_connection(db_name)
        # execute_insert_query(connection, var_query)
        await pgDB.fExec_UpdateQuery(pool_base, var_query)
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="settAlarm"))
        # builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
        # builder.adjust(2)
        await callback.message.edit_text("Записи удалены", reply_markup=builder.as_markup(),
                                         parse_mode=ParseMode.HTML)
    # ------------------------------------------------------------------------------------------удалить запись
    if callback.data == 'settAlarm_Del':
        # получение всех записей
        # динамическая генерация кнопок
        # tmp_Var = ""
        var_query = (
            f"SELECT c_upp_value, c_upp_id "
            f"FROM t_user_paramsplural "
            f"WHERE c_upp_user_id = '{callback.message.chat.id}' AND c_upp_type = '1' "
            f" ORDER BY c_upp_value DESC"
        )
        # connection = create_connection(db_name)
        varArr = await pgDB.fExec_SelectQuery(pool_base, var_query)  # execute_query(connection, var_query)
        varStr = ''
        print('! - ', varArr)
        if len(varArr) == 0:
            # вывести нет записей и кнопки назад-меню
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="settAlarm"))
            # builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
            # builder.adjust(2)
            await callback.message.edit_text("Нет записей", reply_markup=builder.as_markup(),
                                             parse_mode=ParseMode.HTML)
        else:
            # посчитать кол-во записей, вывести соответствующее кол-во кнопок
            builder = InlineKeyboardBuilder()
            tmp_Var = ''
            for i in range(0, len(varArr), 1):
                print('time - ', varArr[i][0], ' ID - ', varArr[i][1])
                str_CallBack = ''.join(['settAlarm_Del_', str(varArr[i][1])])
                print('str_CallBack - ', str_CallBack)
                builder.add(types.InlineKeyboardButton(text=str(varArr[i][0]), callback_data=str_CallBack))
                tmp_Var = ''.join([tmp_Var, '1, '])
            print(tmp_Var)
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="settAlarm"))
            # builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
            # builder.adjust(1)
            await callback.message.edit_text("Выберите удаляемую запись", reply_markup=builder.as_markup(),
                                             parse_mode=ParseMode.HTML)
    if callback.data[:14] == 'settAlarm_Del_':
        # удаление 1 выбранной записи
        # получение ID (передается через callback)
        print(len(callback.data))
        var_ID = callback.data[14:len(callback.data)]
        print(var_ID)
        var_query = (
            f"DELETE FROM t_user_paramsplural "
            f"WHERE c_upp_user_id = '{callback.message.chat.id}' AND c_upp_type = '1' AND c_upp_id = {var_ID}"
        )
        # connection = create_connection(db_name)
        # execute_insert_query(connection, var_query)
        await pgDB.fExec_UpdateQuery(pool_base, var_query)

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="settAlarm"))
        # builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
        # builder.adjust(2)
        await callback.message.edit_text("Запись удалена", reply_markup=builder.as_markup(),
                                         parse_mode=ParseMode.HTML)


@r_oth.message(F.web_app_data)
async def app_set_tz(message: types.Message, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = message.chat.id
    bot = message.bot
    try:
        # Parse the data sent from the miniapp
        data = json.loads(message.web_app_data.data)

        vUserID = message.chat.id       #.from_user.id
        timezone = data.get('timezone')
        city_name = data.get('cityName')
        offset = data.get('offset')
        int_offset = fOffset_to_minutes(offset)

        print(f"Parsed data - Timezone: {timezone}, City: {city_name}, Offset: {offset}, int_offset: {int_offset}")

        # Save timezone to your database
        # your_database.save_user_timezone(user_id, timezone)
        var_query = (
            f"UPDATE t_user_paramssingle "
            f"SET c_timezone = '{int_offset}' "
            f"WHERE c_ups_user_id = '{vUserID}'"
        )
        await pgDB.fExec_UpdateQuery(pool_base, var_query)

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
        # Send confirmation message
        await message.answer(
            f"✅ Timezone updated!\n"
            f"🌍 Location: {city_name} {offset}"
        )

        await fShow_settings_menu(vUserID, state, pool, message_obj=message)




    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error from user {message.chat.id}: {e}")     #.from_user.id
    except Exception as e:
        logger.error(f"Unexpected error processing timezone update: {e}", exc_info=True)


'''
async def web_app_data_handler(message: types.Message, state: FSMContext, pool):
    """Обработка всех данных от WebApp"""
    # Определяем тип данных по содержимому
    try:
        data = json.loads(message.web_app_data.data)
        if 'timezone' in data:
            # Это данные timezone
            await app_set_tz(message, state, pool)
        elif 'selected' in data and 'rejected' in data:
            # Это данные word selector
            await handle_word_selector_data(message, state, pool)
        else:
            print(f"Unknown web_app_data format: {data}")
    except Exception as e:
        print(f"Error handling web_app_data: {e}")

'''


def fOffset_to_minutes(offset):
    """
    Convert timezone offset string to minutes integer

    Examples:
    "UTC+5:30" -> 330
    "UTC-5" -> -300
    "UTC+0" -> 0
    "UTC+12:45" -> 765
    """
    if not offset or not isinstance(offset, str):
        return 0

    # Remove "UTC" prefix and clean the string
    offset_clean = offset.replace('UTC', '').strip()

    if not offset_clean:
        return 0

    # Handle sign
    sign = 1
    if offset_clean.startswith('+'):
        offset_clean = offset_clean[1:]
    elif offset_clean.startswith('-'):
        sign = -1
        offset_clean = offset_clean[1:]

    # Split hours and minutes
    if ':' in offset_clean:
        try:
            hours_str, minutes_str = offset_clean.split(':')
            hours = int(hours_str)
            minutes = int(minutes_str)
        except (ValueError, IndexError):
            return 0
    else:
        try:
            hours = int(offset_clean)
            minutes = 0
        except ValueError:
            return 0

    # Convert to total minutes
    total_minutes = (hours * 60) + minutes

    return sign * total_minutes


def fMinutes_to_offset(minutes):
    """
    Convert minutes integer to UTC offset string

    Examples:
    330 -> "UTC+5:30"
    -300 -> "UTC-5"
    0 -> "UTC+0"
    765 -> "UTC+12:45"
    -510 -> "UTC-8:30"
    """
    if not isinstance(minutes, int):
        return "UTC+0"

    # Determine sign
    if minutes < 0:
        sign = "-"
        minutes = abs(minutes)
    else:
        sign = "+"

    # Calculate hours and remaining minutes
    hours = minutes // 60
    remaining_minutes = minutes % 60

    # Format the offset
    if remaining_minutes == 0:
        return f"UTC{sign}{hours}"
    else:
        return f"UTC{sign}{hours}:{remaining_minutes:02d}"


async def fShow_settings_menu(vUserID, state, pool, message_obj=None, callback_obj=None):
    """
    Show settings menu with timezone info and inline buttons
    Can be called from both callback handler and web_app_data handler
    """
    pool_base, pool_log = pool
    if message_obj:
        bot = message_obj.bot
    else:
        bot = callback_obj.message.bot

    '''
    # Create Web App button
    webapp = WebAppInfo(url=config.URL_TZ)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(
            text=myF.fCSS('tz'),
            web_app=webapp
        )]],
        resize_keyboard=True
    )
    

    # Send reply keyboard
    if callback_obj:
        msg = await callback_obj.message.answer(".", reply_markup=keyboard, parse_mode=ParseMode.HTML)
        await myF.fSubMsgDel(state, pool, vUserID, callback_obj.message.message_id, msg.message_id, bot, 2)
    else:
        msg = await message_obj.answer(".", reply_markup=keyboard, parse_mode=ParseMode.HTML)
        await myF.fSubMsgDel(state, pool, vUserID, message_obj.message_id, msg.message_id, bot, 2)
    
    # Get timezone setting
    try:
        var_query = (
            f"SELECT c_timezone "
            f"FROM t_user_paramssingle "
            f"WHERE c_ups_user_id = '{vUserID}'"
        )
        tmp_Var = await pgDB.fExec_SelectQuery(pool_base, var_query)
        v_tz = fMinutes_to_offset(int(tmp_Var[0][0]))
        str_Aux = f'\n<i>* 🌍 Current timezone - {v_tz}</i>'
    except Exception as e:
        str_Aux = ''
        logger.error(f"error |SELECT c_timezone| err: {e}", exc_info=True)
    '''

    str_Aux = ''
    str_Msg = f"Choose settings:{str_Aux}"

    # Build inline keyboard
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="≣ Ваш уровень английского", callback_data="settEng"))
    # builder.add(types.InlineKeyboardButton(text="⏰ Настройки напоминаний", callback_data="settAlarm"))
    # builder.add(types.InlineKeyboardButton(text=myF.fCSS('tz'), web_app=webapp))
    #builder.add(types.InlineKeyboardButton(text=myF.fCSS('prices'), callback_data="prices"))
    # builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="menu"))  # service
    builder.adjust(1, 1)

    nm_Img = myF.fGetImg('sett')

    # Send photo with inline buttons
    with open(nm_Img, "rb") as image_In:
        if callback_obj:
            msg = await callback_obj.message.answer_photo(
                BufferedInputFile(image_In.read(), filename="settings.jpg"),
                caption=str_Msg,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )
        else:
            msg = await message_obj.answer_photo(
                BufferedInputFile(image_In.read(), filename="settings.jpg"),
                caption=str_Msg,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )

    # Handle cleanup
    if callback_obj:
        # await callback_obj.message.delete()
        await myF.fSubMsgDel(state, pool, vUserID, callback_obj.message.message_id, msg.message_id, bot, 2)
    else:
        await myF.fSubMsgDel(state, pool, vUserID, message_obj.message_id, msg.message_id, bot, 2)


# chapter------------------------------------------------------------------------------------------------------------------ releasenotes callback
@r_oth.callback_query(F.data.startswith("rn_"))
async def callback_release(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    await state.set_state(myState.common)
    if callback.data == 'rn_intro':
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text='30.03.2025', callback_data="rn_4"))
        builder.add(types.InlineKeyboardButton(text='02.03.2025', callback_data="rn_2"))
        builder.add(types.InlineKeyboardButton(text='12.03.2025', callback_data="rn_3"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="service"))
        builder.add(types.InlineKeyboardButton(text='11.11.2024', callback_data="rn_1"))
        # builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))

        str_Msg = (
            f"<i>16.06.2025</i>\n\n"
            f"🆕 <b>В релизе внесены следующие изменения:</b>\n\n"
            f"✔️ Добавлена поддержка анализа грамматики в режимах диалога и {myF.fCSS('native')} \n"
            f"  🔸 теперь каждая фраза анализируется на наличие ошибок и выводится криткий перечень предлагаемых изменений\n"
            f"  🔸 подробное описание ошибок доступно по кнопкам под сообщением\n\n"
            f"📌 Описание других релизов см. ниже"
        )
        builder.adjust(1, 2, 2)

        await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await callback.message.delete()
    elif callback.data == 'rn_4':
        str_Msg = (
            f"<i>30.03.2025</i>\n\n"
            f"🆕 <b>В релизе внесены следующие изменения:</b>\n\n"
            f"✔️ Добавлена возможность ввода сообщений 📝 текстом помимо голоса \n"
            f"✔️ Обновлен 📚 словарь, теперь за основу берется библиотека NGSL (New General Service List Project)\n"
            f"✔️ Созданы карточки слов с \n"
            f"      📖 примерами использования, \n"
            f"      🏛️ происхождением слов и \n"
            f"      📙 описанием из англоязычного толкового словаря\n\n"
            f"📌 Описание других релизов см. ниже"
        )
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="rn_intro"))
        await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await callback.message.delete()
    elif callback.data == 'rn_3':
        str_Msg = (
            f"<i>12.03.2025</i>\n\n"
            f"🆕 <b>В релизе внесены следующие изменения:</b>\n\n"
            f"✔️ Добавлен раздел меню {myF.fCSS('native')}. \n"
            f"  <u>Описание:</u>\n"
            f"  🔸 📝 Введите текст или 🎤 продиктуйте фразу на русском или английском."
            f"В ответе вы получите вариант, как её произнёс бы носитель языка. При наличии грамматических ошибок, "
            f"будет предложено исправление.\n"
            f"  🔸 При вводе одного английского слова, оно будет переведено и добавлено в рекомендуемые.\n"
            f"  🔸 Для русского слова предложим несколько синонимов и возможные сленговые варианты\n\n"
            f"✔️ Переработана визуализация меню\n\n"
            f"✔️ Внесены технические улучшения производительности\n\n"
        )
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="rn_intro"))
        await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await callback.message.delete()
    elif callback.data == 'rn_2':
        str_Msg = (
            f"<i>02.03.2025</i>\n\n"
            f"🆕 <b>В релизе внесены следующие изменения:</b>\n\n"
            f"✔️ Добавлен раздел новостей:\n"
            f"  🔸 каждая статья дается в трех вариантах - 🟢 оригинал, 🟡 Intermediate, 🔴 Beginner\n"
            f"  🔸 статья отображается с отключаемым построчным переводом (по умолчанию включен)\n"
            f"  🔸 к каждой статье приводится список рекомендуемых слов, добавляемый в словарь по кнопке\n\n"
            f"✔️ Переработан раздел добавления рекомендуемых слов к изучаемым:\n"
            f"  🔸 выводится список 9 слов, \n"
            f"  🔸 на цифровой клавиатуре внизу отмечаются слова к изучению\n"
            f"  🔸 по кнопке Submit выбранные слова добавляются к изучаемым\n\n"
            f"✔️ Исправлена ошибка исключения слов из повтора\n\n"
        )
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="rn_intro"))
        await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await callback.message.delete()
    elif callback.data == 'rn_1':
        str_Msg = (
            f"<i>11.11.2024</i>\n"
            f"🆕 <b>В релизе были внесены следующие изменения:</b>\n"
            f"✔️ <u>Поддержка русских слов</u> в английском тексте - теперь в диалоге на английском можно использовать русские слова, бот их "
            f"переведет и добавит к изучаемым словам\n"
            f"✔️ Добавление раздела в блок Words для просмотра всего <u>списка изучаемых слов</u>\n"
            f"✔️ Доработки визуализации\n"
            f"✔️ Добавление <u>ввода английских слов с клавиатуры</u> - при вводе английского слова в режиме Меню выполняется его перевод и добавляется к изучаемым\n"
            f"✔️ <u>Ускорение</u> обработки <u>аудиофайлов</u>\n"
            f"✔️ Разного рода технические улучшения\n\n"
        )
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="rn_intro"))
        await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await callback.message.delete()


# chapter----------------------------------------------------------------------------------------------------------------- donate callback
@r_oth.callback_query(F.data.startswith('donate'))
async def callback_donate(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    donate_url_rf = "https://donate.stream/SpeakPalAI"
    donate_url_world = "https://www.paypal.com/ncp/payment/SE5RREJYUPFPL"
    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(text="❤️ Donate ️☕️(РФ)", url=donate_url_rf))
    builder.add(types.InlineKeyboardButton(text="❤️ Donate ️☕️(WORLD)", url=donate_url_world))
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
    builder.adjust(2, 1)
    str_Msg = (
        f"Будем очень признательны, если Вы сможете поддержать бот чашечкой кофе ☕!\n\n"
        f"Каждая Ваша поддержка помогает проекту развиваться 🎉.\n\n"
        f"💖 Спасибо за Ваш интерес и участие!"
    )
    nm_updImg = myF.fGetImg('donate')
    with open(nm_updImg, "rb") as img:
        msg = await callback.message.answer_photo(BufferedInputFile(img.read(), filename="menu.jpg"), caption=str_Msg,
                                                  reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

    await pgDB.fExec_LogQuery(pool_log, vUserID, f'donate|')


# chapter----------------------------------------------------------------------------------------------------------------------------------------------- edu callback
@r_oth.callback_query(F.data.startswith("edu"))
async def callback_edu(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    if callback.data == 'edu_xx':
        await state.set_state(myState.common)
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('qstart'), callback_data="qstart_1"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('dia'), callback_data="edu_01"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('mono'), callback_data="edu_02"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('lnr'), callback_data="edu_03"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('retell'), callback_data="edu_04"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('repeat'), callback_data="edu_05"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('hr'), callback_data="edu_09"))
        # builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="service"))
        builder.adjust(1, 2, 1, 2, 1, 1)
        str_Msg = (
            f"Выберите раздел обучения"
        )
        nm_updImg = myF.fImageAddQuote(myF.fGetImg('menu'))
        with open(nm_updImg, "rb") as img:
            msg = await callback.message.answer_photo(
                BufferedInputFile(img.read(), filename="menu.jpg"),
                caption=str_Msg,
                reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML
            )
        # myF.fDelFile(nm_updImg)
        await myF.afDelFile(nm_updImg)
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)
    else:
        vAuxTxt = ''
        if callback.data == 'edu_01':
            await state.set_state(myState.edu01)
            vBlock = 'Диалог'
            vCallbck = 'menu'
        elif callback.data == 'edu_02':
            await state.set_state(myState.edu02)
            vBlock = 'Монолог'
            vCallbck = 'daily'
        elif callback.data == 'edu_03':
            await state.set_state(myState.edu03)
            vBlock = 'раздел Listen and repeat'
            vCallbck = 'daily'
        elif callback.data == 'edu_04':
            await state.set_state(myState.edu04)
            vBlock = 'раздел Пересказ'
            vCallbck = 'daily'
        elif callback.data == 'edu_05':
            await state.set_state(myState.edu05)
            vBlock = 'работу с новыми словами'
            vCallbck = 'daily'
        elif callback.data == 'edu_09':
            await state.set_state(myState.edu09)
            vBlock = 'Собеседование'
            vAuxTxt = (
                f'Вам желательно подготовить описание вакансии и Ваше резюме\n'
                f'Оба в формате текста не более 4000 символов. Большее количество не будет обработано\n'
                f'В целом есть предзагруженные вакансии и резюме. Можно воспользоваться ими\n\n'
            )
            vCallbck = 'daily'

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="edu_xx"))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data=vCallbck))
        str_Msg = (
            f'В этом блоке обучения мы разберем {vBlock}\n\n'
            f'{vAuxTxt}'
            f'Начинаем?\n'
        )
        nm_updImg = myF.fImageAddQuote(myF.fGetImg('menu'))
        with open(nm_updImg, "rb") as img:
            msg = await callback.message.answer_photo(
                BufferedInputFile(img.read(), filename="menu.jpg"),
                caption=str_Msg,
                reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML
            )
        # myF.fDelFile(nm_updImg)
        await myF.afDelFile(nm_updImg)
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

def f___cb__________________timeout():
    pass


@r_oth.callback_query(F.data == "activity_continue")
async def callback_activity_continue(callback: types.CallbackQuery, state: FSMContext, pool):
    """
    Handler для кнопки "Продолжить" - восстановление активной подписки
    Переводит статус с 9 (timeout) на 3 (active)
    После этого пользователь автоматически попадет в get_users_with_timezones()
    и начнет получать обычные напоминания
    """
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    sw_timer = myF.SWTimer()
    vLangCode = callback.message.from_user.language_code

    try:
        sw_timer(f'activity_continue - {vLangCode} - ')

        # Обновляем статус подписки с 9 на 3 (active)
        query = f"""
        UPDATE t_user 
        SET 
            c_subscription_status = 3,
            c_subscription_date = NOW()
        WHERE c_user_id = {vUserID}
        RETURNING c_user_id;
        """

        result = await pgDB.fExec_UpdateQuery(pool_base, query)

        if result:
            # Обновляем время последней активности
            query_status = f"""
            INSERT INTO t_user_status (c_user_id, c_last_active)
            VALUES ({vUserID}, NOW())
            ON CONFLICT (c_user_id) 
            DO UPDATE SET c_last_active = NOW();
            """
            await pgDB.fExec_UpdateQuery(pool_base, query_status)

            # Логируем действие
            await pgDB.fExec_LogQuery(
                pool_log,
                vUserID,
                "Activity|Continue|User resumed active subscription from timeout (9->3)",
                1
            )

            sw_timer.close()

            # Формируем сообщение с подтверждением
            vAddress = myF.get_address2user(callback.from_user.first_name)
            str_Msg = (
                f"✅ <b>{vAddress} Отлично! Мы продолжаем!</b>\n\n"
                "Рады, что вы с нами! 🎉\n\n"
                "Уведомления возобновлены, и мы продолжим помогать вам "
                "в изучении английского языка.\n\n"
                "📚 Вы можете продолжить обучение прямо сейчас через меню ниже.\n\n"
                "💡 <b>Что вас ждет:</b>\n"
                "📰 Утренние статьи в 8:00\n"
                "🧠 Квизы в 12:00\n"
                "📚 Практика слов в 18:00\n"
                "🗣️ Разговорная практика в 21:00"
            )

            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
            builder.adjust(1)

            msg = await callback.message.answer(
                str_Msg,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )

            await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

            print(f"✅ User {vUserID} continued subscription (status 9 -> 3)")
        else:
            raise Exception("Failed to update subscription status")

    except Exception as e:
        print(f"❌ Error in activity_continue handler for user {vUserID}: {e}")
        await callback.answer("❌ Произошла ошибка. Попробуйте позже.", show_alert=True)
        sw_timer.close()


@r_oth.callback_query(F.data == "activity_resume")
async def callback_activity_resume(callback: types.CallbackQuery, state: FSMContext, pool):
    """
    Handler для кнопки "Возобновить сейчас" - быстрое возобновление
    Переводит статус с 0 (paused) на 3 (active)
    """
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    sw_timer = myF.SWTimer()
    vLangCode = callback.message.from_user.language_code

    try:
        sw_timer(f'activity_resume - {vLangCode} - ')

        # Устанавливаем статус обратно на 3 (active)
        query = """
        UPDATE t_user 
        SET 
            c_subscription_status = 3,
            c_subscription_date = NOW()
        WHERE c_user_id = $1
        RETURNING c_user_id;
        """

        result = await pgDB.fExec_UpdateQuery(pool_base, query, vUserID)

        if result:
            # Обновляем время последней активности
            query_status = """
            INSERT INTO t_user_status (c_user_id, c_last_active)
            VALUES ($1, NOW())
            ON CONFLICT (c_user_id) 
            DO UPDATE SET c_last_active = NOW();
            """
            await pgDB.fExec_UpdateQuery(pool_base, query_status, vUserID)

            # Логируем действие
            await pgDB.fExec_LogQuery(
                pool_log,
                vUserID,
                "Activity|Resume|User resumed from pause (0->3)",
                1
            )

            sw_timer.close()

            # Формируем приветственное сообщение
            vAddress = myF.get_address2user(callback.from_user.first_name)
            str_Msg = (
                f"🎉 <b>{vAddress} С возвращением!</b>\n\n"
                "Уведомления возобновлены! Мы рады, что вы снова с нами.\n\n"
                "📚 Продолжайте обучение через меню ниже. "
                "У нас есть много интересного для вас!\n\n"
                "💡 <b>Расписание уведомлений:</b>\n"
                "📰 Утренние статьи в 8:00\n"
                "🧠 Квизы в 12:00\n"
                "📚 Практика слов в 18:00\n"
                "🗣️ Разговорная практика в 21:00"
            )

            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
            builder.adjust(1)

            msg = await callback.message.answer(
                str_Msg,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )

            await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

            print(f"🔄 User {vUserID} resumed subscription (status 0 -> 3)")
        else:
            raise Exception("Failed to update subscription status")

    except Exception as e:
        print(f"❌ Error in activity_resume handler for user {vUserID}: {e}")
        await callback.answer("❌ Произошла ошибка. Попробуйте позже.", show_alert=True)
        sw_timer.close()


def f___cb__________________quiz():
    pass


# chapter--------------------------------------------------------------------------------------------------------------- quiz callback
@r_oth.callback_query(F.data.startswith('quiz'))
async def callback_quiz(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    await state.update_data(menu_command_disabled=False)

    if callback.data[:5] == 'quiz_':
        boolIsTrue = callback.data[-1] == 't'
        # print('boolIsTrue - ', boolIsTrue)
        num = int(callback.data.split('_')[1][0])  # Gets the digit before 't'/'f'
        # print('num - ', num)
        vDate = datetime.now().strftime('%y%m%d')
        var_query = (
            # f"SELECT c_comment, c_true FROM public.t_quiz WHERE TO_CHAR(c_date, 'YYMMDD') = '{vDate}'"
            f"SELECT t2.c_comment, t2.c_true "
            f"FROM t_quiz_reminder AS t1 LEFT JOIN t_quiz AS t2 ON t2.c_id = t1.c_quiz_id "
            f"WHERE TO_CHAR(c_date, 'YYMMDD') = '{vDate}'"
        )
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
        v_comment = var_Arr[0][0]
        v_true = var_Arr[0][1]
        srtPreMsg = f'{"✅ Correct!" if boolIsTrue else "❌ Incorrect!"}\n\n'
        str_Msg = (
            f'{srtPreMsg}'
            #f'<u>Правильный ответ:</u>\n'
            #f'      {v_true}\n\n'
            f'{v_comment}'
            #f'\n\n<b>А ещё</b> можно потратить 5 мин ⏱️ на практику с ботом 🤖 — напоминаем, он работает как в текстовом 🗨️, так и в голосовом 🗣️ режиме'
        )
        builder = InlineKeyboardBuilder()
        #builder.add(types.InlineKeyboardButton(text=myN.fCSS('story'), callback_data="story"))
        #builder.add(types.InlineKeyboardButton(text=myF.fCSS('newsppr'), callback_data="news_s1_3-0"))
        #builder.add(types.InlineKeyboardButton(text=myF.fCSS('speak'), callback_data="speak"))
        #builder.add(types.InlineKeyboardButton(text=myF.fCSS('repeat'), callback_data="words"))
        builder.add(types.InlineKeyboardButton(text='get more ❱❱', callback_data="menu"))
        builder.adjust(2, 2, 1)
        msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        #await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)
        await pgDB.fExec_LogQuery(pool_log, vUserID, f'|quiz|srtPreMsg|')


def f___cb__________________other():
    pass


# chapter--------------------------------------------------------------------------------------------------------------- testing callback
@r_oth.callback_query(F.data.startswith('testing'))
async def callback_testing(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot

    # if callback.data == 'testing':
    if callback.data[:8] == 'testingT':
        if callback.data != 'testingT':
            vTarget = int(callback.data[-1])

            var_query = (
                f"UPDATE t_user_paramssingle "
                f"SET c_ups_target = '{vTarget}' "
                f"WHERE c_ups_user_id = '{vUserID}'"
            )
            await pgDB.fExec_UpdateQuery(pool_base, var_query)

        # await state.set_state(myState.englevel01)
        arrCat = ['A', 'B', 'C', 'D', 'E']
        data = await state.get_data()
        if 'test_Cnt' in data:
            test_Cnt = int(data['test_Cnt'])
            test_Cnt += 1
        else:
            test_Cnt = 1
        if 'test_arrWeights' in data:
            arrWeights = data['test_arrWeights']
        else:
            arrWeights = [1, 1, 1, 1, 1]
        if 'test_Category' in data:
            vCat = data['test_Category']
        else:
            vCat = random.choice(arrCat)
        if 'test_Level' in data:
            vLevel = str(data['test_Level'])
        else:
            vLevel = '40'  # should be changed AJRM
        # vCat = callback.data[-1]
        print('vCat - ', vCat)
        print('vLevel - ', vLevel)

        # vLevel = '40'
        # -----------------------category weight adj
        vIndex = arrCat.index(vCat)
        print('vIndex - ', vIndex)
        arrWeights[vIndex] = 0
        print(arrCat)
        print(arrWeights)

        if test_Cnt < 6:
            # ------------------------------------------------------------------------------------
            #   str_Msg task - question - 3-4 options
            #   right option - which one
            #   correct answer - for further displaying
            str_Msg, test_TrueOptionIndx, test_TrueOption, fileNm = myF.getTrainingQuest(vCat, vLevel)

            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text='A', callback_data="testing_1"))
            builder.add(types.InlineKeyboardButton(text='B', callback_data="testing_2"))
            builder.add(types.InlineKeyboardButton(text='C', callback_data="testing_3"))

            if vCat == 'D':
                python_folder = os.path.dirname(sys.executable)
                if os.path.basename(python_folder) == 'bin':
                    python_folder = os.path.dirname(python_folder)
                logger.info(f'--------------------python_folder:{python_folder}')
                pathAudio = os.path.join(python_folder, 'storage', 'speak', 'testing', fileNm)
                # pathAudio = ''.join(['storage/speak/listen/', str(txtListen[2])])
                print(pathAudio)
                builder.adjust(3)
                with open(pathAudio, 'rb') as mp3:
                    msg = await callback.message.answer_audio(
                        BufferedInputFile(mp3.read(), filename="audio.mp3"),
                        caption=str_Msg,
                        reply_markup=builder.as_markup(),
                        parse_mode=ParseMode.HTML
                    )
            else:
                builder.add(types.InlineKeyboardButton(text='D', callback_data="testing_4"))
                builder.adjust(2, 2)
                await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
            print('test_TrueOptionIndx - ', test_TrueOptionIndx)
            await state.update_data(test_TrueOption=test_TrueOption)
            await state.update_data(test_TrueOptionIndx=test_TrueOptionIndx + 1)
            await state.update_data(test_Cnt=test_Cnt)
        else:
            # calculate here final level
            str_Msg = (
                f"final level is {vLevel}"
            )
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="qstart_i"))
            await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

        await state.update_data(test_Category=vCat)
        await state.update_data(test_Level=vLevel)
        await state.update_data(test_arrWeights=arrWeights)

    elif callback.data[:8] == 'testing_':
        vNum = callback.data[-1]
        data = await state.get_data()
        test_TrueOptionIndx = data['test_TrueOptionIndx']
        test_TrueOption = data['test_TrueOption']
        test_Category = data['test_Category']
        test_Level = int(data['test_Level'])
        test_arrWeights = data['test_arrWeights']
        print('test_arrWeights - ', test_arrWeights)
        print('test_TrueOptionIndx - ', test_TrueOptionIndx, '  |vNum - ', vNum)
        # смена категории
        arrCat = ['A', 'B', 'C', 'D', 'E']
        # arrCat.remove(test_Category)
        fTimer()
        vCat = random.choices(arrCat, weights=test_arrWeights, k=1)[0]
        print('vCat - ', vCat)
        fTimer('random')
        if int(vNum) == int(test_TrueOptionIndx):
            # correct
            str_Msg = (
                f'✅ Верно!\n'
                f'<i>{test_TrueOption}</i>'
            )
            # повышение уровня
            test_Level = test_Level + 20 if test_Level < 100 else 100
        else:
            str_Msg = (
                f'❌ Неверно!\n'
                f'<i>{test_TrueOption}</i>'
            )
            # понижение уровня
            test_Level = test_Level - 20 if test_Level > 20 else 20
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="testingT"))  # testing
        await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

        await state.update_data(test_TrueOptionIndx=0)
        await state.update_data(test_TrueOption='')
        await state.update_data(test_Level=test_Level)
        await state.update_data(test_Category=vCat)


# chapter----------------------------------------------------------------------------------------------------------------------------------------------- prices callback
@r_oth.callback_query(F.data.startswith('price'))
async def callback_prices(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot


    # типовое сообщение по тарифам
    if callback.data == 'prices':
        await state.set_state(myState.prices)
        #await myF.fRemoveReplyKB(callback_obj=callback)  # удаление ReplyKB
        var_query = (
            f"SELECT c_subscription_status, c_next_payment_date, c_balance, c_sub_period, c_bal_token "
            f"FROM t_user "
            f"WHERE c_user_id = '{vUserID}'"
        )
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

        vSubscriptionStatus = int(var_Arr[0][0])
        vNextPayDate = str(var_Arr[0][1])
        vBalance = var_Arr[0][2]
        vBal_Token = var_Arr[0][4]
        if vBalance == None: vBalance = 0
        if vBal_Token == None: vBal_Token = 0
        vBalance = vBalance + vBal_Token
        v_sub_period = var_Arr[0][3]
        logger.info(f'v_sub_period:{v_sub_period}')
        if v_sub_period == 'q':
            strPer = 'Квартал'
        elif v_sub_period == 'm':
            strPer = 'Месяц'
        else:
            strPer = 'отключено'



        logger.info(f'vSubscriptionStatus:{vSubscriptionStatus}|vNextPayDate:{vNextPayDate}|vBalance:{vBalance}|v_sub_period:{v_sub_period}')
        builder = InlineKeyboardBuilder()
        if vSubscriptionStatus > 0 and vSubscriptionStatus < 3 :    #
            strAutoPay = 'Включено' if vSubscriptionStatus == 1 else 'Отключено'
            str_Msg = (
                f'Статус подписки - <b>Активна</b>\n'
                f'Дата окончания - <b>{vNextPayDate}</b>\n'
                f'Период подписки - <b>{strPer}</b>\n'
                f'Автопродление - <b>{strAutoPay}</b>'
            )
            if vSubscriptionStatus == 1:
                builder.add(types.InlineKeyboardButton(text="Отменить подписку", callback_data="price_decline"))
                webapp = WebAppInfo(url=config.URL_AGR)
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('agrmnt'), web_app=webapp))
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
                builder.adjust(1, 1, 1)
            else:
                webapp = WebAppInfo(url=config.URL_AGR)
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('agrmnt'), web_app=webapp))
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
                builder.adjust(1, 1)



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
                date_obj = var_Arr[0][1]
                discount_validdate = date_obj.strftime("%Y.%m.%d %H:%M") if date_obj else ''
            else:
                price_m = myPay.PRICE_M
                price_q = myPay.PRICE_Q
                discount_validdate = ''

            strDiscount = f'Скидка - <b>50%</b>\nСкидка действительна до <b>{discount_validdate}</b>\n\n' if discount_validdate else ''

            str_Msg = (
                f'Статус подписки - <b>Неактивна</b>\n'
                f'Стоимость подписки:\n'
                f'  квартал - {price_q}₽\n'
                f'  месяц - {price_m}₽\n\n'
                f'{strDiscount}'
                f'<i>Отменить подписку можно в любой момент в разделе меню Настройки -> Управление подпиской</i>'
            )
            builder.add(types.InlineKeyboardButton(text=f"Купить квартал ({price_q}₽)", callback_data="buy_c_q"))    #   price_buy_c_0_q
            builder.add(types.InlineKeyboardButton(text=f"Купить месяц ({price_m}₽)", callback_data="buy_c_m")) #price_buy_c_0_m
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))
            builder.adjust(1, 1, 1)
            await state.update_data(price_m=price_m)
            await state.update_data(price_q=price_q)

        msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)  # 1

    elif callback.data == 'price_decline':
        str_Msg = (
            "Вы уверены?\n"
            "Подтверждаете отмену?"
        )
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="Нет", callback_data="prices"))
        builder.add(types.InlineKeyboardButton(text="Да", callback_data="price_decline_true"))
        builder.adjust(2)

        msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)

    elif callback.data == 'price_decline_true':
        await state.set_state(myState.prices)
        # удаление информации о сохраненном способе платежа
        var_query = (
            f"UPDATE t_user "
            f"SET c_saved_payment = NULL, c_card_id = NULL, c_amount = NULL, c_subscription_status = 2 "       #, c_sub_period = NULL
            f"WHERE c_user_id = '{vUserID}'"
        )
        await pgDB.fExec_UpdateQuery(pool_base, var_query)
        builder = InlineKeyboardBuilder()
        webapp = WebAppInfo(url=config.URL_AGR)
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('agrmnt'), web_app=webapp))
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('fw'), callback_data="menu"))
        builder.adjust(1, 1)

        str_Msg = (
            f'<b>Автопродление отключено</b>\n\n'
            f'Для возврата средств необходимо подать заявление на возврат (см. условия договора).\n'
            f'В противном случае подписка завершится автоматически по окончании оплаченного периода.\n\n'
            f'Будем рады видеть вас снова! 💙'
        )
        msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)





def text_to_rotated(text):
    """
    Преобразует русский текст в перевернутый вид (для чтения при повороте на 180°)
    """
    russian_to_rotated = {
        'а': 'ɐ',
        'б': 'ƍ',
        'в': 'ʚ',
        'г': '⅃',
        'д': 'ɓ',
        'е': 'ǝ',
        'ж': 'ж',
        'з': 'ε',
        'и': 'и',
        'й': 'и̲',
        'к': 'ʞ',
        'л': 'v',  # '|ʃ'
        'м': 'w',
        'н': 'н',
        'о': 'о',
        'п': 'u',
        'р': 'd',
        'с': 'ɔ',
        'т': '┴',
        'у': 'ʎ',
        'ф': 'ф',
        'х': 'х',
        'ц': 'ǹ',
        'ч': 'h',
        'ш': 'm',
        'щ': "'m",
        'ъ': 'q̧',
        'ы': 'ıq',
        'ь': 'q',
        'э': '€',
        'ю': 'oı',
        'я': 'ʁ',
        ',': "'",
        ' ': ' '
    }

    # Переворачиваем текст справа налево
    reversed_text = text[::-1]

    # Заменяем символы согласно словарю
    result = ''
    for char in reversed_text:
        result += russian_to_rotated.get(char.lower(), char)

    return result

def ___________________dummy():
    pass
