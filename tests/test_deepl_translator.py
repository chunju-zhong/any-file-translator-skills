"""DeepL 翻译器测试"""
import pytest
from unittest.mock import Mock, patch
from src.translators.deepl_translator import DeepLTranslator
from src.translators.base import TranslationRequest
from src.utils.exceptions import APIError


def test_deepl_translator_init():
    """测试 DeepL 翻译器初始化"""
    translator = DeepLTranslator({
        "api_key": "test-key",
        "formality": "more"
    })
    
    assert translator.name == "deepl"
    assert translator.api_key == "test-key"
    assert translator.formality == "more"
    assert len(translator.supported_languages) > 0


def test_deepl_translator_translate():
    """测试 DeepL 翻译"""
    translator = DeepLTranslator({
        "api_key": "test-key"
    })
    
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "translations": [
                {
                    "text": "你好",
                    "detected_source_language": "EN"
                }
            ]
        }
        mock_post.return_value = mock_response
        
        request = TranslationRequest(
            text="Hello",
            source_language="en",
            target_language="zh"
        )
        
        result = translator.translate(request)
        
        assert result.text == "你好"
        assert result.source_language == "EN"
        assert result.target_language == "zh"
        assert result.model == "deepl"


def test_deepl_translator_api_error():
    """测试 DeepL API 错误"""
    translator = DeepLTranslator({
        "api_key": "invalid-key"
    })
    
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Invalid API key"
        mock_post.return_value = mock_response
        
        request = TranslationRequest(
            text="Hello",
            source_language="en",
            target_language="zh"
        )
        
        with pytest.raises(APIError) as exc_info:
            translator.translate(request)
        
        assert "403" in str(exc_info.value)


def test_deepl_translator_batch():
    """测试 DeepL 批量翻译"""
    translator = DeepLTranslator({
        "api_key": "test-key"
    })
    
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "translations": [
                {"text": "你好", "detected_source_language": "EN"},
                {"text": "世界", "detected_source_language": "EN"}
            ]
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


def test_deepl_translator_formality():
    """测试 DeepL formality 参数"""
    translator = DeepLTranslator({
        "api_key": "test-key",
        "formality": "more"
    })
    
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "translations": [
                {"text": "Sie", "detected_source_language": "EN"}
            ]
        }
        mock_post.return_value = mock_response
        
        request = TranslationRequest(
            text="You",
            source_language="en",
            target_language="de"
        )
        
        result = translator.translate(request)
        
        assert result.text == "Sie"
        call_args = mock_post.call_args
        assert "formality" in call_args[1]["data"]


def test_deepl_translator_language_mapping():
    """测试 DeepL 语言映射"""
    translator = DeepLTranslator({"api_key": "test-key"})
    
    assert translator._map_language("zh") == "ZH"
    assert translator._map_language("en-us") == "EN-US"
    assert translator._map_language("pt-br") == "PT-BR"


def test_deepl_translator_quota_exceeded():
    """测试 DeepL 配额超限"""
    translator = DeepLTranslator({"api_key": "test-key"})
    
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 456
        mock_response.text = "Quota exceeded"
        mock_post.return_value = mock_response
        
        request = TranslationRequest(
            text="Hello",
            target_language="zh"
        )
        
        with pytest.raises(APIError) as exc_info:
            translator.translate(request)
        
        assert "quota" in str(exc_info.value).lower()
