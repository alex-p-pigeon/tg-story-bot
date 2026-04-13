"""
Task 6 Reading Service
======================

Сервис для генерации текстов для чтения через AI с поддержкой:
- Различных типов текстов (Email, Story, News, etc.)
- Персонализации по топикам пользователя
- Валидации и fallback логики
- Отслеживания прогресса

Author: AI Assistant
Date: 2025
"""

import json
import random
import hashlib
from typing import Dict, Any, List, Optional, Tuple
import logging

import fpgDB as pgDB
import selfFunctions as myF


logger = logging.getLogger(__name__)


class Task6ReadingService:
    """Сервис для работы с заданиями на чтение (Task 6)"""

    def __init__(self, pool_base):
        """
        Инициализация сервиса

        Args:
            pool_base: Connection pool базы данных
        """
        self.pool_base = pool_base

    # ========================================================================
    # ЗАГРУЗКА ШАБЛОНОВ
    # ========================================================================

    async def load_text_templates(self, template_id: int) -> Optional[Dict[str, Any]]:
        """
        Загрузить шаблоны текстов из БД

        Args:
            template_id: ID шаблона в таблице t_lp_lesson_activity_template

        Returns:
            Dict с структурой:
            {
                "text_length": "80-120 words",
                "questions_count": 4,
                "texts_by_type": {
                    "1": {...},
                    "2": {...}
                }
            }
            или None при ошибке
        """


        # Нормализуем template_id
        if isinstance(template_id, (list, tuple)):
            if len(template_id) == 0:
                logger.error("template_id is empty list/tuple")
                return None
            template_id = template_id[0]

        template_id = int(template_id)
        logger.info(f"Loading text templates for template_id: {template_id}")

        query = """
            SELECT c_template_data
            FROM t_lp_lesson_activity_template
            WHERE c_template_id = $1
        """

        try:
            result = await pgDB.fExec_SelectQuery_args(
                self.pool_base, 
                query, 
                template_id
            )

            if not result:
                logger.error(f"Template {template_id} not found in database")
                return None

            template_data = result[0][0]

            # Парсим JSON если это строка
            if isinstance(template_data, str):
                logger.info("Parsing JSON string to dict")
                template_data = json.loads(template_data)

            # Валидация структуры
            if not self._validate_template_structure(template_data):
                logger.error(f"Invalid template structure for template {template_id}")
                return None

            logger.info(
                f"Successfully loaded {len(template_data.get('texts_by_type', {}))} "
                f"text types from template {template_id}"
            )
            return template_data

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return None

        except Exception as e:
            logger.error(f"Error loading templates: {e}", exc_info=True)
            return None

    def _validate_template_structure(self, template_data: Dict) -> bool:
        """
        Валидация структуры шаблона

        Args:
            template_data: Данные шаблона

        Returns:
            True если структура валидна
        """
        if not isinstance(template_data, dict):
            logger.error("Template data is not a dict")
            return False

        required_fields = ['text_length', 'questions_count', 'texts_by_type']
        if not all(field in template_data for field in required_fields):
            logger.error(f"Missing required fields: {required_fields}")
            return False

        texts_by_type = template_data.get('texts_by_type', {})
        if not isinstance(texts_by_type, dict) or len(texts_by_type) == 0:
            logger.error("texts_by_type is empty or invalid")
            return False

        # Проверяем структуру первого типа текста
        first_type = next(iter(texts_by_type.values()))
        required_type_fields = ['name', 'text', 'questions']
        if not all(field in first_type for field in required_type_fields):
            logger.error(f"Text type missing required fields: {required_type_fields}")
            return False

        return True

    # ========================================================================
    # ВЫБОР ТИПА ТЕКСТА
    # ========================================================================

    def select_random_text_type(
        self, 
        template_data: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Выбрать случайный тип текста из шаблона

        Args:
            template_data: Данные шаблона с texts_by_type

        Returns:
            Tuple (type_id, type_data)
            Например: ("1", {"name": "Email", "text": "...", ...})
        """
        texts_by_type = template_data.get('texts_by_type', {})

        if not texts_by_type:
            raise ValueError("No text types available in template")

        # Получаем список ключей типов текстов
        type_ids = list(texts_by_type.keys())

        # Выбираем случайный
        selected_type_id = random.choice(type_ids)
        selected_type_data = texts_by_type[selected_type_id]

        logger.info(
            f"Selected text type: {selected_type_id} "
            f"({selected_type_data.get('name', 'Unknown')})"
        )

        return selected_type_id, selected_type_data

    # ========================================================================
    # AI ГЕНЕРАЦИЯ
    # ========================================================================

    async def generate_reading_with_ai(
        self,
        text_type: Dict[str, Any],
        topic: Dict[str, Any],
        lesson_context: Optional[str],
        user_id: int,
        text_length: str = "80-120 words",
        questions_count: int = 4
    ) -> Optional[Dict[str, Any]]:
        """
        Генерация текста для чтения через AI

        Args:
            text_type: Данные типа текста (из texts_by_type)
            topic: Информация о топике пользователя
            lesson_context: Контекст урока (модуль, уровень)
            user_id: ID пользователя
            text_length: Требуемая длина текста
            questions_count: Количество вопросов

        Returns:
            Dict с сгенерированным текстом и вопросами или None
        """
        try:
            # Формируем промпт
            prompt = self.build_reading_prompt(
                text_type=text_type,
                topic=topic,
                lesson_context=lesson_context,
                text_length=text_length,
                questions_count=questions_count
            )

            logger.info(
                f"Generating reading text for user {user_id}, "
                f"topic: {topic['topic_name']}, "
                f"type: {text_type.get('name', 'Unknown')}"
            )

            # Отправляем запрос к AI

            ai_response = await myF.afSendMsg2AI(prompt, self.pool_base, user_id)

            if not ai_response:
                raise ValueError("Empty AI response")

            # Парсим ответ
            generated_data = self._parse_ai_response(ai_response)

            # Валидация
            if not self._validate_generated_data(generated_data, questions_count):
                raise ValueError("Invalid AI response structure")

            # Добавляем метаданные
            generated_data['topic_name'] = topic['topic_name']
            generated_data['topic_id'] = topic.get('topic_id')
            generated_data['text_type'] = text_type.get('name', 'Unknown')
            generated_data['is_ai_generated'] = True

            # Создаем хеш для отслеживания прогресса
            generated_data['reading_hash'] = self._create_reading_hash(
                generated_data['title']
            )

            logger.info(
                f"Successfully generated reading text: {generated_data['title']}"
            )

            return generated_data

        except Exception as e:
            logger.error(f"AI generation failed: {e}", exc_info=True)
            return self._create_fallback_reading(text_type, topic)

    def build_reading_prompt(
        self,
        text_type: Dict[str, Any],
        topic: Dict[str, Any],
        lesson_context: Optional[str],
        text_length: str,
        questions_count: int
    ) -> str:
        """
        Формирует промпт для AI генерации текста

        Args:
            text_type: Тип текста (Email, Story, News, etc.)
            topic: Топик пользователя
            lesson_context: Контекст урока
            text_length: Требуемая длина текста
            questions_count: Количество вопросов

        Returns:
            Промпт для AI API
        """
        # Формируем контекст урока
        context_section = ""
        if lesson_context:
            context_section = f"\nLESSON CONTEXT: {lesson_context}\n"

        # Получаем пример текста и вопросов
        example_text = text_type.get('text', '')
        example_questions = text_type.get('questions', [])
        text_type_name = text_type.get('name', 'Text')
        text_type_desc = text_type.get('desc', '')

        # Форматируем примеры вопросов
        example_questions_str = json.dumps(
            example_questions[:2],  # Показываем только 2 примера для краткости
            ensure_ascii=False,
            indent=2
        )

        prompt = f"""You are an English reading comprehension test generator for ESL learners.

TASK: Generate a reading text similar to the template below, but personalized for the topic: "{topic['topic_name']}"
{context_section}

TEXT TYPE: {text_type_name}
DESCRIPTION: {text_type_desc}

EXAMPLE TEXT:
{example_text}

EXAMPLE QUESTIONS (first 2 of {len(example_questions)}):
{example_questions_str}

REQUIREMENTS:

1. TEXT REQUIREMENTS:
   - Length: {text_length}
   - Style: Same as the example ({text_type_name})
   - Topic: {topic['topic_name']}
   - Level: A1-A2 (beginner-elementary)
   - Keep the format and structure of the example
   - Use simple vocabulary and grammar

2. QUESTIONS REQUIREMENTS:
   - Generate exactly {questions_count} questions
   - Each question has 4 options (A, B, C, D)
   - Mix of question types: factual, inference, vocabulary
   - Test comprehension, not memory

3. LOCALIZATION RULES (VERY IMPORTANT):
   
   📌 **Rule for question text:**
   - If question requires DIRECT QUOTE from text → question in ENGLISH
   - If question is about general understanding/inference → question in RUSSIAN
   
   📌 **Rule for options:**
   - If option is DIRECT QUOTE from text → option in ENGLISH
   - If option is paraphrase/interpretation → option in RUSSIAN
   
   📌 **Rule for explanation:**
   - ALWAYS in RUSSIAN
   - Quote the relevant part from text in English if needed
   - Format: "Объяснение... The text says: 'quote'."

   Examples of correct localization:
   
   ✅ CORRECT (question with direct quote):
   {{
     "question": "What did Emma forget?",
     "options": {{
       "A": "her phone",
       "B": "her report",
       "C": "her keys",
       "D": "her laptop"
     }},
     "explanation": "Текст говорит: 'Don't forget your report!'"
   }}
   
   ✅ CORRECT (inference question):
   {{
     "question": "Какое настроение у автора письма?",
     "options": {{
       "A": "дружелюбное",
       "B": "формальное",
       "C": "сердитое",
       "D": "грустное"
     }},
     "explanation": "Приветствие 'Hi' и подпись показывают неформальный тон."
   }}

4. ANSWER DISTRIBUTION:
   - Ensure correct answers are distributed evenly across A, B, C, D
   - Don't make all correct answers "B" or "C"
   - Make wrong options plausible but clearly incorrect

5. OUTPUT FORMAT (strict JSON, no additional text):
{{
  "title": "Title of the text in English",
  "text": "Your generated text here (in English)...",
  "word_count": 95,
  "questions": [
    {{
      "question": "Question text (English or Russian based on rules above)",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "B",
      "explanation": "Explanation in Russian with English quotes if needed"
    }}
    // ... {questions_count} questions total
  ]
}}

IMPORTANT NOTES:
- Do NOT change the text type style
- Do NOT make text too difficult (A1-A2 level)
- Do NOT use complex grammar or vocabulary
- DO follow localization rules strictly
- DO ensure answer variety (not all "B")

Generate the reading text and questions now:"""

        return prompt

    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """
        Парсит ответ AI и извлекает JSON

        Args:
            ai_response: Ответ от AI API

        Returns:
            Распарсенный словарь

        Raises:
            ValueError: Если не удалось распарсить JSON
        """
        ai_response = ai_response.strip()

        # Извлекаем JSON из markdown блока
        if '```json' in ai_response:
            start = ai_response.find('```json') + 7
            end = ai_response.find('```', start)
            ai_response = ai_response[start:end].strip()
        elif '```' in ai_response:
            start = ai_response.find('```') + 3
            end = ai_response.rfind('```')
            ai_response = ai_response[start:end].strip()

        # Парсим JSON
        try:
            generated_data = json.loads(ai_response)
            return generated_data
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Response preview: {ai_response[:500]}")
            raise ValueError(f"Failed to parse AI response: {e}")

    def _validate_generated_data(
        self, 
        data: Dict[str, Any], 
        expected_questions: int
    ) -> bool:
        """
        Валидация сгенерированных данных

        Args:
            data: Сгенерированные данные
            expected_questions: Ожидаемое количество вопросов

        Returns:
            True если данные валидны
        """
        # Проверяем обязательные поля
        required_fields = ['title', 'text', 'word_count', 'questions']
        if not all(field in data for field in required_fields):
            logger.error(f"Missing required fields in generated data")
            return False

        # Проверяем вопросы
        questions = data.get('questions', [])
        if not isinstance(questions, list):
            logger.error("Questions is not a list")
            return False

        if len(questions) != expected_questions:
            logger.warning(
                f"Expected {expected_questions} questions, got {len(questions)}"
            )

        # Проверяем структуру каждого вопроса
        for idx, question in enumerate(questions):
            if not self._validate_question_structure(question, idx):
                return False

        # Проверяем распределение правильных ответов
        correct_answers = [q.get('correct_answer') for q in questions]
        if not self._validate_answer_distribution(correct_answers):
            logger.warning("Poor answer distribution, but accepting")

        return True

    def _validate_question_structure(
        self, 
        question: Dict[str, Any], 
        idx: int
    ) -> bool:
        """
        Валидация структуры одного вопроса

        Args:
            question: Данные вопроса
            idx: Индекс вопроса

        Returns:
            True если структура валидна
        """
        required_fields = ['question', 'options', 'correct_answer', 'explanation']
        if not all(field in question for field in required_fields):
            logger.error(f"Question {idx} missing required fields")
            return False

        # Проверяем options
        options = question.get('options', {})
        if not isinstance(options, dict):
            logger.error(f"Question {idx}: options is not a dict")
            return False

        required_options = {'A', 'B', 'C', 'D'}
        if set(options.keys()) != required_options:
            logger.error(
                f"Question {idx}: options must have A, B, C, D. "
                f"Got: {set(options.keys())}"
            )
            return False

        # Проверяем correct_answer
        correct_answer = question.get('correct_answer')
        if correct_answer not in required_options:
            logger.error(
                f"Question {idx}: correct_answer must be A, B, C, or D. "
                f"Got: {correct_answer}"
            )
            return False

        return True

    def _validate_answer_distribution(self, correct_answers: List[str]) -> bool:
        """
        Проверка распределения правильных ответов

        Предупреждает, если все ответы одинаковые (например, все "B")

        Args:
            correct_answers: Список правильных ответов

        Returns:
            True если распределение приемлемое
        """
        if not correct_answers:
            return False

        # Считаем частоту каждого ответа
        from collections import Counter
        distribution = Counter(correct_answers)

        # Проверяем, что не все ответы одинаковые
        if len(distribution) == 1:
            logger.warning(
                f"All correct answers are the same: {correct_answers[0]}"
            )
            return False

        # Проверяем, что нет доминирующего ответа (>60%)
        max_count = max(distribution.values())
        if max_count / len(correct_answers) > 0.6:
            most_common = distribution.most_common(1)[0]
            logger.warning(
                f"Answer '{most_common[0]}' appears {most_common[1]} times "
                f"({most_common[1]/len(correct_answers)*100:.1f}%)"
            )
            return False

        logger.info(f"Answer distribution: {dict(distribution)}")
        return True

    # ========================================================================
    # FALLBACK ЛОГИКА
    # ========================================================================

    def _create_fallback_reading(
        self,
        text_type: Dict[str, Any],
        topic: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создает fallback текст из шаблона при ошибке AI

        Args:
            text_type: Тип текста
            topic: Топик пользователя

        Returns:
            Текст с вопросами из шаблона
        """
        logger.warning(
            f"Using fallback reading for topic: {topic['topic_name']}, "
            f"type: {text_type.get('name', 'Unknown')}"
        )

        fallback_data = {
            'title': text_type.get('name', 'Reading Text'),
            'text': text_type.get('text', ''),
            'word_count': text_type.get('word_count', 0),
            'questions': text_type.get('questions', []),
            'topic_name': topic.get('topic_name', 'General'),
            'topic_id': topic.get('topic_id'),
            'text_type': text_type.get('name', 'Unknown'),
            'is_ai_generated': False
        }

        # Создаем хеш
        fallback_data['reading_hash'] = self._create_reading_hash(
            fallback_data['title']
        )

        return fallback_data

    def _create_reading_hash(self, title: str) -> str:
        """
        Создает хеш для идентификации текста

        Args:
            title: Заголовок текста

        Returns:
            MD5 хеш заголовка
        """
        return hashlib.md5(title.encode('utf-8')).hexdigest()

    # ========================================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ========================================================================

    def shuffle_question_options(
        self, 
        question: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Перемешивает варианты ответов в вопросе

        Args:
            question: Вопрос с options и correct_answer

        Returns:
            Вопрос с перемешанными опциями
        """
        options = question.get('options', {})
        correct_answer = question.get('correct_answer')

        if not options or not correct_answer:
            return question

        # Получаем текст правильного ответа
        correct_text = options.get(correct_answer)

        # Создаем список значений
        values = list(options.values())
        random.shuffle(values)

        # Создаем новый словарь с перемешанными значениями
        new_options = {}
        new_correct_answer = None

        keys = ['A', 'B', 'C', 'D']

        for i, key in enumerate(keys):
            if i < len(values):
                new_options[key] = values[i]

                # Находим новую позицию правильного ответа
                if values[i] == correct_text:
                    new_correct_answer = key

        # Обновляем вопрос
        shuffled_question = {
            **question,
            'options': new_options,
            'correct_answer': new_correct_answer
        }

        return shuffled_question

    def shuffle_all_questions(
        self, 
        reading_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Перемешивает опции во всех вопросах

        Args:
            reading_data: Данные с текстом и вопросами

        Returns:
            Данные с перемешанными опциями
        """
        questions = reading_data.get('questions', [])

        shuffled_questions = [
            self.shuffle_question_options(q) 
            for q in questions
        ]

        return {
            **reading_data,
            'questions': shuffled_questions
        }
