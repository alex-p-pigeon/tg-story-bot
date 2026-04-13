# generators/base_generator.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseQuestionGenerator(ABC):
    """
    Базовый класс для всех генераторов вопросов
    Определяет единый интерфейс
    """

    @abstractmethod
    def generate_test_for_lesson(
            self,
            lesson_num: int,
            topic_ids_sequence: List[int],
            num_questions: int = None
    ) -> List[Dict[str, Any]]:
        """Генерация теста для урока"""
        pass

    @abstractmethod
    def generate_full_module_test(
            self,
            topic_ids_sequence: List[int],
            num_questions: int = None
    ) -> List[Dict[str, Any]]:
        """Генерация полного теста модуля"""
        pass

    @staticmethod
    async def get_topic_name(pool_base, topic_id: int) -> str:
        """Получить название топика"""
        # Общая реализация для всех генераторов
        from bot.database import pgDB

        var_query = """
            SELECT c_topic_name 
            FROM t_lp_topics 
            WHERE c_topic_id = $1
        """
        var_Arr = await pgDB.fExec_SelectQuery_args(pool_base, var_query, [topic_id])

        if var_Arr:
            return var_Arr[0][0]

        return "General"