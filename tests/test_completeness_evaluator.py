"""完整性评估器测试"""
import pytest
from src.evaluators.completeness_evaluator import CompletenessEvaluator
from src.evaluators.base import EvaluationRequest


def test_completeness_evaluator_evaluate():
    """测试完整性评估器评估"""
    evaluator = CompletenessEvaluator()
    
    request = EvaluationRequest(
        original_text="Hello, World!",
        translated_text="你好，世界！",
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.completeness_score > 0
    assert result.overall_score == result.completeness_score
    assert isinstance(result.issues, list)
    assert isinstance(result.suggestions, list)


def test_completeness_evaluator_empty_translation():
    """测试空翻译"""
    evaluator = CompletenessEvaluator()
    
    request = EvaluationRequest(
        original_text="Hello, World!",
        translated_text="",
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.completeness_score < 50
    assert "翻译文本为空" in result.issues


def test_completeness_evaluator_short_translation():
    """测试过短翻译"""
    evaluator = CompletenessEvaluator()
    
    request = EvaluationRequest(
        original_text="This is a long paragraph with multiple sentences. It has lots of content.",
        translated_text="短",
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.completeness_score < 70
    assert any("过短" in issue for issue in result.issues)


def test_completeness_evaluator_batch():
    """测试批量评估"""
    evaluator = CompletenessEvaluator()
    
    requests = [
        EvaluationRequest(
            original_text="Hello",
            translated_text="你好",
            source_language="en",
            target_language="zh"
        ),
        EvaluationRequest(
            original_text="World",
            translated_text="世界",
            source_language="en",
            target_language="zh"
        )
    ]
    
    results = evaluator.evaluate_batch(requests)
    assert len(results) == 2
    assert all(r.completeness_score > 0 for r in results)
