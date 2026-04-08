# Plan: Core Infrastructure - Phase 1

## Summary

构建文档翻译系统的基础架构，包括文件处理抽象层、翻译服务抽象层、质量评估框架、配置管理系统、日志和错误处理系统。这些是整个系统的基础，后续所有功能模块都将基于这些抽象层构建。

## User Story

作为开发者，我需要一个可扩展的基础架构，这样我可以快速添加新的文件格式支持、新的翻译 API 和新的质量评估方法，而不需要修改核心代码。

## Problem → Solution

当前状态：从零开始构建文档翻译系统
期望状态：具备完整抽象层的基础架构，支持模块化扩展

## Metadata

- **Complexity**: Medium
- **Source PRD**: `.claude/PRPs/prds/any-file-translator.prd.md`
- **PRD Phase**: Phase 1: Core Infrastructure
- **Estimated Files**: 12-15 个文件

---

## UX Design

### Before
```
┌─────────────────────────────────────────┐
│  无基础架构，直接实现具体功能              │
│  - 硬编码的文件处理逻辑                   │
│  - 紧耦合的翻译服务                       │
│  - 无法扩展新的文件格式                   │
└─────────────────────────────────────────┘
```

### After
```
┌─────────────────────────────────────────┐
│  模块化基础架构，清晰的分层                │
│  - 抽象接口层（FileProcessor,           │
│    Translator, QualityEvaluator）        │
│  - 配置管理层                            │
│  - 日志和错误处理系统                    │
└─────────────────────────────────────────┘
```

### Interaction Changes

| Touchpoint | Before | After | Notes |
|------------|--------|-------|-------|
| 添加新文件格式 | 需要修改核心代码 | 只需实现接口并注册 | 插件式架构 |
| 切换翻译 API | 硬编码替换 | 配置切换 | 无需修改代码 |
| 质量评估 | 固定逻辑 | 可插拔的评估器 | 灵活扩展 |

---

## Mandatory Reading

本阶段是基础架构构建，不需要读取现有代码。所有代码都是从头编写。

| Priority | File | Lines | Why |
|----------|------|-------|-----|
| P0 | `src/parsers/base.py` | - | 基础解析器接口 |
| P0 | `src/translators/base.py` | - | 基础翻译器接口 |
| P0 | `src/evaluators/base.py` | - | 基础评估器接口 |
| P1 | `config/default.yaml` | - | 默认配置文件 |
| P1 | `src/config.py` | - | 配置加载器 |

## External Documentation

| Topic | Source | Key Takeaway |
|-------|--------|--------------|
| pydantic v2 | pydantic 官方文档 | 类型安全的配置管理 |
| structlog | structlog 官方文档 | 结构化日志记录 |
| python-docx | python-docx 官方文档 | DOCX 文件处理 |
| pdfplumber | pdfplumber 官方文档 | PDF 文本提取 |
| ebooklib | ebooklib 官方文档 | EPUB 文件处理 |

---

## Patterns to Mirror

由于是新项目，本阶段将创建所有基础模式。以下是预期的代码结构：

### 抽象基类模式（Abstract Base Class）

```python
# SOURCE: 标准 Python abc 模块用法
from abc import ABC, abstractmethod

class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> str:
        """解析文件并返回文本内容"""
        pass
    
    @abstractmethod
    def get_page_count(self, file_path: str) -> int:
        """获取文件页数"""
        pass
```

### 配置管理模式

```python
# SOURCE: pydantic v2 最佳实践
from pydantic import BaseModel
from typing import Optional

class TranslatorConfig(BaseModel):
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4"
    temperature: float = 0.3
    max_tokens: Optional[int] = None
```

### 日志模式

```python
# SOURCE: structlog 最佳实践
import structlog

logger = structlog.get_logger()
logger.info("translation_started", file="example.pdf", pages=100)
```

---

## Files to Change

