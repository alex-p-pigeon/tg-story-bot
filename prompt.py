import random
import fpgDB as pgDB

#===================================================================================================================================================dialog Promt
def fPrompt(stepSelector, dDesc, dHistory, dLineWordLimit, vUserID, dUserLevel):
    '''

    '''

    prompt = ""
    
    #if modelSelector in ['news', 'st']:
    if 1==1:
        #------------------------------------------------------------------------------------------------------------------1st msg
        if stepSelector == 'start':       #vUserID dUserLevel dDesc dLineWordLimit       NO dHistory
            #не зависит от темы
            prompt = (
                f"Forget previous instructions \n"
                f"You are an experienced English teacher making an educational dialog with me. My english level is {dUserLevel}1.\n"
                f"Dialog description - {dDesc}\n"
                f"You and me step by step make a conversation \n"
                f"Now write one starting line in the dialogue. The limit of words is {dLineWordLimit}\n"
                f"Example: [AI]: Hey, long time no see! How have you been? \n"
                f"Format: [AI]: your phrase"
                )
            #f"Give one greeting phrase. The limit of words is {dLineWordLimit}\n"

        
        #------------------------------------------------------------------------------------------------------------------voice  3rd msg
        elif stepSelector == 'loop':
            #не зависит от темы
            prompt = (
                f"Forget previous instructions \n"
                f"You are an experienced English teacher making an educational dialog with me. My english level is {dUserLevel}1.\n"
                f"Dialog description - {dDesc}\n"
                f"You and me step by step make a conversation. \n"
                f"You use words and phrases for person with english level {dUserLevel}1. The limit of words in one message is {dLineWordLimit} \n"
                f"Your chat history is: {dHistory} \n"
                f"Now write one line in the dialogue to continue it\n"
                f"Format: [AI]: your line"
                )

        #------------------------------------------------------------------------------------------------------------------end
        #не зависит от темы
        elif stepSelector == 'end':

            prompt = (
                f'You are tasked with comparing two dialogues: the original and the improved version.\n'
                f'Identify English words from the improved dialogue that undergo the following:\n'
                f'- are not present in the original and have a level of complexity that makes them suitable for learning.\n'
                f'- were used in russian language in the original dialogue\n'
                f'Suggest these words in their base (lemma) form, separated by commas, and enclosed in square brackets.\n\n'
                f'Original dialogue:\n{dDesc}\n'
                f'Improved dialogue:\n{dHistory}\n\n'
                f'The OUTPUT must be in Russian and follow this structure:\n'
                f'{{1}} Слова, рекомендуемые для изучения: [word1, word2, word3]\n\n'
                f'Words should have sufficient complexity to be useful for expanding vocabulary.\n'
                f'Example:\n'
                f'{{1}} Слова, рекомендуемые для изучения: [collaboration, deployment, overcome]'
            )



            '''
            prompt = (
                f'Forget previous instructions \n'
                f'Compare two dialogs - original and improved one\n'
                f'Based on difference between dialogs suggest english words from improved dialog and not presented in original dialog that can be recommended for learning, '
                f'give them as a list devided by comma and put in square brackets.'
                f'Words must be in their base lemma form'
                f'Content of the original dialog is:\n{dDesc}\n'
                f'Content of improved dialog is:\n{dHistory}\n'
                f'The OUTPUT must be given in russian and have the following structure:\n'
                f'{{1}} Слова рекомендуемые к изучению:  [word1, word 2, word 3]\n'
                f'Output example:\n'
                f'{{1}} Слова рекомендуемые к изучению: [collaboration, deployment, overcome]'
            )
            prompt = (
                f"Forget previous instructions \n"
                f"You act as an experienced English teacher. I give you dialogue between AI-assistant and me, my english level is {dUserLevel}1.\n"
                f"Our dialogue is - {dHistory}\n"
                f"\n"
                f"Your task is to analyze my phrases given in a format {{me: phrase1}} in the dialogue, identify any mistakes and point possible improvements.\n"
                f"The output must have the following structure:\n"
                f"- Resume - breif results of the analysis \n"
                f"- Mistakes - point out revealed mistakes \n"
                f"- Improvements - tell what words and phrases would add more variety to the dialogue and would help to move me to a higher level of English  \n"
                f"You must give your answer in russian language preserving english words where necessary \n"
                f"Format: \n"
                f"<b>Resume.</b> answer given in russian language \n"
                f"<b>Mistakes.</b> answer given in russian language \n"
                f"<b>Improvements.</b> answer given in russian language \n"
                f"Example:\n"
                f"<b>Resume.</b> Диалог в целом ... \n"
                f"<b>Mistakes.</b> Есть следующие ошибки...\n"
                f"<b>Improvements.</b> ...\n"
                )
                '''
        elif stepSelector == 'line_analysis':
            prompt = (
                f'You are an experienced English teacher. Analyze the following text for mistakes:\n'
                f'- Grammatical errors: Tense issues, subject-verb agreement, etc.\n'
                f'- Idiomatic/stylistic issues: Awkward phrasing or incorrect idioms.\n\n'
                f"In your analysis DO NOT analyse punctuation\n\n"
                f"The OUTPUT must be in Russian, but all examples and word lists should be in English.\n"
                f'Text: "{dDesc}"\n\n'
                f'OUTPUT format:\n'
                f'{{1}} Грамматические ошибки: ...\n'
                f'{{2}} Идиоматические или стилистические проблемы: ...'
            )
            #f'Provide corrections in Russian. Recheck and improve your output if needed.\n\n'

        elif stepSelector == 'hint':
            prompt = (
                f'Forget previous instructions.\n'
                f'Analyze the following educational dialog and provide three possible options for how the conversation could proceed. \n'
                f'Each option should be a natural continuation based on the context.\n\n'
                f'Dialog to analyze: "{dHistory}"\n\n'
                f'Answer give in Russian language\n'
                f'OUTPUT format:\n'
                f'{{1}} Вариант 1\n'
                f'{{2}} Вариант 2\n'
                f'{{3}} Вариант 3\n'
            )
        elif stepSelector == 'improved':
            prompt_old = (
                f'Forget previous instructions.\n'
                f'You are an experienced English teacher. Please improve the following text excluding grammatical errors, meaning-related and idiomatic or stylistic issues.\n'
                f'Text to improve: "{dDesc}"\n'
                f'OUTPUT: improved version of the text'
            )
            prompt = (
                f'Given a text in English, carefully follow these instructions to ensure accuracy and naturalness:\n\n'
                f'- Improve the English text to sound as fluent and natural as a native speaker would express it.\n'
                f'- If the text is already natural, keep it unchanged.\n'
                f'- Prioritize clarity, idiomatic usage, and correct grammar while preserving the original meaning.\n\n'

                f'### Output Format:\n'
                f'<Rewritten phrase in native-like English>\n'
                
                f'### Example for "I want to investigate my bedroom.":\n'
                f'I want to check out my bedroom.\n'
                f'Now, process the following phrase:\n'
                f'Input: {dDesc}'
            )
        elif stepSelector == 'grammar':

            #Your task is to
            prompt = (
                f'''
                You are an experienced English teacher and grammar expert.

                Keep to the following instructions:
                1. Check if the text is grammatically correct for Standard English:
                    - for a complex sentences verb tenses from each part of the sentence must match with each other (use only Standard/Academic English rules, no colloquial speech simplifications and assumptions allowed)
                    - are all preposition used correctly and natural
                    - are there other grammar mistakes
                2. If the text is not grammatically correct, make necessary changes to correct it
                3. Provide a brief explanation in natural academic Russian of what was corrected, organized into three categories:
            	    [cat1] Semantic preposition misuse (e.g., incorrect use of "in/at/on", "with/by/of", or other idiomatic errors)
            		[cat2] Verb tenses match in terms of Standard/Academic English
            		[cat3] Other grammatical changes (e.g., agreement, word order)
            	4. If there is no mistakes for a category X put '[catX] None', e.g. '[cat3] None'
            	5. For given text carefully follow these instructions to ensure accuracy and naturalness:
            	    - Improve the English text to sound as fluent and natural as a native speaker would express it
            	    - If the text is already natural, keep it unchanged
            	    - Prioritize clarity, idiomatic usage, and correct grammar while preserving the original meaning
            	    

                Format your output strictly as four parts for the whole given text:
                {{1}} grammatically corrected text  
                [cat1] explanation in Russian or None  
                [cat2] explanation in Russian or None  
                [cat3] explanation in Russian or None
                {{2}} improved text as a native speaker would say it

                Given text: {dDesc}
                '''
            )





    return prompt



