"""
Сервис для создания индивидуальных коррекционных уроков (remedial lessons)
после провала теста модуля
"""

from typing import List, Dict, Any
import fpgDB as pgDB
from ..core.lesson_manager import LessonManager


class RemedialService:
    """Сервис создания remedial уроков"""

    def __init__(self, pool):
        self.pool_base, self.pool_log = pool

    async def create_remedial_lessons_after_fail(
            self,
            user_id: int,
            test_progress_id: int
    ) -> List[int]:
        """
        Создает индивидуальные коррекционные уроки после провала теста

        Args:
            user_id: ID студента
            test_progress_id: ID прогресса теста

        Returns:
            Список ID созданных remedial уроков
        """
        # 1. Получить результаты теста
        test_progress = await self._get_test_progress(test_progress_id)

        if not test_progress:
            return []

        failed_lesson_ids = test_progress['failed_lessons']

        if not failed_lesson_ids:
            return []

        # 2. Получить интересы студента
        user_topics = await self._get_user_topics(user_id)

        remedial_lesson_ids = []

        # 3. Для каждой непройденной темы создать remedial урок
        for lesson_id in failed_lesson_ids:
            original_lesson = await self._get_lesson(lesson_id)

            if not original_lesson:
                continue

            # 4. Создать новый remedial урок
            remedial_lesson_id = await self._create_remedial_lesson(
                original_lesson,
                user_id
            )

            if not remedial_lesson_id:
                continue

            # 5. Создать упрощенные задания для remedial урока
            await self._create_remedial_activities(
                remedial_lesson_id,
                lesson_id,
                user_topics
            )

            # 6. Создать прогресс для студента
            await self._create_user_lesson_progress(user_id, remedial_lesson_id)

            remedial_lesson_ids.append(remedial_lesson_id)

        return remedial_lesson_ids

    async def _get_test_progress(self, test_progress_id: int) -> Dict[str, Any]:
        """Получить результаты теста"""
        query = f"""
            SELECT 
                c_user_id,
                c_test_id,
                c_failed_lessons,
                c_score,
                c_max_score
            FROM t_lp_module_test_user_progress
            WHERE c_test_progress_id = {test_progress_id}
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        if not result:
            return None

        row = result[0]
        return {
            'user_id': row[0],
            'test_id': row[1],
            'failed_lessons': row[2] if row[2] else [],
            'score': row[3],
            'max_score': row[4]
        }

    async def _get_lesson(self, lesson_id: int) -> Dict[str, Any]:
        """Получить информацию об оригинальном уроке"""
        query = f"""
            SELECT 
                c_lesson_id,
                c_module_id,
                c_lesson_number,
                c_lesson_name,
                c_grammar_article_code,
                c_description,
                c_estimated_minutes,
                c_difficulty_level
            FROM t_lp_lesson
            WHERE c_lesson_id = {lesson_id}
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        if not result:
            return None

        row = result[0]
        return {
            'lesson_id': row[0],
            'module_id': row[1],
            'lesson_number': row[2],
            'lesson_name': row[3],
            'grammar_article_code': row[4],
            'description': row[5],
            'estimated_minutes': row[6],
            'difficulty_level': row[7]
        }

    async def _get_user_topics(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить топики интересов пользователя"""
        query = f"""
            SELECT 
                tu.c_topic_id,
                t.c_topic_name
            FROM t_lp_topics_user tu
            JOIN t_lp_topics t ON tu.c_topic_id = t.c_topic_id
            WHERE tu.c_user_id = {user_id}
            ORDER BY tu.c_priority DESC
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        topics = []
        for row in result:
            topics.append({
                'topic_id': row[0],
                'topic_name': row[1]
            })

        return topics

    async def _get_next_lesson_number(self, module_id: int) -> int:
        """Получить следующий номер урока в модуле"""
        query = f"""
            SELECT COALESCE(MAX(c_lesson_number), 0) + 1
            FROM t_lp_lesson
            WHERE c_module_id = {module_id}
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        if not result:
            return 1

        return result[0][0]

    async def _create_remedial_lesson(
            self,
            original_lesson: Dict[str, Any],
            user_id: int
    ) -> int:
        """Создать remedial урок"""
        module_id = original_lesson['module_id']
        lesson_number = await self._get_next_lesson_number(module_id)

        lesson_name = f"{original_lesson['lesson_name']} (Повторение)"
        grammar_code = original_lesson['grammar_article_code']

        # Снижаем сложность на 1 уровень (минимум 1)
        difficulty = max(1, original_lesson['difficulty_level'] - 1)

        # Уменьшаем время на 20%
        estimated_minutes = int(original_lesson['estimated_minutes'] * 0.8)

        query = f"""
            INSERT INTO t_lp_lesson (
                c_module_id,
                c_lesson_number,
                c_lesson_name,
                c_lesson_type,
                c_grammar_article_code,
                c_parent_lesson_id,
                c_description,
                c_estimated_minutes,
                c_difficulty_level,
                c_is_active
            ) VALUES (
                {module_id},
                {lesson_number},
                '{lesson_name}',
                'remedial',
                '{grammar_code}',
                {original_lesson['lesson_id']},
                'Индивидуальный урок для закрепления материала',
                {estimated_minutes},
                {difficulty},
                TRUE
            )
            RETURNING c_lesson_id
        """

        lesson_id = await pgDB.fExec_InsertQuery(self.pool_base, query)

        return lesson_id

    async def _create_remedial_activities(
            self,
            remedial_lesson_id: int,
            original_lesson_id: int,
            user_topics: List[Dict[str, Any]]
    ) -> None:
        """Создать упрощенные задания для remedial урока"""
        # Получаем активности оригинального урока
        query = f"""
            SELECT 
                c_activity_type,
                c_activity_order,
                c_is_required,
                c_template_id,
                c_questions_count,
                c_config
            FROM t_lp_lesson_activity
            WHERE c_lesson_id = {original_lesson_id}
            ORDER BY c_activity_order
        """

        original_activities = await pgDB.fExec_SelectQuery(self.pool_base, query)

        activity_order = 1

        for row in original_activities:
            activity_type = row[0]
            orig_order = row[1]
            is_required = row[2]
            template_id = row[3]
            questions_count = row[4]
            config = row[5] if row[5] else {}

            # Task 1: Грамматическая статья (всегда включаем)
            if activity_type == 'task_1_grammar':
                await self._insert_activity(
                    remedial_lesson_id,
                    activity_type,
                    activity_order,
                    True,
                    template_id,
                    None,
                    config
                )
                activity_order += 1

            # Task 2: Слова (меньше слов для remedial)
            elif activity_type == 'task_2_words':
                remedial_config = {
                    'min_words': 5,
                    'max_words': 8
                }
                await self._insert_activity(
                    remedial_lesson_id,
                    activity_type,
                    activity_order,
                    True,
                    template_id,
                    None,
                    remedial_config
                )
                activity_order += 1

            # Task 3: Вопросы (меньше вопросов, более простые)
            elif activity_type == 'task_3_questions':
                reduced_questions = max(3, questions_count - 2)
                await self._insert_activity(
                    remedial_lesson_id,
                    activity_type,
                    activity_order,
                    True,
                    template_id,
                    reduced_questions,
                    config
                )
                activity_order += 1

            # Task 4-6: С большей персонализацией
            elif activity_type in ['task_4_listen_speak', 'task_5_listen_write', 'task_6_reading']:
                remedial_config = {
                    **config,
                    'personalization_level': 'high',
                    'difficulty_adjustment': -1
                }
                await self._insert_activity(
                    remedial_lesson_id,
                    activity_type,
                    activity_order,
                    True,
                    template_id,
                    None,
                    remedial_config
                )
                activity_order += 1

            # Task 7: Повторение слов (всегда включаем)
            elif activity_type == 'task_7_word_repeat':
                await self._insert_activity(
                    remedial_lesson_id,
                    activity_type,
                    activity_order,
                    True,
                    template_id,
                    None,
                    config
                )
                activity_order += 1

            # Task 8: Dialog (опционально, пропускаем для упрощения)

    async def _insert_activity(
            self,
            lesson_id: int,
            activity_type: str,
            activity_order: int,
            is_required: bool,
            template_id: int,
            questions_count: int,
            config: Dict[str, Any]
    ) -> None:
        """Вставить задание в урок"""
        import json

        template_id_str = str(template_id) if template_id else 'NULL'
        questions_count_str = str(questions_count) if questions_count else 'NULL'
        config_str = f"'{json.dumps(config)}'::jsonb" if config else 'NULL'

        query = f"""
            INSERT INTO t_lp_lesson_activity (
                c_lesson_id,
                c_activity_type,
                c_activity_order,
                c_is_required,
                c_template_id,
                c_questions_count,
                c_config
            ) VALUES (
                {lesson_id},
                '{activity_type}',
                {activity_order},
                {is_required},
                {template_id_str},
                {questions_count_str},
                {config_str}
            )
        """

        await pgDB.fExec_InsertQuery(self.pool_base, query)

    async def _create_user_lesson_progress(
            self,
            user_id: int,
            lesson_id: int
    ) -> None:
        """Создать прогресс для студента"""
        query = f"""
            INSERT INTO t_lp_lesson_user_progress (
                c_user_id,
                c_lesson_id,
                c_status,
                c_completed_activities,
                c_lesson_data
            ) VALUES (
                {user_id},
                {lesson_id},
                'not_started',
                ARRAY[]::integer[],
                '{{}}'::jsonb
            )
        """

        await pgDB.fExec_InsertQuery(self.pool_base, query)

    async def get_remedial_lessons_by_module(
            self,
            user_id: int,
            module_id: int
    ) -> List[Dict[str, Any]]:
        """Получить все remedial уроки пользователя по модулю"""
        query = f"""
            SELECT 
                l.c_lesson_id,
                l.c_lesson_name,
                l.c_parent_lesson_id,
                lp.c_status
            FROM t_lp_lesson l
            LEFT JOIN t_lp_lesson_user_progress lp 
                ON l.c_lesson_id = lp.c_lesson_id AND lp.c_user_id = {user_id}
            WHERE l.c_module_id = {module_id}
                AND l.c_lesson_type = 'remedial'
                AND l.c_is_active = TRUE
            ORDER BY l.c_created_at
        """

        result = await pgDB.fExec_SelectQuery(self.pool_base, query)

        lessons = []
        for row in result:
            lessons.append({
                'lesson_id': row[0],
                'lesson_name': row[1],
                'parent_lesson_id': row[2],
                'status': row[3] if row[3] else 'not_started'
            })

        return lessons