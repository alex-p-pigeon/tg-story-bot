from datetime import datetime, date, timezone, timedelta
print("selfFunctions. Start importing:", datetime.now().time().strftime("%H:%M:%S"))
from PIL import Image, ImageDraw, ImageFont
import hashlib
from pathlib import Path
import aiofiles

import textwrap
import math
import random
import uuid
print("selfFunctions. End importing:", datetime.now().time().strftime("%H:%M:%S"))
import os
import sys
import fpgDB as pgDB
from config_reader import config
from aiogram.fsm.context import FSMContext
from aiogram import types, Bot
from typing import Tuple, Optional
import re
from google.cloud import texttospeech_v1
'''
import nltk
from nltk.corpus import cmudict
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk import pos_tag
'''
import aiohttp
import time
import prompt as myP
from openai import AsyncOpenAI
import asyncio
import difflib
import copy
from aiogram.types import ReplyKeyboardRemove

from aiogram.utils.keyboard import InlineKeyboardBuilder
from states import myState

import logging
logger = logging.getLogger(__name__)


'''
SWTimer usage example:
    sw_timer = myF.SWTimer()        #start
    sw_timer('1')               #stopwatch
    sw_timer.close()            #del
'''

# Download the CMU Pronouncing Dictionary if you haven't already
#nltk.download('cmudict')

# Load the CMU Pronouncing Dictionary
#cmu_dict = cmudict.dict()

#stats
'''
size - 50
Capital letter - 35px
small letter - 33 in 693 - 21px
'''

#cImgPath = "img_menu_01.jpg"

dict_base = {
    'menu': "❰❰❰ ☰ Menu",
    'back': "❰ Назад",
    '<<': "❰❰❰",
    '>>': "❱❱❱",
    'native': "How'd native say? 🤔💬",
    'service': "⚙ 🎓 🆕 Other",
    'donate': "❤️ Donate",
    'learnpath': "Learning path",
    'speak': "💬 Speak",
    'repeat': "🔁 Words",
    'newsppr': "📰 News",
    'bas': "🧱 Build-a-Sentence 📝",
    'qstart': "🚀 Quick start",
    'hint': "💡 hint",
    'releasenotes': "🆕 What's new?",
    'Rep_words': "🔁 Repeat 🌟 words",
    'dia': "👥️ Dialogue", #🧍‍♂️🧍‍♂
    'mono': "🧍‍♂️ Monologue",
    'lnr': "🎧🗣️️ Listen and Repeat",
    'retell': "🔁📖️ Retelling",
    'alarm_add': "Add",
    'alarm_del': "Delete",
    'alarm_delall': "Delete all",
    'tz': "🌍 Set time zone",
    'vA_st4_2': "Let's try ❱❱",
    'vA_st3_2': "Yes, let's start ❱❱",
    'vA_st5_2': "Compare plans ❱❱",
    'fs': "⚡ Free talk",
    'finish': "Finish",
}

dict_ru = copy.deepcopy(dict_base)
dict_en = copy.deepcopy(dict_base)

#responses_rus = {
dict_ru.update(
    {
        'audText': "📃 Текст аудио",
        'dialEnd': "❎ Закончить диалог",
        'XdialEnd': "❌ Закончить диалог",
        'resume_custom': "Укажите свое резюме",
        'resume_prebuilt': "Укажите свое резюме",
        'fw': "❱❱ Далее",
        'Trans': "📃 Перевод",
        'settings': "⚙ Настройки",
        'daily': "⚡ Ежедневные задачи",
        'PickOut': "🧩 Разобрать 🌟 рекомендуемые",      #🎩 Разобрать рекомендуемые
        'oxford3': "➕📘 Добавить 20 💰 слов",
        'spd05x': "скорость 0.5х",
        'dhistory': "Текст диалога",
        'prices': "💲 Управление подпиской",
        'edu': "🎓 Обучение",
        'edu_beg': "Пройти сначала",
        'edu_end': "Второй раздел",
        'JB_txtbrk': "📃 Текст вакансии",
        'CV_txtbrk': "📃 Текст резюме",
        'dHR_custom': "Загрузите описание вакансии и резюме",
        'dHR_choose': "Выберите из существующих",
        'analysis': "Анализ текста",
        'duolang': "\n⚡<b> Вы также можете использовать русские слова, в этом случае для лучшего распознавания произносите слова более отчетливо и медленно</b>",
        'wordlist': "👀📚 Просмотреть все слова",
        'Add_words': "🎩 Добавить слова к 🌟 рекомендуемым",
        'trs_on': "Перевод",
        'trs_off': "Перевод ✅",
        'd_next': "❱❱ следующая фраза диалога 💬 ",
        'd_next_s': "❱❱ 💬 ",
        'hr': "🤝 Собеседование",
        'bas_c_f': "❌ Слова не использовались",
        'bas_c_t': "✅ Были использованы: ",
        '1more': "Еще одно задание",
        'vA_st0': "🎵 Текст аудио",
        'vA_st1': '''
📌 Шаг 2/9. На этом этапе укажи уровень английского и отметь цели изучения просто прокликав их (см hint ниже). 

После того, как закончишь, жми "✨ Done! ⚡ Let's continue ❱❱"

<blockquote expandable="true">
💡 hint

Укажи уровень английского:
🔴 A - Beginner
🟡 B - Intermediate (по умолчанию)
🟢 C - Advanced

Отметь цели изучения (можно несколько):
1️⃣ Карьера
2️⃣ Образование
3️⃣ Путешествия
4️⃣ Жизнь за границей
5️⃣ Достичь беглости
6️⃣ Погружение в культуру
</blockquote>
        ''',
        'vA_gram': '❕ Запишите ответ голосовым сообщением или введите текстом\n\nДля завершения диалога нажмите Skip',
        'vA_d_skip': '❕ Запишите ответ голосовым сообщением или введите текстом\n\nДля завершения диалога нажмите Skip',
        'vA_t_skip': '❕ Запишите ответ голосовым сообщением или введите текстом\n\nДля пропуска задания нажмите Skip',
        'fs_finish': '❕ Запишите ответ голосовым сообщением или введите текстом\n\nДля завершения нажмите Finish',
        'agrmnt': 'Договор-оферта',
        'tariff': "Проверить планы ❱❱",
        'fs_hint': '❗️ Запишите аудио или текстовый ответ в продолжение диалога',   #⚡️ Вы также можете использовать русские слова, в этом случае для лучшего распознавания произносите слова более отчетливо и медленно</b>
   }
)

