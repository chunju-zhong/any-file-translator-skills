# PR Review: #7 — feat: Add multi-API support with DeepL and Google Translate

**Reviewed**: 2026-04-13
**Author**: chunju-zhong
**Branch**: feat/multi-api-support → develop
**Decision**: APPROVE

## Summary
Phase 8 implementation adds multi-API support with DeepL and Google Translate translators, plus a TranslatorSelector with priority-based selection and automatic fallback. Well-structured code with comprehensive test coverage. No critical or high-severity issues found.

## Findings

### CRITICAL
None

### HIGH
None

### MEDIUM

| File | Line | Issue | Suggestion |
|------|------|-------|------------|
| `src/translators/selector.py` | 106 | Accessing `e.status_code` without checking if attribute exists | APIError may not always have status_code; add `getattr(e, 'status_code', None)` |
| `src/translators/deepl_translator.py` | 88-93 | DeepL batch API uses `data=params` but should use `json=params` for proper serialization | Consider using `json=params` for consistency with API expectations |

### LOW

| File | Line | Issue | Suggestion |
|------|------|-------|------------|
| `src/translators/google_translator.py` | 14 | `supported_languages = []` means all languages supported | Add comment explaining this means "all languages supported" |
| `src/translators/selector.py` | 89 | Redundant check `if available else False` | The check `info.name != available[0].name` already handles this |
| `src/config.py` | 54-69 | No environment variable support for DeepL/Google API keys | Consider adding `DEEPL_API_KEY` and `GOOGLE_TRANSLATE_API_KEY` env var support |

## Validation Results

| Check | Result |
|---|---|
| Type check | Pass |
| Lint | Pass |
| Tests | Pass (30 new, 153 total) |
| Build | Pass |

## Files Reviewed

| File | Action |
|------|--------|
| `src/config.py` | Modified (+18 lines) |
| `src/translators/__init__.py` | Modified (+18 lines) |
| `src/translators/deepl_translator.py` | Added (+175 lines) |
| `src/translators/google_translator.py` | Added (+144 lines) |
| `src/translators/selector.py` | Added (+166 lines) |
| `tests/test_deepl_translator.py` | Added (+108 lines) |
| `tests/test_google_translator.py` | Added (+99 lines) |
| `tests/test_translator_selector.py` | Added (+194 lines) |

## Strengths

1. **Clean Architecture**: Well-separated concerns with distinct translator classes and selector
2. **Comprehensive Testing**: 30 new tests covering all scenarios including fallback and rate limits
3. **Proper Error Handling**: Try/except blocks with logging throughout
4. **Configuration-Driven**: Uses Pydantic models for clean configuration management
5. **Circular Import Fix**: Proper use of `TYPE_CHECKING` and lazy imports

## Recommendations

1. Consider adding environment variable support for DeepL and Google API keys (like OpenAI)
2. Add a `base_url` field to GoogleTranslateSettings for custom endpoints
3. Document the priority system in the configuration example
