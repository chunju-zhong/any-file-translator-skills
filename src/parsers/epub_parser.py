"""EPUB 文件解析器"""
from pathlib import Path
from typing import List, Dict, Any
import ebooklib
from ebooklib import epub
from src.parsers.base import BaseParser, ParseResult, Chapter
from src.utils.logger import get_logger
from src.utils.exceptions import FileProcessingError


class EpubParser(BaseParser):
    """EPUB 文件解析器"""
    
    supported_extensions = [".epub"]
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
    
    def parse(self, file_path: str) -> ParseResult:
        """解析 EPUB 文件"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise FileProcessingError(f"File not found: {file_path}")
            
            if not self.can_parse(file_path):
                raise FileProcessingError(f"Unsupported file format: {file_path}")
            
            # 使用 ebooklib 提取文本
            book = epub.read_epub(file_path)
            text = ""
            
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    content = item.get_content().decode('utf-8', errors='ignore')
                    # 简单提取文本，去除 HTML 标签
                    import re
                    text_content = re.sub('<[^>]+>', '', content)
                    text += text_content + "\n"
            
            # 提取元数据
            metadata = self._extract_metadata(book)
            
            # 提取章节信息
            chapters = self.extract_chapters(file_path)
            
            self.logger.info(
                "epub_file_parsed",
                file=str(path),
                chapters=len(chapters),
                size=len(text)
            )
            
            return ParseResult(
                text=text,
                page_count=1,  # EPUB 没有固定页数概念
                metadata={
                    "file_size": path.stat().st_size,
                    "file_name": path.name,
                    "chapter_count": len(chapters),
                    **metadata
                },
                format_type="epub"
            )
        
        except Exception as e:
            self.logger.error("epub_parse_error", file=file_path, error=str(e))
            raise FileProcessingError(f"Failed to parse EPUB file: {e}")
    
    def get_page_count(self, file_path: str) -> int:
        """EPUB 文件返回 1 页"""
        return 1
    
    def extract_chapters(self, file_path: str) -> List[Chapter]:
        """从 EPUB 提取章节信息"""
        chapters = []
        
        try:
            book = epub.read_epub(file_path)
            chapter_count = 0
            
            # 遍历 EPUB 的目录结构
            for item in book.toc:
                if isinstance(item, tuple):
                    # 处理嵌套目录
                    chapters.extend(self._process_toc_item(item, 1))
                else:
                    chapter_count += 1
                    chapters.append(Chapter(
                        title=item.title,
                        start_page=1,
                        end_page=1,
                        level=1
                    ))
        
        except Exception as e:
            self.logger.warning("epub_chapter_extraction_error", file=file_path, error=str(e))
        
        return chapters
    
    def _process_toc_item(self, item, level):
        """处理 EPUB 目录项"""
        chapters = []
        title, subitems = item
        
        # 添加当前章节
        chapters.append(Chapter(
            title=title,
            start_page=1,
            end_page=1,
            level=level
        ))
        
        # 处理子章节
        for subitem in subitems:
            if isinstance(subitem, tuple):
                chapters.extend(self._process_toc_item(subitem, level + 1))
            else:
                chapters.append(Chapter(
                    title=subitem.title,
                    start_page=1,
                    end_page=1,
                    level=level + 1
                ))
        
        return chapters
    
    def _extract_metadata(self, book) -> dict:
        """提取 EPUB 元数据"""
        metadata = {}
        
        try:
            # 提取 EPUB 元数据
            if hasattr(book, 'get_metadata'):
                for key, value in book.get_metadata('DC', 'title'):
                    metadata["title"] = value[0]
                for key, value in book.get_metadata('DC', 'creator'):
                    metadata["creator"] = value[0]
                for key, value in book.get_metadata('DC', 'subject'):
                    metadata["subject"] = value[0]
                for key, value in book.get_metadata('DC', 'description'):
                    metadata["description"] = value[0]
        
        except Exception as e:
            self.logger.warning("epub_metadata_extraction_error", error=str(e))
        
        return metadata