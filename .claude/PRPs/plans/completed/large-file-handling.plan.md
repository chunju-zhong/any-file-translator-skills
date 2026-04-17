# Plan: Large File Handling - Phase 7

## Summary
Implement intelligent large file handling with automatic file size detection, smart chunking based on chapters/sections, parallel translation processing, and result merging. This will enable the system to handle 1000-2000 page documents efficiently while maintaining translation quality and format integrity.

## User Story
As a user, I want to translate large documents (1000+ pages) without manual splitting, so that I can efficiently process extensive technical documentation, books, and reports in a single operation.

## Problem → Solution
**Current state**: Large files cause memory issues, timeout errors, and poor translation quality due to context loss. Users must manually split files before translation.
**Desired state**: System automatically detects large files, intelligently splits by chapters/sections, processes chunks in parallel, and merges results with consistent quality across all sections.

## Metadata
- **Complexity**: Large
- **Source PRD**: .claude/PRPs/prds/any-file-translator.prd.md
- **PRD Phase**: Phase 7 - Large File Handling
- **Estimated Files**: 8 files (4 new, 4 modified)

---

## UX Design

### Before
```
┌─────────────────────────────┐
│  User uploads 1500-page PDF │
│  ↓                          │
│  System attempts to process │
│  ↓                          │
│  Memory error / timeout     │
│  ↓                          │
│  User must manually split   │
│  ↓                          │
│  Process each part separately│
│  ↓                          │
│  Manually merge results     │
└─────────────────────────────┘
```

### After
```
┌─────────────────────────────┐
│  User uploads 1500-page PDF │
│  ↓                          │
│  Auto-detect file size      │
│  ↓                          │
│  Smart split by chapters    │
│  ↓                          │
│  Parallel translation       │
│  (4 chunks simultaneously)  │
│  ↓                          │
│  Quality check per chunk    │
│  ↓                          │
│  Auto-merge results         │
│  ↓                          │
│  Single coherent output     │
└─────────────────────────────┘
```

### Interaction Changes
| Touchpoint | Before | After | Notes |
|---|---|---|---|
| File upload | Single file, manual size check | Auto-detect and handle | Transparent to user |
| Processing | Sequential, single-threaded | Parallel, multi-threaded | Faster processing |
| Progress tracking | None | Real-time chunk progress | User sees progress |
| Output | Single file or manual merge | Auto-merged coherent output | Consistent quality |
| Error handling | Fail entire job | Retry failed chunks | More resilient |

---

## Mandatory Reading

Files that MUST be read before implementing:

| Priority | File | Lines | Why |
|---|---|---|---|
| P0 (critical) | `src/utils/pdf_utils.py` | 1-161 | PDF splitting/merging patterns |
| P0 (critical) | `src/translator.py` | 1-100 | Main translation flow to extend |
| P0 (critical) | `src/config.py` | 1-68 | Configuration patterns to extend |
| P1 (important) | `src/parsers/base.py` | all | Parser interface and Chapter class |
| P1 (important) | `tests/test_pdf_utils.py` | 1-30 | Test patterns for splitting/merging |

## External Documentation

| Topic | Source | Key Takeaway |
|---|---|---|
| Parallel Processing | Python concurrent.futures | Use ThreadPoolExecutor for I/O-bound translation tasks |
| Memory Management | Python generators | Use generators and streaming for large file processing |
| Chapter Detection | PDF structure analysis | Use bookmarks, font sizes, and heading patterns |
| Chunk Size Optimization | Translation research | 15-50 pages per chunk balances context vs. memory |

---

## Patterns to Mirror

