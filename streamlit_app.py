import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# 1. 페이지 설정
st.set_page_config(page_title="AI 쉐프의 레시피", page_icon="🍳", layout="wide")

# CSS: 버튼 및 디자인 강조
st.markdown("""
    <style>
    div.stButton > button {
        border: 3px solid #333 !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        height: 3.5em !important;
        transition: 0.2s;
    }
    div.stButton > button:hover {
        border-color: #FF4B4B !important;
        color: #FF4B4B !important;
        background-color: #FFF5F5 !important;
    }
    .michelin-text {
        font-size: 2rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        padding: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍳 AI 쉐프의 레시피")

# 2. 세션 상태 관리
if "messages" not in st.session_state: st.session_state.messages = []
if "sel_cat" not in st.session_state: st.session_state.sel_cat = None
if "show_retry" not in st.session_state: st.session_state.show_retry = False
if "finished_msg" not in st.session_state: st.session_state.finished_msg = False

# 3. 모델 리스트 (Fallback 시스템)
MODELS_TO_TRY = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-pro', 'gemini-pro']

def get_ai_response(prompt_text):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    safety = { HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE, HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE, HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE, HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE }
    for model_name in MODELS_TO_TRY:
        try:
            model = genai.GenerativeModel(model_name=model_name, safety_settings=safety)
            history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages]
            chat = model.start_chat(history=history)
            return chat.send_message(prompt_text, stream=True)
        except: continue
    return None

# 4. 📖 일식 수동 레시피 데이터 (API 미사용)
MANUAL_RECIPES = {
    "등심돈카츠": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n돼지고기 등심 150g, 밀가루 3큰술, 계란 1개, 빵가루 1컵, 소금/후추 약간, 식용유 500ml\n\n[조리 순서]\n1. 등심을 칼등으로 두드려 연육한 뒤 소금, 후추로 밑간합니다.\n2. 밀가루 -> 계란물 -> 빵가루 순으로 옷을 입힙니다.\n3. 170도 기름에서 앞뒤로 3~4분간 노릇하게 튀깁니다.\n4. 2분간 레스팅 후 썹니다.\n\n[AI 쉐프의 꿀팁]\n빵가루에 물을 살짝 뿌려 촉촉하게 사용하면 훨씬 바삭해집니다!",
    "안심돈카츠": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n돼지고기 안심 150g, 밀가루, 계란, 빵가루, 소금, 후추\n\n[조리 순서]\n1. 안심을 두툼한 원통형으로 썰어 밑간합니다.\n2. 튀김옷을 입혀 165도 낮은 온도에서 6~7분간 은근히 튀깁니다.\n3. 단면이 핑크빛일 때 건져 잔열로 익힙니다.\n\n[AI 쉐프의 꿀팁]\n안심은 오버쿡되면 질겨지니 온도를 꼭 지켜주세요!",
    "가츠동": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n돈카츠 1장, 밥 1공기, 계란 1개, 양파 1/4개, 쯔유 소스\n\n[조리 순서]\n1. 쯔유 소스와 양파를 넣고 끓입니다.\n2. 돈카츠를 썰어 소스 위에 올립니다.\n3. 푼 계란을 두르고 반숙으로 익힙니다.\n4. 밥 위에 얹어 마무리합니다.",
    "규동": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n소불고기용 100g, 양파 1/2개, 밥 1공기, 간장, 설탕, 생강\n\n[조리 순서]\n1. 간장 소스를 끓이다 양파를 넣습니다.\n2. 소고기를 한 점씩 넣어 빠르게 익힙니다.\n3. 밥 위에 고기와 국물을 넉넉히 올립니다.",
    "사케동": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n생연어 150g, 밥 1공기, 배합초, 와사비\n\n[조리 순서]\n1. 밥에 배합초를 섞어 식힙니다.\n2. 연어를 0.5cm 두께로 슬라이스합니다.\n3. 밥 위에 연어를 꽃처럼 담고 와사비를 곁들입니다.",
    "텐동": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n새우, 단호박, 채소튀김, 튀김가루, 타레소스\n\n[조리 순서]\n1. 찬물로 반죽하여 바삭하게 튀김을 튀깁니다.\n2. 밥 위에 타레소스를 뿌립니다.\n3. 튀김을 세워서 담아냅니다.",
    "에비동": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n새우튀김 3개, 양파, 계란, 쯔유소스\n\n[조리 순서]\n1. 쯔유 소스에 양파를 넣고 끓입니다.\n2. 새우튀김을 넣고 계란물을 두릅니다.\n3. 밥 위에 조심스럽게 얹습니다.",
    "우나기동": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n장어 1/2마리, 데리야끼 소스, 생강채\n\n[조리 순서]\n1. 장어에 소스를 발라가며 약불에 굽습니다.\n2. 2cm 크기로 자릅니다.\n3. 밥 위에 장어를 올리고 생강채를 곁들입니다.",
    "모둠초밥": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n횟감 10점, 배합초 밥, 와사비\n\n[조리 순서]\n1. 밥을 한입 크기로 쥡니다.\n2. 와사비를 살짝 바릅니다.\n3. 횟감을 올려 가볍게 누릅니다.",
    "유부초밥": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n유부피, 조미액 밥\n\n[조리 순서]\n1. 밥에 조미액을 섞습니다.\n2. 유부 입을 벌려 밥을 채웁니다.\n3. 모양을 평평하게 다듬습니다.",
    "후토마키": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n김, 연어, 계란, 오이, 단무지\n\n[조리 순서]\n1. 김 위에 밥을 펴고 재료를 푸짐하게 쌓습니다.\n2. 힘을 주어 크게 맙니다.\n3. 칼에 기름을 묻혀 썹니다.",
    "냉모밀": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n메밀면, 쯔유 육수, 간 무, 와사비\n\n[조리 순서]\n1. 메밀면을 삶아 찬물에 헹굽니다.\n2. 살얼음 낀 육수를 준비합니다.\n3. 무즙과 와사비를 고명으로 올립니다.",
    "판모밀": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n메밀면, 쯔유 소스, 간 무, 쪽파\n\n[조리 순서]\n1. 면을 판 위에 사리지어 올립니다.\n2. 진한 쯔유 소스를 따로 준비합니다.\n3. 소스에 면을 적셔 먹습니다.",
    "고기우동": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n우동면, 소고기 50g, 우동 장국\n\n[조리 순서]\n1. 고기를 먼저 볶습니다.\n2. 장국에 면을 넣어 끓입니다.\n3. 볶은 고기를 듬뿍 올립니다.",
    "미역우동": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n우동면, 자른 미역, 쯔유\n\n[조리 순서]\n1. 미역을 불려 쯔유와 함께 끓입니다.\n2. 우동면을 넣고 한소끔 끓여 담백하게 냅니다.",
    "돈코츠라멘": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n생면, 돈골 육수, 차슈, 숙주\n\n[조리 순서]\n1. 육수를 끓이고 면은 따로 삶습니다.\n2. 그릇에 면을 담고 육수를 붓습니다.\n3. 차슈와 숙주를 올립니다.",
    "소유라멘": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n생면, 닭육수, 간장 소스\n\n[조리 순서]\n1. 맑은 육수에 간장으로 간을 합니다.\n2. 삶은 면을 넣고 차슈, 멘마를 올립니다.",
    "미소라멘": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n생면, 사골 육수, 미소 된장\n\n[조리 순서]\n1. 육수에 미소를 곱게 풉니다.\n2. 면과 옥수수콘, 버터 한 조각을 올립니다.",
    "마제소바": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n굵은 면, 다진 돼지고기, 노른자, 부추\n\n[조리 순서]\n1. 고기를 양념에 볶아 민찌를 만듭니다.\n2. 면 위에 부추, 김, 고기, 노른자를 올립니다.",
    "야끼소바": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n중화면, 대패삼겹살, 양배추, 소스\n\n[조리 순서]\n1. 고기와 채소를 볶다 면을 넣습니다.\n2. 전용 소스를 붓고 센 불에 볶습니다.",
    "오코노미야끼": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n양배추, 베이컨, 반죽물, 가쓰오부시\n\n[조리 순서]\n1. 양배추 반죽을 팬에 두툼하게 굽습니다.\n2. 소스와 마요네즈, 가쓰오부시를 뿌립니다.",
    "타코야끼": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n타코야끼 가루, 문어 조각, 텐카스\n\n[조리 순서]\n1. 팬에 반죽을 붓고 문어를 넣습니다.\n2. 꼬챙이로 돌려가며 동그랗게 익힙니다.",
    "가라아게": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n닭다리살, 밑간양념, 전분가루\n\n[조리 순서]\n1. 닭고기를 밑간에 재운 뒤 전분을 묻힙니다.\n2. 두 번 튀겨 바삭함을 살립니다.",
    "감자고로케": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n감자 2개, 다진 양파, 빵가루\n\n[조리 순서]\n1. 으깬 감자와 볶은 양파를 섞어 빚습니다.\n2. 튀김옷을 입혀 노릇하게 튀깁니다.",
    "에비후라이": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n새우 4마리, 빵가루, 타르타르 소스\n\n[조리 순서]\n1. 새우를 늘려 튀김옷을 입힙니다.\n2. 175도에서 바삭하게 튀겨 소스를 곁들입니다.",
    "소고기샤브샤브": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n샤브 고기, 배추, 버섯, 가쓰오 육수\n\n[조리 순서]\n1. 육수를 끓여 채소를 먼저 넣습니다.\n2. 고기를 살짝 데쳐 소스에 찍어 먹습니다.",
    "스키야키": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n소고기, 대파, 두부, 노른자, 간장소스\n\n[조리 순서]\n1. 팬에 고기와 대파를 굽다 소스를 붓습니다.\n2. 노른자에 찍어 고소하게 즐깁니다.",
    "밀푀유나베": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n배추, 깻잎, 소고기, 육수\n\n[조리 순서]\n1. 배추-깻잎-고기 순으로 쌓아 자릅니다.\n2. 냄비에 꽉 채워 담고 육수를 끓입니다.",
    "자완무시": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n계란 2개, 다시마 육수, 쯔유\n\n[조리 순서]\n1. 계란물을 체에 걸러 약불에 은근히 찝니다.\n2. 푸딩 같은 식감이 되면 완성입니다.",
    "명란계란말이": "안녕하세요! AI 쉐프입니다. 👨‍🍳\n\n[필요한 재료]\n계란 3개, 명란젓 1줄, 파\n\n[조리 순서]\n1. 계란물에 명란을 통째로 넣어 맙니다.\n2. 노릇하게 익혀 짭조름하게 즐깁니다."
}

# 5. 이전 대화 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# 6. 인터랙션 영역
if st.session_state.finished_msg:
    st.markdown('<div class="michelin-text">🌟 미슐랭 3스타를 향해 나아갑시다!</div>', unsafe_allow_html=True)
    if st.button("처음으로 돌아가기"):
        st.session_state.finished_msg = False
        st.session_state.show_retry = False
        st.rerun()

elif st.session_state.show_retry:
    st.write("#### 🤔 더 물어볼 메뉴가 있나요?")
    c1, c2, _ = st.columns([1, 1, 8])
    if c1.button("✅ 예", use_container_width=True):
        st.session_state.show_retry = False; st.session_state.sel_cat = None; st.rerun()
    if c2.button("❌ 아니오", use_container_width=True):
        st.session_state.finished_msg = True; st.rerun()

else:
    # 메뉴 선택 UI
    m_cols = st.columns(5)
    categories = list(MENU_DATA.keys())
    for i, cat in enumerate(categories):
        if m_cols[i % 5].button(cat, use_container_width=True): st.session_state.sel_cat = cat

    # 기타 모드
    if st.session_state.sel_cat == "기타":
        with st.form("etc_form"):
            etc_dish = st.text_input("궁금한 음식 이름을 입력하세요:")
            if st.form_submit_button("레시피 찾기") and etc_dish:
                user_input_recipe = etc_dish
                # 7. 실행 로직 (기타 메뉴는 AI 실행)
                st.session_state.messages.append({"role": "user", "content": f"메뉴({user_input_recipe}) 레시피 알려줘"})
                with st.chat_message("user"): st.markdown(user_input_recipe)
                with st.chat_message("assistant"):
                    placeholder = st.empty()
                    full_res = ""
                    chef_prompt = f"너는 AI 쉐프야. 사용자가 '{user_input_recipe}'를 요청했어. 상세 레시피를 [필요한 재료], [조리 순서], [AI 쉐프의 꿀팁]으로 정리해줘."
                    stream = get_ai_response(chef_prompt)
                    if stream:
                        for chunk in stream:
                            if chunk.text:
                                full_res += chunk.text
                                placeholder.markdown(full_res)
                        st.session_state.messages.append({"role": "assistant", "content": full_res})
                        st.session_state.show_retry = True; st.rerun()
                    else:
                        st.error("🚨 사용량을 초과했습니다.")

    # 일반 카테고리
    elif st.session_state.sel_cat:
        st.info(f"✨ **{st.session_state.sel_cat}** 메뉴판입니다.")
        s_cols = st.columns(5)
        for i, dish in enumerate(MENU_DATA[st.session_state.sel_cat]):
            if s_cols[i % 5].button(dish, use_container_width=True):
                # 💡 핵심 로직: 수동 레시피에 있으면 즉시 출력, 없으면 AI 실행
                st.session_state.messages.append({"role": "user", "content": f"{dish} 레시피 알려줘"})
                if dish in MANUAL_RECIPES:
                    res = MANUAL_RECIPES[dish]
                    st.session_state.messages.append({"role": "assistant", "content": res})
                    st.session_state.show_retry = True; st.rerun()
                else:
                    # AI 호출 (한식 등 다른 카테고리 대비용)
                    with st.chat_message("assistant"):
                        placeholder = st.empty()
                        full_res = ""
                        stream = get_ai_response(f"{dish} 레시피 상세히 알려줘")
                        if stream:
                            for chunk in stream:
                                if chunk.text:
                                    full_res += chunk.text
                                    placeholder.markdown(full_res)
                            st.session_state.messages.append({"role": "assistant", "content": full_res})
                            st.session_state.show_retry = True; st.rerun()
