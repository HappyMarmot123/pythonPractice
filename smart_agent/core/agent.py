import os
import operator
from typing import Annotated, TypedDict, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

from core.tools import tools

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

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    agent = SmartRAGAgent()
    inputs = {"messages": [HumanMessage(content="삼성전자의 2024년 주가 전망에 대해 알려줘")]}
    
    for output in agent.app.stream(inputs):
        print(f"단계: {list(output.keys())[0]}")