dict_en.update(
    {
        'audText': "📃 Audio text",
        'dialEnd': "❎ Finish dialogue",
        'XdialEnd': "❌ Finish dialogue",
        'resume_custom': "Input your CV",
        'resume_prebuilt': "Choose your CV",
        'fw': "❱❱ Next",
        'Trans': "📃 Translation",
        'settings': "⚙ Settings",
        'daily': "⚡ Daily tasks",
        'PickOut': "🧩 Разобрать 🌟 рекомендуемые",      #🎩 Разобрать рекомендуемые
        'oxford3': "➕📘 Add 20 💰 words",
        'spd05x': "Speed 0.5х",
        'dhistory': "Dialogue text",
        'prices': "💲 Manage subscription",
        'edu': "🎓 Education",
        'edu_beg': "Start from the beginning",
        'edu_end': "Second chapter",
        'JB_txtbrk': "📃 Position description",
        'CV_txtbrk': "📃 CV",
        'dHR_custom': "Upload position description and CV",
        'dHR_choose': "Choose from existing ones",
        'analysis': "Text analysis",
        'duolang': "\n⚡<b> You can also use Russian words, in this case, for better recognition, pronounce the words more clearly and slowly</b>",
        'wordlist': "👀📚 View all words",
        'Add_words': "🎩 Add words to 🌟 recommended",
        'trs_on': "Translation",
        'trs_off': "Translation ✅",
        'd_next': "❱❱ next line of dialogue 💬 ",
        'd_next_s': "❱❱ 💬 ",
        'hr': "🤝 Job interview",
        'bas_c_f': "❌ Words not found",
        'bas_c_t': "✅ Used words: ",
        '1more': "One more",
        'vA_st0': "🎵 Audio text",
        'vA_st1': '''
Tell please your English level and why do you need English
<blockquote expandable="true">
💡 hint

Choose English level:
🟢 A - Beginner
🟡 B - Intermediate (default)
🔵 C - Advanced

Pick your goals in learning language (could be several):
1️⃣ Career & job opportunities
2️⃣ Study abroad / education
3️⃣ Travel & communication
4️⃣ Prepare for living abroad
5️⃣ Achieve fluency & sound natural
6️⃣ Enjoy culture
</blockquote>
        ''',
        'vA_gram': '❕ To continue reply with voice or text, to finish press "❱❱ Next"',
        'vA_d_skip': '❕ To continue reply with voice or text,\n\n to finish press Skip',
        'vA_t_skip': '❕ To continue reply with voice or text,\n\n to finish press Skip',
        'fs_finish': '❕ To continue reply with voice or text,\n\n to finish press Skip',
        'agrmnt': 'Service Agreement',
        'tariff': "Compare plans ❱❱",
        'fs_hint': '❗️ <b>Send an audio or text response to continue the dialogue</b>'
    }
)

dict_all = {
    'ru': dict_ru,
    'en': dict_en,
}


#function for uniform text messages     fCSS('native')
def fCSS(vMark, vLang = 'ru'):
    return dict_all.get(vLang, dict_en).get(vMark, f"[Missing: {vMark}]")


def fArrSynonyms(strIn, strOriginal):
    # предварительная обработка массива синонимов
    cleaned_string = strIn.replace('(', ',').replace(')', '').replace(';', ',').replace('.','')
    arrPrelim = cleaned_string.split(',')
    arrOut = []
    for varWord in arrPrelim:

        varWord_woSpace = ' '.join(varWord.lower().split())  # очистка от пробелов и lowercase

        tmp_Var = re.search(varWord_woSpace, strOriginal, re.IGNORECASE)  # фильтр-очистка от слов, которые использовал пользовательв речи (это не синонимы)  AJRM-оптимизировать
        if not tmp_Var:
            arrOut.append(varWord_woSpace)
    #print('arrOut = ', arrOut)

    return arrOut

async def fLemmatizeWordList(arr_Words, pool_base, vUserID, nlp_tools):
    arr_Words = [" ".join(str(word).lower().split()) for word in arr_Words] # lowercase and remove extra spaces
    print('arr_Words = ', arr_Words)
    # обработка для выделения леммы------------------
    lemmatizer = nlp_tools.lemmatizer

    #lemmatizer = WordNetLemmatizer()
    varStr2_list = []
    arrSyn2DB = []

    for word in arr_Words:
        #tagged_word = pos_tag([word])[0]
        tagged_word = nlp_tools.pos_tag([word])[0]
        #wordnet_pos = get_wordnet_pos(tagged_word[1]) or wordnet.NOUN
        wordnet_pos = get_wordnet_pos(tagged_word[1], nlp_tools) or nlp_tools.wordnet.NOUN
        lemma = lemmatizer.lemmatize(word, pos=wordnet_pos)
        v_Rus = await fDBTranslate(lemma, pool_base)  # проверка слова в БД
        flag2db = 0
        if v_Rus is None:
            v_Rus = await afGoogleTrans(lemma, pool_base, vUserID)  # gogle translate
            flag2db = 1
        arrSyn2DB.append([lemma, v_Rus, flag2db])  # Store in DB list
        varStr2_list.append(f'{lemma} - {v_Rus}\n')  # Store for user output
        # Final formatted string
    varStr2 = ''.join(varStr2_list)
    print('varStr2 - ', varStr2)
    print('arrSyn2DB - ', arrSyn2DB)
    return arrSyn2DB, varStr2


async def fProcWordList2Recommend(arrSyn2DB, pool_base, vUserID, nlp_tools):
    strQuery = ""
    strQuery2 = ""
    query_list = []  # For inserting into `tw_obj`
    query2_list = []  # For inserting into `tw_userprogress`

    for subArr in arrSyn2DB:
        vWord = " ".join(subArr[0].lower().split())  # Lowercase & remove extra spaces
        v_Rus = subArr[1]
        flag2db = subArr[2]
        # структура строк (актуальный см.ниже):
        #       1:obj_eng, obj_rus, obj_rus_alt, obj_arpa, obj_ipa, type_id
        #       2:obj_eng
        if flag2db == 1:  # If 1, generate full attributes; if 0, only `tw_userprogress` query
            #v_Rus, strAltTranslate = await fAltTranslationLLM(vWord, v_Rus, pool_base, vUserID)
            strARPA, strIPA = getTranscriptionNltk(vWord, nlp_tools)  # Get transcription with NLTK
            # Construct query string for `tw_obj`
            #query_list.append(f"('{vWord}', '{v_Rus}', '{strAltTranslate}', '{strARPA}', '{strIPA}', '1')")
            query_list.append(f"('{vWord}', '{v_Rus}', '{strARPA}', '{strIPA}', '1')")
        # Construct query string for `tw_userprogress`
        query2_list.append(f"'{vWord}'")
    # Final query strings
    if query_list:
        strQuery = ", ".join(query_list)  # Remove trailing comma issue

    if query2_list:
        strQuery2 = ", ".join(query2_list)  # Remove trailing comma issue

    print('strQuery - ', strQuery)
    print('strQuery2 - ', strQuery2)
    if strQuery:
        var_query = (
            #f"INSERT INTO tw_obj (obj_eng, obj_rus, obj_rus_alt, obj_arpa, obj_ipa, type_id) "
            f"INSERT INTO tw_obj (obj_eng, obj_rus, obj_arpa, obj_ipa, type_id) "
            f"VALUES {strQuery} ON CONFLICT (obj_eng) DO NOTHING;"
        )
        await pgDB.fExec_UpdateQuery(pool_base, var_query)
    if strQuery2:
        var_query = (
            f"INSERT INTO tw_userprogress (obj_id, userobj_id, user_id, status_id)  "
            f"SELECT obj_id, ('{vUserID}' || obj_id)::bigint, '{vUserID}', '1' "
            f"FROM tw_obj WHERE obj_eng IN ({strQuery2}) "
            f"ON CONFLICT (userobj_id) DO NOTHING"
        )
        # AJRM замерить оптимальность
        await pgDB.fExec_UpdateQuery(pool_base, var_query)
    # формирование карты слова
    for subArr in arrSyn2DB:
        vWord = " ".join(subArr[0].lower().split())  # Lowercase & remove extra spaces
        flag2db = subArr[2]
        if flag2db == 1:
            await fGenWordCard_NLTK_AI(pool_base, nlp_tools, word=vWord, vUserID=vUserID)

