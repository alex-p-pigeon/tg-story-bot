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


