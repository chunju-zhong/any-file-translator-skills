"""DOCX 解析器测试"""
import pytest
import tempfile
from pathlib import Path
from docx import Document
from src.parsers.docx_parser import DocxParser
from src.utils.exceptions import FileProcessingError

def create_test_docx(content: str, path: str):
    """创建测试用的 DOCX 文件"""
    doc = Document()
    doc.add_paragraph(content)
    doc.save(path)

def test_docx_parser_init():
    """测试 DOCX 解析器初始化"""
    parser = DocxParser()
    assert parser is not None
    assert ".docx" in parser.supported_extensions

def test_docx_parser_can_parse():
    """测试 DOCX 解析器是否支持 DOCX 文件"""
    parser = DocxParser()
    assert parser.can_parse("test.docx")
    assert not parser.can_parse("test.txt")
    assert not parser.can_parse("test.pdf")

def test_docx_parser_nonexistent_file():
    """测试解析不存在的文件"""
    parser = DocxParser()
    with pytest.raises(FileProcessingError):
        parser.parse("nonexistent.docx")

def test_docx_parser_parse():
    """测试解析 DOCX 文件"""
    parser = DocxParser()
    
    # 创建测试 DOCX 文件
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        temp_path = f.name
    
    create_test_docx("Hello, World!\nThis is a test.", temp_path)
    
    try:
        result = parser.parse(temp_path)
        assert "Hello, World!" in result.text
        assert result.page_count == 1
        assert result.format_type == "docx"
    finally:
        Path(temp_path).unlink()