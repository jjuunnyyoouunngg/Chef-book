import streamlit as st
import google.generativeai as genai

# 💡 팁: 웹 브라우저 탭 이름과 아이콘도 요리사 컨셉으로 바꿀 수 있습니다.
st.set_page_config(page_title="Chef Chatbot", page_icon="🍳")

st.title("🍳 나만의 셰프 챗봇")
st.write("먹고 싶은 메뉴 카테고리를 선택하거나 직접 물어보세요!")

# API 키 세팅 (Secrets에서 가져오기)
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Streamlit Secrets에 API 키가 설정되지 않았습니다.")
    st.stop()

genai.configure(api_key=gemini_api_key)

try:
    # 모델 세팅 (기존과 동일)
    available_models = [
        m.name for m in genai.list_models() 
        if 'generateContent' in m.supported_generation_methods
    ]
    target_model = available_models[0]
    for m_name in available_models:
        if "flash" in m_name:
            target_model = m_name
            break
    model = genai.GenerativeModel(target_model)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 1. 기존 대화 기록 화면에 띄우기
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    st.write("---") # 화면에 가로줄 긋기 (구분선)
    st.write("#### 🍱 빠른 메뉴 추천")

    # 2. 💡 화면을 4칸으로 나누고 버튼 만들기
    col1, col2, col3, col4 = st.columns(4)
    
    # 사용자가 보낼 최종 메시지를 담아둘 변수
    user_input = None 

    # 각 칸(col)마다 버튼을 배치하고, 눌렸을 때 user_input에 질문을 지정
    with col1:
        if st.button("🍚 한식"):
            user_input = "오늘 먹기 좋은 맛있는 한식 메뉴 3가지만 추천해 줘!"
    with col2:
        if st.button("🍝 양식"):
            user_input = "분위기 좋은 양식 메뉴 3가지만 추천해 줘!"
    with col3:
        if st.button("🍜 중식"):
            user_input = "배달 시켜 먹기 좋은 중식 메뉴 3가지만 추천해 줘!"
    with col4:
        if st.button("🍣 일식"):
            user_input = "깔끔한 일식 메뉴 3가지만 추천해 줘!"

    # 3. 채팅창 입력란 (버튼을 안 누르고 직접 텍스트를 쳤을 때)
    # st.chat_input은 자동으로 화면 맨 아래에 고정됩니다.
    chat_input = st.chat_input("또는 원하는 메뉴를 직접 입력하세요!")
    if chat_input:
        user_input = chat_input # 직접 친 텍스트를 user_input에 덮어씌움

    # 4. 버튼이 눌렸거나 채팅이 입력되었을 때만 답변 생성 로직 실행!
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        history = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            history.append({"role": role, "parts": [m["content"]]})

        chat = model.start_chat(history=history)
        response_stream = chat.send_message(user_input, stream=True)

        def stream_generator():
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        with st.chat_message("assistant"):
            response = st.write_stream(stream_generator())
        st.session_state.messages.append({"role": "assistant", "content": response})
        
except Exception as e:
    st.error(f"🚨 에러 발생! 상세 원인: {e}")
