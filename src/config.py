"""配置管理模块"""
from pathlib import Path
from typing import Optional
import os
import yaml
from pydantic import BaseModel, Field


class TranslatorSettings(BaseModel):
    """翻译服务配置"""
    api_key: str = Field(default="", description="翻译 API 密钥")
    base_url: str = Field(default="https://api.openai.com/v1", description="API 基础 URL")
    model: str = Field(default="gpt-4", description="使用的模型")
    temperature: float = Field(default=0.3, description="翻译温度")
    max_tokens: Optional[int] = Field(default=None, description="最大 token 数")
    timeout: int = Field(default=60, description="请求超时时间（秒）")
    max_retries: int = Field(default=3, description="最大重试次数")


class ProcessingSettings(BaseModel):
    """处理配置"""
    chunk_size: int = Field(default=15, description="分块大小（页数）")
    max_parallel: int = Field(default=4, description="最大并行数")
    cache_enabled: bool = Field(default=True, description="是否启用缓存")
    cache_dir: str = Field(default=".cache", description="缓存目录")


class OutputSettings(BaseModel):
    """输出配置"""
    output_dir: str = Field(default="output", description="输出目录")
    default_format: str = Field(default="markdown", description="默认输出格式")
    bilingual: bool = Field(default=False, description="是否双语对照")


class Config(BaseModel):
    """完整配置"""
    translator: TranslatorSettings = Field(default_factory=TranslatorSettings)
    processing: ProcessingSettings = Field(default_factory=ProcessingSettings)
    output: OutputSettings = Field(default_factory=OutputSettings)


def load_config(config_path: Optional[str] = None) -> Config:
    """加载配置"""
    config = Config()
    
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            if config_data:
                config = Config(**config_data)
    
    if api_key := os.getenv("TRANSLATOR_API_KEY"):
        config.translator.api_key = api_key
    if base_url := os.getenv("TRANSLATOR_BASE_URL"):
        config.translator.base_url = base_url
    if model := os.getenv("TRANSLATOR_MODEL"):
        config.translator.model = model
    
    return config
