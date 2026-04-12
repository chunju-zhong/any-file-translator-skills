"""人味评估器"""
import json
import requests
from typing import Dict, Any, List
from src.evaluators.base import BaseEvaluator, EvaluationRequest, EvaluationResult
from src.utils.logger import get_logger
from src.utils.exceptions import QualityEvaluationError
from src.utils.error_handler import retry


class HumanLikeEvaluator(BaseEvaluator):
    """人味评估器 - 使用 LLM 评估翻译的自然度和人味"""
    
    name = "human_like"
    evaluation_dimensions = ["human_like"]
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        self.api_key = self.config.get("api_key", "")
        self.base_url = self.config.get("base_url", "https://api.openai.com/v1")
        self.model = self.config.get("model", "gpt-4")
        self.temperature = self.config.get("temperature", 0.3)
        self.timeout = self.config.get("timeout", 60)
    
    @retry(max_retries=3, delay=1.0, backoff=2.0)
    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        """评估翻译人味"""
        try:
            system_prompt = self._build_system_prompt(request)
            user_prompt = self._build_user_prompt(request)
            
            response = self._call_api(system_prompt, user_prompt)
            
            evaluation_data = self._parse_response(response)
            
            human_score = evaluation_data.get("human_score", 0.0)
            issues = evaluation_data.get("issues", [])
            suggestions = evaluation_data.get("suggestions", [])
            
            self.logger.info(
                "human_like_evaluation_completed",
                score=human_score,
                issues_count=len(issues)
            )
            
            return EvaluationResult(
                overall_score=human_score,
                fluency_score=0.0,
                accuracy_score=0.0,
                format_score=0.0,
                completeness_score=0.0,
                human_score=human_score,
                issues=issues,
                suggestions=suggestions,
                metadata={
                    "model": self.model,
                    "evaluation_method": "llm_based"
                }
            )
        
        except requests.exceptions.Timeout:
            self.logger.error("api_timeout", timeout=self.timeout)
            raise QualityEvaluationError(f"API request timeout after {self.timeout}s")
        
        except requests.exceptions.RequestException as e:
            self.logger.error("api_request_error", error=str(e))
            raise QualityEvaluationError(f"API request failed: {e}")
        
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            self.logger.error("api_response_parse_error", error=str(e))
            raise QualityEvaluationError(f"Failed to parse API response: {e}")
    
    def evaluate_batch(self, requests: List[EvaluationRequest]) -> List[EvaluationResult]:
        """批量评估"""
        return [self.evaluate(req) for req in requests]
    
    def _build_system_prompt(self, request: EvaluationRequest) -> str:
        """构建系统提示词"""
        return f"""You are a professional translation quality evaluator. Evaluate the naturalness and human-likeness of the translated text.

Evaluation Criteria:
1. Natural flow (0-100) - Does the translation read like it was written by a native speaker?
2. Idiomatic usage (0-100) - Are idioms and expressions translated naturally?
3. Absence of MT artifacts (0-100) - Are there signs of machine translation (literal translations, awkward phrasing)?
4. Cultural adaptation (0-100) - Is the translation culturally appropriate for the target audience?

Output a JSON object with:
{{
  "human_score": <average score 0-100>,
  "issues": [<list of specific naturalness issues found>],
  "suggestions": [<list of improvement suggestions>]
}}

Be objective and specific in your evaluation."""
    
    def _build_user_prompt(self, request: EvaluationRequest) -> str:
        """构建用户提示词"""
        return f"""Source text ({request.source_language}):
{request.original_text}

Translated text ({request.target_language}):
{request.translated_text}

Evaluate the human-likeness and naturalness of the translation. Output only valid JSON."""
    
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
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise QualityEvaluationError(
                f"API returned status {response.status_code}: {response.text}"
            )
        
        return response.json()
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """解析 API 响应"""
        try:
            content = response["choices"][0]["message"]["content"]
            
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            evaluation_data = json.loads(content)
            
            if "human_score" not in evaluation_data:
                evaluation_data["human_score"] = 0.0
            if "issues" not in evaluation_data:
                evaluation_data["issues"] = []
            if "suggestions" not in evaluation_data:
                evaluation_data["suggestions"] = []
            
            return evaluation_data
        
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            self.logger.warning("failed_to_parse_json_response", error=str(e), response=response)
            return {
                "human_score": 0.0,
                "issues": ["Failed to parse LLM evaluation response"],
                "suggestions": ["Please check the translation manually"]
            }
