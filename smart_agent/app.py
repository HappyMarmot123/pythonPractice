import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from core.agent_factory import AgentFactory, AgentType
import uuid
from datetime import datetime

load_dotenv()

st.set_page_config(page_title="Smart AI Agent", page_icon="🤖", layout="wide")

# 채팅 히스토리 관리 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}  # {chat_id: {"messages": [...], "title": "...", "created_at": "...", "agent_type": "..."}}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "show_agent_selection" not in st.session_state:
    st.session_state.show_agent_selection = False

# 에이전트 캐시 (타입별로 에이전트 인스턴스 저장)
if "agent_cache" not in st.session_state:
    st.session_state.agent_cache = {}

# 현재 채팅의 메시지 가져오기
def get_current_messages():
    if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chat_history:
        return st.session_state.chat_history[st.session_state.current_chat_id]["messages"]
    return []

def set_current_messages(messages):
    if st.session_state.current_chat_id:
        if st.session_state.current_chat_id not in st.session_state.chat_history:
            st.session_state.chat_history[st.session_state.current_chat_id] = {
                "messages": [],
                "title": "새 채팅",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "agent_type": None
            }
        st.session_state.chat_history[st.session_state.current_chat_id]["messages"] = messages

def get_current_agent():
    """현재 채팅의 에이전트를 가져옵니다."""
    if not st.session_state.current_chat_id:
        return None
    
    chat_data = st.session_state.chat_history.get(st.session_state.current_chat_id)
    if not chat_data or not chat_data.get("agent_type"):
        return None
    
    agent_type = AgentType(chat_data["agent_type"])
    
    # 에이전트 캐시에서 가져오거나 생성
    if agent_type not in st.session_state.agent_cache:
        try:
            st.session_state.agent_cache[agent_type] = AgentFactory.create_agent(agent_type)
        except NotImplementedError as e:
            st.error(str(e))
            return None
    
    return st.session_state.agent_cache[agent_type]

def create_new_chat(agent_type: AgentType):
    """새 채팅을 생성합니다."""
    new_chat_id = str(uuid.uuid4())
    st.session_state.current_chat_id = new_chat_id
    st.session_state.chat_history[new_chat_id] = {
        "messages": [],
        "title": "새 채팅",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "agent_type": agent_type.value
    }
    st.session_state.show_agent_selection = False
    st.rerun()

# 사이드바 - 채팅 관리
with st.sidebar:
    st.header("💬 채팅 관리")
    
    # 새 채팅 생성 버튼
    if st.button("➕ 새 채팅", use_container_width=True):
        st.session_state.show_agent_selection = True
        st.rerun()
    
    st.markdown("---")
    st.subheader("📋 채팅 목록")
    
    # 채팅 목록 표시
    if st.session_state.chat_history:
        # 최신순으로 정렬
        sorted_chats = sorted(
            st.session_state.chat_history.items(),
            key=lambda x: x[1]["created_at"],
            reverse=True
        )
        
        for chat_id, chat_data in sorted_chats:
            # 채팅 제목 생성 (첫 번째 메시지 기반)
            if not chat_data["messages"]:
                title = "새 채팅"
            else:
                first_user_msg = next(
                    (msg.content for msg in chat_data["messages"] if isinstance(msg, HumanMessage)),
                    "새 채팅"
                )
                title = first_user_msg[:25] + "..." if len(first_user_msg) > 25 else first_user_msg
            
            # AI 타입 아이콘 추가
            agent_type_icon = ""
            if chat_data.get("agent_type"):
                try:
                    agent_type = AgentType(chat_data["agent_type"])
                    agent_info = AgentFactory.get_agent_info(agent_type)
                    agent_type_icon = agent_info["icon"] + " "
                except:
                    pass
            
            # 현재 채팅인지 표시
            is_active = chat_id == st.session_state.current_chat_id
            button_label = f"{agent_type_icon}{title}" if not is_active else f"✅ {agent_type_icon}{title}"
            
            # 채팅 버튼과 삭제 버튼을 같은 행에 배치
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(
                    button_label,
                    key=f"chat_{chat_id}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary"
                ):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()
            
            with col2:
                if st.button("🗑️", key=f"delete_{chat_id}", help="채팅 삭제"):
                    if chat_id in st.session_state.chat_history:
                        del st.session_state.chat_history[chat_id]
                    if st.session_state.current_chat_id == chat_id:
                        # 삭제된 채팅이 현재 채팅이면 새 채팅 생성
                        if st.session_state.chat_history:
                            st.session_state.current_chat_id = list(st.session_state.chat_history.keys())[0]
                        else:
                            st.session_state.current_chat_id = None
                    st.rerun()
    else:
        st.caption("채팅 기록이 없습니다. 새 채팅을 시작하세요.")
    
    st.markdown("---")
    
    # 현재 채팅의 AI 타입 표시
    if st.session_state.current_chat_id:
        chat_data = st.session_state.chat_history.get(st.session_state.current_chat_id)
        if chat_data and chat_data.get("agent_type"):
            agent_type = AgentType(chat_data["agent_type"])
            agent_info = AgentFactory.get_agent_info(agent_type)
            st.caption(f"현재 AI: {agent_info['icon']} {agent_info['name']}")

