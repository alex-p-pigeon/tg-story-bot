"""
Модели данных для LearnPath модуля
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime


@dataclass
class Topic:
    """Модель темы обучения"""
    topic_id: int
    topic_name: str
    topic_name_ru: str
    description: str
    eng_level: int  # 1=A, 2=B, 3=C
    category: str   # essential, speaking, career, travel, study, fluency, culture
    estimated_hours: int
    order_priority: int


@dataclass
class Module:
    """Модель модуля обучения"""
    module_id: int
    topic_id: int
    module_name: str
    module_order: int
    content_type: str  # lesson, practice, test
    content: Dict
    estimated_minutes: int


@dataclass
class UserProgress:
    """Модель прогресса пользователя по теме"""
    user_id: int
    topic_id: int
    status: str  # not_started, in_progress, completed, skipped
    progress_percent: int
    order_in_program: int
    current_module_id: Optional[int] = None
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None


@dataclass
class ModuleProgress:
    """Модель прогресса пользователя по модулю"""
    user_id: int
    module_id: int
    status: str  # not_started, in_progress, completed
    attempts: int
    score: Optional[float] = None
    time_spent_minutes: Optional[int] = None
    completed_at: Optional[datetime] = None


@dataclass
class TestResult:
    """Модель результата теста"""
    test_id: int
    user_id: int
    topic_id: Optional[int]
    test_type: str  # entry, progress, final
    score: float
    max_score: float
    passed: bool
    test_data: Dict
    created_at: datetime


@dataclass
class UserInterest:
    """Модель интереса пользователя к теме"""
    user_id: int
    topic_id: int
    priority: int  # 1-5
    date_set: datetime