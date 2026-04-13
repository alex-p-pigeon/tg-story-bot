"""
Story Fixer - AI-driven исправление проблем в сгенерированных историях

Использует AI для автоматического исправления проблем, найденных валидатором
"""

import logging
from typing import Dict, Any, List, Optional
import json
import selfFunctions as myF

from ..validators.story_validator import ValidationResult, ValidationIssue, IssueSeverity
from ..validators.story_validator import StoryQualityValidator
from ..generators.skeleton_generator_v2 import StorySkeletonGeneratorV2
from ..validators.story_validator import StoryQualityValidator




logger = logging.getLogger(__name__)


class StoryFixer:
    """
    AI-driven исправление проблем в историях
    
    Принимает ValidationResult и использует AI для исправления найденных проблем
    """

    def __init__(self, pool, user_id):
        self.pool_base, self.pool_log = pool
        self.user_id = user_id
        self.max_iterations = 3  # Максимум 3 попытки исправления

    async def fix_story_issues(
        self,
        story_data: Dict[str, Any],
        validation_result: ValidationResult,
        elaboration: Optional[Dict[str, Any]] = None,
        genre: str = "",
        grammar_focus: str = "",
        cefr_level: str = ""
    ) -> Dict[str, Any]:
        """
        Исправить проблемы в истории через AI
        
        Args:
            story_data: Исходные данные истории
            validation_result: Результат валидации с проблемами
            elaboration: Детализация истории
            genre, grammar_focus, cefr_level: Параметры для контекста
            
        Returns:
            Исправленные данные истории
        """
        
        if validation_result.is_valid:
            logger.info("Story is already valid, no fixes needed")
            return story_data
        
        logger.info(f"Attempting to fix {len(validation_result.issues)} issues in story")
        
        # Группируем проблемы по severity
        critical_issues = [i for i in validation_result.issues if i.severity == IssueSeverity.CRITICAL]
        high_issues = [i for i in validation_result.issues if i.severity == IssueSeverity.HIGH]
        
        # Если слишком много критических проблем - лучше сгенерировать заново
        if len(critical_issues) >= 5:
            logger.warning(f"{len(critical_issues)} critical issues - recommend full regeneration")
            raise ValueError("Too many critical issues - story should be regenerated from scratch")
        
        # Итеративно исправляем
        current_story = story_data
        current_elaboration = elaboration

        # Автоматическое исправление educational discovery (без AI)
        current_story = self._fix_reveals_item_system(current_story)
        logger.info("Applied automatic reveals_item fixes")
        
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"Fix iteration {iteration}/{self.max_iterations}")
            
            try:
                # Исправляем через AI
                fixed_story, fixed_elaboration = await self._apply_fixes(
                    current_story,
                    validation_result.issues,
                    current_elaboration,
                    genre,
                    grammar_focus,
                    cefr_level
                )
                
                logger.info(f"Iteration {iteration} completed")
                return {
                    'story_data': fixed_story,
                    'elaboration': fixed_elaboration
                }
                
            except Exception as e:
                logger.error(f"Error in iteration {iteration}: {e}")
                if iteration == self.max_iterations:
                    logger.error("Max iterations reached, returning partially fixed story")
                    return {
                        'story_data': current_story,
                        'elaboration': current_elaboration
                    }
        
        return {
            'story_data': current_story,
            'elaboration': current_elaboration
        }

    async def _apply_fixes(
        self,
        story_data: Dict[str, Any],
        issues: List[ValidationIssue],
        elaboration: Optional[Dict[str, Any]],
        genre: str,
        grammar_focus: str,
        cefr_level: str
    ) -> tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """Применить исправления через AI"""
        
        # Сортируем проблемы по severity (критические первыми)
        sorted_issues = sorted(
            issues, 
            key=lambda i: (
                0 if i.severity == IssueSeverity.CRITICAL else
                1 if i.severity == IssueSeverity.HIGH else
                2 if i.severity == IssueSeverity.MEDIUM else 3
            )
        )
        
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_fix_prompt(
            story_data,
            sorted_issues,
            elaboration,
            genre,
            grammar_focus,
            cefr_level
        )
        
        try:
            ai_response = await myF.afSendMsg2AI(
                user_prompt,
                self.pool_base,
                self.user_id,  # System user
                iModel=4,  # GPT-4o
                toggleParam=3,  # Temperature 0.7
                systemPrompt=system_prompt
            )
            
            # Парсим ответ
            fixed_data = self._parse_ai_response(ai_response)
            
            fixed_story = fixed_data.get('story_data', story_data)
            fixed_elaboration = fixed_data.get('elaboration', elaboration)
            
            return fixed_story, fixed_elaboration
            
        except Exception as e:
            logger.error(f"Error calling AI for fixes: {e}", exc_info=True)
            raise

    def _build_system_prompt(self) -> str:
        """Системный промпт для исправления"""
        
        return """You are an expert story fixer. Your task is to correct issues in interactive educational stories 
while preserving the core narrative, characters, and educational goals.

Key principles:
1. Fix CRITICAL issues first (story-breaking problems)
2. Maintain story coherence and logic
3. Preserve character personalities and goals
4. Keep educational value (grammar focus, CEFR level)
5. Make minimal changes necessary to fix issues
6. Ensure all NPCs, items, and scenes are properly connected

When fixing:
- If an NPC is referenced but not in scene, add them to the scene
- If an item is needed but not available, move it to an earlier scene
- If objectives are unachievable, adjust success conditions or scene contents
- If plot doesn't flow, add proper connections between scenes
- Maintain the original genre, mood, and style

RESPOND ONLY WITH VALID JSON containing both fixed story_data and elaboration.
"""

    def _build_fix_prompt(
        self,
        story_data: Dict[str, Any],
        issues: List[ValidationIssue],
        elaboration: Optional[Dict[str, Any]],
        genre: str,
        grammar_focus: str,
        cefr_level: str
    ) -> str:
        """Промпт для исправления проблем"""
        
        # Форматируем проблемы для AI
        issues_text = []
        for i, issue in enumerate(issues, 1):
            issues_text.append(f"""
Issue #{i} [{issue.severity.value.upper()}]:
- Category: {issue.category}
- Location: {issue.location}
- Problem: {issue.description}
- Suggested fix: {issue.suggestion}
""")
        
        issues_formatted = "\n".join(issues_text)
        
        # Если elaboration отсутствует
        elaboration_section = ""
        if elaboration:
            elaboration_section = f"""
CURRENT ELABORATION:
{json.dumps(elaboration, indent=2, ensure_ascii=False)}
"""
        
        return f"""Fix the following issues in this interactive story:

STORY PARAMETERS:
- Genre: {genre}
- Grammar Focus: {grammar_focus}
- CEFR Level: {cefr_level}

CURRENT STORY DATA:
{json.dumps(story_data, indent=2, ensure_ascii=False)}

{elaboration_section}

ISSUES TO FIX ({len(issues)} total):
{issues_formatted}

INSTRUCTIONS:
1. Fix ALL issues listed above
2. Prioritize CRITICAL issues (these make story unplayable)
3. Maintain story coherence and flow
4. Preserve the core narrative and characters
5. Keep grammar focus ({grammar_focus}) naturally integrated
6. Match CEFR level ({cefr_level})
7. Make minimal changes necessary

SPECIFIC FIXES NEEDED:

For NPC issues:
- If NPC referenced but doesn't exist → add them to npcs list
- If NPC should appear in scene but doesn't → add to npcs_present
- If NPC in scene but shouldn't be → remove from npcs_present
- Update appears_in_scenes to match actual appearances

For Item issues:
- If item needed but doesn't exist → add to items list
- If item needed too early → move to earlier scene or NPC
- If item location unclear → clarify initial_location
- If location_details missing → generate appropriate location_description based on initial_location
- If acquisition_conditions missing → generate based on item type (search/container/automatic)
- Update items_available in scenes accordingly

For Objective issues:
- If objective targets non-existent NPC/item → change target or add NPC/item
- If objective unachievable → add required resources to scene
- If success conditions wrong → update to objectives_complete type
- Ensure min_objectives is reasonable (1-3)

For Plot issues:
- If scene has no next_scene → add next_scene_number or mark as ending
- If next_scene doesn't exist → fix the scene number
- If last scene not ending → set is_ending=true
- Ensure logical scene progression

For Structure issues:
- If missing required fields → add them
- If scene numbering wrong → renumber sequentially
- If too few NPCs/scenes → consider if acceptable or add more

For Item-Objective mismatches:
- If item in items_available but no item objective → CREATE item objective:
  {{
    "id": "obj_X",
    "type": "item",
    "target": "<item_name>",
    "description": "Find <item_name>",
    "description_trs": {{"ru": "Найдите <item_name>"}}
  }}
- If item objective exists but uses wrong type (information/action) → CHANGE type to "item"
- If item objective target doesn't match items_available → either add item to scene or fix target
- CRITICAL RULE: EVERY item in items_available MUST have corresponding item objective


RESPOND WITH JSON ONLY in this format:
{{
  "story_data": {{
    "story_name": "...",
    "description": "...",
    "npcs": [...],
    "items": [...],
    "scenes": [...]
  }},
  "elaboration": {{
    "npc_knowledge": {{}},
    "scene_connections": {{}},
    "key_plot_points": [],
    "mystery_solution": null
  }}
}}

CRITICAL: Ensure the fixed story has NO remaining issues. Double-check all references and connections.
"""

    def _fix_reveals_item_system(
            self,
            story_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Автоисправление educational discovery system

        Исправления:
        1. Создать information objectives для скрытых items без reveals_item
        2. Удалить reveals_item если item не существует
        3. Установить visible=false для items с reveals_item
        """

        logger.info("=== Fixing educational discovery system ===")

        # Собрать все items
        items_by_name = {
            item['name'].lower(): item
            for item in story_data.get('items', [])
        }

        fixes_applied = 0

        # Обработать каждую сцену
        for scene in story_data.get('scenes', []):
            scene_num = scene.get('scene_number')

            if 'detailed_objectives' not in scene:
                scene['detailed_objectives'] = {'objectives': [], 'scene_context': {}}

            objectives = scene['detailed_objectives']['objectives']

            # Собрать reveals_item из objectives
            reveals_items = set()

            for obj in objectives:
                reveals_item = obj.get('reveals_item')
                if reveals_item:
                    reveals_items.add(reveals_item.lower())

                    # ИСПРАВЛЕНИЕ 1: Удалить reveals_item если item не существует
                    if reveals_item.lower() not in items_by_name:
                        logger.warning(f"Scene {scene_num}: Removing invalid reveals_item '{reveals_item}'")
                        del obj['reveals_item']
                        fixes_applied += 1

            # ИСПРАВЛЕНИЕ 2: Создать information objectives для скрытых items
            items_available = scene.get('items_available', [])

            for item_name in items_available:
                item = items_by_name.get(item_name.lower())

                if item:
                    visible = item.get('location_details', {}).get('visible_on_look_around', True)

                    # Если item скрыт и нет reveals_item objective
                    if not visible and item_name.lower() not in reveals_items:
                        # Создать information objective
                        new_obj_id = f"obj_{len(objectives) + 1}"

                        new_objective = {
                            'id': new_obj_id,
                            'type': 'information',
                            'keywords': [item_name.lower(), 'where', 'find'],
                            'reveals_item': item_name,
                            'description': f"Ask where to find {item_name}",
                            'description_trs': {'ru': f"Спросите где найти {item_name}"}
                        }

                        objectives.append(new_objective)
                        reveals_items.add(item_name.lower())

                        logger.info(f"Scene {scene_num}: Created information objective for hidden item '{item_name}'")
                        fixes_applied += 1

            # ИСПРАВЛЕНИЕ 3: Установить visible=false для items с reveals_item
            for item_name in reveals_items:
                item = items_by_name.get(item_name)

                if item:
                    current_visible = item.get('location_details', {}).get('visible_on_look_around', True)

                    if current_visible:
                        item['location_details']['visible_on_look_around'] = False
                        logger.info(f"Set item '{item['name']}' to hidden (has reveals_item)")
                        fixes_applied += 1

        if fixes_applied > 0:
            logger.info(f"Applied {fixes_applied} educational discovery fixes")
        else:
            logger.info("No educational discovery fixes needed")

        return story_data

    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Парсить ответ AI"""
        
        try:
            # Убираем markdown блоки если есть
            cleaned = ai_response.strip()
            if cleaned.startswith('```'):
                lines = cleaned.split('\n')
                cleaned = '\n'.join(lines[1:-1]) if len(lines) > 2 else cleaned
            
            fixed_data = json.loads(cleaned)
            
            # Валидация что есть нужные поля
            if 'story_data' not in fixed_data:
                raise ValueError("AI response missing 'story_data' field")
            
            return fixed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI fix response: {e}")
            logger.error(f"Response: {ai_response[:500]}...")
            raise ValueError("AI returned invalid JSON for fixes")


class StoryFixerWithValidation:
    """
    Обёртка для Fixer + Validator - исправляет и валидирует результат
    """
    
    def __init__(self, pool):
        self.pool_base, self.pool_log = pool
        self.fixer = StoryFixer(pool)
    
    async def fix_and_validate(
        self,
        story_data: Dict[str, Any],
        validation_result: ValidationResult,
        elaboration: Optional[Dict[str, Any]] = None,
        genre: str = "",
        grammar_focus: str = "",
        cefr_level: str = "",
        max_attempts: int = 3
    ) -> tuple[Dict[str, Any], ValidationResult]:
        """
        Исправить историю и валидировать результат
        
        Повторяет процесс fix → validate до тех пор, пока история не станет валидной
        или не исчерпаются попытки
        
        Returns:
            (fixed_story_data, final_validation_result)
        """
        

        validator = StoryQualityValidator()
        
        current_story = story_data
        current_elaboration = elaboration
        current_validation = validation_result
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Fix + Validate attempt {attempt}/{max_attempts}")
            
            # Если уже валидна - всё ок
            if current_validation.is_valid:
                logger.info(f"Story is valid after {attempt-1} fix attempts")
                return {
                    'story_data': current_story,
                    'elaboration': current_elaboration
                }, current_validation
            
            # Исправляем
            try:
                fixed = await self.fixer.fix_story_issues(
                    current_story,
                    current_validation,
                    current_elaboration,
                    genre,
                    grammar_focus,
                    cefr_level
                )
                
                current_story = fixed['story_data']
                current_elaboration = fixed['elaboration']
                
            except ValueError as e:
                # Слишком много критических проблем - нужна полная регенерация
                logger.error(f"Cannot fix story: {e}")
                return {
                    'story_data': current_story,
                    'elaboration': current_elaboration
                }, current_validation
            
            # Валидируем результат
            current_validation = await validator.validate_story(
                current_story,
                current_elaboration
            )
            
            logger.info(f"After fix {attempt}: {current_validation}")
            
            # Если score улучшился до приемлемого уровня
            if current_validation.score >= 80:
                logger.info(f"Story score {current_validation.score} is acceptable")
                return {
                    'story_data': current_story,
                    'elaboration': current_elaboration
                }, current_validation
        
        # Исчерпали попытки
        logger.warning(f"Max fix attempts reached. Final score: {current_validation.score}")
        return {
            'story_data': current_story,
            'elaboration': current_elaboration
        }, current_validation


# ========================================
# Утилиты для интеграции
# ========================================

async def generate_and_validate_story(
    pool,
    user_id: int,
    genre: str,
    mood: str,
    realism: str,
    complexity: List[str],
    goal: str,
    initial_lesson_context: Dict[str, Any],
    num_chapters: int = 2,
    scenes_structure: List[int] = [2, 2],
    auto_fix: bool = True
) -> Dict[str, Any]:
    """
    Полный цикл: генерация → валидация → (опционально) исправление
    
    Args:
        pool: Database pool
        auto_fix: Если True, автоматически исправлять проблемы
        ... остальные параметры как в skeleton_generator
        
    Returns:
        {
            'story_data': {...},
            'elaboration': {...},
            'validation_result': ValidationResult,
            'was_fixed': bool
        }
    """
    

    
    logger.info("Starting full story generation pipeline")
    
    # 1. Генерация
    generator = StorySkeletonGeneratorV2(pool, user_id)
    result = await generator.generate_skeleton(
        #user_id=user_id,
        genre=genre,
        mood=mood,
        realism=realism,
        complexity=complexity,
        goal=goal,
        initial_lesson_context=initial_lesson_context,
        num_chapters=num_chapters,
        scenes_structure=scenes_structure
    )
    
    story_data = result
    elaboration = result.get('elaboration', {})
    
    # 2. Валидация
    validator = StoryQualityValidator()
    validation_result = await validator.validate_story(story_data, elaboration)
    
    logger.info(f"Initial validation: {validation_result}")
    validator.print_validation_report(validation_result)
    
    # 3. Исправление (если нужно)
    was_fixed = False
    if not validation_result.is_valid and auto_fix:
        logger.info("Story has issues, attempting auto-fix")
        
        fixer_with_validation = StoryFixerWithValidation(pool)
        fixed_result, final_validation = await fixer_with_validation.fix_and_validate(
            story_data,
            validation_result,
            elaboration,
            genre,
            initial_lesson_context['grammar_focus'],
            initial_lesson_context['cefr_level']
        )
        
        story_data = fixed_result['story_data']
        elaboration = fixed_result['elaboration']
        validation_result = final_validation
        was_fixed = True
        
        logger.info(f"After fixes: {validation_result}")
        validator.print_validation_report(validation_result)
    
    return {
        'story_data': story_data,
        'elaboration': elaboration,
        'validation_result': validation_result,
        'was_fixed': was_fixed,
        'story_id': result.get('story_id')
    }
