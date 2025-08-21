import streamlit as st
import time
import json
from datetime import datetime
from typing import Dict, Any, List
from agent_v2 import ReactAgentV2, ReasoningCallback
from config.server_config import ServerConfig


class StreamlitReasoningCallback(ReasoningCallback):
    """
    Streamlit UI를 위한 실시간 업데이트 콜백
    """
    
    def __init__(self):
        """초기화 - Streamlit 컨테이너 설정"""
        # 실시간 업데이트를 위한 컨테이너
        self.reasoning_container = None
        self.current_iteration_container = None
        self.status_container = None
        self.result_container = None
        
        # 현재 반복 상태
        self.current_iteration = 0
        self.current_content = []
    
    def set_containers(self, reasoning_container, status_container, result_container):
        """Streamlit 컨테이너 설정"""
        self.reasoning_container = reasoning_container
        self.status_container = status_container
        self.result_container = result_container
    
    def on_iteration_start(self, iteration: int, max_iterations: int):
        """새로운 반복 시작"""
        self.current_iteration = iteration
        self.current_content = []
        
        if self.status_container:
            self.status_container.info(f"🧠 Step {iteration}/{max_iterations} 분석 중...")
        
        if self.reasoning_container:
            with self.reasoning_container:
                # 새로운 분석 단계를 위한 확장 가능한 섹션 생성
                with st.expander(f"🧠 Step {iteration} - 추론 과정", expanded=True):
                    self.current_iteration_container = st.container()
    
    def on_reasoning(self, iteration: int, thought: str):
        """LLM의 추론 과정 표시"""
        if self.current_iteration_container:
            with self.current_iteration_container:
                st.markdown("### 🤔 추론 과정")
                st.info(thought)
                
                # 세션 상태에 저장
                if 'reasoning_steps' not in st.session_state:
                    st.session_state.reasoning_steps = []
                st.session_state.reasoning_steps.append({
                    'iteration': iteration,
                    'type': 'reasoning',
                    'content': thought,
                    'timestamp': datetime.now().isoformat()
                })
    
    def on_tool_call(self, iteration: int, tool: str, arguments: Dict[str, Any]):
        """도구 호출 표시"""
        if self.current_iteration_container:
            with self.current_iteration_container:
                st.markdown("### 🔧 도구 실행")
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.write("**도구:**", tool)
                with col2:
                    st.write("**인자:**")
                    st.json(arguments)
    
    def on_tool_result(self, iteration: int, tool: str, result: str, success: bool):
        """도구 실행 결과 표시"""
        if self.current_iteration_container:
            with self.current_iteration_container:
                if success:
                    # 결과 미리보기 (너무 길면 축약)
                    preview = result[:500] + "..." if len(result) > 500 else result
                    st.success(f"✅ {tool} 실행 성공")
                    with st.expander("결과 보기", expanded=False):
                        st.text(preview)
                else:
                    st.error(f"❌ {tool} 실행 실패: {result}")
    
    def on_observation(self, iteration: int, observation: str):
        """관찰 단계 표시"""
        if self.current_iteration_container:
            with self.current_iteration_container:
                st.markdown("### 👁️ 관찰")
                st.write(observation)
    
    def on_iteration_end(self, iteration: int):
        """분석 단계 종료"""
        if self.status_container:
            self.status_container.success(f"✅ Step {iteration} 완성")
    
    def on_final_result(self, result: str, iterations: int):
        """최종 결과"""
        if self.status_container:
            self.status_container.success(f"🏆 작업 완료! (총 {iterations}단계 수행)")
        
        # 최종 결론을 메인 컨테이너에 표시
        if self.result_container and result:
            # 부분 결론인지 확인 (최대 반복 횟수 도달)
            is_partial = "최대 반복 횟수" in result and "도달로 분석이 중단" in result
            
            if is_partial:
                # 부분 결론의 경우 경고 스타일 적용
                final_content = f"### ⚠️ 부분 결론\n\n{result}"
            else:
                # 정상 완료의 경우
                final_content = f"### 🎯 최종 결론\n\n{result}"
            
            self.result_container.markdown(final_content)
        
        # 세션 상태에 최종 결과 저장 (히스토리용)
        if 'final_results' not in st.session_state:
            st.session_state.final_results = []
        st.session_state.final_results.append({
            'result': result,
            'iterations': iterations,
            'timestamp': datetime.now().isoformat()
        })
    
    def on_error(self, iteration: int, error: str):
        """오류 발생"""
        if self.status_container:
            self.status_container.error(f"❌ 오류 발생: {error}")
        
        if self.current_iteration_container:
            with self.current_iteration_container:
                st.error(f"오류: {error}")


