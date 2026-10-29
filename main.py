
import streamlit as st
import pandas as pd
import requests
from babel import Locale
from deep_translator import GoogleTranslator
from datetime import datetime

st.set_page_config(
    page_title="Air Safe",
    page_icon="✈️",
    layout="wide"
)

AIRPORT_URL = (
    "https://raw.githubusercontent.com/"
    "davidmegginson/ourairports-data/main/airports.csv"
)

LANGUAGES = {
    "ko": "🇰🇷 한국어",
    "en": "🇺🇸 English",
    "ja": "🇯🇵 日本語",
    "zh": "🇨🇳 中文",
    "es": "🇪🇸 Español",
    "fr": "🇫🇷 Français",
}

TARGET_LANG = {
    "ko": "ko",
    "en": "en",
    "ja": "ja",
    "zh": "zh-CN",
    "es": "es",
    "fr": "fr",
}

TEXT = {
    "ko": {
        "subtitle": "항공 안전 · 공항 기상 모니터링",
        "country": "국가 선택",
        "search": "공항 검색",
        "search_hint": "한국어·영어 공항명, 도시명, IATA·ICAO 코드",
        "recommend": "⭐ 추천 공항",
        "recommend_desc": "선택한 국가의 주요 공항입니다.",
        "airport": "공항 선택",
        "weather": "현재 공항 기상",
        "info": "공항 정보",
        "temperature": "기온",
        "wind": "풍속",
        "gust": "돌풍",
        "visibility": "시정",
        "humidity": "습도",
        "cloud": "운량",
        "rain": "강수량",
        "feels": "체감온도",
        "pressure": "기압",
        "direction": "풍향",
        "choose": "이 공항 선택",
        "count": "검색 가능한 공항",
        "no_match": "검색 결과가 없습니다. 다른 이름이나 공항 코드를 입력해 보세요.",
        "loading": "공항 정보를 불러오는 중...",
        "weather_error": "기상 정보를 불러오지 못했습니다.",
        "unknown": "정보 없음",
        "advice": "기상 참고 안내",
        "safe": "표시된 날씨에서 뚜렷한 주의 신호가 감지되지 않았습니다.",
        "caution": "기상 조건에 주의가 필요할 수 있습니다.",
        "danger": "기상 조건이 항공 운항에 영향을 줄 가능성이 있습니다.",
        "disclaimer": "이 정보는 참고용입니다. 실제 운항 가능 여부나 비행 허가를 판단하지 않습니다. 공식 항공 기상 정보와 운항 절차를 따라야 합니다.",
        "source": "데이터 출처",
        "updated": "관측 시각",
    },
    "en": {
        "subtitle": "Aviation Safety · Airport Weather Monitoring",
        "country": "Select country",
        "search": "Search airports",
        "search_hint": "Airport, city, IATA or ICAO code",
        "recommend": "⭐ Recommended Airports",
        "recommend_desc": "Major airports in the selected country.",
        "airport": "Select airport",
        "weather": "Current Airport Weather",
        "info": "Airport Information",
        "temperature": "Temperature",
        "wind": "Wind Speed",
        "gust": "Wind Gust",
        "visibility": "Visibility",
        "humidity": "Humidity",
        "cloud": "Cloud Cover",
        "rain": "Precipitation",
        "feels": "Feels Like",
        "pressure": "Pressure",
        "direction": "Wind Direction",
        "choose": "Select Airport",
        "count": "Airports available",
        "no_match": "No results found. Try another name or airport code.",
        "loading": "Loading airport data...",
        "weather_error": "Unable to load weather data.",
        "unknown": "Unavailable",
        "advice": "Weather Advisory",
        "safe": "No major caution signal detected in the displayed weather.",
        "caution": "Weather conditions may require attention.",
        "danger": "Weather conditions may affect aviation operations.",
        "disclaimer": "For reference only. This does not determine flight clearance or operational suitability. Follow official aviation weather reports and procedures.",
        "source": "Data Sources",
        "updated": "Observation time",
    },
    "ja": {
        "subtitle": "航空安全・空港気象モニタリング",
        "country": "国を選択",
        "search": "空港を検索",
        "search_hint": "空港名、都市名、IATA・ICAOコード",
        "recommend": "⭐ おすすめ空港",
        "recommend_desc": "選択した国の主要空港です。",
        "airport": "空港を選択",
        "weather": "現在の空港気象",
        "info": "空港情報",
        "temperature": "気温",
        "wind": "風速",
        "gust": "最大瞬間風速",
        "visibility": "視程",
        "humidity": "湿度",
        "cloud": "雲量",
        "rain": "降水量",
        "feels": "体感温度",
        "pressure": "気圧",
        "direction": "風向",
        "choose": "この空港を選択",
        "count": "検索可能な空港",
        "no_match": "検索結果がありません。",
        "loading": "空港データを読み込み中...",
        "weather_error": "気象情報を取得できませんでした。",
        "unknown": "情報なし",
        "advice": "気象参考情報",
        "safe": "大きな注意信号は検出されませんでした。",
        "caution": "気象条件に注意が必要な場合があります。",
        "danger": "気象条件が航空運航に影響する可能性があります。",
        "disclaimer": "参考情報です。実際の運航可否を判断するものではありません。公式情報と手順に従ってください。",
        "source": "データ提供元",
        "updated": "観測時刻",
    },
    "zh": {
        "subtitle": "航空安全 · 机场天气监测",
        "country": "选择国家",
        "search": "搜索机场",
        "search_hint": "机场名称、城市、IATA或ICAO代码",
        "recommend": "⭐ 推荐机场",
        "recommend_desc": "所选国家的主要机场。",
        "airport": "选择机场",
        "weather": "当前机场天气",
        "info": "机场信息",
        "temperature": "气温",
        "wind": "风速",
        "gust": "阵风",
        "visibility": "能见度",
        "humidity": "湿度",
        "cloud": "云量",
        "rain": "降水量",
        "feels": "体感温度",
        "pressure": "气压",
        "direction": "风向",
        "choose": "选择此机场",
        "count": "可查询机场",
        "no_match": "没有搜索结果。",
        "loading": "正在加载机场数据...",
        "weather_error": "无法获取天气信息。",
        "unknown": "暂无信息",
        "advice": "天气参考信息",
        "safe": "未发现明显警示信号。",
        "caution": "天气状况可能需要特别注意。",
        "danger": "天气状况可能影响航空运行。",
        "disclaimer": "仅供参考，不能判断航班是否可以运行。请遵循官方航空天气信息和操作程序。",
        "source": "数据来源",
        "updated": "观测时间",
    },
    "es": {
        "subtitle": "Seguridad aérea · Meteorología aeroportuaria",
        "country": "Seleccionar país",
        "search": "Buscar aeropuertos",
        "search_hint": "Aeropuerto, ciudad o código IATA/ICAO",
        "recommend": "⭐ Aeropuertos recomendados",
        "recommend_desc": "Principales aeropuertos del país.",
        "airport": "Seleccionar aeropuerto",
        "weather": "Meteorología actual",
        "info": "Información del aeropuerto",
        "temperature": "Temperatura",
        "wind": "Velocidad del viento",
        "gust": "Ráfagas",
        "visibility": "Visibilidad",
        "humidity": "Humedad",
        "cloud": "Nubosidad",
        "rain": "Precipitación",
        "feels": "Sensación térmica",
        "pressure": "Presión",
        "direction": "Dirección del viento",
        "choose": "Seleccionar aeropuerto",
        "count": "Aeropuertos disponibles",
        "no_match": "No se encontraron resultados.",
        "loading": "Cargando datos...",
        "weather_error": "No se pudo cargar el tiempo.",
        "unknown": "No disponible",
        "advice": "Aviso meteorológico",
        "safe": "No se detectan señales importantes de precaución.",
        "caution": "Las condiciones pueden requerir atención.",
        "danger": "El tiempo podría afectar a las operaciones aéreas.",
        "disclaimer": "Solo como referencia. No determina la autorización ni la viabilidad de un vuelo. Siga los informes oficiales.",
        "source": "Fuentes de datos",
        "updated": "Hora de observación",
    },
    "fr": {
        "subtitle": "Sécurité aérienne · Météo des aéroports",
        "country": "Choisir un pays",
        "search": "Rechercher des aéroports",
        "search_hint": "Aéroport, ville ou code IATA/ICAO",
        "recommend": "⭐ Aéroports recommandés",
        "recommend_desc": "Principaux aéroports du pays.",
        "airport": "Choisir un aéroport",
        "weather": "Météo actuelle",
        "info": "Informations sur l'aéroport",
        "temperature": "Température",
        "wind": "Vitesse du vent",
        "gust": "Rafales",
        "visibility": "Visibilité",
        "humidity": "Humidité",
        "cloud": "Couverture nuageuse",
        "rain": "Précipitations",
        "feels": "Température ressentie",
        "pressure": "Pression",
        "direction": "Direction du vent",
        "choose": "Choisir cet aéroport",
        "count": "Aéroports disponibles",
        "no_match": "Aucun résultat trouvé.",
        "loading": "Chargement des données...",
        "weather_error": "Impossible de charger la météo.",
        "unknown": "Indisponible",
        "advice": "Avis météorologique",
        "safe": "Aucun signal majeur de vigilance détecté.",
        "caution": "Les conditions peuvent nécessiter une attention particulière.",
        "danger": "La météo peut affecter les opérations aériennes.",
        "disclaimer": "À titre indicatif uniquement. Ne détermine pas l'autorisation d'un vol. Suivez les bulletins officiels.",
        "source": "Sources des données",
        "updated": "Heure d'observation",
    },
}

