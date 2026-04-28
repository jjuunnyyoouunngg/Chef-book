import streamlit as st
import google.generativeai as genai

st.title("💬 Gemini Chatbot")
st.write("이제 새로고침해도 API 키를 물어보지 않습니다! 😎")

# 💡 수정: 텍스트 입력창(st.text_input)을 없애고, Streamlit 서버 금고(Secrets)에서 키를 몰래 꺼내옵니다.
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    # 만약 서버 설정(Secrets)에 키를 제대로 안 적어뒀다면 에러를 띄웁니다.
    st.error("Streamlit Secrets에 API 키가 설정되지 않았습니다.")
    st.stop()

# 꺼내온 키로 Gemini API 즉시 연결
genai.configure(api_key=gemini_api_key)

try:
    # 사용 가능한 모델 자동 탐색 및 연결 로직 (이전과 동일)
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

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("무엇이든 물어보세요!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        history = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            history.append({"role": role, "parts": [m["content"]]})

        chat = model.start_chat(history=history)
        response_stream = chat.send_message(prompt, stream=True)

        def stream_generator():
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        with st.chat_message("assistant"):
            response = st.write_stream(stream_generator())
        st.session_state.messages.append({"role": "assistant", "content": response})
        
except Exception as e:
    st.error(f"🚨 에러 발생! 상세 원인: {e}")
