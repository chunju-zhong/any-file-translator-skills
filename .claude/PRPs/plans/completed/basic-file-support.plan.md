# Plan: Basic File Support - Phase 2

## Summary

实现最基础的文件格式支持，包括 .txt 和 .md 文件的读取、翻译和输出，以及直接文本输入处理。这是验证核心流程的关键阶段，将打通从文件输入到翻译输出的完整链路。

## User Story

作为用户，我希望能够翻译简单的文本文件和 Markdown 文档，这样我就能快速验证翻译功能是否正常工作，而不需要等待复杂文件格式的支持。

## Problem → Solution

当前状态：基础架构已完成，但无法处理任何实际文件
期望状态：能够翻译 .txt 和 .md 文件，输出翻译结果和质量评分

## Metadata

- **Complexity**: Medium
- **Source PRD**: `.claude/PRPs/prds/any-file-translator.prd.md`
- **PRD Phase**: Phase 2: Basic File Support
- **Estimated Files**: 8-10 个文件

---

## UX Design

### Before
```
┌─────────────────────────────────────────┐
│  基础架构完成，但无实际功能                │
│  - 无法处理任何文件                       │
│  - 无法进行翻译                          │
│  - 无法评估翻译质量                       │
└─────────────────────────────────────────┘
```

### After
```
┌─────────────────────────────────────────┐
│  基础文件翻译功能可用                     │
│  - 支持 .txt 和 .md 文件                 │
│  - 支持直接文本输入                       │
│  - 输出翻译结果和质量评分                 │
└─────────────────────────────────────────┘
```

### Interaction Changes

| Touchpoint | Before | After | Notes |
|------------|--------|-------|-------|
| 文件输入 | 不支持 | 支持 .txt 和 .md | 基础文件格式 |
| 文本输入 | 不支持 | 支持直接输入 | 快速测试 |
| 翻译输出 | 无 | Markdown 格式 | 简单输出 |
| 质量评估 | 无 | 完整性检查 | 基础评估 |

---

## Mandatory Reading

| Priority | File | Lines | Why |
|----------|------|-------|-----|
| P0 | `src/parsers/base.py` | all | 解析器基类模式 |
| P0 | `src/translators/base.py` | all | 翻译器基类模式 |
| P0 | `src/evaluators/base.py` | all | 评估器基类模式 |
| P1 | `src/config.py` | all | 配置管理模式 |
| P1 | `src/utils/logger.py` | all | 日志模式 |
| P1 | `src/utils/exceptions.py` | all | 异常处理模式 |
| P2 | `tests/test_parsers.py` | all | 测试模式 |

## External Documentation

| Topic | Source | Key Takeaway |
|-------|--------|--------------|
| OpenAI API | OpenAI 官方文档 | Chat Completion API 使用方法 |
| Python file I/O | Python 官方文档 | 文件读写最佳实践 |
| Markdown 格式 | CommonMark 规范 | Markdown 标准语法 |

---

## Patterns to Mirror

### 解析器模式

```python
// SOURCE: src/parsers/base.py
from src.parsers.base import BaseParser, ParseResult
from src.utils.logger import get_logger

class TxtParser(BaseParser):
    supported_extensions = [".txt"]
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
    
    def parse(self, file_path: str) -> ParseResult:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return ParseResult(
            text=text,
            page_count=1,
            metadata={"file_size": len(text)},
            format_type="txt"
        )
    
    def get_page_count(self, file_path: str) -> int:
        return 1
```

### 翻译器模式

```python
// SOURCE: src/translators/base.py
from src.translators.base import BaseTranslator, TranslationRequest, TranslationResult
from src.utils.logger import get_logger
from src.utils.error_handler import retry

class OpenAITranslator(BaseTranslator):
    name = "openai"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = get_logger(__name__)
    
    @retry(max_retries=3)
    def translate(self, request: TranslationRequest) -> TranslationResult:
        # 调用 OpenAI API
        pass
```

### 评估器模式

```python
// SOURCE: src/evaluators/base.py
from src.evaluators.base import BaseEvaluator, EvaluationRequest, EvaluationResult
from src.utils.logger import get_logger

class CompletenessEvaluator(BaseEvaluator):
    name = "completeness"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = get_logger(__name__)
    
    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        # 评估完整性
        pass
```

### 注册模式

```python
// SOURCE: src/parsers/__init__.py
from src.parsers import register_parser
from src.parsers.txt_parser import TxtParser

parser = TxtParser()
register_parser([".txt"], parser)
```

---

## Files to Change

