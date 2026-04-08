"""自定义异常类"""


class TranslationError(Exception):
    """翻译错误基类"""
    pass


class FileProcessingError(TranslationError):
    """文件处理错误"""
    pass


class APIError(TranslationError):
    """API 调用错误"""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class ConfigurationError(TranslationError):
    """配置错误"""
    pass


class UnsupportedFormatError(FileProcessingError):
    """不支持的文件格式"""
    pass


class QualityEvaluationError(TranslationError):
    """质量评估错误"""
    pass