| File | Action | Justification |
|------|--------|----------------|
| `requirements.txt` | CREATE | 项目依赖管理 |
| `pyproject.toml` | CREATE | 项目元数据和配置 |
| `.gitignore` | CREATE | Git 忽略文件 |
| `src/__init__.py` | CREATE | 源代码包初始化 |
| `src/parsers/__init__.py` | CREATE | 解析器包初始化 |
| `src/parsers/base.py` | CREATE | 基础解析器抽象类 |
| `src/translators/__init__.py` | CREATE | 翻译器包初始化 |
| `src/translators/base.py` | CREATE | 基础翻译器抽象类 |
| `src/evaluators/__init__.py` | CREATE | 评估器包初始化 |
| `src/evaluators/base.py` | CREATE | 基础评估器抽象类 |
| `src/config.py` | CREATE | 配置加载和管理 |
| `src/utils/__init__.py` | CREATE | 工具包初始化 |
| `src/utils/logger.py` | CREATE | 日志系统 |
| `src/utils/exceptions.py` | CREATE | 自定义异常类 |
| `src/utils/error_handler.py` | CREATE | 错误处理器 |
| `config/default.yaml` | CREATE | 默认配置文件 |
| `tests/__init__.py` | CREATE | 测试包初始化 |
| `tests/test_config.py` | CREATE | 配置测试 |
| `tests/test_parsers.py` | CREATE | 解析器测试 |
| `tests/test_translators.py` | CREATE | 翻译器测试 |
| `tests/test_evaluators.py` | CREATE | 评估器测试 |

## NOT Building

- 具体文件格式解析器的实现（TXT, MD, PDF, DOCX, EPUB）- 这些在后续阶段实现
- 具体翻译服务的实现（OpenAI, DeepL 等）- 这些在后续阶段实现
- 具体质量评估的实现 - 这些在后续阶段实现
- SKILL 元数据文件 - 在 Phase 10 实现

---

## Step-by-Step Tasks

### Task 1: 创建项目基础结构和依赖管理

- **ACTION**: 创建项目目录结构和依赖管理文件
- **IMPLEMENT**:
  ```bash
  # 创建目录结构
  mkdir -p src/parsers src/translators src/evaluators src/utils config tests
  touch src/__init__.py src/parsers/__init__.py src/translators/__init__.py src/evaluators/__init__.py src/utils/__init__.py tests/__init__.py
  ```
  
  创建 `requirements.txt`:
  ```
  pdfplumber>=0.11.0
  pypdf>=3.0.0
  python-docx>=0.8.11
  ebooklib>=0.17
  requests>=2.31.0
  pydantic>=2.0.0
  structlog>=23.3.0
  PyYAML>=6.0
  ```
  
  创建 `pyproject.toml`:
  ```toml
  [project]
  name = "any-file-translator"
  version = "0.1.0"
  description = "Multi-format document translation skill for AI Coding IDE"
  requires-python = ">=3.8"
  dependencies = [
      "pdfplumber>=0.11.0",
      "pypdf>=3.0.0",
      "python-docx>=0.8.11",
      "ebooklib>=0.17",
      "requests>=2.31.0",
      "pydantic>=2.0.0",
      "structlog>=23.3.0",
      "PyYAML>=6.0",
  ]
  ```
  
  创建 `.gitignore`:
  ```
  __pycache__/
  *.py[cod]
  *$py.class
  *.so
  .Python
  build/
  dist/
  *.egg-info/
  .venv/
  venv/
  .env
  *.log
  .pytest_cache/
  htmlcov/
  .coverage
  output/
  data/
  ```

- **MIRROR**: 标准 Python 项目结构
- **IMPORTS**: 无
- **GOTCHA**: 确保 Python 版本 >= 3.8
- **VALIDATE**:
  ```bash
  ls -la src/ tests/ config/
  cat requirements.txt
  ```

### Task 2: 实现配置管理系统

- **ACTION**: 创建配置管理系统，支持从 YAML 文件和环境变量加载配置
- **IMPLEMENT**:
  创建 `src/config.py`:
  ```python
  """配置管理模块"""
  from pathlib import Path
  from typing import Optional, List
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
      # 默认配置
      config = Config()
      
      # 如果提供了配置文件，从文件加载
      if config_path and Path(config_path).exists():
          with open(config_path, 'r') as f:
              config_data = yaml.safe_load(f)
              if config_data:
                  # 从字典创建配置对象
                  config = Config(**config_data)
      
      # 从环境变量覆盖配置
      if api_key := os.getenv("TRANSLATOR_API_KEY"):
          config.translator.api_key = api_key
      if base_url := os.getenv("TRANSLATOR_BASE_URL"):
          config.translator.base_url = base_url
      if model := os.getenv("TRANSLATOR_MODEL"):
          config.translator.model = model
      
      return config
  ```
  
  创建 `config/default.yaml`:
  ```yaml
  translator:
    api_key: ""
    base_url: "https://api.openai.com/v1"
    model: "gpt-4"
    temperature: 0.3
    timeout: 60
    max_retries: 3
  
  processing:
    chunk_size: 15
    max_parallel: 4
    cache_enabled: true
    cache_dir: ".cache"
  
  output:
    output_dir: "output"
    default_format: "markdown"
    bilingual: false
  ```

