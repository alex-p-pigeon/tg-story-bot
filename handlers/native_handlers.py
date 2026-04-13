from aiogram import Router, F, types, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
import re
from aiogram.utils.keyboard import InlineKeyboardBuilder



#custom
from states import myState
import selfFunctions as myF
import prompt as myP
import fpgDB as pgDB

import logging

# Get logger for this specific module
logger = logging.getLogger(__name__)

# Create router for tech handlers
r_native = Router()


#----------------------------------------------------------------------------------------------------------------   native
@r_native.callback_query(F.data == "native")
async def callback_native(callback: types.CallbackQuery, state: FSMContext, pool):
    pool_base, pool_log = pool
    vUserID = callback.message.chat.id
    bot = callback.bot
    await state.set_state(myState.common)
    curState = await state.get_state()
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))

    str_Msg = (
        f'🔹 📝 <b>Введите текст</b> или 🎤 <b>продиктуйте фразу</b> на русском или английском.\n'
        f'В ответе вы получите вариант, как её произнёс бы носитель языка. При наличии грамматических ошибок, будет предложено исправление.\n\n'
        f'🔹 При вводе одного английского слова, оно будет переведено и добавлено в рекомендуемые.\n\n'
        f'🔹 Для русского слова предложим несколько синонимов и возможные сленговые варианты'
    )



    msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    await myF.fSubMsgDel(state, pool, vUserID, callback.message.message_id, msg.message_id, bot, 3)

