"""格式保持度评估器"""
import re
from typing import Dict, Any, List
from src.evaluators.base import BaseEvaluator, EvaluationRequest, EvaluationResult
from src.utils.logger import get_logger


class FormatEvaluator(BaseEvaluator):
    """格式保持度评估器 - 使用规则检查格式保持度"""
    
    name = "format"
    evaluation_dimensions = ["format"]
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = get_logger(__name__)
    
    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        """评估格式保持度"""
        format_score = self._calculate_format_score(
            request.original_text,
            request.translated_text
        )
        
        issues = self._detect_format_issues(
            request.original_text,
            request.translated_text
        )
        
        suggestions = []
        if format_score < 70:
            suggestions.append("格式保持度较低，建议检查原文格式是否丢失")
        
        self.logger.info(
            "format_evaluation_completed",
            score=format_score,
            issues_count=len(issues)
        )
        
        return EvaluationResult(
            overall_score=format_score,
            fluency_score=0.0,
            accuracy_score=0.0,
            format_score=format_score,
            completeness_score=0.0,
            human_score=0.0,
            issues=issues,
            suggestions=suggestions,
            metadata={
                "evaluation_method": "rule_based"
            }
        )
    
    def evaluate_batch(self, requests: List[EvaluationRequest]) -> List[EvaluationResult]:
        """批量评估"""
        return [self.evaluate(req) for req in requests]
    
    def _calculate_format_score(self, original: str, translated: str) -> float:
        """计算格式保持度分数"""
        scores = []
        
        markdown_score = self._check_markdown_format(original, translated)
        scores.append(markdown_score)
        
        paragraph_score = self._check_paragraph_structure(original, translated)
        scores.append(paragraph_score)
        
        special_chars_score = self._check_special_characters(original, translated)
        scores.append(special_chars_score)
        
        if scores:
            return sum(scores) / len(scores)
        return 100.0
    
    def _check_markdown_format(self, original: str, translated: str) -> float:
        """检查 Markdown 格式保持度"""
        checks = []
        
        original_headers = len(re.findall(r'^#{1,6}\s+', original, re.MULTILINE))
        translated_headers = len(re.findall(r'^#{1,6}\s+', translated, re.MULTILINE))
        if original_headers > 0:
            header_ratio = min(translated_headers / original_headers, 1.0)
            checks.append(header_ratio * 100)
        
        original_code_blocks = len(re.findall(r'```', original))
        translated_code_blocks = len(re.findall(r'```', translated))
        if original_code_blocks > 0:
            code_ratio = min(translated_code_blocks / original_code_blocks, 1.0)
            checks.append(code_ratio * 100)
        
        original_links = len(re.findall(r'\[.*?\]\(.*?\)', original))
        translated_links = len(re.findall(r'\[.*?\]\(.*?\)', translated))
        if original_links > 0:
            link_ratio = min(translated_links / original_links, 1.0)
            checks.append(link_ratio * 100)
        
        original_lists = len(re.findall(r'^\s*[-*+]\s+', original, re.MULTILINE))
        translated_lists = len(re.findall(r'^\s*[-*+]\s+', translated, re.MULTILINE))
        if original_lists > 0:
            list_ratio = min(translated_lists / original_lists, 1.0)
            checks.append(list_ratio * 100)
        
        if checks:
            return sum(checks) / len(checks)
        return 100.0
    
    def _check_paragraph_structure(self, original: str, translated: str) -> float:
        """检查段落结构保持度"""
        original_paragraphs = [p for p in original.split('\n\n') if p.strip()]
        translated_paragraphs = [p for p in translated.split('\n\n') if p.strip()]
        
        if len(original_paragraphs) == 0:
            return 100.0
        
        paragraph_ratio = len(translated_paragraphs) / len(original_paragraphs)
        
        if paragraph_ratio >= 0.9 and paragraph_ratio <= 1.1:
            return 100.0
        elif paragraph_ratio >= 0.8 and paragraph_ratio <= 1.2:
            return 80.0
        else:
            return max(0, 60.0 - abs(1.0 - paragraph_ratio) * 50)
    
    def _check_special_characters(self, original: str, translated: str) -> float:
        """检查特殊字符保持度"""
        checks = []
        
        original_numbers = len(re.findall(r'\d+', original))
        translated_numbers = len(re.findall(r'\d+', translated))
        if original_numbers > 0:
            number_ratio = min(translated_numbers / original_numbers, 1.0)
            checks.append(number_ratio * 100)
        
        original_urls = len(re.findall(r'https?://[^\s]+', original))
        translated_urls = len(re.findall(r'https?://[^\s]+', translated))
        if original_urls > 0:
            url_ratio = min(translated_urls / original_urls, 1.0)
            checks.append(url_ratio * 100)
        
        original_emails = len(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', original))
        translated_emails = len(re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', translated))
        if original_emails > 0:
            email_ratio = min(translated_emails / original_emails, 1.0)
            checks.append(email_ratio * 100)
        
        if checks:
            return sum(checks) / len(checks)
        return 100.0
    
    def _detect_format_issues(self, original: str, translated: str) -> List[str]:
        """检测格式问题"""
        issues = []
        
        original_headers = len(re.findall(r'^#{1,6}\s+', original, re.MULTILINE))
        translated_headers = len(re.findall(r'^#{1,6}\s+', translated, re.MULTILINE))
        if original_headers > 0 and abs(original_headers - translated_headers) > 0:
            issues.append(f"标题数量不匹配（原文: {original_headers}, 译文: {translated_headers}）")
        
        original_code_blocks = len(re.findall(r'```', original))
        translated_code_blocks = len(re.findall(r'```', translated))
        if original_code_blocks > 0 and abs(original_code_blocks - translated_code_blocks) > 0:
            issues.append(f"代码块数量不匹配（原文: {original_code_blocks}, 译文: {translated_code_blocks}）")
        
        original_links = len(re.findall(r'\[.*?\]\(.*?\)', original))
        translated_links = len(re.findall(r'\[.*?\]\(.*?\)', translated))
        if original_links > 0 and abs(original_links - translated_links) > 0:
            issues.append(f"链接数量不匹配（原文: {original_links}, 译文: {translated_links}）")
        
        original_urls = len(re.findall(r'https?://[^\s]+', original))
        translated_urls = len(re.findall(r'https?://[^\s]+', translated))
        if original_urls > 0 and abs(original_urls - translated_urls) > 0:
            issues.append(f"URL 数量不匹配（原文: {original_urls}, 译文: {translated_urls}）")
        
        return issues