- **MIRROR**: pydantic v2 最佳实践
- **IMPORTS**: pydantic, yaml, os, pathlib
- **GOTCHA**: 
  - 环境变量优先级高于配置文件
  - 配置值需要合理的默认值
- **VALIDATE**:
  ```python
  from src.config import load_config
  config = load_config()
  print(config.translator.model)  # 应输出 "gpt-4"
  ```

### Task 3: 实现日志和错误处理系统

- **ACTION**: 创建日志系统和自定义异常类
- **IMPLEMENT**:
  创建 `src/utils/exceptions.py`:
  ```python
  """自定义异常类"""
  
  class TranslationError(Exception):
      """翻译错误基类"""
      pass
  
  class FileProcessingError(TranslationError):
      """文件处理错误"""
      pass
  
  class APIError(TranslationError):
      """API 调用错误"""
      def __init__(self, message: str, status_code: int = None):
          super().__init__(message)
          self.status_code = status_code
  
  class ConfigurationError(TranslationError):
      """配置错误"""
      pass
  
  class UnsupportedFormatError(FileProcessingError):
      """不支持的文件格式"""
      pass
  
  class QualityEvaluationError(TranslationError):
      """质量评估错误"""
      pass
  ```
  
  创建 `src/utils/logger.py`:
  ```python
  """日志系统"""
  import structlog
  import logging
  import sys
  from pathlib import Path
  
  def setup_logger(log_level: str = "INFO", log_file: str = None):
      """配置日志系统"""
      # 配置标准日志
      logging.basicConfig(
          format="%(message)s",
          stream=sys.stdout,
          level=getattr(logging, log_level.upper()),
      )
      
      # 配置 structlog
      processors = [
          structlog.stdlib.add_log_level,
          structlog.stdlib.add_logger_name,
          structlog.processors.TimeStamper(fmt="iso"),
          structlog.processors.StackInfoRenderer(),
          structlog.processors.format_exc_info,
          structlog.processors.JSONRenderer() if not log_file else structlog.dev.ConsoleRenderer(),
      ]
      
      structlog.configure(
          processors=processors,
          context_class=dict,
          logger_factory=structlog.stdlib.LoggerFactory(),
          cache_logger_on_first_use=True,
      )
  
  def get_logger(name: str = None):
      """获取日志记录器"""
      return structlog.get_logger(name)
  ```
  
  创建 `src/utils/error_handler.py`:
  ```python
  """错误处理器"""
  import time
  import functools
  from typing import Callable, Any
  from src.utils.logger import get_logger
  from src.utils.exceptions import APIError
  
  logger = get_logger(__name__)
  
  def retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
      """重试装饰器"""
      def decorator(func: Callable) -> Callable:
          @functools.wraps(func)
          def wrapper(*args, **kwargs) -> Any:
              retries = 0
              current_delay = delay
              
              while retries < max_retries:
                  try:
                      return func(*args, **kwargs)
                  except Exception as e:
                      retries += 1
                      if retries >= max_retries:
                          logger.error(
                              "max_retries_exceeded",
                              function=func.__name__,
                              error=str(e)
                          )
                          raise
                      
                      logger.warning(
                          "retry_attempt",
                          function=func.__name__,
                          attempt=retries,
                          max_retries=max_retries,
                          error=str(e),
                          delay=current_delay
                      )
                      time.sleep(current_delay)
                      current_delay *= backoff
              
              return func(*args, **kwargs)
          
          return wrapper
      return decorator
  ```

- **MIRROR**: structlog 最佳实践，Python 异常处理惯例
- **IMPORTS**: structlog, logging, functools, time
- **GOTCHA**:
  - 异常类需要继承层次结构
  - 重试装饰器需要处理所有异常
