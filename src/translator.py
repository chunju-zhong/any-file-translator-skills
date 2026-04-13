"""主翻译流程编排器"""
from pathlib import Path
from typing import Optional
from src.parsers import get_parser, list_supported_formats
from src.translators import get_translator
from src.evaluators import get_evaluator
from src.improver import IterativeImprover
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
        
        improvement_config = {
            "quality_threshold": self.config.improvement.quality_threshold,
            "max_iterations": self.config.improvement.max_iterations,
            "improvement_delay": self.config.improvement.improvement_delay,
            "enable_improvement": self.config.improvement.enable_improvement
        }
        self.improver = IterativeImprover(improvement_config)
    
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
            
            if self.config.improvement.enable_improvement and evaluation_result.overall_score < self.config.improvement.quality_threshold:
                self.logger.info(
                    "improvement_triggered",
                    score=evaluation_result.overall_score,
                    threshold=self.config.improvement.quality_threshold
                )
                
                improvement_result = self.improver.improve_translation(
                    parse_result.text,
                    translation_result.text,
                    evaluation_result,
                    self.translator,
                    source_language,
                    target_language
                )
                
                if output_path:
                    self._save_output(improvement_result.final_text, output_path)
                
                return {
                    "original_text": parse_result.text,
                    "translated_text": improvement_result.final_text,
                    "quality_score": improvement_result.final_score,
                    "completeness_score": evaluation_result.completeness_score,
                    "issues": evaluation_result.issues,
                    "suggestions": evaluation_result.suggestions,
                    "improvement_iterations": improvement_result.iterations,
                    "improvement_success": improvement_result.success,
                    "metadata": {
                        "source_file": file_path,
                        "source_language": source_language,
                        "target_language": target_language,
                        "format": parse_result.format_type,
                        "model": translation_result.model,
                        "usage": translation_result.usage,
                        "improvement_history": improvement_result.improvement_history
                    }
                }
            
            if output_path:
                self._save_output(translation_result.text, output_path)
            
            return {
                "original_text": parse_result.text,
                "translated_text": translation_result.text,
                "quality_score": evaluation_result.overall_score,
                "completeness_score": evaluation_result.completeness_score,
                "issues": evaluation_result.issues,
                "suggestions": evaluation_result.suggestions,
                "metadata": {
                    "source_file": file_path,
                    "source_language": source_language,
                    "target_language": target_language,
                    "format": parse_result.format_type,
                    "model": translation_result.model,
                    "usage": translation_result.usage
                }
            }
        
            if output_path:
                self._save_output(translation_result.text, output_path)
            
            return {
                "original_text": parse_result.text,
                "translated_text": translation_result.text,
                "quality_score": evaluation_result.overall_score,
                "completeness_score": evaluation_result.completeness_score,
                "issues": evaluation_result.issues,
                "suggestions": evaluation_result.suggestions,
                "metadata": {
                    "source_file": file_path,
                    "source_language": source_language,
                    "target_language": target_language,
                    "format": parse_result.format_type,
                    "model": translation_result.model,
                    "usage": translation_result.usage
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
            
            if self.config.improvement.enable_improvement and evaluation_result.overall_score < self.config.improvement.quality_threshold:
                self.logger.info(
                    "improvement_triggered",
                    score=evaluation_result.overall_score,
                    threshold=self.config.improvement.quality_threshold
                )
                
                improvement_result = self.improver.improve_translation(
                    text,
                    translation_result.text,
                    evaluation_result,
                    self.translator,
                    source_language,
                    target_language
                )
                
                return {
                    "original_text": text,
                    "translated_text": improvement_result.final_text,
                    "quality_score": improvement_result.final_score,
                    "completeness_score": evaluation_result.completeness_score,
                    "issues": evaluation_result.issues,
                    "suggestions": evaluation_result.suggestions,
                    "improvement_iterations": improvement_result.iterations,
                    "improvement_success": improvement_result.success,
                    "metadata": {
                        "source_language": source_language,
                        "target_language": target_language,
                        "model": translation_result.model,
                        "usage": translation_result.usage,
                        "improvement_history": improvement_result.improvement_history
                    }
                }
            
            return {
                "original_text": text,
                "translated_text": translation_result.text,
                "quality_score": evaluation_result.overall_score,
                "completeness_score": evaluation_result.completeness_score,
                "issues": evaluation_result.issues,
                "suggestions": evaluation_result.suggestions,
                "metadata": {
                    "source_language": source_language,
                    "target_language": target_language,
                    "model": translation_result.model,
                    "usage": translation_result.usage
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
