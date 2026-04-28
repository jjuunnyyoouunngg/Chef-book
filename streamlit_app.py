import streamlit as st
import google.generativeai as genai

st.title("💬 Gemini Chatbot")
st.write("Google API가 사용 가능한 최신 모델을 자동으로 찾아 연결합니다.")

gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    genai.configure(api_key=gemini_api_key)
    
    try:
        # 💡 핵심 수정: 내 API 키로 접근 가능한 모델 목록을 구글 서버에서 받아옵니다.
        available_models = [
            m.name for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
        
        # 쓸 수 있는 모델 중 빠르고 가벼운 'flash' 모델을 찾아 우선적으로 선택합니다.
        target_model = available_models[0] # 기본값
        for m_name in available_models:
            if "flash" in m_name:
                target_model = m_name
                break
                
        # 찾은 모델로 챗봇 엔진 장착!
        model = genai.GenerativeModel(target_model)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("What is up?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            history = []
            for m in st.session_state.messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                history.append({"role": role, "parts": [m["content"]]})

            # 메시지 전송
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
        # 또 다른 에러가 나면 화면에 원인과 함께 '사용 가능한 모델 전체 목록'을 출력해 줍니다.
        st.error(f"🚨 에러 발생! 상세 원인: {e}")
        if 'available_models' in locals():
            st.warning(f"참고 - 현재 내 API 키로 사용 가능한 모델 목록:\n{available_models}")
