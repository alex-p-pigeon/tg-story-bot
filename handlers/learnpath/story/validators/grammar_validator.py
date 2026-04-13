"""
Grammar and Vocabulary Validator
AI-driven validation of story texts for grammar correctness and vocabulary level
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import selfFunctions as myF

logger = logging.getLogger(__name__)


@dataclass
class GrammarIssue:
    """Single grammar/vocabulary issue"""
    location: str  # "scene_2_description", "npc_3_dialogue"
    issue_type: str  # "grammar", "vocabulary", "cefr_mismatch"
    severity: str  # "high", "medium", "low"
    description: str
    suggestion: str


@dataclass
class GrammarValidationResult:
    """Grammar validation result"""
    is_valid: bool
    grammar_score: float  # 0-100
    issues: List[GrammarIssue]
    cefr_level_detected: str
    cefr_level_target: str
    recommendations: List[str]


class GrammarValidator:
    """
    Validates story texts for grammar and vocabulary
    Uses AI to check:
    - Grammar correctness
    - Vocabulary appropriateness for CEFR level
    - Text complexity
    """

    def __init__(self, pool=None, user_id: int = 0):
        """
        Args:
            pool: Database pool (для myF.afSendMsg2AI)
            user_id: User ID (для логирования токенов)
        """
        self.pool = pool
        self.user_id = user_id
        
    async def validate_story_texts(
        self,
        story_skeleton: dict,
        story_elaboration: dict,
        target_cefr: str = "B1"
    ) -> GrammarValidationResult:
        """
        Validate all story texts for grammar and vocabulary
        
        Args:
            story_skeleton: Story skeleton data
            story_elaboration: Story elaboration data
            target_cefr: Target CEFR level (A1, A2, B1, B2, C1, C2)
            
        Returns:
            GrammarValidationResult with issues and score
        """
        
        logger.info(f"=== Starting grammar validation for CEFR {target_cefr} ===")
        
        issues = []
        
        # 1. Validate story description
        story_name = story_skeleton.get('story_name', '')
        story_description = story_skeleton.get('description', '')
        
        if story_description and isinstance(story_description, str):
            desc_issues = await self._validate_text(
                text=story_description,
                location="story_description",
                target_cefr=target_cefr,
                context="story introduction"
            )
            issues.extend(desc_issues)
        
        # 2. Validate scenes
        scenes = story_skeleton.get('scenes', [])
        for i, scene in enumerate(scenes, 1):
            # Scene description
            location_desc = scene.get('location_description', '')
            if location_desc and isinstance(location_desc, str):
                scene_issues = await self._validate_text(
                    text=location_desc,
                    location=f"scene_{i}_description",
                    target_cefr=target_cefr,
                    context=f"scene description"
                )
                issues.extend(scene_issues)
            
            # Scene objective
            objective = scene.get('objective', '')
            if objective and isinstance(objective, str):
                obj_issues = await self._validate_text(
                    text=objective,
                    location=f"scene_{i}_objective",
                    target_cefr=target_cefr,
                    context="task description"
                )
                issues.extend(obj_issues)
        
        # 3. Validate NPCs
        npcs = story_skeleton.get('npcs', [])
        for i, npc in enumerate(npcs, 1):
            # NPC description
            description = npc.get('description', '')
            if description and isinstance(description, str):
                npc_issues = await self._validate_text(
                    text=description,
                    location=f"npc_{i}_description",
                    target_cefr=target_cefr,
                    context="character description"
                )
                issues.extend(npc_issues)
            
            # NPC personality - может быть dict или str
            personality = npc.get('personality', '')
            
            # Если personality это dict - извлекаем текстовые поля
            if isinstance(personality, dict):
                # Объединяем все текстовые значения из dict
                personality_texts = []
                for key, value in personality.items():
                    if isinstance(value, str) and value:
                        personality_texts.append(value)
                
                if personality_texts:
                    combined_personality = " ".join(personality_texts)
                    pers_issues = await self._validate_text(
                        text=combined_personality,
                        location=f"npc_{i}_personality",
                        target_cefr=target_cefr,
                        context="character traits"
                    )
                    issues.extend(pers_issues)
            
            elif isinstance(personality, str) and personality:
                pers_issues = await self._validate_text(
                    text=personality,
                    location=f"npc_{i}_personality",
                    target_cefr=target_cefr,
                    context="character traits"
                )
                issues.extend(pers_issues)
        
        # 4. Validate Items
        items = story_skeleton.get('items', [])
        for i, item in enumerate(items, 1):
            description = item.get('description', '')
            if description and isinstance(description, str):
                item_issues = await self._validate_text(
                    text=description,
                    location=f"item_{i}_description",
                    target_cefr=target_cefr,
                    context="object description"
                )
                issues.extend(item_issues)
        
        # Calculate score
        grammar_score = self._calculate_grammar_score(issues)
        
        # Detect overall CEFR level
        detected_cefr = await self._detect_overall_cefr(story_skeleton, story_elaboration)
        
        # Generate recommendations
        recommendations = self._generate_grammar_recommendations(issues, detected_cefr, target_cefr)
        
        is_valid = grammar_score >= 70 and abs(self._cefr_to_num(detected_cefr) - self._cefr_to_num(target_cefr)) <= 1
        
        result = GrammarValidationResult(
            is_valid=is_valid,
            grammar_score=grammar_score,
            issues=issues,
            cefr_level_detected=detected_cefr,
            cefr_level_target=target_cefr,
            recommendations=recommendations
        )
        
        logger.info(f"=== Grammar validation complete: score={grammar_score:.1f}, valid={is_valid} ===")
        
        return result
    
    async def _validate_text(
        self,
        text: str,
        location: str,
        target_cefr: str,
        context: str
    ) -> List[GrammarIssue]:
        """
        Validate single text fragment using AI
        
        Returns:
            List of GrammarIssue objects
        """
        
        # Safety check: ensure text is string
        if not isinstance(text, str):
            logger.warning(f"Skipping validation at {location}: text is not string (type: {type(text)})")
            return []
        
        if not text or len(text.strip()) < 3:
            return []
        
        try:
            # Import here to avoid circular dependency
            import openai
            
            # Build prompt for AI
            prompt = f"""Analyze this English text for grammar and vocabulary appropriateness.

