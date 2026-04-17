"""翻译器选择器测试"""
import pytest
from unittest.mock import Mock, patch
from src.translators.selector import TranslatorSelector, TranslatorInfo, SelectionResult
from src.translators.base import BaseTranslator, TranslationRequest, TranslationResult
from src.utils.exceptions import APIError, ConfigurationError


class MockTranslator(BaseTranslator):
    """模拟翻译器"""
    
    def __init__(self, name, config=None, should_fail=False):
        super().__init__(config)
        self._name = name
        self.should_fail = should_fail
        self.translate_count = 0
    
    @property
    def name(self):
        return self._name
    
    def translate(self, request):
        self.translate_count += 1
        if self.should_fail:
            raise APIError(f"{self._name} failed", status_code=500)
        return TranslationResult(
            text=f"translated by {self._name}",
            source_language=request.source_language,
            target_language=request.target_language,
            model=self._name,
            usage={},
            metadata={}
        )
    
    def translate_batch(self, requests):
        return [self.translate(req) for req in requests]


def test_translator_selector_init():
    """测试选择器初始化"""
    selector = TranslatorSelector()
    
    assert selector is not None
    assert "openai" in selector.translators


def test_translator_selector_with_priorities():
    """测试带优先级的选择器"""
    priorities = {"openai": 1, "deepl": 2, "google": 3}
    selector = TranslatorSelector(priorities=priorities)
    
    assert selector.priorities == priorities


def test_translator_selector_select_translator():
    """测试选择翻译器"""
    selector = TranslatorSelector()
    
    selected = selector.select_translator(target_language="zh")
    
    assert selected is not None
    assert selected.name == "openai"


def test_translator_selector_translate_with_fallback():
    """测试带回退的翻译"""
    selector = TranslatorSelector()
    
    mock_translator = MockTranslator("mock1")
    selector.add_translator("mock1", mock_translator, priority=1)
    
    request = TranslationRequest(
        text="Hello",
        source_language="en",
        target_language="zh"
    )
    
    result = selector.translate_with_fallback(request)
    
    assert result.translator_name == "mock1"
    assert result.result.text == "translated by mock1"
    assert result.fallback_used == False


def test_translator_selector_fallback_on_error():
    """测试错误时回退"""
    selector = TranslatorSelector()
    
    failing_translator = MockTranslator("failing", should_fail=True)
    working_translator = MockTranslator("working", should_fail=False)
    
    selector.add_translator("failing", failing_translator, priority=1)
    selector.add_translator("working", working_translator, priority=2)
    
    request = TranslationRequest(
        text="Hello",
        source_language="en",
        target_language="zh"
    )
    
    result = selector.translate_with_fallback(request)
    
    assert result.translator_name == "working"
    assert result.fallback_used == True
    assert "failing" in result.attempted_translators


def test_translator_selector_rate_limit_tracking():
    """测试速率限制跟踪"""
    selector = TranslatorSelector()
    
    rate_limited_translator = MockTranslator("rate_limited", should_fail=True)
    selector.add_translator("rate_limited", rate_limited_translator, priority=1)
    
    request = TranslationRequest(text="Hello", target_language="zh")
    
    with patch.object(rate_limited_translator, 'translate') as mock_translate:
        mock_translate.side_effect = APIError("Rate limited", status_code=429)
        
        with pytest.raises(APIError):
            selector.translate_with_fallback(request)
    
    assert selector.translators["rate_limited"].rate_limited == True


def test_translator_selector_reset_rate_limits():
    """测试重置速率限制"""
    selector = TranslatorSelector()
    
    mock_translator = MockTranslator("test")
    selector.add_translator("test", mock_translator)
    selector.translators["test"].rate_limited = True
    
    selector.reset_rate_limits()
    
    assert selector.translators["test"].rate_limited == False


def test_translator_selector_get_status():
    """测试获取状态"""
    selector = TranslatorSelector()
    
    status = selector.get_translator_status()
    
    assert "openai" in status
    assert "priority" in status["openai"]
    assert "rate_limited" in status["openai"]


def test_translator_selector_set_priority():
    """测试设置优先级"""
    selector = TranslatorSelector()
    
    mock_translator = MockTranslator("test")
    selector.add_translator("test", mock_translator, priority=5)
    
    selector.set_priority("test", 1)
    
    assert selector.translators["test"].priority == 1


def test_translator_selector_add_translator():
    """测试添加翻译器"""
    selector = TranslatorSelector()
    
    mock_translator = MockTranslator("new_translator")
    selector.add_translator("new_translator", mock_translator, priority=1)
    
    assert "new_translator" in selector.translators
    assert selector.translators["new_translator"].priority == 1


def test_translator_selector_remove_translator():
    """测试移除翻译器"""
    selector = TranslatorSelector()
    
    mock_translator = MockTranslator("to_remove")
    selector.add_translator("to_remove", mock_translator)
    
    selector.remove_translator("to_remove")
    
    assert "to_remove" not in selector.translators


def test_translator_selector_batch_with_fallback():
    """测试批量翻译带回退"""
    selector = TranslatorSelector()
    
    mock_translator = MockTranslator("batch_mock")
    selector.add_translator("batch_mock", mock_translator, priority=1)
    
    requests = [
        TranslationRequest(text="Hello", target_language="zh"),
        TranslationRequest(text="World", target_language="zh")
    ]
    
    results = selector.translate_batch_with_fallback(requests)
    
    assert len(results) == 2
    assert all(r.translator_name == "batch_mock" for r in results)


def test_translator_selector_no_translators_available():
    """测试无可用翻译器"""
    selector = TranslatorSelector()
    selector.translators = {}
    
    request = TranslationRequest(text="Hello", target_language="zh")
    
    with pytest.raises(ConfigurationError):
        selector.translate_with_fallback(request)


def test_translator_selector_all_translators_fail():
    """测试所有翻译器都失败"""
    selector = TranslatorSelector()
    
    failing1 = MockTranslator("fail1", should_fail=True)
    failing2 = MockTranslator("fail2", should_fail=True)
    
    selector.add_translator("fail1", failing1, priority=1)
    selector.add_translator("fail2", failing2, priority=2)
    
    request = TranslationRequest(text="Hello", target_language="zh")
    
    with pytest.raises(APIError) as exc_info:
        selector.translate_with_fallback(request)
    
    assert "All translators failed" in str(exc_info.value)


def test_translator_info_dataclass():
    """测试 TranslatorInfo 数据类"""
    mock_translator = MockTranslator("test")
    info = TranslatorInfo(
        name="test",
        translator=mock_translator,
        priority=1
    )
    
    assert info.name == "test"
    assert info.priority == 1
    assert info.rate_limited == False
    assert info.error_count == 0


def test_selection_result_dataclass():
    """测试 SelectionResult 数据类"""
    mock_translator = MockTranslator("test")
    result = TranslationResult(
        text="translated",
        source_language="en",
        target_language="zh",
        model="test",
        usage={},
        metadata={}
    )
    
    selection = SelectionResult(
        translator_name="test",
        result=result,
        fallback_used=False,
        attempted_translators=["test"]
    )
    
    assert selection.translator_name == "test"
    assert selection.fallback_used == False
    assert selection.attempted_translators == ["test"]
