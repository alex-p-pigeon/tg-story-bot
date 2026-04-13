from aiogram.fsm.state import State, StatesGroup

'''
c_subscription_status 
1 - активна
2 - активна, но запустили приостановку
3 - первичное создание пользователя
9 - таймаут
10 - блокировка
6, 7 - speakpall
'''

class myState(StatesGroup):
    init = State()
    common = State()
    listen = State()
    listenSend = State()
    listenReceived = State()
    monolog = State()
    dialog = State()
    dialogHR = State()
    dialogHR_job = State()
    dialogHR_job2 = State()
    dialogHR_CV = State()
    dialogHR_CV2 = State()
    words = State()
    speak = State()
    settings = State()
    retell = State()
    retell2 = State()
    daily = State()
    qstart = State()
    prices = State()
    edu = State()
    edu01 = State()
    edu02 = State()
    edu03 = State()
    edu04 = State()
    edu04_2 = State()
    edu05 = State()
    edu06 = State()
    edu07 = State()
    edu08 = State()
    edu08_q = State()
    edu08_q2 = State()
    edu08_m = State()
    edu08_m2 = State()
    edu09 = State()
    edu09_CV = State()
    edu09_CV2 = State()
    edu09_job = State()
    edu09_job2 = State()
    edu09_hr = State()
    edu09_hr2 = State()
    edu10 = State()
    reminder = State()
    genreminder = State()
    newstransOff = State()
    newstransOn = State()
    test = State()
    techlink = State()
    varA_st0 = State()
    varA_st1 = State()
    varA = State()
    varA_bas = State()
    varA_news = State()
    varA_pay = State()
    buy_m = State()
    buy_q = State()
    buy_y = State()
    buy_w = State()
    fs = State()

    varB_st2 = State()
    varB_st3 = State()
    varB_st4 = State()
    varB_st5 = State()

    # Curriculum states
    curriculum_assessment = State()  # Начальная оценка
    curriculum_interests = State()  # Определение интересов
    curriculum_active = State()  # Активная программа
    curriculum_practice_text = State()  # Текстовая практика
    curriculum_practice_voice = State()  # Голосовая практика
    curriculum_practice_dialogue = State()  # Диалоговая практика
    curriculum_module_test = State()  # Тест модуля
    curriculum_topic_test = State()  # Финальный тест темы

    learnpath_assessment = State()  # Начальная оценка уровня
    learnpath_interests = State()  # Определение интересов
    learnpath_active = State()  # Активная программа
    learnpath_practice_text = State()  # Текстовая практика
    learnpath_practice_voice = State()  # Голосовая практика
    learnpath_practice_dialogue = State()  # Диалоговая практика
    learnpath_module_test = State()  # Тест модуля
    learnpath_topic_test = State()  # Финальный тест темы

    task4_listen_speak = State()
    task5_listen_write = State()
    task6_reading = State()
    task7_word_repeat = State()
    #task8_dialog = State()
    #task8 = State()

    # ========================================
    # Task 8: Story System
    # ========================================

    # Опросник (5 вопросов)
    task8_questionnaire_q0 = State()
    task8_questionnaire_q1 = State()  # Вопрос 1: Жанр
    task8_questionnaire_q2 = State()  # Вопрос 2: Настроение
    task8_questionnaire_q3 = State()  # Вопрос 3: Реалистичность
    task8_questionnaire_q4 = State()  # Вопрос 4: Стиль (множественный выбор)
    task8_questionnaire_q5 = State()  # Вопрос 5: Главная цель

    # Выбор продолжить или начать новую историю
    task8_choose_continue_or_restart = State()

    # Активная история (общий режим)
    task8_story_active = State()

    # Диалог с NPC
    task8_story_dialogue = State()

    '''
    task8_story = State()
    story_creation_waiting = State()
    story_creation_genre = State()
    story_creation_mood = State()
    story_creation_realism = State()
    story_creation_complexity = State()
    story_creation_goal = State()
    story_creation_confirmation = State()
    story_creation_generating = State()

    waiting_start = State()      # Ожидание начала
    genre = State()               # Шаг 1: Жанр
    mood = State()                # Шаг 2: Настроение
    realism = State()             # Шаг 3: Реалистичность
    complexity = State()          # Шаг 4: Стиль (2 варианта)
    goal = State()                # Шаг 5: Цель
    confirmation = State()        # Шаг 6: Подтверждение
    generating = State()          # Процесс генерации
    '''

    waiting_for_start = State()
    in_test = State()
    viewing_results = State()

    # price01 = State()
    # prices_1_m = State()
    # prices_0_m = State()
    # prices_1_m2 = State()
    # prices_0_m2 = State()
    # prices_1_q = State()
    # prices_0_q = State()
    # prices_1_q2 = State()
    # prices_0_q2 = State()
    # prices_t_q = State()
    # prices_t_m = State()