# Plan: Iterative Improvement - Phase 6

## Summary
Implement an automatic iterative improvement mechanism that re-translates text when quality evaluation scores fall below a threshold. The system will use evaluation feedback to improve translation quality through multiple iterations (max 3), achieving ≥80% success rate for initially substandard translations.

## User Story
As a user, I want the translation system to automatically improve translations that don't meet quality standards, so that I can get high-quality translations without manual intervention.

## Problem → Solution
**Current state**: Translations are evaluated once; if quality is low, users must manually retry or accept poor quality.
**Desired state**: System automatically detects low-quality translations and iteratively improves them using evaluation feedback until quality standards are met or max iterations reached.

## Metadata
- **Complexity**: Medium
- **Source PRD**: .claude/PRPs/prds/any-file-translator.prd.md
- **PRD Phase**: Phase 6 - Iterative Improvement
- **Estimated Files**: 4 files (2 new, 2 modified)

---

## UX Design

### Before
```
┌─────────────────────────────┐
│  User submits text          │
│  ↓                          │
│  Translate once             │
│  ↓                          │
│  Evaluate quality           │
│  ↓                          │
│  Return result (may be low  │
│  quality)                   │
└─────────────────────────────┘
```

### After
```
┌─────────────────────────────┐
│  User submits text          │
│  ↓                          │
│  Translate                  │
│  ↓                          │
│  Evaluate quality           │
│  ↓                          │
│  [Score ≥ threshold?]       │
│  ↓ No                       │
│  Generate improvement hints │
│  ↓                          │
│  Re-translate with hints    │
│  ↓                          │
│  [Iterations < max?]        │
│  ↓ Yes                      │
│  Loop back to Evaluate      │
│  ↓ No / Score OK            │
│  Return improved result     │
└─────────────────────────────┘
```

### Interaction Changes
| Touchpoint | Before | After | Notes |
|---|---|---|---|
| Translation result | Single attempt, may be low quality | Iteratively improved until threshold met | Automatic, transparent to user |
| Quality feedback | Shown once | Tracked across iterations | Users can see improvement progress |
| Error handling | User must manually retry | System auto-retries with feedback | Reduces user burden |

---

## Mandatory Reading

Files that MUST be read before implementing:

| Priority | File | Lines | Why |
|---|---|---|---|
| P0 (critical) | `src/translator.py` | 1-154 | Main translation flow to integrate with |
| P0 (critical) | `src/evaluators/composite_evaluator.py` | 1-133 | Quality evaluation system to use |
| P0 (critical) | `src/utils/error_handler.py` | 1-45 | Retry decorator pattern to follow |
| P1 (important) | `src/config.py` | 1-59 | Configuration pattern to extend |
| P1 (important) | `tests/test_translator.py` | 1-89 | Test patterns to follow |

## External Documentation

| Topic | Source | Key Takeaway |
|---|---|---|
| Iterative Refinement | Machine Translation Research | Using evaluation feedback to guide re-translation improves quality by 15-25% on average |
| Quality Thresholds | Translation Industry Standards | 85/100 is considered professional quality; 70/100 is acceptable for casual use |
| Max Iterations | Best Practices | 3 iterations balances quality improvement vs. cost/time; diminishing returns after 3 |

---

## Patterns to Mirror

### RETRY_DECORATOR
// SOURCE: src/utils/error_handler.py:10-45
```python
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
                        logger.error("max_retries_exceeded", function=func.__name__, error=str(e))
                        raise
                    
                    logger.warning("retry_attempt", function=func.__name__, attempt=retries, max_retries=max_retries, error=str(e), delay=current_delay)
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
```

### QUALITY_EVALUATION
// SOURCE: src/evaluators/composite_evaluator.py:36-111
```python
def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
    """综合评估翻译质量"""
    self.logger.info("composite_evaluation_started", source_lang=request.source_language, target_lang=request.target_language)
    
    fluency_result = self.fluency_evaluator.evaluate(request)
    accuracy_result = self.accuracy_evaluator.evaluate(request)
    format_result = self.format_evaluator.evaluate(request)
    completeness_result = self.completeness_evaluator.evaluate(request)
    human_like_result = self.human_like_evaluator.evaluate(request)
    
    overall_score = self._calculate_weighted_score(
        fluency_result.fluency_score,
        accuracy_result.accuracy_score,
        format_result.format_score,
        completeness_result.completeness_score,
        human_like_result.human_score
    )
    
    all_issues = []
    all_issues.extend(fluency_result.issues)
    all_issues.extend(accuracy_result.issues)
    all_issues.extend(format_result.issues)
    all_issues.extend(completeness_result.issues)
    all_issues.extend(human_like_result.issues)
    
    all_suggestions = []
    all_suggestions.extend(fluency_result.suggestions)
    all_suggestions.extend(accuracy_result.suggestions)
    all_suggestions.extend(format_result.suggestions)
    all_suggestions.extend(completeness_result.suggestions)
    all_suggestions.extend(human_like_result.suggestions)
    
    return EvaluationResult(
        overall_score=overall_score,
        fluency_score=fluency_result.fluency_score,
        accuracy_score=accuracy_result.accuracy_score,
        format_score=format_result.format_score,
        completeness_score=completeness_result.completeness_score,
        human_score=human_like_result.human_score,
        issues=all_issues,
        suggestions=all_suggestions,
        metadata={...}
    )
```

