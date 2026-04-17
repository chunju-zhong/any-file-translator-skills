# Plan: Multi-API Support

## Summary
Add support for multiple translation APIs (DeepL, Google Translate) alongside the existing OpenAI-compatible translator. Enable users to choose between APIs based on cost, quality, and speed preferences.

## User Story
As a user of the translation skill, I want to choose between different translation APIs (OpenAI, DeepL, Google Translate), so that I can optimize for cost, quality, or speed based on my needs.

## Problem → Solution
**Current State**: Only OpenAI-compatible API is supported. Users cannot leverage DeepL's superior quality for European languages or Google Translate's cost-effectiveness.
**Desired State**: Users can configure and switch between multiple translation APIs, with automatic fallback and rate limiting support.

## Metadata
- **Complexity**: Medium
- **Source PRD**: `.claude/PRPs/prds/any-file-translator.prd.md`
- **PRD Phase**: Phase 8 - Multi-API Support
- **Estimated Files**: 6-8 files

---

## UX Design

### Before
```
┌─────────────────────────────────────────────────────────────┐
│  User configures single API (OpenAI)                        │
│                    ↓                                        │
│  All translations use OpenAI                                │
│                    ↓                                        │
│  No fallback if API fails or rate limited                   │
└─────────────────────────────────────────────────────────────┘
```

### After
```
┌─────────────────────────────────────────────────────────────┐
│  User configures multiple APIs with priorities              │
│                    ↓                                        │
│  System selects best API based on:                          │
│  - Language pair support                                    │
│  - Cost preferences                                         │
│  - Rate limit status                                        │
│                    ↓                                        │
│  Automatic fallback on failure/rate limit                   │
└─────────────────────────────────────────────────────────────┘
```

### Interaction Changes
| Touchpoint | Before | After | Notes |
|---|---|---|---|
| Config | Single API config | Multi-API config with priorities | Backward compatible |
| API Selection | Always OpenAI | Configurable default + fallback | |
| Error Handling | Fail on error | Fallback to next API | |

---

## Mandatory Reading

Files that MUST be read before implementing:

| Priority | File | Lines | Why |
|---|---|---|---|
| P0 (critical) | `src/translators/base.py` | 1-55 | Base class pattern to follow |
| P0 (critical) | `src/translators/openai_translator.py` | 1-124 | Existing implementation pattern |
| P1 (important) | `src/translators/__init__.py` | 1-58 | Registration pattern |
| P1 (important) | `src/config.py` | 1-80 | Config structure |
| P2 (reference) | `tests/test_openai_translator.py` | 1-95 | Test pattern |

## External Documentation

| Topic | Source | Key Takeaway |
|---|---|---|
| DeepL API | https://www.deepl.com/docs-api | REST API with auth_key, supports formality parameter |
| Google Translate API | https://cloud.google.com/translate/docs | REST API with API key, supports 100+ languages |
| Rate Limiting | Built-in retry decorator | Use existing `@retry` decorator |

---

## Patterns to Mirror

### NAMING_CONVENTION
// SOURCE: src/translators/openai_translator.py:10-15
```python
class OpenAITranslator(BaseTranslator):
    """OpenAI 兼容翻译器（支持 OpenAI、Azure、本地模型等）"""
    
    name = "openai"
    supported_languages = []
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

### CONFIG_PATTERN
// SOURCE: src/config.py:9-17
```python
class TranslatorSettings(BaseModel):
    """翻译服务配置"""
    api_key: str = Field(default="", description="翻译 API 密钥")
    base_url: str = Field(default="https://api.openai.com/v1", description="API 基础 URL")
    model: str = Field(default="gpt-4", description="使用的模型")
```

### TEST_STRUCTURE
// SOURCE: tests/test_openai_translator.py:9-44
```python
def test_openai_translator_translate():
    """测试 OpenAI 翻译器翻译"""
    translator = OpenAITranslator({
        "api_key": "test-key",
        "model": "gpt-4"
    })
    
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {...}
        mock_post.return_value = mock_response
        ...