Text: "{text}"

Context: {context}
Target CEFR level: {target_cefr}

Check for:
1. Grammar errors (tense, agreement, word order, articles)
2. Vocabulary level (is it appropriate for {target_cefr}?)
3. Sentence complexity (too simple or too complex for {target_cefr}?)

Respond ONLY with valid JSON:
{{
  "issues": [
    {{
      "type": "grammar|vocabulary|cefr_mismatch",
      "severity": "high|medium|low",
      "description": "Brief description",
      "suggestion": "How to fix"
    }}
  ],
  "detected_cefr": "A1|A2|B1|B2|C1|C2"
}}

DO NOT OUTPUT ANYTHING OTHER THAN VALID JSON."""

            # Call OpenAI
            response = await self._call_openai(
                prompt=prompt,
                system_prompt="You are a grammar and CEFR level analyzer. Respond only with valid JSON."
            )
            
            # Parse response
            try:
                data = json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown
                response = response.strip()
                if response.startswith("```json"):
                    response = response.replace("```json\n", "").replace("```\n", "").replace("```", "").strip()
                data = json.loads(response)
            
            # Convert to GrammarIssue objects
            issues = []
            for issue_data in data.get('issues', []):
                issue = GrammarIssue(
                    location=location,
                    issue_type=issue_data.get('type', 'grammar'),
                    severity=issue_data.get('severity', 'medium'),
                    description=issue_data.get('description', ''),
                    suggestion=issue_data.get('suggestion', '')
                )
                issues.append(issue)
            
            return issues
            
        except Exception as e:
            logger.error(f"Error validating text at {location}: {e}")
            return []
    
    async def _detect_overall_cefr(
        self,
        story_skeleton: dict,
        story_elaboration: dict
    ) -> str:
        """
        Detect overall CEFR level of story using AI
        
        Returns:
            CEFR level string (A1, A2, B1, B2, C1, C2)
        """
        
        try:
            # Sample texts from story
            sample_texts = []
            
            # Story description
            if story_skeleton.get('description'):
                sample_texts.append(story_skeleton['description'])
            
            # 2 scene descriptions
            scenes = story_skeleton.get('scenes', [])
            for scene in scenes[:2]:
                if scene.get('location_description'):
                    sample_texts.append(scene['location_description'])
            
            # 2 NPC descriptions
            npcs = story_skeleton.get('npcs', [])
            for npc in npcs[:2]:
                if npc.get('description'):
                    sample_texts.append(npc['description'])
            
            combined_text = "\n\n".join(sample_texts)
            
            prompt = f"""Analyze the overall CEFR level of this story text.

Text samples:
{combined_text}

What is the CEFR level of this text?

Respond ONLY with valid JSON:
{{
  "cefr_level": "A1|A2|B1|B2|C1|C2",
  "reasoning": "Brief explanation"
}}

