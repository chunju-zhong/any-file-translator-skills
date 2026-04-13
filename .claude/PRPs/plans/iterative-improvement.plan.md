# Plan: Iterative Improvement

## Summary
Implement an automatic iterative improvement mechanism that re-translates text when quality evaluation scores fall below a configurable threshold. The system will use evaluation feedback to guide re-translation, with a maximum of 3 iterations to balance quality and efficiency.

## User Story
As a user of the translation skill, I want translations that don't meet quality standards to be automatically improved, so that I can consistently receive high-quality translations without manual intervention.

## Problem → Solution
**Current State**: Translations are evaluated once; low-quality translations are returned with issues/suggestions but not improved.  
**Desired State**: Low-quality translations are automatically re-translated with improvement guidance until they meet quality standards or max iterations are reached.

## Metadata
- **Complexity**: Medium
- **Source PRD**: `.claude/PRPs/prds/any-file-translator.prd.md`
- **PRD Phase**: Phase 6 - Iterative Improvement
- **Estimated Files**: 4-5 files

---

## UX Design

### Before
```
┌─────────────────────────────────────────────────────────────┐
│  User submits text for translation                          │
│                    ↓                                        │
│  Text is translated once                                    │
│                    ↓                                        │
│  Quality is evaluated                                       │
│                    ↓                                        │
│  Result returned (even if quality score is 60/100)         │
│  - Issues: ["Fluency issue", "Accuracy issue"]             │
│  - Suggestions: ["Improve X", "Fix Y"]                      │
│  - User must manually re-request translation                │
└─────────────────────────────────────────────────────────────┘
```

### After
```
┌─────────────────────────────────────────────────────────────┐
│  User submits text for translation                          │
│                    ↓                                        │
│  Text is translated                                         │
│                    ↓                                        │
│  Quality is evaluated                                       │
│                    ↓                                        │
│  [Score >= threshold?]                                      │
│       ↓ YES                    ↓ NO                         │
│  Return result          Generate improvement prompt         │
│                               ↓                             │
│                    Re-translate with guidance               │
│                               ↓                             │
│                    Re-evaluate quality                      │
│                               ↓                             │
│                    [Iterations < 3 and score < threshold?]  │
│                       ↓ YES          ↓ NO                   │
│                    Continue loop    Return best result      │
│                                                        │
│  Final result includes:                                     │
│  - Translation text                                         │
│  - Quality score                                            │
│  - Iteration count                                          │
│  - Improvement history (optional)                           │
└─────────────────────────────────────────────────────────────┘
```

### Interaction Changes
| Touchpoint | Before | After | Notes |
|---|---|---|---|
| Translation result | Single attempt, may be low quality | Iteratively improved until threshold met | User gets better quality automatically |
| Quality feedback | Issues/suggestions shown but not acted on | Issues/suggestions used to guide re-translation | Feedback becomes actionable |
| Processing time | Fixed (one translation + evaluation) | Variable (up to 3x translation + evaluation) | Trade-off: longer time for better quality |
| Transparency | User sees one result | User sees iteration count and improvement history | Optional verbose mode |

---

## Mandatory Reading

Files that MUST be read before implementing:

| Priority | File | Lines | Why |
|---|---|---|---|
| P0 (critical) | `src/translator.py` | 1-150 | Main translation orchestrator - where iterative improvement integrates |
| P0 (critical) | `src/evaluators/composite_evaluator.py` | 1-133 | Quality evaluation system - provides scores and suggestions |
| P0 (critical) | `src/evaluators/base.py` | 1-70 | EvaluationResult and EvaluationRequest data structures |
| P1 (important) | `src/translators/base.py` | 1-55 | TranslationRequest and TranslationResult data structures |
| P1 (important) | `src/translators/openai_translator.py` | 1-124 | How to build prompts with context |
| P2 (reference) | `src/utils/error_handler.py` | 1-45 | Retry decorator pattern |
| P2 (reference) | `src/config.py` | 1-59 | Configuration pattern with Pydantic |

## External Documentation

| Topic | Source | Key Takeaway |
|---|---|---|
| Iterative refinement | OpenAI Cookbook | Using evaluation feedback to guide re-generation improves quality by 15-20% |
| Quality thresholds | Industry practice | 85/100 is typical threshold for "acceptable" translation quality |

