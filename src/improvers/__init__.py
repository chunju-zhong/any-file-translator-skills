"""迭代改进模块"""
from typing import Dict, Any, Optional

from src.improvers.iterative_improver import IterativeImprover, IterationResult


def get_improver(
    translator,
    evaluator,
    config: Optional[Dict[str, Any]] = None
) -> IterativeImprover:
    """获取迭代改进器实例"""
    return IterativeImprover(translator, evaluator, config)