# -------------------------------
# Session state
# -------------------------------
if "language" not in st.session_state:
    st.session_state.language = "ko"

if "chosen_ident" not in st.session_state:
    st.session_state.chosen_ident = ""

def t(key):
    lang = st.session_state.language
    return TEXT.get(lang, TEXT["en"]).get(key, key)

# -------------------------------
# Translation
# -------------------------------
@st.cache_data(ttl=86400, show_spinner=False)
def translate_text(text, language):
    if not text or pd.isna(text):
        return ""

    text = str(text).strip()

    if not text or language == "en":
        return text

    try:
        return GoogleTranslator(
            source="auto",
            target=TARGET_LANG[language]
        ).translate(text) or text
    except Exception:
        return text

@st.cache_data(ttl=86400, show_spinner=False)
def translate_query_to_english(query, language):
    if not query or language == "en":
        return query

    try:
        return GoogleTranslator(
            source=TARGET_LANG[language],
            target="en"
        ).translate(query) or query
    except Exception:
        return query

@st.cache_data(ttl=86400, show_spinner=False)
def localized_country_name(code, language):
    try:
        name = Locale.parse(language).territories.get(code)
        if name:
            return str(name)
    except Exception:
        pass

    return code

# -------------------------------
# Airport data
# -------------------------------
@st.cache_data(ttl=86400, show_spinner=False)
def load_airports():
    response = requests.get(AIRPORT_URL, timeout=40)
    response.raise_for_status()

    from io import BytesIO
    df = pd.read_csv(BytesIO(response.content), low_memory=False)

    df = df[
        df["type"].isin([
            "large_airport",
            "medium_airport",
            "small_airport",
        ])
    ].copy()

    required = [
        "name", "municipality", "iso_country",
        "iata_code", "gps_code", "ident",
        "type", "scheduled_service",
        "latitude_deg", "longitude_deg",
        "elevation_ft",
    ]

    for column in required:
        if column not in df.columns:
            df[column] = ""

    for column in [
        "name", "municipality", "iso_country",
        "iata_code", "gps_code", "ident",
        "type", "scheduled_service",
    ]:
        df[column] = df[column].fillna("").astype(str)

    df = df[df["iso_country"].str.len() == 2]
    return df