async def fProcessRecommendedWord(varStr, strOriginal, pool, vUserID, nlp_tools):
    pool_base, pool_log = pool
    #пример varStr - Слова рекомендуемые к изучению: [amazing, fascinating, experience, opportunity, ancient]
    varStr = varStr.split('[')[1]       #на выходе должно быть - строка - amazing, fascinating, experience, opportunity, ancient]
    varStr = varStr.split(']')[0]       #на выходе должно быть - строка - amazing, fascinating, experience, opportunity, ancient
    varArr = varStr.split(',')          #на выходе должно быть - массив - [amazing, fascinating, experience, opportunity, ancient]
    # --------------------------------------------------------------------------------------------
    arrSyn2DB, varStr2 = await fLemmatizeWordList(varArr, pool_base, vUserID, nlp_tools)

    # --------------------------------------------------------------------------------------------
    # запись синонимов в БД и обновление сообщения пользователю
    if len(arrSyn2DB) > 0:
        await fProcWordList2Recommend(arrSyn2DB, pool_base, vUserID, nlp_tools)


def fGetImg(vMark):
    python_folder = os.path.dirname(os.path.abspath(__file__))
    if vMark == 'menu':
        name = random.choice(
            [
                'img_menu_01.jpg',
                'img_menu_02.jpg',
                'img_menu_03.jpg',
                'img_menu_fencing_02.jpg',
                'img_menu_fencing_03.jpg',
                'img_menu_FGCallus_01.jpg',
                'img_menu_FGCallus_03.jpg',
                'img_menu_climb_01.jpg'
            ]
        )
        #'img_menu_FGCallus_02.jpg', 'img_menu_FGCallus_04.jpg',
    elif vMark == 'start': name = 'img_start.jpg'
    elif vMark == 'startA': name = 'img_chinese.jpg'
    elif vMark == 'speak':
        name = random.choice(
            [
                'img_speak.jpg',
                'img_speak_1.jpg'
            ]
        )
    elif vMark == 'hr':
        name = random.choice(
            [
                'img_HR_1.jpg',
                'img_HR_2.jpg',
                'img_HR_3.jpg',
                'img_HR_4.jpg'
            ]
        )
    elif vMark == 'sett': name = 'img_settings.jpg'
    #elif vMark == 'release': name = 'img_flag_britain_01.jpg'
    elif vMark == 'release': name = 'release_1.jpg'
    elif vMark == 'donate': name = 'img_robot.jpg'
    elif vMark == 'text': name = 'rn_text.jpg'
    elif vMark == 'grammar': name = 'img_grammar.jpg'
    elif vMark == 'word': name = 'img_word2.jpg'
    elif vMark == 'plans_n': name = 'img_plans_n.jpg'
    elif vMark == 'plans_d': name = 'img_plans_d.jpg'
    elif vMark == 'news':
        name = random.choice(
            [
                'img_news_01.jpg'
            ]
        )


    return os.path.join(python_folder, 'storage', 'img', name)
    #return f'{python_folder}\\storage\\img\\{name}'


def get_wordnet_pos(treebank_tag, nlp_tools):
    if treebank_tag.startswith('J'):
        return nlp_tools.wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return nlp_tools.wordnet.VERB
    elif treebank_tag.startswith('N'):
        return nlp_tools.wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return nlp_tools.wordnet.ADV
    else:
        return None

'''
def remove_extra_spaces(input_string):
    words = input_string.split()
    result = ' '.join(words)
    result = ' '.join(input_string.split())
    return result
'''


async def afDelFile(file_path):
    try:
        await asyncio.to_thread(os.remove, file_path)
        #print(f"file deleted successfully | {file_path}")
    except Exception as e:
        print(f"Error occurred while deleting file {file_path}: {e}")


def fImageAddQuote(cImgPath):
    quoteArray = [
        ["Ludwig Wittgenstein", "The limits of my language are the limits of my world"],
        ["Charlemagne", "To have another language is to possess a second soul"],
        ["Frank Smith", "Learning a new language is becoming a member of the club - the community of speakers of that language"],
        ["Benjamin Lee Whorf", "Language shapes the way we think, and determines what we can think about"],
        ["Saint Augustine", "The world is a book, and those who do not travel read only one page"],
        ["Franz Kafka", "To learn a new language is to enter a new world"],
        ["Frank Smith", "One language sets you in a corridor for life. Two languages open every door along the way"],
        ["Ahmed Deedat", "Language is the key to the heart of people"],
        ["Edmund de Waal", "With languages, you are at home anywhere"],
        ["Mark Amidon", "Language is the means of getting an idea from my brain into yours without surgery"],
        ["Rita Mae Brown", "Language is the road map of a culture. It tells you where its people come from and where they are going"],
        ["Ludwig Wittgenstein", "The limits of my language mean the limits of my world"],
        ["Nelson Mandela", "If you talk to a man in a language he understands, that goes to his head. If you talk to him in his own language, that goes to his heart"],
        ["Federico Fellini", "A different language is a different vision of life"],
        ["Henry Boye", "The most important trip you may take in life is meeting people halfway"],
        ["Tomáš Garrigue Masaryk", "The more languages you know, the more you are human"],
        ["Samuel Johnson", "Language is the dress of thought"],
        ["Oliver Wendell Holmes", "Language is the blood of the soul into which thoughts run and out of which they grow"],
        ["James Humes", "The art of communication is the language of leadership"],
        ["Geoffrey Willansa", "You can never understand one language until you understand at least two"],
        ["Winston Churchill", "Success is not final, failure is not fatal: It is the courage to continue that counts"],
        ["Theodore Roosevelt", "Believe you can and you're halfway there"],
        ["Susan Johanson", "The harder you work for something, the greater you'll feel when you achieve it"],
        ["Mark Twain", "The secret of getting ahead is getting started"],
        ["Zig Ziglar", "You don't have to be great to start, but you have to start to be great"],
        ["Lao Tzu", "The journey of a thousand miles begins with one step"],
        ["Nelson Mandela", "It always seems impossible until it's done"],
        ["Bo Bennett", "Success is not in what you have, but who you are"],
        ["Bo Jackson", "Set your goals high, and don't stop till you get there"],
        ["Arnold H. Glasow", "Success is not the result of spontaneous combustion You must set yourself on fire"],
        ["Charles Kingsleigh", "The only way to achieve the impossible is to believe it is possible"],
        ["Martin Luther King Jr.", "You don't have to see the whole staircase, just take the first step"],
        ["Confucius", "It does not matter how slowly you go as long as you do not stop"],
        ["Winston S. Churchill", "Success is stumbling from failure to failure with no loss of enthusiasm"],
    ]

    arrSingleQuote = random.choice(quoteArray)

    font_path = config.font_path
    text_color = "#860c75"
    outline_color = "white"
    outline_width = 5

    cImage = Image.open(cImgPath)
    draw = ImageDraw.Draw(cImage)

    text = arrSingleQuote[1]
    font_size = 50
    font = ImageFont.truetype(font_path, font_size)
    numStr = math.ceil(len(textwrap.wrap(text, width=27)))
    margin = 50
    gapQuoteAuthor = 50
    offset = int((500 - gapQuoteAuthor - 15 - numStr * 60) / 2)
    for line in textwrap.wrap(text, width=27):
        draw.text((margin, offset), line, font=font, fill=text_color, stroke_width=outline_width, stroke_fill=outline_color)
        offset += 60

    txtAuthor = arrSingleQuote[0]
    txtArr = txtAuthor.split(' ')
    txtArrLen = len(txtArr)
    txtLen = len(txtAuthor)
    if txtArrLen > 0:
        lettCap = txtArrLen
        lettSpace = txtArrLen - 1
        lettSmall = txtLen - lettCap - lettSpace
    else:
        lettCap = lettSpace = lettSmall = 0
        txtAuthor = ""
    txtLenPx = lettCap * 21 + lettSpace * 7 + lettSmall * 12
    margin = int(700 - txtLenPx / 2)
    offset = int((500 + gapQuoteAuthor - 15 + 60 * numStr) / 2)
    font_size = 30
    font = ImageFont.truetype(font_path, font_size)
    draw.multiline_text((margin, offset), txtAuthor, font=font, fill=text_color, stroke_width=outline_width, stroke_fill=outline_color, anchor='mm')

    python_folder = os.path.dirname(os.path.abspath(__file__))
    imgFileName = os.path.join(python_folder, 'storage', f"{str(uuid.uuid4())}.jpg")
    cImage.save(imgFileName)
    return imgFileName

