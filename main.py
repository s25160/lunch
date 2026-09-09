import calendar
import datetime
import re
import requests
import streamlit as st

st.set_page_config(page_title="핑크빛 학교 급식 달력", page_icon="🌸", layout="wide")

# -----------------------------------------------------------------------------
# 🌸 Pink Theme Custom CSS Injection
# -----------------------------------------------------------------------------
pink_theme_css = """
<style>
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(135deg, #fff5f7 0%, #fdebed 100%);
        font-family: 'Pretendard', sans-serif;
    }
    
    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background-color: #fff0f3 !important;
        border-right: 1px solid #ffccd5;
    }
    
    /* 타이틀 및 헤더 핑크 톤 설정 */
    h1 {
        color: #d63384 !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 2px #ffc0cb;
    }
    h2, h3, h4 {
        color: #e64980 !important;
    }
    
    /* 급식 카드 (Streamlit Container) 핑크 디자인 */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border: 2px solid #ffccd5 !important;
        border-radius: 16px !important;
        box-shadow: 0px 4px 12px rgba(255, 182, 193, 0.25);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 16px rgba(255, 105, 180, 0.3);
        border-color: #ff85a1 !important;
    }

    /* TODAY 배지 핑크 디자인 */
    .today-badge {
        background-color: #ff6b8b;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
        box-shadow: 0 2px 5px rgba(255, 107, 139, 0.4);
    }

    /* 식단 분류 타이틀 (중식 / 석식 등) */
    .meal-title-lunch {
        color: #ff477e;
        font-weight: bold;
        font-size: 0.95rem;
    }
    .meal-title-dinner {
        color: #b5179e;
        font-weight: bold;
        font-size: 0.95rem;
    }
    .meal-title-other {
        color: #f72585;
        font-weight: bold;
        font-size: 0.95rem;
    }

    /* 칼로리 텍스트 스타일 */
    .cal-text {
        font-size: 0.8rem;
        color: #ff85a1;
        font-weight: 500;
    }

    /* 구분선 컬러 */
    hr {
        border-color: #ffccd5 !important;
    }

    /* 라디오 버튼 / 토글 / 입력을 핑크 Accent로 강조 */
    div[data-baseweb="radio"] div {
        color: #d63384 !important;
    }
</style>
"""
st.markdown(pink_theme_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 🌸 UI Header
# -----------------------------------------------------------------------------
st.title("🌸 우리 학교 핑크 급식 달력")
st.caption("선택한 월의 급식 메뉴를 달콤한 핑크 테마 달력으로 한눈에 확인해보세요 💕")

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
    """메뉴명 뒤의 알레르기 번호를 감지하여 한글 식재료명으로 치환합니다."""
    if not convert_to_text or not dish_text:
        return dish_text

    def convert_match(match):
        raw = match.group(0)
        nums = re.findall(r"\d+", raw)
        allergens = [ALLERGY_MAP[int(n)] for n in nums if int(n) in ALLERGY_MAP]
        if allergens:
            return f" <span style='color:#ff6584; font-size:0.8rem;'>[{', '.join(allergens)}]</span>"
        return raw

    pattern = r"\(?(\d+\.)+\)?"
    return re.sub(pattern, convert_match, dish_text)


# -----------------------------------------------------------------------------
# 🎀 Sidebar Settings
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ 학교 정보 설정")
office_code = st.sidebar.text_input(
    "시도교육청코드", value="T10", help="기본값: 제주특별자치도교육청(T10)"
)
school_code = st.sidebar.text_input(
    "표준학교코드", value="9290088", help="기본값: 제주중앙고등학교(9290088)"
)

st.sidebar.markdown("---")
st.sidebar.subheader("🍽️ 알레르기 표시 설정")
show_allergen_names = st.sidebar.toggle(
    "알레르기 식품명으로 변환",
    value=True,
    help="체크 시 숫자 대신 [난류, 대두] 형태로 변환하여 표시합니다.",
)

with st.sidebar.expander("📖 나이스 알레르기 번호 안내표"):
    table_md = "\n".join([f"- **{k}번**: {v}" for k, v in ALLERGY_MAP.items()])
    st.markdown(table_md)

# -----------------------------------------------------------------------------
# 🗓️ Controls & Filters
# -----------------------------------------------------------------------------
today = datetime.date.today()
col_y, col_m, col_filter = st.columns([1, 1, 2])
with col_y:
    year = st.selectbox(
        "연도 선택", options=list(range(today.year - 1, today.year + 2)), index=1
    )
with col_m:
    month = st.selectbox(
        "월 선택", options=list(range(1, 13)), index=today.month - 1
    )
with col_filter:
    meal_filter = st.radio(
        "급식 종류 선택",
        options=["전체 보기", "중식만 보기", "석식만 보기"],
        index=0,
        horizontal=True,
    )


def fetch_monthly_meals(key, ofcdc_code, schul_code, yr, mo):
    """선택한 월의 1일부터 말일까지의 급식을 조회합니다."""
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
    st.error("⚠️ Streamlit Secrets에 `NEIS_KEY`가 설정되어 있지 않습니다.")
    st.stop()

neis_key = st.secrets["NEIS_KEY"]

# -----------------------------------------------------------------------------
# 🌷 Meal Data Fetch & Display
# -----------------------------------------------------------------------------
try:
    with st.spinner(f"🌸 {year}년 {month}월 급식 정보를 불러오는 중..."):
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

    st.markdown("---")

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
                        # 날짜 헤더 & TODAY 배지
                        if is_today:
                            st.markdown(
                                f"**<span style='color:#d63384;'>{month}월 {day}일 ({weekdays_kr[i]})</span>** <span class='today-badge'>TODAY</span>",
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f"**<span style='color:#495057;'>{month}월 {day}일 ({weekdays_kr[i]})</span>**",
                                unsafe_allow_html=True,
                            )

                        st.divider()

                        if not day_meals:
                            st.caption("✨ 급식 없음 (휴업/방학)")
                        else:
                            displayed_count = 0

                            # 중식 표시
                            if (
                                meal_filter in ["전체 보기", "중식만 보기"]
                                and "중식" in day_meals
                            ):
                                displayed_count += 1
                                cal_text = (
                                    f" <span class='cal-text'>({day_meals['중식']['cal']})</span>"
                                    if day_meals["중식"]["cal"]
                                    else ""
                                )
                                st.markdown(
                                    f"<span class='meal-title-lunch'>🍱 중식</span>{cal_text}",
                                    unsafe_allow_html=True,
                                )
                                for dish in day_meals["중식"]["dishes"]:
                                    st.markdown(
                                        f"<span style='font-size:0.85rem; color:#4a4a4a;'>• {dish}</span>",
                                        unsafe_allow_html=True,
                                    )

                            # 석식 표시
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
                                    f" <span class='cal-text'>({day_meals['석식']['cal']})</span>"
                                    if day_meals["석식"]["cal"]
                                    else ""
                                )
                                st.markdown(
                                    f"<span class='meal-title-dinner'>🌙 석식</span>{cal_text}",
                                    unsafe_allow_html=True,
                                )
                                for dish in day_meals["석식"]["dishes"]:
                                    st.markdown(
                                        f"<span style='font-size:0.85rem; color:#4a4a4a;'>• {dish}</span>",
                                        unsafe_allow_html=True,
                                    )

                            # 기타 식단 (조식 등)
                            if meal_filter == "전체 보기":
                                for m_type, meal_data in day_meals.items():
                                    if m_type not in ["중식", "석식"]:
                                        displayed_count += 1
                                        cal_text = (
                                            f" <span class='cal-text'>({meal_data['cal']})</span>"
                                            if meal_data["cal"]
                                            else ""
                                        )
                                        st.markdown(
                                            f"<span class='meal-title-other'>🍴 {m_type}</span>{cal_text}",
                                            unsafe_allow_html=True,
                                        )
                                        for dish in meal_data["dishes"]:
                                            st.markdown(
                                                f"<span style='font-size:0.85rem; color:#4a4a4a;'>• {dish}</span>",
                                                unsafe_allow_html=True,
                                            )

                            if displayed_count == 0:
                                st.caption("해당 식단 없음")

        if has_school_day:
            st.write("")

except requests.exceptions.RequestException as e:
    st.error(
        f"⚠️ 나이스 API 통신 오류: 네트워크 상태를 확인해 주세요. ({e})"
    )
except Exception as e:
    st.error(f"⚠️ 화면 구성 중 오류가 발생했습니다: {e}")
