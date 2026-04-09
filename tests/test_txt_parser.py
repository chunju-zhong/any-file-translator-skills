"""TXT 解析器测试"""
import pytest
import tempfile
from pathlib import Path
from src.parsers.txt_parser import TxtParser
from src.utils.exceptions import FileProcessingError


def test_txt_parser_can_parse():
    """测试 TXT 解析器支持检查"""
    parser = TxtParser()
    assert parser.can_parse("test.txt")
    assert not parser.can_parse("test.pdf")


def test_txt_parser_parse():
    """测试 TXT 解析器解析"""
    parser = TxtParser()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("Hello, World!")
        temp_file = f.name
    
    try:
        result = parser.parse(temp_file)
        assert result.text == "Hello, World!"
        assert result.page_count == 1
        assert result.format_type == "txt"
        assert "file_size" in result.metadata
    finally:
        Path(temp_file).unlink()


def test_txt_parser_file_not_found():
    """测试文件不存在错误"""
    parser = TxtParser()
    
    with pytest.raises(FileProcessingError):
        parser.parse("nonexistent.txt")


def test_txt_parser_get_page_count():
    """测试获取页数"""
    parser = TxtParser()
    assert parser.get_page_count("any.txt") == 1
