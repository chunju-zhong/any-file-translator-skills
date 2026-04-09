"""PDF 文件解析器"""
from pathlib import Path
from typing import List, Dict, Any
import pdfplumber
from pypdf import PdfReader
from src.parsers.base import BaseParser, ParseResult, Chapter
from src.utils.logger import get_logger
from src.utils.exceptions import FileProcessingError


class PdfParser(BaseParser):
    """PDF 文件解析器"""
    
    supported_extensions = [".pdf"]
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
    
    def parse(self, file_path: str) -> ParseResult:
        """解析 PDF 文件"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise FileProcessingError(f"File not found: {file_path}")
            
            if not self.can_parse(file_path):
                raise FileProcessingError(f"Unsupported file format: {file_path}")
            
            text = ""
            metadata = {}
            
            # 使用 pdfplumber 提取文本
            with pdfplumber.open(path) as pdf:
                page_count = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
            
            # 提取 PDF 元数据
            with open(path, 'rb') as f:
                reader = PdfReader(f)
                if reader.metadata:
                    metadata.update(dict(reader.metadata))
            
            # 提取章节信息
            chapters = self.extract_chapters(file_path)
            metadata["chapter_count"] = len(chapters)
            
            self.logger.info(
                "pdf_file_parsed",
                file=str(path),
                pages=page_count,
                size=len(text),
                chapters=len(chapters)
            )
            
            return ParseResult(
                text=text,
                page_count=page_count,
                metadata={
                    "file_size": path.stat().st_size,
                    "file_name": path.name,
                    "chapter_count": len(chapters),
                    **metadata
                },
                format_type="pdf"
            )
        
        except Exception as e:
            self.logger.error("pdf_parse_error", file=file_path, error=str(e))
            raise FileProcessingError(f"Failed to parse PDF file: {e}")
    
    def get_page_count(self, file_path: str) -> int:
        """获取 PDF 页数"""
        try:
            with pdfplumber.open(file_path) as pdf:
                return len(pdf.pages)
        except Exception as e:
            self.logger.error("pdf_page_count_error", file=file_path, error=str(e))
            raise FileProcessingError(f"Failed to get page count: {e}")
    
    def extract_chapters(self, file_path: str) -> List[Chapter]:
        """提取 PDF 章节信息"""
        chapters = []
        
        try:
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                
                # 尝试从书签提取章节
                if reader.outline:
                    chapters = self._extract_chapters_from_outline(reader.outline)
                
                # 如果没有书签，尝试基于字体大小识别
                if not chapters:
                    chapters = self._extract_chapters_from_fonts(file_path)
        
        except Exception as e:
            self.logger.warning("pdf_chapter_extraction_error", file=file_path, error=str(e))
        
        return chapters
    
    def _extract_chapters_from_outline(self, outline) -> List[Chapter]:
        """从书签提取章节"""
        chapters = []
        
        def process_outline_item(item, level=1, parent_page=None):
            if isinstance(item, list):
                for subitem in item:
                    process_outline_item(subitem, level, parent_page)
            else:
                title = item.title
                page_num = item.page_number
                
                if page_num:
                    # 计算章节结束页
                    end_page = page_num
                    # 简单实现：章节结束页为下一章节开始页减 1
                    # 实际实现可能需要更复杂的逻辑
                    chapters.append(Chapter(
                        title=title,
                        start_page=page_num,
                        end_page=end_page,
                        level=level
                    ))
        
        process_outline_item(outline)
        return chapters
    
    def _extract_chapters_from_fonts(self, file_path: str) -> List[Chapter]:
        """基于字体大小识别章节"""
        chapters = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    if page.chars:
                        # 分析字体大小
                        char_sizes = [char['size'] for char in page.chars if char['text'].strip()]
                        if char_sizes:
                            # 找到最大的字体大小，可能是标题
                            max_size = max(char_sizes)
                            # 找到使用最大字体的文本
                            title_chars = [char for char in page.chars if char['size'] == max_size]
                            if title_chars:
                                # 简单实现：将最大字体的文本作为章节标题
                                title = ''.join([char['text'] for char in title_chars]).strip()
                                if title:
                                    chapters.append(Chapter(
                                        title=title,
                                        start_page=page_num + 1,  # PDF 页码从 1 开始
                                        end_page=page_num + 1,
                                        level=1
                                    ))
        except Exception as e:
            self.logger.warning("pdf_font_based_chapter_error", file=file_path, error=str(e))
        
        return chapters