import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

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
    .status-text { font-size: 1.2rem; font-weight: bold; color: #FF4B4B; margin: 1.5rem 0; }
    </style>
""", unsafe_allow_html=True)

st.title("🍳 AI 쉐프의 레시피")

# 2. 모델 설정 (Gemini 2.0 Flash)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    safety = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    model = genai.GenerativeModel('gemini-2.0-flash', safety_settings=safety)
except Exception as e:
    st.error(f"서버 연결 설정 중 오류: {e}"); st.stop()

# 3. 세션 상태 관리
if "messages" not in st.session_state: st.session_state.messages = []
if "sel_cat" not in st.session_state: st.session_state.sel_cat = None
if "show_retry" not in st.session_state: st.session_state.show_retry = False
if "finished" not in st.session_state: st.session_state.finished = False

# 4. 이전 대화 기록 표시
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# 5. 메뉴 데이터 (15개 카테고리)
MENU_DATA = {
    "한식": ["김치찌개", "된장찌개", "미역국", "소고기무국", "콩나물국", "북어국/황태국", "순두부찌개", "청국장", "만둣국/떡국", "제육볶음", "소불고기", "닭볶음탕", "고등어조림", "갈치구이/조림", "오징어볶음", "찜닭", "소시지야채볶음", "두부조림", "멸치볶음", "진미채무침", "감자조림", "콩나물무침", "시금치나물", "메추리알/계란장조림", "애호박볶음", "오이무침", "비빔밥", "잡채", "계란말이", "김치전/부추전"],
    "중식": ["짜장면", "짜장밥", "짬뽕", "짬뽕탕", "탕수육", "마파두부", "볶음밥", "계란볶음밥", "토마토달걀볶음", "고추잡채", "꽃빵튀김", "깐풍기", "유린기", "양장피", "팔보채", "누룽지탕", "군만두", "찐만두", "물만두", "난자완스", "건두부무침", "마라탕", "마라상궈", "꿔바로우", "깐쇼새우", "울면", "기스면", "잡탕밥", "잡채밥", "탄탄면"],
    "양식": ["치즈버거", "베이컨버거", "치킨버거", "불고기버거", "필리치즈스테이크", "핫도그", "코니도그", "페퍼로니피자", "하와이안피자", "미트러버피자", "버팔로윙", "케이준치킨", "치킨텐더", "팝콘치킨", "감자튀김", "웨지감자", "어니언링", "치즈스틱", "코울슬로", "콘샐러드", "맥앤치즈", "미트볼스파게티", "베이컨치즈프라이", "칠리프라이", "몬테크리스토", "칠리콘카르네", "풀드포크샌드위치", "코브샐러드", "비프스튜", "클램차우더"],
    "일식": ["등심돈카츠", "안심돈카츠", "가츠동", "규동", "사케동", "텐동", "에비동", "우나기동", "모둠초밥", "유부초밥", "후토마키", "냉모밀", "판모밀", "고기우동", "돈코츠라멘", "소유라멘", "미소라멘", "마제소바", "야끼소바", "오코노미야끼", "타코야끼", "가라아게", "감자고로케", "에비후라이", "소고기샤브샤브", "스키야키", "밀푀유나베", "자완무시", "명란계란말이", "미역우동"],
    "분식": ["고추장떡볶이", "로제떡볶이", "짜장떡볶이", "기름떡볶이", "김말이튀김", "오징어튀김", "고구마튀김", "야채튀김", "튀김만두", "야채김밥", "참치김밥", "치즈김밥", "멸치김밥", "매운어묵김밥", "꼬마김밥", "물어묵", "매운어묵", "쫄면", "비빔만두", "냄비라면", "떡만둣국", "라볶이", "소떡소떡", "순대볶음", "피카츄돈까스", "컵떡볶이", "계란토스트", "비빔국수", "잔치국수", "김치볶음밥"],
    "아시아식": ["소고기쌀국수", "매운쌀국수", "닭고기쌀국수", "분짜", "짜조", "월남쌈", "팟타이", "나시고랭", "미고랭", "카오팟", "푸팟퐁커리", "꿍팟퐁커리", "똠양꿍", "쏨땀", "공심채볶음", "파인애플볶음밥", "반미", "칠리크랩", "시리얼새우", "닭고기사테", "락사", "바쿠테", "껌승", "분보싸오", "분보훼", "망고찰밥", "고이꾸온", "그린커리", "레드커리", "탄탄면"],
    "유럽식": ["마르게리따피자", "루꼴라피자", "고르곤졸라피자", "까르보나라", "알리오올리오", "봉골레", "아마트리치아나", "라자냐", "감바스알아히요", "해산물빠에야", "에그인헬", "굴라쉬", "치즈퐁듀", "슈바인학센", "프렌치토스트", "크로크무슈", "감자뇨끼", "버섯리조또", "시저샐러드", "양송이스프", "어니언스프", "에스카르고", "브루스케타", "비프타르타르", "피쉬앤칩스", "미트볼파스타", "쉬림프박스", "라따뚜이", "티본스테이크", "비프부르기뇽"],
    "남미식": ["비프타코", "치킨타코", "쉬림프타코", "비프퀘사디아", "비프브리또", "치킨브리또", "치폴레보울", "나쵸살사", "과카몰리", "스테이크파히타", "엔칠라다", "치미창가", "광어세비체", "엠파나다", "슈라스코", "페이조아다", "옥수수타말레스", "치킨타키토스", "아레파", "피카디요", "로모살타도", "소염통꼬치", "쿠바샌드위치", "수제츄러스", "유카튀김", "또띠아칩", "할라피뇨튀김", "살사베르데", "칼도데폴로", "아로즈콘포요"],
    "채식": ["들기름두부구이", "두부조림", "마라두부", "모둠채소구이", "만가닥버섯구이", "어향가지볶음", "애호박볶음", "콩나물무침", "시금치나물", "미역줄기볶음", "새싹비빔밥", "곤드레솥밥", "표고버섯솥밥", "병아리콩샐러드", "단호박찜", "찐감자", "구운고구마", "토마토마리네이드", "렌틸콩스프", "채소튀김", "수제후무스", "무생채", "상추겉절이", "도토리묵무침", "오이파프리카스틱", "감자죽", "단호박죽", "야채수제비", "두부소면", "채소카레"],
    "건강식": ["현미밥", "오곡밥", "보리비빔밥", "닭가슴살구이", "훈제오리야채볶음", "연어스테이크", "고등어구이", "삼치구이", "전복죽", "소고기미역국", "황태북어국", "차돌박이청국장", "우렁된장찌개", "수제요거트보울", "하루견과", "오트밀죽", "파프리카베이컨말이", "구운계란", "돼지고기수육", "양배추쌈", "두부면파스타", "곤약국수", "데친브로콜리", "닭가슴살샐러드", "콩자반", "멸치볶음", "청포묵무침", "가지선", "버섯전골", "톳밥"],
    "디저트/베이킹": ["딸기케이크", "초코케이크", "치즈케이크", "티라미수", "타르트", "휘낭시에", "마들렌", "까눌레", "스콘", "크루아상", "소금빵", "단팥빵", "슈크림", "소보로빵", "베이글", "꽈배기", "호떡", "와플", "팬케이크", "브라우니", "쿠키", "머핀", "푸딩", "빙수", "약과"],
    "안주": ["골뱅이무침", "수박화채", "닭발", "오돌뼈", "똥집구이", "콘치즈", "조개탕", "홍합탕", "번데기탕", "어묵탕", "먹태구이", "육회", "낙지탕탕이", "두부김치", "계란말이", "바지락술찜", "숙주볶음", "훈제오리", "치즈플래터", "연어카나페", "닭꼬치", "염통꼬치", "타코와사비", "명란구이", "해물파전"],
    "음료": ["아메리카노", "라떼", "바닐라라떼", "카푸치노", "마끼아또", "카페모카", "콜드브루", "아인슈페너", "녹차라떼", "밀크티", "버블티", "딸기스무디", "망고스무디", "레모네이드", "자몽에이드", "진저에일", "아이스티", "딸기우유", "초코우유", "두유", "주스", "보리차", "유자차"],
    "주류": ["자몽하이볼", "레몬하이볼", "모히또", "피나콜라다", "상그리아", "뱅쇼", "막걸리", "소주", "맥주", "진토닉", "잭콕", "와인", "칵테일", "매실주", "복분자하이볼"],
    "기타": "ETC_MODE"
}

# 6. 사용자 인터랙션 로직
st.write("---")
user_q = None

# '아니오'를 눌렀을 때의 문구 표시
if st.session_state.finished:
    st.balloons()
    st.success("🌟 **미슐랭 3스타를 향해 나아갑시다!**")
    if st.button("처음으로 돌아가기"):
        st.session_state.finished = False
        st.rerun()

# '예/아니오' 질문창
elif st.session_state.show_retry:
    st.markdown('<p class="status-text">🤔 더 물어볼 메뉴가 있나요?</p>', unsafe_allow_html=True)
    c1, c2, _ = st.columns([1, 1, 8])
    if c1.button("✅ 예", use_container_width=True):
        st.session_state.show_retry = False
        st.session_state.sel_cat = None # 카테고리 선택 초기화
        st.rerun()
    if c2.button("❌ 아니오", use_container_width=True):
        st.session_state.show_retry = False
        st.session_state.finished = True # 종료 상태 활성화
        st.rerun()

# 메뉴 선택창 (카테고리 15개 버튼)
else:
    st.markdown('<p class="status-text">🔍 어떤 종류의 음식을 찾으시나요?</p>', unsafe_allow_html=True)
    m_cols = st.columns(5)
    for i, cat in enumerate(MENU_DATA.keys()):
        if m_cols[i % 5].button(cat, use_container_width=True, key=f"cat_{cat}"):
            st.session_state.sel_cat = cat

    # '기타' 모드 로직
    if st.session_state.sel_cat == "기타":
        st.write("---")
        st.info("💡 **메뉴를 적어주세요.**")
        with st.form("etc_input_form", clear_on_submit=True):
            etc_dish = st.text_input("궁금한 음식 이름을 입력하세요:")
            submit = st.form_submit_button("레시피 찾기")
            if submit and etc_dish:
                user_q = f"메뉴({etc_dish}) 레시피 알려줘"
                st.session_state.sel_cat = None

    # 세부 메뉴 버튼들
    elif st.session_state.sel_cat:
        st.info(f"✨ **{st.session_state.sel_cat}** 메뉴판")
        s_cols = st.columns(5)
        for i, dish in enumerate(MENU_DATA[st.session_state.sel_cat]):
            if s_cols[i % 5].button(dish, use_container_width=True, key=f"dish_{dish}"):
                user_q = f"{dish} 레시피 알려줘"
                st.session_state.sel_cat = None

    # 하단 통합 검색창
    prompt = st.chat_input("또는 음식 이름을 직접 입력하세요.")
    if prompt: user_q = prompt

    # 7. AI 답변 생성
    if user_q:
        st.session_state.messages.append({"role": "user", "content": user_q})
        with st.chat_message("user"): st.markdown(user_q)
        
        sys_p = f"너는 AI 쉐프야. 사용자가 '{user_q}'를 물어봤어. '안녕하세요! 최고의 맛을 찾아드리는 AI 쉐프입니다. 👨‍🍳'로 시작하고, [필요한 재료], [조리 순서], [AI 쉐프의 꿀팁]으로 정리해줘."
        hist = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
        
        try:
            resp = model.start_chat(history=hist).send_message(sys_p, stream=True)
            with st.chat_message("assistant"):
                full_res = ""
                placeholder = st.empty()
                for chunk in resp:
                    try:
                        if chunk.parts:
                            full_res += chunk.text
                            placeholder.markdown(full_res)
                    except: continue
                if not full_res:
                    full_res = "죄송합니다. 다른 메뉴를 물어봐 주세요!"
                    placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            st.session_state.show_retry = True; st.rerun()
        except Exception as e:
            if "429" in str(e):
                st.error("🚨 **하루 사용량을 다 쓰셨습니다!** 내일 다시 방문해 주세요.")
            else:
                st.error(f"🚨 오류가 발생했습니다: {e}")
