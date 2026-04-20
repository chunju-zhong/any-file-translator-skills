"""DeepL 翻译器"""
import requests
from typing import Dict, Any, List
from src.translators.base import BaseTranslator, TranslationRequest, TranslationResult
from src.utils.logger import get_logger
from src.utils.exceptions import APIError
from src.utils.error_handler import retry


class DeepLTranslator(BaseTranslator):
    """DeepL 翻译器"""
    
    name = "deepl"
    supported_languages = [
        "bg", "cs", "da", "de", "el", "en", "en-gb", "en-us",
        "es", "et", "fi", "fr", "hu", "id", "it", "ja",
        "ko", "lt", "lv", "nb", "nl", "pl", "pt", "pt-br",
        "pt-pt", "ro", "ru", "sk", "sl", "sv", "tr", "uk", "zh"
    ]
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        self.api_key = self.config.get("api_key", "")
        self.base_url = self.config.get("base_url", "https://api.deepl.com/v2")
        self.formality = self.config.get("formality", "default")
        self.timeout = self.config.get("timeout", 60)
    
    @retry(max_retries=3, delay=1.0, backoff=2.0)
    def translate(self, request: TranslationRequest) -> TranslationResult:
        """翻译文本"""
        try:
            response = self._call_api(request)
            
            translated_text = response["translations"][0]["text"]
            detected_source = response["translations"][0].get("detected_source_language", request.source_language)
            
            self.logger.info(
                "translation_completed",
                translator="deepl",
                source_lang=detected_source,
                target_lang=request.target_language
            )
            
            return TranslationResult(
                text=translated_text,
                source_language=detected_source,
                target_language=request.target_language,
                model="deepl",
                usage={"character_count": len(request.text)},
                metadata={"api_response": response}
            )
        
        except requests.exceptions.Timeout:
            self.logger.error("api_timeout", timeout=self.timeout)
            raise APIError(f"DeepL API request timeout after {self.timeout}s")
        
        except requests.exceptions.RequestException as e:
            self.logger.error("api_request_error", error=str(e))
            raise APIError(f"DeepL API request failed: {e}")
        
        except (KeyError, IndexError) as e:
            self.logger.error("api_response_parse_error", error=str(e))
            raise APIError(f"Failed to parse DeepL API response: {e}")
    
    def translate_batch(self, translation_requests: List[TranslationRequest]) -> List[TranslationResult]:
        """批量翻译"""
        if not translation_requests:
            return []
        
        try:
            texts = [req.text for req in translation_requests]
            target_lang = translation_requests[0].target_language
            source_lang = translation_requests[0].source_language
            
            params = {
                "target_lang": self._map_language(target_lang),
                "text": texts
            }
            
            if source_lang and source_lang != "auto":
                params["source_lang"] = self._map_language(source_lang)
            
            if self.formality != "default":
                params["formality"] = self.formality
            
            response = requests.post(
                f"{self.base_url}/translate",
                headers=self._get_headers(),
                data=params,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise APIError(
                    f"DeepL API returned status {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
            
            results = response.json()
            
            return [
                TranslationResult(
                    text=trans["text"],
                    source_language=trans.get("detected_source_language", req.source_language),
                    target_language=req.target_language,
                    model="deepl",
                    usage={"character_count": len(req.text)},
                    metadata={}
                )
                for trans, req in zip(results["translations"], translation_requests)
            ]
        
        except requests.exceptions.Timeout:
            self.logger.error("api_timeout", timeout=self.timeout)
            raise APIError(f"DeepL API request timeout after {self.timeout}s")
        
        except requests.exceptions.RequestException as e:
            self.logger.error("api_request_error", error=str(e))
            raise APIError(f"DeepL API request failed: {e}")
    
    def _call_api(self, request: TranslationRequest) -> Dict[str, Any]:
        """调用 DeepL API"""
        params = {
            "target_lang": self._map_language(request.target_language),
            "text": [request.text]
        }
        
        if request.source_language and request.source_language != "auto":
            params["source_lang"] = self._map_language(request.source_language)
        
        if self.formality != "default":
            params["formality"] = self.formality
        
        response = requests.post(
            f"{self.base_url}/translate",
            headers=self._get_headers(),
            data=params,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            error_msg = response.text
            if response.status_code == 403:
                error_msg = "Invalid DeepL API key"
            elif response.status_code == 456:
                error_msg = "DeepL quota exceeded"
            raise APIError(
                f"DeepL API returned status {response.status_code}: {error_msg}",
                status_code=response.status_code
            )
        
        return response.json()
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"DeepL-Auth-Key {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _map_language(self, lang: str) -> str:
        """映射语言代码"""
        lang_map = {
            "zh": "ZH",
            "zh-cn": "ZH",
            "zh-tw": "ZH",
            "en": "EN",
            "en-us": "EN-US",
            "en-gb": "EN-GB",
            "pt-br": "PT-BR",
            "pt-pt": "PT-PT"
        }
        return lang_map.get(lang.lower(), lang.upper())
