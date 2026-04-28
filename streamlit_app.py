import streamlit as st
import google.generativeai as genai

# Show title and description.
st.title("💬 Gemini Chatbot")
st.write(
    "This is a simple chatbot that uses Google's Gemini model to generate responses. "
    "To use this app, you need to provide a Gemini API key, which you can get [here](https://aistudio.google.com/app/apikey)."
)

# Ask user for their Gemini API key via `st.text_input`.
gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:

    # Configure the Gemini API.
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    # Create a session state variable to store the chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Streamlit의 대화 기록을 Gemini가 이해할 수 있는 형식으로 변환
        history = []
        for m in st.session_state.messages[:-1]: # 방금 입력한 프롬프트는 제외
            role = "user" if m["role"] == "user" else "model"
            history.append({"role": role, "parts": [m["content"]]})

        # Generate a response using the Gemini API.
        chat = model.start_chat(history=history)
        response_stream = chat.send_message(prompt, stream=True)

        # Gemini의 스트리밍 데이터를 Streamlit 화면에 출력하기 위한 헬퍼 함수
        def stream_generator():
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        # Stream the response to the chat using `st.write_stream`, then store it in session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream_generator())
        st.session_state.messages.append({"role": "assistant", "content": response})