def fPromptNative(strUserText, flagLang):
    prompt = ''
    if flagLang == 'en':

        prompt = (
            f'Given a text in English, perform the following steps:\n'
            f'1. Translate it into Russian in the most natural and appropriate way, ensuring grammatically and lexically valid translation. '
            f'Nonexistent words or unnatural constructions must not be generated.\n'
            f'2. Rewrite the English text to make it sound as fluent and natural as a native speaker would say it.\n'
            f'3. Translate the rewritten English text into Russian naturally and appropriately, following the same principles as in Step 1.\n'
            f'4. Omit this step except for the following cases:\n'
            f'4.1 if the given text has grammar error and rewritten text fixes it. In this case provide brief explanation of grammar\n'
            f'4.2 if the rewritten text shows some fluency, lexical, idiomatic or slang improvements. In this case provide brief explanation of improvements'
            f'The explanation must be written in Russian in an **impersonal** form, avoiding first-person pronouns (e.g., instead of "Я изменил", use "Фраза была изменена"). '
            f'Ensure fluency, correctness, and a natural tone in both languages.\n'
            f'Return the output in the following structured format, without extra text:\n\n'
            f'{{1}}: <Russian translation of the original phrase>\n'
            f'{{2}}: <Rewritten phrase in native-like English>\n'
            f'{{3}}: <Russian translation of the rewritten phrase>\n'
            f'{{4}}: <Explanation of the changes in Russian (impersonal tone) - ONLY if a significant change was made>\n\n'
            f'Example for "I want to investigate my bedroom.":\n'
            f'{{1}}: Я хочу осмотреть свою спальню.\n'
            f'{{2}}: I want to check out my bedroom.\n'
            f'{{3}}: Я хочу проверить свою спальню.\n'
            f'{{4}}: Глагол "investigate" звучит слишком формально и обычно используется в юридическом или научном контексте. '
            f'Фраза была заменена на "check out", так как это более естественный вариант для описания осмотра комнаты или места.\n\n'
            f'Now, process the following phrase:\n'
            f'Input: {strUserText}'
        )

        prompt = (
            f'Given a text in English, carefully follow these structured steps to ensure accuracy and naturalness:\n\n'

            f'### Step 1: Initial Translation to Russian\n'
            f'- Translate the input text into Russian in a grammatically and lexically valid way.\n'
            f'- Avoid unnatural constructions, overly literal translations, or nonexistent words.\n'
            f'- Ensure the translation conveys the intended meaning accurately.\n\n'

            f'### Step 2: Rewriting in Fluent, Natural English\n'
            f'- Improve the English text to sound as fluent and natural as a native speaker would express it.\n'
            f'- If the text is already natural, keep it unchanged.\n'
            f'- Prioritize clarity, idiomatic usage, and correct grammar while preserving the original meaning.\n\n'

            f'### Step 3: Translation of the Rewritten English Text into Russian\n'
            f'- Translate the improved English version into Russian, following the same principles as in Step 1.\n\n'

            f'### Step 4: Explanation of Changes (Only if Necessary)\n'
            f'- Provide a brief explanation in **Russian (impersonal tone)** ONLY if:\n'
            f'  1. The original English text had a grammatical mistake that was corrected.\n'
            f'  2. The rewritten English text included notable fluency, lexical, idiomatic, or slang improvements.\n'
            f'- Use an impersonal form in Russian (e.g., "Фраза была изменена" instead of "Я изменил").\n\n'

            f'### Output Format (Return the result strictly in this format):\n'
            f'{{1}}: <Russian translation of the original phrase>\n'
            f'{{2}}: <Rewritten phrase in native-like English>\n'
            f'{{3}}: <Russian translation of the rewritten phrase>\n'
            f'{{4}}: <Explanation in Russian (impersonal tone) - ONLY if a significant change was made>\n\n'

            f'### Example for "I want to investigate my bedroom.":\n'
            f'{{1}}: Я хочу осмотреть свою спальню.\n'
            f'{{2}}: I want to check out my bedroom.\n'
            f'{{3}}: Я хочу проверить свою спальню.\n'
            f'{{4}}: Глагол "investigate" звучит слишком формально и обычно используется в юридическом или научном контексте. '
            f'Фраза была заменена на "check out", так как это более естественный вариант для описания осмотра комнаты или места.\n\n'

            f'Now, process the following phrase:\n'
            f'Input: {strUserText}'
        )


    #            f'differs significantly from the original (i.e., differs by at least 3 words or the length changes by more than 20%), '
