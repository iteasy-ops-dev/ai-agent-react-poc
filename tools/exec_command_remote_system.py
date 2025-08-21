import paramiko
from tools.base_tool import BaseTool
from config.server_config import ServerConfig

class ExecCommandRemoteSystem(BaseTool):
    """
    원격 시스템에서 명령어를 실행하는 도구 클래스
    이 도구는 원격 시스템에서 명령어를 실행하고 결과를 반환합니다 
    """
    
    name = "exec_command_remote_system"
    description = "Executes commands on remote server using configured connection settings. Ready to use - just provide the command to run."
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The command to execute on the remote system"
            }
        },
        "required": ["command"]
    }
    
    def execute(self, command: str) -> str:
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
            
            stdin, stdout, stderr = ssh.exec_command(command)
            
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            if error:
                return f"실행 결과:\n{output}\n에러:\n{error}"
            else:
                return output
            
        except Exception as e:
            return f"연결 오류: {str(e)}"
        finally:
            ssh.close()