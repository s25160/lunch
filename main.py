import calendar
import datetime
import re
import requests
import streamlit as st

st.set_page_config(
    page_title="코스믹 갤럭틱 급식 달력 🌌",
    page_icon="🚀",
    layout="wide",
)

# -----------------------------------------------------------------------------
# 🌌 ULTRA COSMIC CYBERPUNK CUSTOM CSS
# -----------------------------------------------------------------------------
cosmic_css = """
<style>
    /* 1. 우주 배경 애니메이션 */
    @keyframes stars {
        0% { background-position: 0 0; }
        100% { background-position: 1000px 1000px; }
    }
    
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 15px rgba(255, 0, 128, 0.4), 0 0 30px rgba(0, 255, 255, 0.2); }
        50% { box-shadow: 0 0 25px rgba(255, 0, 128, 0.8), 0 0 50px rgba(0, 255, 255, 0.5); }
        100% { box-shadow: 0 0 15px rgba(255, 0, 128, 0.4), 0 0 30px rgba(0, 255, 255, 0.2); }
    }

    .stApp {
        background: radial-gradient(ellipse at bottom, #1b2735 0%, #090a0f 100%);
        color: #e0e6ed;
        font-family: 'Pretendard', sans-serif;
    }

    /* 2. 사이드바 (글래스모피즘 + 사이버네온) */
    [data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.75) !important;
        backdrop-filter: blur(12px);
        border-right: 2px solid #ff007f !important;
        box-shadow: 5px 0 25px rgba(255, 0, 127, 0.3);
    }

    /* 3. 화려한 우주 타이틀 (그라데이션 텍스트) */
    .cosmic-title {
        font-size: 2.8rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #ff007f, #7928ca, #00dfd8, #ff007f);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 6s ease infinite;
        margin-bottom: 5px;
        text-shadow: 0 0 20px rgba(255, 0, 127, 0.5);
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .cosmic-subtitle {
        text-align: center;
        color: #00f0ff;
        font-size: 1.1rem;
        letter-spacing: 2px;
        margin-bottom: 25px;
        text-shadow: 0 0 8px #00f0ff;
    }

    /* 4. 카드 컨테이너 (시공간 카드) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(20, 24, 45, 0.65) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
        border-radius: 20px !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-8px) scale(1.02);
        border-color: #ff007f !important;
        animation: pulseGlow 2s infinite;
    }

    /* 5. TODAY (현재 시공간) 배지 */
    .space-today-badge {
        background: linear-gradient(45deg, #ff007f, #7928ca);
        color: #ffffff;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: bold;
        letter-spacing: 1px;
        box-shadow: 0 0 10px #ff007f;
        display: inline-block;
    }

    /* 6. 에너지(칼로리) 배지 */
    .energy-badge {
        background: rgba(0, 240, 255, 0.15);
        border: 1px solid #00f0ff;
        color: #00f0ff;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 600;
        text-shadow: 0 0 5px #00f0ff;
    }

    /* 7. 식단 타이틀 텍스트 */
    .lunch-title {
        color: #ff007f;
        font-weight: 800;
        font-size: 1.05rem;
        text-shadow: 0 0 10px rgba(255, 0, 127, 0.6);
    }
    .dinner-title {
        color: #7928ca;
        font-weight: 800;
        font-size: 1.05rem;
        text-shadow: 0 0 10px rgba(121, 40, 202, 0.6);
    }

    /* 8. 메뉴 텍스트 */
    .dish-item {
        color: #e2e8f0;
        font-size: 0.85rem;
        line-height: 1.5;
    }

    /* 알레르기 네온 태그 */
    .allergy-tag {
        color: #ff007f;
        font-size: 0.75rem;
        font-weight: bold;
        text-shadow: 0 0 5px #ff007f;
    }

    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
</style>
"""
st.markdown(cosmic_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 🚀 HEADER
# -----------------------------------------------------------------------------
st.markdown(
    "<div class='cosmic-title'>🛸 GALACTIC MEAL SYSTEM</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='cosmic-subtitle'>✨ 은하계 최고의 맛! 우주적 급식 오디세이 ✨</div>",
    unsafe_allow_html=True,
)

ALLERGY_MAP = {
    1: "난류",
    2: "우유",
    3: "메밀",
    4: "땅콩",
    5: "대두",
    6: "밀",
    7: "고등어",
    8: "게",
    9: "새우",
    10: "돼지고기",
    11: "복숭아",
    12: "토마토",
    13: "아황산류",
    14: "호두",
    15: "닭고기",
    16: "쇠고기",
    17: "오징어",
    18: "조개류(굴/전복/홍합 포함)",
    19: "잣",
}


def replace_allergy_codes(dish_text, convert_to_text=True):
    if not convert_to_text or not dish_text:
        return dish_text

    def convert_match(match):
        raw = match.group(0)
        nums = re.findall(r"\d+", raw)
        allergens = [ALLERGY_MAP[int(n)] for n in nums if int(n) in ALLERGY_MAP]
        if allergens:
            return f" <span class='allergy-tag'>[{', '.join(allergens)}]</span>"
        return raw

    pattern = r"\(?(\d+\.)+\)?"
    return re.sub(pattern, convert_match, dish_text)


# -----------------------------------------------------------------------------
# 🛸 SIDEBAR (기지 제어반)
# -----------------------------------------------------------------------------
st.sidebar.markdown("### 🛰️ 행성 기지 좌표 설정")
office_code = st.sidebar.text_input(
    "시도교육청코드", value="T10", help="기본값: 제주특별자치도교육청(T10)"
)
school_code = st.sidebar.text_input(
    "표준학교코드", value="9290088", help="기본값: 제주중앙고등학교(9290088)"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧪 항원 스캐너 (알레르기)")
show_allergen_names = st.sidebar.toggle(
    "알레르기 물질 감지 레이더",
    value=True,
    help="체크 시 숫자 코드 대신 우주 식재료명으로 자동 치환합니다.",
)

with st.sidebar.expander("📖 코스믹 알레르기 식별표"):
    table_md = "\n".join([f"- **{k}번**: {v}" for k, v in ALLERGY_MAP.items()])
    st.markdown(table_md)

# -----------------------------------------------------------------------------
# 🧭 CONTROLS
# -----------------------------------------------------------------------------
today = datetime.date.today()
col_y, col_m, col_filter = st.columns([1, 1, 2])
with col_y:
    year = st.selectbox(
        "시공간 연도", options=list(range(today.year - 1, today.year + 2)), index=1
    )
with col_m:
    month = st.selectbox(
        "궤도 월", options=list(range(1, 13)), index=today.month - 1
    )
with col_filter:
    meal_filter = st.radio(
        "에너지 보충 타임",
        options=["전체 보기", "중식만 보기", "석식만 보기"],
        index=0,
        horizontal=True,
    )


def fetch_monthly_meals(key, ofcdc_code, schul_code, yr, mo):
    _, last_day = calendar.monthrange(yr, mo)
    from_ymd = f"{yr}{mo:02d}01"
    to_ymd = f"{yr}{mo:02d}{last_day:02d}"

    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        "KEY": key,
        "Type": "json",
        "pIndex": 1,
        "pSize": 100,
        "ATPT_OFCDC_SC_CODE": ofcdc_code,
        "SD_SCHUL_CODE": schul_code,
        "MLSV_FROM_YMD": from_ymd,
        "MLSV_TO_YMD": to_ymd,
    }
    response = requests.get(url, params=params, timeout=7)
    return response.json()


if "NEIS_KEY" not in st.secrets:
    st.error("🚨 [경고] NEIS_KEY 보안 파동 실패: Secrets를 확인하세요.")
    st.stop()

neis_key = st.secrets["NEIS_KEY"]

# -----------------------------------------------------------------------------
# 🌠 MAIN DISPLAY
# -----------------------------------------------------------------------------
try:
    with st.spinner("🌌 우주 데이터베이스에서 급식 데이터 워프 중..."):
        res_data = fetch_monthly_meals(
            neis_key, office_code, school_code, year, month
        )

    meal_dict = {}
    if "mealServiceDietInfo" in res_data:
        rows = res_data["mealServiceDietInfo"][1]["row"]
        for row in rows:
            ymd = row.get("MLSV_YMD")
            meal_type = row.get("MMEAL_SC_NM", "급식")
            dish = row.get("DDISH_NM", "")
            cal_info = row.get("CAL_INFO", "").strip()

            formatted_dish = replace_allergy_codes(
                dish, convert_to_text=show_allergen_names
            )
            dish_lines = [
                d.strip()
                for d in formatted_dish.replace("<br/>", "\n").split("\n")
                if d.strip()
            ]

            meal_dict.setdefault(ymd, {})[meal_type] = {
                "dishes": dish_lines,
                "cal": cal_info,
            }

    month_cal = calendar.monthcalendar(year, month)
    weekdays_kr = ["월", "화", "수", "목", "금"]

    st.markdown("<br>", unsafe_allow_html=True)

    for week in month_cal:
        cols = st.columns(5)
        has_school_day = False

        for i in range(5):
            day = week[i]
            with cols[i]:
                if day == 0:
                    st.empty()
                else:
                    has_school_day = True
                    ymd_str = f"{year}{month:02d}{day:02d}"
                    day_meals = meal_dict.get(ymd_str, {})
                    is_today = (
                        year == today.year
                        and month == today.month
                        and day == today.day
                    )

                    with st.container(border=True):
                        # Header
                        if is_today:
                            st.markdown(
                                f"**<span style='color:#00f0ff; font-size:1.1rem;'>{month}.{day} ({weekdays_kr[i]})</span>** <span class='space-today-badge'>PRESENT</span>",
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f"**<span style='color:#a0aec0; font-size:1rem;'>{month}.{day} ({weekdays_kr[i]})</span>**",
                                unsafe_allow_html=True,
                            )

                        st.divider()

                        if not day_meals:
                            st.caption("🌑 데이터 없음 (블랙홀/휴무)")
                        else:
                            displayed_count = 0

                            # 중식
                            if (
                                meal_filter in ["전체 보기", "중식만 보기"]
                                and "중식" in day_meals
                            ):
                                displayed_count += 1
                                cal_text = (
                                    f" <span class='energy-badge'>⚡ {day_meals['중식']['cal']}</span>"
                                    if day_meals["중식"]["cal"]
                                    else ""
                                )
                                st.markdown(
                                    f"<span class='lunch-title'>🛸 중식</span> {cal_text}",
                                    unsafe_allow_html=True,
                                )
                                for dish in day_meals["중식"]["dishes"]:
                                    st.markdown(
                                        f"<div class='dish-item'>✨ {dish}</div>",
                                        unsafe_allow_html=True,
                                    )

                            # 석식
                            if (
                                meal_filter in ["전체 보기", "석식만 보기"]
                                and "석식" in day_meals
                            ):
                                displayed_count += 1
                                if (
                                    meal_filter == "전체 보기"
                                    and "중식" in day_meals
                                ):
                                    st.write("")
                                cal_text = (
                                    f" <span class='energy-badge'>⚡ {day_meals['석식']['cal']}</span>"
                                    if day_meals["석식"]["cal"]
                                    else ""
                                )
                                st.markdown(
                                    f"<span class='dinner-title'>🌙 석식</span> {cal_text}",
                                    unsafe_allow_html=True,
                                )
                                for dish in day_meals["석식"]["dishes"]:
                                    st.markdown(
                                        f"<div class='dish-item'>🪐 {dish}</div>",
                                        unsafe_allow_html=True,
                                    )

                            if displayed_count == 0:
                                st.caption("해당 식단 없음")

        if has_school_day:
            st.write("")

except requests.exceptions.RequestException as e:
    st.error(f"📡 서킷 연결 오류: 우주 통신망 차단됨 ({e})")
except Exception as e:
    st.error(f"💥 시공간 왜곡 발생: {e}")