| File | Action | Justification |
|------|--------|----------------|
| `src/parsers/txt_parser.py` | CREATE | TXT 文件解析器 |
| `src/parsers/md_parser.py` | CREATE | Markdown 文件解析器 |
| `src/translators/openai_translator.py` | CREATE | OpenAI API 翻译器 |
| `src/evaluators/completeness_evaluator.py` | CREATE | 完整性评估器 |
| `src/translator.py` | CREATE | 主翻译流程编排器 |
| `tests/test_txt_parser.py` | CREATE | TXT 解析器测试 |
| `tests/test_md_parser.py` | CREATE | Markdown 解析器测试 |
| `tests/test_openai_translator.py` | CREATE | OpenAI 翻译器测试 |
| `tests/test_completeness_evaluator.py` | CREATE | 完整性评估器测试 |
| `tests/test_translator.py` | CREATE | 主流程集成测试 |

## NOT Building

- PDF 文件处理 - Phase 3 实现
- DOCX 和 EPUB 文件处理 - Phase 4 实现
- 多翻译 API 支持 - Phase 8 实现
- 翻译质量评估系统（流畅度、准确性等） - Phase 5 实现
- 迭代改进机制 - Phase 6 实现
- 超大文件处理 - Phase 7 实现
- PDF 和 DOCX 输出 - Phase 9 实现

---

## Step-by-Step Tasks

### Task 1: 实现 TXT 文件解析器

- **ACTION**: 创建 TXT 文件解析器，继承 BaseParser 并实现所有抽象方法
- **IMPLEMENT**:
  创建 `src/parsers/txt_parser.py`:
  ```python
  """TXT 文件解析器"""
  from pathlib import Path
  from src.parsers.base import BaseParser, ParseResult
  from src.utils.logger import get_logger
  from src.utils.exceptions import FileProcessingError


  class TxtParser(BaseParser):
      """TXT 文件解析器"""
      
      supported_extensions = [".txt"]
      
      def __init__(self):
          super().__init__()
          self.logger = get_logger(__name__)
      
      def parse(self, file_path: str) -> ParseResult:
          """解析 TXT 文件"""
          try:
              path = Path(file_path)
              
              if not path.exists():
                  raise FileProcessingError(f"File not found: {file_path}")
              
              if not self.can_parse(file_path):
                  raise FileProcessingError(f"Unsupported file format: {file_path}")
              
              with open(path, 'r', encoding='utf-8') as f:
                  text = f.read()
              
              self.logger.info(
                  "txt_file_parsed",
                  file=str(path),
                  size=len(text)
              )
              
              return ParseResult(
                  text=text,
                  page_count=1,
                  metadata={
                      "file_size": len(text),
                      "file_name": path.name,
                  },
                  format_type="txt"
              )
          
          except UnicodeDecodeError as e:
              self.logger.error("txt_decode_error", file=file_path, error=str(e))
              raise FileProcessingError(f"Failed to decode file: {file_path}")
          
          except Exception as e:
              self.logger.error("txt_parse_error", file=file_path, error=str(e))
              raise FileProcessingError(f"Failed to parse TXT file: {e}")
      
      def get_page_count(self, file_path: str) -> int:
          """TXT 文件只有 1 页"""
          return 1
  ```
  
  更新 `src/parsers/__init__.py`:
  ```python
  """解析器模块"""
  from src.parsers.base import BaseParser, ParseResult, Chapter
  from src.parsers.txt_parser import TxtParser
  
  # 解析器注册表
  _parsers: Dict[str, BaseParser] = {}
  
  # 自动注册默认解析器
  _txt_parser = TxtParser()
  register_parser([".txt"], _txt_parser)
  
  # ... 其余代码保持不变
  ```

- **MIRROR**: src/parsers/base.py 的 BaseParser 模式
- **IMPORTS**: pathlib, src.parsers.base, src.utils.logger, src.utils.exceptions
- **GOTCHA**: 
  - 需要处理 UTF-8 编码错误
  - 需要检查文件是否存在
  - TXT 文件只有 1 页
- **VALIDATE**:
  ```python
  from src.parsers import get_parser
  parser = get_parser("test.txt")
  result = parser.parse("test.txt")
  assert result.format_type == "txt"
  ```

### Task 2: 实现 Markdown 文件解析器