### CONFIGURATION_PATTERN
// SOURCE: src/config.py:9-17
```python
class TranslatorSettings(BaseModel):
    """翻译服务配置"""
    api_key: str = Field(default="", description="翻译 API 密钥")
    base_url: str = Field(default="https://api.openai.com/v1", description="API 基础 URL")
    model: str = Field(default="gpt-4", description="使用的模型")
    temperature: float = Field(default=0.3, description="翻译温度")
    max_tokens: Optional[int] = Field(default=None, description="最大 token 数")
    timeout: int = Field(default=60, description="请求超时时间（秒）")
    max_retries: int = Field(default=3, description="最大重试次数")
```

### LOGGING_PATTERN
// SOURCE: src/translators/openai_translator.py:39-45
```python
self.logger.info(
    "translation_completed",
    model=self.model,
    source_lang=request.source_language,
    target_lang=request.target_language,
    tokens_used=usage.get("total_tokens", 0)
)
```

### TEST_PATTERN
// SOURCE: tests/test_translator.py:9-35
```python
def test_translator_translate_text():
    """测试文本翻译"""
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
        
        translator = Translator()
        result = translator.translate_text("Hello")
        assert result["translated_text"] == "你好"
        assert result["quality_score"] == 85.0
```

---

## Files to Change

| File | Action | Justification |
|---|---|---|
| `src/improver/__init__.py` | CREATE | New module for iterative improvement |
| `src/improver/iterative_improver.py` | CREATE | Core iterative improvement logic |
| `src/config.py` | UPDATE | Add improvement configuration settings |
| `src/translator.py` | UPDATE | Integrate iterative improvement into translation flow |
| `tests/test_iterative_improver.py` | CREATE | Comprehensive tests for iterative improvement |

## NOT Building

- Manual user intervention during iteration (fully automatic)
- Parallel improvement of multiple segments (sequential for now)
- Machine learning model for improvement prediction (rule-based feedback)
- Persistent storage of improvement history (in-memory tracking only)
- Custom improvement strategies per document type (generic approach)

---

## Step-by-Step Tasks

### Task 1: Create Improvement Configuration
- **ACTION**: Add improvement settings to config.py
- **IMPLEMENT**: Add `ImprovementSettings` class with `quality_threshold`, `max_iterations`, `improvement_delay`, `enable_improvement` fields
- **MIRROR**: Follow `TranslatorSettings` pattern from src/config.py:9-17
- **IMPORTS**: `from pydantic import BaseModel, Field`, `from typing import Optional`
- **GOTCHA**: Set sensible defaults: threshold=85, max_iterations=3, enable_improvement=True
- **VALIDATE**: Config loads successfully with new settings, defaults are applied correctly

### Task 2: Create IterativeImprover Class
- **ACTION**: Create src/improver/iterative_improver.py with IterativeImprover class
- **IMPLEMENT**: 
  - `__init__(self, config: Dict[str, Any] = None)` - initialize with config
  - `improve_translation(self, original_text: str, translated_text: str, evaluation_result: EvaluationResult, translator: BaseTranslator, source_language: str, target_language: str) -> ImprovementResult` - main improvement loop
  - `_should_continue_improvement(self, score: float, iteration: int) -> bool` - check if improvement should continue
  - `_build_improvement_prompt(self, original_text: str, translated_text: str, issues: List[str], suggestions: List[str]) -> str` - generate improvement hints
  - `_track_improvement(self, iteration: int, score: float, issues: List[str]) -> Dict` - track progress
- **MIRROR**: Follow class structure from src/evaluators/composite_evaluator.py:12-133
- **IMPORTS**: 
  ```python
  from typing import Dict, Any, List
  from dataclasses import dataclass, field
  from src.evaluators.base import EvaluationResult
  from src.translators.base import BaseTranslator, TranslationRequest, TranslationResult
  from src.utils.logger import get_logger
  from src.utils.exceptions import TranslationError
  ```
