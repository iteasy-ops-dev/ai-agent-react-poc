from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseTool(ABC):
    """
    모든 도구(Tool)의 기본 추상 클래스
    
    각 도구는 이 클래스를 상속받아 구현해야 함
    """
    
    # 클래스 속성 - 하위 클래스에서 정의해야 함
    name: str = ""
    description: str = ""
    parameters: Optional[Dict[str, Any]] = None
    
    def __init__(self):
        """도구 초기화"""
        if not self.name:
            raise ValueError(f"{self.__class__.__name__}: name 속성을 정의해야 합니다.")
        if not self.description:
            raise ValueError(f"{self.__class__.__name__}: description 속성을 정의해야 합니다.")
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        도구 실행 메서드
        
        Args:
            **kwargs: 도구별 필요한 인자들
            
        Returns:
            str: 실행 결과
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """
        OpenAI Function Calling 스키마 반환
        
        Returns:
            Dict: OpenAI tools 형식의 스키마
        """
        schema = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description
            }
        }
        
        if self.parameters:
            schema["function"]["parameters"] = self.parameters
            
        return schema
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """
        인자 유효성 검사
        
        Args:
            arguments (Dict): 검증할 인자들
            
        Returns:
            bool: 유효한지 여부
        """
        if not self.parameters:
            return True
            
        required = self.parameters.get("required", [])
        
        # 필수 인자 확인
        for field in required:
            if field not in arguments:
                return False
                
        return True
    
    def get_missing_arguments(self, arguments: Dict[str, Any]) -> list:
        """
        누락된 필수 인자 목록 반환
        
        Args:
            arguments (Dict): 확인할 인자들
            
        Returns:
            list: 누락된 인자 목록
        """
        if not self.parameters:
            return []
            
        required = self.parameters.get("required", [])
        missing = []
        
        for field in required:
            if field not in arguments:
                missing.append(field)
                
        return missing
    
    def __str__(self) -> str:
        """문자열 표현"""
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __repr__(self) -> str:
        """개발자용 표현"""
        return self.__str__()