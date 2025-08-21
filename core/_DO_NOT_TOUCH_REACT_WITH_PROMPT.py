from openai import OpenAI
import paramiko
import json
 
client = OpenAI(
    base_url="http://localhost:11434/v1",  # Local Ollama API
    api_key="ollama"                       # Dummy key
)
 

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather in a given city",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_company",
            "description": "Get information about our company",
        },
    },
     {
        "type": "function",
        "function": {
            "name": "exec_command_remote_system",
            "description": "Execute a command on the remote system",
            "parameters": {
                "type": "object",
                "properties": {"ip": {"type": "string"},
                               "port": {"type": "integer"},
                               "username": {"type": "string"},
                               "password": {"type": "string"},
                               "command": {"type": "string", "description": "The command to execute on the remote system"}},
                "required": ["ip", "port", "username", "password", "command"]
            },
        },
    }
]

input_list = [
    {"role": "system", "content": """
You are a senior system engineer who specializes in remote system analysis and troubleshooting. You approach problems systematically, provide quantitative analysis, and offer actionable recommendations in Korean.

## Available Tools:
1. call_tools(tools=exec_command_remote_system, parameters={"ip": "string", "port": int, "username": "string", "password": "string", "command": "string"}): Execute commands on remote systems
2. finish(answer): Provide comprehensive system analysis report

## Enhanced Analysis Framework:
Follow this 5-step reasoning process for thorough system analysis:

**Observation**: 현재 상황 파악 및 정보 수집 계획
**Analysis**: 수집된 데이터의 패턴 분석 및 근본 원인 파악  
**Planning**: 우선순위별 다단계 조치 계획 수립
**Execution**: 배치 명령어를 통한 효율적 정보 수집
**Validation**: 결과 검증 및 다음 단계 결정

## System Engineering Best Practices:
- **배치 명령어 사용**: 여러 정보를 한 번에 수집 (예: "uptime; free -h; df -h; ps aux --sort=-%cpu | head -10")
- **정량적 분석**: CPU 사용률, 메모리 사용량, 디스크 공간, 네트워크 상태 등 수치 기반 평가
- **위험도 평가**: 높음/중간/낮음으로 문제 우선순위 분류
- **점진적 분석**: 기본 상태 → 성능 분석 → 보안 검토 → 심화 진단 순서

## Response Structure:
최종 답변 시 다음 형식을 따르세요:
1. **시스템 개요** (OS, 하드웨어, 가동시간)
2. **핵심 지표** (CPU/메모리/디스크 사용률)
3. **발견된 이슈** (위험도별 분류)
4. **권장 조치사항** (우선순위별)
5. **모니터링 포인트** (지속 관찰 필요 항목)

## Example Enhanced Analysis:
Question: 10.10.25.5 시스템 상태 검토
Observation: 원격 시스템의 전반적 상태를 파악하기 위해 기본 정보부터 수집하겠습니다.
Action: call_tools(tools=exec_command_remote_system, parameters={"ip": "10.10.25.5", "port": 22, "username": "root", "password": "password", "command": "uname -a; uptime; whoami; date"})

Analysis: 시스템 정보를 확인했습니다. 다음으로 리소스 사용량을 종합적으로 분석하겠습니다.
Action: call_tools(tools=exec_command_remote_system, parameters={"ip": "10.10.25.5", "port": 22, "username": "root", "password": "password", "command": "free -h; df -h; iostat 1 3; vmstat 1 3"})

Planning: 수집된 데이터를 바탕으로 성능 병목과 잠재적 위험을 식별하겠습니다.
Action: call_tools(tools=exec_command_remote_system, parameters={"ip": "10.10.25.5", "port": 22, "username": "root", "password": "password", "command": "ps aux --sort=-%cpu | head -10; netstat -tuln | grep LISTEN; systemctl --failed"})

Execution: 보안 관련 점검을 수행하겠습니다.
Action: call_tools(tools=exec_command_remote_system, parameters={"ip": "10.10.25.5", "port": 22, "username": "root", "password": "password", "command": "last | head -10; ss -tuln; iptables -L -n"})

Validation: 종합 분석을 완료하여 체계적인 시스템 상태 보고서를 제공하겠습니다.
Action: finish('[체계적인 한국어 시스템 분석 보고서]')

## 이제 분석을 시작합니다.
"""},
    {"role": "user", "content": "10.10.25.5, 22, root, password는 Zhtjgh*#20의 시스템 상태를 리뷰해줘. 답변은 한글로 해줘."},
]

