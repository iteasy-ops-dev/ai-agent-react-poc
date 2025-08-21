import paramiko
from tools.base_tool import BaseTool
from config.server_config import ServerConfig

class ContainerAnalyzer(BaseTool):
    """
    원격 시스템의 컨테이너 환경을 분석하는 도구 클래스
    Docker 컨테이너, 이미지, Kubernetes 클러스터 정보를 수집합니다
    """
    
    name = "container_analyzer"
    description = "Analyzes Docker containers and Kubernetes info using configured server connection. Ready to use for container environment analysis."
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    def execute(self) -> str:
        # 서버 설정 정보 가져오기
        connection_info = ServerConfig.get_connection_info()
        if not connection_info:
            return "Error: Server connection information not configured. Please configure server settings in the sidebar."
        
        ip = connection_info['ip']
        port = connection_info['port']
        username = connection_info['username']
        password = connection_info['password']
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(ip, port=port, username=username, password=password)
            
            # 먼저 Docker 및 Kubernetes 사용 가능 여부 확인
            availability_check = [
                ("Docker 사용 가능 확인", "which docker"),
                ("Kubernetes 사용 가능 확인", "which kubectl")
            ]
            
            # 사용 가능 여부 확인을 위한 배치 실행
            check_commands = []
            for description, command in availability_check:
                check_commands.append(f'echo "SECTION_START:{description}"')
                check_commands.append(f'({command}) 2>&1')
                check_commands.append(f'echo "SECTION_END:$?"')
            
            check_command = " && ".join(check_commands)
            _, stdout, stderr = ssh.exec_command(check_command)
            check_output = stdout.read().decode('utf-8')
            
            # 사용 가능 여부 파싱
            check_sections = self._parse_batch_output(check_output)
            docker_available = check_sections.get("Docker 사용 가능 확인", {}).get('exit_code', 1) == 0
            k8s_available = check_sections.get("Kubernetes 사용 가능 확인", {}).get('exit_code', 1) == 0
            
            # 실행할 컨테이너 환경 분석 명령어들
            all_commands = [
                ("Docker 컨테이너 목록", "docker ps -a", "docker"),
                ("Docker 이미지 목록", "docker images", "docker"),
                ("Docker 시스템 정보", "docker system df", "docker"),
                ("실행 중인 컨테이너 리소스", "docker stats --no-stream", "docker"),
                ("Kubernetes 팟 목록", "kubectl get pods --all-namespaces", "kubectl"),
                ("Kubernetes 노드 정보", "kubectl get nodes", "kubectl"),
                ("Kubernetes 서비스 목록", "kubectl get services --all-namespaces", "kubectl"),
                ("Kubernetes 클러스터 정보", "kubectl cluster-info", "kubectl")
            ]
            
            # 사용 가능한 명령어만 필터링
            available_commands = []
            for description, command, tool_type in all_commands:
                if tool_type == "docker" and docker_available:
                    available_commands.append((description, command))
                elif tool_type == "kubectl" and k8s_available:
                    available_commands.append((description, command))
            
            # 배치 명령어 생성
            batch_commands = []
            for description, command in available_commands:
                batch_commands.append(f'echo "SECTION_START:{description}"')
                batch_commands.append(f'({command}) 2>&1')
                batch_commands.append(f'echo "SECTION_END:$?"')
            
            results = []
            results.append("="*60)
            results.append("     원격 시스템 컨테이너 환경 분석")
            results.append("="*60)
            
            # 환경 검사 결과 표시
            results.append(f"\n[환경 검사 결과]")
            results.append("-" * 40)
            results.append(f"Docker 사용 가능: {'✅' if docker_available else '❌'}")
            results.append(f"Kubernetes 사용 가능: {'✅' if k8s_available else '❌'}")
            
            if available_commands:
                # 한 번의 SSH 실행으로 모든 명령어 실행
                full_command = " && ".join(batch_commands)
                _, stdout, stderr = ssh.exec_command(full_command)
                full_output = stdout.read().decode('utf-8')
                
                # 섹션별로 결과 분리
                sections = self._parse_batch_output(full_output)
                
                for description, command in available_commands:
                    section_data = sections.get(description, {})
                    output = section_data.get('output', '')
                    exit_code = section_data.get('exit_code', 1)
                    
                    results.append(f"\n[{description}]")
                    results.append("-" * 40)
                    
                    if exit_code == 0 and output:
                        results.append(output.strip())
                    elif output:
                        results.append(f"⚠️ 명령 실행 결과 (exit code: {exit_code}):")
                        results.append(output.strip())
                    else:
                        results.append("❌ 명령 실행 실패 또는 결과 없음")
            
            # 사용할 수 없는 도구들에 대한 메시지 추가
            for description, command, tool_type in all_commands:
                if tool_type == "docker" and not docker_available:
                    results.append(f"\n[{description}]")
                    results.append("-" * 40)
                    results.append("❌ Docker가 설치되지 않았거나 사용할 수 없습니다.")
                elif tool_type == "kubectl" and not k8s_available:
                    results.append(f"\n[{description}]")
                    results.append("-" * 40)
                    results.append("❌ kubectl이 설치되지 않았거나 사용할 수 없습니다.")
            
            return "\n".join(results)
            
        except Exception as e:
            return f"❌ 연결 오류: {str(e)}"
        finally:
            ssh.close()
    
    def _parse_batch_output(self, output: str) -> dict:
        """배치 실행 결과를 섹션별로 파싱"""
        sections = {}
        lines = output.split('\n')
        current_section = None
        current_output = []
        
        for line in lines:
            if line.startswith('SECTION_START:'):
                # 이전 섹션 저장
                if current_section and current_output:
                    sections[current_section]['output'] = '\n'.join(current_output)
                
                # 새 섹션 시작
                current_section = line.replace('SECTION_START:', '')
                sections[current_section] = {'output': '', 'exit_code': 1}
                current_output = []
                
            elif line.startswith('SECTION_END:'):
                # 섹션 종료 및 exit code 저장
                if current_section:
                    try:
                        exit_code = int(line.replace('SECTION_END:', ''))
                        sections[current_section]['exit_code'] = exit_code
                    except ValueError:
                        sections[current_section]['exit_code'] = 1
                    
                    if current_output:
                        sections[current_section]['output'] = '\n'.join(current_output)
                
            else:
                # 명령어 출력 수집
                if current_section is not None:
                    current_output.append(line)
        
        return sections