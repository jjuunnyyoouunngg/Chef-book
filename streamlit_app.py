import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="AI 쉐프의 레시피", page_icon="🍳", layout="wide")

# 💡 CSS: 버튼 테두리 강조 및 가독성 향상
st.markdown("""
    <style>
    div.stButton > button {
        border: 2.5px solid #333333 !important; 
        border-radius: 10px !important;
        font-weight: bold !important;
        height: 3em !important;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        border: 2.5px solid #FF4B4B !important;
        color: #FF4B4B !important;
        background-color: #FFF5F5 !important;
    }
    /* 안내 문구 스타일 */
    .recommend-text {
        font-size: 1.2rem;
        font-weight: bold;
        color: #FF4B4B;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍳 AI 쉐프의 레시피")

# API 및 모델 세팅
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Streamlit Secrets에 API 키가 설정되지 않았습니다.")
    st.stop()

genai.configure(api_key=gemini_api_key)

try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in available_models if "flash" in m), available_models[0])
    model = genai.GenerativeModel(target_model)
except Exception as e:
    st.error(f"API 연결 에러: {e}")
    st.stop()

# 대화 기록 및 화면 상태 저장
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None 

# =====================================================================
# 💬 Part 1: 대화 기록 표시
# =====================================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =====================================================================
# 🍱 Part 2: 하단 추천 메뉴판 (다른 메뉴들은 안 궁금하세요?)
# =====================================================================
st.write("---")
st.markdown('<p class="recommend-text">🔍 다른 메뉴들은 안 궁금하세요?</p>', unsafe_allow_html=True)

# 15개 메인 카테고리 (동남아식 -> 아시아식 변경)
categories = [
    "한식", "중식", "일식", "양식", "분식",
    "아시아식", "유럽식", "남미식", "채식", "건강식",
    "디저트/베이킹", "간편식", "음료", "주류", "기타"
]

cat_cols = st.columns(5)
user_input = None

for i, category in enumerate(categories):
    with cat_cols[i % 5]:
        if st.button(category, use_container_width=True, key=f"main_{category}"):
            if category == "한식":
                st.session_state.selected_category = "한식"
            else:
                st.session_state.selected_category = None
                user_input = f"{category} 스타일의 인기 있는 요리 레시피 하나 추천해 줘."

# 💡 한식 버튼 클릭 시 30가지 메뉴 펼치기
if st.session_state.selected_category == "한식":
    st.info("🥇 **한식 베스트 셀러 30가지입니다.**")
    
    korean_30 = [
        "김치찌개", "된장찌개", "미역국", "소고기무국", "콩나물국", 
        "북어국/황태국", "순두부찌개", "청국장", "만둣국/떡국", "제육볶음", 
        "소불고기", "닭볶음탕", "고등어조림", "갈치구이/조림", "오징어볶음", 
        "찜닭", "소시지야채볶음", "두부조림", "멸치볶음", "진미채무침", 
        "감자조림", "콩나물무침", "시금치나물", "메추리알/계란장조림", "애호박볶음", 
        "오이무침", "비빔밥", "잡채", "계란말이", "김치전/부추전"
    ]
    
    sub_cols = st.columns(5)
    for i, dish in enumerate(korean_30):
        with sub_cols[i % 5]:
            if st.button(dish, use_container_width=True, key=f"sub_{dish}"):
                user_input = f"{dish} 레시피를 알려줘"
                st.session_state.selected_category = None

# 채팅창 직접 입력
chat_input = st.chat_input("또는 궁금한 음식 이름을 직접 입력하세요!")
if chat_input:
    user_input = chat_input
    st.session_state.selected_category = None

# =====================================================================
# 🚀 Part 3: 답변 생성 및 화면 갱신
# =====================================================================
if user_input:
    # 1. 사용자 메시지 추가 및 화면 표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 2. 셰프 페르소나 설정 (매우 상세하고 친절한 답변 유도)
    chef_prompt = f"""너는 세계 최고의 요리 실력을 가진 'AI 쉐프'야. 
    사용자가 '{user_input}'의 레시피를 물어봤어. 
    다음 규칙에 맞춰 답변해줘:
    1. 인사는 "안녕하세요! 최고의 맛을 찾아드리는 AI 쉐프입니다. 👨‍🍳"로 시작해.
    2. 해당 요리에 대한 짧은 유래나 매력 포인트로 서론을 열어줘.
    3. [필요한 재료], [조리 순서], [AI 쉐프의 꿀팁]으로 구분해서 아주 상세하게 알려줘.
    4. 조리 순서는 번호를 매겨서 설명해줘.
    5. 답변의 톤은 매우 친절하고 따뜻하게 유지해줘."""

    history = []
    for m in st.session_state.messages[:-1]:
        role = "user" if m["role"] == "user" else "model"
        history.append({"role": role, "parts": [m["content"]]})

    try:
        chat = model.start_chat(history=history)
        response_stream = chat.send_message(chef_prompt, stream=True)

        # 스트리밍 답변을 기록에 저장하기 위해 빈 메시지 추가
        with st.chat_message("assistant"):
            def stream_generator():
                for chunk in response_stream:
                    if chunk.text: yield chunk.text
            response = st.write_stream(stream_generator())
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun() # 대화 종료 후 화면을 갱신하여 메뉴판이 다시 아래에 오도록 함
        
    except Exception as e:
        st.error(f"🚨 에러 발생: {e}")
