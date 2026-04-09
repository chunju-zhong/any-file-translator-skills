"""Markdown 文件解析器"""
from pathlib import Path
from src.parsers.base import BaseParser, ParseResult
from src.utils.logger import get_logger
from src.utils.exceptions import FileProcessingError


class MdParser(BaseParser):
    """Markdown 文件解析器"""
    
    supported_extensions = [".md", ".markdown"]
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
    
    def parse(self, file_path: str) -> ParseResult:
        """解析 Markdown 文件，保留格式标记"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise FileProcessingError(f"File not found: {file_path}")
            
            if not self.can_parse(file_path):
                raise FileProcessingError(f"Unsupported file format: {file_path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            metadata = self._extract_metadata(text)
            
            self.logger.info(
                "markdown_file_parsed",
                file=str(path),
                size=len(text),
                has_frontmatter=metadata.get("has_frontmatter", False)
            )
            
            return ParseResult(
                text=text,
                page_count=1,
                metadata={
                    "file_size": len(text),
                    "file_name": path.name,
                    **metadata
                },
                format_type="markdown"
            )
        
        except UnicodeDecodeError as e:
            self.logger.error("markdown_decode_error", file=file_path, error=str(e))
            raise FileProcessingError(f"Failed to decode file: {file_path}")
        
        except Exception as e:
            self.logger.error("markdown_parse_error", file=file_path, error=str(e))
            raise FileProcessingError(f"Failed to parse Markdown file: {e}")
    
    def get_page_count(self, file_path: str) -> int:
        """Markdown 文件只有 1 页"""
        return 1
    
    def _extract_metadata(self, text: str) -> dict:
        """提取 Markdown 元数据（如 YAML frontmatter）"""
        metadata = {}
        
        if text.startswith("---\n"):
            try:
                end_index = text.index("---\n", 4)
                frontmatter = text[4:end_index]
                metadata["has_frontmatter"] = True
                metadata["frontmatter_size"] = len(frontmatter)
            except ValueError:
                metadata["has_frontmatter"] = False
        
        lines = text.split('\n')
        heading_count = sum(1 for line in lines if line.startswith('#'))
        metadata["heading_count"] = heading_count
        
        code_block_count = text.count('```')
        metadata["code_block_count"] = code_block_count // 2
        
        return metadata