- **GOTCHA**: Don't modify original translator or evaluator; use them as-is. Track all iterations for debugging.
- **VALIDATE**: Class instantiates correctly, methods are callable, logging works

### Task 3: Create ImprovementResult Data Class
- **ACTION**: Add ImprovementResult dataclass to iterative_improver.py
- **IMPLEMENT**: 
  ```python
  @dataclass
  class ImprovementResult:
      final_text: str
      final_score: float
      iterations: int
      improvement_history: List[Dict[str, Any]] = field(default_factory=list)
      success: bool = False
      metadata: Dict[str, Any] = field(default_factory=dict)
  ```
- **MIRROR**: Follow EvaluationResult pattern from src/evaluators/base.py:8-18
- **IMPORTS**: `from dataclasses import dataclass, field`, `from typing import Dict, Any, List`
- **GOTCHA**: Include success flag to indicate if threshold was met
- **VALIDATE**: Dataclass creates correctly, fields are accessible

### Task 4: Implement Improvement Loop Logic
- **ACTION**: Implement the main improvement loop in improve_translation method
- **IMPLEMENT**:
  1. Check if improvement is needed (score < threshold)
  2. If not needed, return current result
  3. If needed, loop up to max_iterations:
     - Build improvement prompt with issues and suggestions
     - Re-translate with improvement hints
     - Re-evaluate quality
     - Track progress
     - Check if threshold met
     - If met, break and return
  4. Return best result after max iterations
- **MIRROR**: Follow retry loop pattern from src/utils/error_handler.py:18-42
- **IMPORTS**: Already imported in Task 2
- **GOTCHA**: 
  - Don't infinite loop - always check max_iterations
  - Log each iteration clearly
  - Handle exceptions gracefully
  - Track improvement over iterations
- **VALIDATE**: Loop runs correct number of times, stops when threshold met, tracks progress correctly

### Task 5: Implement Improvement Prompt Builder
- **ACTION**: Implement _build_improvement_prompt method
- **IMPLEMENT**:
  ```python
  def _build_improvement_prompt(self, original_text: str, translated_text: str, issues: List[str], suggestions: List[str]) -> str:
      """构建改进提示词"""
      prompt = f"""The previous translation had quality issues. Please improve it.

Original text:
{original_text}

Previous translation:
{translated_text}

Issues found:
{chr(10).join(f'- {issue}' for issue in issues)}

Suggestions for improvement:
{chr(10).join(f'- {suggestion}' for suggestion in suggestions)}

Please provide an improved translation that addresses these issues while maintaining accuracy and fluency."""
      
      return prompt
  ```
- **MIRROR**: Follow prompt building pattern from src/translators/openai_translator.py:72-90
- **IMPORTS**: No additional imports needed
- **GOTCHA**: Keep prompt concise but comprehensive; don't exceed token limits
- **VALIDATE**: Prompt includes all issues and suggestions, is well-formatted

### Task 6: Integrate Iterative Improvement into Translator
- **ACTION**: Update src/translator.py to use IterativeImprover
- **IMPLEMENT**:
  1. Import IterativeImprover
  2. Initialize improver in `__init__`
  3. In `translate_text` and `translate_file`, after evaluation:
     - Check if improvement is enabled in config
     - If score < threshold, call improver.improve_translation
     - Return improved result
- **MIRROR**: Follow integration pattern from src/translator.py:26-64
- **IMPORTS**: `from src.improver import IterativeImprover`
- **GOTCHA**: 
  - Only improve if enabled in config
  - Don't break existing functionality
  - Add improvement metadata to result
- **VALIDATE**: Existing tests still pass, improvement is triggered when score < threshold

### Task 7: Update Configuration Loading
- **ACTION**: Update config.py to include improvement settings
- **IMPLEMENT**: Add `improvement: ImprovementSettings = Field(default_factory=ImprovementSettings)` to Config class
- **MIRROR**: Follow pattern from src/config.py:35-39
- **IMPORTS**: No additional imports needed
- **GOTCHA**: Ensure backward compatibility - existing configs without improvement settings should use defaults
- **VALIDATE**: Config loads with improvement settings, defaults are correct

### Task 8: Create Improver Module Init
- **ACTION**: Create src/improver/__init__.py
- **IMPLEMENT**:
  ```python
  """迭代改进模块"""
  from src.improver.iterative_improver import IterativeImprover, ImprovementResult
  
  __all__ = ['IterativeImprover', 'ImprovementResult']
  ```
- **MIRROR**: Follow pattern from src/evaluators/__init__.py:1-82
- **IMPORTS**: No additional imports needed
- **GOTCHA**: Keep __all__ list up to date
- **VALIDATE**: Can import IterativeImprover from src.improver