### PDF_SPLITTING
// SOURCE: src/utils/pdf_utils.py:12-95
```python
def split_pdf(input_path: str, output_dir: str, chapters: List, max_pages: int = 50) -> List[str]:
    """拆分 PDF 文件"""
    output_files = []
    
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        with open(input_path, 'rb') as f:
            reader = PdfReader(f)
            total_pages = len(reader.pages)
            
            # 如果有章节信息，按章节拆分
            if chapters:
                for i, chapter in enumerate(chapters):
                    start_page = chapter.start_page - 1
                    end_page = chapter.end_page
                    
                    if i == len(chapters) - 1:
                        end_page = total_pages
                    
                    output_path = Path(output_dir) / f"chapter_{i+1}_{chapter.title.replace(' ', '_')[:50]}.pdf"
                    output_path = output_path.with_suffix('.pdf')
                    
                    writer = PdfWriter()
                    for page_num in range(start_page, end_page):
                        writer.add_page(reader.pages[page_num])
                    
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    
                    output_files.append(str(output_path))
            else:
                # 按页数兜底拆分
                current_page = 0
                part = 1
                
                while current_page < total_pages:
                    end_page = min(current_page + max_pages, total_pages)
                    
                    output_path = Path(output_dir) / f"part_{part}.pdf"
                    
                    writer = PdfWriter()
                    for page_num in range(current_page, end_page):
                        writer.add_page(reader.pages[page_num])
                    
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    
                    output_files.append(str(output_path))
                    
                    current_page = end_page
                    part += 1
        
        return output_files
        
    except Exception as e:
        logger.error("pdf_split_error", input=input_path, error=str(e))
        raise FileProcessingError(f"Failed to split PDF: {e}")
```

### CONFIGURATION_PATTERN
// SOURCE: src/config.py:20-25
```python
class ProcessingSettings(BaseModel):
    """处理配置"""
    chunk_size: int = Field(default=15, description="分块大小（页数）")
    max_parallel: int = Field(default=4, description="最大并行数")
    cache_enabled: bool = Field(default=True, description="是否启用缓存")
    cache_dir: str = Field(default=".cache", description="缓存目录")
```

### TRANSLATION_FLOW
// SOURCE: src/translator.py:27-65
```python
def translate_file(
    self,
    file_path: str,
    source_language: str = "auto",
    target_language: str = "zh",
    output_path: Optional[str] = None
) -> dict:
    """翻译文件"""
    try:
        self.parser = get_parser(file_path)
        
        self.logger.info(
            "translation_started",
            file=file_path,
            source_lang=source_language,
            target_lang=target_language
        )
        
        parse_result = self.parser.parse(file_path)
        self.logger.info("file_parsed", format=parse_result.format_type)
        
        from src.translators.base import TranslationRequest
        translation_request = TranslationRequest(
            text=parse_result.text,
            source_language=source_language,
            target_language=target_language
        )
        translation_result = self.translator.translate(translation_request)
        self.logger.info("text_translated", tokens=translation_result.usage.get("total_tokens", 0))
        
        from src.evaluators.base import EvaluationRequest
        evaluation_request = EvaluationRequest(
            original_text=parse_result.text,
            translated_text=translation_result.text,
            source_language=source_language,
            target_language=target_language
        )
        evaluation_result = self.evaluator.evaluate(evaluation_request)
        self.logger.info("quality_evaluated", score=evaluation_result.overall_score)
```

### LOGGING_PATTERN
// SOURCE: src/utils/pdf_utils.py:55-61
```python
logger.info(
    "pdf_split_by_chapter",
    chapter=chapter.title,
    start_page=start_page + 1,
    end_page=end_page,
    output=str(output_path)
)
```

### TEST_PATTERN
// SOURCE: tests/test_pdf_utils.py:9-21
```python
def test_split_pdf_with_chapters():
    """测试按章节拆分 PDF"""
    chapters = [
        Chapter(title="Chapter 1", start_page=1, end_page=5),
        Chapter(title="Chapter 2", start_page=6, end_page=10)
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test implementation
        pass
```

---

## Files to Change

| File | Action | Justification |
|---|---|---|
| `src/processors/__init__.py` | CREATE | New module for file processing |
| `src/processors/large_file_processor.py` | CREATE | Core large file handling logic |
| `src/processors/chunk_manager.py` | CREATE | Chunk management and coordination |
| `src/processors/result_merger.py` | CREATE | Result merging and coherence |
| `src/config.py` | UPDATE | Add LargeFileSettings |
| `src/translator.py` | UPDATE | Integrate large file processing |
| `tests/test_large_file_processor.py` | CREATE | Comprehensive tests |
| `tests/test_chunk_manager.py` | CREATE | Chunk management tests |

## NOT Building

- Real-time collaborative translation (out of scope)
- Custom chunk size per document type (use global config for now)
- Machine learning-based chunk optimization (rule-based for now)
- Persistent chunk state database (in-memory tracking only)
- Distributed processing across multiple machines (single-machine parallel processing)

---

## Step-by-Step Tasks

