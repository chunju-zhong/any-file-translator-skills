# Plan: DOCX & EPUB Support - Phase 4

## Summary

实现 DOCX 和 EPUB 文件格式支持，包括文件解析、文本提取、格式保留和输出功能。这将扩展系统的文件格式支持范围，为后续的多格式输出和超大文件处理奠定基础。

## User Story

As a developer,
I want to translate DOCX and EPUB documents with preserved formatting,
So that I can handle a wider range of document formats in my translation workflow.

## Problem → Solution

当前状态：系统支持 TXT、Markdown 和 PDF 文件格式，但不支持 DOCX 和 EPUB 文件。
期望状态：系统能够解析和处理 DOCX 和 EPUB 文件，保留文档格式和结构。

## Metadata

- **Complexity**: Medium
- **Source PRD**: `.claude/PRPs/prds/any-file-translator.prd.md`
- **PRD Phase**: Phase 4: DOCX & EPUB Support
- **Estimated Files**: 6-8 个文件

---

## UX Design

### Before
```
┌─────────────────────────────┐
│  无法处理 DOCX 和 EPUB 文件  │
│  - 不支持 DOCX 格式输入      │
│  - 不支持 EPUB 格式输入      │
│  - 无法提取文档文本和格式    │
└─────────────────────────────┘
```

### After
```
┌─────────────────────────────┐
│  支持 DOCX 和 EPUB 文件      │
│  - DOCX 文件解析和处理       │
│  - EPUB 文件解析和处理       │
│  - 保留文档格式和结构        │
│  - DOCX 和 EPUB 输出         │
└─────────────────────────────┘
```

### Interaction Changes

| Touchpoint | Before | After | Notes |
|------------|--------|-------|-------|
| 输入文件格式 | 仅支持 .txt, .md, .pdf | 支持 .docx, .epub | 增加 DOCX 和 EPUB 解析能力 |
| 格式保留 | 仅 Markdown 和 PDF | 支持 DOCX 和 EPUB | 保持文档原始格式 |
| 输出格式 | 仅 Markdown | 支持 DOCX 和 EPUB | 扩展输出格式选项 |

---

## Mandatory Reading

| Priority | File | Lines | Why |
|----------|------|-------|-----|
| P0 | `src/parsers/base.py` | 1-100 | 基础解析器接口，必须遵循的抽象方法 |
| P0 | `src/parsers/txt_parser.py` | 1-54 | 参考实现模式，了解解析器结构 |
| P0 | `src/parsers/md_parser.py` | 1-83 | 参考实现模式，了解元数据提取 |
| P0 | `src/parsers/pdf_parser.py` | 1-180 | 参考实现模式，了解复杂文件解析 |
| P1 | `src/parsers/__init__.py` | 1-51 | 了解自动注册机制 |
| P1 | `src/utils/exceptions.py` | 1-71 | 了解异常处理模式 |
| P1 | `src/utils/logger.py` | 1-41 | 了解日志记录模式 |

## External Documentation

| Topic | Source | Key Takeaway |
|-------|--------|--------------|
| python-docx | python-docx 官方文档 | 用于处理 DOCX 文件，提取文本和格式 |
| ebooklib | ebooklib 官方文档 | 用于处理 EPUB 文件，提取文本和结构 |
| DOCX 文件结构 | Microsoft Office 文档规范 | 了解 DOCX 文件的 XML 结构 |
| EPUB 文件结构 | EPUB 3.0 规范 | 了解 EPUB 文件的 ZIP 结构和内容组织 |

---

## Patterns to Mirror

### NAMING_CONVENTION
```python
# SOURCE: src/parsers/txt_parser.py:8
class TxtParser(BaseParser):
    supported_extensions = [".txt"]
```

### ERROR_HANDLING
```python
# SOURCE: src/parsers/txt_parser.py:47-53
except UnicodeDecodeError as e:
    self.logger.error("txt_decode_error", file=file_path, error=str(e))
    raise FileProcessingError(f"Failed to decode file: {file_path}")
except Exception as e:
    self.logger.error("txt_parse_error", file=file_path, error=str(e))
    raise FileProcessingError(f"Failed to parse TXT file: {e}")
```