---

## Patterns to Mirror

Code patterns discovered in the codebase. Follow these exactly.

### NAMING_CONVENTION
```python
# SOURCE: src/evaluators/composite_evaluator.py:12-16
class CompositeEvaluator(BaseEvaluator):
    """组合评估器 - 整合所有维度的评估器"""
    
    name = "composite"
    evaluation_dimensions = ["fluency", "accuracy", "format", "completeness", "human_like"]
```
- Classes: PascalCase with descriptive name
- Class attributes: snake_case for configuration
- Methods: snake_case with descriptive names
- Docstrings: Chinese for this project

### ERROR_HANDLING
```python
# SOURCE: src/translators/openai_translator.py:56-66
except requests.exceptions.Timeout:
    self.logger.error("api_timeout", timeout=self.timeout)
    raise APIError(f"API request timeout after {self.timeout}s")

except requests.exceptions.RequestException as e:
    self.logger.error("api_request_error", error=str(e))
    raise APIError(f"API request failed: {e}")
```
- Log error with structured key-value pairs
- Raise custom exception with descriptive message
- Use existing exception classes from `src/utils/exceptions.py`

### LOGGING_PATTERN
```python
# SOURCE: src/evaluators/composite_evaluator.py:37-42
self.logger.info(
    "composite_evaluation_started",
    source_lang=request.source_language,
    target_lang=request.target_language
)
```
- Use `self.logger` from `get_logger(__name__)`
- Structured logging with event name and key-value pairs
- Log at INFO level for normal operations, ERROR for failures

### DATA_CLASS_PATTERN
```python
# SOURCE: src/evaluators/base.py:7-18
@dataclass
class EvaluationResult:
    """评估结果"""
    overall_score: float
    fluency_score: float
    accuracy_score: float
    format_score: float
    completeness_score: float
    human_score: float
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
```
- Use `@dataclass` decorator for data structures
- Include docstring in Chinese
- Use `field(default_factory=list)` for mutable defaults

### CONFIGURATION_PATTERN
```python
# SOURCE: src/config.py:9-17
class TranslatorSettings(BaseModel):
    """翻译服务配置"""
    api_key: str = Field(default="", description="翻译 API 密钥")
    base_url: str = Field(default="https://api.openai.com/v1", description="API 基础 URL")
    model: str = Field(default="gpt-4", description="使用的模型")
    temperature: float = Field(default=0.3, description="翻译温度")
```
- Use Pydantic `BaseModel` for configuration
- Include Field with default and description
- Chinese descriptions

### TEST_STRUCTURE
```python
# SOURCE: tests/test_composite_evaluator.py:34-45
@patch('src.evaluators.fluency_evaluator.FluencyEvaluator.evaluate')
@patch('src.evaluators.accuracy_evaluator.AccuracyEvaluator.evaluate')
def test_composite_evaluator_evaluate(mock_accuracy, mock_fluency):
    """测试组合评估"""
    mock_fluency.return_value = EvaluationResult(
        overall_score=90.0,
        fluency_score=90.0,
        ...
    )
```
- Use `@patch` decorator for mocking dependencies
- Descriptive test names: `test_<class>_<method>_<scenario>`
- Chinese docstrings for tests

---

## Files to Change

| File | Action | Justification |
|---|---|---|
| `src/improvers/__init__.py` | CREATE | New module for iterative improvement |
| `src/improvers/iterative_improver.py` | CREATE | Core iterative improvement logic |
| `src/config.py` | UPDATE | Add IterativeImprovementSettings |
| `src/translator.py` | UPDATE | Integrate iterative improvement into translation flow |
| `tests/test_iterative_improver.py` | CREATE | Unit tests for iterative improver |

## NOT Building

- **Parallel iterative improvement** - Each translation is improved sequentially (can be added later)
- **Machine learning-based improvement prediction** - Uses rule-based threshold, not ML
- **User-configurable improvement strategies** - Single strategy: re-translate with feedback
- **Improvement history persistence** - History is only kept in memory for the session
- **A/B testing of improvement approaches** - Single deterministic approach

---

## Step-by-Step Tasks