- **ACTION**: 创建 Markdown 文件解析器，保留 Markdown 格式标记
- **IMPLEMENT**:
  创建 `src/parsers/md_parser.py`:
  ```python
  """Markdown 文件解析器"""
  from pathlib import Path
  from src.parsers.base import BaseParser, ParseResult
  from src.utils.logger import get_logger
  from src.utils.exceptions import FileProcessingError


  class MdParser(BaseParser):
      """Markdown 文件解析器"""
      
      supported_extensions = [".md", ".markdown"]
      
      def __init__(self):
          super().__init__()
          self.logger = get_logger(__name__)
      
      def parse(self, file_path: str) -> ParseResult:
          """解析 Markdown 文件，保留格式标记"""
          try:
              path = Path(file_path)
              
              if not path.exists():
                  raise FileProcessingError(f"File not found: {file_path}")
              
              if not self.can_parse(file_path):
                  raise FileProcessingError(f"Unsupported file format: {file_path}")
              
              with open(path, 'r', encoding='utf-8') as f:
                  text = f.read()
              
              # 提取 Markdown 元数据
              metadata = self._extract_metadata(text)
              
              self.logger.info(
                  "markdown_file_parsed",
                  file=str(path),
                  size=len(text),
                  has_frontmatter=metadata.get("has_frontmatter", False)
              )
              
              return ParseResult(
                  text=text,
                  page_count=1,
                  metadata={
                      "file_size": len(text),
                      "file_name": path.name,
                      **metadata
                  },
                  format_type="markdown"
              )
          
          except UnicodeDecodeError as e:
              self.logger.error("markdown_decode_error", file=file_path, error=str(e))
              raise FileProcessingError(f"Failed to decode file: {file_path}")
          
          except Exception as e:
              self.logger.error("markdown_parse_error", file=file_path, error=str(e))
              raise FileProcessingError(f"Failed to parse Markdown file: {e}")
      
      def get_page_count(self, file_path: str) -> int:
          """Markdown 文件只有 1 页"""
          return 1
      
      def _extract_metadata(self, text: str) -> dict:
          """提取 Markdown 元数据（如 YAML frontmatter）"""
          metadata = {}
          
          # 检查是否有 YAML frontmatter
          if text.startswith("---\n"):
              try:
                  end_index = text.index("---\n", 4)
                  frontmatter = text[4:end_index]
                  metadata["has_frontmatter"] = True
                  metadata["frontmatter_size"] = len(frontmatter)
              except ValueError:
                  metadata["has_frontmatter"] = False
          
          # 统计标题数量
          lines = text.split('\n')
          heading_count = sum(1 for line in lines if line.startswith('#'))
          metadata["heading_count"] = heading_count
          
          # 统计代码块数量
          code_block_count = text.count('```')
          metadata["code_block_count"] = code_block_count // 2
          
          return metadata
  ```
  
  更新 `src/parsers/__init__.py`:
  ```python
  from src.parsers.md_parser import MdParser
  
  # 自动注册 Markdown 解析器
  _md_parser = MdParser()
  register_parser([".md", ".markdown"], _md_parser)
  ```

- **MIRROR**: src/parsers/txt_parser.py 的模式
- **IMPORTS**: pathlib, src.parsers.base, src.utils.logger, src.utils.exceptions
- **GOTCHA**: 
  - 需要保留 Markdown 格式标记
  - 可以提取 frontmatter 元数据
  - Markdown 文件只有 1 页
- **VALIDATE**:
  ```python
  from src.parsers import get_parser
  parser = get_parser("test.md")
  result = parser.parse("test.md")
  assert result.format_type == "markdown"
  assert "heading_count" in result.metadata
  ```

### Task 3: 实现 OpenAI 翻译器

- **ACTION**: 创建 OpenAI API 翻译器，支持 OpenAI 兼容接口
- **IMPLEMENT**:
  创建 `src/translators/openai_translator.py`:
  ```python
  """OpenAI 兼容翻译器"""
  import requests
  from typing import Dict, Any
  from src.translators.base import BaseTranslator, TranslationRequest, TranslationResult
  from src.utils.logger import get_logger
  from src.utils.exceptions import APIError
  from src.utils.error_handler import retry


  class OpenAITranslator(BaseTranslator):
      """OpenAI 兼容翻译器（支持 OpenAI、Azure、本地模型等）"""
      
      name = "openai"
      supported_languages = []  # 支持所有语言
      
      def __init__(self, config: Dict[str, Any] = None):
          super().__init__(config)
          self.logger = get_logger(__name__)
          
          # 从配置获取参数
          self.api_key = self.config.get("api_key", "")
          self.base_url = self.config.get("base_url", "https://api.openai.com/v1")
          self.model = self.config.get("model", "gpt-4")
          self.temperature = self.config.get("temperature", 0.3)
          self.max_tokens = self.config.get("max_tokens")
          self.timeout = self.config.get("timeout", 60)
      
      @retry(max_retries=3, delay=1.0, backoff=2.0)
      def translate(self, request: TranslationRequest) -> TranslationResult:
          """翻译文本"""
          try:
              # 构建翻译提示词
              system_prompt = self._build_system_prompt(request)
              user_prompt = self._build_user_prompt(request)
              
              # 调用 API
              response = self._call_api(system_prompt, user_prompt)
              
              # 解析响应
              translated_text = response["choices"][0]["message"]["content"]
              usage = response.get("usage", {})
              
              self.logger.info(
                  "translation_completed",
                  model=self.model,
                  source_lang=request.source_language,
                  target_lang=request.target_language,
                  tokens_used=usage.get("total_tokens", 0)
              )
              
              return TranslationResult(
                  text=translated_text,
                  source_language=request.source_language,
                  target_language=request.target_language,
                  model=self.model,
                  usage=usage,
                  metadata={"api_response": response}
              )
          
          except requests.exceptions.Timeout:
              self.logger.error("api_timeout", timeout=self.timeout)
              raise APIError(f"API request timeout after {self.timeout}s")
          
          except requests.exceptions.RequestException as e:
              self.logger.error("api_request_error", error=str(e))
              raise APIError(f"API request failed: {e}")
          
          except (KeyError, IndexError) as e:
              self.logger.error("api_response_parse_error", error=str(e))
              raise APIError(f"Failed to parse API response: {e}")
      
      def translate_batch(self, requests: list) -> list:
          """批量翻译"""
          return [self.translate(req) for req in requests]
      
      def _build_system_prompt(self, request: TranslationRequest) -> str:
          """构建系统提示词"""
          return f"""You are a professional translator. Translate the following text from {request.source_language} to {request.target_language}.

Requirements:
1. Maintain the original meaning and tone
2. Use natural and fluent language
3. Preserve any formatting (Markdown, code blocks, etc.)
4. Keep proper nouns and technical terms accurate
5. Do not add any explanations or notes"""
      
      def _build_user_prompt(self, request: TranslationRequest) -> str:
          """构建用户提示词"""
          if request.context:
              return f"""Context: {request.context}

Text to translate:
{request.text}"""
          return request.text
      
      def _call_api(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
          """调用 OpenAI 兼容 API"""
          headers = {
              "Authorization": f"Bearer {self.api_key}",
              "Content-Type": "application/json"
          }
          
          data = {
              "model": self.model,
              "messages": [
                  {"role": "system", "content": system_prompt},
                  {"role": "user", "content": user_prompt}
              ],
              "temperature": self.temperature
          }
          
          if self.max_tokens:
              data["max_tokens"] = self.max_tokens
          
          response = requests.post(
              f"{self.base_url}/chat/completions",
              headers=headers,
              json=data,
              timeout=self.timeout
          )
          
          if response.status_code != 200:
              raise APIError(
                  f"API returned status {response.status_code}: {response.text}",
                  status_code=response.status_code
              )
          
          return response.json()
  ```
  
  更新 `src/translators/__init__.py`:
  ```python
  from src.translators.openai_translator import OpenAITranslator
  from src.config import load_config
  
  # 自动注册 OpenAI 翻译器
  config = load_config()
  _openai_translator = OpenAITranslator(config.translator.model_dump())
  register_translator("openai", _openai_translator, set_default=True)
  ```

- **MIRROR**: src/translators/base.py 的 BaseTranslator 模式
- **IMPORTS**: requests, src.translators.base, src.utils.logger, src.utils.exceptions, src.utils.error_handler
- **GOTCHA**: 
  - 需要处理 API 超时和错误
  - 需要使用 retry 装饰器处理重试
  - 需要构建合适的翻译提示词
  - 支持上下文信息
- **VALIDATE**:
  ```python
  from src.translators import get_translator
  translator = get_translator("openai")
  result = translator.translate(TranslationRequest(text="Hello"))
  assert result.text is not None
  ```

### Task 4: 实现完整性评估器

- **ACTION**: 创建完整性评估器，检查翻译是否完整
- **IMPLEMENT**:
  创建 `src/evaluators/completeness_evaluator.py`:
  ```python
  """完整性评估器"""
  from src.evaluators.base import BaseEvaluator, EvaluationRequest, EvaluationResult
  from src.utils.logger import get_logger


  class CompletenessEvaluator(BaseEvaluator):
      """完整性评估器"""
      
      name = "completeness"
      evaluation_dimensions = ["completeness"]
      
      def __init__(self, config: dict = None):
          super().__init__(config)
          self.logger = get_logger(__name__)
      
      def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
          """评估翻译完整性"""
          # 计算完整性分数
          completeness_score = self._calculate_completeness(
              request.original_text,
              request.translated_text
          )
          
          # 检测问题
          issues = self._detect_issues(
              request.original_text,
              request.translated_text
          )
          
          # 生成建议
          suggestions = []
          if completeness_score < 70:
              suggestions.append("翻译完整性较低，可能存在遗漏内容")
          
          self.logger.info(
              "completeness_evaluation_completed",
              score=completeness_score,
              issues_count=len(issues)
          )
          
          return EvaluationResult(
              overall_score=completeness_score,
              fluency_score=0.0,  # 不评估
              accuracy_score=0.0,  # 不评估
              format_score=0.0,  # 不评估
              completeness_score=completeness_score,
              human_score=0.0,  # 不评估
              issues=issues,
              suggestions=suggestions,
              metadata={
                  "original_length": len(request.original_text),
                  "translated_length": len(request.translated_text),
                  "length_ratio": len(request.translated_text) / max(len(request.original_text), 1)
              }
          )
      
      def evaluate_batch(self, requests: list) -> list:
          """批量评估"""
          return [self.evaluate(req) for req in requests]
      
      def _calculate_completeness(self, original: str, translated: str) -> float:
          """计算完整性分数"""
          # 基于长度比例
          length_ratio = len(translated) / max(len(original), 1)
          
          # 基于段落数量
          original_paragraphs = len([p for p in original.split('\n\n') if p.strip()])
          translated_paragraphs = len([p for p in translated.split('\n\n') if p.strip()])
          paragraph_ratio = translated_paragraphs / max(original_paragraphs, 1)
          
          # 基于句子数量（简单统计）
          original_sentences = len([s for s in original.split('。') if s.strip()])
          translated_sentences = len([s for s in translated.split('。') if s.strip()])
          sentence_ratio = translated_sentences / max(original_sentences, 1)
          
          # 综合评分
          score = (length_ratio * 0.4 + paragraph_ratio * 0.3 + sentence_ratio * 0.3) * 100
          
          # 限制在 0-100 之间
          return min(max(score, 0), 100)
      
      def _detect_issues(self, original: str, translated: str) -> list:
          """检测完整性问题"""
          issues = []
          
          # 检查长度差异
          length_ratio = len(translated) / max(len(original), 1)
          if length_ratio < 0.5:
              issues.append(f"翻译文本过短（长度比例: {length_ratio:.2f}）")
          elif length_ratio > 2.0:
              issues.append(f"翻译文本过长（长度比例: {length_ratio:.2f}）")
          
          # 检查段落差异
          original_paragraphs = len([p for p in original.split('\n\n') if p.strip()])
          translated_paragraphs = len([p for p in translated.split('\n\n') if p.strip()])
          if abs(original_paragraphs - translated_paragraphs) > 1:
              issues.append(f"段落数量不匹配（原文: {original_paragraphs}, 译文: {translated_paragraphs}）")
          
          # 检查是否为空
          if not translated.strip():
              issues.append("翻译文本为空")
          
          return issues
  ```
  
  更新 `src/evaluators/__init__.py`:
  ```python
  from src.evaluators.completeness_evaluator import CompletenessEvaluator
  
  # 自动注册完整性评估器
  _completeness_evaluator = CompletenessEvaluator()
  register_evaluator("completeness", _completeness_evaluator, set_default=True)
  ```

- **MIRROR**: src/evaluators/base.py 的 BaseEvaluator 模式
- **IMPORTS**: src.evaluators.base, src.utils.logger
- **GOTCHA**: 
  - 只评估完整性，其他维度返回 0
  - 需要考虑不同语言的长度差异
  - 需要检测明显的遗漏问题
- **VALIDATE**:
  ```python
  from src.evaluators import get_evaluator
  evaluator = get_evaluator("completeness")
  result = evaluator.evaluate(EvaluationRequest(
      original_text="Hello",
      translated_text="你好"
  ))
  assert result.completeness_score > 0
  ```

### Task 5: 实现主翻译流程编排器

- **ACTION**: 创建主翻译流程编排器，整合解析、翻译、评估
- **IMPLEMENT**:
  创建 `src/translator.py`:
  ```python
  """主翻译流程编排器"""
  from pathlib import Path
  from typing import Optional
  from src.parsers import get_parser, list_supported_formats
  from src.translators import get_translator
  from src.evaluators import get_evaluator
  from src.config import load_config
  from src.utils.logger import get_logger, setup_logger
  from src.utils.exceptions import TranslationError, UnsupportedFormatError


  class Translator:
      """主翻译器"""
      
      def __init__(self, config_path: Optional[str] = None):
          """初始化翻译器"""
          # 加载配置
          self.config = load_config(config_path)
          
          # 设置日志
          setup_logger(log_level="INFO")
          self.logger = get_logger(__name__)
          
          # 初始化组件
          self.parser = None
          self.translator = get_translator()
          self.evaluator = get_evaluator()
      
      def translate_file(
          self,
          file_path: str,
          source_language: str = "auto",
          target_language: str = "zh",
          output_path: Optional[str] = None
      ) -> dict:
          """翻译文件"""
          try:
              # 获取适合的解析器
              self.parser = get_parser(file_path)
              
              self.logger.info(
                  "translation_started",
                  file=file_path,
                  source_lang=source_language,
                  target_lang=target_language
              )
              
              # 解析文件
              parse_result = self.parser.parse(file_path)
              self.logger.info("file_parsed", format=parse_result.format_type)
              
              # 翻译文本
              from src.translators.base import TranslationRequest
              translation_request = TranslationRequest(
                  text=parse_result.text,
                  source_language=source_language,
                  target_language=target_language
              )
              translation_result = self.translator.translate(translation_request)
              self.logger.info("text_translated", tokens=translation_result.usage.get("total_tokens", 0))
              
              # 评估翻译质量
              from src.evaluators.base import EvaluationRequest
              evaluation_request = EvaluationRequest(
                  original_text=parse_result.text,
                  translated_text=translation_result.text,
                  source_language=source_language,
                  target_language=target_language
              )
              evaluation_result = self.evaluator.evaluate(evaluation_request)
              self.logger.info("quality_evaluated", score=evaluation_result.overall_score)
              
              # 输出结果
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
              
              # 翻译文本
              from src.translators.base import TranslationRequest
              translation_request = TranslationRequest(
                  text=text,
                  source_language=source_language,
                  target_language=target_language
              )
              translation_result = self.translator.translate(translation_request)
              
              # 评估翻译质量
              from src.evaluators.base import EvaluationRequest
              evaluation_request = EvaluationRequest(
                  original_text=text,
                  translated_text=translation_result.text,
                  source_language=source_language,
                  target_language=target_language
              )
              evaluation_result = self.evaluator.evaluate(evaluation_request)
              
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
  ```

- **MIRROR**: 整合所有模块的模式
- **IMPORTS**: src.parsers, src.translators, src.evaluators, src.config, src.utils
- **GOTCHA**: 
  - 需要处理所有异常
  - 需要记录详细的日志
  - 需要返回完整的结果信息
- **VALIDATE**:
  ```python
  from src.translator import Translator
  translator = Translator()
  result = translator.translate_text("Hello")
  assert result["translated_text"] is not None
  ```

### Task 6: 创建单元测试

- **ACTION**: 为所有新模块创建单元测试
- **IMPLEMENT**:
  创建 `tests/test_txt_parser.py`:
  ```python
  """TXT 解析器测试"""
  import pytest
  import tempfile
  from pathlib import Path
  from src.parsers.txt_parser import TxtParser
  from src.utils.exceptions import FileProcessingError


  def test_txt_parser_can_parse():
      """测试 TXT 解析器支持检查"""
      parser = TxtParser()
      assert parser.can_parse("test.txt")
      assert not parser.can_parse("test.pdf")


  def test_txt_parser_parse():
      """测试 TXT 解析器解析"""
      parser = TxtParser()
      
      # 创建临时文件
      with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
          f.write("Hello, World!")
          temp_file = f.name
      
      try:
          result = parser.parse(temp_file)
          assert result.text == "Hello, World!"
          assert result.page_count == 1
          assert result.format_type == "txt"
          assert "file_size" in result.metadata
      finally:
          Path(temp_file).unlink()


  def test_txt_parser_file_not_found():
      """测试文件不存在错误"""
      parser = TxtParser()
      
      with pytest.raises(FileProcessingError):
          parser.parse("nonexistent.txt")
  ```
  
  创建 `tests/test_md_parser.py`:
  ```python
  """Markdown 解析器测试"""
  import pytest
  import tempfile
  from pathlib import Path
  from src.parsers.md_parser import MdParser


  def test_md_parser_can_parse():
      """测试 Markdown 解析器支持检查"""
      parser = MdParser()
      assert parser.can_parse("test.md")
      assert parser.can_parse("test.markdown")
      assert not parser.can_parse("test.txt")


  def test_md_parser_parse():
      """测试 Markdown 解析器解析"""
      parser = MdParser()
      
      markdown_content = """# Title

This is a paragraph.

## Section

- Item 1
- Item 2

```python
print("Hello")
```
"""
      
      with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
          f.write(markdown_content)
          temp_file = f.name
      
      try:
          result = parser.parse(temp_file)
          assert result.text == markdown_content
          assert result.page_count == 1
          assert result.format_type == "markdown"
          assert result.metadata["heading_count"] == 2
          assert result.metadata["code_block_count"] == 1
      finally:
          Path(temp_file).unlink()
  ```
  
  创建 `tests/test_openai_translator.py`:
  ```python
  """OpenAI 翻译器测试"""
  import pytest
  from unittest.mock import Mock, patch
  from src.translators.openai_translator import OpenAITranslator
  from src.translators.base import TranslationRequest
  from src.utils.exceptions import APIError


  def test_openai_translator_translate():
      """测试 OpenAI 翻译器翻译"""
      translator = OpenAITranslator({
          "api_key": "test-key",
          "model": "gpt-4"
      })
      
      # Mock API 响应
      with patch('requests.post') as mock_post:
          mock_response = Mock()
          mock_response.status_code = 200
          mock_response.json.return_value = {
              "choices": [{
                  "message": {
                      "content": "你好"
                  }
              }],
              "usage": {
                  "prompt_tokens": 10,
                  "completion_tokens": 5,
                  "total_tokens": 15
              }
          }
          mock_post.return_value = mock_response
        
          request = TranslationRequest(
              text="Hello",
              source_language="en",
              target_language="zh"
          )
        
          result = translator.translate(request)
          assert result.text == "你好"
          assert result.source_language == "en"
          assert result.target_language == "zh"
          assert result.model == "gpt-4"


  def test_openai_translator_api_error():
      """测试 API 错误处理"""
      translator = OpenAITranslator({
          "api_key": "test-key",
          "model": "gpt-4"
      })
      
      with patch('requests.post') as mock_post:
          mock_response = Mock()
          mock_response.status_code = 401
          mock_response.text = "Unauthorized"
          mock_post.return_value = mock_response
          
          request = TranslationRequest(text="Hello")
          
          with pytest.raises(APIError):
              translator.translate(request)
  ```
  
  创建 `tests/test_completeness_evaluator.py`:
  ```python
  """完整性评估器测试"""
  import pytest
  from src.evaluators.completeness_evaluator import CompletenessEvaluator
  from src.evaluators.base import EvaluationRequest


  def test_completeness_evaluator_evaluate():
      """测试完整性评估器评估"""
      evaluator = CompletenessEvaluator()
      
      request = EvaluationRequest(
          original_text="Hello, World!",
          translated_text="你好，世界！",
          source_language="en",
          target_language="zh"
      )
      
      result = evaluator.evaluate(request)
      assert result.completeness_score > 0
      assert result.overall_score == result.completeness_score
      assert isinstance(result.issues, list)
      assert isinstance(result.suggestions, list)


  def test_completeness_evaluator_empty_translation():
      """测试空翻译"""
      evaluator = CompletenessEvaluator()
      
      request = EvaluationRequest(
          original_text="Hello, World!",
          translated_text="",
          source_language="en",
          target_language="zh"
      )
      
      result = evaluator.evaluate(request)
      assert result.completeness_score < 50
      assert "翻译文本为空" in result.issues
  ```
  
  创建 `tests/test_translator.py`:
  ```python
  """主翻译器测试"""
  import pytest
  import tempfile
  from pathlib import Path
  from unittest.mock import Mock, patch
  from src.translator import Translator


  def test_translator_translate_text():
      """测试文本翻译"""
      translator = Translator()
      
      # Mock 翻译器和评估器
      with patch('src.translator.get_translator') as mock_get_translator, \
           patch('src.translator.get_evaluator') as mock_get_evaluator:
          
          mock_translator = Mock()
          mock_translator.translate.return_value = Mock(
              text="你好",
              model="gpt-4",
              usage={"total_tokens": 15}
          )
          mock_get_translator.return_value = mock_translator
          
          mock_evaluator = Mock()
          mock_evaluator.evaluate.return_value = Mock(
              overall_score=85.0,
              completeness_score=90.0,
              issues=[],
              suggestions=[]
          )
          mock_get_evaluator.return_value = mock_evaluator
          
          result = translator.translate_text("Hello")
          assert result["translated_text"] == "你好"
          assert result["quality_score"] == 85.0


  def test_translator_translate_file():
      """测试文件翻译"""
      translator = Translator()
      
      # 创建临时文件
      with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
          f.write("Hello, World!")
          temp_file = f.name
      
      try:
          # Mock 组件
          with patch('src.translator.get_parser') as mock_get_parser, \
               patch('src.translator.get_translator') as mock_get_translator, \
               patch('src.translator.get_evaluator') as mock_get_evaluator:
              
              mock_parser = Mock()
              mock_parser.parse.return_value = Mock(
                  text="Hello, World!",
                  page_count=1,
                  format_type="txt",
                  metadata={}
              )
              mock_get_parser.return_value = mock_parser
              
              mock_translator = Mock()
              mock_translator.translate.return_value = Mock(
                  text="你好，世界！",
                  model="gpt-4",
                  usage={"total_tokens": 20}
              )
              mock_get_translator.return_value = mock_translator
              
              mock_evaluator = Mock()
              mock_evaluator.evaluate.return_value = Mock(
                  overall_score=90.0,
                  completeness_score=95.0,
                  issues=[],
                  suggestions=[]
              )
              mock_get_evaluator.return_value = mock_evaluator
              
              result = translator.translate_file(temp_file)
              assert result["translated_text"] == "你好，世界！"
              assert result["quality_score"] == 90.0
      finally:
          Path(temp_file).unlink()
  ```

- **MIRROR**: tests/test_parsers.py 的测试模式
- **IMPORTS**: pytest, tempfile, pathlib, unittest.mock
- **GOTCHA**: 
  - 需要使用 Mock 隔离外部依赖
  - 需要测试异常情况
  - 需要清理临时文件
- **VALIDATE**:
  ```bash
  python -m pytest tests/ -v
  ```

---

## Testing Strategy

### Unit Tests

| Test | Input | Expected Output | Edge Case? |
|------|-------|-----------------|------------|
| test_txt_parser_parse | TXT 文件 | 解析成功 | 否 |
| test_txt_parser_file_not_found | 不存在的文件 | 抛出异常 | 是 |
| test_md_parser_parse | Markdown 文件 | 解析成功，保留格式 | 否 |
| test_openai_translator_translate | 翻译请求 | 翻译成功 | 否 |
| test_openai_translator_api_error | API 错误 | 抛出异常 | 是 |
| test_completeness_evaluator_evaluate | 评估请求 | 评估成功 | 否 |
| test_completeness_evaluator_empty_translation | 空翻译 | 低分，检测问题 | 是 |
| test_translator_translate_text | 文本翻译 | 完整流程成功 | 否 |
| test_translator_translate_file | 文件翻译 | 完整流程成功 | 否 |

### Edge Cases Checklist

- [ ] 文件不存在
- [ ] 文件编码错误
- [ ] 不支持的文件格式
- [ ] API 超时
- [ ] API 错误响应
- [ ] 空文本
- [ ] 空翻译结果

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

### 集成测试
```bash
python -c "from src.translator import Translator; t = Translator(); print(t.list_supported_formats())"
```
EXPECT: 输出支持的文件格式列表

### 功能测试
```bash
# 创建测试文件
echo "Hello, World!" > test.txt

# 运行翻译
python -c "from src.translator import Translator; t = Translator(); result = t.translate_file('test.txt'); print(result['translated_text'])"

# 清理
rm test.txt
```
EXPECT: 输出翻译结果

---

## Acceptance Criteria

- [ ] TXT 文件解析器实现并测试通过
- [ ] Markdown 文件解析器实现并测试通过
- [ ] OpenAI 翻译器实现并测试通过
- [ ] 完整性评估器实现并测试通过
- [ ] 主翻译流程编排器实现并测试通过
- [ ] 所有单元测试通过
- [ ] 能够成功翻译 .txt 文件
- [ ] 能够成功翻译 .md 文件
- [ ] 能够成功翻译直接输入的文本
- [ ] 输出包含翻译结果和质量评分

---

## Completion Checklist

- [x] 代码遵循已建立的模式
- [x] 错误处理遵循约定
- [x] 日志遵循 structlog 最佳实践
- [x] 测试遵循 pytest 模式
- [x] 无硬编码值
- [x] 无不必要的范围添加
- [x] 所有模块自动注册

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| OpenAI API 不可用 | 中 | 高 | 使用 Mock 进行测试，提供降级方案 |
| Markdown 格式丢失 | 低 | 中 | 保留原始文本，不做格式转换 |
| 翻译质量不稳定 | 中 | 中 | 使用低温度参数，提供上下文 |
| 完整性评估不准确 | 中 | 低 | Phase 5 将实现更全面的评估 |

---

## Notes

- Phase 2 是验证核心流程的关键阶段，需要确保从文件输入到翻译输出的完整链路通畅
- 使用 OpenAI 兼容接口，支持多种模型（OpenAI GPT、Azure、本地模型、IDE 内置模型）
- 完整性评估是基础评估，Phase 5 将实现更全面的评估系统
- 所有模块都使用自动注册机制，简化使用流程
- 测试使用 Mock 隔离外部依赖，确保测试稳定性
