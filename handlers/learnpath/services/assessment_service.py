"""
Сервис для оценки уровня английского
"""



from typing import Dict, List, Optional
import json
import fpgDB as pgDB


class AssessmentService:
    """Логика оценки уровня английского"""

    def __init__(self, pool):
        self.pool_base, self.pool_log = pool

    async def get_random_question(self, level: int) -> Optional[Dict]:
        """
        Получить случайный вопрос для уровня

        Args:
            level: Уровень сложности (1-3)

        Returns:
            Dict: Данные вопроса или None
        """
        var_query = f"""
            SELECT c_question_id, c_question_text, c_question_data 
            FROM t_lp_init_assess_questions 
            WHERE c_eng_level = {level} 
                AND c_question_type = 'multiple_choice'
            ORDER BY RANDOM() 
            LIMIT 1
        """
        var_Arr = await pgDB.fExec_SelectQuery(self.pool_base, var_query)

        if not var_Arr:
            return None

        import json
        return {
            'id': var_Arr[0][0],
            'text': var_Arr[0][1],
            'data': json.loads(var_Arr[0][2])
        }

    async def calculate_level(self, test_results: List[Dict]) -> int:
        """
        Вычислить итоговый уровень на основе результатов теста

        Args:
            test_results: Список результатов ответов

        Returns:
            int: Уровень (1-3)
        """
        if not test_results:
            return 2  # По умолчанию intermediate

        correct_count = sum(1 for r in test_results if r.get('correct'))
        total_count = len(test_results)
        accuracy = correct_count / total_count if total_count > 0 else 0

        if accuracy >= 0.8:
            return 3  # Advanced (C)
        elif accuracy >= 0.5:
            return 2  # Intermediate (B)
        else:
            return 1  # Beginner (A)

    async def save_test_result(self, user_id: int, test_data: Dict):
        """
        Сохранить результаты теста

        Args:
            user_id: ID пользователя
            test_data: Данные теста (score, max_score, results)
        """
        import json

        results_json = json.dumps(test_data.get('results', []))
        score = test_data.get('score', 0)
        max_score = test_data.get('max_score', 10)

        var_query = f"""
            INSERT INTO t_lp_init_assess_user_results 
            (c_user_id, c_topic_id, c_test_type, c_score, c_max_score, c_passed, c_test_data)
            VALUES ({user_id}, NULL, 'entry', {score}, {max_score}, true, '{results_json}')
        """
        await pgDB.fExec_UpdateQuery(self.pool_base, var_query)