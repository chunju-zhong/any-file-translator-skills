# Plan: Quality Evaluation System - Phase 5

## Summary
Implement a comprehensive translation quality evaluation system with multi-dimensional scoring (fluency, accuracy, format preservation, completeness, human-likeness) using a combination of LLM-based evaluation and rule-based checks.

## User Story
As a developer using the any-file-translator skill,
I want automatic quality evaluation of translations with detailed scoring,
So that I can trust the translation quality and have clear improvement suggestions when needed.

## Problem → Solution
Current state: Only basic completeness evaluation exists → Desired state: Full multi-dimensional quality evaluation with AI-based assessment

## Metadata
- **Complexity**: Large
- **Source PRD**: .claude/PRPs/prds/any-file-translator.prd.md
- **PRD Phase**: Phase 5: Quality Evaluation System
- **Estimated Files**: 8 new files, 2 modified files

---

## UX Design

### Before
```
┌─────────────────────────────┐
│  Translation completed      │
│  Quality: 75/100            │
│  (Only completeness check)  │
│                             │
│  Issues:                    │
│  - Translation may be short │
└─────────────────────────────┘
```

### After
```
┌─────────────────────────────────────────┐
│  Translation Quality Evaluation         │
│                                         │
│  Overall Score: 87/100 ✓                │
│                                         │
│  Dimension Scores:                      │
│  • Fluency: 90/100 (Excellent)          │
│  • Accuracy: 85/100 (Good)              │
│  • Format: 88/100 (Good)                │
│  • Completeness: 92/100 (Excellent)     │
│  • Human-likeness: 82/100 (Good)        │
│                                         │
│  Issues Detected:                       │
│  • Minor terminology inconsistency      │
│  • Slight machine translation feel      │
│                                         │
│  Suggestions:                           │
│  • Review technical terms for accuracy  │
│  • Improve natural flow in paragraph 3  │
└─────────────────────────────────────────┘
```

### Interaction Changes
| Touchpoint | Before | After | Notes |
|---|---|---|---|
| Quality report | Single score | Multi-dimensional breakdown | More detailed feedback |
| Issue detection | Basic length check | Semantic and structural analysis | Deeper quality insight |
| Improvement suggestions | Generic | Specific, actionable | Better guidance for fixes |

---

## Mandatory Reading

Files that MUST be read before implementing:

| Priority | File | Lines | Why |
|---|---|---|---|
| P0 (critical) | `src/evaluators/base.py` | 1-70 | Core evaluator interface and data structures |
| P0 (critical) | `src/evaluators/completeness_evaluator.py` | 1-92 | Existing evaluator pattern to follow |
| P1 (important) | `src/evaluators/__init__.py` | 1-56 | Evaluator registration pattern |
| P1 (important) | `src/translators/openai_translator.py` | 1-124 | API calling pattern for LLM evaluation |
| P2 (reference) | `src/utils/exceptions.py` | 1-33 | Error handling patterns |
| P2 (reference) | `src/utils/logger.py` | 1-35 | Logging patterns |

## External Documentation

| Topic | Source | Key Takeaway |
|---|---|---|
| Translation Quality Metrics | BLEU, METEOR, COMET research papers | Traditional metrics focus on n-gram overlap; neural metrics (COMET) better correlate with human judgment |
| LLM-based Evaluation | GEMBA-MQM V2, RATE protocol | GPT-4 can evaluate translations with high accuracy; use structured prompts for consistency |
| Fluency vs Accuracy | Translation evaluation research | Separate dimensions: fluency (naturalness) and accuracy (adequacy) should be scored independently |
| Human-likeness | Naturalness scoring research | Machine translation often lacks natural flow; evaluate for idiomatic expressions and smooth transitions |

---

## Patterns to Mirror

Code patterns discovered in the codebase. Follow these exactly.

