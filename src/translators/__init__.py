"""翻译器模块"""
from typing import Dict, List, Optional
from src.translators.base import BaseTranslator, TranslationResult, TranslationRequest

_translators: Dict[str, BaseTranslator] = {}
_default_translator: Optional[str] = None


def register_translator(name: str, translator: BaseTranslator, set_default: bool = False):
    """注册翻译器"""
    global _default_translator
    _translators[name] = translator
    if set_default or not _default_translator:
        _default_translator = name


def get_translator(name: str = None) -> BaseTranslator:
    """获取翻译器"""
    if name is None:
        name = _default_translator
    
    if name not in _translators:
        from src.utils.exceptions import ConfigurationError
        raise ConfigurationError(f"Translator not found: {name}")
    
    return _translators[name]


def list_translators() -> List[str]:
    """列出所有注册的翻译器"""
    return list(_translators.keys())


def set_default_translator(name: str):
    """设置默认翻译器"""
    global _default_translator
    if name not in _translators:
        from src.utils.exceptions import ConfigurationError
        raise ConfigurationError(f"Translator not found: {name}")
    _default_translator = name


__all__ = [
    'BaseTranslator',
    'TranslationResult',
    'TranslationRequest',
    'register_translator',
    'get_translator',
    'list_translators',
    'set_default_translator',
]
