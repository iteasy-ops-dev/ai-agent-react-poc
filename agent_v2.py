import json
import time
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from core.model import LLMClient
from tools.tools_manager import ToolsManager


class ReasoningCallback(ABC):
    """
    콜백 인터페이스 - ReAct 루프의 각 단계에서 실시간 업데이트를 제공
    """
    
    @abstractmethod
    def on_iteration_start(self, iteration: int, max_iterations: int):
        """새로운 반복 시작"""
        pass
    
    @abstractmethod
    def on_reasoning(self, iteration: int, thought: str):
        """LLM의 추론 과정"""
        pass
    
    @abstractmethod
    def on_tool_call(self, iteration: int, tool: str, arguments: Dict[str, Any]):
        """도구 호출 시작"""
        pass
    
    @abstractmethod
    def on_tool_result(self, iteration: int, tool: str, result: str, success: bool):
        """도구 실행 결과"""
        pass
    
    @abstractmethod
    def on_observation(self, iteration: int, observation: str):
        """관찰 단계"""
        pass
    
    @abstractmethod
    def on_iteration_end(self, iteration: int):
        """반복 종료"""
        pass
    
    @abstractmethod
    def on_final_result(self, result: str, iterations: int):
        """최종 결과"""
        pass
    
    @abstractmethod
    def on_error(self, iteration: int, error: str):
        """오류 발생"""
        pass


class DefaultCallback(ReasoningCallback):
    """
    기본 콜백 구현 - 콘솔 출력용
    """
    
    def on_iteration_start(self, iteration: int, max_iterations: int):
        print(f"\n{'='*60}")
        print(f"🔄 반복 {iteration}/{max_iterations} 시작")
        print(f"{'='*60}")
    
    def on_reasoning(self, _iteration: int, thought: str):
        print(f"\n🤔 추론 과정:")
        print(f"   {thought}")
    
    def on_tool_call(self, _iteration: int, tool: str, arguments: Dict[str, Any]):
        print(f"\n🔧 도구 호출: {tool}")
        print(f"   인자: {json.dumps(arguments, ensure_ascii=False, indent=2)}")
    
    def on_tool_result(self, _iteration: int, _tool: str, result: str, success: bool):
        status = "✅ 성공" if success else "❌ 실패"
        print(f"\n📊 도구 결과 [{status}]:")
        preview = result[:200] + "..." if len(result) > 200 else result
        print(f"   {preview}")
    
    def on_observation(self, _iteration: int, observation: str):
        print(f"\n👁️ 관찰:")
        print(f"   {observation}")
    
    def on_iteration_end(self, iteration: int):
        print(f"\n{'='*60}")
        print(f"✅ 반복 {iteration} 완료")
        print(f"{'='*60}")
    
    def on_final_result(self, result: str, iterations: int):
        print(f"\n{'🎯'*30}")
        print(f"최종 결과 (총 {iterations}회 반복):")
        print(result)
        print(f"{'🎯'*30}")
    
    def on_error(self, iteration: int, error: str):
        print(f"\n❌ 오류 발생 (반복 {iteration}):")
        print(f"   {error}")