# AI 타입 선택 화면
if st.session_state.show_agent_selection or st.session_state.current_chat_id is None:
    st.title("🤖 AI 에이전트 선택")
    st.markdown("사용할 AI 에이전트를 선택하세요.")
    
    # 사용 가능한 AI 타입들
    available_agents = [
        AgentType.WEB_SEARCH,
        AgentType.CODE_GENERATOR,
        AgentType.VIDEO_QA
    ]
    
    # AI 타입별 카드 표시
    cols = st.columns(len(available_agents))
    
    for idx, agent_type in enumerate(available_agents):
        with cols[idx]:
            agent_info = AgentFactory.get_agent_info(agent_type)
            
            # 카드 스타일
            st.markdown(f"""
            <div style="
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                height: 200px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                cursor: pointer;
                transition: all 0.3s;
            " onmouseover="this.style.borderColor='#4CAF50'" onmouseout="this.style.borderColor='#e0e0e0'">
                <h2 style="font-size: 48px; margin: 0;">{agent_info['icon']}</h2>
                <h3 style="margin: 10px 0;">{agent_info['name']}</h3>
                <p style="color: #666; font-size: 14px;">{agent_info['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 선택 버튼
            if st.button(f"{agent_info['name']} 선택", key=f"select_{agent_type.value}", use_container_width=True):
                try:
                    create_new_chat(agent_type)
                except NotImplementedError as e:
                    st.error(str(e))
    
    st.markdown("---")
    st.caption("💡 각 AI 에이전트는 특정 작업에 최적화되어 있습니다.")

# 현재 채팅이 있고 AI가 선택된 경우
elif st.session_state.current_chat_id:
    chat_data = st.session_state.chat_history.get(st.session_state.current_chat_id)
    
    if chat_data and chat_data.get("agent_type"):
        # 현재 채팅의 AI 정보 표시
        agent_type = AgentType(chat_data["agent_type"])
        agent_info = AgentFactory.get_agent_info(agent_type)
        
        st.title(f"{agent_info['icon']} {agent_info['name']}")
        st.caption(agent_info['description'])
        
        # 현재 채팅의 메시지 표시
        current_messages = get_current_messages()
        
        for message in current_messages:
            role = "user" if isinstance(message, HumanMessage) else "assistant"
            with st.chat_message(role):
                st.markdown(message.content)

# 사용자 입력 처리
if st.session_state.current_chat_id and not st.session_state.show_agent_selection:
    chat_data = st.session_state.chat_history.get(st.session_state.current_chat_id)
    
    if chat_data and chat_data.get("agent_type"):
        agent = get_current_agent()
        
        if agent:
            current_messages = get_current_messages()
            agent_info = AgentFactory.get_agent_info(AgentType(chat_data["agent_type"]))
            
            placeholder_text = {
                AgentType.WEB_SEARCH: "무엇이든 물어보세요 (예: 오늘 삼성전자 주가는?, 최신 AI 트렌드는?)",
                AgentType.CODE_GENERATOR: "코드 생성 요청을 입력하세요 (예: Python으로 웹 크롤러 만들어줘)",
                AgentType.VIDEO_QA: "영상에 대한 질문을 입력하세요"
            }.get(AgentType(chat_data["agent_type"]), "무엇이든 물어보세요")
            
            if prompt := st.chat_input(placeholder_text):
                # 메시지 추가
                current_messages.append(HumanMessage(content=prompt))
                set_current_messages(current_messages)
                
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner(f"🤔 {agent_info['name']}가 생각 중..."):
                        inputs = {"messages": current_messages}
                        final_state = agent.app.invoke(inputs)
                        
                        last_message = final_state["messages"][-1]
                        response_content = last_message.content
                        
                        # 응답 파싱
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
                        
                        # 웹 검색 사용 여부 확인 (웹 검색 에이전트인 경우)
                        if AgentType(chat_data["agent_type"]) == AgentType.WEB_SEARCH:
                            web_searched = any(
                                hasattr(msg, "tool_calls") and msg.tool_calls 
                                for msg in final_state["messages"]
                            )
                            
                            if web_searched:
                                st.caption("🌐 웹 검색 결과를 참고하여 답변했습니다.")
                        
                        # 코드 생성 에이전트인 경우 코드 블록 감지 및 프리뷰
                        if AgentType(chat_data["agent_type"]) == AgentType.CODE_GENERATOR:
                            import re
                            code_blocks = re.findall(r'```(\w+)?\n(.*?)```', response_content, re.DOTALL)
                            
                            if code_blocks:
                                st.caption("💻 생성된 코드를 확인하세요. 실행 결과를 프리뷰할 수 있습니다.")
                                
                                # HTML, CSS, JavaScript 코드 블록을 분리해서 수집
                                html_code = None
                                css_code = None
                                js_code = None
                                
                                for idx, (lang, code) in enumerate(code_blocks):
                                    lang_lower = (lang or "").lower()
                                    if lang_lower == "html":
                                        html_code = code
                                    elif lang_lower == "css":
                                        css_code = code
                                    elif lang_lower in ["javascript", "js"]:
                                        js_code = code
                                
                                # HTML/CSS/JavaScript 프리뷰 (HTML이 있는 경우만 프리뷰)
                                if html_code:
                                    with st.expander("🌐 웹 프리뷰", expanded=True):
                                        # CSS와 JavaScript를 HTML에 포함
                                        full_html = ""
                                        
                                        if css_code:
                                            full_html += f"<style>\n{css_code}\n</style>\n"
                                        
                                        if js_code:
                                            full_html += f"<script>\n{js_code}\n</script>\n"
                                        
                                        full_html += html_code
                                        
                                        # Streamlit에서 HTML 렌더링
                                        st.components.v1.html(full_html, height=400, scrolling=True)
                                        
                                        # 코드 표시
                                        with st.expander("📝 HTML 코드 보기"):
                                            st.code(html_code, language="html")
                                        
                                        if css_code:
                                            with st.expander("🎨 CSS 코드 보기"):
                                                st.code(css_code, language="css")
                                        
                                        if js_code:
                                            with st.expander("⚡ JavaScript 코드 보기"):
                                                st.code(js_code, language="javascript")
                                        
                                        # 저장 버튼
                                        cols = st.columns(3 if js_code else 2)
                                        with cols[0]:
                                            if st.button("💾 HTML 저장", key=f"save_html_{st.session_state.current_chat_id}"):
                                                from core.code_tools import save_code
                                                result = save_code.invoke({"code": html_code, "filename": "generated_html", "language": "html"})
                                                st.success(result)
                                        with cols[1]:
                                            if css_code and st.button("💾 CSS 저장", key=f"save_css_{st.session_state.current_chat_id}"):
                                                from core.code_tools import save_code
                                                result = save_code.invoke({"code": css_code, "filename": "generated_css", "language": "css"})
                                                st.success(result)
                                        if js_code:
                                            with cols[2]:
                                                if st.button("💾 JS 저장", key=f"save_js_{st.session_state.current_chat_id}"):
                                                    from core.code_tools import save_code
                                                    result = save_code.invoke({"code": js_code, "filename": "generated_js", "language": "javascript"})
                                                    st.success(result)
                                
                                # HTML이 없는 경우 CSS나 JavaScript만 있는 경우 코드만 표시
                                elif css_code or js_code:
                                    if css_code:
                                        with st.expander("🎨 CSS 코드", expanded=True):
                                            st.code(css_code, language="css")
                                            if st.button("💾 CSS 저장", key=f"save_css_only_{st.session_state.current_chat_id}"):
                                                from core.code_tools import save_code
                                                result = save_code.invoke({"code": css_code, "filename": "generated_css", "language": "css"})
                                                st.success(result)
                                    
                                    if js_code:
                                        with st.expander("⚡ JavaScript 코드", expanded=True):
                                            st.code(js_code, language="javascript")
                                            if st.button("💾 JS 저장", key=f"save_js_only_{st.session_state.current_chat_id}"):
                                                from core.code_tools import save_code
                                                result = save_code.invoke({"code": js_code, "filename": "generated_js", "language": "javascript"})
                                                st.success(result)
                        
                        st.markdown(response_content)
                        
                        # 응답 메시지 저장
                        current_messages.append(AIMessage(content=response_content))
                        set_current_messages(current_messages)