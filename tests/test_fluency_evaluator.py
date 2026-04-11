"""流畅度评估器测试"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.evaluators.fluency_evaluator import FluencyEvaluator
from src.evaluators.base import EvaluationRequest
from src.utils.exceptions import QualityEvaluationError


def test_fluency_evaluator_init():
    """测试流畅度评估器初始化"""
    evaluator = FluencyEvaluator()
    assert evaluator.name == "fluency"
    assert evaluator.evaluation_dimensions == ["fluency"]


def test_fluency_evaluator_init_with_config():
    """测试带配置的初始化"""
    config = {
        "api_key": "test_key",
        "base_url": "https://test.api.com/v1",
        "model": "gpt-3.5-turbo"
    }
    evaluator = FluencyEvaluator(config)
    assert evaluator.api_key == "test_key"
    assert evaluator.base_url == "https://test.api.com/v1"
    assert evaluator.model == "gpt-3.5-turbo"


@patch('src.evaluators.fluency_evaluator.requests.post')
def test_fluency_evaluator_evaluate_success(mock_post):
    """测试流畅度评估成功"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": '{"fluency_score": 85.0, "issues": ["Minor grammar issue"], "suggestions": ["Improve sentence structure"]}'
                }
            }
        ]
    }
    mock_post.return_value = mock_response
    
    evaluator = FluencyEvaluator({"api_key": "test_key"})
    request = EvaluationRequest(
        original_text="Hello, World!",
        translated_text="你好，世界！",
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    
    assert result.fluency_score == 85.0
    assert result.overall_score == 85.0
    assert len(result.issues) == 1
    assert len(result.suggestions) == 1
    assert result.metadata["evaluation_method"] == "llm_based"


@patch('src.evaluators.fluency_evaluator.requests.post')
def test_fluency_evaluator_evaluate_with_json_block(mock_post):
    """测试包含 JSON 代码块的响应"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": '```json\n{"fluency_score": 90.0, "issues": [], "suggestions": []}\n```'
                }
            }
        ]
    }
    mock_post.return_value = mock_response
    
    evaluator = FluencyEvaluator({"api_key": "test_key"})
    request = EvaluationRequest(
        original_text="Test",
        translated_text="测试",
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.fluency_score == 90.0


@patch('src.evaluators.fluency_evaluator.requests.post')
def test_fluency_evaluator_evaluate_timeout(mock_post):
    """测试 API 超时"""
    import requests
    mock_post.side_effect = requests.exceptions.Timeout()
    
    evaluator = FluencyEvaluator({"api_key": "test_key"})
    request = EvaluationRequest(
        original_text="Test",
        translated_text="测试",
        source_language="en",
        target_language="zh"
    )
    
    with pytest.raises(QualityEvaluationError) as exc_info:
        evaluator.evaluate(request)
    assert "timeout" in str(exc_info.value).lower()


@patch('src.evaluators.fluency_evaluator.requests.post')
def test_fluency_evaluator_evaluate_api_error(mock_post):
    """测试 API 错误"""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_post.return_value = mock_response
    
    evaluator = FluencyEvaluator({"api_key": "test_key"})
    request = EvaluationRequest(
        original_text="Test",
        translated_text="测试",
        source_language="en",
        target_language="zh"
    )
    
    with pytest.raises(QualityEvaluationError) as exc_info:
        evaluator.evaluate(request)
    assert "500" in str(exc_info.value)


@patch('src.evaluators.fluency_evaluator.requests.post')
def test_fluency_evaluator_evaluate_malformed_json(mock_post):
    """测试畸形 JSON 响应"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "This is not valid JSON"
                }
            }
        ]
    }
    mock_post.return_value = mock_response
    
    evaluator = FluencyEvaluator({"api_key": "test_key"})
    request = EvaluationRequest(
        original_text="Test",
        translated_text="测试",
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.fluency_score == 0.0
    assert "Failed to parse" in result.issues[0]


def test_fluency_evaluator_evaluate_batch():
    """测试批量评估"""
    evaluator = FluencyEvaluator({"api_key": "test_key"})
    
    with patch.object(evaluator, 'evaluate') as mock_evaluate:
        mock_evaluate.return_value = Mock(fluency_score=80.0)
        
        requests = [
            EvaluationRequest("A", "a", "en", "zh"),
            EvaluationRequest("B", "b", "en", "zh")
        ]
        
        results = evaluator.evaluate_batch(requests)
        assert len(results) == 2
        assert mock_evaluate.call_count == 2


def test_fluency_evaluator_build_system_prompt():
    """测试系统提示词构建"""
    evaluator = FluencyEvaluator()
    request = EvaluationRequest("Test", "测试", "en", "zh")
    
    prompt = evaluator._build_system_prompt(request)
    assert "fluency" in prompt.lower()
    assert "0-100" in prompt
    assert "JSON" in prompt


def test_fluency_evaluator_build_user_prompt():
    """测试用户提示词构建"""
    evaluator = FluencyEvaluator()
    request = EvaluationRequest(
        original_text="Hello",
        translated_text="你好",
        source_language="en",
        target_language="zh"
    )
    
    prompt = evaluator._build_user_prompt(request)
    assert "Hello" in prompt
    assert "你好" in prompt
    assert "en" in prompt
    assert "zh" in prompt
