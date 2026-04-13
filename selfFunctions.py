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


class SWTimer:
    def __init__(self):
        self._last_time = time.perf_counter()
        print(f"[Timer started at {self._last_time:.6f}]")

    def __call__(self, label=""):
        current_time = time.perf_counter()
        elapsed = current_time - self._last_time
        self._last_time = current_time
        print(f"{label} --> Elapsed: {elapsed:.6f} seconds")

    def reset(self):
        self._last_time = time.perf_counter()
        print("[Timer reset]")

    def close(self):
        print("[Timer closed]")
        del self

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

def fCSS_old(vMark):
    if vMark == 'menu': return "❰❰❰ Меню"
    elif vMark == 'back': return "❰ Назад"
    elif vMark == 'audText': return "📃 Текст аудио"
    elif vMark == 'dialEnd': return "❎ Закончить диалог"
    elif vMark == 'XdialEnd': return "❌ Закончить диалог"
    elif vMark == 'resume_custom': return "Укажите свое резюме"
    elif vMark == 'resume_prebuilt': return "Укажите свое резюме"
    elif vMark == 'fw': return "❱❱ Далее"
    elif vMark == 'Trans': return "📃 Перевод"
    elif vMark == 'speak': return "💬 Speak"
    elif vMark == 'repeat': return "🔁 Повтор слов"
    elif vMark == 'settings': return "⚙ Настройки"
    elif vMark == 'daily': return "⚡ Ежедневные задачи"
    elif vMark == 'PickOut': return "❕ Разобрать новые слова"
    elif vMark == 'qstart': return "Quick start"
    elif vMark == 'oxford3': return "Добавить 20 слов из Oxford3000"
    elif vMark == 'spd05x': return "скорость 0.5х"
    elif vMark == 'dhistory': return "Текст диалога"
    elif vMark == 'prices': return "💲 Управление подпиской"
    elif vMark == 'edu': return "🎓 Обучение"
    elif vMark == 'edu_beg': return "Пройти сначала"
    elif vMark == 'edu_end': return "Второй раздел"
    elif vMark == 'JB_txtbrk': return "📃 Текст вакансии"
    elif vMark == 'CV_txtbrk': return "📃 Текст резюме"
    elif vMark == 'dHR_custom': return "Загрузите описание вакансии и резюме"
    elif vMark == 'dHR_choose': return "Выберите из существующих"

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
    python_folder = os.path.dirname(sys.executable)
    if os.path.basename(python_folder) == 'bin':
        python_folder = os.path.dirname(python_folder)
    logger.info(f'--------------------python_folder:{python_folder}')
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

async def vGetcMark(pool_base, parameter):
    var_query = "SELECT c_id FROM t_user_mark WHERE c_link = $1"

    try:
        var_Arr = await pgDB.fExec_SelectQuery_args(pool_base, var_query, parameter)

        # Check if any results were returned
        if var_Arr and len(var_Arr) > 0:
            vID = var_Arr[0][0]
            return vID
        else:
            return None

    except Exception as e:
        logging.error(f"Error in vGetcMark: {e}")
        return None

def vGetcMark_old(parameter):
    vMark = 0
    if parameter == 'siw73jsw':
        vMark = 6 #levshits
    elif parameter == 'emf19dyh':
        vMark = 7
    return vMark


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


def fGetCompare(A, B, boolParam=True):
    # print('{', A,'}')
    # print('{', B,'}')

    if boolParam:
        A = A.replace(',', '').replace('.', '').lower()
        B = B.replace(',', '').replace('.', '').lower()

    if A == B:
        strBool = '✅'
    else:
        strBool = '❌'

    # Create a Differ object
    differ = difflib.Differ()

    # Get the differences between the two strings
    diff = list(differ.compare(A.split(), B.split()))

    # Initialize lists to store the resulting strings with differences highlighted
    result_A = []
    result_B = []

    # Process each difference
    for item in diff:
        if item.startswith('  '):  # No change
            result_A.append(item[2:])
            result_B.append(item[2:])
        elif item.startswith('- '):  # Present in A, not in B
            result_A.append('<b>' + item[2:] + '</b>')
        elif item.startswith('+ '):  # Present in B, not in A
            result_B.append('<b>' + item[2:] + '</b>')
        elif item.startswith('? '):  # Show positions of change in the line above
            pass  # Ignore the guide lines provided by Differ

    # Join the resulting lists into strings
    result_A = ' '.join(result_A)
    result_B = ' '.join(result_B)

    return result_A, result_B, strBool

async def afDelFile(file_path):
    try:
        await asyncio.to_thread(os.remove, file_path)
        #print(f"file deleted successfully | {file_path}")
    except Exception as e:
        print(f"Error occurred while deleting file {file_path}: {e}")


def fDelFile(file_path):        #not used
    try:
        os.remove(file_path)
        #print(f"File {file_path} deleted successfully.")
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"Error occurred while deleting file {file_path}: {e}")



def fImageAddQuote(cImgPath):
    #-----------------------------------------------------------------------------------------list of quotes
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
        ["Susan Johanson​", "The harder you work for something, the greater you'll feel when you achieve it"],  
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
        ["Winston S. Churchill", "Success is stumbling from failure to failure with no loss of enthusiasm"]     
        ]

    arrSingleQuote = random.choice(quoteArray)

    #-----------------------------------------------------------------------------------------shared setting
    #font_path = r"C:\Windows\Fonts\constan.ttf"  # Specify the path to Constantia font file
    font_path = config.font_path #"/usr/share/fonts/truetype/vista/constan.ttf"
    text_color = "#860c75"  # Hex color code for text
    #text_color = "#09e4ed"  # Hex color code for text
    outline_color = "white"  # Color for outline
    outline_width = 5  # Width of the outline
    
    cImage = Image.open(cImgPath)
    draw = ImageDraw.Draw(cImage)
    #-----------------------------------------------------------------------------------------input quote to the image
    text = arrSingleQuote[1]
    font_size = 50
    font = ImageFont.truetype(font_path, font_size)
    numStr = math.ceil(len(textwrap.wrap(text, width=27)))
    margin = 50
    gapQuoteAuthor = 50
    offset = int((500 - gapQuoteAuthor - 15 - numStr*60)/2)
    for line in textwrap.wrap(text, width=27):
        draw.text((margin, offset), line, font=font, fill=text_color, stroke_width=outline_width, stroke_fill=outline_color)
        offset += 60
    #-----------------------------------------------------------------------------------------input author name to the image
    #author
    txtAuthor = arrSingleQuote[0]#"Nelson Mandela"
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
    margin = int(700-txtLenPx/2)
    offset = int((500+gapQuoteAuthor-15+60*numStr)/2)#offsetDown
    font_size = 30
    font = ImageFont.truetype(font_path, font_size)
    draw.multiline_text((margin, offset), txtAuthor, font=font, fill=text_color, stroke_width=outline_width, stroke_fill=outline_color, anchor = 'mm')
    python_folder = os.path.dirname(sys.executable)
    if os.path.basename(python_folder) == 'bin':
        python_folder = os.path.dirname(python_folder)
    logger.info(f'--------------------python_folder:{python_folder}')
    imgFileName = os.path.join(python_folder, 'storage', f"{str(uuid.uuid4())}.jpg")      #ajarm99
    #imgFileName = ''.join([str(uuid.uuid4()), ".jpg"])      #ajarm99
    #print(imgFileName)
    cImage.save(imgFileName)
    return imgFileName

#nm_img = "img_menu_01.jpg"
#vTxt = fImageAddQuote(nm_img)

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

