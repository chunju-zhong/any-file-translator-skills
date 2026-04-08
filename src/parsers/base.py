"""基础解析器抽象层"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path


@dataclass
class ParseResult:
    """解析结果"""
    text: str
    page_count: int
    metadata: Dict[str, Any]
    format_type: str


@dataclass
class Chapter:
    """章节信息"""
    title: str
    start_page: int
    end_page: int
    level: int = 1


class BaseParser(ABC):
    """文件解析器基类"""
    
    supported_extensions: List[str] = []
    
    def __init__(self):
        self.logger = None
    
    @abstractmethod
    def parse(self, file_path: str) -> ParseResult:
        """解析文件并返回文本内容"""
        pass
    
    @abstractmethod
    def get_page_count(self, file_path: str) -> int:
        """获取文件页数"""
        pass
    
    def can_parse(self, file_path: str) -> bool:
        """检查是否支持该文件"""
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_extensions
    
    def extract_chapters(self, file_path: str) -> List[Chapter]:
        """提取章节信息（可选实现）"""
        return []
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """获取文件元数据（可选实现）"""
        return {}