- **VALIDATE**:
  ```python
  from src.utils.logger import get_logger
  from src.utils.exceptions import TranslationError
  logger = get_logger(__name__)
  logger.info("test", message="Hello")
  ```

### Task 4: 实现基础解析器抽象层

- **ACTION**: 创建文件解析器抽象基类和注册机制
- **IMPLEMENT**:
  创建 `src/parsers/base.py`:
  ```python
  """基础解析器抽象层"""
  from abc import ABC, abstractmethod
  from dataclasses import dataclass
  from typing import Optional, List, Dict, Any
  from pathlib import Path
  
  @dataclass
  class ParseResult:
      """解析结果"""
      text: str
      page_count: int
      metadata: Dict[str, Any]
      format_type: str
  
  @dataclass
  class Chapter:
      """章节信息"""
      title: str
      start_page: int
      end_page: int
      level: int = 1
  
  class BaseParser(ABC):
      """文件解析器基类"""
      
      # 支持的文件扩展名
      supported_extensions: List[str] = []
      
      def __init__(self):
          self.logger = None  # 将在子类中初始化
      
      @abstractmethod
      def parse(self, file_path: str) -> ParseResult:
          """解析文件并返回文本内容"""
          pass
      
      @abstractmethod
      def get_page_count(self, file_path: str) -> int:
          """获取文件页数"""
          pass
      
      def can_parse(self, file_path: str) -> bool:
          """检查是否支持该文件"""
          ext = Path(file_path).suffix.lower()
          return ext in self.supported_extensions
      
      def extract_chapters(self, file_path: str) -> List[Chapter]:
          """提取章节信息（可选实现）"""
          return []
      
      def get_metadata(self, file_path: str) -> Dict[str, Any]:
          """获取文件元数据（可选实现）"""
          return {}
  ```
  
  创建 `src/parsers/__init__.py`:
  ```python
  """解析器模块"""
  from src.parsers.base import BaseParser, ParseResult, Chapter
  
  # 解析器注册表
  _parsers: Dict[str, BaseParser] = {}
  
  def register_parser(extensions: List[str], parser: BaseParser):
      """注册解析器"""
      for ext in extensions:
          _parsers[ext] = parser
  
  def get_parser(file_path: str) -> BaseParser:
      """获取适合文件的解析器"""
      from pathlib import Path
      ext = Path(file_path).suffix.lower()
      
      if ext not in _parsers:
          from src.utils.exceptions import UnsupportedFormatError
          raise UnsupportedFormatError(f"Unsupported file format: {ext}")
      
      return _parsers[ext]
  
  def list_supported_formats() -> List[str]:
      """列出所有支持的文件格式"""
      return list(_parsers.keys())
  
  __all__ = [
      'BaseParser',
      'ParseResult', 
      'Chapter',
      'register_parser',
      'get_parser',
      'list_supported_formats',
  ]
  ```

- **MIRROR**: Python ABC 最佳实践
- **IMPORTS**: abc, dataclasses, typing, pathlib
- **GOTCHA**:
  - 每个具体解析器需要继承 BaseParser
  - 需要在具体解析器中调用 register_parser 注册
- **VALIDATE**:
  ```python
  from src.parsers.base import BaseParser, ParseResult
  print(BaseParser.__abstractmethods__)  # 应显示抽象方法
  ```

### Task 5: 实现基础翻译器抽象层

- **ACTION**: 创建翻译服务抽象基类和注册机制
- **IMPLEMENT**:
  创建 `src/translators/base.py`:
  ```python
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
      usage: Dict[str, int]  # token 使用量
      metadata: Dict[str, Any]
  
  @dataclass
  class TranslationRequest:
      """翻译请求"""
      text: str
      source_language: str = "auto"
      target_language: str = "zh"
      context: Optional[str] = None  # 上下文，用于提高翻译质量
  
  class BaseTranslator(ABC):
      """翻译器基类"""
      
      # 翻译器名称
      name: str = "base"
      
      # 支持的语言
      supported_languages: List[str] = []
      
      def __init__(self, config: Dict[str, Any] = None):
          self.config = config or {}
          self.logger = None  # 将在子类中初始化
      
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
              return True  # 支持所有语言
          return language in self.supported_languages
      
      def detect_language(self, text: str) -> str:
          """检测语言（可选实现）"""
          return "auto"
  ```
  
  创建 `src/translators/__init__.py`:
  ```python
  """翻译器模块"""
  from src.translators.base import BaseTranslator, TranslationResult, TranslationRequest
  
  # 翻译器注册表
  _translators: Dict[str, BaseTranslator] = {}
  _default_translator: Optional[str] = None
  
  def register_translator(name: str, translator: BaseTranslator, set_default: bool = False):
      """注册翻译器"""
      _translators[name] = translator
      if set_default or not _default_translator:
          global _default_translator
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
  ```