### LOGGING_PATTERN
```python
# SOURCE: src/parsers/txt_parser.py:31-35
self.logger.info(
    "txt_file_parsed",
    file=str(path),
    size=len(text)
)
```

### PARSER_REGISTRATION
```python
# SOURCE: src/parsers/__init__.py:33-41
_txt_parser = TxtParser()
register_parser([".txt"], _txt_parser)

_md_parser = MdParser()
register_parser([".md", ".markdown"], _md_parser)

_pdf_parser = PdfParser()
register_parser([".pdf"], _pdf_parser)
```

### METADATA_EXTRACTION
```python
# SOURCE: src/parsers/md_parser.py:63-82
def _extract_metadata(self, text: str) -> dict:
    """提取 Markdown 元数据（如 YAML frontmatter）"""
    metadata = {}
    
    if text.startswith("---\n"):
        try:
            end_index = text.index("---\n", 4)
            frontmatter = text[4:end_index]
            metadata["has_frontmatter"] = True
            metadata["frontmatter_size"] = len(frontmatter)
        except ValueError:
            metadata["has_frontmatter"] = False
    
    lines = text.split('\n')
    heading_count = sum(1 for line in lines if line.startswith('#'))
    metadata["heading_count"] = heading_count
    
    code_block_count = text.count('```')
    metadata["code_block_count"] = code_block_count // 2
    
    return metadata
