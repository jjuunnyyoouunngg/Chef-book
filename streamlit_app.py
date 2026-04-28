import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import datetime
import time
import random

# 1. 페이지 설정
st.set_page_config(page_title="AI 쉐프의 레시피", page_icon="🍳", layout="wide")
st.markdown("""
    <style>
    div.stButton > button {
        border: 3px solid #333 !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        height: 3.5em !important;
        transition: 0.2s;
    }
    div.stButton > button:hover { border-color: #FF4B4B !important; color: #FF4B4B !important; background: #FFF5F5 !important; }
    .status-text { font-size: 1.2rem; font-weight: bold; color: #FF4B4B; margin: 0.5rem 0; }
    .timer-text { font-size: 0.9rem; color: #666; font-family: monospace; }
    .rotating-text { font-size: 1.1rem; color: #555; font-style: italic; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🍳 AI 쉐프의 레시피")

# 2. 실시간 정보 표시 구역 (타이머 & 랜덤 추천)
timer_placeholder = st.empty()
rotating_placeholder = st.empty()

# 3. 메뉴 데이터 정의 (카테고리 15개)
MENU_DATA = {
    "한식": ["김치찌개", "된장찌개", "미역국", "소고기무국", "콩나물국", "북어국", "순두부찌개", "청국장", "만둣국", "제육볶음", "소불고기", "닭볶음탕", "고등어조림", "갈치구이", "오징어볶음", "찜닭", "소시지야채볶음", "두부조림", "멸치볶음", "진미채무침", "감자조림", "콩나물무침", "시금치나물", "계란장조림", "애호박볶음", "오이무침", "비빔밥", "잡채", "계란말이", "김치전"],
    "중식": ["짜장면", "짬뽕", "탕수육", "마파두부", "볶음밥", "토마토달걀볶음", "고추잡채", "깐풍기", "유린기", "마라탕", "마라상궈", "꿔바로우", "깐쇼새우", "탄탄면"],
    "양식": ["치즈버거", "핫도그", "페퍼로니피자", "버팔로윙", "감자튀김", "어니언링", "맥앤치즈", "미트볼스파게티", "몬테크리스토", "비프스튜"],
    "일식": ["돈카츠", "가츠동", "규동", "사케동", "텐동", "초밥", "냉모밀", "라멘", "마제소바", "야끼소바", "오코노미야끼", "타코야끼", "스키야키"],
    "분식": ["떡볶이", "튀김", "김밥", "물어묵", "쫄면", "라면", "라볶이", "소떡소떡", "순대볶음", "잔치국수"],
    "아시아식": ["쌀국수", "분짜", "짜조", "월남쌈", "팟타이", "나시고랭", "푸팟퐁커리", "똠양꿍", "반미", "망고찰밥"],
    "유럽식": ["라자냐", "감바스", "에그인헬", "굴라쉬", "슈바인학센", "뇨끼", "리조또", "어니언스프", "라따뚜이", "스테이크"],
    "남미식": ["타코", "퀘사디아", "브리또", "나쵸", "과카몰리", "파히타", "세비체", "츄러스"],
    "채식": ["두부구이", "채소구이", "어향가지", "나물무침", "버섯솥밥", "후무스", "두부소면", "채소카레"],
    "건강식": ["닭가슴살구이", "연어스테이크", "전복죽", "양배추쌈", "곤약국수", "버섯전골", "톳밥"],
    "디저트/베이킹": ["케이크", "티라미수", "타르트", "휘낭시에", "스콘", "소금빵", "와플", "브라우니", "푸딩", "약과"],
    "안주": ["골뱅이무침", "닭발", "오돌뼈", "콘치즈", "조개탕", "먹태구이", "육회", "두부김치", "바지락술찜", "해물파전"],
    "음료": ["아메리카노", "카페라떼", "에이드", "스무디", "밀크티", "버블티", "진저에일", "식혜"],
    "주류": ["하이볼", "모히또", "칵테일", "막걸리", "상그리아", "소맥", "매실주"],
    "기타": "ETC_MODE"
}

# 모든 메뉴 리스트화 (랜덤 추천용)
all_dishes = []
for val in MENU_DATA.values():
    if isinstance(val, list): all_dishes.extend(val)

# 4. 실시간 업데이트 함수
def update_realtime_info():
    # 카운트다운 계산 (매일 오후 4시 KST 리셋 기준)
    now = datetime.datetime.now()
    target = now.replace(hour=16, minute=0, second=0, microsecond=0)
    if now > target: target += datetime.timedelta(days=1)
    diff = target - now
    
    # 시간 포맷팅
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    timer_str = f"🕒 다음 토큰 리셋까지: {hours:02d}시간 {minutes:02d}분 {seconds:02d}초 남음"
    
    # 랜덤 메뉴 선정
    random_dish = random.choice(all_dishes)
    rotating_str = f"💡 추천: \"{random_dish}\" 레시피를 알려줘"
    
    timer_placeholder.markdown(f'<p class="timer-text">{timer_str}</p>', unsafe_allow_html=True)
    rotating_placeholder.markdown(f'<p class="rotating-text">{rotating_str}</p>', unsafe_allow_html=True)

# 초기 1회 실행
update_realtime_info()

# 5. 모델 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    safety = { HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE, HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE, HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE, HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE }
    model = genai.GenerativeModel('gemini-2.0-flash', safety_settings=safety)
except Exception as e:
    st.error(f"연결 오류: {e}"); st.stop()

# 6. 세션 상태 관리
if "messages" not in st.session_state: st.session_state.messages = []
if "sel_cat" not in st.session_state: st.session_state.sel_cat = None
if "show_retry" not in st.session_state: st.session_state.show_retry = False
if "finished" not in st.session_state: st.session_state.finished = False

# 7. 이전 대화 기록 표시
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

st.write("---")
user_q = None

# 8. 흐름 제어 (예/아니오 및 카테고리 선택)
if st.session_state.finished:
    st.balloons()
    st.success("🌟 **미슐랭 3스타를 향해 나아갑시다!**")
    if st.button("처음으로 돌아가기"):
        st.session_state.finished = False; st.rerun()

elif st.session_state.show_retry:
    st.markdown('<p class="status-text">🤔 더 물어볼 메뉴가 있나요?</p>', unsafe_allow_html=True)
    c1, c2, _ = st.columns([1, 1, 8])
    if c1.button("✅ 예", use_container_width=True):
        st.session_state.show_retry = False; st.session_state.sel_cat = None; st.rerun()
    if c2.button("❌ 아니오", use_container_width=True):
        st.session_state.show_retry = False; st.session_state.finished = True; st.rerun()

else:
    st.markdown('<p class="status-text">🔍 요리 종류를 선택해 주세요!</p>', unsafe_allow_html=True)
    m_cols = st.columns(5)
    for i, cat in enumerate(MENU_DATA.keys()):
        if m_cols[i % 5].button(cat, use_container_width=True, key=f"cat_{cat}"):
            st.session_state.sel_cat = cat

    # 기타 모드
    if st.session_state.sel_cat == "기타":
        st.info("💡 **메뉴를 적어주세요.**")
        with st.form("etc_form"):
            etc_dish = st.text_input("음식 이름:")
            if st.form_submit_button("레시피 찾기") and etc_dish:
                user_q = f"메뉴({etc_dish}) 레시피 알려줘"; st.session_state.sel_cat = None

    # 카테고리 세부 메뉴
    elif st.session_state.sel_cat:
        st.info(f"✨ {st.session_state.sel_cat} 메뉴판")
        s_cols = st.columns(5)
        for i, dish in enumerate(MENU_DATA[st.session_state.sel_cat]):
            if s_cols[i % 5].button(dish, use_container_width=True, key=f"d_{dish}"):
                user_q = f"{dish} 레시피 알려줘"; st.session_state.sel_cat = None

    prompt = st.chat_input("메뉴를 입력하세요.")
    if prompt: user_q = prompt

    # AI 답변 생성
    if user_q:
        st.session_state.messages.append({"role": "user", "content": user_q})
        with st.chat_message("user"): st.markdown(user_q)
        
        sys_p = f"너는 AI 쉐프야. 사용자가 '{user_q}'를 물어봤어. '안녕하세요! AI 쉐프입니다. 👨‍🍳'로 시작하고 [재료], [순서], [팁]을 알려줘."
        try:
            resp = model.start_chat().send_message(sys_p, stream=True)
            with st.chat_message("assistant"):
                full_res = st.write_stream((c.text for c in resp if c.text))
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            st.session_state.show_retry = True; st.rerun()
        except Exception as e:
            if "429" in str(e): st.error("🚨 **하루 사용량을 다 쓰셨습니다!**")
            else: st.error(f"오류: {e}")
