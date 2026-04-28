import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 제목 변경
st.set_page_config(page_title="AI 쉐프의 레시피", page_icon="🍳")
st.title("🍳 AI 쉐프의 레시피")
st.write("원하는 요리 종류를 선택하거나, 하단 채팅창에 궁금한 음식을 물어보세요!")

# ---------------------------------------------------------
# 📖 2. 카테고리별 레시피 보관함 (여기에 내용을 채워주세요)
# ---------------------------------------------------------
MY_RECIPES = {
    "한식": "한식의 기본은 장맛입니다! 어떤 한식 레시피가 궁금하신가요?",
    "중식": "불맛이 살아있는 중식 레시피를 준비 중입니다.",
    "일식": "깔끔하고 정갈한 일식 요리법입니다.",
    "양식": "홈파티에 어울리는 근사한 양식 레시피입니다.",
    "분식": "매콤달콤한 국민 간식, 분식 레시피입니다.",
    "동남아식": "이국적인 향신료가 매력적인 동남아 요리입니다.",
    "유럽식": "정통 유럽 스타일의 가정식 레시피입니다.",
    "남미식": "열정 가득한 남미의 맛을 느껴보세요.",
    "채식": "몸도 마음도 가벼워지는 건강한 채식 식단입니다.",
    "건강식": "영양 가득, 기운을 북돋아 주는 건강 레시피입니다.",
    "디저트/베이킹": "달콤한 행복을 굽는 베이킹 가이드입니다.",
    "간편식": "바쁜 일상 속, 10분 만에 뚝딱 만드는 간편 요리입니다.",
    "음료": "상큼하고 시원한 홈메이드 음료 레시피입니다.",
    "주류": "요리와 어울리는 어른들의 음료 가이드입니다."
}
# ---------------------------------------------------------

# Gemini API 세팅
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Streamlit Secrets에 API 키가 설정되지 않았습니다.")
    st.stop()

genai.configure(api_key=gemini_api_key)

try:
    # 모델 자동 탐색 및 연결
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in available_models if "flash" in m), available_models[0])
    model = genai.GenerativeModel(target_model)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 이전 대화 띄우기
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    st.write("---")
    st.write("#### 🍱 요리 카테고리 선택")

    # 3. 💡 15개의 버튼을 3열 5행으로 배치
    categories = list(MY_RECIPES.keys()) + ["기타"]
    cols = st.columns(3) # 3개의 칸으로 나누기
    
    user_input = None

    for i, category in enumerate(categories):
        with cols[i % 3]: # 0,1,2번째 칸을 번갈아가며 사용
            if st.button(f"{category}", use_container_width=True):
                if category == "기타":
                    user_input = "제가 가진 레시피 외에 새로운 요리를 찾고 싶어요! 어떤 음식을 도와드릴까요?"
                else:
                    # 버튼을 누르면 해당 카테고리의 기본 안내를 출력
                    user_input = f"{category} 카테고리를 선택하셨습니다. 관련하여 추천하는 레시피나 궁금한 메뉴가 있으신가요?"

    # 4. 채팅 입력창
    chat_input = st.chat_input("궁금한 음식 이름을 입력하세요 (예: 제육볶음 레시피)")
    if chat_input:
        user_input = chat_input

    # 5. 답변 생성 로직
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 셰프 페르소나 부여
        chef_prompt = f"너는 'AI 쉐프'야. 사용자가 '{user_input}'에 대해 물어봤어. 만약 음식 이름을 말했다면 아주 맛있는 레시피를 재료와 단계별 설명으로 친절하게 알려줘."

        history = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            history.append({"role": role, "parts": [m["content"]]})

        chat = model.start_chat(history=history)
        response_stream = chat.send_message(chef_prompt, stream=True)

        with st.chat_message("assistant"):
            def stream_generator():
                for chunk in response_stream:
                    if chunk.text: yield chunk.text
            response = st.write_stream(stream_generator())
        st.session_state.messages.append({"role": "assistant", "content": response})
        
except Exception as e:
    st.error(f"🚨 에러 발생: {e}")
