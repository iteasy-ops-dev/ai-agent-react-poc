from openai import OpenAI
import requests
import json
import time
import os
from typing import List, Dict, Any, Optional, Union
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 모델명과 사용할 라이브러리 매핑
MODEL_LIBRARY_MAPPINGS = {
    # OpenAI 라이브러리 사용 모델들
    "gpt-4": "openai",           # 실제 OpenAI API
    "gpt-4": "openai",           # 실제 OpenAI API
    "gpt-3": "openai",           # 실제 OpenAI API  
    "gpt-oss": "openai",         # Ollama의 OpenAI 호환 API
    "llama": "openai",           # Ollama의 OpenAI 호환 API
    "mixtral": "openai",         # Ollama의 OpenAI 호환 API
    "codellama": "openai",       # Ollama의 OpenAI 호환 API
    
    # 각 모델의 공식 라이브러리 (향후 확장용)
    "qwen": "dashscope",              # Alibaba Qwen 공식
    "claude": "anthropic",            # Anthropic 공식
    "gemini": "google-generativeai",  # Google 공식
    "cohere": "cohere"                # Cohere 공식
}

# 라이브러리별 엔드포인트 타입
LIBRARY_ENDPOINT_TYPES = {
    "openai": ["local", "remote"],    # 로컬(Ollama) 또는 원격(OpenAI)
    "dashscope": ["remote"],          # 원격만
    "anthropic": ["remote"],          # 원격만  
    "google-generativeai": ["remote"], # 원격만
    "cohere": ["remote"]              # 원격만
}