#            f'provide an explanation of the changes. This should include grammatical and lexical considerations, as well as references to idioms or slang if applicable. '
#f'If the difference is minimal, omit Step 4.\n\n'

    else:
        prompt = (
            f'Given a text in Russian, perform the following steps:\n'
            f'1. Translate it into English literally while preserving meaning.\n'
            f'2. Adjust the English translation to sound the most natural, fluent, and idiomatic, as a native speaker would say it.\n'
            f'3. Translate the refined English phrase back into Russian in the most appropriate and natural way, ensuring correct grammar, '
            f'valid word usage, and idiomatic accuracy. Nonexistent words or unnatural constructions must not be generated.\n'
            f'4. If the refined English phrase differs significantly from the literal translation (i.e., differs by at least 3 words or the length changes by more than 20%), '
            f'provide an explanation of the changes. This should include grammatical, lexical, and stylistic considerations, as well as references to idioms or slang if applicable. '
            f'The explanation must be written in Russian in an **impersonal** and **objective** form (e.g., instead of "Я изменил", use "Фраза была скорректирована"). '
            f'If the difference is minimal, omit Step 4.\n\n'
            f'Return the output in the following structured format:\n'
            f'{{1}}: <Literal translation into English>\n'
            f'{{2}}: <Refined natural English phrase>\n'
            f'{{3}}: <Natural Russian translation of the refined phrase>\n'
            f'{{4}}: <Explanation of the transformation (in Russian, impersonal tone) - ONLY if a significant change was made>\n\n'
            f'Example for "У меня полный порядок в комнате.":\n'
            f'{{1}}: "I have full order in my room."\n'
            f'{{2}}: "My room is perfectly tidy."\n'
            f'{{3}}: "Моя комната идеально убрана."\n'
            f'{{4}}: Фраза "I have full order in my room" является дословным переводом, но звучит неестественно на английском. '
            f'В английском языке вместо "full order" чаще используется выражение "perfectly tidy" для описания порядка в комнате. '
            f'Глагол "have" был заменён, так как англоговорящие обычно говорят о состоянии комнаты, а не о владении порядком.\n\n'
            f'Now, process the following phrase:\n'
            f'Input: "{strUserText}"'
        )

        prompt = (
            f'Given a text in Russian, carefully follow these structured steps to ensure accurate and natural translation:\n\n'

            f'### Step 1: Literal Translation into English\n'
            f'- Translate the Russian text into English as literally as possible while preserving the original meaning.\n'
            f'- Maintain the sentence structure where possible, but ensure grammatical correctness.\n'
            f'- Avoid adding extra meaning or making stylistic improvements at this stage.\n\n'

            f'### Step 2: Refining the English Translation\n'
            f'- Adjust the literal translation to make it sound natural, fluent, and idiomatic.\n'
            f'- Ensure the phrase reflects how a native speaker would naturally express the idea.\n'
            f'- Improve clarity and readability while preserving the original meaning.\n\n'

            f'### Step 3: Translation Back into Russian\n'
            f'- Translate the refined English phrase back into Russian.\n'
            f'- Ensure the Russian translation is grammatically correct, lexically appropriate, and idiomatically accurate.\n'
            f'- Avoid unnatural constructions, overly literal phrases, or non-existent words.\n\n'

            f'### Step 4: Explanation of Significant Changes (Only if Necessary)\n'
            f'- Provide a **brief** explanation in **Russian (impersonal and objective tone)** ONLY if the refined English phrase:\n'
            f'  1. Differs from the literal translation by at least **3 words** OR\n'
            f'  2. Changes in length by more than **20%**.\n'
            f'- The explanation should cover **grammatical, lexical, and stylistic** differences, including idioms or slang if relevant.\n'
            f'- Use an impersonal form in Russian (e.g., "Фраза была скорректирована" instead of "Я изменил").\n'
            f'- If the difference is minimal, **omit Step 4**.\n\n'

            f'### Output Format (Strictly follow this structure):\n'
            f'{{1}}: <Literal English translation>\n'
            f'{{2}}: <Refined, natural English phrase>\n'
            f'{{3}}: <Natural Russian translation of the refined phrase>\n'
            f'{{4}}: <Explanation of the transformation (in Russian, impersonal tone) - ONLY if a significant change was made>\n\n'

            f'### Example for "У меня полный порядок в комнате.":\n'
            f'{{1}}: "I have full order in my room."\n'
            f'{{2}}: "My room is perfectly tidy."\n'
            f'{{3}}: "Моя комната идеально убрана."\n'
            f'{{4}}: Фраза "I have full order in my room" является дословным переводом, но звучит неестественно на английском. '
            f'В английском языке вместо "full order" чаще используется выражение "perfectly tidy" для описания порядка в комнате. '
            f'Глагол "have" был заменён, так как англоговорящие обычно говорят о состоянии комнаты, а не о владении порядком.\n\n'

            f'Now, process the following phrase:\n'
            f'Input: "{strUserText}"'
        )

        prompt = (
            f'Given a text in Russian, carefully follow these structured steps to ensure accurate and natural translation:\n\n'

            f'### Step 1: Literal Translation into English\n'
            f'- Translate the Russian text into English as literally as possible while preserving the original meaning.\n'
            f'- Maintain the sentence structure where possible, but ensure grammatical correctness.\n'
            f'- Avoid adding extra meaning or making stylistic improvements at this stage.\n\n'

            f'### Step 2: Refining the English Translation\n'
            f'- Adjust the literal translation to make it sound natural, fluent, and idiomatic.\n'
            f'- If literal translation is already natural, fluent, and idiomatic leave it unchanged\n'
            f'- Prefer widely used, idiomatic expressions over abstract or overly formal phrasing\n'
            f'- Ensure the phrase reflects how a native speaker would naturally express the idea.\n'
            f'- Improve clarity and readability while preserving the original meaning.\n\n'

            f'### Step 3: Translation Back into Russian\n'
            f'- Translate the refined English phrase back into Russian.\n'
            f'- Ensure the Russian translation is grammatically correct, lexically appropriate, and idiomatically accurate.\n'
            f'- Avoid unnatural constructions, overly literal phrases, or non-existent words.\n\n'

            f'### Step 4: Explanation of Significant Changes (Only if Necessary)\n'
            f'- Provide a **brief** explanation in **Russian (impersonal and objective tone)** ONLY if the refined English phrase:\n'
            f'  1. Differs from the literal translation by at least **3 words** OR\n'
            f'  2. Changes in length by more than **20%**.\n'
            f'- The explanation should cover **grammatical, lexical, and stylistic** differences, including idioms or slang if relevant.\n'
            f'- Use an impersonal form in Russian (e.g., "Фраза была скорректирована" instead of "Я изменил").\n'
            f'- If the difference is minimal, **omit Step 4**.\n\n'

            f'### Output Format (Strictly follow this structure):\n'
            f'{{1}}: <Literal English translation>\n'
            f'{{2}}: <Refined, natural English phrase>\n'
            f'{{3}}: <Natural Russian translation of the refined phrase>\n'
            f'{{4}}: <Explanation of the transformation (in Russian, impersonal tone) - ONLY if a significant change was made>\n\n'

            f'### Example for "У меня полный порядок в комнате.":\n'
            f'{{1}}: "I have full order in my room."\n'
            f'{{2}}: "My room is perfectly tidy."\n'
            f'{{3}}: "Моя комната идеально убрана."\n'
            f'{{4}}: Фраза "I have full order in my room" является дословным переводом, но звучит неестественно на английском. '
            f'В английском языке вместо "full order" чаще используется выражение "perfectly tidy" для описания порядка в комнате. '
            f'Глагол "have" был заменён, так как англоговорящие обычно говорят о состоянии комнаты, а не о владении порядком.\n\n'

            f'Now, process the following phrase:\n'
            f'Input: "{strUserText}"'
        )

    return prompt

def fPromptWordTransSyn(strUserText):

    prompt = (
        f'Given a word in Russian, follow these steps:\n'
        f'1. Translate it into English in the most natural way, assuming the word is in its base form (e.g., nouns in the nominative case).\n'
        f'2. If applicable, provide several English synonyms for the translation from Step 1.\n'
        f'3. Omit this step except case where there is/are slang words for a given Russian word. In that case provide slang\n\n'
        f'Additional Instructions:\n'
        f'- Avoid providing words from other languages (e.g., French, Spanish). Only use English equivalents.\n'
        f'- Omit additional context unless absolutely necessary; if included, write it in Russian.\n\n'
        f'Output format:\n'
        f'{{1}}: <main English translation>\n'
        f'{{2}}: <English synonyms (if any)>\n'
        f'{{3}}: <English slang equivalents (if any)>\n\n'
        f'Example for "Класс":\n'
        f'{{1}}: cool, class\n'
        f'{{2}}: great, awesome, excellent\n'
        f'{{3}}: rad, dope\n\n'
        f'Example for "Магнит" (no slang available):\n'
        f'{{1}}: magnet\n'
        f'{{2}}: attraction, lodestone\n'
        f'Now, process the following word: \n'
        f'Given word in Russian: {strUserText}'
    )

    prompt = (
        f'Given a word in Russian, carefully follow these structured steps:\n\n'

        f'### Step 1: Main English Translation\n'
        f'- Translate the Russian word into English **in its base form** (e.g., nouns in the nominative case, verbs in the infinitive form).\n'
        f'- Choose the **most natural and commonly used** translation.\n\n'

        f'### Step 2: Provide Synonyms (If Applicable)\n'
        f'- List **several synonyms** that are valid in English, ensuring they convey the same meaning as the translation from Step 1.\n'
        f'- Synonyms should be commonly used words that fit in general contexts.\n'
        f'- If no synonyms exist, omit this step.\n\n'

        f'### Step 3: Identify English Slang Equivalents (If Applicable)\n'
        f'- **ONLY** provide slang words if applicable.\n'
        f'- Ensure the slang terms are commonly understood in modern English.\n'
        f'- If no slang exists, omit this step.\n\n'

        f'### Additional Instructions:\n'
        f'- **Do NOT** provide words from other languages (e.g., French, Spanish). Use only English equivalents.\n'
        f'- Avoid adding unnecessary context unless **absolutely required**; if included, write it in **Russian**.\n'

        f'### Output Format (Strictly follow this structure):\n'
        f'{{1}}: <Main English translation>\n'
        f'{{2}}: <English synonyms (if any)>\n'
        f'{{3}}: <English slang equivalents (if any)>\n\n'

        f'### Example for "Класс":\n'
        f'{{1}}: cool, class\n'
        f'{{2}}: great, awesome, excellent\n'
        f'{{3}}: rad, dope\n\n'

        f'### Example for "Магнит" (No slang available):\n'
        f'{{1}}: magnet\n'
        f'{{2}}: attraction, lodestone\n\n'

        f'Now, process the following word:\n'
        f'Given word in Russian: {strUserText}'
    )

    return prompt


def fPromptWordsImprovement(word):
    prompt = f'''
                    For the given English word, determine whether it is in its base form using lemmatization. If it is not, return the corrected 
                    base form.\n
                    Nouns should be in the singular nominative case unless the plural has a distinct meaning (for example, "customs" differs in 
                    meaning from "custom")\n
                    Verbs should be in the infinitive form (e.g., "provided" → "provide") unless the given form has a distinct meaning rather then 
                    standard past or participle form \n
                    Parts of speech such as adjective, adverb, infinitive, gerund should be returned unchanged\n
                    If the word is already in its base form, return it unchanged\n
                    Output only the corrected word, without explanations or additional text\n
                    Given word - {word}
                '''

    return prompt

