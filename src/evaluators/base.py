"""基础评估器抽象层"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class EvaluationResult:
    """评估结果"""
    overall_score: float
    fluency_score: float
    accuracy_score: float
    format_score: float
    completeness_score: float
    human_score: float
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationRequest:
    """评估请求"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    context: Optional[str] = None


class BaseEvaluator(ABC):
    """评估器基类"""
    
    name: str = "base"
    evaluation_dimensions: List[str] = ["fluency", "accuracy", "format", "completeness", "human"]
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = None
    
    @abstractmethod
    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        """评估翻译质量"""
        pass
    
    @abstractmethod
    def evaluate_batch(self, requests: List[EvaluationRequest]) -> List[EvaluationResult]:
        """批量评估"""
        pass
    
    def get_dimension_score(self, dimension: str, request: EvaluationRequest) -> float:
        """获取单个维度的分数（可选实现）"""
        return 0.0
    
    def generate_suggestions(self, result: EvaluationResult) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if result.fluency_score < 70:
            suggestions.append("翻译流畅度较低，建议检查语句通顺度")
        if result.accuracy_score < 70:
            suggestions.append("翻译准确性较低，建议检查专业术语翻译")
        if result.format_score < 70:
            suggestions.append("格式保持度较低，建议检查原文格式是否丢失")
        if result.completeness_score < 70:
            suggestions.append("翻译完整性较低，建议检查是否有遗漏内容")
        if result.human_score < 70:
            suggestions.append("人味评分较低，建议使翻译更加自然")
        
        return suggestions