class LLMClient:
    """
    LLM 통신을 위한 클라이언트 클래스
    모델명에 따라 적절한 공식 라이브러리를 동적으로 선택하여 통신
    """
    
    def __init__(self, endpoint: str = "http://localhost:11434", model: str = "gpt-oss:20b"):
        """
        LLM 클라이언트 초기화
        모델명에 따라 적절한 공식 라이브러리를 동적으로 선택
        
        Args:
            endpoint (str): LLM 서버 주소 (기본값: localhost:11434)
            model (str): 사용할 모델명 (기본값: gpt-oss:20b)
        """
        self.endpoint = endpoint.rstrip('/')
        self.model = model
        self.library_type = self._get_library_for_model(model)
        
        # 모델에 따라 적절한 클라이언트 동적 생성
        self.client = self._create_client(model, endpoint)
        
        # 직접 HTTP 요청용 (모델 리스트, 헬스체크 등)
        self.session = requests.Session()
        self.session.timeout = 30
    
    def _get_library_for_model(self, model: str) -> str:
        """
        모델명에서 사용할 라이브러리 결정
        
        Args:
            model (str): 모델명
            
        Returns:
            str: 사용할 라이브러리명
        """
        model_lower = model.lower()
        
        # 모델명 패턴 매칭
        for model_pattern, library in MODEL_LIBRARY_MAPPINGS.items():
            if model_pattern in model_lower:
                return library
        
        # 기본값: OpenAI 라이브러리 (가장 호환성이 높음)
        return "openai"
    
    def _create_client(self, model: str, endpoint: str):
        """
        모델과 엔드포인트에 따라 적절한 클라이언트 생성
        
        Args:
            model (str): 모델명
            endpoint (str): 엔드포인트
            
        Returns:
            클라이언트 인스턴스
        """
        library = self._get_library_for_model(model)
        
        if library == "openai":
            return self._create_openai_client(model, endpoint)
        elif library == "dashscope":
            return self._create_dashscope_client()
        elif library == "anthropic":
            return self._create_anthropic_client()
        elif library == "google-generativeai":
            return self._create_google_client()
        elif library == "cohere":
            return self._create_cohere_client()
        else:
            # 기본값: OpenAI 클라이언트
            return self._create_openai_client(model, endpoint)
    
    def _create_openai_client(self, model: str, endpoint: str):
        """OpenAI 클라이언트 생성"""
        model_lower = model.lower()
        
        # 로컬 모델 (Ollama)인지 확인
        local_models = ["gpt-oss", "llama", "mixtral", "codellama", "iteasy-gpt"]
        is_local = any(local_model in model_lower for local_model in local_models)
        
        if is_local:
            # Ollama 서버 사용
            return OpenAI(
                base_url=f"{endpoint}/v1",
                api_key="dummy"  # Ollama는 API 키 불필요
            )
        else:
            # 실제 OpenAI API 사용
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
            return OpenAI(api_key=api_key)
    
    def _create_dashscope_client(self):
        """Qwen/DashScope 클라이언트 생성 (향후 구현)"""
        raise NotImplementedError("DashScope 클라이언트는 아직 구현되지 않았습니다.")
    
    def _create_anthropic_client(self):
        """Anthropic 클라이언트 생성 (향후 구현)"""
        raise NotImplementedError("Anthropic 클라이언트는 아직 구현되지 않았습니다.")
    
    def _create_google_client(self):
        """Google AI 클라이언트 생성 (향후 구현)"""
        raise NotImplementedError("Google AI 클라이언트는 아직 구현되지 않았습니다.")
    
    def _create_cohere_client(self):
        """Cohere 클라이언트 생성 (향후 구현)"""
        raise NotImplementedError("Cohere 클라이언트는 아직 구현되지 않았습니다.")
    
    def health_check(self) -> Dict[str, Any]:
        """
        서버 연결 상태 확인
        
        Returns:
            Dict: 헬스체크 결과 (status, response_time, error 등)
        """
        start_time = time.time()
        
        try:
            # Ollama 헬스체크용 엔드포인트들 시도
            health_endpoints = [
                f"{self.endpoint}/api/tags",      # 모델 리스트 (Ollama)
                f"{self.endpoint}/api/version",   # 버전 정보 (Ollama)
                f"{self.endpoint}/v1/models"      # OpenAI 호환 모델 리스트
            ]
            
            last_error = None
            
            for url in health_endpoints:
                try:
                    response = self.session.get(url, timeout=10)
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        return {
                            "status": "healthy",
                            "response_time": round(response_time, 3),
                            "endpoint": self.endpoint,
                            "model": self.model,
                            "server_info": response.json() if response.content else None
                        }
                        
                except requests.exceptions.RequestException as e:
                    last_error = str(e)
                    continue
            
            # 모든 엔드포인트 실패
            response_time = time.time() - start_time
            return {
                "status": "unhealthy",
                "response_time": round(response_time, 3),
                "endpoint": self.endpoint,
                "model": self.model,
                "error": last_error or "All health check endpoints failed"
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "status": "error",
                "response_time": round(response_time, 3),
                "endpoint": self.endpoint,
                "model": self.model,
                "error": str(e)
            }
    
    def get_models(self) -> Dict[str, Any]:
        """
        사용 가능한 모델 목록 조회
        
        Returns:
            Dict: 모델 목록과 메타데이터
        """
        try:
            # Ollama API로 모델 리스트 조회 시도
            ollama_url = f"{self.endpoint}/api/tags"
            
            try:
                response = self.session.get(ollama_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    models = []
                    for model in data.get("models", []):
                        models.append({
                            "name": model.get("name", ""),
                            "size": model.get("size", 0),
                            "modified_at": model.get("modified_at", ""),
                            "digest": model.get("digest", ""),
                            "details": model.get("details", {})
                        })
                    
                    return {
                        "success": True,
                        "models": models,
                        "count": len(models),
                        "endpoint": self.endpoint
                    }
                    
            except (requests.exceptions.RequestException, json.JSONDecodeError):
                pass
            
            # OpenAI 호환 API로 시도
            try:
                models_response = self.client.models.list()
                
                models = []
                for model in models_response.data:
                    models.append({
                        "name": model.id,
                        "created": model.created,
                        "owned_by": model.owned_by,
                        "object": model.object
                    })
                
                return {
                    "success": True,
                    "models": models,
                    "count": len(models),
                    "endpoint": self.endpoint
                }
                
            except Exception:
                pass
            
            # 모든 방법 실패 시 기본 응답
            return {
                "success": False,
                "models": [],
                "count": 0,
                "endpoint": self.endpoint,
                "error": "Could not retrieve model list from endpoint"
            }
            
        except Exception as e:
            return {
                "success": False,
                "models": [],
                "count": 0,
                "endpoint": self.endpoint,
                "error": str(e)
            }
    
    def chat_completion(
        self, 
        messages: Union[str, List[Dict[str, str]]], 
        tools: Optional[List[Dict]] = None,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        채팅 완료 요청
        초기화시 지정한 모델을 사용하여 통신
        
        Args:
            messages: 메시지 (문자열 또는 메시지 리스트)
            tools: Function calling용 도구 정의
            stream: 스트리밍 응답 여부
            temperature: 응답 창의성 (0.0-2.0)
            max_tokens: 최대 토큰 수
            **kwargs: 추가 파라미터
            
        Returns:
            Dict: 응답 결과
        """
        try:
            # 메시지 형식 정규화
            if isinstance(messages, str):
                messages = [{"role": "user", "content": messages}]
            
            # 라이브러리 타입에 따라 다른 처리
            if self.library_type == "openai":
                return self._openai_chat_completion(messages, tools, stream, temperature, max_tokens, **kwargs)
            elif self.library_type == "dashscope":
                return self._dashscope_chat_completion(messages, tools, stream, temperature, max_tokens, **kwargs)
            elif self.library_type == "anthropic":
                return self._anthropic_chat_completion(messages, tools, stream, temperature, max_tokens, **kwargs)
            else:
                # 기본값: OpenAI 방식
                return self._openai_chat_completion(messages, tools, stream, temperature, max_tokens, **kwargs)
                
        except Exception as e:
            return {
                "success": False,
                "response": f"Error during chat completion: {str(e)}",
                "model": self.model,
                "endpoint": self.endpoint,
                "library": self.library_type,
                "error": str(e)
            }
    
    def _openai_chat_completion(self, messages, tools, stream, temperature, max_tokens, **kwargs):
        """OpenAI 방식의 채팅 완료"""

        # TODO: model에 따라 적절한 파라미터 조정 필요 (예: gpt-4o, gpt-3.5-turbo 등)
        # gpt-5 시리즈의 추론 모델일 경우, temperature는 반드시 1로 고정
        if "gpt-5" in self.model.lower():
            temperature = 1.0
        # 요청 파라미터 구성
        request_params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        
        if max_tokens:
            request_params["max_tokens"] = max_tokens
            
        if tools:
            request_params["tools"] = tools
            
        # 추가 파라미터 병합
        request_params.update(kwargs)
        
        # API 요청
        response = self.client.chat.completions.create(**request_params)

        # 추론 정보 추출
        reasoning_content = None
        if hasattr(response.choices[0].message, 'reasoning') and response.choices[0].message.reasoning:
            reasoning_content = response.choices[0].message.reasoning
            # print("-" * 30)
            # print("📊 모델 응답 정보:") 
            # print(f"🧠 추론 과정: {reasoning_content}")
            
        if stream:
            # 스트리밍 응답
            return {
                "success": True,
                "stream": response,
                "model": self.model,
                "endpoint": self.endpoint,
                "library": self.library_type
            }
        else:
            # 일반 응답
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "message": response.choices[0].message,
                "reasoning": reasoning_content,  # 추론 정보 추가
                "usage": response.usage.model_dump() if response.usage else None,
                "model": self.model,
                "endpoint": self.endpoint,
                "library": self.library_type,
                "function_result": None,  # Function calling 결과 (필요시 처리)
                "finish_reason": response.choices[0].finish_reason
            }
    
    def _dashscope_chat_completion(self, messages, tools, stream, temperature, max_tokens, **kwargs):
        """DashScope 방식의 채팅 완료 (향후 구현)"""
        raise NotImplementedError("DashScope 채팅 완료는 아직 구현되지 않았습니다.")
    
    def _anthropic_chat_completion(self, messages, tools, stream, temperature, max_tokens, **kwargs):
        """Anthropic 방식의 채팅 완료 (향후 구현)"""
        raise NotImplementedError("Anthropic 채팅 완료는 아직 구현되지 않았습니다.")
    
    def __str__(self) -> str:
        """문자열 표현"""
        return f"LLMClient(endpoint='{self.endpoint}', model='{self.model}', library='{self.library_type}')"
    
    def __repr__(self) -> str:
        """개발자용 표현"""
        return self.__str__()