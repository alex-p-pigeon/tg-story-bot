import copy

dict_base = {
    'menu': "❰❰❰ ☰ Menu",
    'back': "❰ Back",
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
    'inv': "🎒 Inventory",
    'look': "🔍 Look around",
    'pause': "⏸️Pause story",
    'next_scene': "✅ Next ❱❱",
    #'exit': "✅ Exit story ❱❱",
    'exit': "✅ Results ❱❱",
    'story': "🎭 Stories",
    'st_reset': "🔄 Reset & Start Over",
    'st_cont': "▶️ Continue",
    'st_list': "🔍 Stories list",
    'st_grammar': "📝 Grammar",
    'st_action': "🎬 Action",
    'st_action_txt': "perform an action on npc",
    'inv_txt': "check Inventory",
    'vB_st3': "💎 Subscribe",
    'vB_st3_rub': "💳 ₽",
    'vB_st3_usd': "🌍 ₽",
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
        'pause_txt': "выйти из модуля историй (текущий прогресс сохранится)",
        'next_scene_txt': "✅ Сцена завершена! Можно перейти далее",
        'st_grammar_txt': "проверь грамматику",
        'st_action_txt': "выполни действие на npc",
        'exit_txt': "выйти. История завершена",
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
        'fs_hint': '❗️ <b>Send an audio or text response to continue the dialogue</b>',
        'pause_txt': "exit the Stories module (your current progress will be saved)",
        'next_scene_txt': "✅ The scene is complete! You can move on",
        'st_grammar_txt': "check your grammar",
        'st_action_txt': "perform an action on npc",
        'exit_txt': "exit. Story is finished",
    }
)

dict_all = {
    'ru': dict_ru,
    'en': dict_en,
}


#function for uniform text messages     fCSS('native')
def fCSS(vMark, vLang = 'ru'):
    return dict_all.get(vLang, dict_en).get(vMark, f"[Missing: {vMark}]")