def fPromptWordCard_AI(word):
    prompt = f'''
                    For the given English word, generate structured examples demonstrating its different meanings and grammatical uses. 
                    Include at least two example sentences in English with Russian translations, ensuring they illustrate different contexts. 
        	        Additionally, provide a concise historical overview of the word’s origin. Output give in Russian.
        	        
        	        Format:
                    __Example__ 
                    🔸 "example1 in English"
                      <i>— example1 translation<i>
                    🔸 "example2 in English"
                      <i>— example2 translation<i>\n
                    __Origin__
                    word origin in Russian\n
                    
                    Example for the word 'ability':
                    __Example__
                    🔸 "She has the ability to stay calm in stressful situations."
                      <i>— У неё есть способность сохранять спокойствие в стрессовых ситуациях.</i>
                    🔸 "The test measures students' abilities in math and reading."
                      <i>— Тест оценивает способности учеников в математике и чтении.</i>\n
                    __Origin__
                    Слово ability происходит от латинского habilitas («способность, пригодность»), которое через старофранцузское abilite 
                    проникло в английский язык в XIV веке. Изначально использовалось в значении «умение, пригодность» и со временем стало 
                    обозначать как врождённые, так и приобретённые способности.\n
                    
                    Given word - {word}
                    '''
    prompt_old = f'''
                For the given English word, generate structured examples demonstrating its different meanings and grammatical uses. 
                Include at least two example sentences in English with Russian translations, ensuring they illustrate different contexts. 
    	        Additionally, provide a concise historical overview of the word’s origin. Output give in Russian.
    	        Format:
                ✍️ <b>Примеры:</b> 
                🔸 "example1 in English"
                  <i>— example1 translation<i>
                🔸 "example2 in English"
                  <i>— example2 translation<i>\n
                📜 <b>Происхождение:</b>
                word origin in Russian\n
                Example for the word 'ability':
                ✍️ <b>Примеры:</b>
                🔸 "She has the ability to stay calm in stressful situations."
                  <i>— У неё есть способность сохранять спокойствие в стрессовых ситуациях.</i>
                🔸 "The test measures students' abilities in math and reading."
                  <i>— Тест оценивает способности учеников в математике и чтении.</i>\n
                📜 <b>Происхождение:</b>
                Слово ability происходит от латинского habilitas («способность, пригодность»), которое через старофранцузское abilite 
                проникло в английский язык в XIV веке. Изначально использовалось в значении «умение, пригодность» и со временем стало 
                обозначать как врождённые, так и приобретённые способности.\n
                Given word - {word}
                '''



    return prompt

#=================================================================================================================================================== dialog Desc
def fGetDDesc(modelSelector):
    dDescEn = ""
    dDescRu = ""
    #------------------------------------------------------------------------------------------------------------------news
    if modelSelector == 'news':
        dDescEn = "Educational dialog to improve speaking skills. Two friends meet each other after a while and talk about what had happened recently in their lives"
        dDescRu = "Встреча двух знакомых, разговор о новостях за последнее время"
    #------------------------------------------------------------------------------------------------------------------small talk
    if modelSelector == 'st':
        arrST = [
            "Is there any events in the city?",
            "Is there any new restaurant that one could recommend?",
            "Is there any news in sports recently?",
            "Is there any books one had read recently?",
            "If one traveled anywhere interesting recently?",
            "Have one seen any good movies lately?",
            "How is work going recently?",
            "What does one like to do in their free time?",
            "Does one have any plans for the weekend?",
            "How lovely weather we're having today",
            "What a nasty weather we're having today"
            ]
        vSubTopic = random.choice(arrST)
        dDescEn = f"Educational dialog to improve Small talk skills. Two persons don't know each other, they want to break ice and have a small talk on '{vSubTopic}'"
        dDescRu = "Small talk. Разговор на простые, нейтральные, отвлеченные темы"
    #------------------------------------------------------------------------------------------------------------------situations
    if modelSelector == 'situation':
        arrD = [
            ["Ordering Food at a Restaurant: Customer and waiter discussing the menu and placing an order.", "Заказ еды в ресторане"], 
            ["Planning a Vacation: Friends or family members deciding on a destination and itinerary.", "Планирование отпуска"], 
            ["Doctor's Appointment: A patient explaining symptoms to a doctor and receiving advice.", "Прием у врача"], 
            ["Shopping for Clothes: A customer asking a sales assistant for help with sizes and styles.", "Шоппинг. Разговор с продавцом"] ,
            ["Asking for Directions: A tourist asking a local for directions to a landmark.", "Уточнить дорогу"] ,
            ["Making a Hotel Reservation: A guest calling to book a room and asking about amenities.", "Бронирование номера в отеле"] ,
            ["Discussing a Movie: Friends talking about a movie they recently watched and their opinions on it.", "Обсуждение кино"] ,
            ["At the Airport: A traveler checking in, asking about flight details, and going through security.", "В аэропорту"] ,
            ["Library Visit: A patron asking a librarian for help finding specific books or resources.", "В библиотеке"] ,
            ["Parent-Teacher Meeting: A parent discussing their child's progress and behavior with a teacher.", "Разговор учителем об успеваемости ребенка"] ,
            ["Car Trouble: A driver explaining car problems to a mechanic and discussing repair options.", "Разговор с механиком в автомастерской"] ,
            ["Buying a House: A potential buyer asking a real estate agent about a property and its features.", "Разговор с риэлтором о покупке недвижимости"] ,
            ["Planning a Party: Friends or colleagues organizing a party, deciding on the guest list, and planning activities.", "Планирование вечеринки"] ,
            ["Talking About Hobbies: Two people sharing their hobbies and interests and asking questions about each other's activities.", "Разговор о хобби"] ,
            ["Banking Transactions: A customer talking to a bank teller about opening an account, depositing money, or applying for a loan.", "Открытие счета в банке"] ,
            ["Discussing Weather: Casual conversation about the current weather, forecasts, and seasonal changes.", "Обсуждение погоды"] ,
            ["First Day at Work:A new employee being introduced and asking questions about routines and expectations.", "Первый день на работе"] ,
            ["Tech Support: A customer calling tech support to solve an issue with a device or software.", "Общение с тех поддержкой"]
            ]
        subArr = random.choice(arrD)
        dDescEn = subArr[0]
        dDescRu = subArr[1]

    str_Msg = (
        f"Тема диалога: {dDescRu} \n"
        f"Выберите ограничение количества слов во фразах бота: "
        )
    return dDescEn, str_Msg


#=================================================================================================================================================== HR
async def fHR_vacancy_desc(vJobTitle, pool):
    var_query = (
        f"SELECT c_hr_vac_desc "
        f"FROM t_hr_vacancy "
        f"WHERE c_hr_vac_title = '{vJobTitle}'"
        )
    #connection = myDB.create_connection()
    vTxt = await pgDB.fExec_SelectQuery(pool, var_query)    #myDB.execute_query(connection, var_query)
    print('fHR_vacancy_desc - ', vTxt[0][0])
    return vTxt[0][0]
       
def fHR_PromptInit(dHR_vacancyDesc, dHR_CV):
    prompt = (
        f"Forget previous instructions \n"
        f"You act as a HR manager. \n"
        f"Here is a vacancy requirements for the position: {dHR_vacancyDesc}\n"
        f"Here is applicant's resume: {dHR_CV} \n"
        f"Your task is to prepare questions to the candidate's job interview based on resume and job requirements analysis covering all job interview themes: \n"
        f"- Introduction and Background \n"
        f" -Professional Experience \n"
        f" -Professional Skills \n"
        f" -Tools and Techniques \n"
        f" -Communication and Collaboration \n"
        f" -Problem-Solving and Process Improvement \n"
        f" -Certifications and Professional Development \n"
        f" -Industry-Specific Experience \n"
        f" -Preferred Skills and Tools \n"
        f" -Motivation and Cultural Fit \n"
        f"Out should contain only "
        f"Output format: \n"
        f"{{#}} your question\n"
        f"Example:\n"
        f"{{1}} Could you please introduce yourself and give us a brief overview of your professional background?"
        )
    return prompt

def fHR_PromptLoop(dAnswer, dLine, dHistory):
    prompt = (
        f"Forget previous instructions \n"
        f"You act as a HR manager\n"
        f"You are interviewing a candidate\n"
        f"The interview history is - {dHistory}\n"
        f"Your last question was - {dLine}\n"
        f"Candidate's answer is - {dAnswer}\n"
        f"Your task is to tell if there could be some additional questions on candidate's last line or we can move to the next question\n"
        f"OUTPUT give in two possible ways:\n"
        f"if additional question then: \n"
        f"{{1}} your question put here\n"
        f"if move to the next question:\n"
        f"{{2}} ok, let's move further\n"
        )
    return prompt

