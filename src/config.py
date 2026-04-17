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


class IterativeImprovementSettings(BaseModel):
    """迭代改进配置"""
    enabled: bool = Field(default=True, description="是否启用迭代改进")
    quality_threshold: float = Field(default=85.0, description="质量阈值（低于此值触发改进）")
    max_iterations: int = Field(default=3, description="最大迭代次数")
    track_history: bool = Field(default=False, description="是否记录改进历史")


class LargeFileSettings(BaseModel):
    """大文件处理配置"""
    enabled: bool = Field(default=True, description="是否启用大文件处理")
    size_threshold_pages: int = Field(default=100, description="页数阈值（超过此值触发分块）")
    size_threshold_mb: float = Field(default=50.0, description="文件大小阈值 MB（超过此值触发分块）")
    chunk_size: int = Field(default=50, description="分块大小（页数）")
    max_parallel_chunks: int = Field(default=4, description="最大并行处理块数")
    merge_strategy: str = Field(default="sequential", description="合并策略：sequential, parallel")
    progress_tracking: bool = Field(default=True, description="是否启用进度跟踪")


class Config(BaseModel):
    """完整配置"""
    translator: TranslatorSettings = Field(default_factory=TranslatorSettings)
    processing: ProcessingSettings = Field(default_factory=ProcessingSettings)
    output: OutputSettings = Field(default_factory=OutputSettings)
    improvement: IterativeImprovementSettings = Field(default_factory=IterativeImprovementSettings)
    large_file: LargeFileSettings = Field(default_factory=LargeFileSettings)


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
