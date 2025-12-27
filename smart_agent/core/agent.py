import os
import operator
from typing import Annotated, TypedDict, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

from core.tools import tools
from core.code_tools import code_tools
from core.video_tools import video_tools

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

class SmartRAGAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        self.llm_with_tools = self.llm.bind_tools(tools)
        self.workflow = StateGraph(AgentState)
        self._build_graph()

    def _build_graph(self):
        self.workflow.add_node("agent", self.agent_node)
        self.workflow.add_node("tools", ToolNode(tools))
        self.workflow.set_entry_point("agent")
        self.workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        self.workflow.add_edge("tools", "agent")
        self.app = self.workflow.compile()

    def agent_node(self, state: AgentState):
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(self, state: AgentState) -> str:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        return "end"

class CodeGeneratorAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3,  # 코드 생성에는 약간의 창의성 허용
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        self.llm_with_tools = self.llm.bind_tools(code_tools)
        self.workflow = StateGraph(AgentState)
        self._build_graph()

    def _build_graph(self):
        self.workflow.add_node("agent", self.agent_node)
        self.workflow.add_node("tools", ToolNode(code_tools))
        self.workflow.set_entry_point("agent")
        self.workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        self.workflow.add_edge("tools", "agent")
        self.app = self.workflow.compile()

    def agent_node(self, state: AgentState):
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(self, state: AgentState) -> str:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        return "end"

class VideoQAAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        self.llm_with_tools = self.llm.bind_tools(video_tools)
        self.workflow = StateGraph(AgentState)
        self._build_graph()

    def _build_graph(self):
        self.workflow.add_node("agent", self.agent_node)
        self.workflow.add_node("tools", ToolNode(video_tools))
        self.workflow.set_entry_point("agent")
        self.workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        self.workflow.add_edge("tools", "agent")
        self.app = self.workflow.compile()

    def agent_node(self, state: AgentState):
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(self, state: AgentState) -> str:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        return "end"

class PersonaAgent:
    """페르소나 기반 챗봇 에이전트 (트럼프 대통령 말투)"""
    
    def __init__(self, persona_name: str = "트럼프"):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.8,  # 창의성 높여서 말투 표현
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        self.persona_name = persona_name
        self.workflow = StateGraph(AgentState)
        self._build_graph()
    
    def _get_system_prompt(self) -> str:
        """페르소나에 맞는 시스템 프롬프트 반환"""
        if self.persona_name == "트럼프":
            return """당신은 도널드 트럼프 대통령의 말투와 스타일로 대화하는 AI입니다.

말투 특징:
- "엄청난", "환상적인", "믿어봐" 같은 강한 표현 사용
- "우리는 할 거야", "이건 최고가 될 거야" 같은 미래형 표현
- "최고의", "가장 위대한" 같은 최상급 표현
- 자신감 있고 강렬한 어조
- 짧고 임팩트 있는 문장
- "정말", "완전히", "절대적으로" 같은 강조 표현

예시:
- "이건 정말 환상적인 질문이야, 믿어봐!"
- "우리는 최고의 답변을 할 거야, 절대적으로!"
- "이건 엄청난 아이디어야, 정말 훌륭해!"

항상 트럼프 대통령의 말투를 유지하면서도 정확하고 도움이 되는 답변을 제공하세요."""
        return ""
    
    def _build_graph(self):
        self.workflow.add_node("agent", self.agent_node)
        self.workflow.set_entry_point("agent")
        self.workflow.add_edge("agent", END)
        self.app = self.workflow.compile()
    
    def agent_node(self, state: AgentState):
        messages = state["messages"]
        
        # 시스템 프롬프트를 첫 메시지에 추가
        system_prompt = self._get_system_prompt()
        if system_prompt:
            # 첫 메시지가 시스템 프롬프트가 아니면 추가
            if not messages or not isinstance(messages[0], SystemMessage):
                messages_with_system = [SystemMessage(content=system_prompt)] + messages
            else:
                messages_with_system = messages
        else:
            messages_with_system = messages
        
        response = self.llm.invoke(messages_with_system)
        return {"messages": [response]}

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    agent = SmartRAGAgent()
    inputs = {"messages": [HumanMessage(content="삼성전자의 2024년 주가 전망에 대해 알려줘")]}
    
    for output in agent.app.stream(inputs):
        print(f"단계: {list(output.keys())[0]}")