def get_codes(row):
    codes = []

    for column in ["iata_code", "gps_code", "ident"]:
        value = str(row.get(column, "")).strip()

        if value and value.lower() != "nan" and value not in codes:
            codes.append(value)

    return codes

def airport_label(row, language):
    name = translate_text(row.get("name", ""), language)
    city = str(row.get("municipality", "")).strip()

    if city and city.lower() != "nan":
        city = translate_text(city, language)
        name += f" — {city}"

    codes = get_codes(row)

    if codes:
        name += f" [{' · '.join(codes)}]"

    return name

# -------------------------------
# Weather data
# -------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def fetch_weather(latitude, longitude):
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": float(latitude),
            "longitude": float(longitude),
            "current": (
                "temperature_2m,relative_humidity_2m,"
                "apparent_temperature,precipitation,weather_code,"
                "cloud_cover,pressure_msl,wind_speed_10m,"
                "wind_direction_10m,wind_gusts_10m"
            ),
            "hourly": "visibility",
            "forecast_days": 1,
            "timezone": "auto",
        },
        timeout=20,
    )
    response.raise_for_status()

    data = response.json()
    current = data.get("current", {})
    hourly = data.get("hourly", {})

    visibility = None
    times = hourly.get("time", [])
    values = hourly.get("visibility", [])

    if times and values and current.get("time"):
        try:
            current_time = datetime.fromisoformat(current["time"])
            closest = min(
                range(len(times)),
                key=lambda i: abs(
                    datetime.fromisoformat(times[i]) - current_time
                )
            )
            visibility = values[closest]
        except Exception:
            pass

    return current, visibility

