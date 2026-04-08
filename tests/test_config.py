"""配置管理测试"""
import pytest
from src.config import Config, TranslatorSettings, load_config


def test_default_config():
    """测试默认配置"""
    config = Config()
    assert config.translator.model == "gpt-4"
    assert config.processing.chunk_size == 15
    assert config.output.default_format == "markdown"


def test_translator_settings():
    """测试翻译设置"""
    settings = TranslatorSettings(
        api_key="test-key",
        model="gpt-3.5-turbo"
    )
    assert settings.api_key == "test-key"
    assert settings.model == "gpt-3.5-turbo"


def test_load_config_from_dict():
    """测试从字典加载配置"""
    config_data = {
        "translator": {
            "model": "gpt-4-turbo"
        },
        "processing": {
            "chunk_size": 20
        }
    }
    config = Config(**config_data)
    assert config.translator.model == "gpt-4-turbo"
    assert config.processing.chunk_size == 20


def test_config_validation():
    """测试配置验证"""
    config = Config()
    assert isinstance(config.translator.temperature, float)
    assert isinstance(config.processing.chunk_size, int)
    assert isinstance(config.output.bilingual, bool)
