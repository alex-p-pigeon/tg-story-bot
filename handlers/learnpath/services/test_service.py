"""
Сервис для работы с финальными тестами - LAZY GENERATION
Вопросы генерируются "на лету" при показе, а не все сразу
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import random
import json
import fpgDB as pgDB
import selfFunctions as myF

import logging
logger = logging.getLogger(__name__)


class TestService:
    """Сервис для управления тестами с ленивой AI-генерацией вопросов"""

    def __init__(self, pool):
        self.pool = pool

    # ========================================================================
    # СОЗДАНИЕ И ЗАПУСК ТЕСТА - LAZY VERSION
    # ========================================================================

    async def start_module_test(
            self,
            user_id: int,
            module_id: int
    ) -> Tuple[int, List[Dict], List[Dict], Dict]:
        """
        Начать финальный тест модуля (БЕЗ генерации вопросов)
        
        Returns:
            (test_progress_id, templates, topics, config)
            
        Вопросы НЕ генерируются! Возвращаем только шаблоны и топики.
        Генерация происходит в handler при показе каждого вопроса.
        """
        
        # 1. Проверяем, что все уроки модуля пройдены
        lessons_completed = await self._check_lessons_completed(user_id, module_id)
        if not lessons_completed:
            raise ValueError("Not all lessons completed. Cannot start final test.")

        # 2. Получаем конфигурацию теста
        query = """
            SELECT 
                c_test_id, c_test_name, c_num_questions, c_passing_score,
                c_time_limit_minutes, c_grammar_topics
            FROM t_lp_module_test
            WHERE c_module_id = $1 AND c_test_type = 'final' AND c_is_active = true
        """
        
        result = await pgDB.fExec_SelectQuery_args(self.pool, query, module_id)
        if not result:
            raise ValueError(f"No active final test found for module {module_id}")

        test_config = {
            'c_test_id': result[0][0],
            'c_test_name': result[0][1],
            'c_num_questions': result[0][2],
            'c_passing_score': result[0][3],
            'c_time_limit_minutes': result[0][4],
            'c_grammar_topics': result[0][5]
        }

        # 3. Проверяем незавершенные тесты
        query = """
            SELECT c_test_progress_id, c_start_date
            FROM t_lp_module_test_user_progress
            WHERE c_user_id = $1 AND c_test_id = $2 AND c_status = 'in_progress'
            ORDER BY c_start_date DESC LIMIT 1
        """
        
        existing_test = await pgDB.fExec_SelectQuery_args(
            self.pool, query, user_id, test_config['c_test_id']
        )

        if existing_test:
            time_limit = test_config['c_time_limit_minutes']
            if time_limit:
                start_date = existing_test[0][1]
                deadline = start_date + timedelta(minutes=time_limit)
                if datetime.now() > deadline:
                    await self._fail_test_timeout(existing_test[0][0])
                else:
                    raise ValueError("You have an unfinished test.")

        # ========================================================================
        # ✅ LAZY: Загружаем только шаблоны, НЕ генерируем вопросы
        # ========================================================================

        lesson_ids = test_config['c_grammar_topics']
        
        if not lesson_ids or len(lesson_ids) == 0:
            raise ValueError(f"No lessons (c_grammar_topics) defined for module {module_id}")

        logger.info(f"Loading question templates from lessons: {lesson_ids}")

        # Загружаем ВСЕ шаблоны из уроков
        all_templates = await self.load_templates_from_lessons(lesson_ids)
        
        if not all_templates or len(all_templates) == 0:
            raise ValueError(f"No question templates found for lessons {lesson_ids}")

        logger.info(f"Loaded {len(all_templates)} question templates from {len(lesson_ids)} lessons")

        num_questions = test_config['c_num_questions']
        
        if len(all_templates) < num_questions:
            logger.warning(
                f"Not enough templates ({len(all_templates)}) for {num_questions} questions. "
                f"Using all available templates."
            )
            num_questions = len(all_templates)

        # Выбираем случайные N шаблонов
        selected_templates = random.sample(all_templates, num_questions)
        
        logger.info(f"Selected {num_questions} random templates")

        # Получаем топики для каждого вопроса
        question_topics = await self.get_multiple_weighted_topics(user_id, num_questions)
        
        if not question_topics:
            raise ValueError("No user topics found")

        # ✅ ВАЖНО: НЕ генерируем вопросы! Возвращаем только шаблоны и топики
        logger.info(f"⚡ LAZY MODE: Questions will be generated on-demand when shown to user")

        # Получаем номер попытки
        query = """
            SELECT COALESCE(MAX(c_attempt_number), 0) + 1
            FROM t_lp_module_test_user_progress
            WHERE c_user_id = $1 AND c_test_id = $2
        """
        
        attempt_result = await pgDB.fExec_SelectQuery_args(
            self.pool, query, user_id, test_config['c_test_id']
        )
        attempt_number = attempt_result[0][0] if attempt_result else 1

        # Создаем запись о начале теста
        query = """
            INSERT INTO t_lp_module_test_user_progress (
                c_user_id, c_test_id, c_attempt_number, c_status,
                c_start_date, c_max_score, c_answers
            ) VALUES ($1, $2, $3, 'in_progress', NOW(), $4, '[]'::jsonb)
            RETURNING c_test_progress_id
        """
        
        result = await pgDB.fFetch_InsertQuery_args(
            self.pool, query, user_id, test_config['c_test_id'],
            attempt_number, num_questions
        )

        test_progress_id = result[0] if result else None
        if not test_progress_id:
            raise ValueError("Failed to create test progress record")

        # Формируем конфиг
        config = {
            "test_id": test_config['c_test_id'],
            "test_name": test_config['c_test_name'],
            "total_questions": num_questions,
            "passing_score": test_config['c_passing_score'],
            "time_limit_minutes": test_config['c_time_limit_minutes'],
            "attempt_number": attempt_number,
            "module_id": module_id
        }

        # ✅ Возвращаем шаблоны и топики, НЕ сгенерированные вопросы
        return test_progress_id, selected_templates, question_topics, config

    # ========================================================================
    # ГЕНЕРАЦИЯ ОДНОГО ВОПРОСА (вызывается из handler)
    # ========================================================================

    async def generate_single_question(
            self,
            template: Dict,
            topic: Dict,
            user_id: int,
            module_context: Optional[str] = None
    ) -> Dict:
        """
        Генерирует ОДИН вопрос через AI
        
        Вызывается из handler при показе вопроса пользователю
        """
        
        return await self.generate_ai_question(
            template=template,
            topic=topic,
            user_id=user_id,
            module_context=module_context
        )

    # ========================================================================
    # ЗАГРУЗКА ШАБЛОНОВ ИЗ УРОКОВ
    # ========================================================================

    async def load_templates_from_lessons(self, lesson_ids: List[int]) -> List[Dict]:
        """Загрузить все шаблоны вопросов из указанных уроков"""
        
        query = """
            SELECT DISTINCT 
                lat.c_template_id,
                lat.c_template_data,
                lat.c_template_name,
                l.c_lesson_id,
                l.c_lesson_name
            FROM t_lp_lesson l
            JOIN t_lp_lesson_activity la ON l.c_lesson_id = la.c_lesson_id
            JOIN t_lp_lesson_activity_template lat ON la.c_template_id = lat.c_template_id
            WHERE l.c_lesson_id = ANY($1)
              AND lat.c_activity_type = 'task_3_questions'
              AND la.c_activity_type = 'task_3_questions'
            ORDER BY l.c_lesson_id
        """
        
        try:
            result = await pgDB.fExec_SelectQuery_args(self.pool, query, lesson_ids)
            
            if not result:
                logger.error(f"No templates found for lessons {lesson_ids}")
                return []

            all_questions = []
            
            for row in result:
                template_id = row[0]
                template_data = row[1]
                template_name = row[2]
                lesson_id = row[3]
                lesson_name = row[4]
                
                if isinstance(template_data, str):
                    template_data = json.loads(template_data)
                
                if not template_data or 'questions' not in template_data:
                    logger.warning(f"Invalid template_data for template_id {template_id}")
                    continue
                
                questions = template_data['questions']
                
                if not isinstance(questions, list):
                    logger.warning(f"Questions is not a list for template_id {template_id}")
                    continue
                
                # Добавляем метаданные
                for q in questions:
                    q['_source_lesson_id'] = lesson_id
                    q['_source_lesson_name'] = lesson_name
                    q['_source_template_id'] = template_id
                    q['_source_template_name'] = template_name
                
                all_questions.extend(questions)
                
                logger.info(
                    f"Loaded {len(questions)} questions from "
                    f"lesson {lesson_id} ({lesson_name})"
                )
            
            logger.info(f"Total: {len(all_questions)} questions from {len(result)} templates")
            
            return all_questions

        except Exception as e:
            logger.error(f"Error loading templates: {e}", exc_info=True)
            return []

    # ========================================================================
    # AI ГЕНЕРАЦИЯ ВОПРОСОВ
    # ========================================================================

    def build_ai_prompt(
            self, 
            template: Dict, 
            topic: Dict, 
            module_context: Optional[str] = None
    ) -> str:
        """Формирует промпт для AI генерации вопроса"""
        
        context_section = ""
        #if module_context:
        #    context_section = f"\nMODULE CONTEXT: {module_context}\n"

        '''
            E.g., assume the topic is medicine, then don't generate a question like "<template question> in medicine"
            Instead, focus on medicine-related vocabulary and examples
        '''

        #Generate ONE question similar to the template below, but personalized for the topic: "{topic['topic_name']}"
        #{context_section}

        prompt = f"""You are an English grammar test generator for ESL learners.

        TASK: You are given with: 
            - a question template, 
            - examples of four answer options for the template (including correct answer), 
            - example of a correct answer for the template, 
            - example of an explanation for the template, 
            - and a topic. 
        Your tasks are:
            - to provide a topic-aligned question by slightly changing the question template to personalize it for the topic - preferably by changing words only
            - Next, based on given examples you should provide four answer options for the question - 3 wrong and 1 correct
            - Next, for developed question and answer options and based on given example generate explanation of the correct answer to the question
        
        GIVEN INFO:
        Question: {template['question']}
        Options: {json.dumps(template['options'], ensure_ascii=False, indent=2)}
        Correct Answer: {template['correct_answer']}
        Explanation: {template['explanation']}
        Topic: {topic['topic_name']}

        REQUIREMENTS:
        1. ⚠️ IMPORTANT: The question MUST align with the lesson context: {lesson_theme}-{description}
        2. Keep the SAME question structure and grammatical focus as the template
        3. Use vocabulary and examples related to "{topic['topic_name']}". However, if 
            the template is general with limited personalization potential (for example: 
            "Что такое артикль в английском языке?"), don't personalize it
        4. Personalization should sound natural for educational purposes and avoid awkwardness.
            DO NOT add topic to the question. Bad example - "Выберите правильное предложение о чрезвычайных ситуациях за границей:" for topic "Emergencies abroad"
            Good example - "Выберите правильное предложение:"
        5. All examples in the question MUST be in English. Russian is used to ease question understanding    
        6. Ensure all options are grammatically correct and realistic
        7. Make the question at the same difficulty level as the template
        8. Provide 4 options labeled A, B, C, D
        9. The correct answer should be randomly placed among options A, B, C, D (not always option A)
        10. Write the explanation in Russian (like the template)
        11. ⚠️ IMPORTANT: Keep the explanation CONCISE (max 150 characters)
        12. The explanation should be clear and educational
        13. Focus on WHY the answer is correct, not on repeating the question
        14. If options contain references to other options (e.g., "Both A and B"), ensure these references 
            remain accurate after randomization. The explanation must also reference the correct answer letter.
        15. ⚠️ CRITICAL: Verify that the question, all options, correct answer, and explanation are 
            grammatically correct and follow British English conventions. Zero tolerance for errors. 

        ⚠️ VALIDATION STEP (MANDATORY):
        Before finalizing your answer, verify:
        - Read the correct answer option out loud - does it sound natural in British English?
        - Check: Would a native speaker say this exact phrase?
        - Verify the explanation is factually accurate
        - If testing articles (a/an): Remember a/an depends on SOUND, not spelling
          Example: "a CV" (sounds like "see-vee"), "an hour" (sounds like "our")
        - Double-check all grammar rules in your explanation are correct

        IMPORTANT:
        - Do NOT change the grammatical concept being tested
        - Do NOT make the options too obvious or too difficult
        - Use natural, real-world examples related to "{topic['topic_name']}"
        - Ensure the correct answer is definitively correct
        - Ensure wrong answers are plausible but clearly incorrect
        - ⚠️ If you're uncertain about any grammar rule, choose a different example
        
        GENERATION PROCESS:
        1. First, create the question and options
        2. Then, verify the correct answer by saying it out loud mentally
        3. Write the explanation based on verified facts
        4. Review everything one final time
        5. Only then output the JSON

        OUTPUT FORMAT (strict JSON, no additional text):
        {{
            "question": "Your generated question text in Russian",
            "options": {{
                "A": "First option",
                "B": "Second option",
                "C": "Third option",
                "D": "Fourth option"
            }},
            "correct_answer": "A",
            "explanation": "Clear explanation in Russian why this answer is correct and others are wrong"
        }}

        Generate the question now:"""

        return prompt

    async def generate_ai_question(
            self,
            template: Dict,
            topic: Dict,
            user_id: int,
            module_context: Optional[str] = None
    ) -> Dict:
        """Генерирует вопрос через AI с fallback на оригинальный шаблон"""
        
        try:
            prompt = self.build_ai_prompt(template, topic, module_context)
            
            logger.info(f"⚡ Generating question on-demand for topic: {topic['topic_name']}")
            ai_response = await myF.afSendMsg2AI(prompt, self.pool, user_id)

            if not ai_response:
                raise ValueError("Empty AI response")

            # Извлекаем JSON
            ai_response = ai_response.strip()

            if '```json' in ai_response:
                start = ai_response.find('```json') + 7
                end = ai_response.find('```', start)
                ai_response = ai_response[start:end].strip()
            elif '```' in ai_response:
                start = ai_response.find('```') + 3
                end = ai_response.rfind('```')
                ai_response = ai_response[start:end].strip()

            generated = json.loads(ai_response)

            # Валидация
            required_fields = ['question', 'options', 'correct_answer', 'explanation']
            if not all(field in generated for field in required_fields):
                raise ValueError("Invalid AI response structure")

            if not isinstance(generated['options'], dict):
                raise ValueError("Options must be a dictionary")

            required_options = {'A', 'B', 'C', 'D'}
            if set(generated['options'].keys()) != required_options:
                raise ValueError("Options must contain exactly A, B, C, D")

            if generated['correct_answer'] not in required_options:
                raise ValueError("Correct answer must be A, B, C, or D")

            # Рандомизация опций
            #generated = self.shuffle_question_options(generated)

            # Метаданные
            generated['topic_name'] = topic['topic_name']
            generated['topic_id'] = topic['topic_id']
            generated['is_ai_generated'] = True
            generated['source_lesson_id'] = template.get('_source_lesson_id')
            generated['source_lesson_name'] = template.get('_source_lesson_name')

            logger.info(f"✅ Generated AI question for topic: {topic['topic_name']}")
            return generated

        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return self.create_fallback_question(template, topic)

    def create_fallback_question(self, template: Dict, topic: Dict) -> Dict:
        """Создает fallback вопрос на основе оригинального шаблона"""
        
        logger.warning(f"Using fallback question for topic: {topic['topic_name']}")

        fallback = {
            **template,
            'topic_name': topic.get('topic_name', 'General'),
            'topic_id': topic.get('topic_id'),
            'is_ai_generated': False,
            'source_lesson_id': template.get('_source_lesson_id'),
            'source_lesson_name': template.get('_source_lesson_name')
        }
        
        return self.shuffle_question_options(fallback)

    def shuffle_question_options(self, question: Dict) -> Dict:
        """Перемешивает варианты ответов в вопросе"""
        
        options = question.get('options', {})
        correct_answer = question.get('correct_answer')

        if not options or not correct_answer:
            return question

        values = [options[key] for key in ['A', 'B', 'C', 'D']]
        random.shuffle(values)

        new_options = {}
        new_correct_answer = None

        for i, key in enumerate(['A', 'B', 'C', 'D']):
            new_options[key] = values[i]
            
            if values[i] == options[correct_answer]:
                new_correct_answer = key

        return {
            **question,
            'options': new_options,
            'correct_answer': new_correct_answer
        }

    async def get_module_context(self, module_id: int) -> Optional[str]:
        """Получает контекст модуля для улучшения AI генерации"""
        
        query = """
            SELECT m.c_module_name, t3.c_qlvl_name 
            FROM t_lp_module m 
            JOIN ts_qlvl t3 ON m.c_qlvl_id = t3.c_qlvl_id 
            WHERE m.c_module_id = $1
        """

        try:
            result = await pgDB.fExec_SelectQuery_args(self.pool, query, module_id)

            if result:
                module_name = result[0][0]
                englevel = result[0][1]
                return f"{module_name} - English level is {englevel}"

            return None

        except Exception as e:
            logger.error(f"Error getting module context: {e}")
            return None

    # ========================================================================
    # ОБРАБОТКА ОТВЕТОВ (без изменений)
    # ========================================================================

    async def submit_answer(
            self,
            test_progress_id: int,
            question_number: int,
            user_answer: str,
            question_data: Dict,
            time_spent_seconds: Optional[int] = None
    ) -> Dict:
        """Сохранить ответ пользователя на вопрос"""
        
        is_correct = user_answer == question_data['correct_answer']

        answer_record = {
            "question_number": question_number,
            "topic_id": question_data.get('topic_id'),
            "topic_name": question_data.get('topic_name'),
            "source_lesson_id": question_data.get('source_lesson_id'),
            "question_text": question_data['question'],
            "options": question_data['options'],
            "user_answer": user_answer,
            "correct_answer": question_data['correct_answer'],
            "is_correct": is_correct,
            "is_ai_generated": question_data.get('is_ai_generated', False),
            "answered_at": datetime.now().isoformat(),
            "time_spent_seconds": time_spent_seconds
        }

        query = """
            SELECT c_status
            FROM t_lp_module_test_user_progress
            WHERE c_test_progress_id = $1
        """
        
        result = await pgDB.fExec_SelectQuery_args(self.pool, query, test_progress_id)

        if not result:
            raise ValueError("Test not found")

        test_status = result[0][0]
        if test_status != 'in_progress':
            raise ValueError(f"Test is not active. Current status: {test_status}")

        query = """
            UPDATE t_lp_module_test_user_progress
            SET 
                c_answers = c_answers || $1::jsonb,
                c_updated_at = NOW()
            WHERE c_test_progress_id = $2
        """
        
        await pgDB.fExec_UpdateQuery_args(
            self.pool, query,
            json.dumps([answer_record]), test_progress_id
        )

        return {
            "is_correct": is_correct,
            "correct_answer": question_data['correct_answer'],
            "explanation": question_data['explanation']
        }

    # ========================================================================
    # ЗАВЕРШЕНИЕ ТЕСТА (без изменений)
    # ========================================================================

    async def complete_test(self, test_progress_id: int) -> Dict:
        """Завершить тест и подсчитать результаты"""
        
        query = """
            SELECT 
                utp.c_user_id, utp.c_test_id, utp.c_answers, utp.c_max_score,
                utp.c_start_date, mt.c_passing_score, mt.c_module_id,
                mt.c_grammar_topics, mt.c_time_limit_minutes
            FROM t_lp_module_test_user_progress utp
            JOIN t_lp_module_test mt ON utp.c_test_id = mt.c_test_id
            WHERE utp.c_test_progress_id = $1
        """
        
        result = await pgDB.fExec_SelectQuery_args(self.pool, query, test_progress_id)

        if not result:
            raise ValueError("Test not found")

        test_data = {
            'c_user_id': result[0][0],
            'c_test_id': result[0][1],
            'c_answers': json.loads(result[0][2]) if isinstance(result[0][2], str) else result[0][2],
            'c_max_score': result[0][3],
            'c_start_date': result[0][4],
            'c_passing_score': result[0][5],
            'c_module_id': result[0][6],
            'c_grammar_topics': result[0][7],
            'c_time_limit_minutes': result[0][8]
        }

        answers = test_data['c_answers']
        max_score = test_data['c_max_score']

        if len(answers) < max_score:
            raise ValueError(f"Not all questions answered. Answered: {len(answers)}/{max_score}")

        correct_count = sum(1 for ans in answers if ans.get('is_correct', False))
        score_percentage = (correct_count / max_score * 100) if max_score > 0 else 0
        passed = score_percentage >= test_data['c_passing_score']

        topic_stats = self._analyze_topic_performance(answers)
        lesson_stats = self._analyze_lesson_performance(answers)
        failed_topics = []

        if not passed:
            failed_topics = await self._identify_failed_lessons(
                topic_stats, lesson_stats, test_data['c_grammar_topics']
            )

        time_taken = None
        if test_data['c_start_date']:
            time_taken = (datetime.now() - test_data['c_start_date']).total_seconds() / 60

        query = """
            UPDATE t_lp_module_test_user_progress
            SET 
                c_status = $1, c_completion_date = NOW(), c_score = $2,
                c_passed = $3, c_failed_lessons = $4, c_updated_at = NOW()
            WHERE c_test_progress_id = $5
        """
        
        await pgDB.fExec_UpdateQuery_args(
            self.pool, query,
            'passed' if passed else 'failed', correct_count, passed,
            failed_topics if failed_topics else [], test_progress_id
        )

        if passed:
            await self._complete_module(test_data['c_user_id'], test_data['c_module_id'])

        return {
            "passed": passed,
            "score": correct_count,
            "max_score": max_score,
            "percentage": round(score_percentage, 1),
            "passing_score": test_data['c_passing_score'],
            "time_taken_minutes": round(time_taken, 1) if time_taken else None,
            "failed_topics": failed_topics,
            "topic_stats": topic_stats,
            "lesson_stats": lesson_stats
        }


    async def get_weighted_random_topic(
            self,
            user_id: int
    ) -> Optional[Dict[str, any]]:
        """
        Получить ОДИН случайный топик с учетом приоритета

        Args:
            user_id: ID пользователя

        Returns:
            {
                "topic_id": 2,
                "topic_name": "Shopping and money"
            }
            или None если нет топиков

        Example:
            >>> topic = await service.get_weighted_random_topic(user_id=123)
            >>> print(topic)
            {'topic_id': 2, 'topic_name': 'Shopping and money'}
        """

        topics = await self._get_user_topics_with_priority(user_id)

        if not topics:
            return None

        # Weighted random choice
        weights = [t["priority"] for t in topics]
        selected = random.choices(topics, weights=weights, k=1)[0]

        # ✅ Возвращаем Dict с topic_id и topic_name
        return {
            "topic_id": selected["topic_id"],
            "topic_name": selected["topic_name"]
        }

    # ========================================================================
    # ТОПИКИ ПОЛЬЗОВАТЕЛЯ
    # ========================================================================

    async def _get_user_topics_with_priority(self, user_id: int) -> List[Dict]:
        """Получить топики пользователя с приоритетами и названиями"""
        
        query = """
            SELECT tu.c_topic_id, tu.c_priority, t.c_topic_name
            FROM t_lp_topics_user tu
            JOIN t_lp_topics t ON tu.c_topic_id = t.c_topic_id
            WHERE tu.c_user_id = $1 
              AND tu.c_priority > 1
              AND t.c_is_active = true
            ORDER BY tu.c_priority DESC
        """
        
        result = await pgDB.fExec_SelectQuery_args(self.pool, query, user_id)

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

    async def get_multiple_weighted_topics(self, user_id: int, count: int) -> List[Dict]:
        """Получить несколько случайных топиков с учетом приоритета"""
        
        topics = await self._get_user_topics_with_priority(user_id)

        if not topics:
            return []

        weights = [t["priority"] for t in topics]
        selected_topics = random.choices(topics, weights=weights, k=count)

        return [
            {
                "topic_id": topic["topic_id"],
                "topic_name": topic["topic_name"]
            }
            for topic in selected_topics
        ]

    # ========================================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ========================================================================

    async def has_pending_test(self, user_id: int, module_id: int) -> Optional[int]:
        query = """
            SELECT utp.c_test_progress_id
            FROM t_lp_module_test_user_progress utp
            JOIN t_lp_module_test mt ON utp.c_test_id = mt.c_test_id
            WHERE utp.c_user_id = $1 
              AND mt.c_module_id = $2
              AND utp.c_status = 'in_progress'
            ORDER BY utp.c_start_date DESC LIMIT 1
        """
        result = await pgDB.fExec_SelectQuery_args(self.pool, query, user_id, module_id)
        return result[0][0] if result else None

    async def get_pending_test_info(self, user_id: int) -> Optional[Dict]:
        query = """
            SELECT 
                utp.c_test_progress_id, mt.c_module_id, utp.c_answers,
                utp.c_max_score, utp.c_start_date, mt.c_test_name,
                mt.c_passing_score, mt.c_time_limit_minutes
            FROM t_lp_module_test_user_progress utp
            JOIN t_lp_module_test mt ON utp.c_test_id = mt.c_test_id
            WHERE utp.c_user_id = $1 
                AND utp.c_status = 'in_progress'
            ORDER BY utp.c_start_date DESC LIMIT 1
        """
        result = await pgDB.fExec_SelectQuery_args(self.pool, query, user_id)
        if not result:
            return None
        return {
            'test_progress_id': result[0][0],
            'module_id': result[0][1],
            'answers': result[0][2],
            'max_score': result[0][3],
            'start_date': result[0][4],
            'test_name': result[0][5],
            'passing_score': result[0][6],
            'time_limit_minutes': result[0][7]
        }

    async def delete_pending_test(self, user_id: int, module_id: int) -> bool:
        try:
            query = """
                SELECT utp.c_test_progress_id
                FROM t_lp_module_test_user_progress utp
                JOIN t_lp_module_test mt ON utp.c_test_id = mt.c_test_id
                WHERE utp.c_user_id = $1 
                    AND mt.c_module_id = $2
                    AND utp.c_status = 'in_progress'
            """
            result = await pgDB.fExec_SelectQuery_args(self.pool, query, user_id, module_id)
            if not result:
                return False
            test_progress_id = result[0][0]
            query = "DELETE FROM t_lp_module_test_user_progress WHERE c_test_progress_id = $1"
            await pgDB.fExec_UpdateQuery_args(self.pool, query, test_progress_id)
            return True
        except Exception as e:
            logger.error(f"Error deleting test: {e}")
            return False

    async def _check_lessons_completed(self, user_id: int, module_id: int) -> bool:
        query = """
            SELECT 
                COUNT(DISTINCT l.c_lesson_id) as total_lessons,
                COUNT(DISTINCT CASE 
                    WHEN ulp.c_status = 'completed' THEN l.c_lesson_id 
                END) as completed_lessons
            FROM t_lp_lesson l
            LEFT JOIN t_lp_lesson_user_progress ulp 
                ON l.c_lesson_id = ulp.c_lesson_id 
                AND ulp.c_user_id = $1
            WHERE l.c_module_id = $2
                AND l.c_is_active = TRUE
                AND l.c_lesson_type = 'regular'
        """
        result = await pgDB.fExec_SelectQuery_args(self.pool, query, user_id, module_id)
        if not result:
            return False
        total_lessons = result[0][0]
        completed_lessons = result[0][1]
        return total_lessons == completed_lessons

    def _analyze_topic_performance(self, answers: List[Dict]) -> Dict[int, Dict]:
        topic_stats = {}
        for answer in answers:
            topic_id = answer.get('topic_id')
            if topic_id:
                if topic_id not in topic_stats:
                    topic_stats[topic_id] = {
                        "total": 0, 
                        "correct": 0,
                        "topic_name": answer.get('topic_name', 'Unknown')
                    }
                topic_stats[topic_id]["total"] += 1
                if answer.get('is_correct'):
                    topic_stats[topic_id]["correct"] += 1
        for topic_id, stats in topic_stats.items():
            stats["percentage"] = round(
                (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0, 1
            )
        return topic_stats

    def _analyze_lesson_performance(self, answers: List[Dict]) -> Dict[int, Dict]:
        lesson_stats = {}
        for answer in answers:
            lesson_id = answer.get('source_lesson_id')
            if lesson_id:
                if lesson_id not in lesson_stats:
                    lesson_stats[lesson_id] = {
                        "total": 0, 
                        "correct": 0,
                        "lesson_name": answer.get('source_lesson_name', 'Unknown')
                    }
                lesson_stats[lesson_id]["total"] += 1
                if answer.get('is_correct'):
                    lesson_stats[lesson_id]["correct"] += 1
        for lesson_id, stats in lesson_stats.items():
            stats["percentage"] = round(
                (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0, 1
            )
        return lesson_stats

    async def _identify_failed_lessons(
            self, topic_stats: Dict, lesson_stats: Dict, grammar_topic_ids: List[int]
    ) -> List[int]:
        weak_lessons = [
            lesson_id for lesson_id, stats in lesson_stats.items()
            if stats["percentage"] < 50
        ]
        if weak_lessons:
            return weak_lessons
        if lesson_stats:
            sorted_lessons = sorted(lesson_stats.items(), key=lambda x: x[1]['percentage'])
            return [lesson_id for lesson_id, _ in sorted_lessons[:3]]
        return []

    async def _complete_module(self, user_id: int, module_id: int):
        query = """
            UPDATE t_lp_module_user
            SET c_status = 'completed', c_completion_date = NOW(), c_updated_at = NOW()
            WHERE c_user_id = $1 AND c_module_id = $2
        """
        await pgDB.fExec_UpdateQuery_args(self.pool, query, user_id, module_id)

    async def _fail_test_timeout(self, test_progress_id: int):
        query = """
            UPDATE t_lp_module_test_user_progress
            SET c_status = 'failed', c_completion_date = NOW(), 
                c_passed = false, c_updated_at = NOW()
            WHERE c_test_progress_id = $1
        """
        await pgDB.fExec_UpdateQuery_args(self.pool, query, test_progress_id)
