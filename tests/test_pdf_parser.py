"""PDF 解析器测试"""
import pytest
import tempfile
from pathlib import Path
from src.parsers.pdf_parser import PdfParser
from src.utils.exceptions import FileProcessingError


def test_pdf_parser_init():
    """测试 PDF 解析器初始化"""
    parser = PdfParser()
    assert parser is not None
    assert ".pdf" in parser.supported_extensions


def test_pdf_parser_can_parse():
    """测试 PDF 解析器是否支持 PDF 文件"""
    parser = PdfParser()
    assert parser.can_parse("test.pdf")
    assert not parser.can_parse("test.txt")
    assert not parser.can_parse("test.md")


def test_pdf_parser_nonexistent_file():
    """测试解析不存在的文件"""
    parser = PdfParser()
    with pytest.raises(FileProcessingError):
        parser.parse("nonexistent.pdf")


def test_pdf_parser_invalid_format():
    """测试解析无效的 PDF 文件"""
    parser = PdfParser()
    # 创建一个非 PDF 文件
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"not a pdf")
        temp_path = f.name
    
    try:
        with pytest.raises(FileProcessingError):
            parser.parse(temp_path)
    finally:
        Path(temp_path).unlink()