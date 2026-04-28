import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI 쉐프의 레시피", page_icon="🍳", layout="wide")
st.markdown("<style>div.stButton>button{border:2.5px solid #333!important;border-radius:10px!important;font-weight:bold!important;height:3em!important;transition:all .2s;} div.stButton>button:hover{border-color:#FF4B4B!important;color:#FF4B4B!important;background:#FFF5F5!important;} .rec{font-size:1.2rem;font-weight:bold;color:#FF4B4B;margin:2rem 0 1rem;}</style>", unsafe_allow_html=True)
st.title("🍳 AI 쉐프의 레시피")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 💡 2.0이나 2.5 같은 제한 심한 최신 모델 대신, 
    # 가장 안정적이고 무료 할당량이 많은 1.5-flash로 강제 지정합니다.
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"API 에러: {e}")
    st.stop()

# 세션 상태 초기화
for k in ["messages", "selected_category"]:
    if k not in st.session_state:
        st.session_state[k] = [] if k == "messages" else None

# 대화 기록 표시
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

st.write("---")
if st.session_state.messages:
    st.markdown('<p class="rec">🔍 다른 메뉴들은 안 궁금하세요?</p>', unsafe_allow_html=True)
else:
    st.write("#### 🍱 요리 카테고리 선택")

cats = ["한식", "중식", "일식", "양식", "분식", "아시아식", "유럽식", "남미식", "채식", "건강식", "디저트/베이킹", "안주", "음료", "주류", "기타"]
cols = st.columns(5)
user_input = None

for i, c in enumerate(cats):
    if cols[i%5].button(c, use_container_width=True, key=f"m_{c}"):
        st.session_state.selected_category = c if c == "한식" else None
        user_input = "새로운 요리를 찾고 싶어요!" if c == "기타" else f"{c} 대표 레시피 하나 추천해 줘." if c != "한식" else None

if st.session_state.selected_category == "한식":
    st.info("🥇 **한식 베스트 셀러 30가지**")
    kr_30 = ["김치찌개", "된장찌개", "미역국", "소고기무국", "콩나물국", "북어국/황태국", "순두부찌개", "청국장", "만둣국/떡국", "제육볶음", "소불고기", "닭볶음탕", "고등어조림", "갈치구이/조림", "오징어볶음", "찜닭", "소시지야채볶음", "두부조림", "멸치볶음", "진미채무침", "감자조림", "콩나물무침", "시금치나물", "메추리알/계란장조림", "애호박볶음", "오이무침", "비빔밥", "잡채", "계란말이", "김치전/부추전"]
    scols = st.columns(5)
    for i, d in enumerate(kr_30):
        if scols[i%5].button(d, use_container_width=True, key=f"k_{d}"):
            user_input, st.session_state.selected_category = f"{d} 레시피 알려줘", None

chat_input = st.chat_input("궁금한 음식 입력 (예: 제육볶음)")
if chat_input:
    user_input, st.session_state.selected_category = chat_input, None

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    prompt = f"너는 AI 쉐프야. 사용자가 '{user_input}'를 물어봤어. '안녕하세요! 최고의 맛을 찾아드리는 AI 쉐프입니다. 👨‍🍳'로 시작하고, [필요한 재료], [조리 순서], [AI 쉐프의 꿀팁]으로 친절하게 번호 매겨서 알려줘."
    history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
    
    try:
        resp = model.start_chat(history=history).send_message(prompt, stream=True)
        with st.chat_message("assistant"):
            ans = st.write_stream((c.text for c in resp if c.text))
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
    except Exception as e:
        st.error(f"🚨 일시적인 과부하입니다. 1분만 기다려주세요! 에러내용: {e}")
