"""翻译器测试"""
import pytest
from src.translators.base import BaseTranslator, TranslationRequest, TranslationResult


class MockTranslator(BaseTranslator):
    """模拟翻译器"""
    name = "mock"
    supported_languages = ["en", "zh"]
    
    def translate(self, request: TranslationRequest) -> TranslationResult:
        return TranslationResult(
            text=f"translated: {request.text}",
            source_language=request.source_language,
            target_language=request.target_language,
            model="mock-model",
            usage={"prompt_tokens": 10, "completion_tokens": 10},
            metadata={}
        )
    
    def translate_batch(self, requests: list) -> list:
        return [self.translate(req) for req in requests]


def test_translator_supports_language():
    """测试翻译器语言支持检查"""
    translator = MockTranslator()
    assert translator.supports_language("en")
    assert translator.supports_language("zh")
    assert not translator.supports_language("fr")


def test_translator_translate():
    """测试翻译器翻译"""
    translator = MockTranslator()
    request = TranslationRequest(
        text="Hello",
        source_language="en",
        target_language="zh"
    )
    result = translator.translate(request)
    assert result.text == "translated: Hello"
    assert result.source_language == "en"
    assert result.target_language == "zh"


def test_translator_batch_translate():
    """测试翻译器批量翻译"""
    translator = MockTranslator()
    requests = [
        TranslationRequest(text="Hello", source_language="en", target_language="zh"),
        TranslationRequest(text="World", source_language="en", target_language="zh")
    ]
    results = translator.translate_batch(requests)
    assert len(results) == 2
    assert results[0].text == "translated: Hello"
    assert results[1].text == "translated: World"


def test_translator_registration():
    """测试翻译器注册"""
    from src.translators import register_translator, get_translator, list_translators
    
    translator = MockTranslator()
    register_translator("mock", translator, set_default=True)
    
    assert "mock" in list_translators()
    
    retrieved = get_translator("mock")
    assert retrieved.name == "mock"
    
    default = get_translator()
    assert default.name == "mock"
