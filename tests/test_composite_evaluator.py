"""组合评估器测试"""
import pytest
from unittest.mock import Mock, patch
from src.evaluators.composite_evaluator import CompositeEvaluator
from src.evaluators.base import EvaluationRequest, EvaluationResult


def test_composite_evaluator_init():
    """测试组合评估器初始化"""
    evaluator = CompositeEvaluator()
    assert evaluator.name == "composite"
    assert len(evaluator.evaluation_dimensions) == 5
    assert "fluency" in evaluator.evaluation_dimensions
    assert "accuracy" in evaluator.evaluation_dimensions
    assert "format" in evaluator.evaluation_dimensions
    assert "completeness" in evaluator.evaluation_dimensions
    assert "human_like" in evaluator.evaluation_dimensions


def test_composite_evaluator_weights():
    """测试权重配置"""
    evaluator = CompositeEvaluator()
    
    assert evaluator.WEIGHTS["fluency"] == 0.30
    assert evaluator.WEIGHTS["accuracy"] == 0.25
    assert evaluator.WEIGHTS["format"] == 0.20
    assert evaluator.WEIGHTS["completeness"] == 0.15
    assert evaluator.WEIGHTS["human_like"] == 0.10
    
    total_weight = sum(evaluator.WEIGHTS.values())
    assert abs(total_weight - 1.0) < 0.001