### Task 1: Create IterativeImprovementSettings in config.py
- **ACTION**: Add new configuration class for iterative improvement settings
- **IMPLEMENT**: Add `IterativeImprovementSettings` class with threshold, max_iterations, and enabled fields
- **MIRROR**: Follow `TranslatorSettings` pattern from `src/config.py:9-17`
- **IMPORTS**: `from pydantic import BaseModel, Field`
- **GOTCHA**: Add to main `Config` class as `improvement: IterativeImprovementSettings = Field(default_factory=IterativeImprovementSettings)`
- **VALIDATE**: Config loads successfully with default values

```python
class IterativeImprovementSettings(BaseModel):
    """迭代改进配置"""
    enabled: bool = Field(default=True, description="是否启用迭代改进")
    quality_threshold: float = Field(default=85.0, description="质量阈值（低于此值触发改进）")
    max_iterations: int = Field(default=3, description="最大迭代次数")
    track_history: bool = Field(default=False, description="是否记录改进历史")
```

### Task 2: Create IterationResult dataclass
- **ACTION**: Create dataclass to hold iteration result data
- **IMPLEMENT**: Create `IterationResult` dataclass with translation_text, quality_score, issues, suggestions, and iteration_number
- **MIRROR**: Follow `EvaluationResult` pattern from `src/evaluators/base.py:7-18`
- **IMPORTS**: `from dataclasses import dataclass, field` and `from typing import List, Dict, Any`
- **GOTCHA**: Include `improvement_prompt: Optional[str]` to track what guidance was given
- **VALIDATE**: Dataclass can be instantiated with all fields

```python
@dataclass
class IterationResult:
    """单次迭代结果"""
    translation_text: str
    quality_score: float
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    iteration_number: int = 0
    improvement_prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Task 3: Create IterativeImprover class
- **ACTION**: Create main iterative improvement class
- **IMPLEMENT**: Create `IterativeImprover` class with `improve` method that orchestrates the improvement loop
- **MIRROR**: Follow `CompositeEvaluator` class structure from `src/evaluators/composite_evaluator.py:12-35`
- **IMPORTS**: Import translator, evaluator, logger, and data classes
- **GOTCHA**: The improver should NOT create new translator/evaluator instances, it should receive them
- **VALIDATE**: Class can be instantiated with translator and evaluator

```python
class IterativeImprover:
    """迭代改进器 - 自动改进不达标的翻译"""
    
    def __init__(
        self,
        translator: BaseTranslator,
        evaluator: BaseEvaluator,
        config: Dict[str, Any] = None
    ):
        self.translator = translator
        self.evaluator = evaluator
        self.config = config or {}
        self.logger = get_logger(__name__)
        
        self.enabled = self.config.get("enabled", True)
        self.quality_threshold = self.config.get("quality_threshold", 85.0)
        self.max_iterations = self.config.get("max_iterations", 3)
        self.track_history = self.config.get("track_history", False)
```

### Task 4: Implement improve method
- **ACTION**: Implement the main improvement loop
- **IMPLEMENT**: Create `improve` method that evaluates, checks threshold, and iterates if needed
- **MIRROR**: Follow the translation flow pattern from `src/translator.py:26-84`
- **IMPORTS**: Use existing data classes
- **GOTCHA**: Must handle the case where quality doesn't improve - return best result, not last result
- **VALIDATE**: Method returns improved translation with correct iteration count

```python
def improve(
    self,
    original_text: str,
    initial_translation: str,
    source_language: str,
    target_language: str
) -> Tuple[str, IterationResult]:
    """改进翻译直到达标或达到最大迭代次数"""
    current_translation = initial_translation
    history: List[IterationResult] = []
    best_result: Optional[IterationResult] = None
    
    for iteration in range(self.max_iterations + 1):
        # Evaluate current translation
        eval_request = EvaluationRequest(
            original_text=original_text,
            translated_text=current_translation,
            source_language=source_language,
            target_language=target_language
        )
        eval_result = self.evaluator.evaluate(eval_request)
        
        iteration_result = IterationResult(
            translation_text=current_translation,
            quality_score=eval_result.overall_score,
            issues=eval_result.issues,
            suggestions=eval_result.suggestions,
            iteration_number=iteration,
            metadata=eval_result.metadata
        )
        
        if self.track_history:
            history.append(iteration_result)
        
        # Track best result
        if best_result is None or eval_result.overall_score > best_result.quality_score:
            best_result = iteration_result
        
        # Check if threshold met
        if eval_result.overall_score >= self.quality_threshold:
            self.logger.info(
                "quality_threshold_met",
                score=eval_result.overall_score,
                threshold=self.quality_threshold,
                iterations=iteration
            )
            return current_translation, iteration_result
        
        # Generate improvement prompt and re-translate
        if iteration < self.max_iterations:
            improvement_prompt = self._build_improvement_prompt(
                eval_result, source_language, target_language
            )
            iteration_result.improvement_prompt = improvement_prompt
            
            trans_request = TranslationRequest(
                text=original_text,
                source_language=source_language,
                target_language=target_language,
                context=improvement_prompt
            )
            trans_result = self.translator.translate(trans_request)
            current_translation = trans_result.text
    
    # Return best result if threshold never met
    self.logger.info(
        "max_iterations_reached",
        best_score=best_result.quality_score,
        threshold=self.quality_threshold
    )
    return best_result.translation_text, best_result
