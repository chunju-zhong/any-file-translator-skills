"""人味评估器测试"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.evaluators.human_like_evaluator import HumanLikeEvaluator
from src.evaluators.base import EvaluationRequest
from src.utils.exceptions import QualityEvaluationError


def test_human_like_evaluator_init():
    """测试人味评估器初始化"""
    evaluator = HumanLikeEvaluator()
    assert evaluator.name == "human_like"
    assert evaluator.evaluation_dimensions == ["human_like"]


def test_human_like_evaluator_init_with_config():
    """测试带配置的初始化"""
    config = {
        "api_key": "test_key",
        "base_url": "https://test.api.com/v1",
        "model": "gpt-3.5-turbo"
    }
    evaluator = HumanLikeEvaluator(config)
    assert evaluator.api_key == "test_key"
    assert evaluator.base_url == "https://test.api.com/v1"
    assert evaluator.model == "gpt-3.5-turbo"


@patch('src.evaluators.human_like_evaluator.requests.post')
def test_human_like_evaluator_evaluate_success(mock_post):
    """测试人味评估成功"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": '{"human_score": 82.0, "issues": ["Slightly literal translation"], "suggestions": ["Use more idiomatic expressions"]}'
                }
            }
        ]
    }
    mock_post.return_value = mock_response
    
    evaluator = HumanLikeEvaluator({"api_key": "test_key"})
    request = EvaluationRequest(
        original_text="It's raining cats and dogs.",
        translated_text="正在下猫和狗。",
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    
    assert result.human_score == 82.0
    assert result.overall_score == 82.0
    assert len(result.issues) == 1
    assert len(result.suggestions) == 1
    assert result.metadata["evaluation_method"] == "llm_based"


@patch('src.evaluators.human_like_evaluator.requests.post')
def test_human_like_evaluator_evaluate_with_json_block(mock_post):
    """测试包含 JSON 代码块的响应"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": '```json\n{"human_score": 88.0, "issues": [], "suggestions": []}\n```'
                }
            }
        ]
    }
    mock_post.return_value = mock_response
    
    evaluator = HumanLikeEvaluator({"api_key": "test_key"})
    request = EvaluationRequest(
        original_text="How are you?",
        translated_text="你好吗？",
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.human_score == 88.0


@patch('src.evaluators.human_like_evaluator.requests.post')
def test_human_like_evaluator_evaluate_timeout(mock_post):
    """测试 API 超时"""
    import requests
    mock_post.side_effect = requests.exceptions.Timeout()
    
    evaluator = HumanLikeEvaluator({"api_key": "test_key"})
    request = EvaluationRequest(
        original_text="Test",
        translated_text="测试",
        source_language="en",
        target_language="zh"
    )
    
    with pytest.raises(QualityEvaluationError) as exc_info:
        evaluator.evaluate(request)
    assert "timeout" in str(exc_info.value).lower()


@patch('src.evaluators.human_like_evaluator.requests.post')
def test_human_like_evaluator_evaluate_api_error(mock_post):
    """测试 API 错误"""
    mock_response = MagicMock()
    mock_response.status_code = 503
    mock_response.text = "Service Unavailable"
    mock_post.return_value = mock_response
    
    evaluator = HumanLikeEvaluator({"api_key": "test_key"})
    request = EvaluationRequest(
        original_text="Test",
        translated_text="测试",
        source_language="en",
        target_language="zh"
    )
    
    with pytest.raises(QualityEvaluationError) as exc_info:
        evaluator.evaluate(request)
    assert "503" in str(exc_info.value)


@patch('src.evaluators.human_like_evaluator.requests.post')
def test_human_like_evaluator_evaluate_malformed_json(mock_post):
    """测试畸形 JSON 响应"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "Not a valid JSON"
                }
            }
        ]
    }
    mock_post.return_value = mock_response
    
    evaluator = HumanLikeEvaluator({"api_key": "test_key"})
    request = EvaluationRequest(
        original_text="Test",
        translated_text="测试",
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.human_score == 0.0
    assert "Failed to parse" in result.issues[0]


def test_human_like_evaluator_evaluate_batch():
    """测试批量评估"""
    evaluator = HumanLikeEvaluator({"api_key": "test_key"})
    
    with patch.object(evaluator, 'evaluate') as mock_evaluate:
        mock_evaluate.return_value = Mock(human_score=75.0)
        
        requests = [
            EvaluationRequest("A", "a", "en", "zh"),
            EvaluationRequest("B", "b", "en", "zh")
        ]
        
        results = evaluator.evaluate_batch(requests)
        assert len(results) == 2
        assert mock_evaluate.call_count == 2


def test_human_like_evaluator_build_system_prompt():
    """测试系统提示词构建"""
    evaluator = HumanLikeEvaluator()
    request = EvaluationRequest("Test", "测试", "en", "zh")
    
    prompt = evaluator._build_system_prompt(request)
    assert "naturalness" in prompt.lower() or "human" in prompt.lower()
    assert "idiomatic" in prompt.lower()
    assert "MT artifacts" in prompt or "machine translation" in prompt.lower()
    assert "0-100" in prompt


def test_human_like_evaluator_build_user_prompt():
    """测试用户提示词构建"""
    evaluator = HumanLikeEvaluator()
    request = EvaluationRequest(
        original_text="Break a leg!",
        translated_text="断一条腿！",
        source_language="en",
        target_language="zh"
    )
    
    prompt = evaluator._build_user_prompt(request)
    assert "Break a leg!" in prompt
    assert "断一条腿！" in prompt
    assert "en" in prompt
    assert "zh" in prompt
