import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI 쉐프의 레시피", page_icon="🍳", layout="wide")
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
    target_model = next((m for m in available_models if "flash" in m), available_models[0])
    model = genai.GenerativeModel(target_model)
except Exception as e:
    st.error(f"API 연결 에러: {e}")
    st.stop()

# 대화 기록 및 화면 상태(어떤 버튼을 눌렀는지) 저장
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None  # 초기에는 아무 카테고리도 열리지 않은 상태

# 이전 대화 띄우기
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.write("---")
st.write("#### 🍱 요리 카테고리 선택")

# 15개 메인 카테고리 버튼 배치 (5칸씩 3줄로 깔끔하게)
categories = [
    "한식", "중식", "일식", "양식", "분식",
    "아시아식", "유럽식", "남미식", "채식", "건강식",
    "디저트/베이킹", "간편식", "음료", "주류", "기타"
]
cols = st.columns(5)
user_input = None

for i, category in enumerate(categories):
    with cols[i % 5]:
        if st.button(category, use_container_width=True):
            if category == "한식":
                # 한식 버튼을 누르면 세부 메뉴를 열어줌
                st.session_state.selected_category = "한식"
            elif category == "기타":
                st.session_state.selected_category = None # 세부 메뉴 닫기
                user_input = "제가 가진 레시피 외에 새로운 요리를 찾고 싶어요! 어떤 음식을 도와드릴까요?"
            else:
                st.session_state.selected_category = None # 세부 메뉴 닫기
                user_input = f"{category} 카테고리에서 가장 인기 있는 대표 레시피 3가지만 추천해 줘!"

# =====================================================================
# 💡 한식 세부 메뉴 출력 로직 (한식 버튼을 눌렀을 때만 나타남!)
# =====================================================================
if st.session_state.selected_category == "한식":
    st.success("🥇 **한식 베스트 셀러 30가지입니다.** 드시고 싶은 메뉴를 선택해 주세요!")

    KOREAN_MENU = {
        "🍲 국/찌개": [
            ("김치찌개", "참치, 돼지고기, 꽁치 등"), ("된장찌개", "차돌, 우렁, 바지락 등"), ("미역국", "소고기, 황태, 홍합 등"),
            ("소고기무국", "맑고 시원한 맛"), ("콩나물국", "해장과 아이들 국물용"), ("북어국/황태국", "담백하고 고소한 국"),
            ("순두부찌개", "칼칼한 밥도둑"), ("청국장", "구수한 고향의 맛"), ("만둣국/떡국", "간편한 한 그릇 국물")
        ],
        "🥩 메인 반찬": [
            ("제육볶음", "남편들이 가장 좋아하는 메뉴"), ("소불고기", "남녀노소 호불호 없는 메뉴"), ("닭볶음탕", "푸짐한 저녁 메인 요리"),
            ("고등어조림", "무와 함께 푹 익힌 밥도둑"), ("갈치구이/조림", "짭조름한 생선 반찬"), ("오징어볶음", "매콤 달콤한 양념"),
            ("찜닭", "단짠단짠의 정석"), ("소시지야채볶음", "아이들 최애 도시락 반찬"), ("두부조림", "가성비 최고의 밑반찬")
        ],
        "🥗 밑반찬": [
            ("멸치볶음", "바삭하거나 촉촉하게"), ("진미채무침", "매콤하고 쫄깃한 밑반찬"), ("감자조림", "포슬포슬한 식감"),
            ("콩나물무침", "하얗게 혹은 빨갛게"), ("시금치나물", "기본 나물의 정석"), ("메추리알/계란장조림", "아이들 필수 반찬"),
            ("애호박볶음", "새우젓으로 맛을 낸 깔끔한 맛"), ("오이무침", "아삭하고 상큼한 즉석 반찬")
        ],
        "🍚 일품 요리 & 별미": [
            ("비빔밥", "냉장고 남은 나물 처리용"), ("잡채", "생일이나 명절 필수 메뉴"), 
            ("계란말이", "만만하지만 정성이 들어가는 반찬"), ("김치전/부추전", "비 오는 날 생각나는 별미")
        ]
    }

    # 각 그룹별로 세부 버튼 생성
    for section, items in KOREAN_MENU.items():
        st.markdown(f"##### {section}")
        sub_cols = st.columns(3) # 3칸으로 나누어 배치
        for i, (dish, desc) in enumerate(items):
            with sub_cols[i % 3]:
                # 메뉴 이름과 설명을 합쳐서 버튼으로 만듦
                if st.button(f"{dish}\n({desc})", key=f"kr_{dish}", use_container_width=True):
                    # 이 버튼을 누르면 AI에게 보낼 질문이 자동으로 완성됨!
                    user_input = f"{dish} 레시피를 알려줘"
                    st.session_state.selected_category = None # 질문을 던진 후에는 세부 메뉴판을 깔끔하게 닫음
# =====================================================================

# 채팅창 직접 입력 처리
chat_input = st.chat_input("궁금한 음식 이름을 입력하세요 (예: 제육볶음 레시피)")
if chat_input:
    user_input = chat_input
    st.session_state.selected_category = None # 채팅을 직접 치면 메뉴판 닫기

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