def fHR_PromptHint(dHistory, vLastQuestion):
    prompt = (
        f'Disregard previous instructions.\n'
        f'Carefully analyze the following job interview dialog and suggest the most natural, context-appropriate response to the final HR question.\n'
        f'Provide the answer based on the flow and tone of the conversation.\n'
        f'Dialog for analysis: "{dHistory}"\n'
        f'Final question from HR: "{vLastQuestion}"\n'
        f'Please provide the response in both Russian and English, and ensure it is suitable for a professional setting.\n'
        f'Double-check and refine your output if necessary.\n'
        f'Output format:\n'
        f'{{1}} Русский: ...\n'
        f'{{2}} English: ...'
    )

    return prompt


def fHR_PromptEnd_Eng(dHistory, vUserID, dUserLevel):       #isn't used
    prompt = (
        f"Forget previous instructions \n"
        f"You act as an experienced English teacher. I give you dialogue between AI and a candidate, whose english level is {dUserLevel}1.\n"
        f"Dialogue - {dHistory}\n"
        f"Your task is to analyze candidate's phrases given in a format {{candidate: phrase1}} in the dialogue, identify any mistakes and point possible improvements in the following areas: \n"
        f"- Spelling and Grammar, "
        f"- Dialogue Flow, "
        f"- Vocabulary and Expression, "
        f"- Sentence Structure \n"
        f"Give your answer in russian language \n"
        f"Format: \n"
        f"<b>Spelling and Grammar.</b> Your analisys on Spelling and Grammar topic given in russian language \n"
        f"<b>Dialogue Flow.</b> Your analisys on Dialogue Flow topic given in russian language \n"
        f"<b>Vocabulary and Expression.</b> Your analisys on Vocabulary and Expression topic given in russian language \n"
        f"<b>Sentence Structure.</b> Your analisys on Sentence Structure topic given in russian language \n"
        )
    return prompt

def fHR_PromptEnd_HR(dHistory, dHR_vacancyDesc, vUserID):
    prompt = (
        f"Forget previous instructions \n"
        f"You act as a HR manager. I give you dialogue between HR-manager and a candidate \n"
        f"Dialogue - {dHistory}\n"
        f"Here is a vacancy requirements for the position: {dHR_vacancyDesc}\n"
        f"Your task is to analyse candidate answers and perform analysis does the candidate match the job"
        f"Output give in russian language"
        )
    return prompt

#=================================================================================================================================================== Retell
def fPromptRetellGen(dUserLevel, retellWords):
    arrTheme = [
        'Everyday Life. Daily Routines: Describing a typical day in the life of a worker, or family.', 
        'Everyday Life. Shopping: A trip to the supermarket or mall, focusing on interactions and vocabulary related to shopping.', 
        'Everyday Life. Cooking: Preparing a meal, including ingredients, steps, and interactions in the kitchen.', 
        'Travel and Adventure. Vacations: Stories about trips to different places, highlighting landmarks, cultural experiences, and travel-related vocabulary.', 
        'Travel and Adventure. Outdoor Activities: Hiking, camping, or a day at the beach, focusing on nature-related words and activities.', 
        'Fantasy and Imagination. Fairy Tales: Simplified versions of classic fairy tales or new stories involving magical creatures and adventures.', 
        'Historical Events. Famous Historical Moments: Retelling significant events in history in a simplified and engaging way.', 
        'Historical Events. Biographies: Short stories about famous people and their contributions, focusing on key moments in their lives.', 
        'Moral and Ethical Lessons. Fables: Stories with moral lessons, such as Aesop’s fables, adapted for language learners.', 
        'Moral and Ethical Lessons. Dilemmas: Short stories that present a moral or ethical dilemma, encouraging discussion and reflection.', 
        'Cultural Experiences. Festivals and Holidays: Stories about how different cultures celebrate various holidays and festivals.', 
        'Cultural Experiences. Traditional Tales: Folktales from different cultures, introducing learners to diverse traditions and beliefs.'
        ]
    varTheme = random.choice(arrTheme)
    promtEngLevel = ""
    if dUserLevel == 'A':
        promtEngLevel = f"- should be adapted for elementary english level, sentences are short, words are common and widely used."
    prompt = (
        f"Forget previous instructions \n"
        f"Your task is to create one short story for retelling as a part of learning process\n"
        f"Specifications for the story are:\n"
        f"- a unique story\n"
        f"- consists of not more then 100 words\n"
        f"- must be consistent, complete and with one main idea\n"
        f"{promtEngLevel}\n"
        f"- story theme is '{varTheme}'\n"
        f"- story format is 'Narratives told by a third-Person'\n"
        )
    if retellWords != '': prompt = f"{prompt}- story should contain the following words - {retellWords}"


    return prompt

def fPromptRetellCheck(txtRetell, txtOriginal, vUserEngLevel):
    prompt = (
        f"Forget previous instructions.\n"
        f"You are acting as an experienced English teacher.\n"
        f"I will provide you with a retelling text and the original story.\n\n"
        f"Your task is to analyze the retelling based on the following points:\n"
        f"1. Does the retelling demonstrate a clear understanding of the original story?\n"
        f"2. Point out any mistakes in the retelling, focusing on:\n"
        f"- Grammatical errors (tense issues, subject-verb agreement, etc.)\n"
        f"- Idiomatic/stylistic issues (awkward phrasing, incorrect idioms, etc.)\n\n"
        f"In your analysis DO NOT analyse punctuation\n\n"
        f"3. Identify 10 English words from the original story that are not present in the retelling and have a level of complexity suitable for learning.\n"
        f"List these words in their base (lemma) form, separated by commas, and enclosed in square brackets.\n\n"
        f"Original story: {txtOriginal}\n"
        f"Retelling text: {txtRetell}\n\n"
        f"The OUTPUT must be in Russian, but all examples and word lists should be in English.\n"
        f"The output should not exceed 3000 characters and follow this structure:\n"
        f"{{1}} Результаты анализа: brief results of the analysis in Russian\n"
        f"{{2}} Улучшения: pointed-out mistakes and suggested improvements in Russian\n"
        f"{{3}} Слова, рекомендуемые для изучения: [word1, word2, word3]\n\n"
        f"Example of output:\n"
        f"{{1}} Результаты анализа:\n"
        f"Вы хорошо понимаете основную идею текста ...\n"
        f"{{2}} Улучшения:\n"
        f"1. Вместо 'swollen river' - можно использовать ...\n"
        f"{{3}} Слова рекомендуемые для изучения: [collaboration, deployment, overcome]"
    )
    '''
    prompt = (
        f"Forget previous instructions \n"
        f"You act as an experienced english teacher \n"
        f"I will give you my retelling of an original story. Your task is to analyse retelling and answer the following: \n"
        f"- do I understand the original story and did I managed to convey its meaning?\n"
        f"- point out mistakes in the retelling and suggest improvements\n"
        f"- point out 5 words of the original story in their base lemma form, that seemed to be difficult for me and can be recommended for learning, "
        f"give them as a list devided by comma and put in square brackets."
        f"Content of the original story is:\n{txtOriginal}\n"
        f"The text of my retelling is:\n{txtRetell}\n"
        f"The OUTPUT must be given in russian, should not exceed 3000 symbol length and must have the following structure:\n"
        f"{{1}} Результаты анализа:\n brief results of the analysis in russian\n"
        f"{{2}} Улучшения:\n pointed mistakes and suggested improvements in russian\n"
        f"{{3}} Слова рекомендуемые к изучению:  [word1, word 2, word 3]\n"
        f"Output example:\n"
        f"{{1}}Результаты анализа:\n"
        f"Вы хорошо понимаете основную идею текста ...\n"
        f"{{2}} Улучшения:\n"
        f"1. Вместо 'swollen river' - можно использовать ...\n"
        f"{{3}} Слова рекомендуемые к изучению: [collaboration, deployment, overcome]"
        )
    '''
    return prompt


def fPromptSimpleTransText(vText):
    prompt = (
        f"Translate into russian the following text - {vText}"
        )
    return prompt