def get_weather(city: str) -> str:
    return f"{city}의 현재 날씨는 호우주의보입니다.."
def get_company() -> str:
    return "회사 이름은 아이티이지입니다. 대표는 조명래이고, 호스팅서비스를 제공합니다. 서초구에 위치하고 있습니다. 네트워크팀에는 이승건, 반훈 등이 근무합니다."    
def exec_command_remote_system(ip: str, port: str, username: str, password: str, command: str) -> str:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("-" * 20)
    print("Command to execute:", command)

    try:
        ssh.connect(ip, port=port, username=username, password=password)
        
        _, stdout, stderr = ssh.exec_command(command)
        
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

    

def select_function(function_name: str, arguments: dict):
    if function_name == "get_weather":
        return get_weather(arguments["city"])
    elif function_name == "get_company":
        return get_company()
    elif function_name == "exec_command_remote_system":
        return exec_command_remote_system(arguments["ip"], arguments["port"], arguments["username"], arguments["password"], arguments["command"])
    else:
        raise ValueError(f"Unknown function: {function_name}")

# Enhanced ReAct Pattern with Better Control
MAX_ITERATIONS = 10  # 무한 루프 방지
count = 0

print("🤖 Enhanced ReAct 패턴 시작 - 시스템 엔지니어 모드")
print("=" * 50)

while count < MAX_ITERATIONS:
    count += 1
    print(f"\n🔄 반복 {count}/{MAX_ITERATIONS}")
    
    try:
        response = client.chat.completions.create(
            model="gpt-oss:20b",
            messages=input_list,
            tools=tools
        )

        print("-" * 30)
        print("📊 모델 응답 정보:")
        if hasattr(response.choices[0].message, 'reasoning') and response.choices[0].message.reasoning:
            print(f"🧠 추론 과정: {response.choices[0].message.reasoning}")
        print(f"📈 토큰 사용량: {response.usage.total_tokens}")
        print(f"✅ 완료 이유: {response.choices[0].finish_reason}")

        # 메시지 추가
        input_list.append(response.choices[0].message.model_dump())

        # 도구 호출이 없으면 종료
        if response.choices[0].finish_reason != "tool_calls":
            print("\n🎯 최종 응답 생성됨")
            print("=" * 50)
            print("📋 시스템 분석 완료")
            print(f"🔢 총 반복 횟수: {count}")
            print("-" * 30)
            print("📄 최종 보고서:")
            print(response.choices[0].message.content)
            print("=" * 50)
            break

        # 도구 호출 처리
        function_call = None
        function_call_arguments = None
        function_call_id = None

        for item in response.choices[0].message.tool_calls:
            if item.type == "function":
                function_call_id = item.id
                function_call = item.function.name
                function_call_arguments = json.loads(item.function.arguments)
                
                print(f"🔧 도구 호출: {function_call}")
                if function_call == "exec_command_remote_system":
                    print(f"💻 명령어: {function_call_arguments.get('command', 'N/A')}")

        # 함수 실행
        result = select_function(function_call, function_call_arguments)
        
        print(f"📤 도구 실행 결과:")
        print(f"결과 길이: {len(result)} 문자")
        
        # 결과를 대화에 추가
        input_list.append({
            "role": "tool",
            "content": result,
            "tool_call_id": function_call_id
        })

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        print("🔄 다음 반복으로 계속...")
        break

if count >= MAX_ITERATIONS:
    print(f"\n⚠️  최대 반복 횟수 ({MAX_ITERATIONS}) 도달")
    print("분석이 복잡하여 중단되었습니다.")

print("\n🏁 Enhanced ReAct 패턴 종료")