async def fCalcToken(v_ModelID, v_prompt_token, v_completion_token, pool, vUserID):
    var_query = (
        f"SELECT c_balance, c_bal_token "
        f"FROM t_user "
        f"WHERE c_user_id = '{vUserID}'"
    )
    logger.info(f'AJRM - vUserID:{vUserID}|var_query:{var_query}')
    var_Arr = await pgDB.fExec_SelectQuery(pool, var_query)
    logger.info(f'AJRM - var_Arr:{var_Arr}')
    vBalance = var_Arr[0][0]
    vBalToken = var_Arr[0][1]
    if vBalance == None: vBalance = 0
    if vBalToken == None: vBalToken = 0
    #print('vBalance = ', vBalance, '|vBalToken = ', vBalToken)


    if int(v_ModelID) == 1:
        vBase = 1000000
        inPrice = 0.15/vBase         #0.5/vBase
        outPrice = 0.6/vBase        #1.5/vBase
    elif int(v_ModelID) == 2:
        vBase = 1000000
        inPrice = 5 / vBase
        outPrice = 15 / vBase
    elif int(v_ModelID) == 3:
        vBase = 60
        inPrice = 0.006 / vBase
        outPrice = 0
    elif int(v_ModelID) == 4:
        vBase = 1000000
        inPrice = 4 / vBase
        outPrice = 0
    vCost = v_prompt_token * inPrice + v_completion_token * outPrice
    vToken = -1 * vCost * 1000 / 1.888

    vTmp = vBalance + vToken
    vTmp1 = vTmp + vBalToken
    if vTmp > 0:
        vBalance = vTmp
    elif vTmp1 > 0 :
        vBalToken = vTmp + vBalToken
        vBalance = 0
    else:
        vBalToken = 0
        vBalance = vTmp1
    if vBalToken == 0: vBalToken = 'NULL'
    #print('vCost = ', vCost, '|vToken = ', vToken, '|vBalance = ', vBalance, '|vBalToken = ', vBalToken)

    var_query = (
        f"INSERT INTO t_token (c_user_id, c_prompt_token, c_completion_token, c_model, c_datetime, c_cost, c_spal_token) "
        f"VALUES ('{vUserID}', '{v_prompt_token}', '{v_completion_token}', '{v_ModelID}', CURRENT_TIMESTAMP, {vCost}, {vToken}) "
    )
    await pgDB.fExec_UpdateQuery(pool, var_query)

    #print('2')

    var_query = (
        f"UPDATE t_user "
        f"SET c_balance = {vBalance}, c_bal_token = {vBalToken} "
        f"WHERE c_user_id = '{vUserID}'"
    )
    await pgDB.fExec_UpdateQuery(pool, var_query)

    #print('3')


async def fSubMsgDel_DB_update(vUserID, pool_base, vData):
    '''
    отправление данных в БД
    '''
    # Проверка и нормализация данных
    if vData is None or vData == 'None' or vData == '':
        vData = '0'
        logging.warning(f"fSubMsgDel_DB_update: Normalized empty/None to '0' for user {vUserID}")
    else:
        vData = str(vData).strip()
        # Фильтруем 'None' из списка
        if ',' in vData:
            cleaned = [x for x in vData.split(',') if x.strip() and x.strip() != 'None']
            vData = ','.join(cleaned) if cleaned else '0'

    var_query = (
        f"UPDATE t_msg_id "
        f"SET c_msg_id = '{vData}' "
        f"WHERE c_user_id = '{vUserID}'"
    )
    await pgDB.fExec_UpdateQuery(pool_base, var_query)


async def fSubMsgDel_DB_select(vUserID, pool_base):
    '''
    получение строки из БД, перевод в массив чисел, возврат массива чисел
    '''
    var_query = (
        f"SELECT COALESCE(NULLIF(c_msg_id, ''), '0') "  # NULLIF превратит пустую строку в NULL
        f"FROM t_msg_id "
        f"WHERE c_user_id = '{vUserID}'"
    )
    try:
        var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

        # Множественные проверки
        if not var_Arr:
            logging.warning(f"fSubMsgDel_DB_select: No record for user {vUserID}")
            return '0'

        if not var_Arr[0]:
            logging.warning(f"fSubMsgDel_DB_select: Empty first element for user {vUserID}")
            return '0'

        db_msg_id = var_Arr[0][0]

        # Проверка на все варианты пустоты
        if db_msg_id is None or db_msg_id == '' or db_msg_id == 'None':
            logging.warning(f"fSubMsgDel_DB_select: Invalid db_msg_id ({db_msg_id}) for user {vUserID}, returning '0'")
            return '0'

        return str(db_msg_id)

    except Exception as e:
        logging.error(f"Error in fSubMsgDel_DB_select for user {vUserID}: {e}")
        return '0'