WEATHER_CODES = {
    0: {"ko": "맑음", "en": "Clear"},
    1: {"ko": "대체로 맑음", "en": "Mainly clear"},
    2: {"ko": "부분적으로 흐림", "en": "Partly cloudy"},
    3: {"ko": "흐림", "en": "Overcast"},
    45: {"ko": "안개", "en": "Fog"},
    48: {"ko": "착빙성 안개", "en": "Freezing fog"},
    51: {"ko": "약한 이슬비", "en": "Light drizzle"},
    53: {"ko": "이슬비", "en": "Drizzle"},
    55: {"ko": "강한 이슬비", "en": "Heavy drizzle"},
    61: {"ko": "약한 비", "en": "Light rain"},
    63: {"ko": "비", "en": "Rain"},
    65: {"ko": "강한 비", "en": "Heavy rain"},
    71: {"ko": "약한 눈", "en": "Light snow"},
    73: {"ko": "눈", "en": "Snow"},
    75: {"ko": "강한 눈", "en": "Heavy snow"},
    80: {"ko": "소나기", "en": "Rain showers"},
    81: {"ko": "강한 소나기", "en": "Heavy showers"},
    82: {"ko": "매우 강한 소나기", "en": "Violent showers"},
    95: {"ko": "뇌우", "en": "Thunderstorm"},
    96: {"ko": "우박 동반 뇌우", "en": "Thunderstorm with hail"},
    99: {"ko": "강한 우박 동반 뇌우", "en": "Heavy hail thunderstorm"},
}

def weather_description(code, language):
    try:
        code = int(code)
    except Exception:
        return t("unknown")

    entry = WEATHER_CODES.get(code)

    if not entry:
        return t("unknown")

    if language in entry:
        return entry[language]

    english = entry.get("en", "")
    return translate_text(english, language)

def assess_weather(current, visibility):
    code = current.get("weather_code", -1)

    try:
        code = int(code)
    except Exception:
        code = -1

    wind = float(current.get("wind_speed_10m") or 0)
    gust = float(current.get("wind_gusts_10m") or 0)

    severe_codes = {45, 48, 65, 75, 82, 95, 96, 99}
    caution_codes = {2, 3, 51, 53, 55, 61, 63, 71, 73, 80, 81}

    severe = (
        code in severe_codes
        or wind >= 40
        or gust >= 55
        or (visibility is not None and visibility < 1000)
    )

    caution = (
        code in caution_codes
        or wind >= 25
        or gust >= 35
        or (visibility is not None and visibility < 5000)
    )

    if severe:
        return "danger"
    if caution:
        return "caution"
    return "safe"

def fmt(value, unit="", decimals=1):
    try:
        if value is None or pd.isna(value):
            return t("unknown")
        return f"{float(value):,.{decimals}f}{unit}"
    except Exception:
        return t("unknown")