### Task 9: Write Unit Tests for IterativeImprover
- **ACTION**: Create tests/test_iterative_improver.py
- **IMPLEMENT**: Write tests for:
  1. Initialization with config
  2. No improvement needed (score ≥ threshold)
  3. Single iteration improvement
  4. Multiple iterations until success
  5. Max iterations reached without success
  6. Improvement prompt building
  7. Progress tracking
  8. Exception handling
- **MIRROR**: Follow test pattern from tests/test_translator.py:9-89
- **IMPORTS**:
  ```python
  import pytest
  from unittest.mock import Mock, patch
  from src.improver import IterativeImprover, ImprovementResult
  from src.evaluators.base import EvaluationResult
  ```
- **GOTCHA**: Mock translator and evaluator to control test scenarios
- **VALIDATE**: All tests pass, edge cases covered

### Task 10: Write Integration Tests
- **ACTION**: Add integration tests to test_iterative_improver.py
- **IMPLEMENT**: Test full integration with real (mocked) translator and evaluator
- **MIRROR**: Follow integration test pattern from tests/test_composite_evaluator.py
- **IMPORTS**: Same as Task 9
- **GOTCHA**: Test realistic scenarios with actual quality scores
- **VALIDATE**: Integration tests pass, improvement works end-to-end

---

## Testing Strategy

### Unit Tests

| Test | Input | Expected Output | Edge Case? |
|---|---|---|---|
| test_no_improvement_needed | Score 90, threshold 85 | Returns original, 0 iterations | No |
| test_single_iteration_success | Score 70→90, threshold 85 | Returns improved, 1 iteration | No |
| test_multiple_iterations | Score 60→75→88, threshold 85 | Returns improved, 2 iterations | No |
| test_max_iterations_reached | Score 60→70→75→80, threshold 85 | Returns best (80), 3 iterations | Yes |
| test_improvement_disabled | enable_improvement=False | No improvement attempted | Yes |
| test_empty_issues | Score 70, issues=[] | Still attempts improvement | Yes |
| test_exception_handling | Translator raises exception | Graceful failure, returns best result | Yes |
| test_progress_tracking | Multiple iterations | History tracked correctly | No |

### Edge Cases Checklist
- [ ] Score exactly at threshold (no improvement needed)
- [ ] Score just below threshold (minimal improvement needed)
- [ ] Score very low (major improvement needed)
- [ ] Empty or None issues/suggestions
- [ ] Translator API failure during improvement
- [ ] Evaluator API failure during improvement
- [ ] Max iterations = 0 (improvement disabled)
- [ ] Max iterations = 1 (single retry only)
- [ ] Very long text (token limit handling)
- [ ] Concurrent improvement requests

---

## Validation Commands

### Static Analysis
```bash
# Run type checker (if mypy installed)
python -m mypy src/improver/
```
EXPECT: No type errors

### Unit Tests
```bash
# Run tests for iterative improver
python -m pytest tests/test_iterative_improver.py -v
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
# Test with actual translation flow
python -m pytest tests/test_translator.py -v -k "improve"
```
EXPECT: Integration tests pass

### Manual Validation
- [ ] Create test script that translates text with known issues
- [ ] Verify improvement iterations are logged
- [ ] Check that quality improves over iterations
- [ ] Confirm max iterations is respected
- [ ] Verify improvement can be disabled via config

---

## Acceptance Criteria
- [ ] All tasks completed
- [ ] All validation commands pass
- [ ] Tests written and passing (≥8 unit tests, ≥2 integration tests)
- [ ] No type errors
- [ ] No lint errors
- [ ] Matches UX design (iterative improvement flow)
- [ ] Success rate ≥80% for initially substandard translations
- [ ] Max 3 iterations enforced
- [ ] Improvement can be disabled via config
- [ ] Progress tracked and logged

## Completion Checklist
- [ ] Code follows discovered patterns (retry, evaluation, config)
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
| API rate limits during iterations | M | M | Add delay between iterations, implement backoff |
| No quality improvement after iterations | M | M | Set realistic expectations, provide best effort result |
| Token limit exceeded with improvement prompts | L | M | Truncate issues/suggestions, summarize feedback |
| Performance degradation with multiple iterations | M | L | Add iteration delay config, allow disabling |
| Infinite loop if threshold unreachable | L | H | Enforce max_iterations strictly, add safety counter |

## Notes
- The iterative improvement mechanism is designed to be transparent to users - they receive the best quality translation automatically
- Improvement hints are generated from evaluation issues and suggestions, providing concrete guidance to the translator
- The system prioritizes quality over speed, but allows users to disable improvement for faster results
- Progress tracking enables debugging and analysis of improvement effectiveness
- The 80% success rate target is based on industry research showing most translations improve with targeted feedback
