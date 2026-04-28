import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="AI 쉐프의 레시피", page_icon="🍳", layout="wide")

# 💡 마법의 CSS: 모든 버튼의 테두리를 굵고 진하게 만듭니다.
st.markdown("""
    <style>
    div.stButton > button {
        border: 2.5px solid #555555 !important; /* 테두리 굵기와 색상 */
        border-radius: 8px !important;        /* 모서리 둥글기 */
        font-weight: bold !important;         /* 글씨 굵게 */
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        border: 2.5px solid #FF4B4B !important; /* 마우스를 올렸을 때 색상 변화 */
        color: #FF4B4B !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍳 AI 쉐프의 레시피")
st.write("원하는 요리 종류를 선택하거나, 하단 채팅창에 궁금한 음식을 물어보세요!")

# API 및 모델 세팅
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Streamlit Secrets에 API 키가 설정되지 않았습니다.")
    st.stop()

genai.configure(api_key=gemini_api_key)

try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in available_models if "1.5-flash" in m), available_models[0])
    model = genai.GenerativeModel(target_model)
except Exception as e:
    st.error(f"API 연결 에러: {e}")
    st.stop()

# 대화 기록 및 화면 상태 저장
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None 

# 이전 대화 띄우기
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.write("---")
st.write("#### 🍱 요리 카테고리 선택")

# 15개 메인 카테고리 버튼 배치
categories = [
    "한식", "중식", "일식", "양식", "분식",
    "아시아식", "유럽식", "남미식", "채식", "건강식",
    "디저트/베이킹", "안", "음료", "주류", "기타"
]
cols = st.columns(5)
user_input = None

for i, category in enumerate(categories):
    with cols[i % 5]:
        if st.button(category, use_container_width=True):
            if category == "한식":
                st.session_state.selected_category = "한식"
            elif category == "기타":
                st.session_state.selected_category = None
                user_input = "제가 가진 레시피 외에 새로운 요리를 찾고 싶어요! 어떤 음식을 도와드릴까요?"
            else:
                st.session_state.selected_category = None
                user_input = f"{category} 카테고리에서 가장 인기 있는 대표 레시피 3가지만 추천해 줘!"

# =====================================================================
# 💡 한식 세부 메뉴 출력 로직 (설명, 소제목 다 빼고 요리 이름만!)
# =====================================================================
if st.session_state.selected_category == "한식":
    st.success("🥇 **한식 베스트 셀러 30가지입니다.** 드시고 싶은 메뉴를 선택해 주세요!")

    # 깔끔하게 요리 이름만 모아둔 리스트
    KOREAN_MENU_LIST = [
        "김치찌개", "된장찌개", "미역국", "소고기무국", "콩나물국", 
        "북어국/황태국", "순두부찌개", "청국장", "만둣국/떡국", "제육볶음", 
        "소불고기", "닭볶음탕", "고등어조림", "갈치구이/조림", "오징어볶음", 
        "찜닭", "소시지야채볶음", "두부조림", "멸치볶음", "진미채무침", 
        "감자조림", "콩나물무침", "시금치나물", "메추리알/계란장조림", "애호박볶음", 
        "오이무침", "비빔밥", "잡채", "계란말이", "김치전/부추전"
    ]

    # 보기 좋게 5칸으로 나누어서 출력
    sub_cols = st.columns(5)
    for i, dish in enumerate(KOREAN_MENU_LIST):
        with sub_cols[i % 5]:
            if st.button(dish, key=f"kr_{dish}", use_container_width=True):
                user_input = f"{dish} 레시피를 알려줘"
                st.session_state.selected_category = None # 메뉴판 닫기
# =====================================================================

# 채팅창 직접 입력 처리
chat_input = st.chat_input("궁금한 음식 이름을 입력하세요 (예: 제육볶음 레시피)")
if chat_input:
    user_input = chat_input
    st.session_state.selected_category = None

# 답변 생성 로직
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 셰프 페르소나 적용
    chef_prompt = f"너는 친절하고 전문적인 'AI 쉐프'야. 사용자가 '{user_input}'에 대해 물어봤어. 맛있는 레시피를 필요한 재료와 단계별 조리 순서로 보기 좋게 정리해서 알려줘."

    history = []
    for m in st.session_state.messages[:-1]:
        role = "user" if m["role"] == "user" else "model"
        history.append({"role": role, "parts": [m["content"]]})

    try:
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