# -------------------------------
# Design
# -------------------------------
st.markdown("""
<style>
.stApp {
    background:
      radial-gradient(circle at 10% 0%, #17375e 0, transparent 32%),
      linear-gradient(135deg, #07111f, #0b1729 55%, #101e33);
    color: #edf4ff;
}
[data-testid="stHeader"] {background: transparent;}
h1,h2,h3,p,label,span {color:#edf4ff;}
.hero {
    padding:24px 28px;
    border:1px solid #31557c;
    border-radius:20px;
    background:linear-gradient(120deg,#15355b,#0c1c30);
    margin-bottom:18px;
}
.hero-title {
    font-size:34px;
    font-weight:800;
    letter-spacing:3px;
    color:white;
}
.hero-subtitle {font-size:14px;color:#a8c8ee;}
.section-title {
    font-size:20px;
    font-weight:750;
    margin:18px 0 10px;
}
.metric-card {
    background:rgba(17,37,61,.9);
    border:1px solid rgba(119,171,231,.23);
    border-radius:15px;
    padding:16px;
    margin-bottom:10px;
    min-height:100px;
}
.metric-label {font-size:13px;color:#9eb8d9;margin-bottom:8px;}
.metric-value {font-size:23px;font-weight:750;color:white;}
.recommend-card {
    background:linear-gradient(145deg,#142d4b,#0c1b2e);
    border:1px solid #2b4b70;
    border-radius:16px;
    padding:16px;
    min-height:130px;
    margin-bottom:8px;
}
.recommend-name {font-size:15px;font-weight:700;color:white;}
.recommend-meta {font-size:12px;color:#9eb8d9;margin-top:8px;}
.disclaimer {
    background:rgba(111,81,26,.18);
    border:1px solid rgba(237,184,76,.35);
    border-radius:12px;
    padding:13px 15px;
    font-size:12px;
    line-height:1.65;
    margin-top:15px;
}
div[data-baseweb="select"]>div,
div[data-baseweb="input"]>div {
    background:#101f33;
    border-color:#2a4668;
    border-radius:10px;
}
div[data-baseweb="select"] span,
div[data-baseweb="input"] input {color:#f1f6ff;}
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Header
# -------------------------------
left, right = st.columns([5, 1.4], vertical_alignment="center")

with right:
    st.selectbox(
        "Language",
        list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        key="language",
        label_visibility="collapsed",
    )

with left:
    st.markdown(
        f'<div class="hero">'
        f'<div class="hero-title">✈️ AIR SAFE</div>'
        f'<div class="hero-subtitle">{t("subtitle")}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

lang = st.session_state.language

# -------------------------------
# Load airport list
# -------------------------------
try:
    with st.spinner(t("loading")):
        airports = load_airports()
except Exception:
    st.error(t("loading"))
    st.stop()

country_codes = sorted(airports["iso_country"].unique())

country_map = {
    localized_country_name(code, lang): code
    for code in country_codes
}
country_names = sorted(country_map.keys(), key=str.casefold)

default_country = next(
    (name for name, code in country_map.items() if code == "KR"),
    country_names[0]
)

st.markdown(
    f'<div class="section-title">🌍 {t("country")}</div>',
    unsafe_allow_html=True
)

country_display = st.selectbox(
    t("country"),
    country_names,
    index=country_names.index(default_country),
)

country_code = country_map[country_display]

country_airports = airports[
    airports["iso_country"] == country_code
].copy()

if country_airports.empty:
    st.info(t("no_match"))
    st.stop()

st.caption(f'{t("count")}: {len(country_airports):,}')

# -------------------------------
# Search airports in Korean and other languages
# -------------------------------
st.markdown(
    f'<div class="section-title">🔎 {t("search")}</div>',
    unsafe_allow_html=True
)

query_text = st.text_input(
    t("search"),
    placeholder=t("search_hint"),
    key="airport_search",
).strip()

filtered = country_airports.copy()

if query_text:
    query_terms = {query_text.casefold()}

    # Translate the search term into English, e.g. 인천 -> Incheon
    if lang != "en":
        translated_query = translate_query_to_english(query_text, lang)
        if translated_query:
            query_terms.add(translated_query.casefold())

    # Common Korean airport names help when translation is unavailable
    KOREAN_AIRPORT_ALIASES = {
        "인천": ["incheon"],
        "인천공항": ["incheon"],
        "인천국제공항": ["incheon"],
        "김포": ["gimpo"],
        "김포공항": ["gimpo"],
        "김포국제공항": ["gimpo"],
        "제주": ["jeju"],
        "제주공항": ["jeju"],
        "제주국제공항": ["jeju"],
        "김해": ["gimhae", "busan"],
        "김해공항": ["gimhae", "busan"],
        "부산": ["busan", "gimhae"],
        "대구": ["daegu"],
        "청주": ["cheongju"],
        "광주": ["gwangju"],
        "양양": ["yangyang"],
        "울산": ["ulsan"],
        "여수": ["yeosu"],
        "포항": ["pohang"],
        "원주": ["wonju"],
        "군산": ["gunsan"],
    }

    for korean_name, english_names in KOREAN_AIRPORT_ALIASES.items():
        if korean_name in query_text:
            query_terms.update(x.casefold() for x in english_names)

    mask = pd.Series(False, index=filtered.index)

    search_columns = [
        "name",
        "municipality",
        "iata_code",
        "gps_code",
        "ident",
    ]

    for column in search_columns:
        values = filtered[column].fillna("").astype(str).str.casefold()

        for term in query_terms:
            mask |= values.str.contains(
                term,
                regex=False,
                na=False,
            )

    filtered = filtered[mask].copy()

    # If the user searches a translated airport name, check localized names too.
    # Limit extra translation work to avoid translating every airport.
    if filtered.empty and lang != "en":
        candidates = country_airports.head(250)
        translated_matches = []

        for idx, row in candidates.iterrows():
            translated_name = translate_text(row["name"], lang)
            translated_city = translate_text(row["municipality"], lang)

            if (
                query_text.casefold() in translated_name.casefold()
                or query_text.casefold() in translated_city.casefold()
            ):
                translated_matches.append(idx)

        if translated_matches:
            filtered = country_airports.loc[translated_matches].copy()

if filtered.empty:
    st.info(t("no_match"))
    st.stop()

filtered = filtered.head(100).copy()

# -------------------------------
# Recommended airports
# -------------------------------
st.markdown(
    f'<div class="section-title">{t("recommend")}</div>',
    unsafe_allow_html=True
)
st.caption(t("recommend_desc"))

recommendations = country_airports.copy()

recommendations["_rank"] = recommendations["type"].map({
    "large_airport": 0,
    "medium_airport": 1,
    "small_airport": 2,
}).fillna(3)

recommendations["_scheduled"] = (
    recommendations["scheduled_service"]
    .astype(str)
    .str.lower()
    .eq("yes")
    .astype(int)
)

recommendations = recommendations.sort_values(
    ["_rank", "_scheduled", "name"],
    ascending=[True, False, True],
).head(6)

columns = st.columns(3)

for i, (idx, row) in enumerate(recommendations.iterrows()):
    with columns[i % 3]:
        st.markdown(
            f'<div class="recommend-card">'
            f'<div class="recommend-name">✈️ '
            f'{airport_label(row, lang)}</div>'
            f'<div class="recommend-meta">'
            f'{str(row["type"]).replace("_", " ").title()}'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        if st.button(
            t("choose"),
            key=f"recommend_{row['ident']}_{i}",
            use_container_width=True,
        ):
            st.session_state.chosen_ident = str(row["ident"])
            st.session_state.airport_search = ""
            st.rerun()

# -------------------------------
# Airport selection
# -------------------------------
st.markdown(
    f'<div class="section-title">📍 {t("airport")}</div>',
    unsafe_allow_html=True
)

# A recommended airport remains selectable even if it is outside search results.
if st.session_state.chosen_ident:
    chosen_row = country_airports[
        country_airports["ident"].astype(str)
        == st.session_state.chosen_ident
    ]

    if not chosen_row.empty:
        chosen_idx = chosen_row.index[0]
        if chosen_idx not in filtered.index:
            filtered = pd.concat([
                chosen_row,
                filtered,
            ]).loc[lambda x: ~x.index.duplicated(keep="first")]

label_to_index = {}

for idx, row in filtered.iterrows():
    label = airport_label(row, lang)

    if label in label_to_index:
        label += f" · {row['ident']}"

    label_to_index[label] = idx

labels = list(label_to_index.keys())

default_index = 0

if st.session_state.chosen_ident:
    for i, label in enumerate(labels):
        row = filtered.loc[label_to_index[label]]
        if str(row["ident"]) == st.session_state.chosen_ident:
            default_index = i
            break

selected_label = st.selectbox(
    t("airport"),
    labels,
    index=default_index,
)

selected_airport = filtered.loc[label_to_index[selected_label]]

# -------------------------------
# Airport details
# -------------------------------
st.markdown(
    f'<div class="section-title">🛫 {t("info")}</div>',
    unsafe_allow_html=True
)

iata = str(selected_airport.get("iata_code", "")).strip()
icao = str(selected_airport.get("gps_code", "")).strip()

if not iata or iata.lower() == "nan":
    iata = "—"
if not icao or icao.lower() == "nan":
    icao = "—"

airport_type = str(
    selected_airport.get("type", "")
).replace("_", " ").title()

details = [
    ("IATA", iata),
    ("ICAO", icao),
    (t("info"), airport_type),
    (t("country"), country_display),
]

cols = st.columns(4)

for col, (label, value) in zip(cols, details):
    with col:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-label">{label}</div>'
            f'<div class="metric-value" style="font-size:18px">{value}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# -------------------------------
# Weather
# -------------------------------
st.markdown(
    f'<div class="section-title">🌦️ {t("weather")}</div>',
    unsafe_allow_html=True
)

latitude = selected_airport.get("latitude_deg")
longitude = selected_airport.get("longitude_deg")

try:
    current, visibility = fetch_weather(latitude, longitude)

    status = assess_weather(current, visibility)

    if status == "danger":
        st.error("🔴 " + t("danger"))
    elif status == "caution":
        st.warning("🟡 " + t("caution"))
    else:
        st.success("🟢 " + t("safe"))

    description = weather_description(
        current.get("weather_code"),
        lang,
    )

    st.markdown(
        f'<div class="recommend-card">'
        f'<div class="recommend-name">{description}</div>'
        f'<div class="recommend-meta">'
        f'{t("updated")}: {current.get("time", "—")}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    metrics = [
        ("🌡️", t("temperature"), fmt(current.get("temperature_2m"), " °C")),
        ("💨", t("wind"), fmt(current.get("wind_speed_10m"), " km/h")),
        ("🌬️", t("gust"), fmt(current.get("wind_gusts_10m"), " km/h")),
        ("👁️", t("visibility"), fmt(
            visibility / 1000 if visibility is not None else None,
            " km"
        )),
        ("💧", t("humidity"), fmt(current.get("relative_humidity_2m"), "%", 0)),
        ("☁️", t("cloud"), fmt(current.get("cloud_cover"), "%", 0)),
        ("🌧️", t("rain"), fmt(current.get("precipitation"), " mm")),
        ("🌡️", t("feels"), fmt(current.get("apparent_temperature"), " °C")),
        ("🧭", t("direction"), fmt(current.get("wind_direction_10m"), "°", 0)),
        ("📈", t("pressure"), fmt(current.get("pressure_msl"), " hPa")),
    ]

    cols = st.columns(4)

    for i, (emoji, label, value) in enumerate(metrics):
        with cols[i % 4]:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-label">{emoji} {label}</div>'
                f'<div class="metric-value">{value}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        f'<div class="disclaimer">⚠️ <b>{t("advice")}</b><br>'
        f'{t("disclaimer")}</div>',
        unsafe_allow_html=True,
    )

except Exception:
    st.error(t("weather_error"))

# -------------------------------
# Airport map
# -------------------------------
try:
    st.markdown(
        f'<div class="section-title">🗺️ {t("info")}</div>',
        unsafe_allow_html=True
    )

    st.map(
        pd.DataFrame({
            "lat": [float(latitude)],
            "lon": [float(longitude)],
        }),
        zoom=8,
    )
except Exception:
    pass

st.caption(
    f'{t("source")}: OurAirports · Open-Meteo'
)