### Task 1: Create Large File Configuration
- **ACTION**: Add LargeFileSettings to config.py
- **IMPLEMENT**: Add `LargeFileSettings` class with `enabled`, `size_threshold_pages`, `size_threshold_mb`, `chunk_size`, `max_parallel_chunks`, `merge_strategy`, `progress_tracking` fields
- **MIRROR**: Follow `ProcessingSettings` pattern from src/config.py:20-25
- **IMPORTS**: `from pydantic import BaseModel, Field`, `from typing import Optional, Literal`
- **GOTCHA**: Set sensible defaults: size_threshold_pages=100, size_threshold_mb=50, chunk_size=50, max_parallel_chunks=4
- **VALIDATE**: Config loads successfully with new settings, defaults are applied correctly

### Task 2: Create ChunkManager Class
- **ACTION**: Create src/processors/chunk_manager.py with ChunkManager class
- **IMPLEMENT**:
  - `__init__(self, config: Dict[str, Any] = None)` - initialize with config
  - `should_chunk(self, file_path: str, parse_result: ParseResult) -> bool` - determine if file needs chunking
  - `create_chunks(self, file_path: str, parse_result: ParseResult) -> List[Chunk]` - create file chunks
  - `get_chunk_info(self, chunk_id: str) -> Dict` - get chunk metadata
  - `cleanup_chunks(self, chunk_ids: List[str]) -> None` - clean up temporary chunk files
- **MIRROR**: Follow class structure from src/utils/pdf_utils.py:12-95
- **IMPORTS**:
  ```python
  from typing import Dict, Any, List
  from dataclasses import dataclass, field
  from src.parsers.base import ParseResult, Chapter
  from src.utils.logger import get_logger
  from src.utils.exceptions import FileProcessingError
  ```
- **GOTCHA**: Use existing pdf_utils.split_pdf for PDF chunking; extend for other formats
- **VALIDATE**: Class instantiates correctly, methods are callable, logging works

### Task 3: Create Chunk Data Class
- **ACTION**: Add Chunk dataclass to chunk_manager.py
- **IMPLEMENT**:
  ```python
  @dataclass
  class Chunk:
      chunk_id: str
      file_path: str
      start_page: int
      end_page: int
      text: str
      metadata: Dict[str, Any] = field(default_factory=dict)
      status: str = "pending"  # pending, processing, completed, failed
      translation_result: Optional[str] = None
      quality_score: Optional[float] = None
  ```
- **MIRROR**: Follow Chapter pattern from src/parsers/base.py
- **IMPORTS**: `from dataclasses import dataclass, field`, `from typing import Dict, Any, Optional`
- **GOTCHA**: Include status tracking for progress monitoring
- **VALIDATE**: Dataclass creates correctly, fields are accessible

### Task 4: Create ResultMerger Class
- **ACTION**: Create src/processors/result_merger.py with ResultMerger class
- **IMPLEMENT**:
  - `__init__(self, config: Dict[str, Any] = None)` - initialize with config
  - `merge_translations(self, chunks: List[Chunk], output_format: str) -> str` - merge translated chunks
  - `merge_quality_scores(self, chunks: List[Chunk]) -> float` - calculate overall quality score
  - `ensure_coherence(self, text: str) -> str` - ensure text coherence across chunk boundaries
  - `_smooth_boundaries(self, prev_text: str, next_text: str) -> str` - smooth transitions between chunks
- **MIRROR**: Follow merge pattern from src/utils/pdf_utils.py:98-130
- **IMPORTS**:
  ```python
  from typing import Dict, Any, List
  from src.utils.logger import get_logger
  from src.utils.exceptions import FileProcessingError
  ```
- **GOTCHA**: Handle different output formats (PDF, DOCX, Markdown); preserve formatting
- **VALIDATE**: Class instantiates correctly, methods merge chunks properly

### Task 5: Create LargeFileProcessor Class
- **ACTION**: Create src/processors/large_file_processor.py with LargeFileProcessor class
- **IMPLEMENT**:
  - `__init__(self, translator, evaluator, improver, config: Dict[str, Any] = None)` - initialize with dependencies
  - `process_large_file(self, file_path: str, source_language: str, target_language: str) -> ProcessingResult` - main processing flow
  - `_process_chunk(self, chunk: Chunk, source_language: str, target_language: str) -> Chunk` - process single chunk
  - `_process_chunks_parallel(self, chunks: List[Chunk], source_language: str, target_language: str) -> List[Chunk]` - parallel processing
  - `_track_progress(self, chunk_id: str, status: str) -> None` - track processing progress