def fGetFS1L(isPremium=False):
    if isPremium:
        list_ogg = [
            ['0f025975-70b9-47de-9507-531bfc6fecaf.ogg', ['en-AU', 'en-AU-Chirp-HD-D', 'MALE'],
             'Hi there, what would you like to chat about?'],
            ['aeb30064-3024-40d0-bd71-8db85b32fcc8.ogg', ['en-AU', 'en-AU-Chirp3-HD-Achernar', 'FEMALE'],
             'Hey, what do you want to talk about today?'],
            ['ea136b7f-77e3-4e30-8c55-15293728fd30.ogg', ['en-AU', 'en-AU-Chirp3-HD-Achird', 'MALE'],
             'Hey, what do you want to talk about today?'],
            ['6280ef67-dc79-4fbe-8f7b-2db4ddf6990c.ogg', ['en-AU', 'en-AU-Chirp3-HD-Aoede', 'FEMALE'],
             'Hey, what do you want to talk about today?'],
            ['6acc9c98-c11c-480b-ba08-33825e66361d.ogg', ['en-IN', 'en-IN-Chirp3-HD-Fenrir', 'MALE'],
             'Hi there, what would you like to chat about?'],
            ['92e1766d-7476-4e1c-937a-45b5a242911e.ogg', ['en-IN', 'en-IN-Chirp3-HD-Gacrux', 'FEMALE'],
             'Hey, what’s up? What do you wanna talk about?'],
            ['94a8a68b-4327-4069-a2ec-7583c23c489c.ogg', ['en-GB', 'en-GB-Chirp3-HD-Algenib', 'MALE'],
             'Hey, what do you want to talk about today?'],
            ['238a5b88-cae1-4985-9a1d-41c2ff147f4d.ogg', ['en-GB', 'en-GB-Chirp3-HD-Aoede', 'FEMALE'],
             'Hey! Anything you feel like talking about today?'],
            ['cabd2a1b-6574-4c08-b3d1-e845e39fa5b9.ogg', ['en-GB', 'en-GB-Chirp3-HD-Callirrhoe', 'FEMALE'],
             'Hi there, what would you like to chat about?'],
            ['15919ed0-74df-4d3d-9587-9fcc257e988b.ogg', ['en-GB', 'en-GB-Chirp3-HD-Despina', 'FEMALE'],
             'Hey! Anything you feel like talking about today?'],
            ['d4da160f-92b5-4602-b3b8-a3d542ec809d.ogg', ['en-US', 'en-US-Chirp3-HD-Achird', 'MALE'],
             'Hi there, what would you like to chat about?'],
            ['53aae568-9bdf-4dd3-9bc1-b7eaa8c1365b.ogg', ['en-US', 'en-US-Chirp3-HD-Charon', 'MALE'],
             'Hey, what’s up? What do you wanna talk about?'],
            ['98f6f977-5802-4b63-b4b4-8df49155245c.ogg', ['en-US', 'en-US-Chirp3-HD-Despina', 'FEMALE'],
             'Hey, what do you want to talk about today?'],
            ['8cd433e0-b9ec-4673-956b-7e349e3bb5a7.ogg', ['en-US', 'en-US-Chirp3-HD-Callirrhoe', 'FEMALE'],
             'Hey! Anything you feel like talking about today?'],
            ['78286915-fb7e-42d3-9ebf-03de58ddb13a.ogg', ['en-US', 'en-US-Chirp3-HD-Algieba', 'MALE'],
             'Hey! Anything you feel like talking about today?'],
            ['82fee24e-3123-4574-ad6a-882edb2defaf.ogg', ['en-US', 'en-US-Chirp3-HD-Autonoe', 'FEMALE'],
             'Hey! Anything you feel like talking about today?'],
        ]
    else:
        list_ogg = [
            ['371bdf25-847c-4d30-a29a-dbfe514ed336.ogg', ['en-AU', 'en-AU-Standard-A', 'FEMALE'],
             'Hey! Anything you feel like talking about today?'],
            ['920cc564-450c-4743-b0ca-6f133d464e11.ogg', ['en-AU', 'en-AU-Standard-B', 'MALE'],
             'Hey, what’s up? What do you wanna talk about?'],
            ['caaeb13c-d170-40a6-844c-2b593137abb0.ogg', ['en-AU', 'en-AU-Standard-C', 'FEMALE'],
             'Hey, what do you want to talk about today?'],
            ['66b6bc1e-3448-4fa8-bd66-430ed73c9a63.ogg', ['en-AU', 'en-AU-Standard-D', 'MALE'],
             'Hey! Anything you feel like talking about today?'],
            ['db0b3fa4-e7ef-4dc6-8ef8-bc06aac09d39.ogg', ['en-GB', 'en-GB-Standard-A', 'FEMALE'],
             'Hey, what’s up? What do you wanna talk about?'],
            ['fc65cb14-1f2d-47f8-9b24-54f5b08b160e.ogg', ['en-GB', 'en-GB-Standard-B', 'MALE'],
             'Hey, what do you want to talk about today?'],
            ['58ea1206-f6ad-49ee-b465-47ad04579fd2.ogg', ['en-GB', 'en-GB-Standard-C', 'FEMALE'],
             'Hey! Anything you feel like talking about today?'],
            ['e3459c31-cac7-4a83-8786-8e37e0220efb.ogg', ['en-GB', 'en-GB-Standard-D', 'MALE'],
             'Hi there, what would you like to chat about?'],
            ['9e61beab-4916-42d7-acfd-fd09017f1a7f.ogg', ['en-GB', 'en-GB-Standard-F', 'FEMALE'],
             'Hey! Anything you feel like talking about today?'],
            ['406d887d-39fb-4459-8285-6713071221a4.ogg', ['en-US', 'en-US-Standard-A', 'MALE'],
             'Hey, what’s up? What do you wanna talk about?'],
            ['0bca929a-8d67-4c78-b89d-c5e760d1bf1c.ogg', ['en-US', 'en-US-Standard-B', 'MALE'],
             'Hey, what do you want to talk about today?'],
            ['30e462cb-717a-4abd-9184-8dcffa70d6a9.ogg', ['en-US', 'en-US-Standard-C', 'FEMALE'],
             'Hey, what do you want to talk about today?'],
            ['8ee28370-3e2e-47ef-8298-b6283f13f106.ogg', ['en-US', 'en-US-Standard-D', 'MALE'],
             'Hey, what’s up? What do you wanna talk about?'],
            ['43d7d540-3839-4d27-abcc-00fda757dd50.ogg', ['en-US', 'en-US-Standard-E', 'FEMALE'],
             'Hey! Anything you feel like talking about today?'],
            ['3993bdfc-ac01-4567-8c94-056e1800f71e.ogg', ['en-US', 'en-US-Standard-F', 'FEMALE'],
             'Hey, what’s up? What do you wanna talk about?'],
            ['2e99dc22-04d7-4af6-b3fc-bc59ad39e2cc.ogg', ['en-US', 'en-US-Standard-G', 'FEMALE'],
             'Hey, what do you want to talk about today?'],
            ['ec44ee3e-cba5-4a55-897f-198478848819.ogg', ['en-US', 'en-US-Standard-H', 'FEMALE'],
             'Hey! Anything you feel like talking about today?'],
            ['618814ba-56c3-4bba-bedb-d21cd87c130a.ogg', ['en-US', 'en-US-Standard-I', 'MALE'],
             'Hey, what’s up? What do you wanna talk about?'],
            ['9a3e0ba6-5517-40d5-ab83-f26f653b40fa.ogg', ['en-US', 'en-US-Standard-J', 'MALE'],
             'Hey, what do you want to talk about today?'],
        ]
    arr_aud = random.choice(list_ogg)
    fileNm = arr_aud[0]
    python_folder = os.path.dirname(sys.executable)
    if os.path.basename(python_folder) == 'bin':
        python_folder = os.path.dirname(python_folder)
    logger.info(f'--------------------python_folder:{python_folder}')
    pathFile = os.path.join(python_folder, 'storage', 'speak', 'fs1line', fileNm)
    return pathFile, arr_aud[1], arr_aud[2]

