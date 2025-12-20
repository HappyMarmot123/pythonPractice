import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from core.agent import SmartRAGAgent

load_dotenv()

st.set_page_config(page_title="Smart RAG Agent", page_icon="🤖")
st.title("🤖 지능형 검색 에이전트")
st.markdown("실시간 웹 검색과 AI를 결합한 스마트 비서입니다.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = SmartRAGAgent()

with st.sidebar:
    st.header("⚙️ 설정")
    
    if st.button("🗑️ 대화 기록 삭제"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.caption("💡 이 에이전트는 웹 검색을 통해 최신 정보를 찾아 답변합니다.")

for message in st.session_state.messages:
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(message.content)

if prompt := st.chat_input("무엇이든 물어보세요 (예: 오늘 삼성전자 주가는?, 최신 AI 트렌드는?)"):
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤔 검색하고 생각 중..."):
            # 세션 내에서만 대화 이어가기 (영속적 저장 없음)
            inputs = {"messages": st.session_state.messages}
            final_state = st.session_state.agent.app.invoke(inputs)
            
            last_message = final_state["messages"][-1]
            
            response_content = last_message.content
            
            if isinstance(response_content, list):
                text_parts = []
                for item in response_content:
                    if isinstance(item, dict) and "text" in item:
                        text_parts.append(item["text"])
                    elif isinstance(item, str):
                        text_parts.append(item)
                response_content = "\n".join(text_parts) if text_parts else str(response_content)
            elif isinstance(response_content, dict):
                response_content = response_content.get("text", str(response_content))
            
            web_searched = any(
                hasattr(msg, "tool_calls") and msg.tool_calls 
                for msg in final_state["messages"]
            )
            
            if web_searched:
                st.caption("🌐 웹 검색 결과를 참고하여 답변했습니다.")
            
            st.markdown(response_content)
            st.session_state.messages.append(AIMessage(content=response_content))