#----------------------------------------------------------------------------------------------------------------   native voice-text handler
@r_native.message((F.voice | F.text), StateFilter(myState.common, myState.reminder, myState.newstransOn, myState.newstransOff))
async def media_native(message: types.Message, state: FSMContext, pool, dp):        #, bot: Bot
    pool_base, pool_log = pool
    vUserID = message.chat.id
    curState = await state.get_state()

    nlp_tools = dp.workflow_data["nlp_tools"]
    tool = nlp_tools.tool
    spell = nlp_tools.spell
    lemmatizer = nlp_tools.lemmatizer

    #если текст, то message.voice = None, иначе - message.text = None
    strUserText = ''
    if message.voice != None:     #voice
        # ---------------------------------------перевод user voice -> text

        strUserText = await myF.afVoiceToTxt(message, pool, vUserID)  # транскрипция голоса в текст     , bot
    elif message.text != None:

        strUserText = ' '.join(message.text.split())    #message.text


    if strUserText != '':
        #clean text - remove extra spaces and lowercase
        strUserText = " ".join(strUserText.split())     #.lower()
        #strUserText = strUserText.strip()
        logger.info(f'***********************manual logging| strUserText - |{strUserText}|')



        #get text language--------------------------------
        langCode = myF.f_detect_language(strUserText)

        delayedWord = ''
        #--------------------------------

        txtArr = strUserText.split()



        #обработка фраз
        if len(txtArr) > 1:    #считаем, что если больше 1х, то фраза, иначе - слово
            #если русс, то промпт на how'd native say
            # если en, то промпт на перевод изначальной фразы, how'd native say + перевод

            if langCode == 'en':
                # -----------------------проверка грамматики и формирование тоггла для списка ошибка

                str_Msg, index_rule_pairs, var_ImprovedLine = await myF.fGrammarCheck_txt(
                    tool, strUserText, pool, vUserID
                )
                # Generate toggleButtonStatus dictionary dynamically
                toggleButtonStatus = {str(emoji_index): 0 for emoji_index, _ in index_rule_pairs}
                builder = await myF.fSetGrammarBuilder(toggleButtonStatus, index_rule_pairs, state)
                await state.update_data(str_Msg=str_Msg)
                await state.update_data(toggleButtonStatus=toggleButtonStatus)
                await state.update_data(index_rule_pairs=index_rule_pairs)
                # print('index_rule_pairs - ', index_rule_pairs)
            else:
                prompt = myP.fPromptNative(strUserText, langCode)  # формирование промпта
                varRes = await myF.afSendMsg2AI(prompt, pool_base, vUserID, iModel = 4)  # получение текстового ответа от ИИ
                str_Msg = f_parse_PromptNative(varRes, strUserText)
                builder = InlineKeyboardBuilder()
                builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="native"))


        # обработка слов
        else:
            if langCode == 'en':
                flagGibberish = 0
                if len(txtArr) == 1:
                    word = txtArr[0]
                    if word in spell or spell.correction(word):
                        corrected_word = spell.correction(word)
                        # print(corrected_word)
                        #tagged_word = pos_tag([corrected_word])[0]
                        tagged_word = nlp_tools.pos_tag([corrected_word])[0]
                        # print(tagged_word)
                        #wordnet_pos = myF.get_wordnet_pos(tagged_word[1]) or wordnet.NOUN
                        wordnet_pos = myF.get_wordnet_pos(tagged_word[1], nlp_tools) or nlp_tools.wordnet.NOUN
                        lemma = lemmatizer.lemmatize(corrected_word, pos=wordnet_pos)
                        # print(lemma)
                    else:
                        flagGibberish = 1

                if flagGibberish == 0:
                    var_Arr = await myF.fDBTranslate(lemma, pool_base, 2)  # проверка по БД
                    v_Rus = var_Arr[0]
                    strIPA = var_Arr[1]
                    strAltTranslate = var_Arr[2]
                    vObj_ID = var_Arr[3]
                    vExample = var_Arr[4] or ''
                    vOrigin = var_Arr[5] or ''
                    vDict = var_Arr[6] or ''
                    #vWordCard = var_Arr[4] or ''
                    logger.info(f'***********************manual logging| v_Rus - {v_Rus}')

                    if v_Rus is None:
                        v_Rus = await myF.afGoogleTrans(lemma, pool_base, vUserID)  # google translate
                        '''
                        v_Rus, strAltTranslate = await myF.fAltTranslationLLM(
                            lemma,
                            v_Rus,
                            pool_base,
                            vUserID
                        )  # get alternative translations
                        '''
                        strARPA, strIPA = myF.getTranscriptionNltk(lemma, nlp_tools)  # get transription with nltk
                        var_query = (
                            f"INSERT INTO tw_obj (obj_eng, obj_rus, obj_arpa, obj_ipa, type_id) "
                            f"VALUES ('{lemma}', '{v_Rus}', '{strARPA}', '{strIPA}', '1')  "
                            f"ON CONFLICT (obj_eng) DO NOTHING "
                            f"RETURNING obj_id;"
                        )
                        # f"INSERT INTO tw_obj (obj_eng, obj_rus, obj_rus_alt, obj_arpa, obj_ipa, type_id) "
                        # f"VALUES ('{lemma}', '{v_Rus}', '{strAltTranslate}', '{strARPA}', '{strIPA}', '1')  "
                        # await pgDB.fExec_UpdateQuery(pool_base, var_query)
                        var_arr = await pgDB.fExec_SelectQuery(pool_base, var_query)

                        logger.info(f'***********************manual logging| var_arr - {var_arr}')

                        vObj_ID = var_arr[0][0]
                        # print('vObj_ID2 - ', vObj_ID)

                        logger.info(f'***********************manual logging| lemma - |{lemma}|')

                        delayedWord = lemma
                        logger.info(f'***********************manual logging| |||delayedWord - |{delayedWord}|')

                    var_query = (
                        f"INSERT INTO tw_userprogress (obj_id, userobj_id, user_id, status_id)  "
                        f"VALUES ('{vObj_ID}', '{vUserID}{vObj_ID}', '{vUserID}', '1') "
                        f"ON CONFLICT (userobj_id) "
                        f"DO UPDATE SET status_id = EXCLUDED.status_id;"
                    )

                    await pgDB.fExec_UpdateQuery(pool_base, var_query)

                    str_Msg = myF.fShapeWordCard(lemma, v_Rus, strIPA, vExample, vOrigin, vDict)   #strAltTranslate   vWordCard
                    '''
                    transcription_str = f"      <code>[{strIPA}] </code>\n" if strIPA else ""

                    str_Msg = (
                        f"📖 <b>{lemma}</b> \n"
                        f"{transcription_str}"
                        f"      {v_Rus} (<i>{strAltTranslate}</i>)\n\n"
                        f"{vWordCard}"
                    )
                    '''

                    '''
                    str_Msg = (
                        f'{lemma} - [{strIPA}] - {v_Rus}\n'
                        f' {strAltTranslate}'
                    )
                    '''
                else:
                    str_Msg = (
                        f'Слово введено некорректно. Пожалуйста, введите заново'
                    )
            else:   #russian word
                prompt = myP.fPromptWordTransSyn(strUserText)
                varRes = await myF.afSendMsg2AI(prompt, pool_base, vUserID, iModel = 4)  # получение текстового ответа от ИИ
                logger.info(f'***********************manual logging| varRes - {varRes}')

                str_Msg = f_parse_PromptNative(varRes, strUserText, 2)
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text=myF.fCSS('back'), callback_data="native"))

        msg = await message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        #await myF.fSubMsgDel(state, pool, vUserID, message.message_id, msg.message_id, bot, 3)

        logger.info(f'***********************manual logging| delayedWord - {delayedWord}')
        if delayedWord != '':

            await myF.fGenWordCard_NLTK_AI(pool_base, nlp_tools, word=delayedWord, vUserID=vUserID)
        #await callback.answer("Карточка счета создана!")

        await pgDB.fExec_LogQuery(pool_log, vUserID, f'native|{strUserText}|{str_Msg}')