#fSubMsgDel(None, pool, userID, None, bot, 2)
async def fGet_delMsgNum(state: FSMContext, pool_base, vUserID):
    # получить строку (из дата или БД)
    if state is not None:
        data = await state.get_data()
        if 'delMsgNum' in data:
            delMsgNum = data['delMsgNum']
        else:
            delMsgNum = await fSubMsgDel_DB_select(vUserID, pool_base)
    else:
        delMsgNum = await fSubMsgDel_DB_select(vUserID, pool_base)

    # Множественные проверки на пустоту
    if delMsgNum is None or delMsgNum == '' or delMsgNum == 'None':
        delMsgNum = '0'
    else:
        delMsgNum = str(delMsgNum).strip()
        if delMsgNum == '' or delMsgNum == 'None':
            delMsgNum = '0'

    isNull = delMsgNum == '0'

    # Безопасное преобразование - пропускаем все что не является числом
    arr_delMsgNum = []
    for x in delMsgNum.split(','):
        x = x.strip()
        try:
            if x and x != 'None':  # Дополнительная проверка на 'None'
                arr_delMsgNum.append(int(x))
        except ValueError:
            logging.warning(f"fGet_delMsgNum: Cannot convert '{x}' to int for user {vUserID}")
            continue

    # Если массив пустой после фильтрации
    if not arr_delMsgNum:
        isNull = True

    return arr_delMsgNum, isNull


async def fSubMsgDel(state: FSMContext, pool, vUserID, p_msg_id, msg_id_cur, bot, vMark, vClient = 2, flagPrevMsgDel = True):
    '''
    1 - инициализация номера сообщения (добавить в data, БД)
    2 - добавление номера к массиву (получить массив (из дата/БД), добавить элемент, вернуть массив (дата/БД))
    3 - очистка массива сообщений (получить массив (из дата/БД), удалить сообщения, добавить новый первый элемент (дата/БД))
    '''
    pool_base, pool_log = pool

    #проверяем msg_id_cur на None
    if msg_id_cur is None:
        logging.error(f"fSubMsgDel: msg_id_cur is None for user {vUserID}, mark {vMark}")
        # Для vMark=3 это критично, для vMark=1,2 - пропускаем операцию
        if vMark == 3:
            # Получаем последний валидный msg_id
            arr_delMsgNum, isNull = await fGet_delMsgNum(state, pool_base, vUserID)
            if not isNull and arr_delMsgNum:
                msg_id_cur = arr_delMsgNum[0]
            else:
                logging.error(f"Cannot perform cleanup without valid msg_id_cur")
                return
        else:
            logging.warning(f"Skipping fSubMsgDel operation due to None msg_id_cur")
            return

    if vMark == 1:            #инициализация номеров сообщений для очистки
        await state.update_data(delMsgNum=str(msg_id_cur))        #добавление в data текущего сообщения
        await fSubMsgDel_DB_update(vUserID, pool_base, str(msg_id_cur))      #добавление в БД

    elif vMark == 2:
        #получить массив (из дата или БД)
        arr_delMsgNum, isNull = await fGet_delMsgNum(state, pool_base, vUserID)
        if isNull:
            arr_delMsgNum = [msg_id_cur]  #переопределение массива в случае 0
        else:
            if msg_id_cur not in arr_delMsgNum:
                arr_delMsgNum.append(msg_id_cur)    #добавление элемента к массиву
        #вернуть массив (дата/БД)
        arr_delMsgNum = [str(x) for x in arr_delMsgNum]     #преобразование к тексту для join
        delMsgNum = ','.join(arr_delMsgNum)                 #формирование строки для записи
        await state.update_data(delMsgNum=delMsgNum)  # добавление в data
        await fSubMsgDel_DB_update(vUserID, pool_base, delMsgNum)  # добавление в БД

    elif vMark == 3:                  #очистка
        # получить массив (из дата или БД)
        arr_delMsgNum, isNull = await fGet_delMsgNum(state, pool_base, vUserID)
        print('vMark = 3|BEFORE|arr_delMsgNum - ', arr_delMsgNum)
        if flagPrevMsgDel:
            if isNull:
                arr_delMsgNum = [p_msg_id] if p_msg_id != '' else []  #переопределение массива в случае 0
            else:
                if p_msg_id not in arr_delMsgNum and p_msg_id != '':
                    arr_delMsgNum.append(p_msg_id)    #добавление элемента к массиву. p_msg_id используется, т.к. по коду разбросаны await callback.message.delete()
        else:
            try:
                await bot.edit_message_reply_markup(chat_id=vUserID, message_id=p_msg_id, reply_markup=None)
                logger.info('is it really used?>>>>>>>>>>>>>>>>>>.')
            except Exception as e:
                print(f"⚠️ Failed to remove keyboard: {e}")
        print('vMark = 3|AFTER|arr_delMsgNum - ', arr_delMsgNum)
        #удалить сообщения
        if len(arr_delMsgNum) > 0:
            for msg_id in arr_delMsgNum:
                try:
                    print('цикл удаления элемента - ', msg_id)
                    if vClient == 1:        #remainder telephon
                        await bot.delete_messages(vUserID, msg_id)
                    else:                   #mainbot    aiogram
                        await bot.delete_message(vUserID, msg_id)
                except Exception as e:
                    print(f"Failed to delete message {msg_id}: {e}")

        #добавить новый первый элемент (дата/БД)
        if state is not None: await state.update_data(delMsgNum=str(msg_id_cur))  # добавление в data
        await fSubMsgDel_DB_update(vUserID, pool_base, str(msg_id_cur))  # добавление в БД
        #print(f'добавление в БД и ДАТА нового первого элемента - {msg_id_cur}')


#----------------------------------------------------------------------------------------------------------------------------------     DB
async def fDBTranslate(word, pool_base, vMark = 1):
    var_query = f"SELECT obj_id, obj_eng, obj_rus, obj_ipa, obj_rus_alt, obj_desc1, c_exa_ruen, c_origin, c_dict " \
                f"FROM tw_obj WHERE obj_eng = '{word}'"
    #print(var_query)
    tmp_Var = await pgDB.fExec_SelectQuery(pool_base, var_query)
    if tmp_Var:         #len(tmp_Var) > 0:
        varOut = tmp_Var[0][2]
        #varOutm2 = [varOut, tmp_Var[0][3], tmp_Var[0][4], tmp_Var[0][0], tmp_Var[0][5]]
        varOutm2 = [varOut, tmp_Var[0][3], tmp_Var[0][4], tmp_Var[0][0], tmp_Var[0][6], tmp_Var[0][7], tmp_Var[0][8]] #tmp_Var[0][5]]
        #print(varOutm2)
    else:
        varOut = None
        #varOutm2 = [None, None, None, None, None]
        varOutm2 = [None, None, None, None, None, None, None]
    var_Arr = [varOut, ]
    if vMark == 1:
        return varOut
    else:
        return varOutm2


