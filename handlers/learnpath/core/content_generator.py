"""
Core модуль для генерации персонализированного контента
Работает с таблицей: t_lp_lesson_activity_template
"""

from typing import Optional, Dict, Any, List
import json
import random
import hashlib
import fpgDB as pgDB


class ContentGenerator:
    """Генератор персонализированного контента заданий"""

    def __init__(self, pool):
        self.pool_base, self.pool_log = pool

    def _parse_json(self, data) -> dict:
        """Парсит JSON строку или возвращает dict"""
        if isinstance(data, str):
            import json
            try:
                return json.loads(data) if data else {}
            except:
                return {}
        return data if data else {}

    async def get_template(self, template_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить шаблон задания

        Returns:
            {
                'template_id': int,
                'module_id': int,
                'activity_type': str,
                'template_name': str,
                'template_data': dict,
                'ai_prompt': str
            }
        """
        query = f"""
            SELECT 
                c_template_id,
                c_module_id,
                c_activity_type,
                c_template_name,
                c_template_data,
                c_ai_prompt
            FROM t_lp_lesson_activity_template
            WHERE c_template_id = {template_id}
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        if not result:
            return None

        row = result[0]
        return {
            'template_id': row[0],
            'module_id': row[1],
            'activity_type': row[2],
            'template_name': row[3],
            'template_data': self._parse_json(row[4]),
            'ai_prompt': row[5]
        }

    async def get_user_topics(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Получить интересы (топики) пользователя

        Returns:
            [
                {
                    'topic_id': int,
                    'topic_name': str,
                    'priority': int
                },
                ...
            ]
        """

        query = """
            SELECT tu.c_topic_id, tu.c_priority, t.c_topic_name
            FROM t_lp_topics_user tu
            JOIN t_lp_topics t ON tu.c_topic_id = t.c_topic_id
            WHERE tu.c_user_id = $1 
                AND tu.c_priority > 1
                AND t.c_is_active = true
            ORDER BY tu.c_priority DESC
        """

        result = await pgDB.fExec_SelectQuery_args(self.pool_base, query, user_id)

        if not result:
            return []

        return [
            {
                "topic_id": row[0],
                "priority": row[1],
                "topic_name": row[2]
            }
            for row in result
        ]


    async def generate_task3_questions(
            self,
            template_id: int,
            user_id: int,
            questions_count: int
    ) -> List[Dict[str, Any]]:
        """
        Сгенерировать вопросы для Task 3 (Questions)

        Returns:
            [
                {
                    'question': str,
                    'options': {'A': str, 'B': str, 'C': str, 'D': str},
                    'correct_answer': str,
                    'explanation': str
                },
                ...
            ]
        """
        template = await self.get_template(template_id)

        if not template:
            return []

        template_data = template['template_data']
        questions = template_data.get('questions', [])

        # Если вопросов в шаблоне больше, чем нужно - выбираем случайные
        if len(questions) > questions_count:
            questions = random.sample(questions, questions_count)

        return questions[:questions_count]

    async def generate_task4_sentences(
            self,
            template_id: int,
            user_id: int,
            sentences_count: int = 3,
            topic_name: str = None
    ) -> List[Dict[str, Any]]:
        """
        Сгенерировать предложения для Task 4 (Listen & Speak)
        Исключает уже пройденные пользователем предложения

        Args:
            template_id: ID шаблона
            user_id: ID пользователя
            sentences_count: Количество предложений
            topic_name: Название темы (опционально, если задано - использует именно её)

        Returns:
            [
                {
                    'text': str,
                    'audio_text': str,
                    'grammar_breakdown': {...},
                    'sentence_hash': str  # MD5 хеш для идентификации
                },
                ...
            ]
        """
        template = await self.get_template(template_id)

        if not template:
            return []

        template_data = template['template_data']
        examples_by_topic = template_data.get('examples_by_topic', {})

        # Если тема задана явно - используем её
        if topic_name:
            selected_topic = topic_name
        else:
            # Получаем топики пользователя
            user_topics = await self.get_user_topics(user_id)

            if not user_topics:
                # Если нет топиков - используем Technology по умолчанию
                selected_topic = 'Technology'
            else:
                # Выбираем случайный топик из пользовательских
                selected_topic = random.choice(user_topics)['topic_name']

        # Получаем примеры для выбранного топика
        sentences = examples_by_topic.get(selected_topic, [])

        if not sentences and examples_by_topic:
            # Если топика нет - берем первый доступный
            first_topic = list(examples_by_topic.keys())[0]
            sentences = examples_by_topic[first_topic]

        # Получаем список уже пройденных предложений пользователя
        completed_hashes = await self._get_completed_content_hashes(
            user_id=user_id,
            template_id=template_id,
            activity_type='task_4_listen_speak'
        )

        # Фильтруем и добавляем хеши
        available_sentences = []
        for sentence in sentences:
            text = sentence.get('text', '')
            sentence_hash = hashlib.md5(text.encode('utf-8')).hexdigest()

            # Пропускаем уже пройденные
            if sentence_hash not in completed_hashes:
                sentence['sentence_hash'] = sentence_hash
                available_sentences.append(sentence)

        # Если доступных предложений меньше чем нужно, возвращаем все доступные
        if len(available_sentences) < sentences_count:
            return available_sentences

        # Выбираем случайные из доступных
        selected = random.sample(available_sentences, sentences_count)
        return selected

    async def _get_completed_content_hashes(
            self,
            user_id: int,
            template_id: int,
            activity_type: str
    ) -> set:
        """
        Получить хеши всех пройденных элементов пользователя для данного типа задания
        ОБНОВЛЕНО: template_id теперь опциональный

        Args:
            user_id: ID пользователя
            template_id: ID шаблона (может быть None)
            activity_type: Тип задания (task_3_questions, task_4_listen_speak, и т.д.)

        Returns:
            set: Множество хешей пройденных элементов
        """
        # Формируем условие для template_id
        if template_id is not None:
            template_condition = f"AND c_template_id = {template_id}"
        else:
            template_condition = "AND c_template_id IS NULL"

        query = f"""
            SELECT c_content_hash
            FROM t_lp_lesson_activity_progress
            WHERE c_user_id = {user_id}
            {template_condition}
            AND c_activity_type = '{activity_type}'
            AND c_is_completed = TRUE
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        if not result:
            return set()

        return {row[0] for row in result}

    async def mark_content_progress(
            self,
            user_id: int,
            template_id: int,
            activity_type: str,
            content_hash: str,
            content_text: str = None,
            is_completed: bool = True,
            is_correct: bool = None,
            content_data: dict = None
    ) -> None:
        """
        Универсальный метод для отметки прогресса по любому типу задания
        ОБНОВЛЕНО: template_id теперь опциональный (может быть None)

        Args:
            user_id: ID пользователя
            template_id: ID шаблона (опционально, может быть None)
            activity_type: Тип задания (task_3_questions, task_4_listen_speak, и т.д.)
            content_hash: MD5 хеш контента
            content_text: Текст элемента (опционально)
            is_completed: True = пройдено, False = пропущено
            is_correct: True = правильно, False = неправильно, None = не применимо
            content_data: Дополнительные данные в формате dict (будут сохранены как JSONB)
        """
        # Экранируем текст для SQL
        escaped_text = content_text.replace("'", "''") if content_text else ''

        # Преобразуем content_data в JSON строку
        if content_data:
            json_data = json.dumps(content_data, ensure_ascii=False).replace("'", "''")
        else:
            json_data = '{}'

        # Подготовка значения для is_correct (может быть NULL)
        is_correct_value = 'NULL' if is_correct is None else str(is_correct).upper()

        # Подготовка значения для template_id (может быть NULL)
        template_id_value = 'NULL' if template_id is None else str(template_id)

        query = f"""
            INSERT INTO t_lp_lesson_activity_progress 
                (c_user_id, c_template_id, c_activity_type, c_content_hash, 
                 c_content_text, c_is_completed, c_is_correct, c_content_data)
            VALUES 
                ({user_id}, {template_id_value}, '{activity_type}', '{content_hash}', 
                 '{escaped_text}', {is_completed}, {is_correct_value}, '{json_data}'::jsonb)
            ON CONFLICT (c_user_id, c_content_hash, c_activity_type) 
            DO UPDATE SET
                c_is_completed = {is_completed},
                c_is_correct = {is_correct_value},
                c_content_data = '{json_data}'::jsonb,
                c_updated_at = CURRENT_TIMESTAMP
        """

        await pgDB.fExec_UpdateQuery(self.pool_base, query)

    # ============================================================================
    # Специфичные методы для разных типов заданий
    # ============================================================================

    async def mark_task4_progress(
            self,
            user_id: int,
            template_id: int,
            sentence_hash: str,
            sentence_text: str,
            is_completed: bool = True,
            is_correct: bool = None,
            user_answer: str = None,
            grammar_breakdown: dict = None
    ) -> None:
        """
        Отметить прогресс для Task 4 (Listen & Speak)

        Args:
            user_id: ID пользователя
            template_id: ID шаблона
            sentence_hash: MD5 хеш предложения
            sentence_text: Текст предложения
            is_completed: True = пройдено, False = пропущено
            is_correct: True = правильно произнесено, False = с ошибками, None = не оценивается
            user_answer: Ответ пользователя (транскрибированный)
            grammar_breakdown: Грамматическая структура предложения
        """
        content_data = {
            'sentence_text': sentence_text,
            'grammar_breakdown': grammar_breakdown or {}
        }

        if user_answer:
            content_data['user_answer'] = user_answer

        await self.mark_content_progress(
            user_id=user_id,
            template_id=template_id,
            activity_type='task_4_listen_speak',
            content_hash=sentence_hash,
            content_text=sentence_text,
            is_completed=is_completed,
            is_correct=is_correct,
            content_data=content_data
        )

    async def mark_task3_progress(
            self,
            user_id: int,
            template_id: int,
            question: dict,
            selected_answer: str,
            is_completed: bool = True
    ) -> None:
        """
        Отметить прогресс для Task 3 (Questions)

        Args:
            user_id: ID пользователя
            template_id: ID шаблона
            question: Словарь с вопросом (содержит question, options, correct_answer)
            selected_answer: Выбранный пользователем ответ
            is_completed: True = ответил, False = пропустил
        """
        question_text = question.get('question', '')
        correct_answer = question.get('correct_answer', '')
        question_hash = hashlib.md5(question_text.encode('utf-8')).hexdigest()

        is_correct = (selected_answer == correct_answer) if is_completed else None

        content_data = {
            'question_text': question_text,
            'options': question.get('options', {}),
            'selected_answer': selected_answer,
            'correct_answer': correct_answer
        }

        await self.mark_content_progress(
            user_id=user_id,
            template_id=template_id,
            activity_type='task_3_questions',
            content_hash=question_hash,
            content_text=question_text,
            is_completed=is_completed,
            is_correct=is_correct,
            content_data=content_data
        )

    async def mark_task5_progress(
            self,
            user_id: int,
            template_id: int,
            sentence_hash: str,
            audio_text: str,
            user_text: str,
            is_completed: bool = True,
            accuracy: float = None
    ) -> None:
        """
        Отметить прогресс для Task 5 (Listen & Write)

        Args:
            user_id: ID пользователя
            template_id: ID шаблона
            sentence_hash: MD5 хеш предложения
            audio_text: Правильный текст из аудио
            user_text: Текст, написанный пользователем
            is_completed: True = ответил, False = пропустил
            accuracy: Процент точности (0-100)
        """
        # Определяем правильность (например, если точность > 80%)
        is_correct = None
        if accuracy is not None and is_completed:
            is_correct = accuracy >= 80

        content_data = {
            'audio_text': audio_text,
            'user_text': user_text,
            'accuracy': accuracy
        }

        await self.mark_content_progress(
            user_id=user_id,
            template_id=template_id,
            activity_type='task_5_listen_write',
            content_hash=sentence_hash,
            content_text=audio_text,
            is_completed=is_completed,
            is_correct=is_correct,
            content_data=content_data
        )

    async def mark_task6_progress(
            self,
            user_id: int,
            template_id: int,
            reading_id: int,
            question_id: int,
            question_text: str,
            selected_answer: str,
            correct_answer: str,
            is_completed: bool = True
    ) -> None:
        """
        Отметить прогресс для Task 6 (Reading)

        Args:
            user_id: ID пользователя
            template_id: ID шаблона
            reading_id: ID текста для чтения
            question_id: ID вопроса
            question_text: Текст вопроса
            selected_answer: Выбранный ответ
            correct_answer: Правильный ответ
            is_completed: True = ответил, False = пропустил
        """
        # Создаем уникальный хеш из reading_id + question_id
        hash_string = f"{reading_id}_{question_id}_{question_text}"
        content_hash = hashlib.md5(hash_string.encode('utf-8')).hexdigest()

        is_correct = (selected_answer == correct_answer) if is_completed else None

        content_data = {
            'reading_id': reading_id,
            'question_id': question_id,
            'question_text': question_text,
            'selected_answer': selected_answer,
            'correct_answer': correct_answer
        }

        await self.mark_content_progress(
            user_id=user_id,
            template_id=template_id,
            activity_type='task_6_reading',
            content_hash=content_hash,
            content_text=question_text,
            is_completed=is_completed,
            is_correct=is_correct,
            content_data=content_data
        )

    # ============================================================================
    # Методы для получения статистики
    # ============================================================================

    async def get_user_activity_stats(
            self,
            user_id: int,
            activity_type: str = None
    ) -> Dict[str, Any]:
        """
        Получить статистику активности пользователя

        Args:
            user_id: ID пользователя
            activity_type: Тип задания (опционально, если None - по всем типам)

        Returns:
            {
                'total': int,
                'completed': int,
                'skipped': int,
                'correct': int,
                'incorrect': int,
                'accuracy_percent': float
            }
        """
        activity_filter = f"AND c_activity_type = '{activity_type}'" if activity_type else ""

        query = f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN c_is_completed = TRUE THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN c_is_completed = FALSE THEN 1 ELSE 0 END) as skipped,
                SUM(CASE WHEN c_is_correct = TRUE THEN 1 ELSE 0 END) as correct,
                SUM(CASE WHEN c_is_correct = FALSE THEN 1 ELSE 0 END) as incorrect
            FROM t_lp_lesson_activity_progress
            WHERE c_user_id = {user_id}
            {activity_filter}
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        if not result or not result[0][0]:
            return {
                'total': 0,
                'completed': 0,
                'skipped': 0,
                'correct': 0,
                'incorrect': 0,
                'accuracy_percent': 0.0
            }

        row = result[0]
        total = row[0] or 0
        completed = row[1] or 0
        skipped = row[2] or 0
        correct = row[3] or 0
        incorrect = row[4] or 0

        # Вычисляем процент правильных ответов
        accuracy = 0.0
        if correct + incorrect > 0:
            accuracy = round((correct / (correct + incorrect)) * 100, 2)

        return {
            'total': total,
            'completed': completed,
            'skipped': skipped,
            'correct': correct,
            'incorrect': incorrect,
            'accuracy_percent': accuracy
        }

    async def generate_task5_sentences(
            self,
            template_id: int,
            user_id: int,
            sentences_count: int = 3,
            topic_name: str = None
    ) -> List[Dict[str, Any]]:
        """
        Сгенерировать предложения для Task 5 (Listen & Write)
        Исключает уже пройденные пользователем предложения

        Args:
            template_id: ID шаблона
            user_id: ID пользователя
            sentences_count: Количество предложений
            topic_name: Название темы (опционально, если задано - использует именно её)

        Returns:
            [
                {
                    'audio_text': str,
                    'correct_answer': str,
                    'grammar_breakdown': {...},
                    'sentence_hash': str  # MD5 хеш для идентификации
                },
                ...
            ]
        """
        template = await self.get_template(template_id)

        if not template:
            return []

        template_data = template['template_data']
        examples_by_topic = template_data.get('examples_by_topic', {})

        # Если тема задана явно - используем её
        if topic_name:
            selected_topic = topic_name
        else:
            # Получаем топики пользователя
            user_topics = await self.get_user_topics(user_id)

            if not user_topics:
                # Если нет топиков - используем Technology по умолчанию
                selected_topic = 'Technology'
            else:
                # Выбираем случайный топик из пользовательских
                selected_topic = random.choice(user_topics)['topic_name']

        # Получаем примеры для выбранного топика
        sentences = examples_by_topic.get(selected_topic, [])

        if not sentences and examples_by_topic:
            # Если топика нет - берем первый доступный
            first_topic = list(examples_by_topic.keys())[0]
            sentences = examples_by_topic[first_topic]

        # Получаем список уже пройденных предложений пользователя
        completed_hashes = await self._get_completed_content_hashes(
            user_id=user_id,
            template_id=template_id,
            activity_type='task_5_listen_write'
        )

        # Фильтруем и добавляем хеши
        available_sentences = []
        for sentence in sentences:
            audio_text = sentence.get('audio_text', sentence.get('text', ''))
            sentence_hash = hashlib.md5(audio_text.encode('utf-8')).hexdigest()

            # Пропускаем уже пройденные
            if sentence_hash not in completed_hashes:
                sentence['sentence_hash'] = sentence_hash
                # Убеждаемся, что есть correct_answer
                if 'correct_answer' not in sentence:
                    sentence['correct_answer'] = audio_text
                available_sentences.append(sentence)

        # Если доступных предложений меньше чем нужно, возвращаем все доступные
        if len(available_sentences) < sentences_count:
            return available_sentences

        # Выбираем случайные из доступных
        selected = random.sample(available_sentences, sentences_count)
        return selected

    async def generate_task6_reading(
            self,
            template_id: int,
            user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Сгенерировать текст и вопросы для Task 6 (Reading)
        Если все предзаготовленные тексты использованы - генерирует через AI

        Returns:
            {
                'title': str,
                'text': str,
                'word_count': int,
                'reading_hash': str,  # MD5 хеш для идентификации
                'questions': [
                    {
                        'question': str,
                        'options': {...},
                        'correct_answer': str,
                        'explanation': str
                    },
                    ...
                ]
            }
        """
        template = await self.get_template(template_id)

        if not template:
            return None

        user_topics = await self.get_user_topics(user_id)
        selected_topic = 'Technology' if not user_topics else random.choice(user_topics)['topic_name']

        template_data = template['template_data']
        examples_by_topic = template_data.get('examples_by_topic', {})

        # Получаем данные для выбранного топика
        reading_data = examples_by_topic.get(selected_topic)

        # Если нет текста для выбранного топика, пробуем другие
        if not reading_data and examples_by_topic:
            first_topic = list(examples_by_topic.keys())[0]
            reading_data = examples_by_topic[first_topic]

        # Если вообще нет готовых текстов - генерируем через AI
        if not reading_data:
            reading_data = await self._generate_task6_via_ai(
                user_id=user_id,
                topic_name=selected_topic,
                template_ai_prompt=template.get('ai_prompt', '')
            )

            if not reading_data:
                return None

        # Добавляем hash к данным
        title = reading_data.get('title', '')
        reading_hash = hashlib.md5(title.encode('utf-8')).hexdigest()
        reading_data['reading_hash'] = reading_hash

        return reading_data

    async def _generate_task6_via_ai(
            self,
            user_id: int,
            topic_name: str,
            template_ai_prompt: str
    ) -> Optional[Dict[str, Any]]:
        """
        Генерация текста и вопросов через AI

        Args:
            user_id: ID пользователя
            topic_name: Название темы
            template_ai_prompt: Промпт из шаблона

        Returns:
            Dict с текстом и вопросами или None при ошибке
        """
        import myPrompts as myP
        import selfFunctions as myF
        import json

        try:
            # Формируем промпт
            prompt = myP.fPromptTask6Reading(topic_name, template_ai_prompt)

            # Отправляем запрос к AI
            ai_response = await myF.afSendMsg2AI(prompt, self.pool_base, user_id)

            if not ai_response:
                return None

            # Парсим JSON ответ
            # Пытаемся извлечь JSON из ответа (может быть обернут в ```json```)
            ai_response = ai_response.strip()

            # Убираем markdown форматирование если есть
            if ai_response.startswith('```json'):
                ai_response = ai_response[7:]
            if ai_response.startswith('```'):
                ai_response = ai_response[3:]
            if ai_response.endswith('```'):
                ai_response = ai_response[:-3]

            ai_response = ai_response.strip()

            # Парсим JSON
            reading_data = json.loads(ai_response)

            # Проверяем наличие обязательных полей
            required_fields = ['title', 'text', 'questions']
            if not all(field in reading_data for field in required_fields):
                return None

            # Проверяем, что есть хотя бы один вопрос
            if not reading_data['questions'] or len(reading_data['questions']) == 0:
                return None

            # Добавляем word_count если отсутствует
            if 'word_count' not in reading_data:
                reading_data['word_count'] = len(reading_data['text'].split())

            return reading_data

        except json.JSONDecodeError as e:
            print(f"Error parsing AI JSON response: {e}")
            return None
        except Exception as e:
            print(f"Error generating reading via AI: {e}")
            return None