```

### Task 5: Implement _build_improvement_prompt method
- **ACTION**: Create method to generate improvement guidance from evaluation results
- **IMPLEMENT**: Build a prompt that includes issues and suggestions for the translator
- **MIRROR**: Follow `_build_system_prompt` pattern from `src/translators/openai_translator.py:72-81`
- **IMPORTS**: None needed
- **GOTCHA**: Keep prompt concise - don't include all issues if there are too many
- **VALIDATE**: Prompt includes relevant issues and suggestions

```python
def _build_improvement_prompt(
    self,
    eval_result: EvaluationResult,
    source_language: str,
    target_language: str
) -> str:
    """构建改进提示词"""
    issues_text = "\n".join(f"- {issue}" for issue in eval_result.issues[:5])
    suggestions_text = "\n".join(f"- {suggestion}" for suggestion in eval_result.suggestions[:5])
    
    return f"""The previous translation had the following quality issues that need to be addressed:

Issues found:
{issues_text}

Improvement suggestions:
{suggestions_text}

Please re-translate the text addressing these issues while maintaining accuracy and natural flow."""
```

### Task 6: Create improvers module __init__.py
- **ACTION**: Create module init file with factory function
- **IMPLEMENT**: Create `get_improver` factory function similar to `get_translator` and `get_evaluator`
- **MIRROR**: Follow `src/translators/__init__.py` pattern
- **IMPORTS**: Import IterativeImprover and config
- **GOTCHA**: Check if improvement is enabled in config before returning active improver
- **VALIDATE**: Factory function returns correct instance

```python
"""迭代改进模块"""
from typing import Dict, Any, Optional
from src.improvers.iterative_improver import IterativeImprover


def get_improver(
    translator,
    evaluator,
    config: Optional[Dict[str, Any]] = None
) -> IterativeImprover:
    """获取迭代改进器实例"""
    return IterativeImprover(translator, evaluator, config)
```

### Task 7: Integrate into Translator class
- **ACTION**: Update Translator class to use iterative improvement
- **IMPLEMENT**: Modify `translate_file` and `translate_text` methods to use IterativeImprover
- **MIRROR**: Follow existing translation flow pattern
- **IMPORTS**: Import IterativeImprover and related classes
- **GOTCHA**: Only use improver if enabled in config; add iteration info to result metadata
- **VALIDATE**: Translation results include iteration information when improvement occurs

```python
# In translate_file method, after evaluation:
if self.config.improvement.enabled:
    improver = get_improver(
        self.translator,
        self.evaluator,
        self.config.improvement.model_dump()
    )
    
    improved_text, iteration_result = improver.improve(
        original_text=parse_result.text,
        initial_translation=translation_result.text,
        source_language=source_language,
        target_language=target_language
    )
    
    translation_result.text = improved_text
    metadata["iterations"] = iteration_result.iteration_number
    metadata["quality_improved"] = iteration_result.iteration_number > 0