- **MIRROR**: Follow translation flow from src/translator.py:27-100
- **IMPORTS**:
  ```python
  from typing import Dict, Any, List
  from concurrent.futures import ThreadPoolExecutor, as_completed
  from src.processors.chunk_manager import ChunkManager, Chunk
  from src.processors.result_merger import ResultMerger
  from src.utils.logger import get_logger
  from src.utils.exceptions import TranslationError
  ```
- **GOTCHA**: Use ThreadPoolExecutor for parallel processing; limit concurrent requests to avoid API rate limits
- **VALIDATE**: Class processes large files in parallel, tracks progress correctly

### Task 6: Create ProcessingResult Data Class
- **ACTION**: Add ProcessingResult dataclass to large_file_processor.py
- **IMPLEMENT**:
  ```python
  @dataclass
  class ProcessingResult:
      final_text: str
      overall_quality_score: float
      chunks_processed: int
      chunks_failed: int
      processing_time: float
      chunk_details: List[Dict[str, Any]] = field(default_factory=list)
      metadata: Dict[str, Any] = field(default_factory=dict)
  ```
- **MIRROR**: Follow EvaluationResult pattern from src/evaluators/base.py
- **IMPORTS**: `from dataclasses import dataclass, field`, `from typing import Dict, Any, List`
- **GOTCHA**: Include both successful and failed chunk counts for monitoring
- **VALIDATE**: Dataclass creates correctly, fields are accessible

### Task 7: Integrate Large File Processing into Translator
- **ACTION**: Update src/translator.py to use LargeFileProcessor
- **IMPLEMENT**:
  1. Import LargeFileProcessor
  2. In `translate_file`, check if large file processing is needed
  3. If file is large, use LargeFileProcessor instead of direct translation
  4. Return merged result with chunk statistics
- **MIRROR**: Follow integration pattern from src/translator.py:74-100
- **IMPORTS**: `from src.processors import LargeFileProcessor`
- **GOTCHA**: Only use large file processing if enabled in config and file meets threshold
- **VALIDATE**: Existing tests still pass, large files are processed correctly

### Task 8: Create Processors Module Init
- **ACTION**: Create src/processors/__init__.py
- **IMPLEMENT**:
  ```python
  """文件处理模块"""
  from src.processors.large_file_processor import LargeFileProcessor, ProcessingResult
  from src.processors.chunk_manager import ChunkManager, Chunk
  from src.processors.result_merger import ResultMerger
  
  __all__ = ['LargeFileProcessor', 'ProcessingResult', 'ChunkManager', 'Chunk', 'ResultMerger']
  ```
- **MIRROR**: Follow pattern from src/evaluators/__init__.py
- **IMPORTS**: No additional imports needed
- **GOTCHA**: Keep __all__ list up to date
- **VALIDATE**: Can import all classes from src.processors

### Task 9: Write Unit Tests for ChunkManager
- **ACTION**: Create tests/test_chunk_manager.py
- **IMPLEMENT**: Write tests for:
  1. Initialization with config
  2. should_chunk detection (small file, large file, threshold check)
  3. create_chunks for PDF with chapters
  4. create_chunks for PDF without chapters (fallback to page-based)
  5. create_chunks for DOCX
  6. create_chunks for EPUB
  7. get_chunk_info retrieval
  8. cleanup_chunks removal
- **MIRROR**: Follow test pattern from tests/test_pdf_utils.py:9-30
- **IMPORTS**:
  ```python
  import pytest
  import tempfile
  from pathlib import Path
  from src.processors import ChunkManager, Chunk
  from src.parsers.base import ParseResult, Chapter
  ```
- **GOTCHA**: Use temporary directories for chunk files; clean up after tests
- **VALIDATE**: All tests pass, edge cases covered

### Task 10: Write Unit Tests for LargeFileProcessor
- **ACTION**: Create tests/test_large_file_processor.py
- **IMPLEMENT**: Write tests for:
  1. Initialization with dependencies
  2. Processing small file (no chunking)
  3. Processing large file with chunking
  4. Parallel chunk processing
  5. Chunk failure handling and retry
  6. Result merging
  7. Progress tracking
  8. Quality score aggregation
- **MIRROR**: Follow test pattern from tests/test_translator.py
- **IMPORTS**:
  ```python
  import pytest
  from unittest.mock import Mock, patch
  from src.processors import LargeFileProcessor, ProcessingResult
  ```
- **GOTCHA**: Mock translator and evaluator to control test scenarios
- **VALIDATE**: All tests pass, parallel processing works correctly