### NAMING_CONVENTION
// SOURCE: src/evaluators/completeness_evaluator.py:6-14
```python
class CompletenessEvaluator(BaseEvaluator):
    """完整性评估器"""
    
    name = "completeness"
    evaluation_dimensions = ["completeness"]
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.logger = get_logger(__name__)
```

### ERROR_HANDLING
// SOURCE: src/translators/openai_translator.py:56-66
```python
except requests.exceptions.Timeout:
    self.logger.error("api_timeout", timeout=self.timeout)
    raise APIError(f"API request timeout after {self.timeout}s")

except requests.exceptions.RequestException as e:
    self.logger.error("api_request_error", error=str(e))
    raise APIError(f"API request failed: {e}")

except (KeyError, IndexError) as e:
    self.logger.error("api_response_parse_error", error=str(e))
    raise APIError(f"Failed to parse API response: {e}")
```

### LOGGING_PATTERN
// SOURCE: src/evaluators/completeness_evaluator.py:32-36
```python
self.logger.info(
    "completeness_evaluation_completed",
    score=completeness_score,
    issues_count=len(issues)
)
```

### EVALUATOR_PATTERN
// SOURCE: src/evaluators/completeness_evaluator.py:16-52
```python
def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
    """评估翻译完整性"""
    completeness_score = self._calculate_completeness(
        request.original_text,
        request.translated_text
    )
    
    issues = self._detect_issues(
        request.original_text,
        request.translated_text
    )
    
    suggestions = []
    if completeness_score < 70:
        suggestions.append("翻译完整性较低，可能存在遗漏内容")
    
    return EvaluationResult(
        overall_score=completeness_score,
        fluency_score=0.0,
        accuracy_score=0.0,
        format_score=0.0,
        completeness_score=completeness_score,
        human_score=0.0,
        issues=issues,
        suggestions=suggestions,
        metadata={...}
    )
```

### TEST_STRUCTURE
// SOURCE: tests/test_completeness_evaluator.py:7-23
```python
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
```

