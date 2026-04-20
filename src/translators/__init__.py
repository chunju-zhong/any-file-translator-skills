"""翻译器模块"""
from typing import Dict, List, Optional
from src.translators.base import BaseTranslator, TranslationResult, TranslationRequest
from src.translators.openai_translator import OpenAITranslator
from src.translators.deepl_translator import DeepLTranslator
from src.translators.google_translator import GoogleTranslator
from src.translators.selector import TranslatorSelector, SelectionResult
from src.config import load_config

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


_config = load_config()

_openai_translator = OpenAITranslator(_config.translator.model_dump())
register_translator("openai", _openai_translator, set_default=True)

if _config.deepl.enabled and _config.deepl.api_key:
    _deepl_translator = DeepLTranslator(_config.deepl.model_dump())
    register_translator("deepl", _deepl_translator)

if _config.google_translate.enabled and _config.google_translate.api_key:
    _google_translator = GoogleTranslator(_config.google_translate.model_dump())
    register_translator("google", _google_translator)


__all__ = [
    'BaseTranslator',
    'TranslationResult',
    'TranslationRequest',
    'register_translator',
    'get_translator',
    'list_translators',
    'set_default_translator',
    'TranslatorSelector',
    'SelectionResult',
    'OpenAITranslator',
    'DeepLTranslator',
    'GoogleTranslator',
]