def fGetD1L(isPremium=False):
    if isPremium:
        list_mp3 = [
            ['fe77665a-982c-4ba0-bde1-3b3a57bd117f.ogg', ['en-AU', 'en-AU-Chirp-HD-D', 'MALE'],
             "Hi! What's new since the last time we met?"],
            ['a47e4c76-b5a9-4e8c-a25a-9f455fe90a01.ogg', ['en-AU', 'en-AU-Chirp3-HD-Achernar', 'FEMALE'],
             'Hey! What’s been going on since our last chat?'],
            ['d49db2a3-fbc6-44e2-85c8-48f1a6d3c641.ogg', ['en-AU', 'en-AU-Chirp3-HD-Achird', 'MALE'],
             "Hi! What's new since the last time we met?"],
            ['8a70ed5e-e394-4ade-930d-d3bd01b98ab5.ogg', ['en-AU', 'en-AU-Chirp3-HD-Aoede', 'FEMALE'],
             "Hi! What's new since the last time we met?"],
            ['806728fc-dd51-495b-9a5e-348f97edded5.ogg', ['en-IN', 'en-IN-Chirp3-HD-Fenrir', 'MALE'],
             "Hi! What's new since the last time we met?"],
            ['f2e391ff-0dec-4a5a-ad8a-743c3f5557b8.ogg', ['en-IN', 'en-IN-Chirp3-HD-Gacrux', 'FEMALE'],
             'Hey! What’s been going on since our last chat?'],
            ['e2acb7ed-f174-4414-9b4f-c99209bec779.ogg', ['en-GB', 'en-GB-Chirp3-HD-Algenib', 'MALE'],
             'Hey! What’s been going on since our last chat?'],
            ['48687993-db2f-4d4e-b98a-3c06ce81fca2.ogg', ['en-GB', 'en-GB-Chirp3-HD-Aoede', 'FEMALE'],
             "Hi! What's new since the last time we met?"],
            ['68defa4b-4f30-4c12-bf1d-2342cbfa259b.ogg', ['en-GB', 'en-GB-Chirp3-HD-Callirrhoe', 'FEMALE'],
             'Hi! What’s been happening since we last connected?'],
            ['44400924-c9f2-45ea-a2b9-b212548dc3da.ogg', ['en-GB', 'en-GB-Chirp3-HD-Despina', 'FEMALE'],
             'Hey! What’s been going on since our last chat?'],
            ['5124e139-8e14-4734-a99b-9f8ebb537533.ogg', ['en-US', 'en-US-Chirp3-HD-Achird', 'MALE'],
             "Hi! What's new since the last time we met?"],
            ['b34ddb25-bdba-428b-9278-71d92834447b.ogg', ['en-US', 'en-US-Chirp3-HD-Charon', 'MALE'],
             'Hi! What’s been happening since we last connected?'],
            ['f4ae27f1-5fee-4db2-833b-ee4d2fc8f1d2.ogg', ['en-US', 'en-US-Chirp3-HD-Despina', 'FEMALE'],
             'Hi! What’s been happening since we last connected?'],
            ['4ac2dcd1-61ea-4451-9e3b-7b69a2d7b60f.ogg', ['en-US', 'en-US-Chirp3-HD-Callirrhoe', 'FEMALE'],
             'Hi! What’s been happening since we last connected?'],
            ['9d0afbf2-589c-473d-8277-48068d2ec833.ogg', ['en-US', 'en-US-Chirp3-HD-Algieba', 'MALE'],
             "Hi! What's new since the last time we met?"],
            ['90e5ff2e-b3b0-4090-a39a-9ede2a0a6551.ogg', ['en-US', 'en-US-Chirp3-HD-Autonoe', 'FEMALE'],
             "Hi! What's new since the last time we met?"]
        ]
    else:
        list_mp3 = [
            ['baca7d66-018e-45ec-98dd-d01330cb886d.ogg', ['en-AU', 'en-AU-Standard-A', 'FEMALE'],
             "Hi! What's new since the last time we met?"],
            ['1cbad031-9d73-4519-960b-2243f516cb3d.ogg', ['en-AU', 'en-AU-Standard-B', 'MALE'],
             'Hi! What’s been happening since we last connected?'],
            ['4e7e4eed-b463-40f1-a2db-8b9cf2acc5a1.ogg', ['en-AU', 'en-AU-Standard-C', 'FEMALE'],
             'Hi! What’s been happening since we last connected?'],
            ['18fef94d-0d6a-42dc-8223-87dc4255bcdc.ogg', ['en-AU', 'en-AU-Standard-D', 'MALE'],
             'Hi! What’s been happening since we last connected?'],
            ['f1dc522f-8e5e-4238-95a2-83a54fde3d71.ogg', ['en-GB', 'en-GB-Standard-A', 'FEMALE'],
             "Hi! What's new since the last time we met?"],
            ['0d7f6a1c-fe00-4d08-9da8-aacd03293d2d.ogg', ['en-GB', 'en-GB-Standard-B', 'MALE'],
             'Hey! What’s been going on since our last chat?'],
            ['2a96d557-ddbb-4302-88df-e3e3cbf77c30.ogg', ['en-GB', 'en-GB-Standard-C', 'FEMALE'],
             'Hi! What’s been happening since we last connected?'],
            ['be5ae519-4bda-454d-bd8a-dec84bb53dea.ogg', ['en-GB', 'en-GB-Standard-D', 'MALE'],
             'Hi! What’s been happening since we last connected?'],
            ['e0fc7c8e-938f-483b-a291-f44e4ef8a35a.ogg', ['en-GB', 'en-GB-Standard-F', 'FEMALE'],
             'Hi! What’s been happening since we last connected?'],
            ['3a005bcf-833b-4afa-b7ea-a0933ba7d1d5.ogg', ['en-US', 'en-US-Standard-A', 'MALE'],
             'Hi! What’s been happening since we last connected?'],
            ['8430a968-474c-402e-a16d-1875dc6bf81a.ogg', ['en-US', 'en-US-Standard-B', 'MALE'],
             'Hey! What’s been going on since our last chat?'],
            ['23e13607-7cce-41a5-905b-c0de1af0e902.ogg', ['en-US', 'en-US-Standard-C', 'FEMALE'],
             'Hey! What’s been going on since our last chat?'],
            ['6b9ceb2a-2f6a-40c4-8763-29ebda12319d.ogg', ['en-US', 'en-US-Standard-D', 'MALE'],
             'Hi! What’s been happening since we last connected?'],
            ['665ed1a9-23e7-431d-8e9c-880e2fbe82e1.ogg', ['en-US', 'en-US-Standard-E', 'FEMALE'],
             "Hi! What's new since the last time we met?"],
            ['cce3ac2a-1531-4faa-b79d-bbb3c09ead04.ogg', ['en-US', 'en-US-Standard-F', 'FEMALE'],
             "Hi! What's new since the last time we met?"],
            ['39c26369-accc-4443-aaf7-5351472a816e.ogg', ['en-US', 'en-US-Standard-G', 'FEMALE'],
             'Hi! What’s been happening since we last connected?'],
            ['bfa2f876-72da-4fd4-bb1c-8d60c60cb10b.ogg', ['en-US', 'en-US-Standard-H', 'FEMALE'],
             "Hi! What's new since the last time we met?"],
            ['d1390e77-4a06-462d-8dfd-49b95d11ca44.ogg', ['en-US', 'en-US-Standard-I', 'MALE'],
             'Hi! What’s been happening since we last connected?'],
            ['44e9adf0-2deb-47af-bbb8-7f2be112f750.ogg', ['en-US', 'en-US-Standard-J', 'MALE'],
             'Hi! What’s been happening since we last connected?'],
        ]


    arr_mp3 = random.choice(list_mp3)
    return arr_mp3[0], arr_mp3[1], arr_mp3[2]

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

