"""OpenAI 兼容翻译器"""
import requests
from typing import Dict, Any
from src.translators.base import BaseTranslator, TranslationRequest, TranslationResult
from src.utils.logger import get_logger
from src.utils.exceptions import APIError
from src.utils.error_handler import retry


class OpenAITranslator(BaseTranslator):
    """OpenAI 兼容翻译器（支持 OpenAI、Azure、本地模型等）"""
    
    name = "openai"
    supported_languages = []
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        self.api_key = self.config.get("api_key", "")
        self.base_url = self.config.get("base_url", "https://api.openai.com/v1")
        self.model = self.config.get("model", "gpt-4")
        self.temperature = self.config.get("temperature", 0.3)
        self.max_tokens = self.config.get("max_tokens")
        self.timeout = self.config.get("timeout", 60)
    
    @retry(max_retries=3, delay=1.0, backoff=2.0)
    def translate(self, request: TranslationRequest) -> TranslationResult:
        """翻译文本"""
        try:
            system_prompt = self._build_system_prompt(request)
            user_prompt = self._build_user_prompt(request)
            
            response = self._call_api(system_prompt, user_prompt)
            
            translated_text = response["choices"][0]["message"]["content"]
            usage = response.get("usage", {})
            
            self.logger.info(
                "translation_completed",
                model=self.model,
                source_lang=request.source_language,
                target_lang=request.target_language,
                tokens_used=usage.get("total_tokens", 0)
            )
            
            return TranslationResult(
                text=translated_text,
                source_language=request.source_language,
                target_language=request.target_language,
                model=self.model,
                usage=usage,
                metadata={"api_response": response}
            )
        
        except requests.exceptions.Timeout:
            self.logger.error("api_timeout", timeout=self.timeout)
            raise APIError(f"API request timeout after {self.timeout}s")
        
        except requests.exceptions.RequestException as e:
            self.logger.error("api_request_error", error=str(e))
            raise APIError(f"API request failed: {e}")
        
        except (KeyError, IndexError) as e:
            self.logger.error("api_response_parse_error", error=str(e))
            raise APIError(f"Failed to parse API response: {e}")
    
    def translate_batch(self, requests: list) -> list:
        """批量翻译"""
        return [self.translate(req) for req in requests]
    
    def _build_system_prompt(self, request: TranslationRequest) -> str:
        """构建系统提示词"""
        return f"""You are a professional translator. Translate the following text from {request.source_language} to {request.target_language}.

Requirements:
1. Maintain the original meaning and tone
2. Use natural and fluent language
3. Preserve any formatting (Markdown, code blocks, etc.)
4. Keep proper nouns and technical terms accurate
5. Do not add any explanations or notes"""
    
    def _build_user_prompt(self, request: TranslationRequest) -> str:
        """构建用户提示词"""
        if request.context:
            return f"""Context: {request.context}

Text to translate:
{request.text}"""
        return request.text
    
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
