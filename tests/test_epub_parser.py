"""EPUB 解析器测试"""
import pytest
import tempfile
from pathlib import Path
import ebooklib
from ebooklib import epub
from src.parsers.epub_parser import EpubParser
from src.utils.exceptions import FileProcessingError

def create_test_epub(content: str, path: str):
    """创建测试用的 EPUB 文件"""
    book = epub.EpubBook()
    book.set_title('Test Book')
    book.set_language('en')
    book.add_author('Test Author')
    
    # 创建章节
    chapter = epub.EpubHtml(title='Chapter 1', file_name='chapter1.xhtml', lang='en')
    chapter.content = f'<html><body><p>{content}</p></body></html>'
    
    # 添加章节
    book.add_item(chapter)
    book.toc = [epub.Link('chapter1.xhtml', 'Chapter 1', 'chapter1')]
    book.spine = ['nav', chapter]
    
    # 添加导航
    book.add_item(epub.EpubNav())
    book.add_item(epub.EpubNcx())
    
    # 保存 EPUB
    epub.write_epub(path, book, {})

def test_epub_parser_init():
    """测试 EPUB 解析器初始化"""
    parser = EpubParser()
    assert parser is not None
    assert ".epub" in parser.supported_extensions

def test_epub_parser_can_parse():
    """测试 EPUB 解析器是否支持 EPUB 文件"""
    parser = EpubParser()
    assert parser.can_parse("test.epub")
    assert not parser.can_parse("test.txt")
    assert not parser.can_parse("test.pdf")

def test_epub_parser_nonexistent_file():
    """测试解析不存在的文件"""
    parser = EpubParser()
    with pytest.raises(FileProcessingError):
        parser.parse("nonexistent.epub")

def test_epub_parser_parse():
    """测试解析 EPUB 文件"""
    parser = EpubParser()
    
    # 创建测试 EPUB 文件
    with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
        temp_path = f.name
    
    create_test_epub("Hello, EPUB World!\nThis is a test.", temp_path)
    
    try:
        result = parser.parse(temp_path)
        assert "Hello, EPUB World!" in result.text
        assert result.page_count == 1
        assert result.format_type == "epub"
    finally:
        Path(temp_path).unlink()