"""文档工具函数测试"""
import pytest
import tempfile
from pathlib import Path
from src.utils.doc_utils import create_docx, extract_docx_styles

def test_create_docx():
    """测试创建 DOCX 文件"""
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        temp_path = f.name
    
    try:
        result_path = create_docx(temp_path, "Hello, DOCX!\nThis is a test.")
        assert result_path == temp_path
        assert Path(result_path).exists()
    finally:
        Path(temp_path).unlink()

def test_extract_docx_styles():
    """测试提取 DOCX 样式"""
    from docx import Document
    
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        temp_path = f.name
    
    # 创建测试 DOCX 文件
    doc = Document()
    doc.add_paragraph("Test")
    doc.save(temp_path)
    
    try:
        styles = extract_docx_styles(temp_path)
        assert 'paragraph_styles' in styles
        assert isinstance(styles['paragraph_styles'], dict)
    finally:
        Path(temp_path).unlink()