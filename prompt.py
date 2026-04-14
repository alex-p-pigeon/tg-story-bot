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


#=================================================================================================================================================== HR
       

#=================================================================================================================================================== Retell


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