- **MIRROR**: Python ABC 最佳实践
- **IMPORTS**: abc, dataclasses, typing
- **GOTCHA**:
  - 每个具体翻译器需要继承 BaseTranslator
  - 需要在具体翻译器中调用 register_translator 注册
- **VALIDATE**:
  ```python
  from src.translators.base import BaseTranslator, TranslationRequest
  print(BaseTranslator.__abstractmethods__)  # 应显示抽象方法
  ```

### Task 6: 实现基础评估器抽象层

- **ACTION**: 创建质量评估器抽象基类和注册机制
- **IMPLEMENT**:
  创建 `src/evaluators/base.py`:
  ```python
  """基础评估器抽象层"""
  from abc import ABC, abstractmethod
  from dataclasses import dataclass
  from typing import Dict, List, Optional, Any
  
  @dataclass
  class EvaluationResult:
      """评估结果"""
      overall_score: float  # 0-100
      fluency_score: float  # 流畅度 0-100
      accuracy_score: float  # 准确性 0-100
      format_score: float  # 格式保持度 0-100
      completeness_score: float  # 完整性 0-100
      human_score: float  # 人味评分 0-100
      issues: List[str]  # 发现的问题
      suggestions: List[str]  # 改进建议
      metadata: Dict[str, Any]
  
  @dataclass
  class EvaluationRequest:
      """评估请求"""
      original_text: str
      translated_text: str
      source_language: str
      target_language: str
      context: Optional[str] = None
  
  class BaseEvaluator(ABC):
      """评估器基类"""
      
      # 评估器名称
      name: str = "base"
      
      # 评估维度
      evaluation_dimensions: List[str] = ["fluency", "accuracy", "format", "completeness", "human"]
      
      def __init__(self, config: Dict[str, Any] = None):
          self.config = config or {}
          self.logger = None  # 将在子类中初始化
      
      @abstractmethod
      def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
          """评估翻译质量"""
          pass
      
      @abstractmethod
      def evaluate_batch(self, requests: List[EvaluationRequest]) -> List[EvaluationResult]:
          """批量评估"""
          pass
      
      def get_dimension_score(self, dimension: str, request: EvaluationRequest) -> float:
          """获取单个维度的分数（可选实现）"""
          return 0.0
      
      def generate_suggestions(self, result: EvaluationResult) -> List[str]:
          """生成改进建议"""
          suggestions = []
          
          if result.fluency_score < 70:
              suggestions.append("翻译流畅度较低，建议检查语句通顺度")
          if result.accuracy_score < 70:
              suggestions.append("翻译准确性较低，建议检查专业术语翻译")
          if result.format_score < 70:
              suggestions.append("格式保持度较低，建议检查原文格式是否丢失")
          if result.completeness_score < 70:
              suggestions.append("翻译完整性较低，建议检查是否有遗漏内容")
          if result.human_score < 70:
              suggestions.append("人味评分较低，建议使翻译更加自然")
          
          return suggestions
  ```
  
  创建 `src/evaluators/__init__.py`:
  ```python
  """评估器模块"""
  from src.evaluators.base import BaseEvaluator, EvaluationResult, EvaluationRequest
  
  # 评估器注册表
  _evaluators: Dict[str, BaseEvaluator] = {}
  _default_evaluator: Optional[str] = None
  
  def register_evaluator(name: str, evaluator: BaseEvaluator, set_default: bool = False):
      """注册评估器"""
      _evaluators[name] = evaluator
      if set_default or not _default_evaluator:
          global _default_evaluator
          _default_evaluator = name
  
  def get_evaluator(name: str = None) -> BaseEvaluator:
      """获取评估器"""
      if name is None:
          name = _default_evaluator
      
      if name not in _evaluators:
          from src.utils.exceptions import ConfigurationError
          raise ConfigurationError(f"Evaluator not found: {name}")
      
      return _evaluators[name]
  
  def list_evaluators() -> List[str]:
      """列出所有注册的评估器"""
      return list(_evaluators.keys())
  
  def set_default_evaluator(name: str):
      """设置默认评估器"""
      global _default_evaluator
      if name not in _evaluators:
          from src.utils.exceptions import ConfigurationError
          raise ConfigurationError(f"Evaluator not found: {name}")
      _default_evaluator = name
  
  __all__ = [
      'BaseEvaluator',
      'EvaluationResult',
      'EvaluationRequest',
      'register_evaluator',
      'get_evaluator',
      'list_evaluators',
      'set_default_evaluator',
  ]
  ```

