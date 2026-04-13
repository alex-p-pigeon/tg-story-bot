# generators/factory.py
from typing import Dict, Type, Optional, List
import importlib
from .base_generator import BaseQuestionGenerator


class QuestionGeneratorFactory:
    """
    Фабрика для создания генераторов вопросов
    Использует динамический импорт и кеширование
    """

    # Маппинг: имя генератора → (модуль, класс)
    GENERATOR_MAP = {
        "SPOQuestionGenerator": ("gram_10_generator", "SPOQuestionGenerator"),
        "ToBeQuestionGenerator": ("gram_20_generator", "ToBeQuestionGenerator"),
        "PresentSimpleQuestionGenerator": ("gram_30_generator", "PresentSimpleQuestionGenerator"),
        "ArticlesQuestionGenerator": ("gram_40_generator", "ArticlesQuestionGenerator"),
        "SingularPluralQuestionGenerator": ("gram_50_generator", "SingularPluralQuestionGenerator"),
        # Добавляйте новые генераторы здесь:
        # "PastSimpleQuestionGenerator": ("gram_40_generator", "PastSimpleQuestionGenerator"),
        # "FutureSimpleQuestionGenerator": ("gram_50_generator", "FutureSimpleQuestionGenerator"),
        # и т.д. для всех 41 модуля
    }

    # Кеш загруженных генераторов
    _cache: Dict[str, BaseQuestionGenerator] = {}

    @classmethod
    def get_generator(
            cls,
            generator_name: str,
            seed: Optional[int] = None
    ) -> BaseQuestionGenerator:
        """
        Получить экземпляр генератора по имени

        Args:
            generator_name: Имя класса генератора (из БД)
            seed: Seed для воспроизводимости

        Returns:
            Экземпляр генератора

        Raises:
            ValueError: Если генератор не найден
        """

        # Проверяем кеш
        cache_key = f"{generator_name}_{seed}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        # Проверяем маппинг
        if generator_name not in cls.GENERATOR_MAP:
            raise ValueError(
                f"Generator '{generator_name}' not found. "
                f"Available: {list(cls.GENERATOR_MAP.keys())}"
            )

        module_name, class_name = cls.GENERATOR_MAP[generator_name]

        try:
            # Динамический импорт модуля
            module = importlib.import_module(f".{module_name}", package="handlers.learnpath.generators")

            # Получаем класс генератора
            generator_class = getattr(module, class_name)

            # Создаем экземпляр
            generator = generator_class(seed=seed)

            # Кешируем
            cls._cache[cache_key] = generator

            return generator

        except ImportError as e:
            raise ImportError(
                f"Failed to import generator '{generator_name}' "
                f"from module 'generators.{module_name}': {e}"
            )
        except AttributeError as e:
            raise AttributeError(
                f"Class '{class_name}' not found in module "
                f"'generators.{module_name}': {e}"
            )

    @classmethod
    def clear_cache(cls):
        """Очистить кеш генераторов"""
        cls._cache.clear()

    @classmethod
    def list_available_generators(cls) -> List[str]:
        """Получить список доступных генераторов"""
        return list(cls.GENERATOR_MAP.keys())