```

---

## Files to Change

| File | Action | Justification |
|------|--------|---------------|
| `src/parsers/docx_parser.py` | CREATE | DOCX 文件解析器，实现文本提取和格式保留 |
| `src/parsers/epub_parser.py` | CREATE | EPUB 文件解析器，实现文本提取和结构保留 |
| `src/parsers/__init__.py` | UPDATE | 注册 DOCX 和 EPUB 解析器 |
| `tests/test_docx_parser.py` | CREATE | DOCX 解析器测试 |
| `tests/test_epub_parser.py` | CREATE | EPUB 解析器测试 |
| `src/utils/doc_utils.py` | CREATE | 文档工具函数，如 DOCX 格式处理 |
| `tests/test_doc_utils.py` | CREATE | 文档工具函数测试 |

## NOT Building

- DOCX 高级格式处理（如复杂表格、图表）- 超出当前范围
- EPUB 复杂排版处理 - 超出当前范围
- 文档转换功能 - 将在 Phase 9 实现

---

## Step-by-Step Tasks

### Task 1: 创建 DOCX 解析器

- **ACTION**: 实现 DOCX 解析器，支持文本提取和格式保留
- **IMPLEMENT**: 创建 `src/parsers/docx_parser.py`：
  ```python
  """DOCX 文件解析器"""
  from pathlib import Path
  from typing import List, Dict, Any
  from docx import Document
  from src.parsers.base import BaseParser, ParseResult, Chapter
  from src.utils.logger import get_logger
  from src.utils.exceptions import FileProcessingError


  class DocxParser(BaseParser):
      """DOCX 文件解析器"""
      
      supported_extensions = [".docx"]
      
      def __init__(self):
          super().__init__()
          self.logger = get_logger(__name__)
      
      def parse(self, file_path: str) -> ParseResult:
          """解析 DOCX 文件"""
          try:
              path = Path(file_path)
              
              if not path.exists():
                  raise FileProcessingError(f"File not found: {file_path}")
              
              if not self.can_parse(file_path):
                  raise FileProcessingError(f"Unsupported file format: {file_path}")
              
              # 使用 python-docx 提取文本
              doc = Document(file_path)
              text = ""
              
              for paragraph in doc.paragraphs:
                  text += paragraph.text + "\n"
              
              # 提取元数据
              metadata = self._extract_metadata(doc)
              
              self.logger.info(
                  "docx_file_parsed",
                  file=str(path),
                  paragraphs=len(doc.paragraphs),
                  size=len(text)
              )
              
              return ParseResult(
                  text=text,
                  page_count=1,  # DOCX 没有固定页数概念
                  metadata={
                      "file_size": path.stat().st_size,
                      "file_name": path.name,
                      "paragraph_count": len(doc.paragraphs),
                      **metadata
                  },
                  format_type="docx"
              )
          
          except Exception as e:
              self.logger.error("docx_parse_error", file=file_path, error=str(e))
              raise FileProcessingError(f"Failed to parse DOCX file: {e}")
      
      def get_page_count(self, file_path: str) -> int:
          """DOCX 文件返回 1 页"""
          return 1
      
      def extract_chapters(self, file_path: str) -> List[Chapter]:
          """从 DOCX 提取章节信息"""
          chapters = []
          
          try:
              doc = Document(file_path)
              chapter_count = 0
              
              for i, paragraph in enumerate(doc.paragraphs):
                  # 简单实现：基于标题样式识别章节
                  if paragraph.style.name.startswith('Heading'):
                      chapter_count += 1
                      chapters.append(Chapter(
                          title=paragraph.text.strip(),
                          start_page=1,
                          end_page=1,
                          level=int(paragraph.style.name[-1]) if paragraph.style.name[-1].isdigit() else 1
                      ))
          
          except Exception as e:
              self.logger.warning("docx_chapter_extraction_error", file=file_path, error=str(e))
          
          return chapters
      
      def _extract_metadata(self, doc) -> dict:
          """提取 DOCX 元数据"""
          metadata = {}
          
          try:
              # 提取文档属性
              core_properties = doc.core_properties
              if core_properties.title:
                  metadata["title"] = core_properties.title
              if core_properties.author:
                  metadata["author"] = core_properties.author
              if core_properties.subject:
                  metadata["subject"] = core_properties.subject
              if core_properties.keywords:
                  metadata["keywords"] = core_properties.keywords
          
          except Exception as e:
              self.logger.warning("docx_metadata_extraction_error", error=str(e))
          
          return metadata
  ```

- **MIRROR**: 遵循 `TxtParser` 和 `PdfParser` 的实现模式
- **IMPORTS**: python-docx, pathlib, typing
- **GOTCHA**: 
  - DOCX 文件可能包含复杂格式，需要适当处理
  - python-docx 可能无法处理某些特殊格式
- **VALIDATE**: 运行测试确保 DOCX 解析功能正常

### Task 2: 创建 EPUB 解析器

- **ACTION**: 实现 EPUB 解析器，支持文本提取和结构保留
- **IMPLEMENT**: 创建 `src/parsers/epub_parser.py`：
  ```python
  """EPUB 文件解析器"""
  from pathlib import Path
  from typing import List, Dict, Any
  import ebooklib
  from ebooklib import epub
  from src.parsers.base import BaseParser, ParseResult, Chapter
  from src.utils.logger import get_logger
  from src.utils.exceptions import FileProcessingError


  class EpubParser(BaseParser):
      """EPUB 文件解析器"""
      
      supported_extensions = [".epub"]
      
      def __init__(self):
          super().__init__()
          self.logger = get_logger(__name__)
      
      def parse(self, file_path: str) -> ParseResult:
          """解析 EPUB 文件"""
          try:
              path = Path(file_path)
              
              if not path.exists():
                  raise FileProcessingError(f"File not found: {file_path}")
              
              if not self.can_parse(file_path):
                  raise FileProcessingError(f"Unsupported file format: {file_path}")
              
              # 使用 ebooklib 提取文本
              book = epub.read_epub(file_path)
              text = ""
              
              for item in book.get_items():
                  if item.get_type() == ebooklib.ITEM_DOCUMENT:
                      content = item.get_content().decode('utf-8', errors='ignore')
                      # 简单提取文本，去除 HTML 标签
                      import re
                      text_content = re.sub('<[^>]+>', '', content)
                      text += text_content + "\n"
              
              # 提取元数据
              metadata = self._extract_metadata(book)
              
              # 提取章节信息
              chapters = self.extract_chapters(file_path)
              
              self.logger.info(
                  "epub_file_parsed",
                  file=str(path),
                  chapters=len(chapters),
                  size=len(text)
              )
              
              return ParseResult(
                  text=text,
                  page_count=1,  # EPUB 没有固定页数概念
                  metadata={
                      "file_size": path.stat().st_size,
                      "file_name": path.name,
                      "chapter_count": len(chapters),
                      **metadata
                  },
                  format_type="epub"
              )
          
          except Exception as e:
              self.logger.error("epub_parse_error", file=file_path, error=str(e))
              raise FileProcessingError(f"Failed to parse EPUB file: {e}")
      
      def get_page_count(self, file_path: str) -> int:
          """EPUB 文件返回 1 页"""
          return 1
      
      def extract_chapters(self, file_path: str) -> List[Chapter]:
          """从 EPUB 提取章节信息"""
          chapters = []
          
          try:
              book = epub.read_epub(file_path)
              chapter_count = 0
              
              # 遍历 EPUB 的目录结构
              for item in book.toc:
                  if isinstance(item, tuple):
                      # 处理嵌套目录
                      chapters.extend(self._process_toc_item(item, 1))
                  else:
                      chapter_count += 1
                      chapters.append(Chapter(
                          title=item.title,
                          start_page=1,
                          end_page=1,
                          level=1
                      ))
          
          except Exception as e:
              self.logger.warning("epub_chapter_extraction_error", file=file_path, error=str(e))
          
          return chapters
      
      def _process_toc_item(self, item, level):
          """处理 EPUB 目录项"""
          chapters = []
          title, subitems = item
          
          # 添加当前章节
          chapters.append(Chapter(
              title=title,
              start_page=1,
              end_page=1,
              level=level
          ))
          
          # 处理子章节
          for subitem in subitems:
              if isinstance(subitem, tuple):
                  chapters.extend(self._process_toc_item(subitem, level + 1))
              else:
                  chapters.append(Chapter(
                      title=subitem.title,
                      start_page=1,
                      end_page=1,
                      level=level + 1
                  ))
          
          return chapters
      
      def _extract_metadata(self, book) -> dict:
          """提取 EPUB 元数据"""
          metadata = {}
          
          try:
              # 提取 EPUB 元数据
              if hasattr(book, 'get_metadata'):
                  for key, value in book.get_metadata('DC', 'title'):
                      metadata["title"] = value[0]
                  for key, value in book.get_metadata('DC', 'creator'):
                      metadata["creator"] = value[0]
                  for key, value in book.get_metadata('DC', 'subject'):
                      metadata["subject"] = value[0]
                  for key, value in book.get_metadata('DC', 'description'):
                      metadata["description"] = value[0]
          
          except Exception as e:
              self.logger.warning("epub_metadata_extraction_error", error=str(e))
          
          return metadata
  ```

- **MIRROR**: 遵循 `TxtParser` 和 `PdfParser` 的实现模式
- **IMPORTS**: ebooklib, pathlib, typing, re
- **GOTCHA**: 
  - EPUB 文件是 ZIP 格式，可能包含复杂的内部结构
  - 不同 EPUB 版本可能有不同的结构
- **VALIDATE**: 运行测试确保 EPUB 解析功能正常

### Task 3: 注册 DOCX 和 EPUB 解析器

- **ACTION**: 在 `src/parsers/__init__.py` 中注册 DOCX 和 EPUB 解析器
- **IMPLEMENT**: 更新 `src/parsers/__init__.py`：
  ```python
  """解析器模块"""
  from typing import Dict, List, Optional
  from src.parsers.base import BaseParser, ParseResult, Chapter
  from src.parsers.txt_parser import TxtParser
  from src.parsers.md_parser import MdParser
  from src.parsers.pdf_parser import PdfParser
  from src.parsers.docx_parser import DocxParser
  from src.parsers.epub_parser import EpubParser

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


  _txt_parser = TxtParser()
  register_parser([".txt"], _txt_parser)

  _md_parser = MdParser()
  register_parser([".md", ".markdown"], _md_parser)

  _pdf_parser = PdfParser()
  register_parser([".pdf"], _pdf_parser)

  _docx_parser = DocxParser()
  register_parser([".docx"], _docx_parser)

  _epub_parser = EpubParser()
  register_parser([".epub"], _epub_parser)


  __all__ = [
      'BaseParser',
      'ParseResult', 
      'Chapter',
      'register_parser',
      'get_parser',
      'list_supported_formats',
  ]
  ```

- **MIRROR**: 遵循现有的解析器注册模式
- **IMPORTS**: DocxParser, EpubParser
- **GOTCHA**: 确保导入路径正确
- **VALIDATE**: 运行 `list_supported_formats()` 确保 DOCX 和 EPUB 格式被正确注册

### Task 4: 创建文档工具函数

- **ACTION**: 实现文档工具函数，如 DOCX 格式处理
- **IMPLEMENT**: 创建 `src/utils/doc_utils.py`：
  ```python
  """文档工具函数"""
  from pathlib import Path
  from typing import List, Optional
  from docx import Document
  from docx.shared import Pt
  from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
  from src.utils.logger import get_logger
  from src.utils.exceptions import FileProcessingError

  logger = get_logger(__name__)