- **MIRROR**: Python ABC 最佳实践
- **IMPORTS**: abc, dataclasses, typing
- **GOTCHA**:
  - 每个具体评估器需要继承 BaseEvaluator
  - 需要在具体评估器中调用 register_evaluator 注册
- **VALIDATE**:
  ```python
  from src.evaluators.base import BaseEvaluator, EvaluationRequest
  print(BaseEvaluator.__abstractmethods__)  # 应显示抽象方法
  ```

### Task 7: 创建单元测试

- **ACTION**: 为配置管理、解析器抽象层、翻译器抽象层、评估器抽象层编写单元测试
- **IMPLEMENT**:
  创建 `tests/test_config.py`:
  ```python
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
  ```
  
  创建 `tests/test_parsers.py`:
  ```python
  """解析器测试"""
  import pytest
  from src.parsers.base import BaseParser, ParseResult, Chapter
  from src.utils.exceptions import UnsupportedFormatError
  
  class MockParser(BaseParser):
      """模拟解析器"""
      supported_extensions = [".txt"]
      
      def parse(self, file_path: str) -> ParseResult:
          return ParseResult(
              text="test content",
              page_count=1,
              metadata={},
              format_type="txt"
          )
      
      def get_page_count(self, file_path: str) -> int:
          return 1
  
  def test_parser_registration():
      """测试解析器注册"""
      from src.parsers import register_parser, get_parser
      
      parser = MockParser()
      register_parser([".txt"], parser)
      
      # 注意：这里只是测试注册机制，实际文件解析需要具体实现
      assert parser.can_parse("test.txt")
      assert not parser.can_parse("test.pdf")
  ```
  
  创建 `tests/test_translators.py`:
  ```python
  """翻译器测试"""
  import pytest
  from src.translators.base import BaseTranslator, TranslationRequest, TranslationResult
  from src.utils.exceptions import ConfigurationError
  
  class MockTranslator(BaseTranslator):
      """模拟翻译器"""
      name = "mock"
      supported_languages = ["en", "zh"]
      
      def translate(self, request: TranslationRequest) -> TranslationResult:
          return TranslationResult(
              text=f"translated: {request.text}",
              source_language=request.source_language,
              target_language=request.target_language,
              model="mock-model",
              usage={"prompt_tokens": 10, "completion_tokens": 10},
              metadata={}
          )
      
      def translate_batch(self, requests: list[TranslationRequest]) -> list[TranslationResult]:
          return [self.translate(req) for req in requests]
  
  def test_translator_registration():
      """测试翻译器注册"""
      from src.translators import register_translator, get_translator
      
      translator = MockTranslator()
      register_translator("mock", translator, set_default=True)
      
      retrieved = get_translator("mock")
      assert retrieved.name == "mock"
      
      default = get_translator()
      assert default.name == "mock"
  ```
  
  创建 `tests/test_evaluators.py`:
  ```python
  """评估器测试"""
  import pytest
  from src.evaluators.base import BaseEvaluator, EvaluationRequest, EvaluationResult
  
  class MockEvaluator(BaseEvaluator):
      """模拟评估器"""
      name = "mock"
      
      def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
          return EvaluationResult(
              overall_score=85.0,
              fluency_score=90.0,
              accuracy_score=85.0,
              format_score=80.0,
              completeness_score=85.0,
              human_score=85.0,
              issues=[],
              suggestions=[],
              metadata={}
          )
      
      def evaluate_batch(self, requests: list[EvaluationRequest]) -> list[EvaluationResult]:
          return [self.evaluate(req) for req in requests]
  
  def test_evaluator_registration():
      """测试评估器注册"""
      from src.evaluators import register_evaluator, get_evaluator
      
      evaluator = MockEvaluator()
      register_evaluator("mock", evaluator, set_default=True)
      
      retrieved = get_evaluator("mock")
      assert retrieved.name == "mock"
      
      default = get_evaluator()
      assert default.name == "mock"
  
  def test_generate_suggestions():
      """测试生成改进建议"""
      evaluator = MockEvaluator()
      
      result = EvaluationResult(
          overall_score=50.0,
          fluency_score=60.0,
          accuracy_score=60.0,
          format_score=60.0,
          completeness_score=60.0,
          human_score=60.0,
          issues=[],
          suggestions=[],
          metadata={}
      )
      
      suggestions = evaluator.generate_suggestions(result)
      assert len(suggestions) > 0
  ```

