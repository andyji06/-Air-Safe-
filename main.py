
import requests
import pandas as pd
import pycountry
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(
    page_title="Air Safe | 세계 공항 기상",
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
    max-width: 1450px;
    padding-top: 2rem;
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
}
.hero p {
    color: #d4eaff !important;
}
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    padding: 16px;
    border-radius: 15px;
}
div[data-testid="stMetricLabel"] {
    color: #b9d8f5 !important;
}
div[data-testid="stMetricValue"] {
    color: white !important;
}
.stButton > button {
    background: linear-gradient(90deg, #00a8cc, #0878d1);
    color: white;
    border: none;
    border-radius: 12px;
    min-height: 45px;
    font-weight: 700;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #355775;
    border-radius: 12px;
}
.info-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(180,220,255,0.2);
    padding: 18px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>✈️ AIR SAFE</h1>
    <p>WORLD AIRPORT WEATHER SYSTEM</p>
    <p>국가를 선택하면 해당 국가의 공항 목록과 기상 정보를 조회합니다.</p>
</div>
""", unsafe_allow_html=True)

AIRPORTS_URL = (
    "https://raw.githubusercontent.com/"
    "davidmegginson/ourairports-data/main/airports.csv"
)

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

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
    85: "눈 소나기",
    86: "강한 눈 소나기",
    95: "뇌우",
    96: "우박 가능 뇌우",
    99: "강한 뇌우",
}


@st.cache_data(ttl=86400)
def load_airports():
    response = requests.get(AIRPORTS_URL, timeout=60)
    response.raise_for_status()

    df = pd.read_csv(response.url if False else AIRPORTS_URL)

    required = [
        "name", "type", "latitude_deg",
        "longitude_deg", "iso_country",
        "municipality", "ident"
    ]

    df = df[required].copy()

    df = df[
        df["type"].isin([
            "large_airport",
            "medium_airport",
            "small_airport"
        ])
    ]

    df = df.dropna(
        subset=["latitude_deg", "longitude_deg", "iso_country"]
    )

    df["latitude_deg"] = pd.to_numeric(
        df["latitude_deg"], errors="coerce"
    )
    df["longitude_deg"] = pd.to_numeric(
        df["longitude_deg"], errors="coerce"
    )

    df = df.dropna(
        subset=["latitude_deg", "longitude_deg"]
    )

    df["country_name"] = df["iso_country"].apply(
        country_name
    )

    return df


def country_name(code):
    try:
        country = pycountry.countries.get(alpha_2=code)
        return country.name if country else code
    except Exception:
        return code


@st.cache_data(ttl=600)
def get_weather_batch(airport_rows):
    if not airport_rows:
        return []

    latitudes = ",".join(
        str(row["latitude_deg"]) for row in airport_rows
    )
    longitudes = ",".join(
        str(row["longitude_deg"]) for row in airport_rows
    )

    params = {
        "latitude": latitudes,
        "longitude": longitudes,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "precipitation,weather_code,"
            "wind_speed_10m,wind_gusts_10m,visibility"
        ),
        "timezone": "UTC"
    }

    response = requests.get(
        WEATHER_URL,
        params=params,
        timeout=45
    )
    response.raise_for_status()

    data = response.json()

    # 여러 위치를 요청하면 결과가 목록으로 반환될 수 있음
    if isinstance(data, dict):
        data = [data]

    results = []

    for row, item in zip(airport_rows, data):
        current = item.get("current", {})
        code = current.get("weather_code")

        wind = current.get("wind_speed_10m")
        gust = current.get("wind_gusts_10m")
        rain = current.get("precipitation")
        visibility = current.get("visibility")

        warnings = []

        if wind is not None and wind >= 30:
            warnings.append("강풍 주의")

        if gust is not None and gust >= 50:
            warnings.append("돌풍 주의")

        if rain is not None and rain > 0:
            warnings.append("강수 확인")

        if visibility is not None and visibility < 5000:
            warnings.append("가시거리 주의")

        if code in [45, 48]:
            warnings.append("안개")

        if code in [95, 96, 99]:
            warnings.append("뇌우")

        results.append({
            "국가": row["country_name"],
            "공항명": row["name"],
            "도시": row["municipality"],
            "공항 코드": row["ident"],
            "공항 종류": {
                "large_airport": "대형",
                "medium_airport": "중형",
                "small_airport": "소형"
            }.get(row["type"], row["type"]),
            "기온(°C)": current.get("temperature_2m"),
            "날씨": WEATHER_NAMES.get(code, "정보 없음"),
            "풍속(km/h)": wind,
            "돌풍(km/h)": gust,
            "강수량(mm)": rain,
            "가시거리(km)": (
                round(visibility / 1000, 1)
                if visibility is not None else None
            ),
            "기상 안내": ", ".join(warnings) if warnings else "설정된 주의 조건 없음",
            "위도": row["latitude_deg"],
            "경도": row["longitude_deg"],
            "주의 조건 감지": bool(warnings)
        })

    return results


# 공항 데이터 불러오기
try:
    with st.spinner("세계 공항 데이터베이스를 불러오는 중입니다..."):
        airports_df = load_airports()

except Exception as e:
    st.error(
        "공항 데이터를 불러오지 못했습니다. "
        "인터넷 연결을 확인한 뒤 다시 실행해 주세요."
    )
    st.stop()


# 국가 선택
st.markdown("## 🌍 국가 선택")

countries = sorted(
    airports_df["country_name"].dropna().unique().tolist()
)

default_country = (
    countries.index("South Korea")
    if "South Korea" in countries
    else 0
)

selected_country = st.selectbox(
    "날씨를 확인할 국가를 선택하세요.",
    countries,
    index=default_country
)

country_df = airports_df[
    airports_df["country_name"] == selected_country
].copy()

country_df = country_df.sort_values(
    ["type", "name"]
).reset_index(drop=True)

st.markdown("### 🛫 조회 범위")

type_options = {
    "대형 공항": "large_airport",
    "중형 공항": "medium_airport",
    "소형 공항": "small_airport"
}

selected_types = st.multiselect(
    "조회할 공항 종류",
    list(type_options.keys()),
    default=list(type_options.keys())
)

if selected_types:
    allowed_types = [
        type_options[name] for name in selected_types
    ]
    country_df = country_df[
        country_df["type"].isin(allowed_types)
    ]

total_airports = len(country_df)

st.info(
    f"**{selected_country}**에서 데이터베이스로 확인된 "
    f"대상 공항은 **{total_airports:,}개**입니다. "
    "공항 정보의 누락이나 변경이 있을 수 있습니다."
)

# 대량 요청으로 인한 API 제한을 줄이기 위해
# 조회할 공항 수를 사용자가 직접 설정
if total_airports > 0:
    max_limit = min(total_airports, 2000)

    airport_limit = st.slider(
        "날씨를 조회할 공항 수",
        min_value=1,
        max_value=max_limit,
        value=min(total_airports, 300),
        step=1
    )
else:
    airport_limit = 0
    st.warning("선택한 조건에 해당하는 공항이 없습니다.")

st.caption(
    "공항이 많은 국가에서는 조회 시간이 길어질 수 있습니다. "
    "API 사용량 제한을 고려하여 한 번에 최대 2,000개까지 조회합니다."
)

if st.button("🌦️ 선택한 국가의 공항 날씨 조회", type="primary"):
    if country_df.empty:
        st.warning("조회할 공항이 없습니다.")
        st.stop()

    target_df = country_df.head(airport_limit).copy()
    airport_rows = target_df.to_dict("records")

    batches = [
        airport_rows[i:i + 50]
        for i in range(0, len(airport_rows), 50)
    ]

    all_results = []
    progress = st.progress(0)
    status = st.empty()
    errors = 0

    # 동시에 요청 수를 제한해 서버 부담을 줄임
    def fetch_batch(batch):
        return get_weather_batch(tuple(
            tuple(sorted(row.items())) for row in batch
        ))

    # 캐시 함수 입력 형식을 딕셔너리 목록으로 복구
    def fetch_weather(batch):
        return get_weather_batch(tuple(
            {
                "name": row["name"],
                "type": row["type"],
                "latitude_deg": row["latitude_deg"],
                "longitude_deg": row["longitude_deg"],
                "iso_country": row["iso_country"],
                "municipality": row.get("municipality"),
                "ident": row["ident"],
                "country_name": row["country_name"]
            }
            for row in batch
        ))

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_map = {
            executor.submit(
                fetch_weather, batch
            ): index
            for index, batch in enumerate(batches)
        }

        completed = 0

        for future in as_completed(future_map):
            try:
                all_results.extend(future.result())
            except Exception:
                errors += 1

            completed += 1
            progress.progress(completed / len(batches))
            status.write(
                f"날씨 조회 중: {completed}/{len(batches)} 묶음 완료"
            )

    status.empty()
    progress.empty()

    if all_results:
        result_df = pd.DataFrame(all_results)

        # 주의 조건이 있는 공항을 먼저 표시
        result_df = result_df.sort_values(
            "주의 조건 감지",
            ascending=False
        )

        st.session_state["weather_results"] = result_df
        st.session_state["weather_country"] = selected_country

        st.success(
            f"날씨 조회 완료: {len(result_df):,}개 공항"
        )

        if errors:
            st.warning(
                f"{errors}개 묶음은 조회에 실패했습니다. "
                "일시적인 API 오류일 수 있습니다."
            )
    else:
        st.error(
            "날씨 정보를 가져오지 못했습니다. "
            "잠시 후 다시 시도하거나 조회할 공항 수를 줄여 주세요."
        )


# 조회 결과 표시
if "weather_results" in st.session_state:
    result_df = st.session_state["weather_results"]
    result_country = st.session_state["weather_country"]

    if result_country != selected_country:
        st.info(
            f"현재 화면에는 이전에 조회한 "
            f"{result_country}의 결과가 표시되고 있습니다."
        )

    st.markdown("---")
    st.markdown("## 📊 공항별 날씨 조회 결과")

    total = len(result_df)
    warning_count = int(result_df["주의 조건 감지"].sum())
    average_temp = result_df["기온(°C)"].mean()

    m1, m2, m3 = st.columns(3)
    m1.metric("조회된 공항", f"{total:,}개")
    m2.metric("주의 조건 감지 공항", f"{warning_count:,}개")
    m3.metric(
        "평균 기온",
        f"{average_temp:.1f} °C"
        if pd.notna(average_temp) else "정보 없음"
    )

    show_warnings_only = st.checkbox(
        "주의 조건이 감지된 공항만 보기",
        value=False
    )

    display_df = result_df.copy()

    if show_warnings_only:
        display_df = display_df[
            display_df["주의 조건 감지"]
        ]

    search = st.text_input(
        "🔎 공항명 또는 공항 코드 검색"
    )

    if search:
        mask = (
            display_df["공항명"].astype(str).str.contains(
                search, case=False, na=False
            )
            |
            display_df["공항 코드"].astype(str).str.contains(
                search, case=False, na=False
            )
        )
        display_df = display_df[mask]

    visible_columns = [
        "공항명",
        "도시",
        "공항 코드",
        "공항 종류",
        "기온(°C)",
        "날씨",
        "풍속(km/h)",
        "돌풍(km/h)",
        "강수량(mm)",
        "가시거리(km)",
        "기상 안내"
    ]

    st.dataframe(
        display_df[visible_columns],
        use_container_width=True,
        hide_index=True
    )

    csv = display_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "📥 조회 결과 CSV 다운로드",
        data=csv,
        file_name="air_safe_weather.csv",
        mime="text/csv"
    )

    st.markdown("### 🗺️ 공항 위치")

    if not display_df.empty:
        map_df = display_df[
            ["위도", "경도"]
        ].rename(columns={
            "위도": "latitude",
            "경도": "longitude"
        })

        st.map(map_df)

st.markdown("---")

st.markdown("""
<div class="info-card">
    <h3>🔧 항공정비 관점에서 알아보기</h3>
    <p>• 강풍과 돌풍은 항공기 지상 작업에 영향을 줄 수 있습니다.</p>
    <p>• 비와 눈은 활주로 상태와 결빙 가능성 확인에 중요합니다.</p>
    <p>• 안개와 낮은 가시거리는 공항의 지상 이동에 영향을 줄 수 있습니다.</p>
    <p>• 실제 운항 및 정비 작업 판단은 공식 항공기상 정보와 관련 규정을 따라야 합니다.</p>
</div>
""", unsafe_allow_html=True)

st.caption(
    "Air Safe는 교육용 참고 프로그램입니다. "
    "공항 데이터 출처: OurAirports / 기상 데이터 출처: Open-Meteo. "
    "일부 공항의 기상 정보가 제공되지 않을 수 있으며, "
    "이 프로그램만으로 항공기 운항 가능 여부를 판단할 수 없습니다."
)
