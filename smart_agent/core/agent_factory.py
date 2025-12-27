"""
AI 에이전트 팩토리 모듈
다양한 AI 타입에 맞는 에이전트를 생성합니다.
"""
from enum import Enum
from core.agent import SmartRAGAgent, CodeGeneratorAgent

class AgentType(str, Enum):
    """사용 가능한 AI 에이전트 타입"""
    WEB_SEARCH = "web_search"  # 웹 검색 기반 RAG 에이전트
    CODE_GENERATOR = "code_generator"  # 코드 생성 및 실시간 프리뷰 에이전트
    VIDEO_QA = "video_qa"  # 영상 기반 Q&A 비서
    # 향후 추가될 AI 타입들...

class AgentFactory:
    """AI 에이전트를 생성하는 팩토리 클래스"""
    
    @staticmethod
    def create_agent(agent_type: AgentType):
        """
        AI 타입에 맞는 에이전트를 생성합니다.
        
        Args:
            agent_type: 생성할 에이전트 타입
            
        Returns:
            생성된 에이전트 인스턴스
        """
        match agent_type:
            case AgentType.WEB_SEARCH:
                return SmartRAGAgent()
            case AgentType.CODE_GENERATOR:
                return CodeGeneratorAgent()
            case AgentType.VIDEO_QA:
                # TODO: 영상 Q&A 에이전트 구현
                raise NotImplementedError("영상 Q&A 에이전트는 아직 구현되지 않았습니다.")
            case _:
                raise ValueError(f"알 수 없는 에이전트 타입: {agent_type}")
    
    @staticmethod
    def get_agent_info(agent_type: AgentType) -> dict:
        """
        AI 타입에 대한 정보를 반환합니다.
        
        Args:
            agent_type: 에이전트 타입
            
        Returns:
            에이전트 정보 딕셔너리 (name, description, icon)
        """
        agent_info = {
            AgentType.WEB_SEARCH: {
                "name": "웹 검색 비서",
                "description": "실시간 웹 검색을 통해 최신 정보를 찾아 답변합니다.",
                "icon": "🌐"
            },
            AgentType.CODE_GENERATOR: {
                "name": "코드 생성 에이전트",
                "description": "코드를 생성하고 실시간으로 프리뷰를 제공합니다.",
                "icon": "💻"
            },
            AgentType.VIDEO_QA: {
                "name": "영상 Q&A 비서",
                "description": "영상 내용을 분석하여 질문에 답변합니다.",
                "icon": "🎥"
            }
        }
        return agent_info.get(agent_type, {
            "name": "알 수 없는 에이전트",
            "description": "",
            "icon": "❓"
        })