def create_docx(output_path: str, content: str, metadata: dict = None) -> str:
    """创建 DOCX 文件
    
    Args:
        output_path: 输出文件路径
        content: 文档内容
        metadata: 文档元数据
        
    Returns:
        输出文件路径
    """
    try:
        # 创建文档
        doc = Document()
        
        # 设置元数据
        if metadata:
            core_properties = doc.core_properties
            if 'title' in metadata:
                core_properties.title = metadata['title']
            if 'author' in metadata:
                core_properties.author = metadata['author']
            if 'subject' in metadata:
                core_properties.subject = metadata['subject']
        
        # 添加内容
        paragraphs = content.split('\n')
        for paragraph_text in paragraphs:
            if paragraph_text.strip():
                paragraph = doc.add_paragraph(paragraph_text)
                # 设置默认格式
                paragraph.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 保存文档
        doc.save(output_path)
        
        logger.info("docx_created", output=output_path, paragraphs=len(paragraphs))
        return output_path
        
    except Exception as e:
        logger.error("docx_creation_error", output=output_path, error=str(e))
        raise FileProcessingError(f"Failed to create DOCX file: {e}")


def extract_docx_styles(docx_path: str) -> dict:
    """提取 DOCX 文档样式
    
    Args:
        docx_path: DOCX 文件路径
        
    Returns:
        样式信息字典
    """
    try:
        doc = Document(docx_path)
        styles = {}
        
        # 提取段落样式
        paragraph_styles = {}
        for style in doc.styles:
            if style.type == 1:  # 段落样式
                paragraph_styles[style.name] = {
                    'font_size': style.font.size.pt if style.font.size else None,
                    'font_name': style.font.name,
                    'bold': style.font.bold,
                    'italic': style.font.italic
                }
        
        styles['paragraph_styles'] = paragraph_styles
        
        return styles
        
    except Exception as e:
        logger.error("docx_style_extraction_error", file=docx_path, error=str(e))
        raise FileProcessingError(f"Failed to extract DOCX styles: {e}")
  ```

- **MIRROR**: 遵循项目的错误处理和日志记录模式
- **IMPORTS**: python-docx, pathlib
- **GOTCHA**: 
  - python-docx 的样式处理可能比较复杂
  - 需要处理各种格式的边界情况
- **VALIDATE**: 运行测试确保文档工具函数正常

### Task 5: 编写 DOCX 解析器测试

- **ACTION**: 为 DOCX 解析器编写单元测试
- **IMPLEMENT**: 创建 `tests/test_docx_parser.py`：
  ```python
  """DOCX 解析器测试"""
  import pytest
  import tempfile
  from pathlib import Path
  from docx import Document
  from src.parsers.docx_parser import DocxParser
  from src.utils.exceptions import FileProcessingError

  def create_test_docx(content: str, path: str):
      """创建测试用的 DOCX 文件"""
      doc = Document()
      doc.add_paragraph(content)
      doc.save(path)

  def test_docx_parser_init():
      """测试 DOCX 解析器初始化"""
      parser = DocxParser()
      assert parser is not None
      assert ".docx" in parser.supported_extensions

  def test_docx_parser_can_parse():
      """测试 DOCX 解析器是否支持 DOCX 文件"""
      parser = DocxParser()
      assert parser.can_parse("test.docx")
      assert not parser.can_parse("test.txt")
      assert not parser.can_parse("test.pdf")

  def test_docx_parser_nonexistent_file():
      """测试解析不存在的文件"""
      parser = DocxParser()
      with pytest.raises(FileProcessingError):
          parser.parse("nonexistent.docx")

  def test_docx_parser_parse():
      """测试解析 DOCX 文件"""
      parser = DocxParser()
      
      # 创建测试 DOCX 文件
      with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
          temp_path = f.name
      
      create_test_docx("Hello, World!\nThis is a test.", temp_path)
      
      try:
          result = parser.parse(temp_path)
          assert "Hello, World!" in result.text
          assert result.page_count == 1
          assert result.format_type == "docx"
      finally:
          Path(temp_path).unlink()
  ```

- **MIRROR**: 遵循现有的测试模式
- **IMPORTS**: pytest, tempfile, pathlib, python-docx
- **GOTCHA**: 测试需要创建实际的 DOCX 文件
- **VALIDATE**: 运行测试确保 DOCX 解析器测试通过

### Task 6: 编写 EPUB 解析器测试

- **ACTION**: 为 EPUB 解析器编写单元测试
- **IMPLEMENT**: 创建 `tests/test_epub_parser.py`：
  ```python
  """EPUB 解析器测试"""
  import pytest
  import tempfile
  from pathlib import Path
  import ebooklib
  from ebooklib import epub
  from src.parsers.epub_parser import EpubParser
  from src.utils.exceptions import FileProcessingError

  def create_test_epub(content: str, path: str):
      """创建测试用的 EPUB 文件"""
      book = epub.EpubBook()
      book.set_title('Test Book')
      book.set_language('en')
      book.add_author('Test Author')
      
      # 创建章节
      chapter = epub.EpubHtml(title='Chapter 1', file_name='chapter1.xhtml', lang='en')
      chapter.content = f'<html><body><p>{content}</p></body></html>'
      
      # 添加章节
      book.add_item(chapter)
      book.toc = [epub.Link('chapter1.xhtml', 'Chapter 1', 'chapter1')]
      book.spine = ['nav', chapter]
      
      # 添加导航
      book.add_item(epub.EpubNav())
      book.add_item(epub.EpubNcx())
      
      # 保存 EPUB
      epub.write_epub(path, book, {})

  def test_epub_parser_init():
      """测试 EPUB 解析器初始化"""
      parser = EpubParser()
      assert parser is not None
      assert ".epub" in parser.supported_extensions

  def test_epub_parser_can_parse():
      """测试 EPUB 解析器是否支持 EPUB 文件"""
      parser = EpubParser()
      assert parser.can_parse("test.epub")
      assert not parser.can_parse("test.txt")
      assert not parser.can_parse("test.pdf")

  def test_epub_parser_nonexistent_file():
      """测试解析不存在的文件"""
      parser = EpubParser()
      with pytest.raises(FileProcessingError):
          parser.parse("nonexistent.epub")

  def test_epub_parser_parse():
      """测试解析 EPUB 文件"""
      parser = EpubParser()
      
      # 创建测试 EPUB 文件
      with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
          temp_path = f.name
      
      create_test_epub("Hello, EPUB World!\nThis is a test.", temp_path)
      
      try:
          result = parser.parse(temp_path)
          assert "Hello, EPUB World!" in result.text
          assert result.page_count == 1
          assert result.format_type == "epub"
      finally:
          Path(temp_path).unlink()
  ```

- **MIRROR**: 遵循现有的测试模式
- **IMPORTS**: pytest, tempfile, pathlib, ebooklib
- **GOTCHA**: 测试需要创建实际的 EPUB 文件
- **VALIDATE**: 运行测试确保 EPUB 解析器测试通过

### Task 7: 编写文档工具函数测试

- **ACTION**: 为文档工具函数编写单元测试
- **IMPLEMENT**: 创建 `tests/test_doc_utils.py`：
  ```python
  """文档工具函数测试"""
  import pytest
  import tempfile
  from pathlib import Path
  from src.utils.doc_utils import create_docx, extract_docx_styles

  def test_create_docx():
      """测试创建 DOCX 文件"""
      with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
          temp_path = f.name
      
      try:
          result_path = create_docx(temp_path, "Hello, DOCX!\nThis is a test.")
          assert result_path == temp_path
          assert Path(result_path).exists()
      finally:
          Path(temp_path).unlink()

  def test_extract_docx_styles():
      """测试提取 DOCX 样式"""
      from docx import Document
      
      with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
          temp_path = f.name
      
      # 创建测试 DOCX 文件
      doc = Document()
      doc.add_paragraph("Test")
      doc.save(temp_path)
      
      try:
          styles = extract_docx_styles(temp_path)
          assert 'paragraph_styles' in styles
          assert isinstance(styles['paragraph_styles'], dict)
      finally:
          Path(temp_path).unlink()
  ```

- **MIRROR**: 遵循现有的测试模式
- **IMPORTS**: pytest, tempfile, pathlib
- **GOTCHA**: 测试需要创建实际的 DOCX 文件
- **VALIDATE**: 运行测试确保文档工具函数测试通过

---

## Testing Strategy

### Unit Tests

| Test | Input | Expected Output | Edge Case? |
|------|-------|-----------------|------------|
| test_docx_parser_init | 无 | 解析器初始化成功 | 是 |
| test_docx_parser_can_parse | ".docx" | 返回 True | 是 |
| test_docx_parser_nonexistent_file | 不存在的文件 | 抛出 FileProcessingError | 是 |
| test_docx_parser_parse | DOCX 文件 | 解析成功，返回文本内容 | 是 |
| test_epub_parser_init | 无 | 解析器初始化成功 | 是 |
| test_epub_parser_can_parse | ".epub" | 返回 True | 是 |
| test_epub_parser_nonexistent_file | 不存在的文件 | 抛出 FileProcessingError | 是 |
| test_epub_parser_parse | EPUB 文件 | 解析成功，返回文本内容 | 是 |
| test_create_docx | 文本内容 | 创建 DOCX 文件 | 是 |
| test_extract_docx_styles | DOCX 文件 | 提取样式信息 | 是 |

### Edge Cases Checklist
- [ ] 空 DOCX 文件
- [ ] 空 EPUB 文件
- [ ] 包含复杂格式的 DOCX 文件
- [ ] 包含嵌套目录的 EPUB 文件
- [ ] 大体积 DOCX 文件
- [ ] 大体积 EPUB 文件

---

## Validation Commands

### 安装依赖
```bash
pip install -r requirements.txt
```
EXPECT: 所有依赖安装成功

### 单元测试
```bash
python -m pytest tests/test_docx_parser.py -v
python -m pytest tests/test_epub_parser.py -v
python -m pytest tests/test_doc_utils.py -v
```
EXPECT: 所有测试通过

### 集成测试
```bash
python -m pytest tests/ -v
```
EXPECT: 所有测试通过，无回归

### 导入测试
```bash
python -c "from src.parsers import get_parser; print(get_parser('test.docx')); print(get_parser('test.epub')); print('DOCX and EPUB parsers imported successfully')"
```
EXPECT: 成功导入 DOCX 和 EPUB 解析器

---

## Acceptance Criteria
- [ ] DOCX 解析器实现完成
- [ ] EPUB 解析器实现完成
- [ ] DOCX 和 EPUB 解析器注册成功
- [ ] 文档工具函数实现完成
- [ ] 所有单元测试通过
- [ ] 集成测试通过
- [ ] 支持 DOCX 和 EPUB 文件的基本解析和处理

## Completion Checklist
- [ ] 代码遵循项目的命名和结构规范
- [ ] 错误处理符合项目模式
- [ ] 日志记录符合项目规范
- [ ] 测试覆盖主要功能和边缘情况
- [ ] 无硬编码值
- [ ] 文档完善

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| DOCX 格式复杂性 | 中 | 中 | 优先提取文本内容，格式处理作为次要目标 |
| EPUB 结构差异 | 中 | 中 | 处理不同 EPUB 版本的兼容性 |
| 依赖库版本冲突 | 低 | 中 | 使用固定版本范围 |
| 内存使用过高 | 低 | 高 | 对于大文件使用流式处理 |

## Notes

- DOCX 和 EPUB 处理是系统的重要扩展，需要确保稳定性
- 优先实现基本的文本提取功能，格式处理可以在后续阶段优化
- 测试需要创建实际的 DOCX 和 EPUB 文件，确保功能的真实性
- 后续阶段将基于此实现多格式输出和超大文件处理