```

### Task 8: Write unit tests
- **ACTION**: Create comprehensive unit tests for IterativeImprover
- **IMPLEMENT**: Test improvement loop, threshold checking, max iterations, best result selection
- **MIRROR**: Follow `tests/test_composite_evaluator.py` pattern
- **IMPORTS**: pytest, unittest.mock, data classes
- **GOTCHA**: Mock translator and evaluator to control test scenarios
- **VALIDATE**: All tests pass

```python
"""迭代改进器测试"""
import pytest
from unittest.mock import Mock, patch
from src.improvers.iterative_improver import IterativeImprover, IterationResult
from src.evaluators.base import EvaluationResult, EvaluationRequest
from src.translators.base import TranslationResult, TranslationRequest


def test_iterative_improver_init():
    """测试迭代改进器初始化"""
    mock_translator = Mock()
    mock_evaluator = Mock()
    
    improver = IterativeImprover(mock_translator, mock_evaluator)
    
    assert improver.enabled == True
    assert improver.quality_threshold == 85.0
    assert improver.max_iterations == 3


def test_iterative_improver_no_improvement_needed():
    """测试质量达标时不需要改进"""
    mock_translator = Mock()
    mock_evaluator = Mock()
    mock_evaluator.evaluate.return_value = EvaluationResult(
        overall_score=90.0,
        fluency_score=90.0,
        accuracy_score=90.0,
        format_score=90.0,
        completeness_score=90.0,
        human_score=90.0,
        issues=[],
        suggestions=[],
        metadata={}
    )
    
    improver = IterativeImprover(mock_translator, mock_evaluator)
    text, result = improver.improve("Hello", "你好", "en", "zh")
    
    assert result.quality_score == 90.0
    assert result.iteration_number == 0
    mock_translator.translate.assert_not_called()


def test_iterative_improver_improves_quality():
    """测试质量改进"""
    mock_translator = Mock()
    mock_evaluator = Mock()
    
    # First evaluation: low quality
    # Second evaluation: high quality
    mock_evaluator.evaluate.side_effect = [
        EvaluationResult(
            overall_score=70.0,
            fluency_score=70.0,
            accuracy_score=70.0,
            format_score=70.0,
            completeness_score=70.0,
            human_score=70.0,
            issues=["Issue 1"],
            suggestions=["Suggestion 1"],
            metadata={}
        ),
        EvaluationResult(
            overall_score=90.0,
            fluency_score=90.0,
            accuracy_score=90.0,
            format_score=90.0,
            completeness_score=90.0,
            human_score=90.0,
            issues=[],
            suggestions=[],
            metadata={}
        )
    ]
    
    mock_translator.translate.return_value = TranslationResult(
        text="改进后的翻译",
        source_language="en",
        target_language="zh",
        model="gpt-4",
        usage={},
        metadata={}
    )
    
    improver = IterativeImprover(mock_translator, mock_evaluator)
    text, result = improver.improve("Hello", "你好", "en", "zh")
    
    assert result.quality_score == 90.0
    assert result.iteration_number == 1
    mock_translator.translate.assert_called_once()


def test_iterative_improver_max_iterations():
    """测试最大迭代次数限制"""
    mock_translator = Mock()
    mock_evaluator = Mock()
    
    # Always return low quality
    mock_evaluator.evaluate.return_value = EvaluationResult(
        overall_score=70.0,
        fluency_score=70.0,
        accuracy_score=70.0,
        format_score=70.0,
        completeness_score=70.0,
        human_score=70.0,
        issues=["Issue"],
        suggestions=["Suggestion"],
        metadata={}
    )
    
    mock_translator.translate.return_value = TranslationResult(
        text="翻译",
        source_language="en",
        target_language="zh",
        model="gpt-4",
        usage={},
        metadata={}
    )
    
    improver = IterativeImprover(mock_translator, mock_evaluator, {"max_iterations": 2})
    text, result = improver.improve("Hello", "你好", "en", "zh")
    
    assert result.iteration_number == 2
    assert mock_translator.translate.call_count == 2