async def afGoogleTrans(text, pool, vUserID, target_lang='ru'):
    api_key = config.GGL_API_KEY.get_secret_value()
    url = "https://translation.googleapis.com/language/translate/v2"
    params = {
        'q': text,
        'target': target_lang,
        'source': 'en',
        'key': api_key
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            response_json = await response.json()
            translated_text = response_json['data']['translations'][0]['translatedText']

            # Call token calculation
            await fCalcToken('4', len(translated_text), 0, pool, vUserID)

            return translated_text


# ---------------------------------------------------------------------------------------get Alt Translations


async def afSendMsg2AI(userPrompt, pool, vUserID, iModel=0, toggleParam = 1, systemPrompt = ''):
    tModel = 'gpt-4o-mini'  # "gpt-3.5-turbo-0125"
    idModel = 1
    if iModel == 4: tModel = "gpt-4o"; idModel = 2
    client = AsyncOpenAI()
    if toggleParam == 1:
        completion = await client.chat.completions.create(
            model=tModel,
            messages=[{"role": "user", "content": userPrompt}]
        )
    elif toggleParam == 2:
        completion = await client.chat.completions.create(
            model=tModel,
            messages=[{"role": "system", "content": systemPrompt},
                      {"role": "user", "content": userPrompt}],
            temperature=0.2,
            top_p=0.2,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            max_tokens=2000
        )
    elif toggleParam == 3:
        completion = await client.chat.completions.create(
            model=tModel,
            messages=[{"role": "system", "content": systemPrompt},
                      {"role": "user", "content": userPrompt}],
            temperature=0.7,
            max_tokens=4000  # Увеличено для больших историй
        )


    # print(completion.choices[0].message.content)
    # varToken = completion.usage
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    # print(varToken)
    # print(prompt_tokens)
    await fCalcToken(idModel, prompt_tokens, completion_tokens, pool, vUserID)

    vText = completion.choices[0].message.content
    if vText.startswith('"') and vText.endswith('"'):
        vText = vText[1:-1]

    return vText


# -----------------------------------------------------------------------------------------------------------------------------------------------NLTK f
# obtain English word transcription.
def getTranscriptionNltk(word, nlp_tools):
    """

    Args:
    word (str): The word for which transcription is required.

    Returns:
    list: A list of possible transcriptions for the input word.
    """


    word = word.lower()  # Ensure lowercase for consistency
    if word in nlp_tools.cmu_dict:
        arrARPA = nlp_tools.cmu_dict[word]  # array
        # print('word = ', word, '   |arrARPA[0] = ', arrARPA[0])
        strARPA = ':'.join(arrARPA[0])  # string
        strIPA = transformARPA_IPA(arrARPA[0])  # string
        return strARPA, strIPA
    else:
        return '', ''  # Return None if word not found in the dictionary


def transformARPA_IPA(tokens):
    # Mapping from ARPAbet to IPA
    arpabet_to_ipa = {
        'AA': 'ɑ', 'AE': 'æ', 'AH': 'ə', 'AO': 'ɔ', 'AW': 'aʊ', 'AY': 'aɪ', 'B': 'b', 'CH': 'tʃ', 'D': 'd', 'DH': 'ð',
        'EH': 'ɛ', 'ER': 'ɜː',
        'EY': 'eɪ', 'F': 'f', 'G': 'ɡ', 'HH': 'h', 'IH': 'ɪ', 'IY': 'i', 'JH': 'dʒ', 'K': 'k', 'L': 'l', 'M': 'm',
        'N': 'n', 'NG': 'ŋ',
        'OW': 'oʊ', 'OY': 'ɔɪ', 'P': 'p', 'R': 'r', 'S': 's', 'SH': 'ʃ', 'T': 't', 'TH': 'θ', 'UH': 'ʊ', 'UW': 'u',
        'V': 'v', 'W': 'w',
        'Y': 'j', 'Z': 'z', 'ZH': 'ʒ', 'AX': 'ə', 'IX': 'ɨ'
    }

    # Stress markers mapping
    stress_markers = {
        '0': '',  # Unstressed
        '1': 'ˈ',  # Primary stress
        '2': 'ˌ'  # Secondary stress
    }
    ipa_str = ''
    # tokens = arpabet_str.split()

    for token in tokens:
        # Separate the phoneme from the stress marker if present
        if token[-1].isdigit():
            phoneme = token[:-1]
            stress = token[-1]
        else:
            phoneme = token
            stress = ''

        # Convert phoneme to IPA
        ipa_phoneme = arpabet_to_ipa.get(phoneme, phoneme)  # fallback to original if not found

        # Add stress marker if present
        ipa_stress = stress_markers.get(stress, '')

        # Append to IPA string
        ipa_str += ipa_stress + ipa_phoneme

    return ipa_str


def get_word_meanings(word, nlp_tools):
    """Fetch all possible meanings and corresponding parts of speech for a given word using NLTK's WordNet."""
    meanings = {}

    for synset in nlp_tools.wordnet.synsets(word):
        pos = synset.pos()  # Get part of speech (n, v, a, r)

        # Convert WordNet POS to human-readable format
        pos_mapping = {
            'n': "Noun",
            'v': "Verb",
            'a': "Adjective",
            's': "Adjective",
            'r': "Adverb"
        }

        pos_readable = pos_mapping.get(pos, "Unknown")

        # Store meanings under the correct POS category
        if pos_readable not in meanings:
            meanings[pos_readable] = []

        meanings[pos_readable].append(synset.definition())

    return meanings


def fGetEmodjiNum(index, shape=1):
    if shape == 1:
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
    else:
        response = {
            1: '①',
            2: '②',
            3: '③',
            4: '④',
            5: '⑤',
            6: '⑥',
            7: '⑦',
            8: '⑧',
            9: '⑨'
        }

    return response.get(index)

'''
        
'''


async def fGenWordCard_NLTK_AI(pool_base, nlp_tools, word = '', vUserID = '372671079'):
    tmp_Var = [[]]

    print(f'word - |{word}|')
    if word:
        tmp_Var = [[word]]
    else:

        var_query = (
            f'SELECT obj_eng FROM public.tw_obj '
            f'ORDER BY obj_id ASC '
            # f'LIMIT 5'
        )

        '''
        var_query = (
            f'SELECT o.obj_eng '
            f'FROM public.tw_obj o '
            f'JOIN public.tw_userprogress up ON o.obj_id = up.obj_id '
            f'WHERE up.user_id = 372671079  AND up.status_id < 8 '
        )
        '''

        tmp_Var = await pgDB.fExec_SelectQuery(pool_base, var_query)
        #    tmp_Var = [['deprivate']]
        #    tmp_Var = [['ambiance']]

    strVar = ""
    update_tasks = []
    for rec_word in tmp_Var:
        v_word = rec_word[0]
        print('v_word - ', v_word)

		# Get part of speech
        meanings = get_word_meanings(v_word, nlp_tools)
        print('meanings - ', meanings)

        strVar = ""
        vDict = strVar
        if meanings == {}:
            pass        #AI запрос на формирование карточки
        else:           #формирование карточки из NLTK
            #print('             ____->>>>>>meanings - ', meanings)

            for pos, defs in meanings.items():
                #print(f"🔹 {pos}:")
                strVar += f"🔹 {pos}:\n"  # Add POS header
                for idx, definition in enumerate(defs, 1):
                    #print(f"  {idx}. {definition}")
                    strVar += f"  {idx}. {definition}\n"  # Add numbered definitions
            #v_Rus = await afGoogleTrans(strVar, pool_base, vUserID) if strVar else ""  # google перевод карточки

            vDict = strVar
            strVar = f'🔍 🇬🇧 <b>Толковый словарь:</b>\n<blockquote expandable="true">{strVar}</blockquote>'


            #strVar = f'{strVar}\n\n🔍 <b>Толковый словарь:</b>\n<blockquote expandable="true">{v_Rus}</blockquote>' if v_Rus else strVar
        prompt = myP.fPromptWordCard_AI(v_word)
        varRes = await afSendMsg2AI(prompt, pool_base, vUserID)
        vExample, vOrigin = parseWordCard(varRes)
        print('         ------------>> varRes - ', varRes)

        strVar = f'{varRes}\n\n{strVar}'

        var_query = '''
            UPDATE tw_obj 
            SET 
                c_exa_ruen = $1, 
                c_origin = $2, 
                c_dict = $3 
            WHERE obj_eng = $4 
        ''' #obj_desc1 = $1
        await pgDB.fExec_UpdateQuery_args(pool_base, var_query, vExample, vOrigin, vDict, v_word)


def parseWordCard(text):
    """
    Parse formatted text and extract content between __Example__ and __Origin__ markers.

    Args:
        text (str): Input text with __Example__ and __Origin__ sections

    Returns:
        tuple: (examples_text, origin_text)
    """

    # Pattern to match text between "__Example__" and "__Origin__"
    examples_pattern = r'__Example__\s*(.*?)(?=__Origin__)'

    # Pattern to match text from "__Origin__" to the end
    origin_pattern = r'__Origin__\s*(.*?)$'

    # Extract examples text
    examples_match = re.search(examples_pattern, text, re.DOTALL)
    examples_text = examples_match.group(1).strip() if examples_match else ""

    # Extract origin text
    origin_match = re.search(origin_pattern, text, re.DOTALL)
    origin_text = origin_match.group(1).strip() if origin_match else ""

    return examples_text, origin_text


async def fRemoveReplyKB(message_obj=None, callback_obj=None, use_telethon=False, bot=None, chat_id=None):
    """
    Remove Reply Keyboard

    Args:
        message_obj: Message object (aiogram or telethon)
        callback_obj: Callback object (aiogram only)
        use_telethon: Boolean flag to switch between aiogram and telethon
        bot: Bot instance (required for telethon)
    """

    if use_telethon:
        # Telethon implementation
        if not bot: print("Bot instance is required for telethon")
        if not chat_id: print("chat_id is required for telethon")

        # Send message with empty buttons to remove keyboard
        sent_message = await bot.send_message(
            chat_id,
            ".",
            buttons=None,  # This removes the keyboard in telethon
            parse_mode='html'
        )
        await sent_message.delete()


    else:
        if callback_obj:
            msg = await callback_obj.message.answer(".", reply_markup=ReplyKeyboardRemove())
        else:
            msg = await message_obj.answer(".", reply_markup=ReplyKeyboardRemove())
        await msg.delete()


async def getRmndrPost(vDate, pool):
    pool_base, pool_log = pool

    var_query = (
            f"SELECT t2.c_example, t2.c_true, t2.c_false1, t2.c_false2, t2.c_false3, t2.c_topic, t2.c_obj FROM t_quiz_reminder AS t1 "
            f"LEFT JOIN t_quiz AS t2 ON t2.c_id = t1.c_quiz_id "
            f"WHERE TO_CHAR(c_date, 'YYMMDD') = '{vDate}'"
    )

    var_query = (
        f"SELECT t2.c_example, t2.c_true, t2.c_false1, t2.c_false2, t2.c_false3, t3.c_desc, t2.c_obj  "
    	f"FROM t_quiz_reminder AS t1 " 
    	f"LEFT JOIN t_quiz AS t2 ON t2.c_id = t1.c_quiz_id " 
    	f"LEFT JOIN t_quiz_topic AS t3 ON t2.c_topic = t3.c_id " 
    	f"WHERE TO_CHAR(t1.c_date, 'YYMMDD') = '{vDate}'"
    )

    varRes = await pgDB.fExec_SelectQuery(pool_base, var_query)

    print('varRes - ', varRes)

    varArr = [varRes[0][0], varRes[0][1], varRes[0][2], varRes[0][3], varRes[0][4], varRes[0][5], varRes[0][6]]
    print('varArr - ', varArr)
    return varArr


async def afVoiceToTxt(message: types.Message, pool, vUserID):      #, bot: Bot
    pool_base, pool_log = pool
    python_folder = os.path.dirname(sys.executable)
    if os.path.basename(python_folder) == 'bin':
        python_folder = os.path.dirname(python_folder)
    logger.info(f'--------------------python_folder:{python_folder}')
    audio_file_path = os.path.join(python_folder, '1', f"{message.voice.file_id}.ogg")
    duration = message.voice.duration
    bot = message.bot

    try:
        await bot.download(message.voice, destination=audio_file_path)
        client = AsyncOpenAI()

        with open(audio_file_path, "rb") as audio_file:
            #audio_file = open(audio_file_path, "rb")
            strOut = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                prompt = (
                    f"The audio may contain only English and/or Russian words; Transcribe precisely each word in its own language as it was spoken"
                    f"Include any mistakes in the phrase as heard.\n"
                    f"Double check the output so that all english words are written in english alphabet and russian words are written in Cyrillic"
                    f"Output example - It was about 10 years ago. So it's kind of воспоминания."
                )
            )
        await afDelFile(audio_file_path)   #delete file
            #language = "en",

    except Exception as e:
        logger.error(f"Error in afVoiceToTxt: {e}")
        await pgDB.fExec_LogQuery(pool_log, vUserID, f"Error in afVoiceToTxt: {e}")
        return ''
    await fCalcToken('3', duration, 0, pool_base, vUserID)

    return strOut

