"""翻译器选择器"""
from typing import Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from src.translators.base import BaseTranslator, TranslationRequest, TranslationResult
from src.utils.logger import get_logger
from src.utils.exceptions import APIError, ConfigurationError

if TYPE_CHECKING:
    from src.translators import get_translator, list_translators


@dataclass
class TranslatorInfo:
    """翻译器信息"""
    name: str
    translator: BaseTranslator
    priority: int
    rate_limited: bool = False
    error_count: int = 0


@dataclass
class SelectionResult:
    """选择结果"""
    translator_name: str
    result: TranslationResult
    fallback_used: bool = False
    attempted_translators: List[str] = field(default_factory=list)


class TranslatorSelector:
    """翻译器选择器"""
    
    def __init__(self, priorities: Optional[Dict[str, int]] = None):
        self.logger = get_logger(__name__)
        self.priorities = priorities or {}
        self.translators: Dict[str, TranslatorInfo] = {}
        self._init_translators()
    
    def _init_translators(self):
        """初始化翻译器"""
        from src.translators import get_translator, list_translators
        for name in list_translators():
            try:
                translator = get_translator(name)
                priority = self.priorities.get(name, 99)
                self.translators[name] = TranslatorInfo(
                    name=name,
                    translator=translator,
                    priority=priority
                )
            except Exception as e:
                self.logger.warning("translator_init_failed", name=name, error=str(e))
    
    def select_translator(self, source_language: str = "auto", target_language: str = "zh") -> Optional[TranslatorInfo]:
        """选择最佳翻译器"""
        available = [
            info for info in self.translators.values()
            if not info.rate_limited and info.translator.supports_language(target_language)
        ]
        
        if not available:
            return None
        
        available.sort(key=lambda x: x.priority)
        return available[0]
    
    def translate_with_fallback(self, request: TranslationRequest) -> SelectionResult:
        """带回退的翻译"""
        attempted = []
        
        available = [
            info for info in self.translators.values()
            if not info.rate_limited
        ]
        available.sort(key=lambda x: x.priority)
        
        if not available:
            raise ConfigurationError("No translators available")
        
        last_error = None
        
        for info in available:
            attempted.append(info.name)
            
            try:
                result = info.translator.translate(request)
                
                fallback_used = info.name != available[0].name if available else False
                
                return SelectionResult(
                    translator_name=info.name,
                    result=result,
                    fallback_used=fallback_used,
                    attempted_translators=attempted
                )
            
            except APIError as e:
                self.logger.warning(
                    "translator_failed",
                    translator=info.name,
                    error=str(e)
                )
                info.error_count += 1
                
                if e.status_code == 429:
                    info.rate_limited = True
                    self.logger.warning("translator_rate_limited", translator=info.name)
                
                last_error = e
                continue
            
            except Exception as e:
                self.logger.error(
                    "translator_unexpected_error",
                    translator=info.name,
                    error=str(e)
                )
                info.error_count += 1
                last_error = e
                continue
        
        raise APIError(f"All translators failed. Last error: {last_error}")
    
    def translate_batch_with_fallback(self, requests: List[TranslationRequest]) -> List[SelectionResult]:
        """批量翻译带回退"""
        return [self.translate_with_fallback(req) for req in requests]
    
    def get_translator_status(self) -> Dict[str, Dict]:
        """获取翻译器状态"""
        return {
            name: {
                "priority": info.priority,
                "rate_limited": info.rate_limited,
                "error_count": info.error_count,
                "supports_language": info.translator.supported_languages if info.translator.supported_languages else "all"
            }
            for name, info in self.translators.items()
        }
    
    def reset_rate_limits(self):
        """重置速率限制"""
        for info in self.translators.values():
            info.rate_limited = False
        self.logger.info("rate_limits_reset")
    
    def set_priority(self, name: str, priority: int):
        """设置翻译器优先级"""
        if name in self.translators:
            self.translators[name].priority = priority
            self.logger.info("priority_updated", translator=name, priority=priority)
    
    def add_translator(self, name: str, translator: BaseTranslator, priority: int = 99):
        """添加翻译器"""
        self.translators[name] = TranslatorInfo(
            name=name,
            translator=translator,
            priority=priority
        )
        self.logger.info("translator_added", name=name, priority=priority)
    
    def remove_translator(self, name: str):
        """移除翻译器"""
        if name in self.translators:
            del self.translators[name]
            self.logger.info("translator_removed", name=name)
