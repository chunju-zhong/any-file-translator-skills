"""评估器模块"""
from typing import Dict, List, Optional
from src.evaluators.base import BaseEvaluator, EvaluationResult, EvaluationRequest
from src.evaluators.completeness_evaluator import CompletenessEvaluator
from src.evaluators.fluency_evaluator import FluencyEvaluator
from src.evaluators.accuracy_evaluator import AccuracyEvaluator
from src.evaluators.format_evaluator import FormatEvaluator
from src.evaluators.human_like_evaluator import HumanLikeEvaluator
from src.evaluators.composite_evaluator import CompositeEvaluator

_evaluators: Dict[str, BaseEvaluator] = {}
_default_evaluator: Optional[str] = None


def register_evaluator(name: str, evaluator: BaseEvaluator, set_default: bool = False):
    """注册评估器"""
    global _default_evaluator
    _evaluators[name] = evaluator
    if set_default or not _default_evaluator:
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


_completeness_evaluator = CompletenessEvaluator()
register_evaluator("completeness", _completeness_evaluator)

_fluency_evaluator = FluencyEvaluator()
register_evaluator("fluency", _fluency_evaluator)

_accuracy_evaluator = AccuracyEvaluator()
register_evaluator("accuracy", _accuracy_evaluator)

_format_evaluator = FormatEvaluator()
register_evaluator("format", _format_evaluator)

_human_like_evaluator = HumanLikeEvaluator()
register_evaluator("human_like", _human_like_evaluator)

_composite_evaluator = CompositeEvaluator()
register_evaluator("composite", _composite_evaluator, set_default=True)


__all__ = [
    'BaseEvaluator',
    'EvaluationResult',
    'EvaluationRequest',
    'CompletenessEvaluator',
    'FluencyEvaluator',
    'AccuracyEvaluator',
    'FormatEvaluator',
    'HumanLikeEvaluator',
    'CompositeEvaluator',
    'register_evaluator',
    'get_evaluator',
    'list_evaluators',
    'set_default_evaluator',
]
