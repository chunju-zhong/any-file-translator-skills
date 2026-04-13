"""结果合并器"""
from typing import Dict, Any, List
from src.processors.chunk_manager import Chunk
from src.utils.logger import get_logger
from src.utils.exceptions import FileProcessingError


logger = get_logger(__name__)


class ResultMerger:
    """结果合并器 - 合并翻译后的文件块"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = get_logger(__name__)
        
        self.merge_strategy = self.config.get("merge_strategy", "sequential")
    
    def merge_translations(self, chunks: List[Chunk], output_format: str = "markdown") -> str:
        """合并翻译结果"""
        try:
            if not chunks:
                raise FileProcessingError("No chunks to merge")
            
            sorted_chunks = sorted(chunks, key=lambda c: c.metadata.get("chunk_index", 0))
            
            translated_texts = []
            for chunk in sorted_chunks:
                if chunk.translation_result:
                    translated_texts.append(chunk.translation_result)
                else:
                    self.logger.warning(
                        "chunk_missing_translation",
                        chunk_id=chunk.chunk_id,
                        chunk_index=chunk.metadata.get("chunk_index")
                    )
            
            if self.merge_strategy == "sequential":
                merged_text = self._merge_sequential(translated_texts)
            else:
                merged_text = self._merge_parallel(translated_texts)
            
            merged_text = self.ensure_coherence(merged_text)
            
            self.logger.info(
                "translations_merged",
                total_chunks=len(chunks),
                successful_chunks=len(translated_texts),
                output_format=output_format,
                merged_length=len(merged_text)
            )
            
            return merged_text
            
        except Exception as e:
            self.logger.error("translation_merge_failed", error=str(e))
            raise FileProcessingError(f"Failed to merge translations: {e}")
    
    def merge_quality_scores(self, chunks: List[Chunk]) -> float:
        """合并质量评分"""
        try:
            scores = [chunk.quality_score for chunk in chunks if chunk.quality_score is not None]
            
            if not scores:
                return 0.0
            
            overall_score = sum(scores) / len(scores)
            
            self.logger.info(
                "quality_scores_merged",
                total_chunks=len(chunks),
                scored_chunks=len(scores),
                average_score=round(overall_score, 2)
            )
            
            return overall_score
            
        except Exception as e:
            self.logger.error("quality_merge_failed", error=str(e))
            return 0.0
    
    def ensure_coherence(self, text: str) -> str:
        """确保文本连贯性"""
        try:
            paragraphs = text.split('\n\n')
            
            coherent_paragraphs = []
            for i, paragraph in enumerate(paragraphs):
                paragraph = paragraph.strip()
                
                if i > 0 and paragraph:
                    paragraph = self._smooth_boundaries(paragraphs[i-1], paragraph)
                
                coherent_paragraphs.append(paragraph)
            
            coherent_text = '\n\n'.join(coherent_paragraphs)
            
            return coherent_text
            
        except Exception as e:
            self.logger.warning("coherence_check_failed", error=str(e))
            return text
    
    def _merge_sequential(self, texts: List[str]) -> str:
        """顺序合并"""
        return '\n\n'.join(texts)
    
    def _merge_parallel(self, texts: List[str]) -> str:
        """并行合并（带分隔符）"""
        separator = '\n\n---\n\n'
        return separator.join(texts)
    
    def _smooth_boundaries(self, prev_text: str, next_text: str) -> str:
        """平滑块边界"""
        try:
            if not prev_text or not next_text:
                return next_text
            
            prev_last_sentence = prev_text.rstrip().split('.')[-1] if '.' in prev_text else prev_text.rstrip()[-50:]
            
            next_first_sentence = next_text.split('.')[0] if '.' in next_text else next_text[:50]
            
            if prev_last_sentence and next_first_sentence:
                if prev_last_sentence[-1] in '。！？!?' and next_first_sentence[0].isupper():
                    return next_text
            
            return next_text
            
        except Exception as e:
            self.logger.warning("boundary_smoothing_failed", error=str(e))
            return next_text
