LearnPath Module

Модуль персонализированной программы обучения английскому языку для Telegram-бота.

## Структура
learnpath/
+-- router.py              # Главный router
+-- handlers/              # Обработчики событий
¦   +-- assessment.py      # Тестирование уровня
¦   +-- interests.py       # Опрос интересов
¦   +-- generation.py      # Генерация программы
¦   +-- viewing.py         # Просмотр программы
¦   +-- learning.py        # Обучение (модули)
¦   +-- practice.py        # Практические задания
¦   +-- testing.py         # Тесты
¦   L-- management.py      # Управление программой
+-- services/              # Бизнес-логика
¦   +-- learnpath_service.py
¦   +-- assessment_service.py
¦   +-- progress_service.py
¦   L-- content_service.py
+-- database/              # SQL и модели
¦   +-- queries.py
¦   L-- models.py
L-- utils/                 # Вспомогательные функции
+-- keyboards.py
+-- messages.py
L-- validators.py

## Использование

### Импорт в главный файл
```python
from handlers.learnpath import r_learnpath

dp.include_router(r_learnpath)
Команды

/learnpath - Доступ к программе обучения

Callback данные

learnpath_start - Начало создания программы
view_learnpath - Просмотр программы
continue_learning - Продолжить обучение
И другие (см. handlers)

FSM States
pythonmyState.learnpath_assessment      # Оценка уровня
myState.learnpath_interests       # Опрос интересов
myState.learnpath_active          # Активная программа
myState.learnpath_practice_text   # Текстовая практика
myState.learnpath_practice_voice  # Голосовая практика
myState.learnpath_practice_dialogue # Диалоговая практика
myState.learnpath_module_test     # Тест модуля
myState.learnpath_topic_test      # Финальный тест
Зависимости

aiogram 3.x
asyncpg (через fpgDB)
selfFunctions (AI, транскрипция, грамматика)
states (FSM states)

Разработка
Добавление нового handler

Создать файл в handlers/
Создать Router
Добавить handlers
Зарегистрировать в router.py

Добавление нового service

Создать файл в services/
Создать класс с методами
Добавить импорт в services/__init__.py

Тестирование
bash# Запуск бота в тестовом режиме
python eng_main.py
Логирование
Все действия логируются через fpgDB.fExec_LogQuery():

learnpath_init
assess_level_start
module_test_complete
И т.д.

Поддержка
При возникновении проблем:

Проверить логи БД
Проверить FSM states
Проверить callback_data


---

## Итоговая структура проекта
project/
+-- eng_main.py                          # ? Главный файл (обновлен)
+-- states.py                            # ? FSM states (обновлены)
+-- selfFunctions.py                     # Существующий
+-- fpgDB.py                             # Существующий
+-- prompt.py                            # Существующий
¦
L-- handlers/
+-- start_handlers.py                # Существующий
+-- other_handlers.py                # Существующие handlers
¦
L-- learnpath/                       # ? НОВЫЙ МОДУЛЬ
+-- init.py                  # ? Экспорт r_learnpath
+-- router.py                    # ? Главный router
+-- README.md                    # ? Документация
¦
+-- handlers/                    # ? Sub-handlers
¦   +-- init.py
¦   +-- assessment.py            # ? Тестирование уровня
¦   +-- interests.py             # ? Опрос интересов
¦   +-- generation.py            # ? Генерация программы
¦   +-- viewing.py               # ? Просмотр программы
¦   +-- learning.py              # ? Обучение
¦   +-- practice.py              # ? Практика
¦   +-- testing.py               # ? Тесты
¦   L-- management.py            # ? Управление
¦
+-- services/                    # ? Бизнес-логика
¦   +-- init.py
¦   +-- learnpath_service.py     # ? Работа с программой
¦   +-- assessment_service.py    # ? Оценка уровня
¦   +-- progress_service.py      # ? Прогресс
¦   L-- content_service.py       # ? Контент
¦
+-- database/                    # ? SQL и модели
¦   +-- init.py
¦   +-- queries.py               # ? SQL запросы
¦   L-- models.py                # ? Dataclasses
¦
L-- utils/                       # ? Вспомогательные
+-- init.py
+-- keyboards.py             # ? Клавиатуры
+-- messages.py              # ? Сообщения
L-- validators.py            # ? Валидация

## Преимущества новой структуры

1. ? **Модульность** - каждый компонент в отдельном файле
2. ? **Переиспользование** - services можно использовать везде
3. ? **Тестируемость** - легко тестировать каждый модуль
4. ? **Масштабируемость** - легко добавлять новый функционал
5. ? **Читаемость** - понятная структура и навигация
6. ? **Независимость** - learnpath не влияет на другие handlers
7. ? **Совместимость** - интегрируется в существующую структуру

Готово! Теперь у вас есть полная структура модуля LearnPath с разделением на handlers, services, database layer и utils. Можете начинать миграцию по чеклисту! ??