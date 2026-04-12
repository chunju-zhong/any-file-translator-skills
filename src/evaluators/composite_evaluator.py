"""组合评估器"""
from typing import Dict, Any, List
from src.evaluators.base import BaseEvaluator, EvaluationRequest, EvaluationResult
from src.evaluators.fluency_evaluator import FluencyEvaluator
from src.evaluators.accuracy_evaluator import AccuracyEvaluator
from src.evaluators.format_evaluator import FormatEvaluator
from src.evaluators.completeness_evaluator import CompletenessEvaluator
from src.evaluators.human_like_evaluator import HumanLikeEvaluator
from src.utils.logger import get_logger


class CompositeEvaluator(BaseEvaluator):
    """组合评估器 - 整合所有维度的评估器"""
    
    name = "composite"
    evaluation_dimensions = ["fluency", "accuracy", "format", "completeness", "human_like"]
    
    WEIGHTS = {
        "fluency": 0.30,
        "accuracy": 0.25,
        "format": 0.20,
        "completeness": 0.15,
        "human_like": 0.10
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        self.fluency_evaluator = FluencyEvaluator(config)
        self.accuracy_evaluator = AccuracyEvaluator(config)
        self.format_evaluator = FormatEvaluator(config)
        self.completeness_evaluator = CompletenessEvaluator(config)
        self.human_like_evaluator = HumanLikeEvaluator(config)
    
    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        """综合评估翻译质量"""
        self.logger.info(
            "composite_evaluation_started",
            source_lang=request.source_language,
            target_lang=request.target_language
        )
        
        fluency_result = self.fluency_evaluator.evaluate(request)
        accuracy_result = self.accuracy_evaluator.evaluate(request)
        format_result = self.format_evaluator.evaluate(request)
        completeness_result = self.completeness_evaluator.evaluate(request)
        human_like_result = self.human_like_evaluator.evaluate(request)
        
        overall_score = self._calculate_weighted_score(
            fluency_result.fluency_score,
            accuracy_result.accuracy_score,
            format_result.format_score,
            completeness_result.completeness_score,
            human_like_result.human_score
        )
        
        all_issues = []
        all_issues.extend(fluency_result.issues)
        all_issues.extend(accuracy_result.issues)
        all_issues.extend(format_result.issues)
        all_issues.extend(completeness_result.issues)
        all_issues.extend(human_like_result.issues)
        
        all_suggestions = []
        all_suggestions.extend(fluency_result.suggestions)
        all_suggestions.extend(accuracy_result.suggestions)
        all_suggestions.extend(format_result.suggestions)
        all_suggestions.extend(completeness_result.suggestions)
        all_suggestions.extend(human_like_result.suggestions)
        
        all_suggestions.extend(self.generate_suggestions(EvaluationResult(
            overall_score=overall_score,
            fluency_score=fluency_result.fluency_score,
            accuracy_score=accuracy_result.accuracy_score,
            format_score=format_result.format_score,
            completeness_score=completeness_result.completeness_score,
            human_score=human_like_result.human_score,
            issues=[],
            suggestions=[]
        )))
        
        self.logger.info(
            "composite_evaluation_completed",
            overall_score=overall_score,
            fluency=fluency_result.fluency_score,
            accuracy=accuracy_result.accuracy_score,
            format=format_result.format_score,
            completeness=completeness_result.completeness_score,
            human=human_like_result.human_score
        )
        
        return EvaluationResult(
            overall_score=overall_score,
            fluency_score=fluency_result.fluency_score,
            accuracy_score=accuracy_result.accuracy_score,
            format_score=format_result.format_score,
            completeness_score=completeness_result.completeness_score,
            human_score=human_like_result.human_score,
            issues=all_issues,
            suggestions=all_suggestions,
            metadata={
                "evaluation_method": "composite",
                "weights": self.WEIGHTS,
                "fluency_metadata": fluency_result.metadata,
                "accuracy_metadata": accuracy_result.metadata,
                "format_metadata": format_result.metadata,
                "completeness_metadata": completeness_result.metadata,
                "human_like_metadata": human_like_result.metadata
            }
        )
    
    def evaluate_batch(self, requests: List[EvaluationRequest]) -> List[EvaluationResult]:
        """批量评估"""
        return [self.evaluate(req) for req in requests]
    
    def _calculate_weighted_score(
        self,
        fluency: float,
        accuracy: float,
        format_score: float,
        completeness: float,
        human: float
    ) -> float:
        """计算加权总分"""
        weighted_sum = (
            fluency * self.WEIGHTS["fluency"] +
            accuracy * self.WEIGHTS["accuracy"] +
            format_score * self.WEIGHTS["format"] +
            completeness * self.WEIGHTS["completeness"] +
            human * self.WEIGHTS["human_like"]
        )
        
        return min(max(weighted_sum, 0), 100)