- **MIRROR**: pytest 最佳实践
- **IMPORTS**: pytest
- **GOTCHA**:
  - 测试需要覆盖所有抽象方法
  - Mock 类需要实现所有抽象方法
- **VALIDATE**:
  ```bash
  python -m pytest tests/ -v
  ```

---

## Testing Strategy

### Unit Tests

| Test | Input | Expected Output | Edge Case? |
|------|-------|-----------------|------------|
| test_default_config | 无 | 默认配置值正确 | 是 |
| test_translator_settings | 自定义设置 | 配置覆盖默认值 | 是 |
| test_load_config_from_dict | 字典 | 配置对象正确创建 | 是 |
| test_parser_registration | 解析器实例 | 注册成功，可检索 | 是 |
| test_translator_registration | 翻译器实例 | 注册成功，可检索 | 是 |
| test_evaluator_registration | 评估器实例 | 注册成功，可检索 | 是 |
| test_generate_suggestions | 低分评估结果 | 生成改进建议 | 是 |

### Edge Cases Checklist

- [x] 空配置
- [x] 无效的配置值
- [x] 不支持的文件格式
- [x] 未注册的解析器
- [x] 未注册的翻译器
- [x] 未注册的评估器

---

## Validation Commands

### 安装依赖
```bash
pip install -r requirements.txt
```
EXPECT: 所有依赖安装成功

### 类型检查
```bash
python -m mypy src/ --ignore-missing-imports
```
EXPECT: 无类型错误

### 单元测试
```bash
python -m pytest tests/ -v
```
EXPECT: 所有测试通过

### 导入测试
```bash
python -c "from src.parsers import get_parser; from src.translators import get_translator; from src.evaluators import get_evaluator; print('All imports successful')"
```
EXPECT: 所有模块导入成功

---

## Acceptance Criteria

- [ ] 项目结构创建完成
- [ ] 依赖管理文件创建完成
- [ ] 配置管理系统实现并测试通过
- [ ] 日志系统实现
- [ ] 自定义异常类实现
- [ ] 错误处理器实现
- [ ] 基础解析器抽象层实现并测试通过
- [ ] 基础翻译器抽象层实现并测试通过
- [ ] 基础评估器抽象层实现并测试通过
- [ ] 所有单元测试通过

---

## Completion Checklist

- [x] 代码遵循 Python 最佳实践
- [x] 错误处理遵循约定
- [x] 日志遵循 structlog 最佳实践
- [x] 测试遵循 pytest 模式
- [x] 无硬编码值
- [x] 无不必要的范围添加

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| 依赖库版本冲突 | 中 | 中 | 使用版本范围指定兼容版本 |
| 抽象层设计不合理 | 低 | 高 | 预留扩展接口，保持简单 |
| 测试覆盖不足 | 中 | 中 | 添加更多单元测试 |

---

## Notes

- Phase 1 是整个系统的基础，需要确保抽象层设计合理
- 所有抽象类都预留了扩展接口，具体实现将在后续阶段完成
- 使用注册机制实现插件式架构，便于添加新的文件格式、翻译服务和评估器
- MVP 阶段只实现 OpenAI 兼容接口，其他翻译服务将在后续阶段添加