#=================================================================================================================================================== Monolog
def fPromptTransAlt(vText):
    '''
    prompt = (
        f"Forget previous instructions \n"
        f"You act as a translator from english into russian. \n"
        f"A word for translation is '{vText}'. \n"
        f"Give possible translations of the word in case if the meaning of the translation significantly differs. \n"
        f"Every return word must be in its base lemma form. \n"
        f"Format: {{English}} - (Russian) - [possible translation1, possible translation2] \n"
        f"Examples: \n"
        f"{{tense}} - (напряженный) - [время, возбужденный] \n"
        f"{{fly}} - (муха) - [летать, ширинка]"
        )
    '''
    prompt = (
        f"You are an expert translator from English to Russian. \n"
        f"Your task is to translate the English word '{vText}' accurately, ensuring that **only Russian words are returned**. "
        f"Any response containing English words, transliterations, or Latin characters is incorrect. \n\n"

        f"### Follow this structured reasoning step-by-step: \n"
        f"1. Identify all possible meanings of '{vText}' in English. \n"
        f"2. Prioritize the most commonly used meaning first, based on frequency in modern usage. \n"
        f"3. Find the most accurate Russian translation for every meaning from steps 1 and 2, "
        f"ensuring the translation **exists in Russian** and is **grammatically correct**. \n"
        f"4. Ensure that each Russian translation is in its **base lemma form** (infinitive for verbs, singular nominative for nouns, etc.). \n"
        f"5. Verify that **all output words are strictly in Russian Cyrillic script**. "
        f"Do not return any English words, transliterations, or words containing Latin characters. \n"
        f"6. If a direct translation does not exist, select the **most semantically correct Russian word**, but **never use English** as a fallback. \n"
        f"7. **Final Validation:** Before submitting the response, check again that every word is in **Russian Cyrillic script only** and that no English words are included. \n\n"

        f"### Format your response strictly as follows: \n"
        f"Translation1, Translation2, Translation3 \n"

        f"### Limitations:\n"
        f"- **No English words allowed in the output.**\n"
        f"- **Only Russian Cyrillic characters should be used.**\n"
        f"- **No transliterations of English words.**\n\n"

        f"### Output Example for 'tense': \n"
        f"напряжённый, время, возбуждённый \n"
        f"### Output Example for 'fly': \n"
        f"муха, летать, ширинка \n"

        f"Now, provide the translation for '{vText}' following these steps and format."
    )
    systemPrompt = "You are an expert English-to-Russian translator"

    return prompt, systemPrompt

def fPromptMonologCheck(strOriginal):
    prompt = (
        f"You act as an experienced English teacher.\n"
        f"I will provide you with a text\n\n"
        f"Your task is to analyze the text, focusing on:\n"
        f"- Grammatical errors (tense issues, subject-verb agreement, etc.)\n"
        f"- Idiomatic/stylistic issues (awkward phrasing, incorrect idioms, etc.)\n\n"
        f"In your analysis DO NOT analyse punctuation\n\n"
        f"The given phrase is: {strOriginal}\n\n"
        f"Provide a corrected or improved version.\n"
        f"In addition, suggest some synonym words from the phrase that would be useful for vocabulary building.\n"
        f"Ensure the synonyms are in their base (lemma) form.\n\n"
        f"Structure your response as follows:\n"
        f"{{1}} Improved message: your answer\n"
        f"{{2}} Analysis: your answer (Mistakes should be explained in Russian, while retaining references to the original English words)\n"
        f"{{3}} Synonym suggestions: word1 (synonym1, synonym2); word2 (synonym1, synonym2)\n\n"
        f"Example response for the given phrase 'Sure, I can talk. Let's discuss something. I don't know what. I have a great weekend. Thank you.' is:\n"
        f"{{1}} Improved message: Sure, I can talk. Let's discuss something. I don't know what. I hope you have a great weekend. Thank you.\n"
        f"{{2}} Mistakes: Фраза в целом корректна, с незначительной ошибкой в замене I have на I hope.\n"
        f"{{3}} Synonym suggestions: Sure (certain, positive); discuss (converse, debate); great (fantastic, excellent); thank you (appreciate, gratitude)"
    )
    '''
    prompt = (
        f"The given phrase is: {strOriginal}\n"
        f"Please point out any mistakes in the phrase, focusing on:\n"
        f"- Grammatical errors: Tense issues, subject-verb agreement, punctuation, etc.\n"
        f"- Idiomatic/stylistic issues: Awkward phrasing or incorrect idioms.\n\n"
        f"Provide a corrected or improved version.\n"
        f"In addition, suggest some synonym words from the phrase that would be useful for vocabulary building.\n"
        f"Ensure the synonyms are in their base (lemma) form.\n\n"
        f"Structure your response as follows:\n"
        f"{{1}} Improved message: your answer\n"
        f"{{2}} Mistakes: your answer (Mistakes should be explained in Russian, while retaining references to the original English words)\n"
        f"{{3}} Synonym suggestions: word1 (synonym1, synonym2); word2 (synonym1, synonym2)\n\n"
        f"Example response for the given phrase 'Sure, I can talk. Let's discuss something. I don't know what. I have a great weekend. Thank you.' is:\n"
        f"{{1}} Improved message: Sure, I can talk. Let's discuss something. I don't know what. I hope you have a great weekend. Thank you.\n"
        f"{{2}} Mistakes: Фраза в целом корректна, с незначительной ошибкой в замене I have на I hope.\n"
        f"{{3}} Synonym suggestions: Sure (certain, positive); discuss (converse, debate); great (fantastic, excellent); thank you (appreciate, gratitude)"
    )    
    prompt = (
        f"The given phrase is - {strOriginal} \n"
        f"Point out mistakes in the given phrase and send correct/improved message. \n"
        f"Additionaly suggest please some synonym words based on the given phrase one could start learning. \n"
        f"The synonyms must be in their base lemma form \n"
        f"Response please give in the following structure:\n"
        f"{{1}} Improved message is - your answer \n"
        f"{{2}} Mistakes are - your answer (Mistakes must be indicated in Russian while preserving references to English words in English)\n"
        f"{{3}} Synonym words are - word1 (synonyms1 for the word1, synonym2 for the word1); word2(synonyms1 for the word2, synonym2 for the word2)\n"
        f"Example of response for given phrase 'Sure, I can talk. Let''s discuss something. I don''t know what. I have a great weekend. Thank you.' is the following:\n"
        f"{{1}} Improved message is - Sure, I can talk. Let''s discuss something. I don''t know what. I hope you have a great weekend. Thank you.\n"
        f"{{2}} Mistakes are - Фраза в целом корректна с незначительной ошибкой в замене I have на I hope\n"
        f"{{3}} Synonym words are - Sure (certain, positive); discuss (converse, debate); great (fantastic, excellent); thank you (appreciate, gratitude)\n"
        )
    '''
    return prompt

        
