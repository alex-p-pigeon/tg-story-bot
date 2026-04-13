"""
Story Quality Validator - Валидация качества сгенерированных историй

Проверяет:
1. Целостность NPC (consistency)
2. Flow предметов (items)
3. Достижимость целей сцен (objectives)
4. Связность сюжета (plot coherence)
5. Соответствие грамматике
6. CEFR vocabulary level
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class IssueSeverity(Enum):
    """Серьёзность проблемы"""
    CRITICAL = "critical"  # История непроходима
    HIGH = "high"  # Серьёзные проблемы
    MEDIUM = "medium"  # Средние проблемы
    LOW = "low"  # Мелкие недочёты


@dataclass
class ValidationIssue:
    """Проблема валидации"""
    severity: IssueSeverity
    category: str  # npc, items, objectives, plot, grammar, vocabulary
    description: str
    location: str  # где проблема (scene 2, NPC John, etc)
    suggestion: str  # как исправить

    def to_dict(self) -> Dict[str, Any]:
        return {
            'severity': self.severity.value,
            'category': self.category,
            'description': self.description,
            'location': self.location,
            'suggestion': self.suggestion
        }


@dataclass
class ValidationResult:
    """Результат валидации"""
    is_valid: bool
    score: float  # 0-100
    issues: List[ValidationIssue]
    recommendations: List[str]
    
    def __str__(self) -> str:
        status = "VALID" if self.is_valid else "INVALID"
        return f"{status} | Score: {self.score}/100 | Issues: {len(self.issues)}"


class StoryQualityValidator:
    """
    Валидатор качества историй
    
    Проверяет целостность и логичность сгенерированной истории
    """

    def __init__(self):
        pass

    async def validate_story(
        self, 
        story_data: Dict[str, Any],
        elaboration: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Комплексная проверка качества истории
        
        Args:
            story_data: Базовый скелет истории
            elaboration: Детализация (опционально)
            
        Returns:
            ValidationResult с оценкой и списком проблем
        """
        
        logger.info(f"Validating story: {story_data.get('story_name', 'Unknown')}")
        
        issues = []
        
        # 1. Проверка целостности NPC
        issues.extend(await self._validate_npc_consistency(story_data))
        
        # 2. Проверка flow предметов
        issues.extend(await self._validate_items_flow(story_data))
        
        # 3. Проверка достижимости целей сцен
        issues.extend(await self._validate_objectives_achievable(story_data))
        
        # 4. Проверка связности сюжета
        issues.extend(await self._validate_plot_coherence(story_data, elaboration))
        
        # 5. Проверка структурной целостности
        issues.extend(await self._validate_structural_integrity(story_data))

        # 6. ✅ НОВАЯ ПРОВЕРКА: item objectives соответствуют items
        issues.extend(await self._validate_item_objectives_match(story_data))
        
        # Подсчёт score
        score = self._calculate_quality_score(issues)
        
        # Генерация рекомендаций
        recommendations = self._generate_recommendations(issues)
        
        # История валидна если нет критических проблем
        is_valid = not any(i.severity == IssueSeverity.CRITICAL for i in issues)
        
        result = ValidationResult(
            is_valid=is_valid,
            score=score,
            issues=issues,
            recommendations=recommendations
        )
        
        logger.info(f"Validation complete: {result}")
        
        return result

    async def _validate_item_objectives_match(
            self,
            story_data: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """
        Проверить что для каждого item в сцене есть соответствующий objective
        """

        issues = []
        scenes = story_data.get('scenes', [])
        items_list = story_data.get('items', [])

        # Создаем маппинг item_id -> item_name
        item_names_in_story = {item['name'] for item in items_list}

        for scene in scenes:
            scene_num = scene['scene_number']
            items_available = set(scene.get('items_available', []))

            # Получаем objectives этой сцены
            detailed_objectives = scene.get('c_detailed_objectives', {})
            if isinstance(detailed_objectives, str):
                import json
                detailed_objectives = json.loads(detailed_objectives)

            objectives = detailed_objectives.get('objectives', [])

            # Находим item objectives
            item_objectives_targets = set()
            for obj in objectives:
                if obj.get('type') == 'item':
                    target = obj.get('target')
                    if target:
                        item_objectives_targets.add(target)

            # Проверяем: для каждого item в items_available должен быть objective
            for item_name in items_available:
                # Проверяем существует ли item в базе
                if item_name not in item_names_in_story:
                    issues.append(ValidationIssue(
                        severity=IssueSeverity.CRITICAL,
                        category='items',
                        description=f"Scene references non-existent item '{item_name}' in items_available",
                        location=f"Scene {scene_num}",
                        suggestion=f"Remove '{item_name}' from items_available or add item to story"
                    ))
                    continue

                if item_name not in item_objectives_targets:
                    issues.append(ValidationIssue(
                        severity=IssueSeverity.HIGH,
                        category='objectives',
                        description=f"Item '{item_name}' in scene but no 'item' type objective for it",
                        location=f"Scene {scene_num}",
                        suggestion=f"Add item objective with target='{item_name}' and type='item'"
                    ))

            # Обратная проверка: item objectives должны ссылаться на items в сцене
            for obj in objectives:
                if obj.get('type') == 'item':
                    target = obj.get('target')
                    if target and target not in items_available:
                        # Проверим может item у NPC в этой сцене
                        item_found_with_npc = False
                        npcs_in_scene = scene.get('npcs_present', [])

                        for item in items_list:
                            if item['name'] == target:
                                initial_loc = item.get('initial_location', '')
                                if initial_loc.startswith('npc:'):
                                    npc_name = initial_loc.split(':')[1]
                                    if npc_name in npcs_in_scene:
                                        item_found_with_npc = True

                        if not item_found_with_npc:
                            issues.append(ValidationIssue(
                                severity=IssueSeverity.HIGH,
                                category='objectives',
                                description=f"Item objective targets '{target}', but item not available in scene",
                                location=f"Scene {scene_num}, objective {obj['id']}",
                                suggestion=f"Add '{target}' to items_available or remove objective"
                            ))

        return issues

    # ========================================
    # 1. Проверка целостности NPC
    # ========================================
    async def _validate_npc_consistency(
        self, 
        story_data: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Проверить целостность NPC"""
        
        issues = []
        npcs = story_data.get('npcs', [])
        scenes = story_data.get('scenes', [])
        
        # Создаём маппинг NPC имён
        npc_names = {npc['name'] for npc in npcs}
        
        for scene in scenes:
            scene_num = scene['scene_number']
            npcs_in_scene = set(scene.get('npcs_present', []))
            
            # Проверка 1: Все NPC в сцене должны существовать
            unknown_npcs = npcs_in_scene - npc_names
            if unknown_npcs:
                issues.append(ValidationIssue(
                    severity=IssueSeverity.CRITICAL,
                    category='npc',
                    description=f"Scene references non-existent NPCs: {', '.join(unknown_npcs)}",
                    location=f"Scene {scene_num}",
                    suggestion=f"Add these NPCs to the story or remove them from scene {scene_num}"
                ))
            
            # Проверка 2: NPC должен появиться в сцене согласно appears_in_scenes
            for npc in npcs:
                npc_name = npc['name']
                should_appear = scene_num in npc.get('appears_in_scenes', [])
                actually_appears = npc_name in npcs_in_scene
                
                if should_appear != actually_appears:
                    issues.append(ValidationIssue(
                        severity=IssueSeverity.HIGH,
                        category='npc',
                        description=f"NPC '{npc_name}' mismatch: appears_in_scenes says {should_appear}, but scene has {actually_appears}",
                        location=f"Scene {scene_num}, NPC {npc_name}",
                        suggestion=f"Update appears_in_scenes or npcs_present for consistency"
                    ))
            
            # Проверка 3: Success conditions должны ссылаться на существующих NPC
            success_cond = scene.get('success_conditions', {})
            target_npc = success_cond.get('target')
            
            if target_npc and target_npc not in npc_names:
                issues.append(ValidationIssue(
                    severity=IssueSeverity.CRITICAL,
                    category='objectives',
                    description=f"Success condition targets non-existent NPC '{target_npc}'",
                    location=f"Scene {scene_num}",
                    suggestion=f"Change target to an existing NPC or add '{target_npc}' to story"
                ))
            
            # Проверка 4: Если success condition требует NPC, он должен быть в сцене
            if target_npc and target_npc not in npcs_in_scene:
                issues.append(ValidationIssue(
                    severity=IssueSeverity.CRITICAL,
                    category='objectives',
                    description=f"Success requires talking to '{target_npc}', but they're not in scene",
                    location=f"Scene {scene_num}",
                    suggestion=f"Add '{target_npc}' to npcs_present in scene {scene_num}"
                ))
        
        return issues

    # ========================================
    # 2. Проверка flow предметов
    # ========================================

    async def _validate_items_flow(
        self, 
        story_data: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Проверить логику flow предметов"""
        
        issues = []
        items = story_data.get('items', [])
        scenes = story_data.get('scenes', [])
        
        # Создаём маппинг предметов
        item_names = {item['name'] for item in items}
        
        # Создаём граф доступности предметов
        item_availability = {}  # {item_name: scene_number_available}
        
        for item in items:
            item_name = item['name']

            # Проверка location_details
            if 'location_details' not in item or not item['location_details']:
                issues.append(ValidationIssue(
                    severity=IssueSeverity.CRITICAL,
                    category='items',
                    description=f"Item '{item_name}' missing location_details",
                    location=f"Item {item_name}",
                    suggestion=f"Add location_details with location_description, search_keywords, visible_on_look_around"
                ))
            else:
                loc_details = item['location_details']
                if not loc_details.get('location_description'):
                    issues.append(ValidationIssue(
                        severity=IssueSeverity.HIGH,
                        category='items',
                        description=f"Item '{item_name}' has empty location_description",
                        location=f"Item {item_name}",
                        suggestion=f"Add descriptive location_description"
                    ))

                if not loc_details.get('search_keywords'):
                    issues.append(ValidationIssue(
                        severity=IssueSeverity.MEDIUM,
                        category='items',
                        description=f"Item '{item_name}' has no search_keywords",
                        location=f"Item {item_name}",
                        suggestion=f"Add search_keywords list"
                    ))

            # Проверка acquisition_conditions
            if 'acquisition_conditions' not in item or not item['acquisition_conditions']:
                issues.append(ValidationIssue(
                    severity=IssueSeverity.CRITICAL,
                    category='items',
                    description=f"Item '{item_name}' missing acquisition_conditions",
                    location=f"Item {item_name}",
                    suggestion=f"Add acquisition_conditions with type and requirements"
                ))

            initial_loc = item.get('initial_location', '')
            
            if initial_loc.startswith('scene:'):
                scene_num = int(initial_loc.split(':')[1])
                item_availability[item_name] = scene_num
            elif initial_loc.startswith('npc:'):
                # Предмет у NPC - найдём в какой сцене NPC появляется впервые
                npc_name = initial_loc.split(':')[1]
                for npc in story_data.get('npcs', []):
                    if npc['name'] == npc_name:
                        appears_in = npc.get('appears_in_scenes', [])
                        if appears_in:
                            item_availability[item_name] = min(appears_in)
                        break
            elif initial_loc == 'inventory':
                item_availability[item_name] = 0  # Доступен с начала
        
        # Проверяем каждую сцену
        for scene in scenes:
            scene_num = scene['scene_number']
            items_in_scene = set(scene.get('items_available', []))
            
            # Проверка 1: Все предметы в сцене должны существовать
            unknown_items = items_in_scene - item_names
            if unknown_items:
                issues.append(ValidationIssue(
                    severity=IssueSeverity.CRITICAL,
                    category='items',
                    description=f"Scene references non-existent items: {', '.join(unknown_items)}",
                    location=f"Scene {scene_num}",
                    suggestion=f"Add these items to the story or remove from scene {scene_num}"
                ))
            
            # Проверка 2: Success conditions с item_obtained - предмет должен быть доступен
            success_cond = scene.get('success_conditions', {})
            if success_cond.get('type') == 'item_obtained':
                target_item = success_cond.get('target')
                
                if target_item and target_item not in item_names:
                    issues.append(ValidationIssue(
                        severity=IssueSeverity.CRITICAL,
                        category='items',
                        description=f"Success requires obtaining non-existent item '{target_item}'",
                        location=f"Scene {scene_num}",
                        suggestion=f"Add item '{target_item}' to story or change success condition"
                    ))
                
                # Проверяем доступен ли предмет к этому моменту
                if target_item in item_availability:
                    available_from = item_availability[target_item]
                    if available_from > scene_num:
                        issues.append(ValidationIssue(
                            severity=IssueSeverity.CRITICAL,
                            category='items',
                            description=f"Item '{target_item}' needed in scene {scene_num}, but only available from scene {available_from}",
                            location=f"Scene {scene_num}",
                            suggestion=f"Move item to earlier scene or change objective"
                        ))
            
            # Проверка 3: Success conditions с item_use
            if success_cond.get('type') == 'item_use':
                target_item = success_cond.get('target')
                
                if target_item and target_item in item_availability:
                    available_from = item_availability[target_item]
                    if available_from >= scene_num:
                        issues.append(ValidationIssue(
                            severity=IssueSeverity.HIGH,
                            category='items',
                            description=f"Item '{target_item}' must be used in scene {scene_num}, but only available from scene {available_from}",
                            location=f"Scene {scene_num}",
                            suggestion=f"Make item available before scene {scene_num}"
                        ))
        
        return issues

    # ========================================
    # 3. Проверка достижимости целей
    # ========================================

    async def _validate_objectives_achievable(
        self, 
        story_data: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Проверить что цели сцен достижимы"""
        
        issues = []
        scenes = story_data.get('scenes', [])
        
        for scene in scenes:
            scene_num = scene['scene_number']
            success_cond = scene.get('success_conditions', {})
            cond_type = success_cond.get('type')
            
            # Проверяем разные типы условий
            if cond_type == 'dialogue_complete':
                # Должны быть NPC в сцене
                npcs_in_scene = scene.get('npcs_present', [])
                if not npcs_in_scene:
                    issues.append(ValidationIssue(
                        severity=IssueSeverity.CRITICAL,
                        category='objectives',
                        description=f"Success requires dialogue, but no NPCs present in scene",
                        location=f"Scene {scene_num}",
                        suggestion=f"Add NPCs to scene {scene_num} or change success condition"
                    ))
            
            elif cond_type == 'item_obtained':
                # Предмет должен быть доступен в сцене или у NPC в сцене
                target_item = success_cond.get('target')
                items_in_scene = scene.get('items_available', [])
                
                if target_item and target_item not in items_in_scene:
                    # Проверим может он у NPC
                    npcs_in_scene = scene.get('npcs_present', [])
                    item_found = False
                    
                    for item in story_data.get('items', []):
                        if item['name'] == target_item:
                            initial_loc = item.get('initial_location', '')
                            if initial_loc.startswith('npc:'):
                                npc_name = initial_loc.split(':')[1]
                                if npc_name in npcs_in_scene:
                                    item_found = True
                    
                    if not item_found:
                        issues.append(ValidationIssue(
                            severity=IssueSeverity.CRITICAL,
                            category='objectives',
                            description=f"Success requires obtaining '{target_item}', but it's not available in scene",
                            location=f"Scene {scene_num}",
                            suggestion=f"Add '{target_item}' to items_available or to an NPC in scene"
                        ))
            
            elif cond_type == 'objectives_complete':
                # Проверяем минимальное количество objectives
                min_objectives = success_cond.get('min_objectives', 0)
                if min_objectives <= 0:
                    issues.append(ValidationIssue(
                        severity=IssueSeverity.HIGH,
                        category='objectives',
                        description=f"objectives_complete type but min_objectives is {min_objectives}",
                        location=f"Scene {scene_num}",
                        suggestion=f"Set min_objectives to at least 1"
                    ))

        issues.extend(self._validate_reveals_item_system(story_data))

        return issues

    def _validate_reveals_item_system(
            self,
            story_data: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """
        Проверить корректность educational discovery (reveals_item)

        Проверки:
        1. Каждый reveals_item указывает на существующий item
        2. Каждый скрытый item имеет соответствующий reveals_item objective
        3. reveals_item только у information objectives
        """

        issues = []

        # Собрать все items
        items_by_name = {
            item['name'].lower(): item
            for item in story_data.get('items', [])
        }

        # Проверить каждую сцену
        for scene in story_data.get('scenes', []):
            scene_num = scene.get('scene_number')
            objectives = scene.get('detailed_objectives', {}).get('objectives', [])

            # Собрать reveals_item из objectives
            reveals_items = {}  # {item_name: obj_id}

            for obj in objectives:
                obj_id = obj.get('id')
                obj_type = obj.get('type')
                reveals_item = obj.get('reveals_item')

                if reveals_item:
                    # ПРОВЕРКА 1: reveals_item только у information objectives
                    if obj_type != 'information':
                        issues.append(ValidationIssue(
                            severity=IssueSeverity.HIGH,
                            category='objectives',
                            description=f"Objective {obj_id} has reveals_item but type is '{obj_type}' (should be 'information')",
                            location=f"Scene {scene_num}",
                            suggestion=f"Change objective type to 'information' or remove reveals_item"
                        ))

                    # ПРОВЕРКА 2: reveals_item указывает на существующий item
                    if reveals_item.lower() not in items_by_name:
                        issues.append(ValidationIssue(
                            severity=IssueSeverity.CRITICAL,
                            category='objectives',
                            description=f"Objective {obj_id} reveals non-existent item '{reveals_item}'",
                            location=f"Scene {scene_num}",
                            suggestion=f"Create item '{reveals_item}' or fix reveals_item value"
                        ))
                    else:
                        reveals_items[reveals_item.lower()] = obj_id

            # ПРОВЕРКА 3: Скрытые items имеют reveals_item objective
            items_available = scene.get('items_available', [])

            for item_name in items_available:
                item = items_by_name.get(item_name.lower())

                if item:
                    visible = item.get('location_details', {}).get('visible_on_look_around', True)

                    # Если item скрыт, должен быть reveals_item objective
                    if not visible and item_name.lower() not in reveals_items:
                        issues.append(ValidationIssue(
                            severity=IssueSeverity.HIGH,
                            category='items',
                            description=f"Item '{item_name}' is hidden but has no reveals_item objective",
                            location=f"Scene {scene_num}",
                            suggestion=f"Add information objective with reveals_item: '{item_name}'"
                        ))

        if issues:
            logger.warning(f"Found {len(issues)} reveals_item issues")
        else:
            logger.info("Educational discovery system is valid")

        return issues

    # ========================================
    # 4. Проверка связности сюжета
    # ========================================

    async def _validate_plot_coherence(
        self, 
        story_data: Dict[str, Any],
        elaboration: Optional[Dict[str, Any]] = None
    ) -> List[ValidationIssue]:
        """Проверить связность сюжета"""
        
        issues = []
        scenes = story_data.get('scenes', [])
        
        # Проверка 1: Каждая сцена (кроме последней) должна иметь next_scene
        for scene in scenes:
            scene_num = scene['scene_number']
            is_ending = scene.get('is_ending', False)
            next_scene = scene.get('next_scene_number')
            
            if not is_ending and not next_scene:
                issues.append(ValidationIssue(
                    severity=IssueSeverity.CRITICAL,
                    category='plot',
                    description=f"Scene {scene_num} is not ending but has no next_scene",
                    location=f"Scene {scene_num}",
                    suggestion=f"Add next_scene_number or mark as ending"
                ))
        
        # Проверка 2: Последняя сцена должна быть ending
        if scenes:
            last_scene = max(scenes, key=lambda s: s['scene_number'])
            if not last_scene.get('is_ending'):
                issues.append(ValidationIssue(
                    severity=IssueSeverity.HIGH,
                    category='plot',
                    description=f"Last scene {last_scene['scene_number']} is not marked as ending",
                    location=f"Scene {last_scene['scene_number']}",
                    suggestion=f"Set is_ending=true for last scene"
                ))
        
        # Проверка 3: Все next_scene должны существовать
        scene_numbers = {s['scene_number'] for s in scenes}
        for scene in scenes:
            next_scene = scene.get('next_scene_number')
            if next_scene and next_scene not in scene_numbers:
                issues.append(ValidationIssue(
                    severity=IssueSeverity.CRITICAL,
                    category='plot',
                    description=f"Scene {scene['scene_number']} references non-existent next scene {next_scene}",
                    location=f"Scene {scene['scene_number']}",
                    suggestion=f"Fix next_scene_number to point to existing scene"
                ))
        
        # Проверка 4: Если есть elaboration, проверяем mystery solution
        if elaboration:
            mystery_solution = elaboration.get('mystery_solution')
            genre = story_data.get('genre', '')
            
            if genre in ['mystery', 'detective'] and not mystery_solution:
                issues.append(ValidationIssue(
                    severity=IssueSeverity.HIGH,
                    category='plot',
                    description=f"Mystery genre story but no mystery_solution provided",
                    location="Elaboration",
                    suggestion=f"Add mystery_solution to elaboration"
                ))
        
        return issues

    # ========================================
    # 5. Структурная целостность
    # ========================================

    async def _validate_structural_integrity(
        self, 
        story_data: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Проверить структурную целостность"""
        
        issues = []
        
        # Проверка обязательных полей
        required_fields = ['story_name', 'description', 'npcs', 'items', 'scenes']
        for field in required_fields:
            if field not in story_data:
                issues.append(ValidationIssue(
                    severity=IssueSeverity.CRITICAL,
                    category='structure',
                    description=f"Missing required field: {field}",
                    location="Story root",
                    suggestion=f"Add {field} to story data"
                ))
        
        # Проверка минимального количества элементов
        if len(story_data.get('npcs', [])) < 2:
            issues.append(ValidationIssue(
                severity=IssueSeverity.HIGH,
                category='structure',
                description=f"Only {len(story_data.get('npcs', []))} NPCs (minimum 2 recommended)",
                location="NPCs",
                suggestion="Add more NPCs for richer story"
            ))
        
        if len(story_data.get('scenes', [])) < 2:
            issues.append(ValidationIssue(
                severity=IssueSeverity.HIGH,
                category='structure',
                description=f"Only {len(story_data.get('scenes', []))} scenes (minimum 2 recommended)",
                location="Scenes",
                suggestion="Add more scenes for longer story"
            ))
        
        # Проверка numbering сцен
        scenes = story_data.get('scenes', [])
        scene_numbers = sorted([s['scene_number'] for s in scenes])
        expected_numbers = list(range(1, len(scenes) + 1))
        
        if scene_numbers != expected_numbers:
            issues.append(ValidationIssue(
                severity=IssueSeverity.HIGH,
                category='structure',
                description=f"Scene numbers are not sequential: {scene_numbers}",
                location="Scenes",
                suggestion="Renumber scenes sequentially starting from 1"
            ))
        
        return issues

    # ========================================
    # Scoring и рекомендации
    # ========================================

    def _calculate_quality_score(self, issues: List[ValidationIssue]) -> float:
        """
        Подсчитать score качества (0-100)
        
        Штрафы:
        - CRITICAL: -25 points
        - HIGH: -10 points
        - MEDIUM: -5 points
        - LOW: -2 points
        """
        
        score = 100.0
        
        for issue in issues:
            if issue.severity == IssueSeverity.CRITICAL:
                score -= 25
            elif issue.severity == IssueSeverity.HIGH:
                score -= 10
            elif issue.severity == IssueSeverity.MEDIUM:
                score -= 5
            elif issue.severity == IssueSeverity.LOW:
                score -= 2
        
        return max(0.0, score)

    def _generate_recommendations(self, issues: List[ValidationIssue]) -> List[str]:
        """Сгенерировать рекомендации на основе проблем"""
        
        recommendations = []
        
        # Группируем по категориям
        categories = {}
        for issue in issues:
            cat = issue.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(issue)
        
        # Рекомендации по категориям
        if 'npc' in categories:
            recommendations.append(
                f"Fix {len(categories['npc'])} NPC consistency issues - ensure NPCs appear correctly in scenes"
            )
        
        if 'items' in categories:
            recommendations.append(
                f"Fix {len(categories['items'])} item flow issues - ensure items are available when needed"
            )
        
        if 'objectives' in categories:
            recommendations.append(
                f"Fix {len(categories['objectives'])} objective issues - ensure all objectives are achievable"
            )
        
        if 'plot' in categories:
            recommendations.append(
                f"Fix {len(categories['plot'])} plot coherence issues - ensure story flows logically"
            )
        
        if 'structure' in categories:
            recommendations.append(
                f"Fix {len(categories['structure'])} structural issues - ensure all required fields present"
            )
        
        # Если много критических проблем
        critical_count = sum(1 for i in issues if i.severity == IssueSeverity.CRITICAL)
        if critical_count >= 3:
            recommendations.insert(0, f"!!!️ {critical_count} CRITICAL issues found - story may be unplayable. Consider regenerating.")
        
        return recommendations

    def print_validation_report(self, result: ValidationResult):
        """Распечатать красивый отчёт валидации"""
        
        logger.info("\n" + "="*70)
        logger.info("STORY QUALITY VALIDATION REPORT")
        logger.info("="*70)
        logger.info(f"\n{result}\n")
        
        if result.issues:
            logger.info("ISSUES FOUND:\n")
            
            # Группируем по severity
            by_severity = {}
            for issue in result.issues:
                sev = issue.severity.value
                if sev not in by_severity:
                    by_severity[sev] = []
                by_severity[sev].append(issue)
            
            # Печатаем по severity
            severity_order = ['critical', 'high', 'medium', 'low']
            severity_icons = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }
            
            for sev in severity_order:
                if sev in by_severity:
                    logger.info(f"\n{severity_icons[sev]} {sev.upper()} ({len(by_severity[sev])} issues):")
                    for issue in by_severity[sev]:
                        logger.info(f"  - [{issue.category}] {issue.description}")
                        logger.info(f"    Location: {issue.location}")
                        logger.info(f"    Fix: {issue.suggestion}")

        
        if result.recommendations:
            logger.info("\n RECOMMENDATIONS:\n")
            for i, rec in enumerate(result.recommendations, 1):
                logger.info(f"  {i}. {rec}")
        
        logger.info("\n" + "="*70 + "\n")
