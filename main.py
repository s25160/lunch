import requests
import streamlit as st

st.set_page_config(page_title="실시간 환율 변환기", page_icon="\U0001f4b1")
st.title("\U0001f4b1 실시간 환율 변환기")

CURRENCIES = ["KRW", "USD", "JPY", "EUR", "CNY"]
base = st.selectbox("기준 통화", CURRENCIES, index=0)
target = st.selectbox("바꿀 통화", CURRENCIES, index=1)
amount = st.number_input("금액", min_value=0.0, value=1000.0, step=100.0)

API_KEY = st.secrets["EXCHANGE_KEY"]

@st.cache_data(ttl=3600, show_spinner="환율 정보를 불러오는 중입니다...")
def get_rate(base_currency):
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base_currency}"
    return requests.get(url, timeout=10).json()

try:
    data = get_rate(base)
    rate = data["conversion_rates"][target]
    converted = amount * rate
    st.metric(f"{amount:,.0f} {base} \u2192", f"{converted:,.2f} {target}")
    st.caption(f"1 {base} = {rate} {target}")
except Exception:
    st.error("환율 정보를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")
