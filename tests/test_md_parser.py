"""Markdown 解析器测试"""
import pytest
import tempfile
from pathlib import Path
from src.parsers.md_parser import MdParser


def test_md_parser_can_parse():
    """测试 Markdown 解析器支持检查"""
    parser = MdParser()
    assert parser.can_parse("test.md")
    assert parser.can_parse("test.markdown")
    assert not parser.can_parse("test.txt")


def test_md_parser_parse():
    """测试 Markdown 解析器解析"""
    parser = MdParser()
    
    markdown_content = """# Title

This is a paragraph.

## Section

- Item 1
- Item 2

```python
print("Hello")
```
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(markdown_content)
        temp_file = f.name
    
    try:
        result = parser.parse(temp_file)
        assert result.text == markdown_content
        assert result.page_count == 1
        assert result.format_type == "markdown"
        assert result.metadata["heading_count"] == 2
        assert result.metadata["code_block_count"] == 1
    finally:
        Path(temp_file).unlink()


def test_md_parser_frontmatter():
    """测试 YAML frontmatter 检测"""
    parser = MdParser()
    
    markdown_with_frontmatter = """---
title: Test
author: Author
---

# Content

This is content.
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(markdown_with_frontmatter)
        temp_file = f.name
    
    try:
        result = parser.parse(temp_file)
        assert result.metadata["has_frontmatter"] == True
    finally:
        Path(temp_file).unlink()


def test_md_parser_get_page_count():
    """测试获取页数"""
    parser = MdParser()
    assert parser.get_page_count("any.md") == 1
