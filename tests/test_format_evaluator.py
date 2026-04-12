"""格式保持度评估器测试"""
import pytest
from src.evaluators.format_evaluator import FormatEvaluator
from src.evaluators.base import EvaluationRequest


def test_format_evaluator_init():
    """测试格式评估器初始化"""
    evaluator = FormatEvaluator()
    assert evaluator.name == "format"
    assert evaluator.evaluation_dimensions == ["format"]


def test_format_evaluator_evaluate_markdown_headers():
    """测试 Markdown 标题格式评估"""
    evaluator = FormatEvaluator()
    
    original = """# Title 1
## Title 2
### Title 3
"""
    
    translated = """# 标题 1
## 标题 2
### 标题 3
"""
    
    request = EvaluationRequest(
        original_text=original,
        translated_text=translated,
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.format_score > 90
    assert len(result.issues) == 0


def test_format_evaluator_evaluate_markdown_code_blocks():
    """测试 Markdown 代码块格式评估"""
    evaluator = FormatEvaluator()
    
    original = """Here is some code:

```python
def hello():
    print("Hello")
```
"""
    
    translated = """这是一些代码：

```python
def hello():
    print("Hello")
```
"""
    
    request = EvaluationRequest(
        original_text=original,
        translated_text=translated,
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.format_score > 90


def test_format_evaluator_evaluate_markdown_links():
    """测试 Markdown 链接格式评估"""
    evaluator = FormatEvaluator()
    
    original = """Check out [this link](https://example.com) for more info."""
    translated = """查看[此链接](https://example.com)了解更多信息。"""
    
    request = EvaluationRequest(
        original_text=original,
        translated_text=translated,
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.format_score > 90


def test_format_evaluator_evaluate_missing_headers():
    """测试缺失标题的情况"""
    evaluator = FormatEvaluator()
    
    original = """# Title 1
## Title 2
### Title 3
"""
    
    translated = """# 标题 1
## 标题 2
"""
    
    request = EvaluationRequest(
        original_text=original,
        translated_text=translated,
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.format_score < 100
    assert any("标题数量不匹配" in issue for issue in result.issues)


def test_format_evaluator_evaluate_missing_code_blocks():
    """测试缺失代码块的情况"""
    evaluator = FormatEvaluator()
    
    original = """Code:

```python
print("test")
```
"""
    
    translated = """代码：

这里没有代码块
"""
    
    request = EvaluationRequest(
        original_text=original,
        translated_text=translated,
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.format_score < 100
    assert any("代码块数量不匹配" in issue for issue in result.issues)


def test_format_evaluator_evaluate_paragraph_structure():
    """测试段落结构评估"""
    evaluator = FormatEvaluator()
    
    original = """First paragraph.

Second paragraph.

Third paragraph.
"""
    
    translated = """第一段。

第二段。

第三段。
"""
    
    request = EvaluationRequest(
        original_text=original,
        translated_text=translated,
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.format_score > 90


def test_format_evaluator_evaluate_special_characters():
    """测试特殊字符保持"""
    evaluator = FormatEvaluator()
    
    original = """Visit https://example.com or email test@example.com"""
    translated = """访问 https://example.com 或发邮件至 test@example.com"""
    
    request = EvaluationRequest(
        original_text=original,
        translated_text=translated,
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.format_score > 90


def test_format_evaluator_evaluate_numbers():
    """测试数字保持"""
    evaluator = FormatEvaluator()
    
    original = """The year 2024 has 365 days."""
    translated = """2024 年有 365 天。"""
    
    request = EvaluationRequest(
        original_text=original,
        translated_text=translated,
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.format_score > 80


def test_format_evaluator_evaluate_empty_texts():
    """测试空文本"""
    evaluator = FormatEvaluator()
    
    request = EvaluationRequest(
        original_text="",
        translated_text="",
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.format_score >= 0


def test_format_evaluator_evaluate_batch():
    """测试批量评估"""
    evaluator = FormatEvaluator()
    
    requests = [
        EvaluationRequest("# Title", "# 标题", "en", "zh"),
        EvaluationRequest("Paragraph", "段落", "en", "zh")
    ]
    
    results = evaluator.evaluate_batch(requests)
    assert len(results) == 2
    assert all(r.format_score >= 0 for r in results)


def test_format_evaluator_suggestions():
    """测试改进建议生成"""
    evaluator = FormatEvaluator()
    
    original = """# Title"""
    translated = """没有标题"""
    
    request = EvaluationRequest(
        original_text=original,
        translated_text=translated,
        source_language="en",
        target_language="zh"
    )
    
    result = evaluator.evaluate(request)
    assert result.format_score < 70
    assert len(result.suggestions) > 0
    assert any("格式保持度较低" in s for s in result.suggestions)