def test_iterative_improver_returns_best_result():
    """测试返回最佳结果"""
    mock_translator = Mock()
    mock_evaluator = Mock()
    
    # Quality goes down then up - should return best
    mock_evaluator.evaluate.side_effect = [
        EvaluationResult(overall_score=70.0, fluency_score=70.0, accuracy_score=70.0, format_score=70.0, completeness_score=70.0, human_score=70.0, issues=[], suggestions=[], metadata={}),
        EvaluationResult(overall_score=60.0, fluency_score=60.0, accuracy_score=60.0, format_score=60.0, completeness_score=60.0, human_score=60.0, issues=[], suggestions=[], metadata={}),
        EvaluationResult(overall_score=75.0, fluency_score=75.0, accuracy_score=75.0, format_score=75.0, completeness_score=75.0, human_score=75.0, issues=[], suggestions=[], metadata={}),
    ]
    
    mock_translator.translate.return_value = TranslationResult(
        text="翻译",
        source_language="en",
        target_language="zh",
        model="gpt-4",
        usage={},
        metadata={}
    )
    
    improver = IterativeImprover(mock_translator, mock_evaluator, {"max_iterations": 2})
    text, result = improver.improve("Hello", "你好", "en", "zh")
    
    # Should return the best score (75.0 from iteration 2)
    assert result.quality_score == 75.0
```

---

## Testing Strategy

### Unit Tests

| Test | Input | Expected Output | Edge Case? |
|---|---|---|---|
| test_iterative_improver_init | Default config | Instance with default values | No |
| test_iterative_improver_no_improvement_needed | Score 90 > threshold 85 | Returns immediately, no re-translation | No |
| test_iterative_improver_improves_quality | Score 70 → 90 | Re-translates once, returns improved | No |
| test_iterative_improver_max_iterations | Score always 70 | Stops at max_iterations | No |
| test_iterative_improver_returns_best_result | Scores: 70, 60, 75 | Returns best (75) not last (60) | Yes |
| test_iterative_improver_disabled | enabled=False | No improvement attempted | Yes |
| test_iterative_improver_custom_threshold | threshold=95 | Triggers improvement at higher score | Yes |
| test_iterative_improver_history_tracking | track_history=True | History populated | Yes |

### Edge Cases Checklist
- [x] Quality already above threshold - no improvement needed
- [x] Quality never improves - return best result
- [x] Quality degrades - return best result, not last
- [x] Max iterations reached - stop and return best
- [x] Improvement disabled - skip improvement logic
- [x] Empty issues/suggestions - handle gracefully
- [x] Very long issues list - truncate in prompt

---

## Validation Commands

### Static Analysis
```bash
# Run type checker
python -m mypy src/improvers/ --ignore-missing-imports
```
EXPECT: Zero type errors

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
EXPECT: No regressions

### Integration Test
```bash
# Test with actual translation (requires API key)
python -c "
from src.translator import Translator
t = Translator()
result = t.translate_text('This is a test translation.', 'en', 'zh')
print(f'Quality: {result[\"quality_score\"]}')
print(f'Iterations: {result[\"metadata\"].get(\"iterations\", 0)}')
"
```
EXPECT: Translation completes with quality score and iteration count

### Manual Validation
- [ ] Translate a text with intentional issues
- [ ] Verify improvement iterations are logged
- [ ] Check that final quality score is reported
- [ ] Confirm metadata includes iteration information

---

## Acceptance Criteria
- [ ] All tasks completed
- [ ] All validation commands pass
- [ ] Tests written and passing
- [ ] No type errors
- [ ] No lint errors
- [ ] Integration with Translator class works
- [ ] Quality threshold is configurable
- [ ] Max iterations is configurable
- [ ] Best result is returned when threshold not met

## Completion Checklist
- [ ] Code follows discovered patterns
- [ ] Error handling matches codebase style
- [ ] Logging follows codebase conventions
- [ ] Tests follow test patterns
- [ ] No hardcoded values
- [ ] Configuration uses Pydantic models
- [ ] Self-contained — no questions needed during implementation

## Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| API rate limits during iteration | M | M | Add delay between iterations, configurable max |
| Quality doesn't improve | M | L | Return best result, log for analysis |
| Long processing time | M | M | Make iteration count configurable, add progress logging |
| Improvement prompt too long | L | L | Truncate issues/suggestions to top 5 |

## Notes
- The improvement mechanism uses the existing `context` parameter in `TranslationRequest` to pass improvement guidance
- History tracking is optional and disabled by default to minimize memory usage
- The best result tracking ensures users always get the best translation, even if later iterations are worse
- Consider adding a "fast mode" that skips improvement for time-sensitive use cases (future enhancement)
