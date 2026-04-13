"""
Главный router модуля learnpath
"""

from aiogram import Router

from .handlers import story

r_learnpath = Router(name='learnpath')
r_learnpath.include_router(story.story_router)

__all__ = ['r_learnpath']