async def fSetGrammarBuilder(toggle_dict, index_rule_pairs, state: FSMContext, switcher=False):
    builder = InlineKeyboardBuilder()
    curState = await state.get_state()
    if curState == myState.dialog.state:
        nm_Short = fCSS('d_next_s') #описание ссылки на clbck в кратком режиме
        nm_Full = fCSS('d_next')    #описание ссылки на clbck в полном режиме
        cb_next = "d_next"      #ссылка на clbck
    elif curState == myState.common.state or curState == myState.reminder.state or curState == myState.newstransOn.state or curState == myState.newstransOff.state:
        nm_Short = fCSS('back')
        nm_Full = fCSS('back')
        cb_next = "native"
    elif curState == myState.words.state:
        nm_Short = fCSS('1more')
        nm_Full = fCSS('1more')
        cb_next = "w_bas"
    elif curState == myState.varA.state:
        nm_Short = 'Skip'
        nm_Full = 'Skip'
        cb_next = "vA_st3"
    elif curState == myState.varA_bas.state:
        nm_Short = fCSS('fw')
        nm_Full = fCSS('fw')
        cb_next = "vA_st4"
    elif curState == myState.fs.state:
        nm_Short = fCSS('finish')
        nm_Full = fCSS('finish')
        cb_next = "speak"
    elif curState == myState.task8_story_active:
        nm_Short = '« Back to dialogue'
        nm_Full = '« Back to dialogue'
        cb_next = "story_gram_back"

    if index_rule_pairs != []:
        index_rule_pairs = [pair for pair in index_rule_pairs if not str(pair[0]).startswith('ℹ')]
        #print('index_rule_pairs - ', index_rule_pairs)
        for emoji_index, rule_id in index_rule_pairs:
            is_selected = toggle_dict.get(str(emoji_index), 0) == 1
            emoji = fGetEmodjiNum(int(emoji_index))
            if is_selected:
                btn_text = f"{emoji}✅"
                emoji_index = 0
                rule_id = 0
            else:
                btn_text = emoji

            callback_data = f"gram:{emoji_index};{rule_id}"
            builder.add(types.InlineKeyboardButton(text=btn_text, callback_data=callback_data))

        # Layout logic
        '''
        count = len(index_rule_pairs)
        if count < 4:
            adjust_layout = [count]
        else:
            full_rows, remainder = divmod(count, 4)
            if remainder == 0:
                adjust_layout = [4] * full_rows
            elif remainder == 1:
                adjust_layout = [4] * (full_rows - 2) + [3, 4] if full_rows >= 2 else [3, 2]
            elif remainder == 2:
                adjust_layout = [4] * full_rows + [2]
            elif remainder == 3:
                adjust_layout = [4] * full_rows + [3]
        '''

        count = len(index_rule_pairs)
        adjust_layout = []

        if count > 0:
            if count < 4:
                adjust_layout = [count]
            else:
                max_per_row = 4
                rows = math.ceil(count / max_per_row)
                base = count // rows
                remainder = count % rows  # number of rows that get one extra button

                adjust_layout = [base + 1] * remainder + [base] * (rows - remainder)

        # Optional extra buttons

        if switcher:
            builder.add(types.InlineKeyboardButton(text='↩', callback_data="gram:0;0"))             #AJRM
            builder.add(types.InlineKeyboardButton(text=nm_Short, callback_data=cb_next))
            adjust_layout = adjust_layout + [2]
        else:
            builder.add(types.InlineKeyboardButton(text=nm_Full, callback_data=cb_next))
            adjust_layout = adjust_layout + [1]
        print('adjust_layout - ', adjust_layout)
        #builder.adjust(*adjust_layout)
        if all(n > 0 for n in adjust_layout):
            builder.adjust(*adjust_layout)
        else:
            # Optional: handle the fallback layout or skip adjust entirely
            #builder.adjust(1)  # safe fallback
            pass
    else:
        builder.add(types.InlineKeyboardButton(text=nm_Full, callback_data=cb_next))


    return builder


