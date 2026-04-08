"""解析器模块"""
from typing import Dict, List, Optional
from src.parsers.base import BaseParser, ParseResult, Chapter

_parsers: Dict[str, BaseParser] = {}


def register_parser(extensions: List[str], parser: BaseParser):
    """注册解析器"""
    for ext in extensions:
        _parsers[ext] = parser


def get_parser(file_path: str) -> BaseParser:
    """获取适合文件的解析器"""
    from pathlib import Path
    ext = Path(file_path).suffix.lower()
    
    if ext not in _parsers:
        from src.utils.exceptions import UnsupportedFormatError
        raise UnsupportedFormatError(f"Unsupported file format: {ext}")
    
    return _parsers[ext]


def list_supported_formats() -> List[str]:
    """列出所有支持的文件格式"""
    return list(_parsers.keys())


__all__ = [
    'BaseParser',
    'ParseResult', 
    'Chapter',
    'register_parser',
    'get_parser',
    'list_supported_formats',
]
