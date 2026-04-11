"""准确性评估器测试"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.evaluators.accuracy_evaluator import AccuracyEvaluator
from src.evaluators.base import EvaluationRequest
from src.utils.exceptions import QualityEvaluationError


def test_accuracy_evaluator_init():
    """测试准确性评估器初始化"""
    evaluator = AccuracyEvaluator()
    assert evaluator.name == "accuracy"
    assert evaluator.evaluation_dimensions == ["accuracy"]


def test_accuracy_evaluator_init_with_config():
    """测试带配置的初始化"""
    config = {
        "api_key": "test_key",
        "base_url": "https://test.api.com/v1",
        "model": "gpt-3.5-turbo"
    }
    evaluator = AccuracyEvaluator(config)
    assert evaluator.api_key == "test_key"
    assert evaluator.base_url == "https://test.api.com/v1"
    assert evaluator.model == "gpt-3.5-turbo"


@patch('src.evaluators.accuracy_evaluator.requests.post')
def test_accuracy_evaluator_evaluate_success(mock_post):
    """测试准确性评估成功"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": '{"accuracy_score": 88.0, "issues": ["Minor terminology issue"], "suggestions": ["Check technical terms"]}'
                }
            }
        ]
    }
    mock_post.return_value = mock_response
    
    evaluator = AccuracyEvaluator({"api_key": "test_key"})
    request = EvaluationRequest(
        original_text="Machine Learning",
        translated_text="机器学习",
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    
    assert result.accuracy_score == 88.0
    assert result.overall_score == 88.0
    assert len(result.issues) == 1
    assert len(result.suggestions) == 1
    assert result.metadata["evaluation_method"] == "llm_based"


@patch('src.evaluators.accuracy_evaluator.requests.post')
def test_accuracy_evaluator_evaluate_with_json_block(mock_post):
    """测试包含 JSON 代码块的响应"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": '```json\n{"accuracy_score": 95.0, "issues": [], "suggestions": []}\n```'
                }
            }
        ]
    }
    mock_post.return_value = mock_response
    
    evaluator = AccuracyEvaluator({"api_key": "test_key"})
    request = EvaluationRequest(
        original_text="API",
        translated_text="API",
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.accuracy_score == 95.0


@patch('src.evaluators.accuracy_evaluator.requests.post')
def test_accuracy_evaluator_evaluate_timeout(mock_post):
    """测试 API 超时"""
    import requests
    mock_post.side_effect = requests.exceptions.Timeout()
    
    evaluator = AccuracyEvaluator({"api_key": "test_key"})
    request = EvaluationRequest(
        original_text="Test",
        translated_text="测试",
        source_language="en",
        target_language="zh"
    )
    
    with pytest.raises(QualityEvaluationError) as exc_info:
        evaluator.evaluate(request)
    assert "timeout" in str(exc_info.value).lower()


@patch('src.evaluators.accuracy_evaluator.requests.post')
def test_accuracy_evaluator_evaluate_api_error(mock_post):
    """测试 API 错误"""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_post.return_value = mock_response
    
    evaluator = AccuracyEvaluator({"api_key": "test_key"})
    request = EvaluationRequest(
        original_text="Test",
        translated_text="测试",
        source_language="en",
        target_language="zh"
    )
    
    with pytest.raises(QualityEvaluationError) as exc_info:
        evaluator.evaluate(request)
    assert "401" in str(exc_info.value)


@patch('src.evaluators.accuracy_evaluator.requests.post')
def test_accuracy_evaluator_evaluate_malformed_json(mock_post):
    """测试畸形 JSON 响应"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "Invalid JSON response"
                }
            }
        ]
    }
    mock_post.return_value = mock_response
    
    evaluator = AccuracyEvaluator({"api_key": "test_key"})
    request = EvaluationRequest(
        original_text="Test",
        translated_text="测试",
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.accuracy_score == 0.0
    assert "Failed to parse" in result.issues[0]


def test_accuracy_evaluator_evaluate_batch():
    """测试批量评估"""
    evaluator = AccuracyEvaluator({"api_key": "test_key"})
    
    with patch.object(evaluator, 'evaluate') as mock_evaluate:
        mock_evaluate.return_value = Mock(accuracy_score=85.0)
        
        requests = [
            EvaluationRequest("A", "a", "en", "zh"),
            EvaluationRequest("B", "b", "en", "zh")
        ]
        
        results = evaluator.evaluate_batch(requests)
        assert len(results) == 2
        assert mock_evaluate.call_count == 2


def test_accuracy_evaluator_build_system_prompt():
    """测试系统提示词构建"""
    evaluator = AccuracyEvaluator()
    request = EvaluationRequest("Test", "测试", "en", "zh")
    
    prompt = evaluator._build_system_prompt(request)
    assert "accuracy" in prompt.lower()
    assert "meaning preservation" in prompt.lower()
    assert "terminology" in prompt.lower()
    assert "0-100" in prompt


def test_accuracy_evaluator_build_user_prompt():
    """测试用户提示词构建"""
    evaluator = AccuracyEvaluator()
    request = EvaluationRequest(
        original_text="Hello World",
        translated_text="你好世界",
        source_language="en",
        target_language="zh"
    )
    
    prompt = evaluator._build_user_prompt(request)
    assert "Hello World" in prompt
    assert "你好世界" in prompt
    assert "en" in prompt
    assert "zh" in prompt
