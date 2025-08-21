import paramiko
from tools.base_tool import BaseTool
from config.server_config import ServerConfig

class ServiceStatusAnalyzer(BaseTool):
    """
    원격 시스템의 서비스 상태를 분석하는 도구 클래스
    systemd 서비스 상태, 활성/비활성/실패한 서비스 목록을 확인합니다
    """
    
    name = "service_status_analyzer"
    description = "Checks systemd service status using configured server connection. Ready to use - lists active/inactive/failed services."
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
            
            # 실행할 서비스 상태 분석 명령어들
            commands = [
                ("활성 서비스 목록", "systemctl list-units --type=service --state=active --no-pager"),
                ("실패한 서비스 목록", "systemctl list-units --type=service --state=failed --no-pager"),
                ("모든 서비스 상태 요약", "systemctl list-units --type=service --no-pager | head -20"),
                ("시스템 상태", "systemctl status --no-pager"),
                ("부팅 시 활성화된 서비스", "systemctl list-unit-files --type=service --state=enabled --no-pager | head -15"),
                ("서비스 개수 통계", "systemctl list-units --type=service --all --no-pager | grep -c 'service'")
            ]
            
            # 배치 명령어 생성
            batch_commands = []
            for description, command in commands:
                batch_commands.append(f'echo "SECTION_START:{description}"')
                batch_commands.append(f'({command}) 2>&1')
                batch_commands.append(f'echo "SECTION_END:$?"')
            
            # 모든 명령어를 하나로 결합
            full_command = " && ".join(batch_commands)
            
            # 한 번의 SSH 실행으로 모든 명령어 실행
            _, stdout, stderr = ssh.exec_command(full_command)
            full_output = stdout.read().decode('utf-8')
            
            # 결과 파싱
            results = []
            results.append("="*60)
            results.append("     원격 시스템 서비스 상태 분석")
            results.append("="*60)
            
            # 섹션별로 결과 분리
            sections = self._parse_batch_output(full_output)
            
            for description, command in commands:
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