def fPromptNews(vNewsTxt, vCat, vLevel = 2):
    if vCat == '1':      #abridge article
        if vLevel == 2: strLevel = 'intermediate'
        elif vLevel == 1: strLevel = 'beginner'
        elif vLevel == 3: strLevel = 'advanced'
        prompt = (
            f"Abridge the given news article for an {strLevel}-english-level audience:\n"
            f"- Maintain the newspaper's formal style and tone;\n"
            f"- Simplify vocabulary and sentence structure to suit reader's level while preserving the article's main points.\n"
            f"In case if bold format is needed use only <b> tags. Do not use any other HTML tags.\n"
            f"Do not put any additional information, title, etc., just make given text simplification\n"
            f"Article Text:\n"
            f"{vNewsTxt}"
        )
        return prompt
    elif vCat == '3':    #abridge title
        if vLevel == 2:
            strLevel = 'intermediate'
        elif vLevel == 1:
            strLevel = 'beginner'
        elif vLevel == 3:
            strLevel = 'advanced'

        prompt = (
            f"Abridge the given text for an {strLevel}-english-level audience:\n"
            f"- Simplify vocabulary and sentence structure to suit reader's level while preserving the text's main points.\n"
            f"Do not put any additional information, just make given text simplification\n"
            f"Input Text:\n"
            f"{vNewsTxt}"
        )
        return prompt
    elif vCat == '2':   #analyse words
        if vLevel == 2:
            strLevel = 'the Intermediate level (B1)'
            srtRemoveRule = "Basic vocabulary (e.g., pronouns, conjunctions, prepositions, high-frequency verbs)"
            srtKeepRule1 = ""
            srtKeepRule2 = ""
            srtKeepRule3 = ""
        elif vLevel == 1:
            strLevel = 'the Beginner level (A1-A2)'
            srtRemoveRule = 'A1-A2 vocabulary, such as high-frequency verbs, simple adjectives, prepositions, conjunctions, and pronouns.'
            srtKeepRule1 = " (B1 and above)."
            srtKeepRule2 = "- Less frequent in everyday beginner-level English.\n"
            srtKeepRule3 = "Useful for expanding vocabulary beyond A1-A2."
        elif vLevel == 3:
            strLevel = 'the Advanced level (B2-C1-C2)'
            srtRemoveRule = "Basic vocabulary (e.g., pronouns, conjunctions, prepositions, high-frequency verbs)"
            srtKeepRule1 = ""
            srtKeepRule2 = ""
            srtKeepRule3 = ""

        prompt = (
            f"I will provide an input list of English words separated by colons (:).  \n\n"
            f"Your task is to filter out words based on the following criteria for English learners at {strLevel}:  \n"
            f"- Remove common and basic words, including:\n"
            f"  - {srtRemoveRule}   \n"
            f"  - Proper nouns (e.g., names, places).\n"
            f"  - Abbreviations (e.g., NASA, USA).\n\n"
            f"- Convert plurals and inflected forms to their base singular form (e.g., 'changes' → 'change', 'running' → 'run').\n\n"
            f"Keep only words that are:  \n"
            f"- Uncommon, academic, or advanced{srtKeepRule1}.  \n"
            f"{srtKeepRule2}"
            f"- {srtKeepRule3}\n\n"
            f"Instructions for Output:  \n"
            f"- Use lemmatization to convert words to their base forms.\n"
            f"- Ensure the output contains only a colon-separated list of words in lowercase\n"
            f"- Ensure there are no duplicates or additional text.\n\n"
            f"Examples:  \n"
            f"Input: 13year:an:and:assad:be:capabilities:civil:but:conflict:another:decimated  \n"
            f"Output: capability:decimate  \n\n"
            f"Now process the following input list:  \n"
            f"{vNewsTxt}  "
        )


        '''
        prompt = (
            f"I will give input list of english words separated by ':'.\n"
            f"Your task is to filter out words that are considered common and simple for an English learner at level {strLevel}, "
            f"based on frequency and basic vocabulary lists (such as NGSL or CEFR A1-A2).\n"
            f"Keep only the words that are uncommon, academic, or advanced.\n"
            f"Instructions:\n"
            f"- Remove basic words, including pronouns, conjunctions, prepositions, and high-frequency verbs.\n"
            f"- Keep words that are rare, subject-specific, or academic.\n"
            f"- Use lemmatization to unify different word forms.\n"
            f"- Ensure the output contains only a colon-separated list of words in lowercase, without duplicates. No additional text allowed\n"
            f"Example:\n"
            f"Input: 13year:an:and:assad:be:capabilities:civil:but:conflict:another:decimated\n"
            f"Output: capabilities:civil:conflict:decimated\n\n"
            f"Input list:\n"
            f"{vNewsTxt}"
        )
        '''
        return prompt

def fPromptNewsTopic(vSummary, vTitle):
    prompt = (
        f"I will provide the title and first paragraph of a newspaper article.\n"
        f"Your task: Determine the most suitable topic from the following options:\n"
        f"1 - Politics\n"
        f"2 - Art and Culture\n"
        f"3 - Environment\n"
        f"4 - Business and Economy\n"
        f"5 - Education\n"
        f"6 - Health\n"
        f"7 - Science\n"
        f"Instructions:\n"
        f"- Analyze the key themes in the title and paragraph. \n"
        f"- Select the single best-matching topic from the list.\n"
        f"- Your output must be a single digit (1-7) with no additional text.\n"
        f"Example:\n"
        f"Title - US pressure has forced Panama to quit China’s Belt and Road Initiative – it could set the pattern for further superpower clashes\n"
        f"Text - Following Donald Trump’s repeated claims that the US needs to “take back” the Panama canal from Chinese control, the US secretary of state, "
        f"Marco Rubio, visited Panama to demand the country reduce China’s influence. On the surface, it seems Rubio has succeeded.\n"
        f"Output - 1\n"
        f"Now classify the following article: \n"
        f"Title - {vTitle}\n"
        f"Paragraph - {vSummary}"
    )
    return prompt

def fPromptReminder(numIsIdiom, vObj, vStage=1):
    if vStage == 1:
        if numIsIdiom == 1: #idiom
            prompt = f'''
                Generate a catchy and engaging educational blog post in Russian about the input idiom. The idiom should remain in English within the text. The post should:
                Include lots of appropriate emojis to the text.
                Stracture of the post should be:
                - title (put emoji in the end)
                - where is used (GB or UK or AU or all)?
                - idiom's meaning (put emojis)
                - origin if applicable (put emojis)
                - 4 usage examples in english by bullets with translate into Russian in most appropriate and natural way.
                Translate cover in <i>-tags (put emojis)
                Limit of overall text is 1000 letters
                Double factcheck the origin section
                Format the output using <b> and <i> tags: Use <b> for important terms (e.g., the idiom and key facts) and <i> for explanations or additional context. Do not use any other HTML tags.
                Always start with 🕊️ emoji
                
                Example:
                    🕊️ <b>Idiom "..."</b>
                    
                    <b>🌍 Используется в:</b> 🇺🇸, 🇬🇧
                    
                    <b>Значение идиомы</b>
                    <i>...</i>
                    
                    <b>Происхождение</b>
                    <i>...</i>
                    
                    <b>Примеры использования:</b>
                    🔸 "..."
                      <i>— ...</i>
                Input idiom:{vObj}
            '''
        elif numIsIdiom == 2:  # slang
            prompt = f'''
                Generate a catchy and engaging educational blog post in Russian about the input slang word. The slang word itself should remain in English within the text. The post must:
                Start with the 🕊️ emoji.
                Use a clear structure:
                Title (must be in English): Include the 'slang' word and end with an emoji. Example - 🕊️ <b>Slang "Tea" 🍵</b>
                Give transcription of a word wraped in <code>-tags
                Usage Region: Indicate where the slang is primarily used (e.g., 🇺🇸 for the US, 🇬🇧 for the UK, 🇦🇺 for Australia).
                Meaning: Provide a brief explanation of the slang's meaning (include appropriate emojis).
                Origin: Describe the slang's origin, if applicable (include emojis).
                Examples: Provide four usage examples in English. Translate each example into Russian in most appropriate and natural way, wrapping the translation in <i> tags (include emojis).
                Double factcheck the origin section
                Use <b> for important terms (e.g., the slang and key facts) and <i> for explanations or additional context. Avoid other HTML tags.
                Limit the overall text to 1000 characters.
                Example:
                    🕊️ <b>Slang "Tea" 🍵</b>
                    <code>[tˈi]</code>
                    
                    <b>🌍 Используется в:</b> 🇺🇸, 🇬🇧, 🇦🇺
                    
                    <b>Значение</b>
                    <i>"Tea" в сленге означает информацию или слухи, особенно касающиеся чьих-то личных дел. Это слово используется, чтобы рассказать интересную или сенсационную новость.</i> 🗣️💬
                    
                    <b>Происхождение</b>
                    <i>Термин "tea" вероятно происходит от фразы "spill the tea", что означает "выливать секреты", которая стала популярной в социальных сетях и среди молодежи.</i> ☕🕵️‍♂️
                    
                    <b>Примеры использования:</b>
                    🔸 "Do you have any tea on him?" 
                      <i>— Есть ли у тебя какие-нибудь слухи о нем?</i> 🧐💭
                    🔸 "She spilled the tea about their breakup." 
                      <i>— Она рассказала сплетни о их расставании.</i> 💔🗣️
                    🔸 "Give me the tea, I want to know everything!"
                      <i>— Расскажи все, я хочу все знать!</i> 🤐🍵
                    🔸 "Everyone is talking about the tea from last night’s party."
                      <i>— Все обсуждают слухи с вечеринки прошлой ночью.</i> 🎉👀
                Input slang: {vObj}
            '''
    elif vStage == 2:
        if numIsIdiom == 1:
            vTopic = 'idiom'
        elif numIsIdiom == 2:
            vTopic = 'slang'
        prompt = f'''
            You are a quiz builder AI. Generate 4 answer options for a multiple-choice quiz based on the meaning 
            of a given English {vTopic} expression.
            Instructions:
            - One option must be the correct meaning.
            - Three options must be incorrect but plausible (i.e. commonly mistaken or similar in tone/theme).
            - Also provide one example sentence using the {vTopic} in natural context to help users guess.
            
            A must format:
            {{1}} Correct meaning
            {{2}} Incorrect option 1
            {{3}} Incorrect option 2
            {{4}} Incorrect option 3
            {{5}} Example sentence using the {vTopic}
            Example for Slang "Big mood":
            {{1}} A strong feeling or vibe that someone can relate to
            {{2}} A large physical object that is difficult to carry
            {{3}} A term used to describe a party or celebration
            {{4}} An act of showing off wealth or status
            {{5}} When she said she wanted to stay in bed all day, I felt that—it’s a big mood!
                        
            Input {vTopic}: {vObj}
        '''

    return prompt

