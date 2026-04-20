"""Google Translate 翻译器"""
import requests
from typing import Dict, Any, List
from src.translators.base import BaseTranslator, TranslationRequest, TranslationResult
from src.utils.logger import get_logger
from src.utils.exceptions import APIError
from src.utils.error_handler import retry


class GoogleTranslator(BaseTranslator):
    """Google Translate 翻译器"""
    
    name = "google"
    supported_languages = []
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        self.api_key = self.config.get("api_key", "")
        self.base_url = self.config.get("base_url", "https://translation.googleapis.com/language/translate/v2")
        self.timeout = self.config.get("timeout", 60)
    
    @retry(max_retries=3, delay=1.0, backoff=2.0)
    def translate(self, request: TranslationRequest) -> TranslationResult:
        """翻译文本"""
        try:
            response = self._call_api(request)
            
            translated_text = response["data"]["translations"][0]["translatedText"]
            detected_source = response["data"]["translations"][0].get("detectedSourceLanguage", request.source_language)
            
            self.logger.info(
                "translation_completed",
                translator="google",
                source_lang=detected_source,
                target_lang=request.target_language
            )
            
            return TranslationResult(
                text=translated_text,
                source_language=detected_source,
                target_language=request.target_language,
                model="google",
                usage={"character_count": len(request.text)},
                metadata={"api_response": response}
            )
        
        except requests.exceptions.Timeout:
            self.logger.error("api_timeout", timeout=self.timeout)
            raise APIError(f"Google Translate API request timeout after {self.timeout}s")
        
        except requests.exceptions.RequestException as e:
            self.logger.error("api_request_error", error=str(e))
            raise APIError(f"Google Translate API request failed: {e}")
        
        except (KeyError, IndexError) as e:
            self.logger.error("api_response_parse_error", error=str(e))
            raise APIError(f"Failed to parse Google Translate API response: {e}")
    
    def translate_batch(self, translation_requests: List[TranslationRequest]) -> List[TranslationResult]:
        """批量翻译"""
        if not translation_requests:
            return []
        
        try:
            texts = [req.text for req in translation_requests]
            target_lang = translation_requests[0].target_language
            source_lang = translation_requests[0].source_language
            
            params = {
                "target": target_lang,
                "q": texts
            }
            
            if source_lang and source_lang != "auto":
                params["source"] = source_lang
            
            response = requests.post(
                f"{self.base_url}",
                params={"key": self.api_key},
                json=params,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise APIError(
                    f"Google Translate API returned status {response.status_code}: {response.text}",
                    status_code=response.status_code
                )
            
            results = response.json()
            
            return [
                TranslationResult(
                    text=trans["translatedText"],
                    source_language=trans.get("detectedSourceLanguage", req.source_language),
                    target_language=req.target_language,
                    model="google",
                    usage={"character_count": len(req.text)},
                    metadata={}
                )
                for trans, req in zip(results["data"]["translations"], translation_requests)
            ]
        
        except requests.exceptions.Timeout:
            self.logger.error("api_timeout", timeout=self.timeout)
            raise APIError(f"Google Translate API request timeout after {self.timeout}s")
        
        except requests.exceptions.RequestException as e:
            self.logger.error("api_request_error", error=str(e))
            raise APIError(f"Google Translate API request failed: {e}")
    
    def _call_api(self, request: TranslationRequest) -> Dict[str, Any]:
        """调用 Google Translate API"""
        params = {
            "target": request.target_language,
            "q": [request.text]
        }
        
        if request.source_language and request.source_language != "auto":
            params["source"] = request.source_language
        
        response = requests.post(
            f"{self.base_url}",
            params={"key": self.api_key},
            json=params,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            error_msg = response.text
            if response.status_code == 400:
                error_msg = "Invalid request to Google Translate API"
            elif response.status_code == 403:
                error_msg = "Invalid Google Translate API key"
            elif response.status_code == 429:
                error_msg = "Google Translate API quota exceeded"
            raise APIError(
                f"Google Translate API returned status {response.status_code}: {error_msg}",
                status_code=response.status_code
            )
        
        return response.json()
