from pathlib import Path
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def generate_code(description: str, language: str = "python") -> str:
    """
    사용자의 요청에 따라 코드를 생성합니다.
    
    Args:
        description: 생성할 코드에 대한 설명
        language: 프로그래밍 언어 (python, javascript, html 등)
    
    Returns:
        생성된 코드 문자열
    """
    # 이 함수는 LLM이 직접 코드를 생성하므로 여기서는 설명만 반환
    # 실제 코드 생성은 LLM이 메시지에서 직접 수행
    return f"코드 생성 요청: {description} ({language})"

@tool
def save_code(code: str, filename: str, language: str = "python") -> str:
    """
    생성된 코드를 파일로 저장합니다.
    
    Args:
        code: 저장할 코드
        filename: 파일명
        language: 프로그래밍 언어 (확장자 결정에 사용)
    
    Returns:
        저장 결과 메시지
    """
    try:
        # 확장자 결정
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "js": ".js",
            "html": ".html",
            "css": ".css",
            "json": ".json"
        }
        ext = extensions.get(language.lower(), ".txt")
        
        # 파일명에 확장자가 없으면 추가
        if not filename.endswith(ext):
            filename += ext
        
        # 코드 저장 디렉토리 생성
        code_dir = Path("generated_code")
        code_dir.mkdir(exist_ok=True)
        
        filepath = code_dir / filename
        
        # 파일 저장
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        
        return f"코드가 저장되었습니다: {filepath}"
    
    except Exception as e:
        return f"파일 저장 중 오류 발생: {str(e)}"

# 도구 리스트
code_tools = [generate_code, save_code]