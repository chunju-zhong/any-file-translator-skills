"""主翻译器测试"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from src.translator import Translator


def test_translator_translate_text():
    """测试文本翻译"""
    with patch('src.translator.get_translator') as mock_get_translator, \
         patch('src.translator.get_evaluator') as mock_get_evaluator:
        
        mock_translator = Mock()
        mock_translator.translate.return_value = Mock(
            text="你好",
            model="gpt-4",
            usage={"total_tokens": 15}
        )
        mock_get_translator.return_value = mock_translator
        
        mock_evaluator = Mock()
        mock_evaluator.evaluate.return_value = Mock(
            overall_score=85.0,
            completeness_score=90.0,
            issues=[],
            suggestions=[]
        )
        mock_get_evaluator.return_value = mock_evaluator
        
        translator = Translator()
        result = translator.translate_text("Hello")
        assert result["translated_text"] == "你好"
        assert result["quality_score"] == 85.0
        assert result["completeness_score"] == 90.0


def test_translator_translate_file():
    """测试文件翻译"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("Hello, World!")
        temp_file = f.name
    
    try:
        with patch('src.translator.get_parser') as mock_get_parser, \
             patch('src.translator.get_translator') as mock_get_translator, \
             patch('src.translator.get_evaluator') as mock_get_evaluator:
            
            mock_parser = Mock()
            mock_parser.parse.return_value = Mock(
                text="Hello, World!",
                page_count=1,
                format_type="txt",
                metadata={}
            )
            mock_get_parser.return_value = mock_parser
            
            mock_translator = Mock()
            mock_translator.translate.return_value = Mock(
                text="你好，世界！",
                model="gpt-4",
                usage={"total_tokens": 20}
            )
            mock_get_translator.return_value = mock_translator
            
            mock_evaluator = Mock()
            mock_evaluator.evaluate.return_value = Mock(
                overall_score=90.0,
                completeness_score=95.0,
                issues=[],
                suggestions=[]
            )
            mock_get_evaluator.return_value = mock_evaluator
            
            translator = Translator()
            result = translator.translate_file(temp_file)
            assert result["translated_text"] == "你好，世界！"
            assert result["quality_score"] == 90.0
            assert result["metadata"]["format"] == "txt"
    finally:
        Path(temp_file).unlink()


def test_translator_list_supported_formats():
    """测试列出支持的格式"""
    formats = Translator.list_supported_formats()
    assert isinstance(formats, list)
    assert ".txt" in formats
    assert ".md" in formats
