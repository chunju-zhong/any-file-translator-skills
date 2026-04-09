"""TXT 文件解析器"""
from pathlib import Path
from src.parsers.base import BaseParser, ParseResult
from src.utils.logger import get_logger
from src.utils.exceptions import FileProcessingError


class TxtParser(BaseParser):
    """TXT 文件解析器"""
    
    supported_extensions = [".txt"]
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
    
    def parse(self, file_path: str) -> ParseResult:
        """解析 TXT 文件"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise FileProcessingError(f"File not found: {file_path}")
            
            if not self.can_parse(file_path):
                raise FileProcessingError(f"Unsupported file format: {file_path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            self.logger.info(
                "txt_file_parsed",
                file=str(path),
                size=len(text)
            )
            
            return ParseResult(
                text=text,
                page_count=1,
                metadata={
                    "file_size": len(text),
                    "file_name": path.name,
                },
                format_type="txt"
            )
        
        except UnicodeDecodeError as e:
            self.logger.error("txt_decode_error", file=file_path, error=str(e))
            raise FileProcessingError(f"Failed to decode file: {file_path}")
        
        except Exception as e:
            self.logger.error("txt_parse_error", file=file_path, error=str(e))
            raise FileProcessingError(f"Failed to parse TXT file: {e}")
    
    def get_page_count(self, file_path: str) -> int:
        """TXT 文件只有 1 页"""
        return 1