class ReactAgentV2:
    """
    개선된 ReAct 에이전트 - 실시간 추론 과정 표시 지원
    
    주요 개선사항:
    1. 콜백 시스템으로 실시간 업데이트 제공
    2. 추론 과정을 명확히 분리하여 표시
    3. 구조화된 실행 로그로 각 단계 추적
    """
    
    def __init__(
        self,
        endpoint: str = "http://localhost:11434",
        model: str = "gpt-oss:20b",
        max_iterations: int = 10,
        system_prompt: Optional[str] = None,
        callback: Optional[ReasoningCallback] = None,
        verbose: bool = True
    ):
        """
        ReactAgentV2 초기화
        
        Args:
            endpoint: LLM 서버 엔드포인트
            model: 사용할 모델명
            max_iterations: 최대 반복 횟수
            system_prompt: 사용자 정의 시스템 프롬프트
            callback: 실시간 업데이트를 위한 콜백 객체
            verbose: 상세 로그 출력 여부
        """
        self.endpoint = endpoint
        self.model = model
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        # 콜백 설정 (없으면 기본 콜백 사용)
        self.callback = callback or DefaultCallback()
        
        # 핵심 컴포넌트 초기화
        self.llm_client = LLMClient(endpoint=endpoint, model=model)
        self.tools_manager = ToolsManager()
        
        # 실행 상태
        self.current_iteration = 0
        self.conversation_history = []
        self.execution_log = []
        self.reasoning_history = []  # 추론 과정 저장
        self.token_usage_history = []  # 실제 토큰 사용량 저장
        
        # 시스템 프롬프트 설정
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        
        # 초기 시스템 메시지 설정
        self._initialize_conversation()
    
    def _get_default_system_prompt(self) -> str:
        """
        기본 시스템 프롬프트 생성 - 참조 파일 기반으로 개선된 체계적 프롬프트
        """
        available_tools = self.tools_manager.get_available_tools()
        tools_info = []
        
        for tool_name in available_tools:
            tool_info = self.tools_manager.get_tool_info(tool_name)
            tools_info.append(f"- {tool_name}: {tool_info.get('description', 'No description')}")
        
        tools_list = "\n".join(tools_info)
        
        return f"""
당신은 전문적인 시스템 분석 및 문제 해결 전문가입니다.
ReAct(Reasoning-Acting-Observing) 패턴을 사용하여 체계적으로 문제를 해결합니다.

## 사용 가능한 도구들:
{tools_list}

## ReAct 분석 프레임워크:
다음 5단계 추론 과정을 따라 체계적으로 문제를 해결하세요:

### 1️⃣ 관찰(Observation)
- 현재 상황 파악 및 정보 수집 계획 수립
- 필요한 정보의 우선순위 결정
- 효율적인 정보 수집 전략 수립

### 2️⃣ 분석(Analysis)
- 수집된 데이터의 패턴 분석 및 근본 원인 파악
- 상관관계 및 인과관계 식별
- 문제의 핵심 요소 추출

### 3️⃣ 계획(Planning)
- 우선순위별 다단계 조치 계획 수립
- 리스크 평가 및 대안 준비
- 단계별 검증 포인트 설정

### 4️⃣ 실행(Execution)
- 적절한 도구를 사용한 효율적 작업 수행
- 배치 처리로 여러 작업 동시 수행
- 실시간 피드백 반영

### 5️⃣ 검증(Validation)
- 결과 검증 및 목표 달성도 평가
- 추가 조치 필요성 판단
- 다음 단계 결정

## Best Practices:

### 효율적인 도구 사용:
- **배치 처리**: 가능한 여러 작업을 한 번에 수행
- **점진적 탐색**: 기본 정보 → 상세 정보 → 심화 분석 순서
- **재사용**: 이전 결과를 활용하여 중복 작업 방지

### 분석 원칙:
- **정량적 분석**: 수치와 메트릭 기반 평가
- **위험도 평가**: 높음/중간/낮음으로 우선순위 분류
- **근거 제시**: 모든 결론에 명확한 근거 제공

## 응답 구조:

### 추론 단계에서:
"🤔 현재 상황: [상황 설명]
📊 필요한 정보: [수집할 정보 목록]
🎯 다음 행동: [수행할 작업]"

### 도구 호출 시:
"🔧 도구 선택 이유: [왜 이 도구를 사용하는지]
📥 예상 결과: [기대하는 정보나 결과]"

### 관찰 단계에서:
"👁️ 수집된 정보: [핵심 발견사항]
💡 인사이트: [데이터가 의미하는 것]
➡️ 다음 단계: [추가 필요 작업]"

## 최종 보고서 형식:

1. **요약**: 핵심 발견사항과 결론
2. **상세 분석**: 
   - 수집된 데이터
   - 분석 과정
   - 주요 발견사항
3. **권장사항**: 우선순위별 조치 사항
4. **위험 요소**: 주의해야 할 점
5. **다음 단계**: 후속 작업 제안

## 중요 지침:
1. 각 반복마다 명확한 추론 과정을 먼저 제시하세요
2. 도구를 호출하기 전에 왜 그 도구를 사용하는지 설명하세요
3. 결과를 받은 후 그 의미를 해석하고 다음 단계를 계획하세요
4. 불확실한 경우 추가 정보를 수집하세요
5. 최종 답변은 체계적이고 실행 가능한 형태로 제공하세요

이제 주어진 작업을 ReAct 패턴으로 처리하겠습니다.
"""
    
    def _initialize_conversation(self):
        """대화 초기화"""
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
        self.reasoning_history = []
        self.execution_log = []
        self.token_usage_history = []  # 초기화 시에도 토큰 히스토리 리셋
    
    def run(self, user_input: str) -> Dict[str, Any]:
        """
        사용자 입력에 대해 ReAct 패턴으로 처리
        
        Args:
            user_input: 사용자 요청
            
        Returns:
            실행 결과와 메타데이터
        """
        start_time = time.time()
        self.current_iteration = 0
        self.execution_log = []
        self.reasoning_history = []
        
        # 사용자 메시지 추가
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        try:
            # ReAct 루프 실행
            final_result = self._react_loop()
            
            execution_time = time.time() - start_time
            
            # 토큰 사용량 정보 수집
            total_token_usage = self._calculate_total_token_usage()
            
            # 최종 결과 콜백
            self.callback.on_final_result(final_result, self.current_iteration)
            
            return {
                "success": True,
                "result": final_result,
                "iterations": self.current_iteration,
                "execution_time": round(execution_time, 2),
                "tools_used": [log["tool"] for log in self.execution_log if log.get("type") == "tool_call"],
                "conversation_length": len(self.conversation_history),
                "token_usage": total_token_usage,
                "reasoning_history": self.reasoning_history.copy(),
                "execution_log": self.execution_log.copy()
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"ReAct 실행 중 오류 발생: {str(e)}"
            
            self.callback.on_error(self.current_iteration, error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "iterations": self.current_iteration,
                "execution_time": round(execution_time, 2),
                "conversation_length": len(self.conversation_history),
                "tools_used": [log["tool"] for log in self.execution_log if log.get("type") == "tool_call"],
                "reasoning_history": self.reasoning_history.copy(),
                "execution_log": self.execution_log.copy()
            }
    
    def _react_loop(self) -> str:
        """
        ReAct 패턴의 핵심 루프 - 개선된 추론 과정 추적
        """
        while self.current_iteration < self.max_iterations:
            self.current_iteration += 1
            
            # 반복 시작 콜백
            self.callback.on_iteration_start(self.current_iteration, self.max_iterations)
            
            # 현재 반복 정보를 실행 로그에 추가
            iteration_log = {
                "iteration": self.current_iteration,
                "timestamp": time.time(),
                "reasoning": None,
                "tool_calls": [],
                "observations": []
            }
            
            try:
                # LLM 응답 생성
                response = self._get_llm_response()
                
                if not response.get("success", False):
                    raise Exception(f"LLM 응답 실패: {response.get('error', 'Unknown error')}")
                
                message = response.get("message")
                finish_reason = response.get("finish_reason")
                
                # 추론 과정 추출 - 실제 reasoning 속성 우선 사용
                reasoning = response.get("reasoning")  # LLM에서 제공하는 실제 reasoning
                if not reasoning:
                    # 폴백: 응답 내용에서 추론 과정 추출
                    reasoning = self._extract_reasoning(message.content)
                
                if reasoning:
                    iteration_log["reasoning"] = reasoning
                    self.reasoning_history.append({
                        "iteration": self.current_iteration,
                        "reasoning": reasoning,
                        "timestamp": time.time()
                    })
                    
                    # 추론 콜백
                    self.callback.on_reasoning(self.current_iteration, reasoning)
                
                # 대화 히스토리에 응답 추가
                self.conversation_history.append(message.model_dump())
                
                # 도구 호출이 없으면 최종 응답으로 간주
                if finish_reason != "tool_calls" or not hasattr(message, 'tool_calls'):
                    final_response = message.content or "작업이 완료되었습니다."
                    
                    # 최종 관찰 콜백
                    self.callback.on_observation(self.current_iteration, "최종 결론 도달")
                    
                    # 반복 종료 콜백
                    self.callback.on_iteration_end(self.current_iteration)
                    
                    self.execution_log.append(iteration_log)
                    return final_response
                
                # 도구 호출 처리
                tool_results = self._process_tool_calls(message.tool_calls, iteration_log)
                
                # 도구 결과에 대한 관찰
                if tool_results:
                    observation = self._generate_observation(tool_results)
                    iteration_log["observations"].append(observation)
                    
                    # 관찰 콜백
                    self.callback.on_observation(self.current_iteration, observation)
                
                # 반복 종료 콜백
                self.callback.on_iteration_end(self.current_iteration)
                
                # 실행 로그에 추가
                self.execution_log.append(iteration_log)
                
            except Exception as e:
                error_msg = f"반복 {self.current_iteration}에서 오류 발생: {str(e)}"
                
                # 오류 콜백
                self.callback.on_error(self.current_iteration, str(e))
                
                # 오류 로그 추가
                iteration_log["error"] = str(e)
                self.execution_log.append(iteration_log)
                
                # 심각한 오류가 아니면 계속 진행
                if self.current_iteration < self.max_iterations - 1:
                    continue
                else:
                    raise Exception(error_msg)
        
        # 최대 반복 횟수 도달 - 부분적인 결론 생성
        partial_conclusion = self._generate_partial_conclusion()
        
        # 경고 콜백 (부분 결론의 첫 번째 줄만 사용)
        warning_msg = partial_conclusion.split('\n')[0] if partial_conclusion else f"최대 반복 횟수 ({self.max_iterations}) 도달"
        self.callback.on_observation(self.current_iteration, warning_msg)
        
        return partial_conclusion
    
    def _extract_reasoning(self, content: Optional[str]) -> Optional[str]:
        """
        LLM 응답에서 추론 과정 추출 (폴백용)
        실제 reasoning 속성이 없을 때만 사용
        
        Args:
            content: LLM 응답 내용
            
        Returns:
            추출된 추론 과정 또는 None
        """
        if not content:
            return None
        
        # 추론 관련 키워드 패턴 (더 엄격하게)
        reasoning_patterns = [
            "🤔 현재 상황:",
            "📊 필요한 정보:",
            "🎯 다음 행동:",
            "분석:",
            "추론:",
            "계획:",
            "관찰:"
        ]
        
        # 응답에서 추론 부분 찾기
        for pattern in reasoning_patterns:
            if pattern in content:
                # 패턴이 발견되면 추론으로 간주
                return content.strip()
        
        # 더 엄격한 조건: 명확한 추론 의도가 없으면 None 반환
        # 최종 답변과 구분하기 위해
        if any(keyword in content.lower() for keyword in ["생각해보겠습니다", "분석해보겠습니다", "확인해보겠습니다"]):
            return content.strip()
        
        return None
    
    def _get_llm_response(self) -> Dict[str, Any]:
        """LLM으로부터 응답 획득"""
        # 도구 스키마 가져오기
        tools_schemas = self.tools_manager.get_tools_schemas()
        
        # LLM 호출
        response = self.llm_client.chat_completion(
            messages=self.conversation_history,
            tools=tools_schemas if tools_schemas else None,
            temperature=0.7
        )
        
        # 실제 토큰 사용량 저장 (있는 경우)
        if response.get("success") and response.get("usage"):
            usage_info = {
                "iteration": self.current_iteration,
                "timestamp": time.time(),
                "usage": response["usage"],
                "type": "llm_response"
            }
            self.token_usage_history.append(usage_info)
        
        return response
    
    def _process_tool_calls(self, tool_calls: List[Any], iteration_log: Dict) -> List[Dict]:
        """
        도구 호출들을 처리하고 결과 반환
        
        Args:
            tool_calls: 도구 호출 목록
            iteration_log: 현재 반복의 로그
            
        Returns:
            도구 실행 결과 목록
        """
        results = []
        
        for tool_call in tool_calls:
            if tool_call.type == "function":
                result = self._execute_single_tool(tool_call, iteration_log)
                results.append(result)
        
        return results
    
    def _execute_single_tool(self, tool_call, iteration_log: Dict) -> Dict:
        """
        단일 도구 실행 및 결과 반환
        
        Args:
            tool_call: 도구 호출 정보
            iteration_log: 현재 반복의 로그
            
        Returns:
            도구 실행 결과
        """
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        tool_call_id = tool_call.id
        
        # 도구 호출 콜백
        self.callback.on_tool_call(self.current_iteration, function_name, function_args)
        
        # 도구 호출 로그
        tool_log = {
            "tool": function_name,
            "arguments": function_args,
            "timestamp": time.time(),
            "tool_call_id": tool_call_id
        }
        
        try:
            # 도구 실행
            result = self.tools_manager.execute_tool(function_name, function_args)
            
            tool_log["success"] = True
            tool_log["result"] = result
            tool_log["result_length"] = len(str(result))
            
            # 도구 결과 콜백
            self.callback.on_tool_result(
                self.current_iteration,
                function_name,
                result,
                True
            )
            
            # 도구 실행 결과를 대화 히스토리에 추가
            self.conversation_history.append({
                "role": "tool",
                "content": str(result),
                "tool_call_id": tool_call_id
            })
            
        except Exception as e:
            error_msg = f"도구 실행 실패: {str(e)}"
            tool_log["success"] = False
            tool_log["error"] = str(e)
            result = error_msg
            
            # 도구 오류 콜백
            self.callback.on_tool_result(
                self.current_iteration,
                function_name,
                error_msg,
                False
            )
            
            # 오류 결과도 대화 히스토리에 추가
            self.conversation_history.append({
                "role": "tool",
                "content": f"오류: {error_msg}",
                "tool_call_id": tool_call_id
            })
        
        # 반복 로그에 도구 호출 추가
        iteration_log["tool_calls"].append(tool_log)
        
        # 전체 실행 로그에도 추가
        self.execution_log.append({
            "iteration": self.current_iteration,
            "type": "tool_call",
            **tool_log
        })
        
        return tool_log
    
    def _generate_observation(self, tool_results: List[Dict]) -> str:
        """
        도구 실행 결과로부터 관찰 생성
        
        Args:
            tool_results: 도구 실행 결과 목록
            
        Returns:
            관찰 내용
        """
        observations = []
        
        for result in tool_results:
            if result.get("success"):
                observations.append(f"{result['tool']} 실행 성공")
            else:
                observations.append(f"{result['tool']} 실행 실패: {result.get('error', 'Unknown error')}")
        
        return ", ".join(observations) if observations else "도구 실행 완료"
    
    def _generate_partial_conclusion(self) -> str:
        """
        최대 반복 횟수 도달 시 부분적인 결론 생성
        
        실행 로그와 추론 히스토리를 바탕으로 의미 있는 부분 결과를 제시
        
        Returns:
            부분적인 분석 결과와 권장사항
        """
        if not self.execution_log and not self.reasoning_history:
            return "분석을 위한 충분한 데이터가 수집되지 않았습니다. 문제를 단순화하거나 더 구체적인 질문으로 다시 시도해보세요."
        
        # 완료된 작업 분석
        completed_tools = []
        successful_tools = []
        failed_tools = []
        key_insights = []
        
        # 실행 로그에서 도구 사용 현황 분석
        for log_entry in self.execution_log:
            if log_entry.get("type") == "tool_call":
                tool_name = log_entry.get("tool")
                if tool_name:
                    completed_tools.append(tool_name)
                    if log_entry.get("success", False):
                        successful_tools.append(tool_name)
                        # 성공한 도구의 결과에서 인사이트 추출
                        result = log_entry.get("result", "")
                        if result and len(str(result)) > 50:
                            preview = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
                            key_insights.append(f"• {tool_name}: {preview}")
                    else:
                        failed_tools.append(f"{tool_name} ({log_entry.get('error', '알 수 없는 오류')})")
        
        # 추론 히스토리에서 핵심 사고 과정 추출
        reasoning_insights = []
        for reasoning_entry in self.reasoning_history[-3:]:  # 최근 3개 추론만
            reasoning = reasoning_entry.get("reasoning", "")
            if reasoning and len(reasoning) > 30:
                # 핵심 키워드가 포함된 추론만 선별
                if any(keyword in reasoning.lower() for keyword in 
                       ["분석", "발견", "문제", "해결", "개선", "추천", "결론", "중요"]):
                    preview = reasoning[:150] + "..." if len(reasoning) > 150 else reasoning
                    reasoning_insights.append(f"• {preview}")
        
        # 전체 대화에서 중요한 정보 추출
        important_context = []
        if len(self.conversation_history) > 2:  # 시스템 프롬프트 + 사용자 질문 이후
            for message in self.conversation_history[2:]:  # 실제 대화 내용만
                if message.get("role") == "assistant" and message.get("content"):
                    content = message["content"]
                    # 구체적인 정보나 결과가 포함된 응답만 선별
                    if any(indicator in content.lower() for indicator in 
                           ["발견했습니다", "확인했습니다", "분석 결과", "권장사항", "해결책"]):
                        preview = content[:200] + "..." if len(content) > 200 else content
                        important_context.append(f"• {preview}")
        
        # 부분 결론 구성
        conclusion_parts = [
            f"⚠️ 최대 반복 횟수 ({self.max_iterations}) 도달로 분석이 중단되었습니다.",
            "",
            "## 📊 현재까지의 진행 상황"
        ]
        
        if completed_tools:
            conclusion_parts.extend([
                f"**실행된 작업**: {len(completed_tools)}개 도구 사용",
                f"- 성공: {len(successful_tools)}개 ({', '.join(set(successful_tools))})",
            ])
            if failed_tools:
                conclusion_parts.append(f"- 실패: {len(failed_tools)}개 ({', '.join(failed_tools)})")
        
        if key_insights:
            conclusion_parts.extend([
                "",
                "## 🔍 수집된 주요 정보",
                *key_insights[:5]  # 최대 5개만 표시
            ])
        
        if reasoning_insights:
            conclusion_parts.extend([
                "",
                "## 🤔 핵심 분석 내용",
                *reasoning_insights[:3]  # 최대 3개만 표시
            ])
        
        if important_context:
            conclusion_parts.extend([
                "",
                "## 💡 주요 발견사항",
                *important_context[:3]  # 최대 3개만 표시
            ])
        
        # 권장사항 추가
        conclusion_parts.extend([
            "",
            "## 🎯 권장사항",
            "• 문제를 더 구체적이고 단순한 하위 작업으로 나누어 다시 시도하세요",
            "• 특정 부분에 집중하여 단계별로 접근해보세요",
            f"• max_iterations 값을 {self.max_iterations + 5} 이상으로 증가시켜 재시도하세요"
        ])
        
        if successful_tools:
            conclusion_parts.append("• 성공한 작업 결과를 바탕으로 다음 단계를 계획하세요")
        
        if failed_tools:
            conclusion_parts.append("• 실패한 작업들을 개별적으로 다시 검토해보세요")
        
        return "\n".join(conclusion_parts)
    
    def _calculate_total_token_usage(self) -> Dict[str, Any]:
        """전체 토큰 사용량 계산 - 실제 API 응답 기반"""
        total_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "estimated": False
        }
        
        # token_usage_history에서 실제 사용량 합산
        if self.token_usage_history:
            for usage_record in self.token_usage_history:
                usage = usage_record.get("usage", {})
                if isinstance(usage, dict):
                    total_usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
                    total_usage["completion_tokens"] += usage.get("completion_tokens", 0)
                    total_usage["total_tokens"] += usage.get("total_tokens", 0)
            
            # 실제 토큰 정보가 있으면 그대로 사용
            if total_usage["total_tokens"] > 0:
                return total_usage
        
        # 실제 토큰 정보가 없는 경우 추정값 사용 (폴백)
        total_usage["estimated"] = True
        for message in self.conversation_history:
            content = message.get('content', '')
            if content:
                # 더 정확한 추정을 위해 tiktoken 라이브러리 사용 권장
                # 현재는 간단한 추정 (한글은 2-3토큰, 영어는 3-4자당 1토큰)
                if message.get('role') == 'user':
                    estimated_tokens = len(content) // 3
                    total_usage["prompt_tokens"] += estimated_tokens
                elif message.get('role') == 'assistant':
                    estimated_tokens = len(content) // 3
                    total_usage["completion_tokens"] += estimated_tokens
                elif message.get('role') == 'system':
                    estimated_tokens = len(content) // 3
                    total_usage["prompt_tokens"] += estimated_tokens
                elif message.get('role') == 'tool':
                    # 도구 응답도 프롬프트에 포함됨
                    estimated_tokens = len(content) // 3
                    total_usage["prompt_tokens"] += estimated_tokens
        
        total_usage["total_tokens"] = total_usage["prompt_tokens"] + total_usage["completion_tokens"]
        
        return total_usage
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """대화 히스토리 반환"""
        return self.conversation_history.copy()
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """실행 로그 반환"""
        return self.execution_log.copy()
    
    def get_reasoning_history(self) -> List[Dict[str, Any]]:
        """추론 히스토리 반환"""
        return self.reasoning_history.copy()
    
    def reset(self):
        """에이전트 상태 리셋"""
        self.current_iteration = 0
        self.execution_log = []
        self.reasoning_history = []
        self.token_usage_history = []  # 토큰 사용 히스토리도 초기화
        self._initialize_conversation()
    
    def health_check(self) -> Dict[str, Any]:
        """에이전트 및 구성 요소 상태 확인"""
        return {
            "agent_status": "healthy",
            "llm_client": self.llm_client.health_check(),
            "tools_manager": {
                "status": "healthy",
                "available_tools": len(self.tools_manager),
                "tools": self.tools_manager.get_available_tools()
            },
            "configuration": {
                "endpoint": self.endpoint,
                "model": self.model,
                "max_iterations": self.max_iterations,
                "callback": self.callback.__class__.__name__
            }
        }
    
    def __str__(self) -> str:
        """문자열 표현"""
        return f"ReactAgentV2(model='{self.model}', tools={len(self.tools_manager)}, iterations={self.current_iteration})"
    
    def __repr__(self) -> str:
        """개발자용 표현"""
        return self.__str__()


# 편의를 위한 팩토리 함수
def create_agent_v2(
    endpoint: str = "http://localhost:11434",
    model: str = "gpt-oss:20b",
    max_iterations: int = 10,
    callback: Optional[ReasoningCallback] = None
) -> ReactAgentV2:
    """
    ReactAgentV2 인스턴스를 생성하는 편의 함수
    
    Args:
        endpoint: LLM 서버 엔드포인트
        model: 사용할 모델명
        max_iterations: 최대 반복 횟수
        callback: 실시간 업데이트를 위한 콜백 객체
        
    Returns:
        ReactAgentV2: 초기화된 에이전트 인스턴스
    """
    return ReactAgentV2(
        endpoint=endpoint,
        model=model,
        max_iterations=max_iterations,
        callback=callback
    )