@patch('src.evaluators.fluency_evaluator.FluencyEvaluator.evaluate')
@patch('src.evaluators.accuracy_evaluator.AccuracyEvaluator.evaluate')
@patch('src.evaluators.format_evaluator.FormatEvaluator.evaluate')
@patch('src.evaluators.completeness_evaluator.CompletenessEvaluator.evaluate')
@patch('src.evaluators.human_like_evaluator.HumanLikeEvaluator.evaluate')
def test_composite_evaluator_evaluate(
    mock_human, mock_completeness, mock_format, mock_accuracy, mock_fluency
):
    """测试组合评估"""
    mock_fluency.return_value = EvaluationResult(
        overall_score=90.0,
        fluency_score=90.0,
        accuracy_score=0.0,
        format_score=0.0,
        completeness_score=0.0,
        human_score=0.0,
        issues=["Fluency issue"],
        suggestions=["Fluency suggestion"],
        metadata={}
    )
    
    mock_accuracy.return_value = EvaluationResult(
        overall_score=85.0,
        fluency_score=0.0,
        accuracy_score=85.0,
        format_score=0.0,
        completeness_score=0.0,
        human_score=0.0,
        issues=["Accuracy issue"],
        suggestions=["Accuracy suggestion"],
        metadata={}
    )
    
    mock_format.return_value = EvaluationResult(
        overall_score=88.0,
        fluency_score=0.0,
        accuracy_score=0.0,
        format_score=88.0,
        completeness_score=0.0,
        human_score=0.0,
        issues=["Format issue"],
        suggestions=["Format suggestion"],
        metadata={}
    )
    
    mock_completeness.return_value = EvaluationResult(
        overall_score=92.0,
        fluency_score=0.0,
        accuracy_score=0.0,
        format_score=0.0,
        completeness_score=92.0,
        human_score=0.0,
        issues=["Completeness issue"],
        suggestions=["Completeness suggestion"],
        metadata={}
    )
    
    mock_human.return_value = EvaluationResult(
        overall_score=80.0,
        fluency_score=0.0,
        accuracy_score=0.0,
        format_score=0.0,
        completeness_score=0.0,
        human_score=80.0,
        issues=["Human issue"],
        suggestions=["Human suggestion"],
        metadata={}
    )
    
    evaluator = CompositeEvaluator()
    request = EvaluationRequest(
        original_text="Hello World",
        translated_text="你好世界",
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    
    assert result.overall_score > 0
    assert result.fluency_score == 90.0
    assert result.accuracy_score == 85.0
    assert result.format_score == 88.0
    assert result.completeness_score == 92.0
    assert result.human_score == 80.0
    
    assert len(result.issues) == 5
    assert len(result.suggestions) >= 5
    
    assert "weights" in result.metadata


def test_composite_evaluator_calculate_weighted_score():
    """测试加权分数计算"""
    evaluator = CompositeEvaluator()
    
    score = evaluator._calculate_weighted_score(
        fluency=90.0,
        accuracy=80.0,
        format_score=85.0,
        completeness=95.0,
        human=75.0
    )
    
    expected = (
        90.0 * 0.30 +
        80.0 * 0.25 +
        85.0 * 0.20 +
        95.0 * 0.15 +
        75.0 * 0.10
    )
    
    assert abs(score - expected) < 0.01


def test_composite_evaluator_calculate_weighted_score_bounds():
    """测试加权分数边界"""
    evaluator = CompositeEvaluator()
    
    score = evaluator._calculate_weighted_score(
        fluency=100.0,
        accuracy=100.0,
        format_score=100.0,
        completeness=100.0,
        human=100.0
    )
    assert score == 100.0
    
    score = evaluator._calculate_weighted_score(
        fluency=0.0,
        accuracy=0.0,
        format_score=0.0,
        completeness=0.0,
        human=0.0
    )
    assert score == 0.0


def test_composite_evaluator_evaluate_batch():
    """测试批量评估"""
    evaluator = CompositeEvaluator()
    
    with patch.object(evaluator, 'evaluate') as mock_evaluate:
        mock_evaluate.return_value = Mock(overall_score=85.0)
        
        requests = [
            EvaluationRequest("A", "a", "en", "zh"),
            EvaluationRequest("B", "b", "en", "zh")
        ]
        
        results = evaluator.evaluate_batch(requests)
        assert len(results) == 2
        assert mock_evaluate.call_count == 2


@patch('src.evaluators.fluency_evaluator.FluencyEvaluator.evaluate')
@patch('src.evaluators.accuracy_evaluator.AccuracyEvaluator.evaluate')
@patch('src.evaluators.format_evaluator.FormatEvaluator.evaluate')
@patch('src.evaluators.completeness_evaluator.CompletenessEvaluator.evaluate')
@patch('src.evaluators.human_like_evaluator.HumanLikeEvaluator.evaluate')
def test_composite_evaluator_aggregates_issues_and_suggestions(
    mock_human, mock_completeness, mock_format, mock_accuracy, mock_fluency
):
    """测试问题和建议的聚合"""
    mock_fluency.return_value = EvaluationResult(
        overall_score=90.0,
        fluency_score=90.0,
        accuracy_score=0.0,
        format_score=0.0,
        completeness_score=0.0,
        human_score=0.0,
        issues=["Issue 1"],
        suggestions=["Suggestion 1"],
        metadata={}
    )
    
    mock_accuracy.return_value = EvaluationResult(
        overall_score=85.0,
        fluency_score=0.0,
        accuracy_score=85.0,
        format_score=0.0,
        completeness_score=0.0,
        human_score=0.0,
        issues=["Issue 2"],
        suggestions=["Suggestion 2"],
        metadata={}
    )
    
    mock_format.return_value = EvaluationResult(
        overall_score=88.0,
        fluency_score=0.0,
        accuracy_score=0.0,
        format_score=88.0,
        completeness_score=0.0,
        human_score=0.0,
        issues=["Issue 3"],
        suggestions=["Suggestion 3"],
        metadata={}
    )
    
    mock_completeness.return_value = EvaluationResult(
        overall_score=92.0,
        fluency_score=0.0,
        accuracy_score=0.0,
        format_score=0.0,
        completeness_score=92.0,
        human_score=0.0,
        issues=["Issue 4"],
        suggestions=["Suggestion 4"],
        metadata={}
    )
    
    mock_human.return_value = EvaluationResult(
        overall_score=80.0,
        fluency_score=0.0,
        accuracy_score=0.0,
        format_score=0.0,
        completeness_score=0.0,
        human_score=80.0,
        issues=["Issue 5"],
        suggestions=["Suggestion 5"],
        metadata={}
    )
    
    evaluator = CompositeEvaluator()
    request = EvaluationRequest("Test", "测试", "en", "zh")
    
    result = evaluator.evaluate(request)
    
    assert "Issue 1" in result.issues
    assert "Issue 2" in result.issues
    assert "Issue 3" in result.issues
    assert "Issue 4" in result.issues
    assert "Issue 5" in result.issues
    
    assert "Suggestion 1" in result.suggestions
    assert "Suggestion 2" in result.suggestions
    assert "Suggestion 3" in result.suggestions
    assert "Suggestion 4" in result.suggestions
    assert "Suggestion 5" in result.suggestions
