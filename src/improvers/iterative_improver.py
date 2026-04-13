"""迭代改进器"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

from src.evaluators.base import BaseEvaluator, EvaluationRequest, EvaluationResult
from src.translators.base import BaseTranslator, TranslationRequest
from src.utils.logger import get_logger


@dataclass
class IterationResult:
    """单次迭代结果"""
    translation_text: str
    quality_score: float
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    iteration_number: int = 0
    improvement_prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class IterativeImprover:
    """迭代改进器 - 自动改进不达标的翻译"""
    
    def __init__(
        self,
        translator: BaseTranslator,
        evaluator: BaseEvaluator,
        config: Dict[str, Any] = None
    ):
        self.translator = translator
        self.evaluator = evaluator
        self.config = config or {}
        self.logger = get_logger(__name__)
        
        self.enabled = self.config.get("enabled", True)
        self.quality_threshold = self.config.get("quality_threshold", 85.0)
        self.max_iterations = self.config.get("max_iterations", 3)
        self.track_history = self.config.get("track_history", False)
    
    def improve(
        self,
        original_text: str,
        initial_translation: str,
        source_language: str,
        target_language: str
    ) -> Tuple[str, IterationResult]:
        """改进翻译直到达标或达到最大迭代次数"""
        if not self.enabled:
            eval_request = EvaluationRequest(
                original_text=original_text,
                translated_text=initial_translation,
                source_language=source_language,
                target_language=target_language
            )
            eval_result = self.evaluator.evaluate(eval_request)
            
            return initial_translation, IterationResult(
                translation_text=initial_translation,
                quality_score=eval_result.overall_score,
                issues=eval_result.issues,
                suggestions=eval_result.suggestions,
                iteration_number=0,
                metadata=eval_result.metadata
            )
        
        current_translation = initial_translation
        history: List[IterationResult] = []
        best_result: Optional[IterationResult] = None
        
        for iteration in range(self.max_iterations + 1):
            eval_request = EvaluationRequest(
                original_text=original_text,
                translated_text=current_translation,
                source_language=source_language,
                target_language=target_language
            )
            eval_result = self.evaluator.evaluate(eval_request)
            
            iteration_result = IterationResult(
                translation_text=current_translation,
                quality_score=eval_result.overall_score,
                issues=eval_result.issues,
                suggestions=eval_result.suggestions,
                iteration_number=iteration,
                metadata=eval_result.metadata
            )
            
            if self.track_history:
                history.append(iteration_result)
            
            if best_result is None or eval_result.overall_score > best_result.quality_score:
                best_result = iteration_result
            
            if eval_result.overall_score >= self.quality_threshold:
                self.logger.info(
                    "quality_threshold_met",
                    score=eval_result.overall_score,
                    threshold=self.quality_threshold,
                    iterations=iteration
                )
                return current_translation, iteration_result
            
            if iteration < self.max_iterations:
                improvement_prompt = self._build_improvement_prompt(
                    eval_result, source_language, target_language
                )
                iteration_result.improvement_prompt = improvement_prompt
                
                trans_request = TranslationRequest(
                    text=original_text,
                    source_language=source_language,
                    target_language=target_language,
                    context=improvement_prompt
                )
                trans_result = self.translator.translate(trans_request)
                current_translation = trans_result.text
        
        self.logger.info(
            "max_iterations_reached",
            best_score=best_result.quality_score,
            threshold=self.quality_threshold
        )
        return best_result.translation_text, best_result
    
    def _build_improvement_prompt(
        self,
        eval_result: EvaluationResult,
        source_language: str,
        target_language: str
    ) -> str:
        """构建改进提示词"""
        issues_text = "\n".join(f"- {issue}" for issue in eval_result.issues[:5])
        suggestions_text = "\n".join(f"- {suggestion}" for suggestion in eval_result.suggestions[:5])
        
        return f"""The previous translation had the following quality issues that need to be addressed:

Issues found:
{issues_text}

Improvement suggestions:
{suggestions_text}

Please re-translate the text addressing these issues while maintaining accuracy and natural flow."""