async def afGoogleTrans_old(text, pool, vUserID, target_lang='ru'):
    api_key=config.GGL_API_KEY.get_secret_value()
    url = "https://translation.googleapis.com/language/translate/v2"
    params = {
        'q': text,
        'target': target_lang,
        'key': api_key
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            response_json = await response.json()
            translated_text = response_json['data']['translations'][0]['translatedText']
            #print(translated_text)

            await fCalcToken('4', len(translated_text), 0, pool, vUserID)

            return translated_text

    await afGoogleTrans()

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


def f_detect_language(text: str) -> str:
    """Detects whether the text is in English or Russian based on character distribution."""
    if not text.strip():
        return "unknown"  # Handle empty input

    latin_chars = re.findall(r'[a-zA-Z]', text)
    ratio = len(latin_chars) / len(text)

    return 'en' if ratio > 0.7 else 'ru'

# ---------------------------------------------------------------------------------------get Alt Translations
async def fAltTranslationLLM(word, strComp, pool, vUserID):
    prompt, systemPrompt = myP.fPromptTransAlt(word)
    var_StrX = await afSendMsg2AI(
        prompt, pool, vUserID,
        toggleParam = 2,
        systemPrompt = systemPrompt)  # send_message_to_chatgpt(prompt)  ##Format: {{English}} - (Russian) - [possible translation1, possible translation2]
    #example: var_StrX = 'летать, муха, прыжок'
    #--->>   strComp = прыжок

    #step 1. get strRu and strAlt
    print('var_StrX - ', var_StrX, '    |strComp (RU) - ', strComp)

    if not var_StrX.strip():  # Check if var_StrX is empty or only contains spaces
        return strComp, ""

    words = [word.strip() for word in var_StrX.split(',')]  # Split and remove extra spaces


    upd_words = []
    for word in words:
        wLang = f_detect_language(word)
        print('wLang - ', wLang)
        if wLang != "en":
            upd_words.append(word)
    words = upd_words


    strRu = words[0]  # First word
    # --->> strRu = 'летать'
    print('strRu - ', strRu)

    strAlt = ", ".join(words[1:]) if len(words) > 1 else ""  # Join remaining words if they exist
    # --->> strAlt = 'муха, прыжок'
    print('strAlt - ', strAlt)

    #step 2. compare with strComp to get final result
    if strRu:
        if strRu == strComp:  # если основной перевод и гугловский совпадают, то возвращаем текущий strAlt
            return strComp, strAlt
        else:  # если (основной и гугловский различаются) и (гугловский есть в альтернативных), то возвращаем основной и альтернативный ???
            if strAlt:
                arrTmp = [word.strip() for word in strAlt.split(',')]  # Remove extra spaces
                if strComp.strip() in arrTmp:  # Compare clean words
                    return strRu, strAlt
                else:  # если (основной и гугловский различаются) и (гугловского нет в альтернативных), то возвращаем гугловский, а основной добавляем к альтернативным
                    strAlt = f"{strRu}, {strAlt}"
                    return strComp, strAlt
            else:
                return strComp, strAlt

    else:
        return strComp, strAlt



async def fAltTranslationLLM_old(word, strComp, pool, vUserID):
    prompt = myP.fPromptTransAlt(word)
    var_StrX = await afSendMsg2AI(prompt, pool, vUserID)  # send_message_to_chatgpt(prompt)  ##Format: {{English}} - (Russian) - [possible translation1, possible translation2]
    #example: var_StrX = 'летать, муха, прыжок'
    #--->>   strComp = прыжок

    print('var_StrX - ', var_StrX, '    |strComp (RU) - ', strComp)

    # step 1 - get alt translations+++++++++++++++++++
    # step 1.1 - exlude last ]
    arrX = var_StrX.split(']')
    strAlt = arrX[0]  # не содержит правой ']'

    # step 1.2 - exclude [ and get alt translation
    arrX = strAlt.split('[')
    if len(arrX) > 1:  # найдена [
        if len(arrX[1]) > 1:
            strAlt = arrX[1]  # альтерн переводы найдены
        else:
            strAlt = ''  # альт переводы не найдены
    else:
        strAlt = ''  # альт переводы не найдены
    #--->> strAlt = муха, прыжок

    # step 2 get main translation++++++++++++++++++++
    # step 2.1 - exlude last )
    strRu = arrX[0]  # take left part
    arrX = strRu.split(')')  # reinit array variable and split by ). не нужно проверок, т.к. на результат не влияет найден ли )
    strRu = arrX[0]  # take left part wo )
    arrX = strRu.split('(')  # reinit array variable and split by (. нужны доп проверки на наличие (
    if len(arrX) > 1:  # найдена (
        if len(arrX[1]) > 1:
            strRu = arrX[1]  # перевод найден
        else:
            strRu = ''  # перевод не найден
    else:
        strRu = ''  # перевод не найден
    # --->> strRu = летать

    # step 3 compare with strComp to get final result
    if strRu != '':
        if strRu == strComp:  # если основной перевод и гугловский совпадают, то возвращаем текущий strAlt
            return strComp, strAlt
        else:  # если (основной и гугловский различаются) и (гугловский есть в альтернативных), то возвращаем основной и альтернативный ???
            if strAlt != '':
                arrTmp = [word.strip() for word in strAlt.split(',')]  # Remove extra spaces
                if strComp.strip() in arrTmp:    # Compare clean words
                    return strRu, strAlt
                else:  # если (основной и гугловский различаются) и (гугловского нет в альтернативных), то возвращаем гугловский, а основной добавляем к альтернативным
                    strAlt = f"{strRu}, {strAlt}"
                    return strComp, strAlt
            else:
                return strComp, strAlt

    else:
        return strComp, strAlt

async def af_tts_openai(text: str, voice: str = "onyx"):
    client = AsyncOpenAI()
    response = await client.audio.speech.create(
        model="tts-1-hd",  # или tts-1 (быстрее, дешевле)
        voice=voice,
        input=text,
        response_format="opus"  # или mp3, aac, flac
    )

    text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
    filename = f"openai_voice_{text_hash}_{voice}.ogg"

    audio_dir = Path("handlers/learnpath/audio/")
    audio_dir.mkdir(parents=True, exist_ok=True)
    filepath = audio_dir / filename

    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(response.content)

    return str(filepath)

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




async def fGrammarCheck_txt(tool, txt, pool, vUserID):
    pool_base, pool_log = pool
    max_passes = 5
    match_info_list = []
    strMistakes = ""
    strAuxMistakes = ""
    emoji_index = 1

    seen_aux_rule_ids = set()
    aux_rule_ids_to_fetch = set()
    rule_id_to_sdesc = {}
    index_rule_pairs = []
    #testMatches = []        #remove after testing

    adjusted_text = txt

    # ---------------------------------------------------LangTool part started (run I)
    #LangTool analysis runs on parsed text list
    for pass_num in range(max_passes):
        matches = tool.check(adjusted_text)
        if not matches:
            break

        matches = sorted(matches, key=lambda m: m.offset, reverse=True)

        #print('matches - ', matches)
        #testMatches = matches

        for match in matches:
            match.sentence = adjusted_text
            adj_match = get_adjusted_match(match, adjusted_text)
            adjusted_text = adj_match["adjusted"]
            match_info = {
                "ruleId": adj_match["ruleId"],
                "matchedText": adj_match["matchedText"],
                "message": adj_match["message"],
                "replacements": adj_match["replacements"],
                "wrongWord": adj_match["wrongWord"],
                "highlightedContext": adj_match["highlightedContext"],
                "offset": match.offset,
                "length": match.errorLength,
                "is_main": (pass_num == 0)
            }
            match_info_list.append(match_info)

            if pass_num == 0:
#                index_rule_pairs.append([emoji_index, adj_match["ruleId"]])
#                emoji_index += 1
                match_info["ruleId_for_index"] = adj_match["ruleId"]  # mark for emoji later
            else:
                aux_rule_ids_to_fetch.add(adj_match["ruleId"])

    # --- DB QUERY: Fetch short grammar descriptions ---
    if aux_rule_ids_to_fetch:
        rule_list_str = "', '".join(aux_rule_ids_to_fetch)
        var_query = (
            f"SELECT c_ruleid, c_sdesc FROM t_grammar "
            f"WHERE c_ruleid in ('{rule_list_str}')"
        )
        queryRes = await pgDB.fExec_SelectQuery(pool_base, var_query)
        rule_id_to_sdesc = {row[0]: row[1] for row in queryRes}

    # --- Assign emoji numbers to main matches in original order ---
    main_matches = [m for m in match_info_list if m["is_main"]]
    main_matches_sorted_by_offset = sorted(main_matches, key=lambda x: x["offset"])

    main_rule_ids = [m["ruleId_for_index"] for m in main_matches_sorted_by_offset]
    rule_list_str = "', '".join(main_rule_ids)
    var_query = (
        f"SELECT c_ruleid, c_ldesc FROM t_grammar "
        f"WHERE c_ruleid IN ('{rule_list_str}') AND c_ldesc IS NOT NULL"
    )
    queryRes = await pgDB.fExec_SelectQuery(pool_base, var_query)
    rule_ids_with_ldesc = {row[0] for row in queryRes}

    emoji_index = 1
    rule_ids_missing_desc = []

    for match in main_matches_sorted_by_offset:
        rule_id = match["ruleId_for_index"]
        if rule_id in rule_ids_with_ldesc:
            match["emoji"] = fGetEmodjiNum(emoji_index)
            index_rule_pairs.append([emoji_index, rule_id])
            emoji_index += 1
        else:
            match["emoji"] = "ℹ"
            index_rule_pairs.append(["ℹ", rule_id])
            rule_ids_missing_desc.append(rule_id)

    # --- Apply highlights in reverse offset order (to preserve positions) ---
    txt_highlighted = txt
    for match in sorted(main_matches_sorted_by_offset, key=lambda x: x["offset"], reverse=True):
        emoji = match["emoji"]
        start = match["offset"]
        end = start + match["length"]
        matched_text = txt[start:end]
        highlighted = f"<b>{emoji} {matched_text}</b>"
        txt_highlighted = txt_highlighted[:start] + highlighted + txt_highlighted[end:]

    # --- Main error explanation ---
    for match in main_matches_sorted_by_offset:
        emoji = match["emoji"]
        strMistakes += (
            f"      {emoji} "
            f"<i><b>{match['wrongWord']}</b> необходимо заменить на <b>{match['replacements']}</b></i>\n"   #||{match['ruleId']}
        )

    # --- Auxiliary explanation (with short grammar descriptions) ---
    for match in match_info_list:
        if not match["is_main"]:
            rule_id = match["ruleId"]
            if rule_id not in seen_aux_rule_ids:
                sdesc = rule_id_to_sdesc.get(rule_id, "(описание не найдено)")
                if rule_id in rule_ids_with_ldesc:
                    emoji = fGetEmodjiNum(emoji_index)
                    index_rule_pairs.append([emoji_index, rule_id])
                    emoji_index += 1
                else:
                    emoji = "ℹ"
                    index_rule_pairs.append([emoji, rule_id])
                    rule_ids_missing_desc.append(rule_id)
                strAuxMistakes += f"      {emoji} {sdesc}\n"
                seen_aux_rule_ids.add(rule_id)



                #strAuxMistakes += f"      {emoji} {sdesc}\n"
                #index_rule_pairs.append([emoji_index, rule_id])
                #seen_aux_rule_ids.add(rule_id)
                #emoji_index += 1

    if strAuxMistakes:
        strMistakes += (
            f"\n<i>Также обратите внимание:</i>\n"
            f"<i>{strAuxMistakes}</i>\n"
        )

    strKeyBPointer = ''
    strRun_I = ""
    if not index_rule_pairs:
        strRun_I = (
            f"      ✅<i>Грамматических ошибок не найдено!</i>\n"
        )

        strOrigin = txt
        strRun_I_out = txt
        var_ImprovedLine = strRun_I_out

    else:
        strDummy, strCorrect, varBool = fGetCompare(txt, adjusted_text, False)
        strRun_I = (
            #f"\n<i>Найденные неточности:</i>\n"
            f"{strMistakes}\n"
            f"<u>Промежуточная корректировка:</u>\n"
            f"<blockquote>{strCorrect}</blockquote>\n"
        )
        strKeyBPointer = f"💡 Подробнее правила смотрите по кнопкам (1️⃣...) ниже 👇"

        strOrigin = txt_highlighted
        strRun_I_out = adjusted_text
        var_ImprovedLine = strRun_I_out

    #---------------------------------------------------LangTool part finished (run I)

    # ---------------------------------------------------AI part started (run II)
    prompt = myP.fPrompt('grammar', adjusted_text, '', '', '', '')
    #print('prompt - ', prompt)
    var_AI_response = await afSendMsg2AI(prompt, pool_base, vUserID)        #{1}, {2}, [id1], [id2], [id3]  , iModel = 4
    #print('var_AI_response - ', var_AI_response)
    #parse var_AI_response by {1} X [cat1] Y [cat2] Z [cat3] W
    '''
    var_Srt = var_AI_response.split("{1}", 1)[1]        #{2}, {3}
    var_Arr = var_Srt.split("{2}", 1)                   #{3}
    strAI_adj = var_Arr[0]                             #clear
    var_Arr = var_Arr[1].split("{3}", 1)                #
    runIIdesc = var_Arr[0]                              #clear
    srtIDs = var_Arr[1]                                 #clear
    print('runIIdesc - ', runIIdesc)
    print('runIIdesc len - ', len(runIIdesc))
    print('srtIDs - ', srtIDs)
    '''
    var_Srt = var_AI_response.split("{1}", 1)[1]    # str - X [cat1] Y [cat2] Z [cat3] W {2} N
    var_Arr = var_Srt.split("[cat1]", 1)            # arr - [X , Y [cat2] Z [cat3] W  {2} N ]
    strAI_adj = " ".join(var_Arr[0].split())        #X
    var_Srt = var_Arr[1]                            #str - Y [cat2] Z [cat3] W  {2} N
    var_Arr = var_Srt.split("[cat2]", 1)             # arr - [Y , Z [cat3] W  {2} N ]
    strAI_id1 = " ".join(var_Arr[0].split())        #Y
    var_Arr = var_Arr[1].split("[cat3]", 1)          # arr - [Z , W  {2} N ]
    strAI_id2 = " ".join(var_Arr[0].split())        #Z
    var_Arr = var_Arr[1].split("{2}", 1)            #arr - [W , N ]
    strAI_id3 = " ".join(var_Arr[0].split())        #W
    strNative = " ".join(var_Arr[1].split())        #N

    #index = len(index_rule_pairs)+1       #.append([emoji_index, rule_id])
    if strAI_id1.lower() != 'none':
        strAI_id1 = f'      {fGetEmodjiNum(emoji_index)} {strAI_id1}\n'       #index
        index_rule_pairs.append([emoji_index, 'ID_PREP'])     #index
        #index = index + 1
        emoji_index += 1
    else:
        strAI_id1 = ''
    if strAI_id2.lower() != 'none':
        strAI_id2 = f'      {fGetEmodjiNum(emoji_index)} {strAI_id2}\n'       #index
        index_rule_pairs.append([emoji_index, 'ID_TENCES'])           #index
    else:
        strAI_id2 = ""
    srt_Aux = ''
    if strAI_id3.lower() != 'none': srt_Aux = f'      ℹ️{strAI_id3}\n'


    strDummy, strCorrect, varBool = fGetCompare(strRun_I_out, strAI_adj, False)
    #print('varBool - ', varBool)
    strRun_II = ""
    if varBool == '✅':          #если совпадают
        strRun_II = (
            f"      ✅<i>Грамматических ошибок не найдено!</i>\n"
        )
        strRun_II_out = strRun_I_out
        var_ImprovedLine = strRun_II_out
    else:
        strRun_II = (
            f'<i>{strAI_id1}{strAI_id2}{srt_Aux}</i>\n'                                 #runIIdesc
            f"<u>Итоговый текст:</u>\n"
            f"<blockquote>{strCorrect}</blockquote>\n"
        )
        strRun_II_out = strAI_adj
        var_ImprovedLine = strRun_II_out
        strKeyBPointer = f"💡 Подробнее правила смотрите по кнопкам (1️⃣ ...) ниже 👇"

    #strRun_II +=  strKeyBPointer
    # ---------------------------------------------------AI part finished (run II)

    # ---------------------------------------------------how d native say part start
    #print('txt - ', txt)
    #prompt = myP.fPrompt('improved', txt, '', '', '', '')  # формирование промпта
    #strNative = await afSendMsg2AI(prompt, pool_base, vUserID)  # получение текстового ответа от ИИ
    #print('strNative - ', strNative)
    strDummy, strNative, varBool = fGetCompare(strRun_II_out, strNative, False)
    # ---------------------------------------------------how d native say part finished

    str_Msg = (
        f'🔍 Ниже <b>анализ</b> Вашего сообщения\n\n'
        f'<u>Первоначальная фраза:</u>\n'
        f'<blockquote>{strOrigin}</blockquote>\n\n'
        f'❱❱ Первый проход\n'
        f'{strRun_I}\n'
        f'❱❱ Второй проход\n'
        f'{strRun_II}\n\n'
        f'<u>{fCSS("native")}</u>:\n'
        f'<blockquote>{strNative}</blockquote>\n\n'
        f'{strKeyBPointer}'
    )

    '''
    # --- Generate comma-separated string of all rule_ids ---
    all_rule_ids = [rule_id for _, rule_id in index_rule_pairs]
    strRuleIDs = ", ".join(all_rule_ids)
    print("🔍 All Rule IDs:", strRuleIDs)
    await pgDB.fExec_LogQuery(pool_log, vUserID, f'{strRuleIDs}', 4)
    '''

    if rule_ids_missing_desc:
        #print('rule_ids_missing_desc - ', rule_ids_missing_desc)
        strRuleIDs_missing = ", ".join(rule_ids_missing_desc)
        await pgDB.fExec_LogQuery(pool_log, vUserID, strRuleIDs_missing, 4)
        #await pgDB.fExec_LogQuery_test(pool_log, vUserID, varRes, testText, output, match.ruleId, 4)

    #print('index_rule_pairs - ', index_rule_pairs)

    return str_Msg, index_rule_pairs, var_ImprovedLine      #, testMatches     #matches - later remove from return





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

def get_adjusted_match(match_obj, sentence):
    """Apply a correction to the sentence and return match info + adjusted version."""
    replacements = match_obj.replacements
    offset = match_obj.offset
    error_length = match_obj.errorLength

    # Extract the wrong word
    wrong_word = sentence[offset:offset + error_length]

    # Extract up to 7 characters before and after
    start = max(0, offset - 7)
    end = min(len(sentence), offset + error_length + 7)
    context_with_highlight = (
            sentence[start:offset] +
            "<b>" + wrong_word + "</b>" +
            sentence[offset + error_length:end]
    )

    if replacements:
        adjusted = sentence[:offset] + replacements[0] + sentence[offset + error_length:]
    else:
        adjusted = sentence

    match_data = {
        "index": match_obj.offset,
        "ruleId": match_obj.ruleId,
        "matchedText": match_obj.context,
        "message": match_obj.message,
        "replacements": replacements if replacements else None,
        "wrongWord": wrong_word,
        "highlightedContext": context_with_highlight,
        "adjusted": adjusted
    }
    return match_data


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




async def fGetNewsQuery(pool_base, vLevel, offset=0, limit=4, s_reminder = 1):
    if s_reminder == 1:
        var_query = (
            f"SELECT t1.c_title, t1.c_id, t1.c_summary, t2.c_emoji, t1.c_date, t1.c_title_ru "
            f"FROM t_news AS t1 LEFT JOIN t_news_topic AS t2 ON t1.c_topic = t2.c_id "
            f"WHERE c_englvl = {vLevel} "
            f"ORDER BY c_id DESC "
            f"LIMIT {limit} + 1  OFFSET {offset}"
        )
    elif s_reminder == 3:
        var_query = (
            f"SELECT t1.c_title, t1.c_id, t1.c_summary, t2.c_emoji, t1.c_date, t1.c_title_ru "
            f"FROM t_news AS t1 LEFT JOIN t_news_topic AS t2 ON t1.c_topic = t2.c_id "
            f"WHERE c_englvl = {vLevel} AND (c_reminder_sp IS DISTINCT FROM 1) "
            f"ORDER BY c_id DESC "
            f"LIMIT {limit} + 1  OFFSET {offset}"
        )
    else:
        var_query = (
            f"SELECT t1.c_title, t1.c_id, t1.c_summary, t2.c_emoji, t1.c_date, t1.c_title_ru "
            f"FROM t_news AS t1 LEFT JOIN t_news_topic AS t2 ON t1.c_topic = t2.c_id "
            f"WHERE c_englvl = {vLevel} AND (c_reminder IS DISTINCT FROM 1) "
            f"ORDER BY c_id DESC "
            f"LIMIT {limit} + 1  OFFSET {offset}"
        )
    var_Arr = await pgDB.fExec_SelectQuery(pool_base, var_query)
    isNext = len(var_Arr) > limit
    return var_Arr[:limit], isNext

async def set_news_reminded(pool_base, v_id):


    var_query = '''
        UPDATE t_news 
        SET 
            c_reminder = 1 
        WHERE c_id = $1
    '''
    await pgDB.fExec_UpdateQuery_args(pool_base, var_query, v_id)

async def set_news_reminded_sp(pool_base, v_id):


    var_query = '''
        UPDATE t_news 
        SET 
            c_reminder_sp = 1 
        WHERE c_id = $1
    '''
    await pgDB.fExec_UpdateQuery_args(pool_base, var_query, v_id)

async def fGetLearnWords(vUserID, pool_base, num_words=5):
    vWords = ''
    var_query = (
        f"SELECT t2.obj_eng, t2.obj_rus "
        f"FROM tw_userprogress AS t1 LEFT JOIN tw_obj AS t2 ON t1.obj_id = t2.obj_id "
        f"WHERE user_id = {vUserID} AND status_id < 8 AND status_id > 1 "
        f"ORDER BY RANDOM() "
        f"LIMIT {num_words}"
    )
    queryRes = await pgDB.fExec_SelectQuery(pool_base, var_query)
    bFlag = False
    if queryRes is not None:
        if len(queryRes) > 0:
            vOut = ''
            print(queryRes)

            for v in queryRes:
                vOut = f'{vOut} <b>{v[0]}</b> ({v[1]}), '
            vWords = vOut[:-2]
        else:
            bFlag = True
    else:
        bFlag = True
    if bFlag:
        vWords = random.choice(
            [
                'cat (кот), book (книга), sun (солнце), chair (стул)',
                'tree (дерево), milk (молоко), ball (мяч), bed (кровать)',
                'bird (птица), bread (хлеб), water (вода), pen (ручка)',
                'fish (рыба), table (стол), sky (небо), hand (рука)',
                'dog (собака), apple (яблоко), house (дом), car (машина)',
                'flower (цветок), clock (часы), door (дверь), shoe (туфля)',
                'horse (лошадь), hat (шляпа), tree (дерево), cup (чашка)',
                'milk (молоко), cheese (сыр), egg (яйцо), bread (хлеб)',
                'school (школа), book (книга), desk (парта), bag (сумка)',
                'journey (поездка), village (деревня), bridge (мост), river (река)',
                'clever (умный), brave (смелый), lazy (ленивый), polite (вежливый)',
                'borrow (одолжить), lend (дать взаймы), spend (тратить), save (копить)',
                'forest (лес), mountain (гора), island (остров), desert (пустыня)',
                'promise (обещание), secret (секрет), decision (решение), advice (совет)',
                'angry (злой), excited (взволнованный), worried (обеспокоенный), proud (гордый)',
                'accident (несчастный случай), traffic (движение), passenger (пассажир), ticket (билет)',
                'illness (болезнь), medicine (лекарство), pain (боль), health (здоровье)',
                'freedom (свобода), danger (опасность), power (сила), success (успех)',
                'appear (появляться), disappear (исчезать), improve (улучшать), fail (провалиться)',
            ]
        )

    return vWords

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

def get_address2user(first_name):
    return f"👋 {random.choice(['Hi', 'Hey'])} <b>{first_name}</b>!"

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



async def afTxtToMp3(text, arrVoiceParams):
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
    #audio_config.audio_encoding = texttospeech_v1.AudioEncoding.OGG_OPUS  # Use enum instead of string
    audio_config.audio_encoding = "MP3"

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
    audFileName = os.path.join(python_folder, 'storage', f"{str(uuid.uuid4())}.mp3")
    # audFileName = ''.join([str(uuid.uuid4()), ".mp3"])
    # The response's audio_content is binary.
    with open(audFileName, "wb") as out:
        out.write(response.audio_content)
        print(f'Audio content written to file {audFileName}')
    return audFileName

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

def detect_gender(name, gender_detector):
    """
    Detect gender and return the name part used for detection

    Returns:
        tuple: (gender, relevant_name)
        - For single names: (gender, cleaned_name_with_preserved_case)
        - For composite names: (gender, subname_that_determined_gender_with_preserved_case)
        - For unknown gender: ('unknown', original_name)
    """
    # Clean and split the name
    clrName = re.sub(r'[^a-zA-Zа-яА-ЯёЁ ]', '', name)
    name_parts = [part.strip() for part in clrName.split() if part.strip()]

    if not name_parts:
        return 'unknown', name

    # If single word, use simple detection
    if len(name_parts) == 1:
        gender_result = detect_gender_simple(name_parts[0],gender_detector)
        if gender_result == 'unknown':
            return 'unknown', name  # Return original name
        else:
            # Return cleaned name with ONLY first letter capitalized, preserve rest
            cleaned_name = name_parts[0][0].upper() + name_parts[0][1:]
            return gender_result, cleaned_name

    # For composite names, check each part and find the one that determines gender
    part_results = []

    for part in name_parts:
        part_gender = detect_gender_simple(part, gender_detector)
        if part_gender not in ['unknown', 'unisex']:
            part_results.append({'part': part, 'gender': part_gender})

    # If no parts have known gender
    if not part_results:
        return 'unknown', name

    # Count male and female results
    male_parts = [p for p in part_results if p['gender'] == 'male']
    female_parts = [p for p in part_results if p['gender'] == 'female']

    if male_parts and female_parts:
        # Both male and female -> return female (as per rules)
        # Return the first female part found
        relevant_name = female_parts[0]['part']
        cleaned_name = relevant_name[0].upper() + relevant_name[1:]  # Preserve case!
        return 'female', cleaned_name
    elif male_parts:
        # Return the first male part found
        relevant_name = male_parts[0]['part']
        cleaned_name = relevant_name[0].upper() + relevant_name[1:]  # Preserve case!
        return 'male', cleaned_name
    elif female_parts:
        # Return the first female part found
        relevant_name = female_parts[0]['part']
        cleaned_name = relevant_name[0].upper() + relevant_name[1:]  # Preserve case!
        return 'female', cleaned_name
    else:
        return 'unknown', name


def detect_gender_simple(name, gender_detector):
    """Simple gender detection with Russian name patterns"""
    # Clean the name but preserve case for gender.Detector()
    clrName = re.sub(r'[^a-zA-Zа-яА-ЯёЁ ]', '', name)  # Keep spaces for splitting

    # Capitalize ONLY first letter, preserve the rest
    if clrName:
        clrName_capitalized = clrName[0].upper() + clrName[1:]  # Don't lowercase the rest!
    else:
        return 'unknown'

    # Try Latin names first with properly capitalized name
    latin_result = gender_detector.get_gender(clrName_capitalized)
    if latin_result not in ['unknown', 'andy']:
        return latin_result

    # Convert to lowercase ONLY for pattern matching, not for final result
    clrName_lower = clrName.lower()

    # Manual mapping for common ambiguous names (check against lowercase)
    name_mapping = {
        'женя': 'unisex', 'саша': 'unisex', 'валя': 'unisex',
        'елена': 'female', 'лейла': 'female', 'алекс': 'male', 'олежа': 'male',
        'ольга': 'female', 'оля': 'female', 'анна': 'female', 'аня': 'female',
        'мария': 'female', 'маша': 'female', 'дмитрий': 'male', 'дима': 'male',
        'александр': 'male', 'владимир': 'male', 'сергей': 'male', 'андрей': 'male',
        'михаил': 'male', 'миша': 'male', 'иван': 'male', 'ваня': 'male',
        'петр': 'male', 'петя': 'male', 'наталья': 'female', 'наташа': 'female',
        'светлана': 'female', 'света': 'female', 'ирина': 'female', 'ира': 'female',
        'екатерина': 'female', 'катя': 'female', 'юлия': 'female', 'юля': 'female',
        'алена': 'female', 'алёна': 'female', 'майра': 'female', 'yulia': 'female',
    }

    if clrName_lower in name_mapping:
        return name_mapping[clrName_lower]

    # Russian name ending patterns (check against lowercase)
    if re.search(r'[а-яё]', clrName_lower):
        # Definitely female endings
        if clrName_lower.endswith(('на', 'ра', 'ла', 'та', 'да', 'ка', 'га', 'ша', 'ща', 'ля', 'ня', 'ся')):
            return 'female'
        elif clrName_lower.endswith(('ия', 'ья', 'ея')):
            return 'female'
        elif clrName_lower.endswith('а') and len(clrName_lower) > 2:
            return 'female'

        # Definitely male endings
        elif clrName_lower.endswith(('ич', 'ей', 'ай', 'ий', 'ой', 'ын', 'ин', 'он', 'ан', 'ен')):
            return 'male'
        elif clrName_lower.endswith(
                ('р', 'л', 'н', 'м', 'к', 'т', 'd', 'с', 'в', 'з', 'ь', 'й')) and not clrName_lower.endswith('ль'):
            return 'male'

    return 'unknown'

def fRemoveLastBadSymbol(strA):
    # print('fRemoveLastBadSymbol - 1 - ', strA, ']')
    if len(strA) > 0:
        strA = strA.strip()
        # print('fRemoveLastBadSymbol - 2 - ', strA, ']')
        lastChar = strA[-1:]
        # print('fRemoveLastBadSymbol - 3 - ', lastChar, ']')
        if lastChar == '.': strA = strA[:-1]
        lastChar = strA[-2:]
        # print('fRemoveLastBadSymbol - 4 - ', lastChar, ']')
        if lastChar == '\n': strA = strA[:-2]
        strA = strA.replace(',', '')
        strA = strA.replace('.', '')
        strA = strA.replace("'", "’")
        strA = strA.lower()

    return strA


def generate_random_time():
    # Define start and end times
    start_time = datetime.strptime("09:00", "%H:%M")
    end_time = datetime.strptime("22:00", "%H:%M")

    # Calculate the time difference in seconds
    time_delta = end_time - start_time
    total_seconds = time_delta.total_seconds()

    # Generate a random number of seconds to add
    random_seconds = random.randint(0, int(total_seconds))

    # Add the random number of seconds to the start time
    random_time = start_time + timedelta(seconds=random_seconds)

    # Format the time as "%H:%M"
    return random_time.strftime("%H:%M")


def fCheckWords_BAS(text, words, nlp):
    # if words is a comma-separated string → turn into list
    if isinstance(words, str):
        words = [w.strip() for w in words.split(",") if w.strip()]

    # remove <b> and </b> tags
    words = [re.sub(r"</?b>", "", w) for w in words]

    # extract only the part before '(' for each word
    words = [re.split(r"\s*\(", w)[0].strip() for w in words]

    print(words)
    print(text)
    # process text
    doc = nlp(text.lower())
    lemmas = {token.lemma_ for token in doc}

    # compare using lemmatized forms
    result = []
    for w in words:
        lemma = nlp(w.lower())[0].lemma_
        if lemma in lemmas:
            result.append(w.strip())  # return original word, not lemma
    vOutput = fCSS('bas_c_f')
    if result:
        vOutput = f"{fCSS('bas_c_t')}" + ', '.join(result)
    return vOutput



def fProcessArr_News(arrText, arrTrans):
    # очистка от нумерации       очистка от нулевых записей
    # ------------------------------------------------------------------------------------------------------------------------
    subArr = []
    for vParagraph in arrText:
        if len(vParagraph) > 1: vParagraph = vParagraph.split('. - ')[1]  # очистка от нумерации
        if len(vParagraph) > 1: subArr.append(vParagraph)  # очистка от нулевых записей

    # print('--------------------------arrText')
    # print(subArr)
    arrText = subArr  # переопределение диапазона текста для исключения нумерации

    subArr = []
    for vParagraph in arrTrans:
        if len(vParagraph) > 1: vParagraph = vParagraph.split('. - ')[1]  # очистка от нумерации
        if len(vParagraph) > 1: subArr.append(vParagraph)  # очистка от нулевых записей
    # print('--------------------------arrTrans')
    # print(subArr)
    arrTrans = subArr  # переопределение диапазона перевода для исключения нумерации

    # разделение на страницы
    # ------------------------------------------------------------------------------------------------------------------------
    arrPages_Txt = []
    arrCurPage_Txt = []
    vCurLen_Txt = 0
    arrPages_Trans = []
    arrCurPage_Trans = []

    '''
    for i, text in enumerate(arrText):
        arrCurPage_Txt.append(text)
        arrCurPage_Trans.append(arrTrans[i])
        vCurLen_Txt += len(text)

        # Ensure at least 4 elements in a group before checking length condition
        if len(arrCurPage_Txt) >= 4 and vCurLen_Txt >= 1000:
            arrPages_Txt.append(arrCurPage_Txt)
            arrPages_Trans.append(arrCurPage_Trans)
            arrCurPage_Txt = []
            arrCurPage_Trans = []
            vCurLen_Txt = 0

    # Add the remaining elements if any
    if arrCurPage_Txt:
        arrPages_Txt.append(arrCurPage_Txt)
        arrPages_Trans.append(arrCurPage_Trans)
    '''
    # print('arrPages_Txt - ', arrPages_Txt)

    for i, text in enumerate(arrText):
        # Ensure at least 4 elements in a group before checking length condition
        if len(arrCurPage_Txt) + 1 >= 4 and vCurLen_Txt + len(text) >= 1000:
            if text.startswith("<b>"):
                arrPages_Txt.append(arrCurPage_Txt)
                arrPages_Trans.append(arrCurPage_Trans)
                arrCurPage_Txt = [text]
                arrCurPage_Trans = [arrTrans[i]]
                vCurLen_Txt = len(text)
            else:
                arrCurPage_Txt.append(text)
                arrCurPage_Trans.append(arrTrans[i])
                arrPages_Txt.append(arrCurPage_Txt)
                arrPages_Trans.append(arrCurPage_Trans)
                arrCurPage_Txt = []
                arrCurPage_Trans = []
                vCurLen_Txt = 0

        else:
            arrCurPage_Txt.append(text)
            arrCurPage_Trans.append(arrTrans[i])
            vCurLen_Txt += len(text)

    # Add the remaining elements if any
    if arrCurPage_Txt:
        arrPages_Txt.append(arrCurPage_Txt)
        arrPages_Trans.append(arrCurPage_Trans)

    return arrPages_Txt, arrPages_Trans


def fShapeNews1Page(vDate, vTitle, vTitle_ru, vCnt, num, vWeb, str_Msg):
    return (
            (f"<i>{vDate}</i>\n" if vDate else "")
            + (f"<b>{vTitle}</b>\n" if vTitle else "")
            + (f"<i>{vTitle_ru}</i>\n" if vTitle_ru else "")
            + (f"<i>{vCnt + 1}/{num}</i>\n" if vTitle else f"🕊️ <i>{vCnt + 1}/{num}</i> ❧ ⌘ ✧ ✤ ❖ ❈ ☙ ✨ \n\n")
            + (f'<b>Оригинал статьи <a href="{vWeb}">здесь</a></b>\n\n' if vWeb else "")
            + f"{str_Msg}\n"
            + f"<i>{vCnt + 1}/{num}</i>\n"
    )


async def getSubscription(state: FSMContext, vUserID, pool):
    pool_base, pool_log = pool
    user_data = await state.get_data()
    sub_stat = user_data.get('sub_stat', None)
    if sub_stat is not None:
        if 0 < int(sub_stat) < 2:
            return True, sub_stat
        else:
            return False, sub_stat

    is_premium, sub_stat = await getSubscription_from_DB(vUserID, pool)
    await state.update_data(sub_stat=sub_stat)
    return is_premium, sub_stat


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

def parse_ai_fs_response(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse AI teacher response into corrections and teacher parts.

    Args:
        text: Input text containing {Corrections}: and {Teacher}: sections

    Returns:
        Tuple of (corrections_text, teacher_text). Returns (None, None) if parsing fails.

    Examples:
        >>> input_text = "{Corrections}: That's exciting! Just a small correction...\\n{Teacher}: Happy birthday! Do you have..."
        >>> corrections, teacher = parse_teacher_response(input_text)
        >>> print(corrections)  # "That's exciting! Just a small correction..."
        >>> print(teacher)      # "Happy birthday! Do you have..."
    """

    # Clean up the input text
    text = text.strip()

    # Pattern to match {Corrections}: and {Teacher}: sections
    # This handles both with and without curly braces around labels
    corrections_pattern = r'(?:\{Corrections\}:?|Corrections:)\s*(.*?)(?=\{Teacher\}:?|Teacher:|$)'
    teacher_pattern = r'(?:\{Teacher\}:?|Teacher:)\s*(.*?)$'

    corrections_match = re.search(corrections_pattern, text, re.DOTALL | re.IGNORECASE)
    teacher_match = re.search(teacher_pattern, text, re.DOTALL | re.IGNORECASE)

    corrections_text = None
    teacher_text = None

    if corrections_match:
        corrections_text = corrections_match.group(1).strip()
        # Remove any trailing newlines or whitespace
        corrections_text = re.sub(r'\s*\n\s*$', '', corrections_text)

    if teacher_match:
        teacher_text = teacher_match.group(1).strip()
        # Remove any trailing newlines or whitespace
        teacher_text = re.sub(r'\s*\n\s*$', '', teacher_text)

    return corrections_text, teacher_text


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


def fGenerateVoiceParams(isPremium=False):
    """Legacy функция - вернуть один рандомный голос"""
    return random.choice(fGetAllVoices(isPremium))


# -----------подбор выдачи 4 вариантов для проверки
# передает запись (userID, t1.obj_id, status_id, obj_eng, obj_rus, date_repeat),
# к ней подбираются 3 варианта на англ
async def fArrChoiceGen(arr_Repeat, var_Cnt, pool_base):
    # global db_name
    try:
        # ------------gp_ReviewArray в итоге хранит массив 4х элементов obj_id
        arr_Out = []
        var_query = (
            f"SELECT obj_eng "
            f"FROM tw_obj "
            f"WHERE obj_id <> '{arr_Repeat[var_Cnt][1]}' "
            f"ORDER BY RANDOM() "
            f"LIMIT 3;"
        )
        # connection = create_connection(db_name)
        tstArray = await pgDB.fExec_SelectQuery(pool_base, var_query)  # execute_query(connection, var_query)
        # print('tstArray = ', tstArray)
        # print('count = ', var_Cnt,' arr_Repeat[var_Cnt][1] = ', arr_Repeat[var_Cnt][1], ' arr_Repeat[var_Cnt][3] = ', arr_Repeat[var_Cnt][3])
        s = []
        for a in tstArray:
            s.append(a[0])
        s.append(arr_Repeat[var_Cnt][3])
        arr_Out = s
        random.shuffle(arr_Out)
        print('arr_Out = ', arr_Out)
        return arr_Out

    except Error as e:
        logger.error(f"The error '{e}' occurred")


def getDateRepeatShift(var_status_id):
    if var_status_id == 1:
        return "CURRENT_DATE"
    elif var_status_id == 2:
        return "CURRENT_DATE + INTERVAL '1 days'"
    elif var_status_id == 3:
        return "CURRENT_DATE + INTERVAL '3 days'"
    elif var_status_id == 4:
        return "CURRENT_DATE + INTERVAL '5 days'"
    elif var_status_id == 5:
        return "CURRENT_DATE + INTERVAL '8 days'"
    elif var_status_id == 6:
        return "CURRENT_DATE + INTERVAL '15 days'"
    elif var_status_id == 7:
        return "CURRENT_DATE + INTERVAL '31 days'"


def getRandomEmoji(varMood):
    varOut = ''
    if varMood == 'cheer':
        arrEmoji = ['😀', '😆', '😁', '🤗', '🤓', '🤩']
        varOut = random.choice(arrEmoji)
    if varMood == 'sad':
        arrEmoji = ['😒', '😕', '😔', '😟', '😞']
        varOut = random.choice(arrEmoji)
    if varMood == 'wd':
        arrEmoji = ['🤝', '👍', '👏']
        varOut = random.choice(arrEmoji)
    return varOut + ' '


async def f_setDaily(vElement, vUserID, pool_base):

    # dictDailyLimit = {'c_pick_out':1, 'c_repeat':1, 'c_lnr':7, 'c_retell':2, 'c_dial_news':1, 'c_dial_situation':2, 'c_monolog':1}
    # проверка статусов
    var_query = (
        f"SELECT c_user_id, c_date, {vElement} FROM t_daily WHERE c_user_id = '{vUserID}'"
    )
    # connection = myDB.create_connection()
    resQuery = await pgDB.fExec_SelectQuery(pool_base, var_query)  # myDB.execute_query(connection, var_query)
    vDateToday = date.today().strftime("%Y%m%d")
    vSetNum = resQuery[0][2] + 1
    var_query = (
        f"UPDATE t_daily "
        f"SET c_date = '{vDateToday}', {vElement} = '{vSetNum}' "
        f"WHERE c_user_id = '{vUserID}'"
    )
    # connection = myDB.create_connection()
    # execute_insert_query(connection, var_query)
    await pgDB.fExec_UpdateQuery(pool_base, var_query)


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



def f______________________dummy():
    pass

def fMsgWidth(cStr):
    cStr = (
        f"{cStr} \n"
        f"                                                                                                                    ."
    )
    return cStr

def getTrainingQuest(vCat, vLevel):

    responses = {
        'A': {
            '20': [
                "Что означает слово:",
                [
                    ["Happy", "Joyful", "Sad", "Angry", "Tired"]
                ]
            ],
            '40': [
                "Укажите синоним для:",
                [
                    ["Big", "Huge", "Small", "Short", "Narrow"]
                ]
            ],
            '60': [
                "Укажите антоним для",
                [
                    ["Difficult", "Easy", "Hard", "Strong", "Weak"]
                ]
            ],
            '80': [
                "Подберите пропущенное слово, которое лучше подходит по смыслу.",
                [
                    ["The lecture was so __________ that everyone was asleep by the end.", "Boring", "Exciting", "Loud", "Funny"]
                ]
            ],
            '100': [
                "Укажите синоним для:",
                [
                    ["Meticulous", "Precise", "Careless", "Quick", "Lazy"]
                ]
            ]
        },
        'B': {
            '20': [
                "Укажите корректное предложение",
                [
                    ["", "He goes to school every day", "He go to school every day", "He going to school every day", "He went to the school every day"]
                ]
            ],
            '40': [
                "Укажите пропущенное слово",
                [
                    ["We _________ watching a movie right now", "are", "is", "am", "were"]
                ]
            ],
            '60': [
                "Укажите корректное предложение",
                [
                    ["", "If I see her, I will tell her the truth", "If I will see her, I will tell her the truth", "If I saw her, I will tell her the truth", "If I see her, I would tell her the truth"]
                ]
            ],
            '80': [
                "Укажите, какое предложение корректно переформулировано в пассивном залоге/passive voice?",
                [
                    ["The chef cooked a delicious meal", "A delicious meal was cooked by the chef", "The chef was cooked by a delicious meal", "A delicious meal is cooked by the chef", "A delicious meal has been cooked by the chef"]
                ]
            ],
            '100': [
                "Укажите корректное предложение",
                [
                    ["", "Each of the students is required to submit their assignments by tomorrow", "Each of the students were required to submit their assignments by tomorrow", "Each of the student are required to submit their assignments by tomorrow", "Each of the students is required to submit his assignment by tomorrow"]
                ]
            ]
        },
        'C': {
            '20': [
                "Прочтите текст и выберите вариант ответа на вопрос:",
                [
                    ["<blockquote>Anna has a dog named Max. Every morning, Anna takes Max for a walk in the park.</blockquote>\n\nWhat does Anna do every morning?", "Takes her dog for a walk", "Goes shopping", "Watches TV", "Takes her cat for a walk"]
                ]
            ],
            '40': [
                "Прочтите текст и выберите вариант ответа на вопрос:",
                [
                    ["<blockquote>Tom enjoys reading books about space. His favorite book is about astronauts who travel to the moon.</blockquote>\n\nWhat is Tom's favorite topic to read about?", "Space", "Animals", "Adventure", "History"]
                ]
            ],
            '60': [
                "Прочтите текст и выберите вариант ответа на вопрос:",
                [
                    ["<blockquote>The Amazon rainforest is one of the largest ecosystems in the world. It is home to millions of species of plants and animals. Unfortunately, deforestation is causing significant harm to this environment.</blockquote>\n\nWhat is causing harm to the Amazon rainforest?", "Deforestation", "Too many animals", "Pollution in rivers", "Overpopulation of insects"]
                ]
            ],
            '80': [
                "Прочтите текст и выберите вариант ответа на вопрос:",
                [
                    ["<blockquote>The invention of the printing press in the 15th century revolutionized the way information was shared. Books, which were once expensive and rare, became affordable and accessible to more people, leading to increased literacy and knowledge across Europe.</blockquote>\n\nWhat was one effect of the invention of the printing press?", "Literacy and knowledge increased", "Fewer people learned to read", "Books became more expensive", "Handwritten books became more popular"]
                ]
            ],
            '100': [
                "Прочтите текст и выберите вариант ответа на вопрос:",
                [
                    ["<blockquote>Climate change poses a serious threat to global ecosystems. Rising temperatures have led to the melting of polar ice caps, which in turn causes sea levels to rise. Additionally, extreme weather events, such as hurricanes and droughts, have become more frequent and severe. Governments and organizations around the world are working to mitigate these effects by reducing greenhouse gas emissions and investing in renewable energy.</blockquote>\n\nWhat are two major consequences of rising global temperatures mentioned in the text?", "Melting ice caps and rising sea levels", "Increased polar bear populations and colder winters", "Fewer hurricanes and less severe droughts", "Rising temperatures creating more stable ecosystems"]
                ]
            ]
        },
        'D': {
            '20': [
                "Прослушайте аудио и ответьте на вопросы:",
                [
                    ["Where does Sarah live?", "testing_0_en-GB-Standard-A.mp3", "New York", "Chicago", "Los Angeles"]
                ]
            ],
            '40': [
                "Прослушайте аудио и ответьте на вопросы",
                [
                    ["What is John buying for his sister?", "testing_1_en-GB-Standard-B.mp3", "Chocolate", "Bread", "Milk"]
                ]
            ],
            '60': [
                "Прослушайте аудио и ответьте на вопросы:",
                [
                    ["Why is the train delayed?", "testing_2_en-GB-Standard-B.mp3", "Maintenance work on the tracks", "Bad weather", "A technical issue"]
                ]
            ],
            '80': [
                "Прослушайте аудио и ответьте на вопросы:",
                [
                    ["What is one reason governments are encouraging renewable energy?", "testing_3_en-GB-Standard-B.mp3", "To reduce carbon emissions", "To increase electricity prices", "To improve traditional energy sources"]
                ]
            ],
            '100': [
                "Прослушайте аудио и ответьте на вопросы:",
                [
                    ["What is one concern mentioned about artificial intelligence?", "testing_4_en-GB-Standard-A.mp3", "It has unresolved ethical issues", "It lacks sufficient computational power", "It is too expensive"]
                ]
            ]
        },
        'E': {
            '20': [
                "Заполните пропущенное слово:",
                [
                    ["I like to drink ___ in the morning", "water", "pencil", "sun", "tree"]
                ]
            ],
            '40': [
                "Заполните пропущенное слово:",
                [
                    ["She ___ to the park every Saturday with her friends", "goes", "going", "gone", "go"]
                ]
            ],
            '60': [
                "Заполните пропущенное слово:",
                [
                    ["If I ___ more time, I would learn how to play the piano", "had", "have", "will have", "would have"]
                ]
            ],
            '80': [
                "Заполните пропущенное слово:",
                [
                    ["The project was delayed because of a lack of ___", "resources", "information", "decision", "strategy"]
                ]
            ],
            '100': [
                "Заполните пропущенное слово:",
                [
                    ["Although she was underqualified, she applied for the position, ___ the potential challenges ahead", "foreseeing", "avoiding", "ignoring", "underestimating"]
                ]
            ]
        }
    }
    # Safely retrieve the value
    category = responses.get(vCat)  # Get the nested dictionary for category
    #print('category - ', category)
    if category is None:
        return "CAT-1"

    level_questions = category.get(vLevel)  # Get the value for the level
    #print('level_questions - ', level_questions)
    if level_questions is None:
        return "LVL-1"

    #общий код
    #---------------------------------------------------------
    if len(level_questions[1]) > 1:
        vArr = random.choice(level_questions[1])
        #print('if   random| len - ', len(level_questions[1]))
    else:
        vArr = level_questions[1][0]
        #print('else| len - ', len(level_questions[1]))
    #print('vArr - ', vArr)



    #уточнения для разных категорий
    #--------------------------------------------------------
    fileNm = ''
    if vCat == 'D':
        vTask = level_questions[0]
        vQuestion = vArr[0]
        vOptionTrue = vArr[2]
        arrShuffle = vArr[2:]
        random.shuffle(arrShuffle)
        indTrue = arrShuffle.index(vOptionTrue)
        str_Msg = (
            f"{vTask}\n"
            f"{vQuestion}\n"
            f"A. {arrShuffle[0]}\n"
            f"B. {arrShuffle[1]}\n"
            f"C. {arrShuffle[2]}"
        )
        fileNm = vArr[1]
    else:
        vTask = level_questions[0]
        vQuestion = vArr[0]
        vOptionTrue = vArr[1]
        arrShuffle = vArr[1:]
        random.shuffle(arrShuffle)
        indTrue = arrShuffle.index(vOptionTrue)
        str_Msg = (
            f"{vTask}\n"
            f"{vQuestion}\n"
            f"A. {arrShuffle[0]}\n"
            f"B. {arrShuffle[1]}\n"
            f"C. {arrShuffle[2]}\n"
            f"D. {arrShuffle[3]}"
        )






    return str_Msg, indTrue, vOptionTrue, fileNm  # Return the list of questions