def f_parse_PromptNative(response: str, strUserText, switch = 1):
    """
    Parses the AI response and extracts values for {1}, {2}, {3}, and {4} (if present).

    :param response: AI-generated text containing {1}, {2}, {3}, and optionally {4}.
    :return: Tuple (text_1, text_2, text_3, text_4 or None if omitted).
    """
    pattern = r"\{(\d)\}:\s*(.+?)(?=\n\{\d\}:|\Z)"  # Matches {1}: ..., {2}: ..., etc.
    matches = re.findall(pattern, response, re.DOTALL)

    # Dictionary to hold extracted values
    parsed_data = {str(i): None for i in range(1, 5)}

    # Populate dictionary with found matches
    for key, value in matches:
        parsed_data[key] = value.strip()

    if switch == 1:     #обработка Native
        if parsed_data.get("4"):
            strAux = f'💡 {parsed_data["4"]}'
        else:
            strAux = ""

        str_Msg = (
            f'<u>Первоначальная фраза:</u>\n'
            f'🟡 {strUserText}\n'
            f'      ❱         <i>{parsed_data["1"]}</i>\n\n'
            f'<u>{myF.fCSS("native")}:</u>\n'
            f'🔵 <b>{parsed_data["2"]}</b>\n'
            f'      ❱         <i>{parsed_data["3"]}</i>\n\n'
            f'<i>{strAux}</i>'
        )
    else:
        #print('strSlang - ', parsed_data["3"])
        if parsed_data["3"] is None:
            parsed_data["3"] = ''
        elif re.search(r"\b(?:None|none|n/a|n\a)\b", parsed_data["3"], re.IGNORECASE):
            parsed_data["3"] = ''

        strSyn = f'🔄 <b>Синонимы:</b> {parsed_data["2"]}\n' if parsed_data["2"] else ''
        strSlang = f'😎 <b>Сленг:</b> {parsed_data["3"]}\n' if parsed_data["3"] else ''
        str_Msg = (
            f'💬 <b>Слово:</b> {strUserText}\n'
            f'📖 <b>Перевод:</b> {parsed_data["1"]}\n'
            f'{strSyn}{strSlang}'
        )


    return str_Msg