def fShapeWordCard(lemma, v_Rus, strIPA, vExample, vOrigin, vDict):  # v_Alt    vWordCard
    transcription_str = f"      <code>[{strIPA}] </code>\n" if strIPA else ""
    # v_Alt = f'(<i>{v_Alt}</i>)' if v_Alt else ''
    v_Alt = ''

    if vExample:
        vExample = (
            f'✍️ <b>Примеры:</b>  \n'
            f'<blockquote expandable="true">{vExample}</blockquote>\n'
        )
    else:
        vExample = ''

    if vOrigin:
        vOrigin = (
            f'📜 <b>Происхождение:</b>  \n'
            f'<blockquote expandable="true">{vOrigin}</blockquote>\n'
        )
    else:
        vOrigin = ''

    if vDict:
        vDict = (
            f'🔍 🇬🇧 <b>Толковый словарь:</b>\n'
            f'<blockquote expandable="true">{vDict}</blockquote>\n'
        )
    else:
        vDict = ''

    vWordCard = f'{vDict}{vExample}'

    return (
        f"📖 <b>{lemma}</b> \n"
        f"{transcription_str}"
        f"      {v_Rus} {v_Alt}\n\n"
        f"{vWordCard}"
    )


async def afTxtToOGG(text, arrVoiceParams, settings = False):
    # print('language_code = ', arrVoiceParams[0], ' name = ', arrVoiceParams[1], ' ssml_gender = ', arrVoiceParams[2])
    # ----------------------------------------------------------------------settings
    if arrVoiceParams[2] == 'MALE':
        v_ssml_gender = texttospeech_v1.SsmlVoiceGender.MALE
    else:
        v_ssml_gender = texttospeech_v1.SsmlVoiceGender.FEMALE

    client = texttospeech_v1.TextToSpeechAsyncClient()

    input_text = texttospeech_v1.SynthesisInput(text=text)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech_v1.VoiceSelectionParams()
    voice.language_code = arrVoiceParams[0]
    voice.name = arrVoiceParams[1]
    voice.ssml_gender = v_ssml_gender

    audio_config = texttospeech_v1.AudioConfig()
    audio_config.audio_encoding = texttospeech_v1.AudioEncoding.OGG_OPUS  # Use enum instead of string
    if settings:

        audio_config.speaking_rate = 0.8  # 20% slower for better comprehension
        #audio_config.pitch = -1.0  # Slightly lower pitch (more pleasant)
        #audio_config.volume_gain_db = 1.0  # Slightly louder

    request = texttospeech_v1.SynthesizeSpeechRequest(
        input=input_text,
        voice=voice,
        audio_config=audio_config,
    )

    # ----------------------------------------------------------------------voice synthesis
    response = await client.synthesize_speech(request=request)

    # ----------------------------------------------------------------------save and return      ajarm99
    python_folder = os.path.dirname(sys.executable)
    if os.path.basename(python_folder) == 'bin':
        python_folder = os.path.dirname(python_folder)
    logger.info(f'--------------------python_folder:{python_folder}')
    audShortFlName = f"{str(uuid.uuid4())}.ogg"
    audFileName = os.path.join(python_folder, 'storage', audShortFlName)


    # The response's audio_content is binary.
    with open(audFileName, "wb") as out:
        out.write(response.audio_content)
        print(f'Audio content written to file {audFileName}')
    return audFileName#, audShortFlName


async def getSubscription_from_DB(vUserID, pool):
    pool_base, pool_log = pool

    var_query = f"""
        SELECT c_subscription_status 
        FROM t_user 
        WHERE c_user_id = {vUserID}
    """
    var_arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
    sub_stat = var_arr[0][0]
    if 0 < int(sub_stat) < 2:
        return True, sub_stat
    else:
        return False, sub_stat


def fGetAllVoices(isPremium=False):
    """
    Вернуть ВСЕ доступные голоса для распределения по NPC

    Returns:
        List of [language, voice_id, gender]
    """
    if isPremium:
        return [
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
    else:
        return [
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
            ['en-US', 'en-US-Standard-J', 'MALE']
        ]


# -----------подбор выдачи 4 вариантов для проверки
# передает запись (userID, t1.obj_id, status_id, obj_eng, obj_rus, date_repeat),
# к ней подбираются 3 варианта на англ


# получить уровень пользователя
async def fGetUserEngLevel(state: FSMContext, userID, pool_base):
    #pool_base, pool_log = pool
    englevel = ''
    englevel_num = 0
    if state:
        user_data = await state.get_data()
        englevel = user_data.get('englevel', '')        # A B C


    if not englevel:

        var_query = (
            f"SELECT c_ups_eng_level "
            f"FROM t_user_paramssingle "
            f"WHERE c_ups_user_id = '{userID}'"
        )
        tmp_Var = await pgDB.fExec_SelectQuery(pool_base, var_query)
        englevel_num = tmp_Var[0][0]
        if int(englevel_num) == 2:
            englevel = 'B'
        elif int(englevel_num) == 1:
            englevel = 'A'
        else:
            englevel = 'C'
        if state: await state.update_data(englevel=englevel)

    if not englevel_num:
        if englevel == 'A':
            englevel_num = 1
        elif englevel == 'C':
            englevel_num = 3
        else:
            englevel_num = 2
            englevel = 'B'

    return englevel_num, englevel     #numeric, string


