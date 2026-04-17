"""大文件处理器"""
import time
from typing import Dict, Any, List
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.processors.chunk_manager import ChunkManager, Chunk
from src.processors.result_merger import ResultMerger
from src.parsers.base import ParseResult
from src.translators.base import TranslationRequest
from src.evaluators.base import EvaluationRequest
from src.utils.logger import get_logger
from src.utils.exceptions import TranslationError


logger = get_logger(__name__)


@dataclass
class ProcessingResult:
    """处理结果"""
    final_text: str
    overall_quality_score: float
    chunks_processed: int
    chunks_failed: int
    processing_time: float
    chunk_details: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LargeFileProcessor:
    """大文件处理器 - 处理超大文件的分块翻译"""
    
    def __init__(
        self,
        translator,
        evaluator,
        improver,
        config: Dict[str, Any] = None
    ):
        self.translator = translator
        self.evaluator = evaluator
        self.improver = improver
        self.config = config or {}
        self.logger = get_logger(__name__)
        
        self.max_parallel_chunks = self.config.get("max_parallel_chunks", 4)
        self.progress_tracking = self.config.get("progress_tracking", True)
        
        self.chunk_manager = ChunkManager(config)
        self.result_merger = ResultMerger(config)
        
        self.progress = {}
    
    def process_large_file(
        self,
        file_path: str,
        parse_result: ParseResult,
        source_language: str,
        target_language: str
    ) -> ProcessingResult:
        """处理大文件"""
        start_time = time.time()
        
        self.logger.info(
            "large_file_processing_started",
            file=file_path,
            source_lang=source_language,
            target_lang=target_language
        )
        
        try:
            chunks = self.chunk_manager.create_chunks(file_path, parse_result)
            
            self.logger.info(
                "chunks_created_for_processing",
                total_chunks=len(chunks)
            )
            
            processed_chunks = self._process_chunks_parallel(
                chunks,
                source_language,
                target_language
            )
            
            final_text = self.result_merger.merge_translations(
                processed_chunks,
                output_format="markdown"
            )
            
            overall_quality_score = self.result_merger.merge_quality_scores(
                processed_chunks
            )
            
            chunks_processed = sum(1 for c in processed_chunks if c.status == "completed")
            chunks_failed = sum(1 for c in processed_chunks if c.status == "failed")
            
            processing_time = time.time() - start_time
            
            chunk_details = [
                {
                    "chunk_id": chunk.chunk_id,
                    "status": chunk.status,
                    "quality_score": chunk.quality_score,
                    "start_page": chunk.start_page,
                    "end_page": chunk.end_page
                }
                for chunk in processed_chunks
            ]
            
            self.chunk_manager.cleanup_chunks([c.chunk_id for c in processed_chunks])
            
            result = ProcessingResult(
                final_text=final_text,
                overall_quality_score=overall_quality_score,
                chunks_processed=chunks_processed,
                chunks_failed=chunks_failed,
                processing_time=processing_time,
                chunk_details=chunk_details,
                metadata={
                    "file_path": file_path,
                    "total_chunks": len(chunks),
                    "source_language": source_language,
                    "target_language": target_language
                }
            )
            
            self.logger.info(
                "large_file_processing_completed",
                file=file_path,
                chunks_processed=chunks_processed,
                chunks_failed=chunks_failed,
                quality_score=round(overall_quality_score, 2),
                processing_time=round(processing_time, 2)
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "large_file_processing_failed",
                file=file_path,
                error=str(e)
            )
            raise TranslationError(f"Large file processing failed: {e}")
    
    def _process_chunk(
        self,
        chunk: Chunk,
        source_language: str,
        target_language: str
    ) -> Chunk:
        """处理单个块"""
        try:
            self._track_progress(chunk.chunk_id, "processing")
            
            if not chunk.text:
                from src.utils.pdf_utils import extract_text_from_pdf
                chunk.text = extract_text_from_pdf(
                    chunk.file_path,
                    page_range=[chunk.start_page, chunk.end_page]
                )
            
            translation_request = TranslationRequest(
                text=chunk.text,
                source_language=source_language,
                target_language=target_language
            )
            
            translation_result = self.translator.translate(translation_request)
            
            evaluation_request = EvaluationRequest(
                original_text=chunk.text,
                translated_text=translation_result.text,
                source_language=source_language,
                target_language=target_language
            )
            
            evaluation_result = self.evaluator.evaluate(evaluation_request)
            
            chunk.translation_result = translation_result.text
            chunk.quality_score = evaluation_result.overall_score
            chunk.status = "completed"
            
            self._track_progress(chunk.chunk_id, "completed")
            
            self.logger.info(
                "chunk_processed",
                chunk_id=chunk.chunk_id,
                quality_score=round(chunk.quality_score, 2),
                status=chunk.status
            )
            
            return chunk
            
        except Exception as e:
            chunk.status = "failed"
            self._track_progress(chunk.chunk_id, "failed")
            
            self.logger.error(
                "chunk_processing_failed",
                chunk_id=chunk.chunk_id,
                error=str(e)
            )
            
            return chunk
    
    def _process_chunks_parallel(
        self,
        chunks: List[Chunk],
        source_language: str,
        target_language: str
    ) -> List[Chunk]:
        """并行处理块"""
        processed_chunks = []
        
        try:
            with ThreadPoolExecutor(max_workers=self.max_parallel_chunks) as executor:
                future_to_chunk = {
                    executor.submit(
                        self._process_chunk,
                        chunk,
                        source_language,
                        target_language
                    ): chunk
                    for chunk in chunks
                }
                
                for future in as_completed(future_to_chunk):
                    chunk = future_to_chunk[future]
                    try:
                        processed_chunk = future.result()
                        processed_chunks.append(processed_chunk)
                    except Exception as e:
                        self.logger.error(
                            "chunk_future_failed",
                            chunk_id=chunk.chunk_id,
                            error=str(e)
                        )
                        chunk.status = "failed"
                        processed_chunks.append(chunk)
            
            return processed_chunks
            
        except Exception as e:
            self.logger.error("parallel_processing_failed", error=str(e))
            raise TranslationError(f"Parallel processing failed: {e}")
    
    def _track_progress(self, chunk_id: str, status: str) -> None:
        """跟踪处理进度"""
        if self.progress_tracking:
            self.progress[chunk_id] = {
                "status": status,
                "timestamp": time.time()
            }
            
            self.logger.info(
                "progress_tracked",
                chunk_id=chunk_id,
                status=status
            )
