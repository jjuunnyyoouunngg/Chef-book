import streamlit as st
import google.generativeai as genai

st.title("💬 Gemini Chatbot")
st.write(
    "This is a simple chatbot that uses Google's Gemini model to generate responses. "
    "To use this app, you need to provide a Gemini API key, which you can get [here](https://aistudio.google.com/app/apikey)."
)

gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    genai.configure(api_key=gemini_api_key)
    
    # 💡 수정 1: 구버전 라이브러리에서도 100% 인식하는 가장 안정적인 기본 모델명으로 변경
    model = genai.GenerativeModel('gemini-pro')

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

        # 💡 수정 2: 에러가 나면 서버가 숨기지 못하게 빨간 박스로 진짜 에러 원인을 화면에 출력
        try:
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
