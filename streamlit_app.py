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
st.write("원하는 요리 종류를 선택하거나, 하단 채팅창에 궁금한 음식을 물어보세요!")

# API 세팅
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Streamlit Secrets에 API 키가 설정되지 않았습니다.")
    st.stop()

genai.configure(api_key=gemini_api_key)

# 💡 모델 1.5-flash 강제 고정 (하루 1500번 무료 제한)
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
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
# 🍱 Part 2: 상단/하단 메뉴판
# =====================================================================
st.write("---")
# 대화가 있을 때는 '다른 메뉴 추천', 처음에는 '요리 카테고리 선택' 문구 출력
if len(st.session_state.messages) > 0:
    st.markdown('<p class="recommend-text">🔍 다른 메뉴들은 안 궁금하세요?</p>', unsafe_allow_html=True)
else:
    st.write("#### 🍱 요리 카테고리 선택")

# 15개 메인 카테고리 (간편식 -> 안주 변경)
categories = [
    "한식", "중식", "일식", "양식", "분식",
    "아시아식", "유럽식", "남미식", "채식", "건강식",
    "디저트/베이킹", "안주", "음료", "주류", "기타"
]

cat_cols = st.columns(5)
user_input = None

for i, category in enumerate(categories):
    with cat_cols[i % 5]:
        if st.button(category, use_container_width=True, key=f"main_{category}"):
            if category == "한식":
                st.session_state.selected_category = "한식"
            elif category == "기타":
                st.session_state.selected_category = None
                user_input = "제가 가진 레시피 외에 새로운 요리를 찾고 싶어요! 어떤 음식을 도와드릴까요?"
            else:
                st.session_state.selected_category = None
                user_input = f"{category} 스타일의 인기 있는 요리 레시피 하나 추천해 줘."

# 💡 한식 버튼 클릭 시 30가지 메뉴 펼치기
if st.session_state.selected_category == "한식":
    st.info("🥇 **한식 베스트 셀러 30가지입니다.**")
    
    korean_30 = [
        "김치찌개", "된장찌개", "미역국",
