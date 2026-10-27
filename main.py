import requests
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Air Safe | 항공 기상 안전",
    page_icon="✈️",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

.stApp {
    background: linear-gradient(135deg, #071426, #102b49, #163c5b);
    color: #f4f8ff;
    font-family: 'Noto Sans KR', sans-serif;
}
.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1, h2, h3, p, label {
    color: #f4f8ff !important;
}
.hero {
    background: linear-gradient(120deg, #163e65, #087eaa);
    padding: 30px;
    border-radius: 22px;
    border: 1px solid #397ba7;
    margin-bottom: 24px;
}
.hero h1 {
    font-size: 36px;
    font-weight: 900;
    margin-bottom: 8px;
}
.hero p {
    color: #d4eaff !important;
    margin-bottom: 0;
}
.info-card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(180,220,255,0.2);
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 12px;
}
.status-card {
    background: #102b42;
    border-left: 5px solid #32c7a5;
    padding: 18px;
    border-radius: 12px;
    margin: 12px 0;
}
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    padding: 18px;
    border-radius: 16px;
}
div[data-testid="stMetricLabel"] {
    color: #b9d8f5 !important;
}
div[data-testid="stMetricValue"] {
    color: #ffffff !important;
}
.stButton > button {
    background: linear-gradient(90deg, #00a8cc, #0878d1);
    color: white;
    border: none;
    border-radius: 12px;
    min-height: 48px;
    font-weight: 700;
    width: 100%;
}
.stButton > button:hover {
    background: #168fc1;
    color: white;
    border: 1px solid #8de4ff;
}
div[data-baseweb="select"] > div {
    background-color: #173653;
    color: white;
    border-radius: 10px;
}
div[data-testid="stAlert"] {
    border-radius: 12px;
}
.footer {
    color: #a8c4dc;
    font-size: 12px;
    text-align: center;
    padding-top: 24px;
}
</style>
""", unsafe_allow_html=True)

AIRPORTS = {
    "인천국제공항": (37.4602, 126.4407),
    "김포국제공항": (37.5583, 126.7906),
    "제주국제공항": (33.5113, 126.4930),
    "김해국제공항": (35.1795, 128.9382),
}

WEATHER_NAMES = {
    0: "맑음",
    1: "대체로 맑음",
    2: "구름 조금",
    3: "흐림",
    45: "안개",
    48: "짙은 안개 가능",
    51: "약한 이슬비",
    53: "이슬비",
    55: "강한 이슬비",
    56: "어는 이슬비",
    57: "강한 어는 이슬비",
    61: "약한 비",
    63: "비",
    65: "강한 비",
    66: "어는 비",
    67: "강한 어는 비",
    71: "약한 눈",
    73: "눈",
    75: "강한 눈",
    77: "싸락눈",
    80: "약한 소나기",
    81: "소나기",
    82: "강한 소나기",
    85: "약한 눈 소나기",
    86: "강한 눈 소나기",
    95: "뇌우",
    96: "우박 가능 뇌우",
    99: "강한 우박 가능 뇌우",
}

DANGEROUS_CODES = {45, 48, 56, 57, 66, 67, 75, 82, 86, 95, 96, 99}

st.markdown("""
<div class="hero">
    <h1>✈️ AIR SAFE</h1>
    <p>항공 기상 안전 확인 시스템</p>
    <p>공항별 날씨 정보를 확인하고 항공 안전에 영향을 줄 수 있는 기상 조건을 살펴보세요.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🛫 공항 선택")

airport = st.selectbox(
    "날씨를 확인할 공항을 선택하세요.",
    list(AIRPORTS.keys())
)

if st.button("🌤️ 현재 날씨 확인하기"):
    lat, lon = AIRPORTS[airport]

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "precipitation,rain,showers,snowfall,"
            "weather_code,wind_speed_10m,wind_gusts_10m,"
            "visibility"
        ),
        "timezone": "Asia/Seoul",
        "forecast_days": 1
    }

    try:
        with st.spinner("날씨 정보를 가져오는 중입니다..."):
            response = requests.get(
                url, params=params, timeout=20
            )
            response.raise_for_status()
            current = response.json()["current"]

        temp = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")
        precipitation = current.get("precipitation")
        rain = current.get("rain")
        snowfall = current.get("snowfall")
        wind = current.get("wind_speed_10m")
        gust = current.get("wind_gusts_10m")
        visibility = current.get("visibility")
        code = current.get("weather_code")
        weather = WEATHER_NAMES.get(code, "기타 기상 상태")

        st.markdown("---")
        st.markdown(f"## 📍 {airport}")
        st.caption(
            f"자료 기준 시각: {current.get('time', '정보 없음')} "
            "| 풍속 단위: km/h"
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🌡️ 기온", f"{temp} °C" if temp is not None else "정보 없음")
        c2.metric("💨 풍속", f"{wind} km/h" if wind is not None else "정보 없음")
        c3.metric("🌬️ 돌풍", f"{gust} km/h" if gust is not None else "정보 없음")
        c4.metric("💧 습도", f"{humidity}%" if humidity is not None else "정보 없음")

        c5, c6, c7 = st.columns(3)
        c5.metric(
            "🌧️ 강수량",
            f"{precipitation} mm" if precipitation is not None else "정보 없음"
        )
        c6.metric(
            "👁️ 가시거리",
            f"{visibility / 1000:.1f} km" if visibility is not None else "정보 없음"
        )
        c7.metric(
            "❄️ 적설량",
            f"{snowfall} cm" if snowfall is not None else "정보 없음"
        )

        st.markdown(f"""
        <div class="info-card">
            <h3>🌦️ 현재 기상 상태</h3>
            <h2>{weather}</h2>
            <p>기온, 바람, 강수량과 가시거리를 함께 확인하세요.</p>
        </div>
        """, unsafe_allow_html=True)

        warnings = []

        if wind is not None and wind >= 30:
            warnings.append("풍속이 강합니다. 공식 항공기상 자료를 확인하세요.")

        if gust is not None and gust >= 50:
            warnings.append("돌풍이 강할 수 있습니다. 추가 확인이 필요합니다.")

        if precipitation is not None and precipitation > 0:
            warnings.append("강수가 관측됩니다. 시정과 활주로 상태를 확인해야 합니다.")

        if visibility is not None and visibility < 5000:
            warnings.append("가시거리가 짧습니다. 공식 시정 정보를 확인하세요.")

        if code in DANGEROUS_CODES:
            warnings.append("주의가 필요한 기상 현상이 표시되었습니다.")

        if snowfall is not None and snowfall > 0:
            warnings.append("눈이 관측됩니다. 활주로 결빙 및 제설 상태 확인이 필요합니다.")

        st.markdown("### ⚠️ 기상 주의 안내")

        if warnings:
            for item in warnings:
                st.warning(item)
        else:
            st.success(
                "설정한 주의 조건은 감지되지 않았습니다. "
                "이 결과가 안전한 운항을 보장하지는 않습니다."
            )

        st.markdown("### 🔧 항공정비 관점에서 확인할 사항")
        st.markdown("""
        <div class="info-card">
            <p>• 강풍: 지상 작업 및 항공기 고정 상태에 주의합니다.</p>
            <p>• 비와 눈: 활주로 상태, 수분 유입 및 결빙 가능성을 확인합니다.</p>
            <p>• 낮은 가시거리: 지상 이동과 작업 시 주변 안전에 유의합니다.</p>
            <p>• 뇌우: 공항의 공식 안전 지침과 작업 제한을 확인합니다.</p>
        </div>
        """, unsafe_allow_html=True)

        st.caption(
            "이 프로그램은 일반 기상 예보를 이용한 교육용 참고 도구입니다. "
            "실제 항공기 운항 여부나 정비 작업 가능 여부는 "
            "공식 항공기상 자료와 관련 규정에 따라 판단해야 합니다."
        )

    except requests.exceptions.Timeout:
        st.error("날씨 서버 응답 시간이 초과되었습니다. 잠시 후 다시 시도하세요.")
    except requests.exceptions.RequestException:
        st.error("날씨 정보를 가져오지 못했습니다. 인터넷 연결을 확인하세요.")
    except (KeyError, TypeError, ValueError):
        st.error("날씨 데이터 형식이 예상과 다릅니다. 잠시 후 다시 시도하세요.")
    except Exception:
        st.error("예상하지 못한 오류가 발생했습니다. 다시 시도하세요.")

st.markdown("---")
st.markdown("### 📘 프로그램 소개")

st.markdown("""
<div class="info-card">
    <p><b>프로젝트명:</b> 에어 세이프(Air Safe)</p>
    <p><b>목적:</b> 공항별 기상 정보를 쉽게 확인하고 항공 안전과 관련된 기상 조건을 이해합니다.</p>
    <p><b>사용 기술:</b> Python, Streamlit, Open-Meteo API</p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="footer">AIR SAFE · 항공 기상 안전 확인 프로그램 · 교육용</div>',
    unsafe_allow_html=True
)
