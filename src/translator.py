"""主翻译流程编排器"""
from pathlib import Path
from typing import Optional
from src.parsers import get_parser, list_supported_formats
from src.translators import get_translator
from src.evaluators import get_evaluator
from src.improvers import get_improver
from src.processors import LargeFileProcessor
from src.config import load_config
from src.utils.logger import get_logger, setup_logger
from src.utils.exceptions import TranslationError


class Translator:
    """主翻译器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化翻译器"""
        self.config = load_config(config_path)
        
        setup_logger(log_level="INFO")
        self.logger = get_logger(__name__)
        
        self.parser = None
        self.translator = get_translator()
        self.evaluator = get_evaluator()
        self.large_file_processor = None
    
    def translate_file(
        self,
        file_path: str,
        source_language: str = "auto",
        target_language: str = "zh",
        output_path: Optional[str] = None
    ) -> dict:
        """翻译文件"""
        try:
            self.parser = get_parser(file_path)
            
            self.logger.info(
                "translation_started",
                file=file_path,
                source_lang=source_language,
                target_lang=target_language
            )
            
            parse_result = self.parser.parse(file_path)
            self.logger.info("file_parsed", format=parse_result.format_type)
            
            if self._should_use_large_file_processing(file_path, parse_result):
                return self._process_large_file(
                    file_path,
                    parse_result,
                    source_language,
                    target_language,
                    output_path
                )
            
            from src.translators.base import TranslationRequest
            translation_request = TranslationRequest(
                text=parse_result.text,
                source_language=source_language,
                target_language=target_language
            )
            translation_result = self.translator.translate(translation_request)
            self.logger.info("text_translated", tokens=translation_result.usage.get("total_tokens", 0))
            
            from src.evaluators.base import EvaluationRequest
            evaluation_request = EvaluationRequest(
                original_text=parse_result.text,
                translated_text=translation_result.text,
                source_language=source_language,
                target_language=target_language
            )
            evaluation_result = self.evaluator.evaluate(evaluation_request)
            self.logger.info("quality_evaluated", score=evaluation_result.overall_score)
            
            translated_text = translation_result.text
            final_quality_score = evaluation_result.overall_score
            final_issues = evaluation_result.issues
            final_suggestions = evaluation_result.suggestions
            iterations = 0
            quality_improved = False
            
            if self.config.improvement.enabled:
                improver = get_improver(
                    self.translator,
                    self.evaluator,
                    self.config.improvement.model_dump()
                )
                
                improved_text, iteration_result = improver.improve(
                    original_text=parse_result.text,
                    initial_translation=translation_result.text,
                    source_language=source_language,
                    target_language=target_language
                )
                
                translated_text = improved_text
                final_quality_score = iteration_result.quality_score
                final_issues = iteration_result.issues
                final_suggestions = iteration_result.suggestions
                iterations = iteration_result.iteration_number
                quality_improved = iteration_result.iteration_number > 0
                
                self.logger.info(
                    "iterative_improvement_completed",
                    iterations=iterations,
                    final_score=final_quality_score,
                    improved=quality_improved
                )
            
            if output_path:
                self._save_output(translated_text, output_path)
            
            return {
                "original_text": parse_result.text,
                "translated_text": translated_text,
                "quality_score": final_quality_score,
                "completeness_score": evaluation_result.completeness_score,
                "issues": final_issues,
                "suggestions": final_suggestions,
                "metadata": {
                    "source_file": file_path,
                    "source_language": source_language,
                    "target_language": target_language,
                    "format": parse_result.format_type,
                    "model": translation_result.model,
                    "usage": translation_result.usage,
                    "iterations": iterations,
                    "quality_improved": quality_improved
                }
            }
        
        except Exception as e:
            self.logger.error("translation_failed", file=file_path, error=str(e))
            raise TranslationError(f"Translation failed: {e}")
    
    def translate_text(
        self,
        text: str,
        source_language: str = "auto",
        target_language: str = "zh"
    ) -> dict:
        """翻译文本"""
        try:
            self.logger.info(
                "text_translation_started",
                source_lang=source_language,
                target_lang=target_language,
                text_length=len(text)
            )
            
            from src.translators.base import TranslationRequest
            translation_request = TranslationRequest(
                text=text,
                source_language=source_language,
                target_language=target_language
            )
            translation_result = self.translator.translate(translation_request)
            
            from src.evaluators.base import EvaluationRequest
            evaluation_request = EvaluationRequest(
                original_text=text,
                translated_text=translation_result.text,
                source_language=source_language,
                target_language=target_language
            )
            evaluation_result = self.evaluator.evaluate(evaluation_request)
            
            translated_text = translation_result.text
            final_quality_score = evaluation_result.overall_score
            final_issues = evaluation_result.issues
            final_suggestions = evaluation_result.suggestions
            iterations = 0
            quality_improved = False
            
            if self.config.improvement.enabled:
                improver = get_improver(
                    self.translator,
                    self.evaluator,
                    self.config.improvement.model_dump()
                )
                
                improved_text, iteration_result = improver.improve(
                    original_text=text,
                    initial_translation=translation_result.text,
                    source_language=source_language,
                    target_language=target_language
                )
                
                translated_text = improved_text
                final_quality_score = iteration_result.quality_score
                final_issues = iteration_result.issues
                final_suggestions = iteration_result.suggestions
                iterations = iteration_result.iteration_number
                quality_improved = iteration_result.iteration_number > 0
                
                self.logger.info(
                    "iterative_improvement_completed",
                    iterations=iterations,
                    final_score=final_quality_score,
                    improved=quality_improved
                )
            
            return {
                "original_text": text,
                "translated_text": translated_text,
                "quality_score": final_quality_score,
                "completeness_score": evaluation_result.completeness_score,
                "issues": final_issues,
                "suggestions": final_suggestions,
                "metadata": {
                    "source_language": source_language,
                    "target_language": target_language,
                    "model": translation_result.model,
                    "usage": translation_result.usage,
                    "iterations": iterations,
                    "quality_improved": quality_improved
                }
            }
        
        except Exception as e:
            self.logger.error("text_translation_failed", error=str(e))
            raise TranslationError(f"Text translation failed: {e}")
    
    def _save_output(self, text: str, output_path: str):
        """保存输出文件"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        self.logger.info("output_saved", file=str(output_file))
    
    @staticmethod
    def list_supported_formats() -> list:
        """列出支持的文件格式"""
        return list_supported_formats()
    
    def _should_use_large_file_processing(self, file_path: str, parse_result) -> bool:
        """判断是否应该使用大文件处理"""
        if not self.config.large_file.enabled:
            return False
        
        from src.processors import ChunkManager
        chunk_manager = ChunkManager(self.config.large_file.model_dump())
        return chunk_manager.should_chunk(file_path, parse_result)
    
    def _process_large_file(
        self,
        file_path: str,
        parse_result,
        source_language: str,
        target_language: str,
        output_path: Optional[str]
    ) -> dict:
        """处理大文件"""
        self.logger.info(
            "large_file_processing_initiated",
            file=file_path,
            threshold_pages=self.config.large_file.size_threshold_pages,
            threshold_mb=self.config.large_file.size_threshold_mb
        )
        
        if not self.large_file_processor:
            improver = get_improver(
                self.translator,
                self.evaluator,
                self.config.improvement.model_dump()
            ) if self.config.improvement.enabled else None
            
            self.large_file_processor = LargeFileProcessor(
                translator=self.translator,
                evaluator=self.evaluator,
                improver=improver,
                config=self.config.large_file.model_dump()
            )
        
        processing_result = self.large_file_processor.process_large_file(
            file_path=file_path,
            parse_result=parse_result,
            source_language=source_language,
            target_language=target_language
        )
        
        if output_path:
            self._save_output(processing_result.final_text, output_path)
        
        return {
            "original_text": parse_result.text[:1000] + "..." if len(parse_result.text) > 1000 else parse_result.text,
            "translated_text": processing_result.final_text,
            "quality_score": processing_result.overall_quality_score,
            "completeness_score": 0.0,
            "issues": [],
            "suggestions": [],
            "metadata": {
                "source_file": file_path,
                "source_language": source_language,
                "target_language": target_language,
                "format": parse_result.format_type,
                "large_file_processing": True,
                "chunks_processed": processing_result.chunks_processed,
                "chunks_failed": processing_result.chunks_failed,
                "processing_time": processing_result.processing_time,
                "chunk_details": processing_result.chunk_details
            }
        }
