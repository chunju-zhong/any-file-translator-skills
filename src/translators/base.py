"""基础翻译器抽象层"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class TranslationResult:
    """翻译结果"""
    text: str
    source_language: str
    target_language: str
    model: str
    usage: Dict[str, int]
    metadata: Dict[str, Any]


@dataclass
class TranslationRequest:
    """翻译请求"""
    text: str
    source_language: str = "auto"
    target_language: str = "zh"
    context: Optional[str] = None


class BaseTranslator(ABC):
    """翻译器基类"""
    
    name: str = "base"
    supported_languages: List[str] = []
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = None
    
    @abstractmethod
    def translate(self, request: TranslationRequest) -> TranslationResult:
        """翻译文本"""
        pass
    
    @abstractmethod
    def translate_batch(self, requests: List[TranslationRequest]) -> List[TranslationResult]:
        """批量翻译"""
        pass
    
    def supports_language(self, language: str) -> bool:
        """检查是否支持该语言"""
        if not self.supported_languages:
            return True
        return language in self.supported_languages
    
    def detect_language(self, text: str) -> str:
        """检测语言（可选实现）"""
        return "auto"
