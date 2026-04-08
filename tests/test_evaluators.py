"""评估器测试"""
import pytest
from src.evaluators.base import BaseEvaluator, EvaluationRequest, EvaluationResult


class MockEvaluator(BaseEvaluator):
    """模拟评估器"""
    name = "mock"
    
    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        return EvaluationResult(
            overall_score=85.0,
            fluency_score=90.0,
            accuracy_score=85.0,
            format_score=80.0,
            completeness_score=85.0,
            human_score=85.0,
            issues=[],
            suggestions=[],
            metadata={}
        )
    
    def evaluate_batch(self, requests: list) -> list:
        return [self.evaluate(req) for req in requests]


def test_evaluator_registration():
    """测试评估器注册"""
    from src.evaluators import register_evaluator, get_evaluator, list_evaluators
    
    evaluator = MockEvaluator()
    register_evaluator("mock", evaluator, set_default=True)
    
    assert "mock" in list_evaluators()
    
    retrieved = get_evaluator("mock")
    assert retrieved.name == "mock"
    
    default = get_evaluator()
    assert default.name == "mock"


def test_evaluator_evaluate():
    """测试评估器评估"""
    evaluator = MockEvaluator()
    request = EvaluationRequest(
        original_text="Hello",
        translated_text="你好",
        source_language="en",
        target_language="zh"
    )
    result = evaluator.evaluate(request)
    assert result.overall_score == 85.0
    assert result.fluency_score == 90.0


def test_evaluator_batch_evaluate():
    """测试评估器批量评估"""
    evaluator = MockEvaluator()
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
    assert results[0].overall_score == 85.0
    assert results[1].overall_score == 85.0


def test_generate_suggestions():
    """测试生成改进建议"""
    evaluator = MockEvaluator()
    
    result = EvaluationResult(
        overall_score=50.0,
        fluency_score=60.0,
        accuracy_score=60.0,
        format_score=60.0,
        completeness_score=60.0,
        human_score=60.0,
        issues=[],
        suggestions=[],
        metadata={}
    )
    
    suggestions = evaluator.generate_suggestions(result)
    assert len(suggestions) > 0
