"""Google Translate 翻译器测试"""
import pytest
from unittest.mock import Mock, patch
from src.translators.google_translator import GoogleTranslator
from src.translators.base import TranslationRequest
from src.utils.exceptions import APIError


def test_google_translator_init():
    """测试 Google 翻译器初始化"""
    translator = GoogleTranslator({
        "api_key": "test-key"
    })
    
    assert translator.name == "google"
    assert translator.api_key == "test-key"
    assert translator.supported_languages == []


def test_google_translator_translate():
    """测试 Google 翻译"""
    translator = GoogleTranslator({
        "api_key": "test-key"
    })
    
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "translations": [
                    {
                        "translatedText": "你好",
                        "detectedSourceLanguage": "en"
                    }
                ]
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
        assert result.model == "google"


def test_google_translator_api_error():
    """测试 Google API 错误"""
    translator = GoogleTranslator({
        "api_key": "invalid-key"
    })
    
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Invalid API key"
        mock_post.return_value = mock_response
        
        request = TranslationRequest(
            text="Hello",
            target_language="zh"
        )
        
        with pytest.raises(APIError) as exc_info:
            translator.translate(request)
        
        assert "403" in str(exc_info.value)


def test_google_translator_batch():
    """测试 Google 批量翻译"""
    translator = GoogleTranslator({
        "api_key": "test-key"
    })
    
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "translations": [
                    {"translatedText": "你好", "detectedSourceLanguage": "en"},
                    {"translatedText": "世界", "detectedSourceLanguage": "en"}
                ]
            }
        }
        mock_post.return_value = mock_response
        
        requests = [
            TranslationRequest(text="Hello", source_language="en", target_language="zh"),
            TranslationRequest(text="World", source_language="en", target_language="zh")
        ]
        
        results = translator.translate_batch(requests)
        
        assert len(results) == 2
        assert results[0].text == "你好"
        assert results[1].text == "世界"


def test_google_translator_auto_detect():
    """测试 Google 自动检测语言"""
    translator = GoogleTranslator({
        "api_key": "test-key"
    })
    
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "translations": [
                    {
                        "translatedText": "你好",
                        "detectedSourceLanguage": "en"
                    }
                ]
            }
        }
        mock_post.return_value = mock_response
        
        request = TranslationRequest(
            text="Hello",
            source_language="auto",
            target_language="zh"
        )
        
        result = translator.translate(request)
        
        assert result.text == "你好"
        assert result.source_language == "en"


def test_google_translator_quota_exceeded():
    """测试 Google 配额超限"""
    translator = GoogleTranslator({"api_key": "test-key"})
    
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Quota exceeded"
        mock_post.return_value = mock_response
        
        request = TranslationRequest(
            text="Hello",
            target_language="zh"
        )
        
        with pytest.raises(APIError) as exc_info:
            translator.translate(request)
        
        assert "quota" in str(exc_info.value).lower()


def test_google_translator_timeout():
    """测试 Google 超时"""
    import requests
    translator = GoogleTranslator({
        "api_key": "test-key",
        "timeout": 30
    })
    
    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.Timeout()
        
        request = TranslationRequest(
            text="Hello",
            target_language="zh"
        )
        
        with pytest.raises(APIError) as exc_info:
            translator.translate(request)
        
        assert "timeout" in str(exc_info.value).lower()