### API_CALL_PATTERN
// SOURCE: src/translators/openai_translator.py:92-124
```python
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

---

## Files to Change

| File | Action | Justification |
|---|---|---|
| `src/evaluators/fluency_evaluator.py` | CREATE | LLM-based fluency evaluation |
| `src/evaluators/accuracy_evaluator.py` | CREATE | LLM-based accuracy evaluation |
| `src/evaluators/format_evaluator.py` | CREATE | Rule-based format preservation check |
| `src/evaluators/human_like_evaluator.py` | CREATE | LLM-based human-likeness evaluation |
| `src/evaluators/composite_evaluator.py` | CREATE | Combines all dimension evaluators |
| `src/evaluators/__init__.py` | UPDATE | Register new evaluators |
| `tests/test_fluency_evaluator.py` | CREATE | Unit tests for fluency evaluator |
| `tests/test_accuracy_evaluator.py` | CREATE | Unit tests for accuracy evaluator |
| `tests/test_format_evaluator.py` | CREATE | Unit tests for format evaluator |
| `tests/test_human_like_evaluator.py` | CREATE | Unit tests for human-likeness evaluator |
| `tests/test_composite_evaluator.py` | CREATE | Integration tests for composite evaluator |

## NOT Building

- BLEU/METEOR/COMET metric implementations (using LLM-based evaluation instead)
- Custom neural network models for evaluation (using OpenAI-compatible API)
- Real-time quality monitoring dashboard
- Translation memory integration
- Professional terminology database integration
- Human evaluation interface

---

## Step-by-Step Tasks

### Task 1: Create FluencyEvaluator
- **ACTION**: Implement LLM-based fluency evaluation
- **IMPLEMENT**: 
  - Create `src/evaluators/fluency_evaluator.py`
  - Inherit from `BaseEvaluator`
  - Implement `evaluate()` method using OpenAI-compatible API
  - Build structured prompt for fluency assessment
  - Parse LLM response to extract fluency score (0-100)
  - Detect fluency issues (grammar, clarity, readability)
- **MIRROR**: Follow `CompletenessEvaluator` pattern from `src/evaluators/completeness_evaluator.py:6-92`
- **IMPORTS**: 
  ```python
  from src.evaluators.base import BaseEvaluator, EvaluationRequest, EvaluationResult
  from src.utils.logger import get_logger
  from src.utils.exceptions import QualityEvaluationError
  import requests
  import json
  ```
- **GOTCHA**: LLM responses may not always follow expected format; implement robust JSON parsing with fallback
- **VALIDATE**: Run `pytest tests/test_fluency_evaluator.py -v` and verify all tests pass

### Task 2: Create AccuracyEvaluator
- **ACTION**: Implement LLM-based accuracy/adequacy evaluation
- **IMPLEMENT**:
  - Create `src/evaluators/accuracy_evaluator.py`
  - Inherit from `BaseEvaluator`
  - Implement `evaluate()` method using OpenAI-compatible API
  - Build structured prompt for accuracy assessment (meaning preservation, terminology correctness)
  - Parse LLM response to extract accuracy score (0-100)
  - Detect accuracy issues (mistranslation, terminology errors, meaning shifts)
- **MIRROR**: Follow `OpenAITranslator` API calling pattern from `src/translators/openai_translator.py:28-54`
- **IMPORTS**: Same as Task 1
- **GOTCHA**: Accuracy evaluation requires comparing source and target; ensure prompt includes both texts clearly
- **VALIDATE**: Run `pytest tests/test_accuracy_evaluator.py -v` and verify all tests pass

### Task 3: Create FormatEvaluator
- **ACTION**: Implement rule-based format preservation evaluation
- **IMPLEMENT**:
  - Create `src/evaluators/format_evaluator.py`
  - Inherit from `BaseEvaluator`
  - Implement `evaluate()` method using rule-based checks
  - Check Markdown formatting preservation (headers, lists, code blocks, links)
  - Check paragraph structure preservation
  - Check special characters and punctuation preservation
  - Calculate format score (0-100) based on preservation ratio
  - Detect format issues (missing headers, broken links, lost formatting)
- **MIRROR**: Follow `CompletenessEvaluator` rule-based pattern from `src/evaluators/completeness_evaluator.py:58-91`
- **IMPORTS**: 
  ```python
  from src.evaluators.base import BaseEvaluator, EvaluationRequest, EvaluationResult
  from src.utils.logger import get_logger
  import re
  ```
- **GOTCHA**: Different file formats have different formatting rules; start with Markdown and plain text
- **VALIDATE**: Run `pytest tests/test_format_evaluator.py -v` and verify all tests pass

### Task 4: Create HumanLikeEvaluator
- **ACTION**: Implement LLM-based human-likeness/naturalness evaluation
- **IMPLEMENT**:
  - Create `src/evaluators/human_like_evaluator.py`
  - Inherit from `BaseEvaluator`
  - Implement `evaluate()` method using OpenAI-compatible API
  - Build structured prompt for naturalness assessment
  - Check for machine translation artifacts (literal translations, unnatural phrasing)
  - Check for idiomatic expressions and smooth transitions
  - Parse LLM response to extract human-likeness score (0-100)
  - Detect naturalness issues (stiff language, literal translations, missing idioms)
- **MIRROR**: Follow `FluencyEvaluator` pattern (similar LLM-based approach)
- **IMPORTS**: Same as Task 1
- **GOTCHA**: Human-likeness is subjective; use clear criteria in prompt (idiomatic usage, natural flow, absence of MT artifacts)
- **VALIDATE**: Run `pytest tests/test_human_like_evaluator.py -v` and verify all tests pass

### Task 5: Create CompositeEvaluator
- **ACTION**: Implement composite evaluator that combines all dimension evaluators
- **IMPLEMENT**:
  - Create `src/evaluators/composite_evaluator.py`
  - Inherit from `BaseEvaluator`
  - Initialize all dimension evaluators (FluencyEvaluator, AccuracyEvaluator, FormatEvaluator, CompletenessEvaluator, HumanLikeEvaluator)
  - Implement `evaluate()` method that calls all dimension evaluators
  - Calculate weighted overall score using PRD weights: Fluency 30%, Accuracy 25%, Format 20%, Completeness 15%, Human-likeness 10%
  - Aggregate issues and suggestions from all evaluators
  - Implement caching to avoid redundant LLM calls
- **MIRROR**: Follow evaluator composition pattern, similar to how `Translator` uses multiple components
- **IMPORTS**:
  ```python
  from src.evaluators.base import BaseEvaluator, EvaluationRequest, EvaluationResult
  from src.evaluators.fluency_evaluator import FluencyEvaluator
  from src.evaluators.accuracy_evaluator import AccuracyEvaluator
  from src.evaluators.format_evaluator import FormatEvaluator
  from src.evaluators.completeness_evaluator import CompletenessEvaluator
  from src.evaluators.human_like_evaluator import HumanLikeEvaluator
  from src.utils.logger import get_logger
  ```
- **GOTCHA**: Calling multiple LLM evaluators can be slow and expensive; consider parallel execution or caching
- **VALIDATE**: Run `pytest tests/test_composite_evaluator.py -v` and verify all tests pass

### Task 6: Update Evaluator Registration
- **ACTION**: Register new evaluators in `__init__.py`
- **IMPLEMENT**:
  - Update `src/evaluators/__init__.py`
  - Import all new evaluator classes
  - Register `CompositeEvaluator` as the default evaluator
  - Register individual dimension evaluators for optional use
  - Update `__all__` list
- **MIRROR**: Follow existing registration pattern from `src/evaluators/__init__.py:44-45`
- **IMPORTS**: Add imports for new evaluator classes
- **GOTCHA**: Ensure backward compatibility; existing code using `get_evaluator()` should get `CompositeEvaluator`
- **VALIDATE**: Run `pytest tests/test_evaluators.py -v` and verify registration works

### Task 7: Write Unit Tests for FluencyEvaluator
- **ACTION**: Create comprehensive unit tests
- **IMPLEMENT**:
  - Create `tests/test_fluency_evaluator.py`
  - Test normal evaluation case
  - Test edge cases (empty text, very short text, very long text)
  - Test LLM API error handling
  - Test JSON parsing with malformed responses
  - Mock LLM API calls for deterministic testing
- **MIRROR**: Follow test pattern from `tests/test_completeness_evaluator.py:7-78`
- **IMPORTS**:
  ```python
  import pytest
  from unittest.mock import Mock, patch
  from src.evaluators.fluency_evaluator import FluencyEvaluator
  from src.evaluators.base import EvaluationRequest
  ```
- **GOTCHA**: LLM responses are non-deterministic; use mocking for consistent test results
- **VALIDATE**: Run `pytest tests/test_fluency_evaluator.py -v` and verify all tests pass

### Task 8: Write Unit Tests for AccuracyEvaluator
- **ACTION**: Create comprehensive unit tests
- **IMPLEMENT**:
  - Create `tests/test_accuracy_evaluator.py`
  - Test normal evaluation case
  - Test terminology accuracy detection
  - Test meaning preservation detection
  - Test edge cases and error handling
  - Mock LLM API calls
- **MIRROR**: Follow test pattern from Task 7
- **IMPORTS**: Same as Task 7 with `AccuracyEvaluator`
- **GOTCHA**: Accuracy evaluation requires both source and target; test with various language pairs
- **VALIDATE**: Run `pytest tests/test_accuracy_evaluator.py -v` and verify all tests pass

### Task 9: Write Unit Tests for FormatEvaluator
- **ACTION**: Create comprehensive unit tests
- **IMPLEMENT**:
  - Create `tests/test_format_evaluator.py`
  - Test Markdown format preservation
  - Test paragraph structure preservation
  - Test special character preservation
  - Test format score calculation
  - Test issue detection
- **MIRROR**: Follow test pattern from `tests/test_completeness_evaluator.py`
- **IMPORTS**:
  ```python
  import pytest
  from src.evaluators.format_evaluator import FormatEvaluator
  from src.evaluators.base import EvaluationRequest
  ```
- **GOTCHA**: Different formats have different rules; test with various input formats
- **VALIDATE**: Run `pytest tests/test_format_evaluator.py -v` and verify all tests pass

### Task 10: Write Unit Tests for HumanLikeEvaluator
- **ACTION**: Create comprehensive unit tests
- **IMPLEMENT**:
  - Create `tests/test_human_like_evaluator.py`
  - Test naturalness evaluation
  - Test machine translation artifact detection
  - Test idiomatic expression detection
  - Test edge cases and error handling
  - Mock LLM API calls
- **MIRROR**: Follow test pattern from Task 7
- **IMPORTS**: Same as Task 7 with `HumanLikeEvaluator`
- **GOTCHA**: Human-likeness is subjective; test with clear examples of natural vs unnatural translations
- **VALIDATE**: Run `pytest tests/test_human_like_evaluator.py -v` and verify all tests pass

### Task 11: Write Integration Tests for CompositeEvaluator
- **ACTION**: Create integration tests for composite evaluation
- **IMPLEMENT**:
  - Create `tests/test_composite_evaluator.py`
  - Test full evaluation pipeline
  - Test weighted score calculation
  - Test issue aggregation
  - Test suggestion generation
  - Test with real translation examples
  - Test performance with multiple evaluations
- **MIRROR**: Follow integration test pattern
- **IMPORTS**:
  ```python
  import pytest
  from src.evaluators.composite_evaluator import CompositeEvaluator
  from src.evaluators.base import EvaluationRequest
  ```
- **GOTCHA**: Composite evaluation may be slow; consider test timeouts and mocking
- **VALIDATE**: Run `pytest tests/test_composite_evaluator.py -v` and verify all tests pass

### Task 12: Update PRD Phase Status
- **ACTION**: Mark Phase 5 as complete in PRD
- **IMPLEMENT**:
  - Update `.claude/PRPs/prds/any-file-translator.prd.md`
  - Change Phase 5 status from `pending` to `complete`
  - Add plan file reference
- **MIRROR**: Follow existing phase completion pattern
- **IMPORTS**: None (manual file edit)
- **GOTCHA**: Ensure all tasks are complete before marking phase as complete
- **VALIDATE**: Verify PRD reflects correct status

---

## Testing Strategy

### Unit Tests

| Test | Input | Expected Output | Edge Case? |
|---|---|---|---|
| FluencyEvaluator - normal text | Well-translated text | Score 80-100, no major issues | No |
| FluencyEvaluator - poor grammar | Text with grammar errors | Score < 70, grammar issues detected | No |
| FluencyEvaluator - empty text | Empty string | Score 0, error handling | Yes |
| AccuracyEvaluator - accurate translation | Correct translation | Score 85-100, no issues | No |
| AccuracyEvaluator - mistranslation | Incorrect meaning | Score < 70, accuracy issues detected | No |
| AccuracyEvaluator - terminology error | Wrong technical term | Score < 80, terminology issue detected | No |
| FormatEvaluator - preserved format | Markdown with preserved headers | Score 90-100, no issues | No |
| FormatEvaluator - lost format | Missing headers/links | Score < 70, format issues detected | No |
| HumanLikeEvaluator - natural translation | Idiomatic, natural text | Score 80-100, no issues | No |
| HumanLikeEvaluator - MT artifacts | Literal, stiff translation | Score < 70, MT artifacts detected | No |
| CompositeEvaluator - full evaluation | Real translation | All dimension scores, weighted overall | No |
| CompositeEvaluator - low quality | Poor translation | Overall score < 70, multiple issues | No |

### Edge Cases Checklist
- [x] Empty input text
- [x] Very short text (< 10 characters)
- [x] Very long text (> 10,000 characters)
- [x] Invalid language codes
- [x] LLM API timeout
- [x] LLM API error responses
- [x] Malformed LLM JSON responses
- [x] Missing API credentials
- [x] Concurrent evaluation requests
- [x] Mixed language content

---

## Validation Commands

### Static Analysis
```bash
# Run type checker
mypy src/evaluators/
```
EXPECT: Zero type errors

### Unit Tests
```bash
# Run tests for evaluators
pytest tests/test_*_evaluator.py -v
```
EXPECT: All tests pass

### Full Test Suite
```bash
# Run complete test suite
pytest tests/ -v
```
EXPECT: No regressions

### Integration Test
```bash
# Run integration test with real translation
python -m pytest tests/test_composite_evaluator.py::test_real_translation -v
```
EXPECT: Composite evaluation completes successfully

### Manual Validation
- [ ] Test fluency evaluation with various text qualities
- [ ] Test accuracy evaluation with technical documents
- [ ] Test format evaluation with Markdown files
- [ ] Test human-likeness evaluation with MT vs human translations
- [ ] Test composite evaluation end-to-end
- [ ] Verify scoring correlation with human judgment (> 0.8)
- [ ] Test performance with large documents
- [ ] Verify error handling and logging

---

## Acceptance Criteria
- [x] All tasks completed
- [x] All validation commands pass
- [x] Tests written and passing (80%+ coverage)
- [x] No type errors
- [x] No lint errors
- [x] Matches UX design
- [x] Evaluation dimensions implemented: fluency, accuracy, format, completeness, human-likeness
- [x] Weighted scoring algorithm implemented
- [x] LLM-based evaluation working with OpenAI-compatible API
- [x] Rule-based format checking working
- [x] Issue detection and suggestion generation working
- [x] Composite evaluator integrates all dimensions
- [x] Performance acceptable (< 5 seconds for typical document)

## Completion Checklist
- [x] Code follows discovered patterns
- [x] Error handling matches codebase style
- [x] Logging follows codebase conventions
- [x] Tests follow test patterns
- [x] No hardcoded values
- [x] Documentation updated (inline comments)
- [x] No unnecessary scope additions
- [x] Self-contained — no questions needed during implementation

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM API costs high for evaluation | M | M | Implement caching, use smaller models for evaluation, batch evaluations |
| LLM evaluation inconsistent | M | M | Use structured prompts, implement retry logic, average multiple evaluations |
| Performance slow with multiple LLM calls | M | M | Implement parallel execution, caching, optional evaluation modes |
| Format detection incomplete | L | L | Start with common formats (Markdown, plain text), expand gradually |
| Human-likeness scoring subjective | M | M | Use clear criteria in prompts, validate with human evaluators |

## Notes

### Design Decisions

1. **LLM-based vs Rule-based**: 
   - Fluency, Accuracy, Human-likeness: LLM-based (semantic understanding needed)
   - Format, Completeness: Rule-based (structural checks sufficient)

2. **Scoring Weights** (from PRD):
   - Fluency: 30% (most important for readability)
   - Accuracy: 25% (critical for correctness)
   - Format: 20% (important for usability)
   - Completeness: 15% (basic requirement)
   - Human-likeness: 10% (nice to have)

3. **API Usage**:
   - Use OpenAI-compatible API for LLM evaluation
   - Reuse existing `OpenAITranslator` configuration
   - Implement caching to reduce API calls

4. **Performance Optimization**:
   - Cache evaluation results for identical text
   - Consider parallel execution for dimension evaluators
   - Provide "quick evaluation" mode (fewer dimensions)

5. **Evaluation Prompts**:
   - Use structured JSON output format
   - Include clear scoring rubrics (0-100 scale)
   - Request specific issue detection
   - Ask for improvement suggestions

### Future Enhancements

- BLEU/METEOR/COMET metrics for comparison
- Custom evaluation criteria per domain (medical, legal, technical)
- Evaluation history tracking
- A/B testing of evaluation prompts
- Integration with translation memory
- Human evaluation interface for validation
