"""
Главный router модуля learnpath
Объединяет все sub-routers
"""

from aiogram import Router

# Импорт sub-routers
from .handlers import assessment
from .handlers import interests
from .handlers import generation

from .handlers import learning
from .handlers import activity
from .handlers import practice
from .handlers import test
from .handlers import management
from .handlers import story

# Создаем главный router
r_learnpath = Router(name='learnpath')

# Включаем все sub-routers
r_learnpath.include_router(assessment.router)
r_learnpath.include_router(interests.router)
r_learnpath.include_router(generation.router)
r_learnpath.include_router(learning.router)
r_learnpath.include_router(activity.router)
r_learnpath.include_router(practice.router)
r_learnpath.include_router(test.router)
r_learnpath.include_router(story.story_router)
r_learnpath.include_router(management.router)


__all__ = ['r_learnpath']