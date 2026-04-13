"""迭代改进器"""
import time
from typing import Dict, Any, List
from dataclasses import dataclass, field
from src.evaluators.base import EvaluationResult
from src.translators.base import BaseTranslator, TranslationRequest, TranslationResult
from src.utils.logger import get_logger
from src.utils.exceptions import TranslationError


@dataclass
class ImprovementResult:
    """改进结果"""
    final_text: str
    final_score: float
    iterations: int
    improvement_history: List[Dict[str, Any]] = field(default_factory=list)
    success: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class IterativeImprover:
    """迭代改进器 - 自动改进低质量翻译"""
    
    name = "iterative_improver"
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = get_logger(__name__)
        
        self.quality_threshold = self.config.get("quality_threshold", 85.0)
        self.max_iterations = self.config.get("max_iterations", 3)
        self.improvement_delay = self.config.get("improvement_delay", 1.0)
        self.enable_improvement = self.config.get("enable_improvement", True)
    
    def improve_translation(
        self,
        original_text: str,
        translated_text: str,
        evaluation_result: EvaluationResult,
        translator: BaseTranslator,
        source_language: str,
        target_language: str
    ) -> ImprovementResult:
        """改进翻译质量"""
        self.logger.info(
            "improvement_started",
            initial_score=evaluation_result.overall_score,
            threshold=self.quality_threshold,
            max_iterations=self.max_iterations
        )
        
        if not self.enable_improvement:
            self.logger.info("improvement_disabled")
            return ImprovementResult(
                final_text=translated_text,
                final_score=evaluation_result.overall_score,
                iterations=0,
                success=True,
                metadata={"improvement_disabled": True}
            )
        
        if not self._should_continue_improvement(evaluation_result.overall_score, 0):
            self.logger.info(
                "no_improvement_needed",
                score=evaluation_result.overall_score,
                threshold=self.quality_threshold
            )
            return ImprovementResult(
                final_text=translated_text,
                final_score=evaluation_result.overall_score,
                iterations=0,
                success=True,
                metadata={"no_improvement_needed": True}
            )
        
        current_text = translated_text
        current_score = evaluation_result.overall_score
        current_issues = evaluation_result.issues
        current_suggestions = evaluation_result.suggestions
        
        improvement_history = []
        iteration = 0
        
        while self._should_continue_improvement(current_score, iteration):
            iteration += 1
            
            self.logger.info(
                "improvement_iteration_started",
                iteration=iteration,
                current_score=current_score
            )
            
            improvement_prompt = self._build_improvement_prompt(
                original_text,
                current_text,
                current_issues,
                current_suggestions
            )
            
            try:
                translation_request = TranslationRequest(
                    text=improvement_prompt,
                    source_language=source_language,
                    target_language=target_language,
                    context=f"Improve previous translation (iteration {iteration})"
                )
                
                translation_result = translator.translate(translation_request)
                current_text = translation_result.text
                
                from src.evaluators.base import EvaluationRequest
                evaluation_request = EvaluationRequest(
                    original_text=original_text,
                    translated_text=current_text,
                    source_language=source_language,
                    target_language=target_language
                )
                
                from src.evaluators import get_evaluator
                evaluator = get_evaluator()
                new_evaluation_result = evaluator.evaluate(evaluation_request)
                current_score = new_evaluation_result.overall_score
                current_issues = new_evaluation_result.issues
                current_suggestions = new_evaluation_result.suggestions
                
                improvement_history.append(self._track_improvement(
                    iteration,
                    current_score,
                    current_issues
                ))
                
                self.logger.info(
                    "improvement_iteration_completed",
                    iteration=iteration,
                    new_score=current_score,
                    issues_count=len(current_issues)
                )
                
                if self.improvement_delay > 0 and iteration < self.max_iterations:
                    time.sleep(self.improvement_delay)
            
            except Exception as e:
                self.logger.error(
                    "improvement_iteration_failed",
                    iteration=iteration,
                    error=str(e)
                )
                improvement_history.append({
                    "iteration": iteration,
                    "error": str(e),
                    "score": current_score
                })
                break
        
        success = current_score >= self.quality_threshold
        
        self.logger.info(
            "improvement_completed",
            final_score=current_score,
            iterations=iteration,
            success=success
        )
        
        return ImprovementResult(
            final_text=current_text,
            final_score=current_score,
            iterations=iteration,
            improvement_history=improvement_history,
            success=success,
            metadata={
                "original_score": evaluation_result.overall_score,
                "threshold": self.quality_threshold,
                "max_iterations": self.max_iterations
            }
        )
    
    def _should_continue_improvement(self, score: float, iteration: int) -> bool:
        """检查是否应该继续改进"""
        return score < self.quality_threshold and iteration < self.max_iterations
    
    def _build_improvement_prompt(
        self,
        original_text: str,
        translated_text: str,
        issues: List[str],
        suggestions: List[str]
    ) -> str:
        """构建改进提示词"""
        prompt = f"""The previous translation had quality issues. Please improve it.

Original text:
{original_text}

Previous translation:
{translated_text}

Issues found:
{chr(10).join(f'- {issue}' for issue in issues)}

Suggestions for improvement:
{chr(10).join(f'- {suggestion}' for suggestion in suggestions)}

Please provide an improved translation that addresses these issues while maintaining accuracy and fluency."""
        
        return prompt
    
    def _track_improvement(
        self,
        iteration: int,
        score: float,
        issues: List[str]
    ) -> Dict[str, Any]:
        """跟踪改进进度"""
        return {
            "iteration": iteration,
            "score": score,
            "issues_count": len(issues),
            "issues": issues
        }
