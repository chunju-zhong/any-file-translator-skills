"""迭代改进器测试"""
import pytest
from unittest.mock import Mock, patch
from src.improvers.iterative_improver import IterativeImprover, IterationResult
from src.evaluators.base import EvaluationResult, EvaluationRequest
from src.translators.base import TranslationResult, TranslationRequest


def test_iterative_improver_init():
    """测试迭代改进器初始化"""
    mock_translator = Mock()
    mock_evaluator = Mock()
    
    improver = IterativeImprover(mock_translator, mock_evaluator)
    
    assert improver.enabled == True
    assert improver.quality_threshold == 85.0
    assert improver.max_iterations == 3


def test_iterative_improver_custom_config():
    """测试自定义配置"""
    mock_translator = Mock()
    mock_evaluator = Mock()
    
    config = {
        "enabled": False,
        "quality_threshold": 90.0,
        "max_iterations": 5
    }
    
    improver = IterativeImprover(mock_translator, mock_evaluator, config)
    
    assert improver.enabled == False
    assert improver.quality_threshold == 90.0
    assert improver.max_iterations == 5


def test_iterative_improver_no_improvement_needed():
    """测试质量达标时不需要改进"""
    mock_translator = Mock()
    mock_evaluator = Mock()
    mock_evaluator.evaluate.return_value = EvaluationResult(
        overall_score=90.0,
        fluency_score=90.0,
        accuracy_score=90.0,
        format_score=90.0,
        completeness_score=90.0,
        human_score=90.0,
        issues=[],
        suggestions=[],
        metadata={}
    )
    
    improver = IterativeImprover(mock_translator, mock_evaluator)
    text, result = improver.improve("Hello", "你好", "en", "zh")
    
    assert result.quality_score == 90.0
    assert result.iteration_number == 0
    mock_translator.translate.assert_not_called()


def test_iterative_improver_improves_quality():
    """测试质量改进"""
    mock_translator = Mock()
    mock_evaluator = Mock()
    
    mock_evaluator.evaluate.side_effect = [
        EvaluationResult(
            overall_score=70.0,
            fluency_score=70.0,
            accuracy_score=70.0,
            format_score=70.0,
            completeness_score=70.0,
            human_score=70.0,
            issues=["Issue 1"],
            suggestions=["Suggestion 1"],
            metadata={}
        ),
        EvaluationResult(
            overall_score=90.0,
            fluency_score=90.0,
            accuracy_score=90.0,
            format_score=90.0,
            completeness_score=90.0,
            human_score=90.0,
            issues=[],
            suggestions=[],
            metadata={}
        )
    ]
    
    mock_translator.translate.return_value = TranslationResult(
        text="改进后的翻译",
        source_language="en",
        target_language="zh",
        model="gpt-4",
        usage={},
        metadata={}
    )
    
    improver = IterativeImprover(mock_translator, mock_evaluator)
    text, result = improver.improve("Hello", "你好", "en", "zh")
    
    assert result.quality_score == 90.0
    assert result.iteration_number == 1
    mock_translator.translate.assert_called_once()


def test_iterative_improver_max_iterations():
    """测试最大迭代次数限制"""
    mock_translator = Mock()
    mock_evaluator = Mock()
    
    mock_evaluator.evaluate.side_effect = [
        EvaluationResult(
            overall_score=70.0,
            fluency_score=70.0,
            accuracy_score=70.0,
            format_score=70.0,
            completeness_score=70.0,
            human_score=70.0,
            issues=["Issue"],
            suggestions=["Suggestion"],
            metadata={}
        )
    ]
    
    improver = IterativeImprover(mock_translator, mock_evaluator, {"max_iterations": 2, "enabled": False})
    text, result = improver.improve("Hello", "你好", "en", "zh")
    
    assert result.quality_score == 70.0
    assert mock_translator.translate.call_count == 0


def test_iterative_improver_returns_best_result():
    """测试返回最佳结果"""
    mock_translator = Mock()
    mock_evaluator = Mock()
    
    mock_evaluator.evaluate.side_effect = [
        EvaluationResult(
            overall_score=70.0,
            fluency_score=70.0,
            accuracy_score=70.0,
            format_score=70.0,
            completeness_score=70.0,
            human_score=70.0,
            issues=[],
            suggestions=[],
            metadata={}
        ),
        EvaluationResult(
            overall_score=60.0,
            fluency_score=60.0,
            accuracy_score=60.0,
            format_score=60.0,
            completeness_score=60.0,
            human_score=60.0,
            issues=[],
            suggestions=[],
            metadata={}
        ),
        EvaluationResult(
            overall_score=75.0,
            fluency_score=75.0,
            accuracy_score=75.0,
            format_score=75.0,
            completeness_score=75.0,
            human_score=75.0,
            issues=[],
            suggestions=[],
            metadata={}
        ),
    ]
    
    mock_translator.translate.return_value = TranslationResult(
        text="翻译",
        source_language="en",
        target_language="zh",
        model="gpt-4",
        usage={},
        metadata={}
    )
    
    improver = IterativeImprover(mock_translator, mock_evaluator, {"max_iterations": 2})
    text, result = improver.improve("Hello", "你好", "en", "zh")
    
    assert result.quality_score == 75.0


def test_iterative_improver_disabled():
    """测试禁用迭代改进"""
    mock_translator = Mock()
    mock_evaluator = Mock()
    mock_evaluator.evaluate.return_value = EvaluationResult(
        overall_score=70.0,
        fluency_score=70.0,
        accuracy_score=70.0,
        format_score=70.0,
        completeness_score=70.0,
        human_score=70.0,
        issues=["Issue"],
        suggestions=["Suggestion"],
        metadata={}
    )
    
    improver = IterativeImprover(
        mock_translator,
        mock_evaluator,
        {"enabled": False, "max_iterations": 2}
    )
    text, result = improver.improve("Hello", "你好", "en", "zh")
    
    assert result.quality_score == 70.0
    assert result.iteration_number == 0
    mock_translator.translate.assert_not_called()


def test_iteration_result_dataclass():
    """测试 IterationResult 数据类"""
    result = IterationResult(
        translation_text="测试翻译",
        quality_score=85.0,
        issues=["问题1", "问题2"],
        suggestions=["建议1"],
        iteration_number=1,
        improvement_prompt="改进提示",
        metadata={"key": "value"}
    )
    
    assert result.translation_text == "测试翻译"
    assert result.quality_score == 85.0
    assert len(result.issues) == 2
    assert len(result.suggestions) == 1
    assert result.iteration_number == 1
    assert result.improvement_prompt == "改进提示"
    assert result.metadata["key"] == "value"


def test_build_improvement_prompt():
    """测试构建改进提示词"""
    mock_translator = Mock()
    mock_evaluator = Mock()
    
    improver = IterativeImprover(mock_translator, mock_evaluator)
    
    eval_result = EvaluationResult(
        overall_score=70.0,
        fluency_score=70.0,
        accuracy_score=70.0,
        format_score=70.0,
        completeness_score=70.0,
        human_score=70.0,
        issues=["流畅度问题", "准确性问题"],
        suggestions=["改进流畅度", "改进准确性"],
        metadata={}
    )
    
    prompt = improver._build_improvement_prompt(eval_result, "en", "zh")
    
    assert "Issues found:" in prompt
    assert "Improvement suggestions:" in prompt
    assert "- 流畅度问题" in prompt
    assert "- 改进流畅度" in prompt