---

## Testing Strategy

### Unit Tests

| Test | Input | Expected Output | Edge Case? |
|---|---|---|---|
| test_should_chunk_small_file | 50 pages, threshold 100 | False | No |
| test_should_chunk_large_file | 150 pages, threshold 100 | True | No |
| test_create_chunks_with_chapters | PDF with 3 chapters | 3 chunks | No |
| test_create_chunks_without_chapters | 200-page PDF, chunk_size 50 | 4 chunks | No |
| test_parallel_processing | 4 chunks, max_parallel 2 | Processed in 2 batches | No |
| test_chunk_failure_retry | 1 chunk fails, max_retries 3 | Retry 3 times | Yes |
| test_result_merging | 3 translated chunks | Single coherent text | No |
| test_quality_aggregation | Chunks with scores 85, 90, 88 | Overall score ~87.7 | No |
| test_empty_chunk | Chunk with no text | Skip or handle gracefully | Yes |
| test_boundary_smoothing | Two chunks with abrupt transition | Smoothed transition | Yes |

### Edge Cases Checklist
- [ ] File exactly at threshold size (no chunking needed)
- [ ] File just above threshold (minimal chunking)
- [ ] Very large file (1000+ pages)
- [ ] File with no chapters (fallback to page-based)
- [ ] File with many small chapters (merge small chapters)
- [ ] Chunk processing failure (retry logic)
- [ ] API rate limiting during parallel processing
- [ ] Memory constraints with large chunks
- [ ] Concurrent chunk processing limits
- [ ] Output format preservation (PDF, DOCX, Markdown)

---

## Validation Commands

### Static Analysis
```bash
# Run type checker (if mypy installed)
python -m mypy src/processors/
```
EXPECT: No type errors

### Unit Tests
```bash
# Run tests for large file processor
python -m pytest tests/test_large_file_processor.py -v
python -m pytest tests/test_chunk_manager.py -v
```
EXPECT: All tests pass

### Full Test Suite
```bash
# Run complete test suite
python -m pytest tests/ -v
```
EXPECT: No regressions, all tests pass

### Integration Test
```bash
# Test with actual large file
python -c "from src.translator import Translator; t = Translator(); result = t.translate_file('test_large.pdf'); print(result)"
```
EXPECT: Large file processed successfully with chunking

### Manual Validation
- [ ] Create test PDF with 200+ pages
- [ ] Verify file is split into chunks
- [ ] Check parallel processing occurs
- [ ] Confirm results are merged correctly
- [ ] Validate quality scores are aggregated
- [ ] Test with different output formats

---

## Acceptance Criteria
- [ ] All tasks completed
- [ ] All validation commands pass
- [ ] Tests written and passing (≥10 unit tests, ≥2 integration tests)
- [ ] No type errors
- [ ] No lint errors
- [ ] Matches UX design (automatic large file handling)
- [ ] Files >100 pages are automatically chunked
- [ ] Parallel processing works correctly
- [ ] Results are merged coherently
- [ ] Progress tracking is functional

## Completion Checklist
- [ ] Code follows discovered patterns (splitting, merging, config)
- [ ] Error handling matches codebase style (try-except, logging)
- [ ] Logging follows codebase conventions (structured logging)
- [ ] Tests follow test patterns (mocking, assertions)
- [ ] No hardcoded values (use config)
- [ ] Documentation updated (docstrings, comments)
- [ ] No unnecessary scope additions
- [ ] Self-contained — no questions needed during implementation

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| API rate limits during parallel processing | M | M | Implement request throttling and backoff |
| Memory overflow with very large files | M | H | Use streaming and limit chunk size |
| Inconsistent quality across chunks | M | M | Implement chunk context sharing |
| Merge boundary issues | M | M | Implement boundary smoothing algorithm |
| Chapter detection failure | L | M | Fallback to page-based chunking |
| Processing timeout | L | M | Implement chunk timeout and retry |

## Notes
- The large file handling system is designed to be transparent to users - they simply upload a file and get results
- Chunking is based on chapters when available, falling back to page-based splitting
- Parallel processing is limited to 4 concurrent chunks by default to avoid API rate limits
- Progress tracking enables users to monitor long-running translations
- The system prioritizes quality over speed, but parallel processing provides significant speedup
- Boundary smoothing ensures coherent text flow across chunk boundaries
- The 100-page threshold is based on typical memory constraints and API limits