def fPromptFS(text, user_level, history=''):
    str_history = f'CONVERSATION HISTORY:\n{history}' if history else ''

    promptSys = f"""
        You are an experienced and friendly English teacher having a natural conversation with your student. 
    
        YOUR APPROACH:
        - If the student makes errors, gently correct them in a natural, conversational way
        - Focus only on 1-2 most important issues to avoid overwhelming
        - Use encouraging transitions like "I understand! Just to note..." or "Great point! By the way..."
        - After any corrections, smoothly continue with phrases like "Now, let's continue our chat..." or "Anyway, back to our conversation..."
        - Mention they can use the "Grammar Check" button for more detailed explanations if needed
    
        YOUR CONVERSATION STYLE:
        - Act as a friendly teacher meeting the student for the first time
        - Ask about their interests, background, goals, job, and life in a natural smalltalk manner
        - Adapt your language level to match the student's proficiency
        - Keep the conversation flowing with follow-up questions
        - Be warm, encouraging, and genuinely interested
    
        STUDENT CONTEXT:
        Student's English level: {user_level}
        {str_history}
        
        Remember: Respond in one seamless paragraph that feels like natural conversation - no separate sections or formatting!
    """


    promptUser = f"""
        CONVERSATION CONTEXT: This is a free speech conversation on any theme between teacher and student.
    
        STUDENT'S LATEST MESSAGE: "{text}"
    
        Please respond naturally as the friendly teacher, providing gentle corrections if needed and continuing the getting-to-know-you conversation in a seamless way.
    """
    return promptSys, promptUser

def fPromptStart(text, user_level, user_goals, conversation_history = ''):
    # Improved system prompt with clear structure and examples
    if conversation_history:
        conversation_history = f'CONVERSATION HISTORY: {conversation_history}'
    promptSys = f"""
        You are an experienced and friendly English teacher having a natural conversation with your student during a first meeting smalltalk scenario.
        
        Your response must be divided into exactly TWO parts:
        
        ## PART 1: CORRECTIONS
        - If the student's message has errors: Provide 1-2 gentle corrections using encouraging language
        - If no errors: Acknowledge their message positively  
        - Limit: 300 characters including spaces
        - Use format: "{{Corrections}}: [your feedback]"
        
        ## PART 2: CONVERSATION (for voice synthesis)
        - Continue the natural first-meeting conversation
        - Ask engaging follow-up questions about their background, interests, goals
        - Match their English proficiency level
        - Limit: 200 characters including spaces  
        - Use format: "{{Teacher}}: [your response]"
        
        ## EXAMPLES:
        **Example 1 (with errors):**
        Input student's text: "I am come from Japan and I studying English for 2 year."
        OUTPUT:
        {{Corrections}}: Great! Small note: "I come from Japan and I've been studying English for 2 years." The present perfect tense works better here.
        {{Teacher}}: How wonderful! What inspired you to start learning English? Are you planning to use it for work or travel?
        
        **Example 2 (no errors):**
        Input student's text: "I love reading books, especially mystery novels. What about you?"
        OUTPUT:
        {{Corrections}}: Perfect grammar and great topic choice! I can see you have strong English skills.
        {{Teacher}}: I'm a mystery fan too! Have you read any English mystery novels yet? I could recommend some great ones for your level.
        
        **Example 3 (beginner level):**
        Input student's text: "Me like music very much. You like music?"
        OUTPUT:
        {{Corrections}}: Nice! Try: "I like music very much. Do you like music?" Remember to use "I" and "do" for questions.
        {{Teacher}}: Yes, I love music! What kind of music do you enjoy? Rock, pop, classical?
        
        ## STUDENT CONTEXT:
        Student's English level: {user_level}
        Learning goals: {user_goals}
        
        Respond as the friendly teacher, always using both parts in the exact format shown.
    """
    promptUser = f"""
        CONVERSATION CONTEXT: This is a first meeting smalltalk conversation between teacher and student, getting to know each other.
    
        STUDENT'S LATEST MESSAGE: "{text}"
        {conversation_history}
    
        Please respond naturally as the friendly teacher, providing gentle corrections if needed and continuing the getting-to-know-you conversation in a seamless way.
    """

    #- Ask about their interests, background, goals, and life in a natural smalltalk manner
    return promptSys, promptUser



'''
    promptSys = f"""
You are an experienced and friendly English teacher having a natural conversation with your student. This is a first meeting smalltalk scenario where you're getting to know each other.

YOUR APPROACH:
- If the student makes errors, gently correct them in a natural, conversational way
- Focus only on 1-2 most important issues to avoid overwhelming
- Use encouraging transitions like "I understand! Just to note..." or "Great point! By the way..."
- After any corrections, smoothly continue with phrases like "Now, let's continue our chat..." or "Anyway, back to our conversation..."
- Mention they can use the "Grammar Check" button for more detailed explanations if needed

YOUR CONVERSATION STYLE:
- Act as a friendly teacher meeting the student for the first time
- Ask about their interests, background, goals, and life in a natural smalltalk manner
- Adapt your language level to match the student's proficiency
- Keep the conversation flowing with follow-up questions
- Be warm, encouraging, and genuinely interested

STUDENT CONTEXT:
Student's English level: {user_level}
Learning goals: {user_goals}

Remember: Respond in one seamless paragraph that feels like natural conversation - no separate sections or formatting!
    """

#CONVERSATION HISTORY:
#{conversation_history}

    promptUser = f"""
CONVERSATION CONTEXT: This is a first meeting smalltalk conversation between teacher and student, getting to know each other.

STUDENT'S LATEST MESSAGE: "{text}"

Please respond naturally as the friendly teacher, providing gentle corrections if needed and continuing the getting-to-know-you conversation in a seamless way.
    """
    
'''
#
'''
promptSys = """
    You are an experienced and friendly English teacher conducting a conversational lesson. Your role has two parts:

    ## PART 1: GENTLE CORRECTIONS (if needed)
    - If the user's message contains errors, provide brief, encouraging corrections
    - Focus only on 1-2 most important issues to avoid overwhelming
    - Use positive language: "Great attempt! Just a small note..." or "I understand you perfectly! One tiny adjustment..."
    - Suggest they can use the "Grammar Check" button for more details

    ## PART 2: CONTINUE CONVERSATION
    - Stay in character as a teacher in a realistic scenario (cafe, job interview, travel, etc.)
    - Ask engaging follow-up questions to keep conversation flowing
    - Adapt your language level to match the student's proficiency
    - Be encouraging and create a safe learning environment

    ## FORMAT YOUR RESPONSE:
    {Corrections}: [Only if needed - keep brief and positive]
    {Teacher}: [Your response in the role-play scenario]

    ## CURRENT SCENARIO: {scenario}
    You are roleplaying as: {teacher_role}
    Student's English level: {user_level}
    Learning goals: {user_goals}

    Remember: Be conversational, supportive, and educational!"""

'''

'''
promptSys = """
        You act as an English teacher
        You are playing educational dialog with a user
        I give you last user phrase
        Your task is to check user's phrase on grammar, naturalness, fluency - give some advices, tell him that he could use buttom "grammar check"
        for more details on grammar
        Then you go back to dialog and provide him next dialog phrase
    """
'''


# ============================================================================
# TASK 6: AI PROMPT FUNCTION
# ============================================================================

def fPromptTask6Reading(topic_name: str, template_ai_prompt: str) -> str:
    """
    Формирование промпта для генерации текста и вопросов через AI

    Args:
        topic_name: Название темы интересов пользователя
        template_ai_prompt: Промпт из c_ai_prompt таблицы шаблонов

    Returns:
        str: Готовый промпт для отправки в AI
    """

    # Используем базовый промпт из шаблона и подставляем тему
    prompt = template_ai_prompt.replace("{user_interest_topic}", topic_name)

    # Добавляем инструкцию по формату ответа
    prompt += """

IMPORTANT: Return ONLY valid JSON in this exact format, no additional text:
{
  "title": "Article Title",
  "text": "Full text of the reading passage (50-80 words)...",
  "word_count": 65,
  "questions": [
    {
      "question": "Question text?",
      "options": {
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
      },
      "correct_answer": "B",
      "explanation": "The text states: '...'"
    }
  ]
}

Generate exactly 4 questions. Make sure all JSON is valid and properly formatted.
"""

    return prompt