def init_session_state():
    """세션 상태 초기화"""
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'execution_history' not in st.session_state:
        st.session_state.execution_history = []
    if 'reasoning_steps' not in st.session_state:
        st.session_state.reasoning_steps = []
    if 'final_results' not in st.session_state:
        st.session_state.final_results = []
    
    # 서버 설정 초기화
    ServerConfig.initialize_session()


def create_agent_with_callback(endpoint: str, model: str, max_iterations: int) -> tuple:
    """콜백과 함께 에이전트 생성"""
    callback = StreamlitReasoningCallback()
    agent = ReactAgentV2(
        endpoint=endpoint,
        model=model,
        max_iterations=max_iterations,
        callback=callback,
        verbose=False  # UI에서는 콘솔 출력 비활성화
    )
    return agent, callback


def main():
    st.set_page_config(
        page_title="ReAct Agent v2",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 ReAct Agent v2")
    st.markdown("LLM의 추론 과정을 실시간으로 확인할 수 있는 개선된 인터페이스")
    
    # 세션 상태 초기화
    init_session_state()
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 에이전트 설정")
        
        endpoint = st.selectbox(
            "LLM 엔드포인트",
            options=[
                "https://api.openai.com",
                "http://localhost:11434",
                "http://10.10.25.5:11434",
            ],
            index=0,
            help="사용할 LLM 서비스 선택"
        )
        
        model = st.selectbox(
            "모델명",
            options=[
                "gpt-3.5-turbo",
                "gpt-4o",
                "gpt-oss:20b",
                "iteasy-gpt",
            ],
            index=0,
            help="사용할 LLM 모델 선택"
        )
        
        max_iterations = st.slider(
            "🧠 최대 분석 단계",
            min_value=1,
            max_value=20,
            value=10,
            help="ReAct 에이전트의 최대 사고 단계 수"
        )
        
        st.divider()
        
        # 서버 접속 설정
        st.header("🔐 서버 접속 설정")
        
        with st.expander("원격 서버 정보", expanded=False):
            server_ip = st.text_input(
                "서버 IP",
                value=st.session_state.server_config.get('ip', '') if 'server_config' in st.session_state else '',
                placeholder="예: 192.168.1.100",
                help="원격 서버의 IP 주소"
            )
            
            server_port = st.number_input(
                "SSH 포트",
                min_value=1,
                max_value=65535,
                value=st.session_state.server_config.get('port', 22) if 'server_config' in st.session_state else 22,
                help="SSH 포트 번호 (기본값: 22)"
            )
            
            server_username = st.text_input(
                "사용자명",
                value=st.session_state.server_config.get('username', '') if 'server_config' in st.session_state else '',
                placeholder="예: admin",
                help="SSH 사용자명"
            )
            
            server_password = st.text_input(
                "비밀번호",
                type="password",
                value=st.session_state.server_config.get('password', '') if 'server_config' in st.session_state else '',
                placeholder="비밀번호 입력",
                help="SSH 비밀번호 (안전하게 세션에만 저장됩니다)"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 저장", use_container_width=True):
                    if server_ip and server_username and server_password:
                        ServerConfig.set_connection_info(
                            ip=server_ip,
                            port=server_port,
                            username=server_username,
                            password=server_password
                        )
                        st.success("✅ 서버 정보 저장됨")
                    else:
                        st.error("모든 필드를 입력해주세요")
            
            with col2:
                if st.button("🗑️ 초기화", use_container_width=True):
                    ServerConfig.clear_connection_info()
                    st.info("서버 정보가 초기화되었습니다")
                    st.rerun()
        
        # 서버 연결 상태 표시
        if ServerConfig.is_configured():
            st.success(f"✅ 서버 설정됨: {ServerConfig.get_display_info()}")
        else:
            st.warning("⚠️ 서버 정보를 설정해주세요")
        
        st.divider()
        
        # 대화 기록 초기화
        if st.button("🔄 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.session_state.execution_history = []
            st.session_state.reasoning_steps = []
            st.session_state.final_results = []
            if st.session_state.agent:
                st.session_state.agent.reset()
            st.rerun()
    
    # 메인 컨텐츠 영역
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 대화")
        
        # 대화 히스토리 표시
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # 사용자 입력
        if prompt := st.chat_input("질문을 입력하세요..."):
            # 사용자 메시지 추가
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # 에이전트 응답 생성
            with st.chat_message("assistant"):
                # 상태 컨테이너
                status_container = st.empty()
                status_container.info("🤔 처리 중...")
                
                # 추론 과정을 표시할 컨테이너
                reasoning_container = st.container()
                
                # 최종 결과를 표시할 컨테이너
                result_container = st.empty()
                
                try:
                    # 에이전트와 콜백 생성
                    agent, callback = create_agent_with_callback(endpoint, model, max_iterations)
                    st.session_state.agent = agent
                    
                    # 콜백에 컨테이너 설정
                    callback.set_containers(reasoning_container, status_container, result_container)
                    
                    # 에이전트 실행
                    result = agent.run(prompt)
                    
                    if result['success']:
                        # 최종 결론은 on_final_result에서 표시됨
                        pass
                        
                        # 대화 히스토리에 추가
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result['result']
                        })
                        
                        # 실행 기록 저장
                        execution_record = {
                            "timestamp": datetime.now().isoformat(),
                            "user_input": prompt,
                            "result": result,
                            "reasoning_history": result.get('reasoning_history', []),
                            "execution_log": result.get('execution_log', [])
                        }
                        st.session_state.execution_history.append(execution_record)
                        
                        # 상태 업데이트
                        status_container.success(
                            f"✅ 완료! "
                            f"(분석 단계: {result['iterations']}, "
                            f"시간: {result['execution_time']}초, "
                            f"토큰: {result.get('token_usage', {}).get('total_tokens', 0)})"
                        )
                    else:
                        error_msg = result.get('error', '알 수 없는 오류')
                        result_container.error(f"오류: {error_msg}")
                        status_container.error("❌ 처리 실패")
                        
                except Exception as e:
                    result_container.error(f"시스템 오류: {str(e)}")
                    status_container.error("❌ 시스템 오류 발생")
    
    with col2:
        st.header("📊 분석 정보")
        
        # 탭 생성
        tab1, tab2, tab3 = st.tabs(["추론 과정", "실행 로그", "성능 지표"])
        
        with tab1:
            st.subheader("🤔 추론 히스토리")
            if st.session_state.reasoning_steps:
                for step in reversed(st.session_state.reasoning_steps[-10:]):  # 최근 10개
                    with st.expander(f"🧠 Step {step['iteration']} - {step['type']}", expanded=False):
                        st.write(step['content'])
                        st.caption(f"시간: {step['timestamp']}")
            else:
                st.info("추론 과정이 여기에 표시됩니다")
        
        with tab2:
            st.subheader("📝 실행 로그")
            if st.session_state.execution_history:
                latest = st.session_state.execution_history[-1]
                execution_log = latest.get('execution_log', [])
                
                if execution_log:
                    for log in reversed(execution_log[-10:]):  # 최근 10개
                        if 'tool_calls' in log:
                            for tool_call in log['tool_calls']:
                                with st.expander(f"🔧 {tool_call['tool']}", expanded=False):
                                    st.json({
                                        "도구": tool_call['tool'],
                                        "인자": tool_call['arguments'],
                                        "성공": tool_call.get('success', False),
                                        "결과 크기": tool_call.get('result_length', 0)
                                    })
                else:
                    st.info("실행 로그가 여기에 표시됩니다")
            else:
                st.info("실행 로그가 여기에 표시됩니다")
        
        with tab3:
            st.subheader("⚡ 성능 지표")
            if st.session_state.execution_history:
                latest = st.session_state.execution_history[-1]
                result = latest['result']
                
                # 성능 메트릭
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🧠 분석 단계", result.get('iterations', 0))
                    st.metric("⏱️ 실행 시간", f"{result.get('execution_time', 0)}초")
                
                with col2:
                    token_usage = result.get('token_usage', {})
                    st.metric("총 토큰", token_usage.get('total_tokens', 0))
                    st.metric("도구 사용", len(result.get('tools_used', [])))
                
                # 토큰 사용 세부사항
                if token_usage:
                    st.divider()
                    is_estimated = token_usage.get('estimated', False)
                    if is_estimated:
                        st.write("**토큰 사용 세부사항 (추정값):**")
                        st.caption("⚠️ 실제 API 토큰 정보가 없어 추정값을 표시합니다")
                    else:
                        st.write("**토큰 사용 세부사항 (실제):**")
                    st.write(f"• 프롬프트: {token_usage.get('prompt_tokens', 0)}")
                    st.write(f"• 완성: {token_usage.get('completion_tokens', 0)}")
                
                # 사용된 도구 목록
                if result.get('tools_used'):
                    st.divider()
                    st.write("**사용된 도구:**")
                    for tool in result['tools_used']:
                        st.write(f"• {tool}")
            else:
                st.info("성능 지표가 여기에 표시됩니다")


if __name__ == "__main__":
    main()