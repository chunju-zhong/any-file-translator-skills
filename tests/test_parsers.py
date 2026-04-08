"""解析器测试"""
import pytest
from src.parsers.base import BaseParser, ParseResult, Chapter
from src.utils.exceptions import UnsupportedFormatError


class MockParser(BaseParser):
    """模拟解析器"""
    supported_extensions = [".txt"]
    
    def parse(self, file_path: str) -> ParseResult:
        return ParseResult(
            text="test content",
            page_count=1,
            metadata={},
            format_type="txt"
        )
    
    def get_page_count(self, file_path: str) -> int:
        return 1


def test_parser_can_parse():
    """测试解析器支持检查"""
    parser = MockParser()
    assert parser.can_parse("test.txt")
    assert not parser.can_parse("test.pdf")


def test_parser_parse():
    """测试解析器解析"""
    parser = MockParser()
    result = parser.parse("test.txt")
    assert result.text == "test content"
    assert result.page_count == 1
    assert result.format_type == "txt"


def test_parser_get_page_count():
    """测试解析器获取页数"""
    parser = MockParser()
    page_count = parser.get_page_count("test.txt")
    assert page_count == 1


def test_parser_registration():
    """测试解析器注册"""
    from src.parsers import register_parser, get_parser, list_supported_formats
    
    parser = MockParser()
    register_parser([".txt"], parser)
    
    assert ".txt" in list_supported_formats()
