import os
from typing import Annotated
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

web_search_tool = TavilySearchResults(
    api_key=os.getenv("TAVILY_API_KEY"),
    k=3,
    search_depth="advanced",
    description=(
        "실시간 웹 검색 도구입니다. "
        "현재 사건, 최신 기술 트렌드, 또는 내부 문서에 없는 일반적인 지식을 찾을 때 사용합니다."
    )
)

@tool
def search_web(query: str) -> str:
    """
    최신 정보나 웹상의 지식이 필요할 때 이 도구를 호출하세요.
    입력값은 구체적인 검색 쿼리 문자열이어야 합니다.
    """
    # 도구 실행 및 결과 반환
    results = web_search_tool.invoke({"query": query})
    
    # 결과를 하나의 문자열로 결합 (에이전트가 읽기 편하도록 포맷팅)
    content = "\n\n".join(
        [f"소스: {res['url']}\n내용: {res['content']}" for res in results]
    )
    return content

# 2. 도구 리스트 정의 (나중에 에이전트에 전달될 목록)
tools = [search_web]

if __name__ == "__main__":
    # 테스트 코드
    from dotenv import load_dotenv
    load_dotenv()
    
    print("--- 웹 검색 테스트 시작 ---")
    test_query = "2024년 12월 삼성전자의 최신 소식은?"
    result = search_web.invoke(test_query)
    print(result)