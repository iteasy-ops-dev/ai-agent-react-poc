import os
import sys
import importlib
import importlib.util
import inspect
from typing import Dict, List, Any, Optional, Type
from tools.base_tool import BaseTool


class ToolsManager:
    """
    도구들을 자동으로 발견하고 관리하는 매니저 클래스
    순수 동적 로딩으로 새 도구 파일만 추가하면 자동 인식
    """
    
    def __init__(self, tools_dir: Optional[str] = None):
        """
        ToolsManager 초기화
        
        Args:
            tools_dir (str, optional): 도구들이 있는 디렉토리 경로
        """
        if tools_dir is None:
            tools_dir = os.path.dirname(__file__)
        
        self.tools_dir = tools_dir
        self.tools: Dict[str, BaseTool] = {}
        self.tools_classes: Dict[str, Type[BaseTool]] = {}
        
        # 패키지 경로 설정으로 임포트 문제 해결
        self._setup_package_path()
        
        # 도구들을 자동으로 발견하고 로딩
        self._discover_tools()
    
    def _setup_package_path(self):
        """
        패키지 경로를 sys.path에 추가하여 임포트 문제 해결
        """
        # tools 디렉토리의 부모 디렉토리 (프로젝트 루트)
        project_root = os.path.dirname(self.tools_dir)
        
        # sys.path에 프로젝트 루트 추가 (중복 방지)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            print(f"📁 프로젝트 루트 추가: {project_root}")
        
        # tools 패키지가 sys.modules에 등록되어 있는지 확인
        if 'tools' not in sys.modules:
            try:
                import tools
                print("📦 tools 패키지 로딩 완료")
            except ImportError as e:
                print(f"⚠️ tools 패키지 로딩 실패: {e}")
    
    def _discover_tools(self):
        """
        tools 디렉토리에서 도구들을 자동으로 발견하고 로딩
        """
        # tools 디렉토리의 모든 Python 파일 검색
        for filename in os.listdir(self.tools_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                if filename in ['base_tool.py', 'tools_manager.py']:
                    continue
                    
                module_name = filename[:-3]  # .py 제거
                self._load_tool_from_file(filename, module_name)
    
    def _load_tool_from_file(self, filename: str, module_name: str):
        """
        파일에서 도구를 로드 - 다층 fallback 전략
        
        Args:
            filename (str): 파일명
            module_name (str): 모듈명
        """
        full_module_name = f"tools.{module_name}"
        
        # 전략 1: importlib.import_module (가장 안전)
        if self._load_with_import_module(full_module_name, module_name):
            return
        
        # 전략 2: importlib.util.spec_from_file_location (직접 로딩)
        if self._load_with_spec_from_file(filename, full_module_name, module_name):
            return
        
        # 전략 3: 파일 직접 읽기 및 exec (최후 수단)
        if self._load_with_exec(filename, full_module_name, module_name):
            return
        
        print(f"❌ 모든 로딩 전략 실패: {filename}")
    
    def _load_with_import_module(self, full_module_name: str, module_name: str) -> bool:
        """
        importlib.import_module을 사용한 표준 로딩
        """
        try:
            print(f"🔄 표준 임포트 시도: {full_module_name}")
            module = importlib.import_module(full_module_name)
            return self._extract_tools_from_module(module, module_name, "import_module")
            
        except ImportError as e:
            print(f"📝 표준 임포트 실패: {full_module_name} - {str(e)}")
            return False
        except Exception as e:
            print(f"❌ 표준 임포트 오류: {full_module_name} - {str(e)}")
            return False
    
    def _load_with_spec_from_file(self, filename: str, full_module_name: str, module_name: str) -> bool:
        """
        importlib.util.spec_from_file_location을 사용한 직접 로딩
        """
        try:
            print(f"🔄 파일 스펙 로딩 시도: {filename}")
            file_path = os.path.join(self.tools_dir, filename)
            
            spec = importlib.util.spec_from_file_location(full_module_name, file_path)
            if spec is None or spec.loader is None:
                print(f"📝 스펙 생성 실패: {filename}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            
            # sys.modules에 등록하여 패키지 컨텍스트 제공
            sys.modules[full_module_name] = module
            
            # 모듈 실행
            spec.loader.exec_module(module)
            
            return self._extract_tools_from_module(module, module_name, "spec_from_file")
            
        except Exception as e:
            print(f"📝 파일 스펙 로딩 실패: {filename} - {str(e)}")
            return False
    
    def _load_with_exec(self, filename: str, full_module_name: str, module_name: str) -> bool:
        """
        파일 내용을 직접 읽어서 exec으로 실행 (최후 수단)
        """
        try:
            print(f"🔄 직접 실행 시도: {filename}")
            file_path = os.path.join(self.tools_dir, filename)
            
            # 파일 내용 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # 새로운 모듈 생성
            module = type(sys)('tools.' + module_name)
            module.__file__ = file_path
            module.__name__ = full_module_name
            
            # sys.modules에 등록
            sys.modules[full_module_name] = module
            
            # 코드 실행
            exec(source_code, module.__dict__)
            
            return self._extract_tools_from_module(module, module_name, "exec")
            
        except Exception as e:
            print(f"📝 직접 실행 실패: {filename} - {str(e)}")
            return False
    
    def _extract_tools_from_module(self, module, module_name: str, method: str) -> bool:
        """
        모듈에서 BaseTool 서브클래스를 찾아 등록
        """
        found_tools = 0
        
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (obj != BaseTool and 
                issubclass(obj, BaseTool) and 
                getattr(obj, '__module__', '').endswith(module_name)):
                
                try:
                    # 도구 인스턴스 생성
                    tool_instance = obj()
                    self.tools[tool_instance.name] = tool_instance
                    self.tools_classes[tool_instance.name] = obj
                    
                    print(f"✅ 도구 로딩 성공: {tool_instance.name} ({name}) via {method}")
                    found_tools += 1
                    
                except Exception as e:
                    print(f"❌ 도구 인스턴스 생성 실패: {name} - {str(e)}")
        
        return found_tools > 0
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        이름으로 도구 인스턴스 조회
        
        Args:
            name (str): 도구명
            
        Returns:
            BaseTool: 도구 인스턴스 (없으면 None)
        """
        return self.tools.get(name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """
        모든 도구 인스턴스 반환
        
        Returns:
            Dict[str, BaseTool]: 도구명: 도구인스턴스 매핑
        """
        return self.tools.copy()
    
    def get_function_registry(self) -> Dict[str, BaseTool]:
        """
        함수 레지스트리 형태로 도구들 반환 (AgentClient 호환성)
        
        Returns:
            Dict[str, BaseTool]: 함수명: 도구인스턴스 매핑
        """
        return self.tools.copy()
    
    def get_tools_schemas(self) -> List[Dict[str, Any]]:
        """
        모든 도구들의 OpenAI 스키마 반환
        
        Returns:
            List[Dict]: OpenAI tools 스키마 리스트
        """
        schemas = []
        for tool in self.tools.values():
            schemas.append(tool.get_schema())
        return schemas
    
    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """
        도구 실행
        
        Args:
            name (str): 실행할 도구명
            arguments (Dict): 도구 인자
            
        Returns:
            str: 실행 결과
        """
        tool = self.get_tool(name)
        if not tool:
            return f"{{\"error\": \"알 수 없는 도구: {name}\", \"available_tools\": {list(self.tools.keys())}}}"
        
        # 인자 유효성 검사
        missing_args = tool.get_missing_arguments(arguments)
        if missing_args:
            return f"{{\"error\": \"필수 인자가 누락되었습니다: {missing_args}\"}}"
        
        try:
            return tool.execute(**arguments)
        except Exception as e:
            return f"{{\"error\": \"도구 실행 중 오류가 발생했습니다: {str(e)}\", \"tool\": \"{name}\", \"arguments\": {arguments}}}"
    
    def get_available_tools(self) -> List[str]:
        """
        사용 가능한 도구 목록 반환
        
        Returns:
            List[str]: 도구명 목록
        """
        return list(self.tools.keys())
    
    def reload_tools(self):
        """
        도구들을 다시 로딩 (개발 시 유용)
        """
        self.tools.clear()
        self.tools_classes.clear()
        self._discover_tools()
    
    def get_tool_info(self, name: str) -> Dict[str, Any]:
        """
        도구 정보 반환
        
        Args:
            name (str): 도구명
            
        Returns:
            Dict: 도구 정보
        """
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"도구를 찾을 수 없습니다: {name}"}
        
        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
            "schema": tool.get_schema(),
            "class": tool.__class__.__name__
        }
    
    def __len__(self) -> int:
        """로딩된 도구 개수"""
        return len(self.tools)
    
    def __str__(self) -> str:
        """문자열 표현"""
        return f"ToolsManager(tools={len(self.tools)}: {list(self.tools.keys())})"
    
    def __repr__(self) -> str:
        """개발자용 표현"""
        return self.__str__()