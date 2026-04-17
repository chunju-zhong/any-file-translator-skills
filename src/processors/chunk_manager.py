"""分块管理器"""
import os
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from src.parsers.base import ParseResult, Chapter
from src.utils.logger import get_logger
from src.utils.exceptions import FileProcessingError
from src.utils.pdf_utils import split_pdf


logger = get_logger(__name__)


@dataclass
class Chunk:
    """文件块"""
    chunk_id: str
    file_path: str
    start_page: int
    end_page: int
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    translation_result: Optional[str] = None
    quality_score: Optional[float] = None


class ChunkManager:
    """分块管理器 - 管理大文件的分块和合并"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = get_logger(__name__)
        
        self.size_threshold_pages = self.config.get("size_threshold_pages", 100)
        self.size_threshold_mb = self.config.get("size_threshold_mb", 50.0)
        self.chunk_size = self.config.get("chunk_size", 50)
        self.temp_dir = self.config.get("temp_dir", ".chunks")
    
    def should_chunk(self, file_path: str, parse_result: ParseResult) -> bool:
        """判断文件是否需要分块"""
        page_count = parse_result.page_count
        
        file_size_mb = 0
        if os.path.exists(file_path):
            file_size_bytes = os.path.getsize(file_path)
            file_size_mb = file_size_bytes / (1024 * 1024)
        
        needs_chunking = (
            page_count > self.size_threshold_pages or
            file_size_mb > self.size_threshold_mb
        )
        
        self.logger.info(
            "chunking_decision",
            file=file_path,
            page_count=page_count,
            file_size_mb=round(file_size_mb, 2),
            threshold_pages=self.size_threshold_pages,
            threshold_mb=self.size_threshold_mb,
            needs_chunking=needs_chunking
        )
        
        return needs_chunking
    
    def create_chunks(self, file_path: str, parse_result: ParseResult) -> List[Chunk]:
        """创建文件块"""
        chunks = []
        
        try:
            file_format = parse_result.format_type.lower()
            page_count = parse_result.page_count
            chapters = parse_result.metadata.get("chapters", [])
            
            if file_format == "pdf":
                chunks = self._create_pdf_chunks(file_path, parse_result, chapters)
            elif file_format in ["docx", "epub"]:
                chunks = self._create_document_chunks(file_path, parse_result)
            else:
                chunks = self._create_text_chunks(file_path, parse_result)
            
            self.logger.info(
                "chunks_created",
                file=file_path,
                format=file_format,
                total_chunks=len(chunks),
                total_pages=page_count
            )
            
            return chunks
            
        except Exception as e:
            self.logger.error("chunk_creation_failed", file=file_path, error=str(e))
            raise FileProcessingError(f"Failed to create chunks: {e}")
    
    def _create_pdf_chunks(
        self,
        file_path: str,
        parse_result: ParseResult,
        chapters: List[Chapter]
    ) -> List[Chunk]:
        """创建 PDF 文件块"""
        chunks = []
        temp_dir = Path(self.temp_dir) / str(uuid.uuid4())
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            chunk_files = split_pdf(
                input_path=file_path,
                output_dir=str(temp_dir),
                chapters=chapters,
                max_pages=self.chunk_size
            )
            
            for i, chunk_file in enumerate(chunk_files):
                chunk_id = str(uuid.uuid4())
                
                start_page = i * self.chunk_size + 1
                end_page = min((i + 1) * self.chunk_size, parse_result.page_count)
                
                chunk = Chunk(
                    chunk_id=chunk_id,
                    file_path=chunk_file,
                    start_page=start_page,
                    end_page=end_page,
                    text="",
                    metadata={
                        "original_file": file_path,
                        "chunk_index": i,
                        "total_chunks": len(chunk_files),
                        "temp_file": True
                    }
                )
                chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            self.logger.error("pdf_chunk_creation_failed", file=file_path, error=str(e))
            raise FileProcessingError(f"Failed to create PDF chunks: {e}")
    
    def _create_document_chunks(
        self,
        file_path: str,
        parse_result: ParseResult
    ) -> List[Chunk]:
        """创建文档块（DOCX, EPUB）"""
        chunks = []
        
        text = parse_result.text
        total_length = len(text)
        chunk_text_size = self.chunk_size * 2000
        
        chunk_index = 0
        start_pos = 0
        
        while start_pos < total_length:
            end_pos = min(start_pos + chunk_text_size, total_length)
            chunk_text = text[start_pos:end_pos]
            
            chunk_id = str(uuid.uuid4())
            
            chunk = Chunk(
                chunk_id=chunk_id,
                file_path=file_path,
                start_page=chunk_index * self.chunk_size + 1,
                end_page=(chunk_index + 1) * self.chunk_size,
                text=chunk_text,
                metadata={
                    "original_file": file_path,
                    "chunk_index": chunk_index,
                    "start_pos": start_pos,
                    "end_pos": end_pos,
                    "temp_file": False
                }
            )
            chunks.append(chunk)
            
            start_pos = end_pos
            chunk_index += 1
        
        return chunks
    
    def _create_text_chunks(
        self,
        file_path: str,
        parse_result: ParseResult
    ) -> List[Chunk]:
        """创建文本块（TXT, MD）"""
        chunks = []
        
        text = parse_result.text
        total_length = len(text)
        chunk_text_size = self.chunk_size * 2000
        
        chunk_index = 0
        start_pos = 0
        
        while start_pos < total_length:
            end_pos = min(start_pos + chunk_text_size, total_length)
            chunk_text = text[start_pos:end_pos]
            
            chunk_id = str(uuid.uuid4())
            
            chunk = Chunk(
                chunk_id=chunk_id,
                file_path=file_path,
                start_page=chunk_index + 1,
                end_page=chunk_index + 1,
                text=chunk_text,
                metadata={
                    "original_file": file_path,
                    "chunk_index": chunk_index,
                    "start_pos": start_pos,
                    "end_pos": end_pos,
                    "temp_file": False
                }
            )
            chunks.append(chunk)
            
            start_pos = end_pos
            chunk_index += 1
        
        return chunks
    
    def get_chunk_info(self, chunk_id: str) -> Dict[str, Any]:
        """获取块信息"""
        return {
            "chunk_id": chunk_id,
            "status": "pending"
        }
    
    def cleanup_chunks(self, chunk_ids: List[str]) -> None:
        """清理临时块文件"""
        try:
            temp_dir = Path(self.temp_dir)
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
                self.logger.info("chunks_cleaned", directory=str(temp_dir))
        except Exception as e:
            self.logger.warning("chunk_cleanup_failed", error=str(e))
