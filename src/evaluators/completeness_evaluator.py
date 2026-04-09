"""完整性评估器"""
from src.evaluators.base import BaseEvaluator, EvaluationRequest, EvaluationResult
from src.utils.logger import get_logger


class CompletenessEvaluator(BaseEvaluator):
    """完整性评估器"""
    
    name = "completeness"
    evaluation_dimensions = ["completeness"]
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.logger = get_logger(__name__)
    
    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        """评估翻译完整性"""
        completeness_score = self._calculate_completeness(
            request.original_text,
            request.translated_text
        )
        
        issues = self._detect_issues(
            request.original_text,
            request.translated_text
        )
        
        suggestions = []
        if completeness_score < 70:
            suggestions.append("翻译完整性较低，可能存在遗漏内容")
        
        self.logger.info(
            "completeness_evaluation_completed",
            score=completeness_score,
            issues_count=len(issues)
        )
        
        return EvaluationResult(
            overall_score=completeness_score,
            fluency_score=0.0,
            accuracy_score=0.0,
            format_score=0.0,
            completeness_score=completeness_score,
            human_score=0.0,
            issues=issues,
            suggestions=suggestions,
            metadata={
                "original_length": len(request.original_text),
                "translated_length": len(request.translated_text),
                "length_ratio": len(request.translated_text) / max(len(request.original_text), 1)
            }
        )
    
    def evaluate_batch(self, requests: list) -> list:
        """批量评估"""
        return [self.evaluate(req) for req in requests]
    
    def _calculate_completeness(self, original: str, translated: str) -> float:
        """计算完整性分数"""
        length_ratio = len(translated) / max(len(original), 1)
        
        original_paragraphs = len([p for p in original.split('\n\n') if p.strip()])
        translated_paragraphs = len([p for p in translated.split('\n\n') if p.strip()])
        paragraph_ratio = translated_paragraphs / max(original_paragraphs, 1)
        
        original_sentences = len([s for s in original.split('。') if s.strip()])
        translated_sentences = len([s for s in translated.split('。') if s.strip()])
        sentence_ratio = translated_sentences / max(original_sentences, 1)
        
        score = (length_ratio * 0.4 + paragraph_ratio * 0.3 + sentence_ratio * 0.3) * 100
        
        return min(max(score, 0), 100)
    
    def _detect_issues(self, original: str, translated: str) -> list:
        """检测完整性问题"""
        issues = []
        
        length_ratio = len(translated) / max(len(original), 1)
        if length_ratio < 0.5:
            issues.append(f"翻译文本过短（长度比例: {length_ratio:.2f}）")
        elif length_ratio > 2.0:
            issues.append(f"翻译文本过长（长度比例: {length_ratio:.2f}）")
        
        original_paragraphs = len([p for p in original.split('\n\n') if p.strip()])
        translated_paragraphs = len([p for p in translated.split('\n\n') if p.strip()])
        if abs(original_paragraphs - translated_paragraphs) > 1:
            issues.append(f"段落数量不匹配（原文: {original_paragraphs}, 译文: {translated_paragraphs}）")
        
        if not translated.strip():
            issues.append("翻译文本为空")
        
        return issues