DO NOT OUTPUT ANYTHING OTHER THAN VALID JSON."""

            response = await self._call_openai(
                prompt=prompt,
                system_prompt="You are a grammar and CEFR level analyzer. Respond only with valid JSON."
            )
            
            try:
                data = json.loads(response)
            except json.JSONDecodeError:
                response = response.strip()
                if response.startswith("```json"):
                    response = response.replace("```json\n", "").replace("```\n", "").replace("```", "").strip()
                data = json.loads(response)
            
            detected_cefr = data.get('cefr_level', 'B1')
            logger.info(f"Detected CEFR level: {detected_cefr} - {data.get('reasoning', '')}")
            
            return detected_cefr
            
        except Exception as e:
            logger.error(f"Error detecting CEFR: {e}")
            return "B1"  # Default fallback
    
    async def _call_openai(self, prompt: str, system_prompt: str = "") -> str:
        """
        Call OpenAI API using myF.afSendMsg2AI
        
        Returns:
            Response text
        """
        
        try:

            
            if not self.pool:
                raise ValueError("Pool is required for myF.afSendMsg2AI")
            
            # Используем готовую функцию!
            response = await myF.afSendMsg2AI(
                userPrompt=prompt,
                pool=self.pool,
                vUserID=self.user_id,
                iModel=0,  # gpt-4o-mini (cheaper)
                toggleParam=2,  # With system prompt, temperature 0.2
                systemPrompt=system_prompt or "You are a grammar and CEFR level analyzer. Respond only with valid JSON."
            )
            
            return response
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _calculate_grammar_score(self, issues: List[GrammarIssue]) -> float:
        """
        Calculate grammar score from issues
        
        Returns:
            Score 0-100
        """
        
        score = 100.0
        
        for issue in issues:
            if issue.severity == 'high':
                score -= 15
            elif issue.severity == 'medium':
                score -= 8
            elif issue.severity == 'low':
                score -= 3
        
        return max(0.0, score)
    
    def _generate_grammar_recommendations(
        self,
        issues: List[GrammarIssue],
        detected_cefr: str,
        target_cefr: str
    ) -> List[str]:
        """Generate recommendations based on issues"""
        
        recommendations = []
        
        # CEFR mismatch
        detected_num = self._cefr_to_num(detected_cefr)
        target_num = self._cefr_to_num(target_cefr)
        
        if detected_num > target_num + 1:
            recommendations.append(f"Story is too complex for {target_cefr}. Simplify vocabulary and sentence structure.")
        elif detected_num < target_num - 1:
            recommendations.append(f"Story is too simple for {target_cefr}. Use more varied vocabulary and complex sentences.")
        
        # Grammar issues
        grammar_issues = [i for i in issues if i.issue_type == 'grammar']
        if len(grammar_issues) > 5:
            recommendations.append(f"Found {len(grammar_issues)} grammar issues. Review and fix before deployment.")
        
        # Vocabulary issues
        vocab_issues = [i for i in issues if i.issue_type == 'vocabulary']
        if len(vocab_issues) > 3:
            recommendations.append(f"Vocabulary not appropriate for target level. Replace {len(vocab_issues)} words.")
        
        return recommendations
    
    def _cefr_to_num(self, cefr: str) -> int:
        """Convert CEFR to number for comparison"""
        mapping = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}
        return mapping.get(cefr.upper(), 3)
    
    def print_grammar_report(self, result: GrammarValidationResult):
        """Print readable grammar validation report"""
        
        logger.info("\n" + "=" * 60)
        logger.info("GRAMMAR VALIDATION REPORT")
        logger.info("=" * 60)
        
        logger.info(f"\n Valid: {result.is_valid}")
        logger.info(f"Grammar Score: {result.grammar_score:.1f}/100")
        logger.info(f"Detected CEFR: {result.cefr_level_detected}")
        logger.info(f"Target CEFR: {result.cefr_level_target}")
        
        if result.issues:
            logger.info(f"\n!!!️ Issues Found: {len(result.issues)}")
            logger.info("-" * 60)
            
            # Group by severity
            for severity in ['high', 'medium', 'low']:
                severity_issues = [i for i in result.issues if i.severity == severity]
                if severity_issues:
                    logger.info(f"\n{severity.upper()} SEVERITY ({len(severity_issues)}):")
                    for issue in severity_issues:
                        logger.info(f"  - [{issue.location}] {issue.description}")
                        logger.info(f"    !!! {issue.suggestion}")
        
        if result.recommendations:
            logger.info(f"\n!!! Recommendations:")
            for i, rec in enumerate(result.recommendations, 1):
                logger.info(f"  {i}. {rec}")
        
        logger.info("\n" + "=" * 60 + "\n")
