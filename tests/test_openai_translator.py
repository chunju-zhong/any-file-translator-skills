"""OpenAI 翻译器测试"""
import pytest
from unittest.mock import Mock, patch
from src.translators.openai_translator import OpenAITranslator
from src.translators.base import TranslationRequest
from src.utils.exceptions import APIError


def test_openai_translator_translate():
    """测试 OpenAI 翻译器翻译"""
    translator = OpenAITranslator({
        "api_key": "test-key",
        "model": "gpt-4"
    })
    
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "你好"
                }
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }
        mock_post.return_value = mock_response
        
        request = TranslationRequest(
            text="Hello",
            source_language="en",
            target_language="zh"
        )
        
        result = translator.translate(request)
        assert result.text == "你好"
        assert result.source_language == "en"
        assert result.target_language == "zh"
        assert result.model == "gpt-4"


def test_openai_translator_api_error():
    """测试 API 错误处理"""
    translator = OpenAITranslator({
        "api_key": "test-key",
        "model": "gpt-4"
    })
    
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        request = TranslationRequest(text="Hello")
        
        with pytest.raises(APIError):
            translator.translate(request)


def test_openai_translator_batch():
    """测试批量翻译"""
    translator = OpenAITranslator({
        "api_key": "test-key",
        "model": "gpt-4"
    })
    
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "翻译结果"
                }
            }],
            "usage": {
                "total_tokens": 10
            }
        }
        mock_post.return_value = mock_response
        
        requests = [
            TranslationRequest(text="Hello"),
            TranslationRequest(text="World")
        ]
        
        results = translator.translate_batch(requests)
        assert len(results) == 2
        assert results[0].text == "翻译结果"
        assert results[1].text == "翻译结果"