```

### REGISTRATION_PATTERN
// SOURCE: src/translators/__init__.py:45-47
```python
_config = load_config()
_openai_translator = OpenAITranslator(_config.translator.model_dump())
register_translator("openai", _openai_translator, set_default=True)
```

---

## Files to Change

| File | Action | Justification |
|---|---|---|
| `src/config.py` | UPDATE | Add DeepL and Google config classes |
| `src/translators/deepl_translator.py` | CREATE | DeepL API implementation |
| `src/translators/google_translator.py` | CREATE | Google Translate API implementation |
| `src/translators/__init__.py` | UPDATE | Register new translators |
| `src/translators/selector.py` | CREATE | API selection logic with fallback |
| `tests/test_deepl_translator.py` | CREATE | DeepL translator tests |
| `tests/test_google_translator.py` | CREATE | Google translator tests |
| `tests/test_translator_selector.py` | CREATE | Selection logic tests |

## NOT Building

- Real-time API cost comparison (future enhancement)
- Custom API endpoints beyond the three supported (OpenAI, DeepL, Google)
- Translation memory/caching across APIs
- Language detection API (use existing auto-detect)

---

## Step-by-Step Tasks

### Task 1: Add DeepL Configuration
- **ACTION**: Add DeepLSettings class to config.py
- **IMPLEMENT**: 
  ```python
  class DeepLSettings(BaseModel):
      """DeepL 翻译配置"""
      enabled: bool = Field(default=False, description="是否启用 DeepL")
      api_key: str = Field(default="", description="DeepL API 密钥")
      base_url: str = Field(default="https://api.deepl.com/v2", description="API 基础 URL")
      formality: str = Field(default="default", description="正式程度: default, more, less")
      priority: int = Field(default=2, description="优先级 (1=最高)")
  ```
- **MIRROR**: CONFIG_PATTERN from src/config.py
- **IMPORTS**: `from pydantic import BaseModel, Field`
- **GOTCHA**: DeepL has different base URLs for free vs pro accounts
- **VALIDATE**: Config loads without errors, DeepLSettings accessible

### Task 2: Add Google Translate Configuration
- **ACTION**: Add GoogleTranslateSettings class to config.py
- **IMPLEMENT**:
  ```python
  class GoogleTranslateSettings(BaseModel):
      """Google Translate 翻译配置"""
      enabled: bool = Field(default=False, description="是否启用 Google Translate")
      api_key: str = Field(default="", description="Google Cloud API 密钥")
      priority: int = Field(default=3, description="优先级 (1=最高)")
  ```
- **MIRROR**: CONFIG_PATTERN from src/config.py
- **IMPORTS**: `from pydantic import BaseModel, Field`
- **GOTCHA**: Google requires Cloud project setup with Translate API enabled
- **VALIDATE**: Config loads without errors

### Task 3: Update Config Class
- **ACTION**: Add deepl and google_translate fields to Config class
- **IMPLEMENT**:
  ```python
  class Config(BaseModel):
      translator: TranslatorSettings = Field(default_factory=TranslatorSettings)
      processing: ProcessingSettings = Field(default_factory=ProcessingSettings)
      output: OutputSettings = Field(default_factory=OutputSettings)
      improvement: IterativeImprovementSettings = Field(default_factory=IterativeImprovementSettings)
      large_file: LargeFileSettings = Field(default_factory=LargeFileSettings)
      deepl: DeepLSettings = Field(default_factory=DeepLSettings)
      google_translate: GoogleTranslateSettings = Field(default_factory=GoogleTranslateSettings)
  ```
- **MIRROR**: CONFIG_PATTERN from src/config.py
- **VALIDATE**: All tests still pass

### Task 4: Create DeepL Translator
- **ACTION**: Create src/translators/deepl_translator.py
- **IMPLEMENT**: DeepLTranslator class following BaseTranslator pattern
  - `translate()` method using DeepL REST API
  - `translate_batch()` using DeepL batch endpoint
  - Proper error handling for DeepL-specific errors
  - Support for formality parameter
- **MIRROR**: OpenAITranslator pattern from src/translators/openai_translator.py
- **IMPORTS**: `import requests`, `from src.translators.base import ...`, `from src.utils.exceptions import APIError`
- **GOTCHA**: DeepL uses `auth_key` header, not `Authorization: Bearer`
- **VALIDATE**: Can instantiate DeepLTranslator, translate() works with mocked response

### Task 5: Create Google Translate Translator
- **ACTION**: Create src/translators/google_translator.py
- **IMPLEMENT**: GoogleTranslator class following BaseTranslator pattern
  - `translate()` method using Google Translate REST API
  - `translate_batch()` using batch endpoint
  - Proper error handling
- **MIRROR**: OpenAITranslator pattern from src/translators/openai_translator.py
- **IMPORTS**: `import requests`, `from src.translators.base import ...`, `from src.utils.exceptions import APIError`
- **GOTCHA**: Google uses `key` query parameter for auth
- **VALIDATE**: Can instantiate GoogleTranslator, translate() works with mocked response

### Task 6: Create Translator Selector
- **ACTION**: Create src/translators/selector.py
- **IMPLEMENT**: 
  - `TranslatorSelector` class with fallback logic
  - `select_translator()` method based on language support and priority
  - `translate_with_fallback()` method that tries APIs in order
  - Rate limit tracking per API
- **MIRROR**: Registration pattern from src/translators/__init__.py
- **IMPORTS**: `from src.translators import get_translator, list_translators`
- **GOTCHA**: Need to handle case where no translators are available
- **VALIDATE**: Selector chooses correct translator based on priority

### Task 7: Update Translators Init
- **ACTION**: Update src/translators/__init__.py to register new translators
- **IMPLEMENT**:
  ```python
  # Register DeepL if configured
  if _config.deepl.enabled and _config.deepl.api_key:
      _deepl_translator = DeepLTranslator(_config.deepl.model_dump())
      register_translator("deepl", _deepl_translator)
  
  # Register Google if configured
  if _config.google_translate.enabled and _config.google_translate.api_key:
      _google_translator = GoogleTranslator(_config.google_translate.model_dump())
      register_translator("google", _google_translator)
  ```
- **MIRROR**: REGISTRATION_PATTERN from src/translators/__init__.py
- **VALIDATE**: Translators register when config is set

### Task 8: Write DeepL Tests
- **ACTION**: Create tests/test_deepl_translator.py
- **IMPLEMENT**: Tests for:
  - Basic translation
  - API error handling
  - Batch translation
  - Formality parameter
- **MIRROR**: TEST_STRUCTURE from tests/test_openai_translator.py
- **VALIDATE**: All tests pass

### Task 9: Write Google Tests
- **ACTION**: Create tests/test_google_translator.py
- **IMPLEMENT**: Tests for:
  - Basic translation
  - API error handling
  - Batch translation
- **MIRROR**: TEST_STRUCTURE from tests/test_openai_translator.py
- **VALIDATE**: All tests pass

### Task 10: Write Selector Tests
- **ACTION**: Create tests/test_translator_selector.py
- **IMPLEMENT**: Tests for:
  - Translator selection by priority
  - Fallback on error
  - Language support checking
- **VALIDATE**: All tests pass

---

## Testing Strategy

### Unit Tests

| Test | Input | Expected Output | Edge Case? |
|---|---|---|---|
| test_deepl_translate | "Hello" | "你好" | No |
| test_deepl_api_error | Invalid key | APIError raised | Yes |
| test_google_translate | "Hello" | "你好" | No |
| test_google_api_error | Invalid key | APIError raised | Yes |
| test_selector_priority | Multiple APIs | Highest priority selected | No |
| test_selector_fallback | Primary fails | Secondary used | Yes |
| test_selector_no_translators | None enabled | ConfigurationError | Yes |

### Edge Cases Checklist
- [ ] Empty API key
- [ ] Invalid API key
- [ ] Rate limit exceeded (429)
- [ ] Network timeout
- [ ] Unsupported language pair
- [ ] All APIs fail
- [ ] No APIs configured

---

## Validation Commands

### Static Analysis
```bash
# Type check (if mypy configured)
python -m mypy src/translators/
```
EXPECT: Zero type errors

### Unit Tests
```bash
# Run new translator tests
python -m pytest tests/test_deepl_translator.py tests/test_google_translator.py tests/test_translator_selector.py -v
```
EXPECT: All new tests pass

### Full Test Suite
```bash
# Run complete test suite
python -m pytest --tb=short
```
EXPECT: No regressions, all tests pass

### Manual Validation
- [ ] Can configure DeepL API key
- [ ] Can configure Google API key
- [ ] Can switch between APIs via config
- [ ] Fallback works when primary API fails

---

## Acceptance Criteria
- [ ] All tasks completed
- [ ] All validation commands pass
- [ ] Tests written and passing (target: 15+ new tests)
- [ ] No type errors
- [ ] No lint errors
- [ ] Backward compatible with existing OpenAI config

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
| DeepL API changes | L | M | Use stable v2 API, version pin |
| Google API quota limits | M | M | Document quota limits, add rate limiting |
| Test API keys exposed | L | H | Use environment variables, mock in tests |
| Backward compatibility | L | H | Keep OpenAI as default, optional new APIs |

## Notes
- DeepL excels at European language pairs (en↔de, en↔fr, etc.)
- Google Translate supports 100+ languages but may have lower quality for technical docs
- Consider adding a "quality" rating per API for language pairs in future
- The existing `@retry` decorator handles transient failures
