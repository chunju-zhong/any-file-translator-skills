"""迭代改进器测试"""
import pytest
from unittest.mock import Mock, patch
from src.improver import IterativeImprover, ImprovementResult
from src.evaluators.base import EvaluationResult


def test_improver_initialization():
    """测试改进器初始化"""
    config = {
        "quality_threshold": 85.0,
        "max_iterations": 3,
        "improvement_delay": 0.1,
        "enable_improvement": True
    }
    
    improver = IterativeImprover(config)
    
    assert improver.quality_threshold == 85.0
    assert improver.max_iterations == 3
    assert improver.improvement_delay == 0.1
    assert improver.enable_improvement == True


def test_no_improvement_needed():
    """测试不需要改进的情况"""
    improver = IterativeImprover({
        "quality_threshold": 85.0,
        "max_iterations": 3,
        "enable_improvement": True
    })
    
    mock_translator = Mock()
    evaluation_result = EvaluationResult(
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
    
    result = improver.improve_translation(
        "Hello",
        "你好",
        evaluation_result,
        mock_translator,
        "en",
        "zh"
    )
    
    assert result.success == True
    assert result.iterations == 0
    assert result.final_text == "你好"
    assert result.final_score == 90.0


def test_improvement_disabled():
    """测试改进功能被禁用"""
    improver = IterativeImprover({
        "quality_threshold": 85.0,
        "max_iterations": 3,
        "enable_improvement": False
    })
    
    mock_translator = Mock()
    evaluation_result = EvaluationResult(
        overall_score=70.0,
        fluency_score=70.0,
        accuracy_score=70.0,
        format_score=70.0,
        completeness_score=70.0,
        human_score=70.0,
        issues=["Test issue"],
        suggestions=["Test suggestion"],
        metadata={}
    )
    
    result = improver.improve_translation(
        "Hello",
        "你好",
        evaluation_result,
        mock_translator,
        "en",
        "zh"
    )
    
    assert result.success == True
    assert result.iterations == 0
    assert result.final_text == "你好"
    assert result.final_score == 70.0
    assert result.metadata["improvement_disabled"] == True


def test_single_iteration_success():
    """测试单次迭代成功"""
    improver = IterativeImprover({
        "quality_threshold": 85.0,
        "max_iterations": 3,
        "improvement_delay": 0.0,
        "enable_improvement": True
    })
    
    mock_translator = Mock()
    mock_translator.translate.return_value = Mock(
        text="你好，世界",
        model="gpt-4",
        usage={"total_tokens": 20}
    )
    
    with patch('src.evaluators.get_evaluator') as mock_get_evaluator:
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
        mock_get_evaluator.return_value = mock_evaluator
        
        evaluation_result = EvaluationResult(
            overall_score=70.0,
            fluency_score=70.0,
            accuracy_score=70.0,
            format_score=70.0,
            completeness_score=70.0,
            human_score=70.0,
            issues=["Low fluency"],
            suggestions=["Improve fluency"],
            metadata={}
        )
        
        result = improver.improve_translation(
            "Hello, World",
            "你好",
            evaluation_result,
            mock_translator,
            "en",
            "zh"
        )
        
        assert result.success == True
        assert result.iterations == 1
        assert result.final_text == "你好，世界"
        assert result.final_score == 90.0
        assert len(result.improvement_history) == 1


def test_multiple_iterations():
    """测试多次迭代"""
    improver = IterativeImprover({
        "quality_threshold": 85.0,
        "max_iterations": 3,
        "improvement_delay": 0.0,
        "enable_improvement": True
    })
    
    mock_translator = Mock()
    
    with patch('src.evaluators.get_evaluator') as mock_get_evaluator:
        mock_evaluator = Mock()
        
        call_count = [0]
        
        def mock_evaluate(request):
            call_count[0] += 1
            if call_count[0] == 1:
                return EvaluationResult(
                    overall_score=75.0,
                    fluency_score=75.0,
                    accuracy_score=75.0,
                    format_score=75.0,
                    completeness_score=75.0,
                    human_score=75.0,
                    issues=["Still needs improvement"],
                    suggestions=["Continue improving"],
                    metadata={}
                )
            elif call_count[0] == 2:
                return EvaluationResult(
                    overall_score=88.0,
                    fluency_score=88.0,
                    accuracy_score=88.0,
                    format_score=88.0,
                    completeness_score=88.0,
                    human_score=88.0,
                    issues=[],
                    suggestions=[],
                    metadata={}
                )
            return EvaluationResult(
                overall_score=70.0,
                fluency_score=70.0,
                accuracy_score=70.0,
                format_score=70.0,
                completeness_score=70.0,
                human_score=70.0,
                issues=["Initial"],
                suggestions=["Initial"],
                metadata={}
            )
        
        mock_evaluator.evaluate.side_effect = mock_evaluate
        mock_get_evaluator.return_value = mock_evaluator
        
        mock_translator.translate.return_value = Mock(
            text="Improved translation",
            model="gpt-4",
            usage={"total_tokens": 25}
        )
        
        evaluation_result = EvaluationResult(
            overall_score=60.0,
            fluency_score=60.0,
            accuracy_score=60.0,
            format_score=60.0,
            completeness_score=60.0,
            human_score=60.0,
            issues=["Very low quality"],
            suggestions=["Major improvement needed"],
            metadata={}
        )
        
        result = improver.improve_translation(
            "Original text",
            "Initial translation",
            evaluation_result,
            mock_translator,
            "en",
            "zh"
        )
        
        assert result.success == True
        assert result.iterations == 2
        assert result.final_score == 88.0
        assert len(result.improvement_history) == 2


def test_max_iterations_reached():
    """测试达到最大迭代次数"""
    improver = IterativeImprover({
        "quality_threshold": 85.0,
        "max_iterations": 3,
        "improvement_delay": 0.0,
        "enable_improvement": True
    })
    
    mock_translator = Mock()
    
    with patch('src.evaluators.get_evaluator') as mock_get_evaluator:
        mock_evaluator = Mock()
        mock_evaluator.evaluate.return_value = EvaluationResult(
            overall_score=80.0,
            fluency_score=80.0,
            accuracy_score=80.0,
            format_score=80.0,
            completeness_score=80.0,
            human_score=80.0,
            issues=["Still not good enough"],
            suggestions=["Keep trying"],
            metadata={}
        )
        mock_get_evaluator.return_value = mock_evaluator
        
        mock_translator.translate.return_value = Mock(
            text="Best effort translation",
            model="gpt-4",
            usage={"total_tokens": 30}
        )
        
        evaluation_result = EvaluationResult(
            overall_score=60.0,
            fluency_score=60.0,
            accuracy_score=60.0,
            format_score=60.0,
            completeness_score=60.0,
            human_score=60.0,
            issues=["Poor quality"],
            suggestions=["Needs work"],
            metadata={}
        )
        
        result = improver.improve_translation(
            "Original",
            "Bad translation",
            evaluation_result,
            mock_translator,
            "en",
            "zh"
        )
        
        assert result.success == False
        assert result.iterations == 3
        assert result.final_score == 80.0
        assert len(result.improvement_history) == 3


def test_build_improvement_prompt():
    """测试构建改进提示词"""
    improver = IterativeImprover()
    
    prompt = improver._build_improvement_prompt(
        "Hello",
        "你好",
        ["Issue 1", "Issue 2"],
        ["Suggestion 1", "Suggestion 2"]
    )
    
    assert "Hello" in prompt
    assert "你好" in prompt
    assert "Issue 1" in prompt
    assert "Issue 2" in prompt
    assert "Suggestion 1" in prompt
    assert "Suggestion 2" in prompt
    assert "improved translation" in prompt.lower()


def test_track_improvement():
    """测试跟踪改进进度"""
    improver = IterativeImprover()
    
    track = improver._track_improvement(
        1,
        85.0,
        ["Issue 1", "Issue 2"]
    )
    
    assert track["iteration"] == 1
    assert track["score"] == 85.0
    assert track["issues_count"] == 2
    assert len(track["issues"]) == 2


def test_exception_handling():
    """测试异常处理"""
    improver = IterativeImprover({
        "quality_threshold": 85.0,
        "max_iterations": 3,
        "enable_improvement": True
    })
    
    mock_translator = Mock()
    mock_translator.translate.side_effect = Exception("API Error")
    
    evaluation_result = EvaluationResult(
        overall_score=70.0,
        fluency_score=70.0,
        accuracy_score=70.0,
        format_score=70.0,
        completeness_score=70.0,
        human_score=70.0,
        issues=["Test issue"],
        suggestions=["Test suggestion"],
        metadata={}
    )
    
    result = improver.improve_translation(
        "Hello",
        "你好",
        evaluation_result,
        mock_translator,
        "en",
        "zh"
    )
    
    assert result.success == False
    assert result.iterations == 1
    assert result.final_score == 70.0
    assert len(result.improvement_history) == 1
    assert "error" in result.improvement_history[0]
