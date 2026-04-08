"""错误处理器"""
import time
import functools
from typing import Callable, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)


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
                        logger.error(
                            "max_retries_exceeded",
                            function=func.__name__,
                            error=str(e)
                        )
                        raise
                    
                    logger.warning(
                        "retry_attempt",
                        function=func.__name__,
                        attempt=retries,
                        max_retries=max_retries,
                        error=str(e),
                        delay=current_delay
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
