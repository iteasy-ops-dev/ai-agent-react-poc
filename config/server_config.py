"""
서버 접속 정보를 중앙에서 관리하는 설정 클래스
민감한 정보를 LLM으로부터 보호하고 UI를 통해서만 관리
"""
import streamlit as st
from typing import Optional, Dict, Any


class ServerConfig:
    """
    서버 접속 정보를 안전하게 관리하는 클래스
    Streamlit 세션 상태를 활용하여 메모리에서만 관리
    """
    
    @staticmethod
    def initialize_session():
        """세션 상태 초기화"""
        if 'server_config' not in st.session_state:
            st.session_state.server_config = {
                'ip': None,
                'port': None,
                'username': None,
                'password': None,
                'is_configured': False
            }
    
    @staticmethod
    def set_connection_info(ip: str, port: int, username: str, password: str):
        """
        서버 접속 정보 설정
        
        Args:
            ip: 서버 IP 주소
            port: SSH 포트 번호
            username: SSH 사용자명
            password: SSH 비밀번호
        """
        ServerConfig.initialize_session()
        
        st.session_state.server_config = {
            'ip': ip,
            'port': port,
            'username': username,
            'password': password,
            'is_configured': True
        }
    
    @staticmethod
    def get_connection_info() -> Optional[Dict[str, Any]]:
        """
        저장된 서버 접속 정보 반환
        
        Returns:
            접속 정보 딕셔너리 또는 None
        """
        ServerConfig.initialize_session()
        
        config = st.session_state.server_config
        if config['is_configured']:
            return {
                'ip': config['ip'],
                'port': config['port'],
                'username': config['username'],
                'password': config['password']
            }
        return None
    
    @staticmethod
    def is_configured() -> bool:
        """
        서버 접속 정보가 설정되었는지 확인
        
        Returns:
            설정 여부
        """
        ServerConfig.initialize_session()
        return st.session_state.server_config.get('is_configured', False)
    
    @staticmethod
    def clear_connection_info():
        """저장된 서버 접속 정보 삭제"""
        ServerConfig.initialize_session()
        st.session_state.server_config = {
            'ip': None,
            'port': None,
            'username': None,
            'password': None,
            'is_configured': False
        }
    
    @staticmethod
    def get_display_info() -> str:
        """
        표시용 서버 정보 반환 (비밀번호 제외)
        
        Returns:
            표시용 서버 정보 문자열
        """
        if not ServerConfig.is_configured():
            return "서버 미설정"
        
        config = st.session_state.server_config
        return f"{config['username']}@{config['ip']}:{config['port']}"