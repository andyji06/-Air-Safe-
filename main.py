
import requests
import pandas as pd
import streamlit as st
from babel import Locale
from functools import lru_cache

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Air Safe | Airport Weather",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

LANGUAGES = {
    "🇰🇷 한국어": "ko",
    "🇺🇸 English": "en",
    "🇯🇵 日本語": "ja",
    "🇨🇳 中文": "zh",
    "🇪🇸 Español": "es",
    "🇫🇷 Français": "fr",
}

TEXT = {
    "ko": {
        "tagline": "항공 기상 모니터링",
        "country": "국가 선택",
        "search": "공항 검색",
        "search_help": "공항 이름, 도시명, IATA 또는 ICAO 코드를 입력하세요.",
        "placeholder": "예: 인천, Incheon, ICN, RKSI, Heathrow",
        "choose_airport": "공항 선택",
        "no_match": "검색 결과가 없습니다. 다른 이름이나 코드를 입력해 보세요.",
        "loading": "공항 데이터를 불러오는 중입니다...",
        "airport_error": "공항 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.",
        "weather_error": "날씨 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.",
        "temperature": "기온",
        "wind": "풍속",
        "gust": "돌풍",
        "visibility": "시정",
        "humidity": "습도",
        "cloud": "운량",
        "rain": "강수량",
        "weather": "현재 날씨",
        "flight": "기상 참고",
        "good": "상대적으로 양호한 기상 조건",
        "caution": "주의가 필요한 기상 조건",
        "poor": "기상 조건을 면밀히 확인하세요",
        "unknown": "판단할 기상 데이터가 부족합니다",
        "disclaimer": "이 결과는 공개 기상 데이터를 이용한 참고 정보입니다. 실제 운항 가능 여부는 공식 항공 기상 자료와 항공사·조종사의 판단을 따라야 합니다.",
        "refresh": "날씨 새로고침",
        "updated": "날씨 정보는 조회 시점 기준입니다.",
        "airport_count": "검색된 공항 수",
        "select_hint": "검색 결과에서 공항을 선택하세요.",
        "airport_info": "공항 정보",
        "city": "도시",
        "code": "공항 코드",
        "coordinates": "좌표",
        "empty_country": "이 국가에서 검색 가능한 공항이 없습니다.",
        "wind_direction": "풍향",
        "pressure": "기압",
        "feels": "체감 기온",
        "source": "데이터 출처",
        "bad_weather": "강한 바람, 낮은 시정 또는 강수가 감지되었습니다.",
        "normal_weather": "표시된 지표에서 뚜렷한 주의 신호가 적습니다.",
    },
    "en": {
        "tagline": "AVIATION WEATHER MONITOR",
        "country": "Select country",
        "search": "Search airports",
        "search_help": "Search by airport name, city, IATA or ICAO code.",
        "placeholder": "e.g. Incheon, ICN, RKSI, Heathrow, LHR",
        "choose_airport": "Select airport",
        "no_match": "No results. Try another name or code.",
        "loading": "Loading airport data...",
        "airport_error": "Could not load airport data. Please try again.",
        "weather_error": "Could not load weather data. Please try again.",
        "temperature": "Temperature",
        "wind": "Wind",
        "gust": "Wind gust",
        "visibility": "Visibility",
        "humidity": "Humidity",
        "cloud": "Cloud cover",
        "rain": "Precipitation",
        "weather": "Current weather",
        "flight": "Weather guidance",
        "good": "Relatively favorable weather conditions",
        "caution": "Weather conditions require caution",
        "poor": "Review weather conditions carefully",
        "unknown": "Insufficient weather data",
        "disclaimer": "This is guidance based on public weather data, not an operational flight decision. Always follow official aviation weather reports and airline/pilot judgment.",
        "refresh": "Refresh weather",
        "updated": "Weather reflects the time of retrieval.",
        "airport_count": "Matching airports",
        "select_hint": "Choose an airport from the results.",
        "airport_info": "Airport information",
        "city": "City",
        "code": "Airport code",
        "coordinates": "Coordinates",
        "empty_country": "No searchable airports found in this country.",
        "wind_direction": "Wind direction",
        "pressure": "Pressure",
        "feels": "Feels like",
        "source": "Data source",
        "bad_weather": "Strong wind, low visibility, or precipitation detected.",
        "normal_weather": "Few obvious caution signals in the displayed indicators.",
    },
    "ja": {
        "tagline": "航空気象モニター",
        "country": "国を選択",
        "search": "空港を検索",
        "search_help": "空港名、都市名、IATA・ICAOコードで検索できます。",
        "placeholder": "例：仁川、Incheon、ICN、RKSI",
        "choose_airport": "空港を選択",
        "no_match": "検索結果がありません。別の名前やコードを入力してください。",
        "loading": "空港データを読み込み中...",
        "airport_error": "空港データを読み込めませんでした。",
        "weather_error": "気象データを読み込めませんでした。",
        "temperature": "気温",
        "wind": "風速",
        "gust": "最大瞬間風速",
        "visibility": "視程",
        "humidity": "湿度",
        "cloud": "雲量",
        "rain": "降水量",
        "weather": "現在の天気",
        "flight": "気象の目安",
        "good": "比較的良好な気象条件",
        "caution": "注意が必要な気象条件",
        "poor": "気象条件を慎重に確認してください",
        "unknown": "気象データが不足しています",
        "disclaimer": "これは公開気象データに基づく参考情報です。実際の運航判断には公式航空気象情報と航空会社・操縦士の判断が必要です。",
        "refresh": "気象情報を更新",
        "updated": "取得時点の気象情報です。",
        "airport_count": "検索された空港数",
        "select_hint": "検索結果から空港を選択してください。",
        "airport_info": "空港情報",
        "city": "都市",
        "code": "空港コード",
        "coordinates": "座標",
        "empty_country": "この国に検索可能な空港がありません。",
        "wind_direction": "風向",
        "pressure": "気圧",
        "feels": "体感温度",
        "source": "データソース",
        "bad_weather": "強風、視程不良、または降水が検出されました。",
        "normal_weather": "表示された指標では明確な注意信号は少なめです。",
    },
    "zh": {
        "tagline": "航空天气监测",
        "country": "选择国家",
        "search": "搜索机场",
        "search_help": "可搜索机场名称、城市、IATA 或 ICAO 代码。",
        "placeholder": "例如：仁川、Incheon、ICN、RKSI",
        "choose_airport": "选择机场",
        "no_match": "没有搜索结果，请尝试其他名称或代码。",
        "loading": "正在加载机场数据...",
        "airport_error": "无法加载机场数据，请稍后重试。",
        "weather_error": "无法加载天气数据，请稍后重试。",
        "temperature": "气温",
        "wind": "风速",
        "gust": "阵风",
        "visibility": "能见度",
        "humidity": "湿度",
        "cloud": "云量",
        "rain": "降水量",
        "weather": "当前天气",
        "flight": "天气参考",
        "good": "天气条件相对良好",
        "caution": "天气条件需要注意",
        "poor": "请仔细检查天气条件",
        "unknown": "天气数据不足",
        "disclaimer": "本结果仅为公开天气数据参考，不代表实际航班运行决定。请以官方航空气象资料及航空公司、飞行员判断为准。",
        "refresh": "刷新天气",
        "updated": "天气信息以查询时为准。",
        "airport_count": "符合条件的机场",
        "select_hint": "请从搜索结果中选择机场。",
        "airport_info": "机场信息",
        "city": "城市",
        "code": "机场代码",
        "coordinates": "坐标",
        "empty_country": "该国家没有可搜索的机场。",
        "wind_direction": "风向",
        "pressure": "气压",
        "feels": "体感温度",
        "source": "数据来源",
        "bad_weather": "检测到强风、低能见度或降水。",
        "normal_weather": "显示的指标中明显的注意信号较少。",
    },
    "es": {
        "tagline": "MONITOR METEOROLÓGICO AERONÁUTICO",
        "country": "Seleccionar país",
        "search": "Buscar aeropuertos",
        "search_help": "Busca por nombre, ciudad o código IATA/ICAO.",
        "placeholder": "Ej.: Incheon, ICN, RKSI, Heathrow",
        "choose_airport": "Seleccionar aeropuerto",
        "no_match": "Sin resultados. Prueba otro nombre o código.",
        "loading": "Cargando datos de aeropuertos...",
        "airport_error": "No se pudieron cargar los aeropuertos.",
        "weather_error": "No se pudo cargar el tiempo.",
        "temperature": "Temperatura",
        "wind": "Viento",
        "gust": "Ráfagas",
        "visibility": "Visibilidad",
        "humidity": "Humedad",
        "cloud": "Nubosidad",
        "rain": "Precipitación",
        "weather": "Tiempo actual",
        "flight": "Referencia meteorológica",
        "good": "Condiciones meteorológicas relativamente favorables",
        "caution": "Se requiere precaución",
        "poor": "Revise cuidadosamente las condiciones",
        "unknown": "Datos meteorológicos insuficientes",
        "disclaimer": "Esta información es orientativa y no decide si un vuelo puede operar. Consulte los informes oficiales y el criterio de la aerolínea y los pilotos.",
        "refresh": "Actualizar tiempo",
        "updated": "Información según la hora de consulta.",
        "airport_count": "Aeropuertos encontrados",
        "select_hint": "Selecciona un aeropuerto de los resultados.",
        "airport_info": "Información del aeropuerto",
        "city": "Ciudad",
        "code": "Código del aeropuerto",
        "coordinates": "Coordenadas",
        "empty_country": "No hay aeropuertos disponibles para buscar en este país.",
        "wind_direction": "Dirección del viento",
        "pressure": "Presión",
        "feels": "Sensación térmica",
        "source": "Fuente de datos",
        "bad_weather": "Se detectó viento fuerte, baja visibilidad o precipitación.",
        "normal_weather": "Hay pocas señales claras de precaución en los indicadores mostrados.",
    },
    "fr": {
        "tagline": "SURVEILLANCE MÉTÉO AÉRONAUTIQUE",
        "country": "Choisir un pays",
        "search": "Rechercher des aéroports",
        "search_help": "Recherchez par nom, ville ou code IATA/ICAO.",
        "placeholder": "Ex. : Incheon, ICN, RKSI, Heathrow",
        "choose_airport": "Choisir un aéroport",
        "no_match": "Aucun résultat. Essayez un autre nom ou code.",
        "loading": "Chargement des données aéroportuaires...",
        "airport_error": "Impossible de charger les aéroports.",
        "weather_error": "Impossible de charger la météo.",
        "temperature": "Température",
        "wind": "Vent",
        "gust": "Rafales",
        "visibility": "Visibilité",
        "humidity": "Humidité",
        "cloud": "Nébulosité",
        "rain": "Précipitations",
        "weather": "Météo actuelle",
        "flight": "Repère météorologique",
        "good": "Conditions météorologiques relativement favorables",
        "caution": "Conditions nécessitant de la prudence",
        "poor": "Vérifiez attentivement les conditions météo",
        "unknown": "Données météo insuffisantes",
        "disclaimer": "Ces informations sont indicatives et ne déterminent pas si un vol peut opérer. Consultez les bulletins officiels et les décisions de la compagnie et des pilotes.",
        "refresh": "Actualiser la météo",
        "updated": "Informations au moment de la consultation.",
        "airport_count": "Aéroports correspondants",
        "select_hint": "Choisissez un aéroport dans les résultats.",
        "airport_info": "Informations sur l'aéroport",
        "city": "Ville",
        "code": "Code de l'aéroport",
        "coordinates": "Coordonnées",
        "empty_country": "Aucun aéroport consultable dans ce pays.",
        "wind_direction": "Direction du vent",
        "pressure": "Pression",
        "feels": "Température ressentie",
        "source": "Source des données",
        "bad_weather": "Vent fort, faible visibilité ou précipitations détectés.",
        "normal_weather": "Peu de signaux d’alerte évidents dans les indicateurs affichés.",
    },
}

if "language" not in st.session_state:
    st.session_state.language = "ko"

# ---------------- STYLING ----------------
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 10% 0%, #142c4e 0, transparent 34%),
        linear-gradient(145deg, #07111f 0%, #0b1728 55%, #101f34 100%);
    color: #edf4ff;
}
.block-container {
    padding-top: 1.4rem;
    max-width: 1250px;
}
h1, h2, h3, p, label, span {
    color: inherit;
}
.hero {
    padding: 26px 28px;
    border: 1px solid rgba(132, 180, 255, .22);
    border-radius: 22px;
    background: linear-gradient(115deg, rgba(24, 53, 88, .95), rgba(10, 24, 43, .9));
    box-shadow: 0 12px 40px rgba(0,0,0,.18);
    margin-bottom: 20px;
}
.hero-kicker {
    font-size: 11px;
    letter-spacing: 3px;
    color: #83b8ff;
    font-weight: 700;
}
.hero-title {
    font-size: clamp(30px, 4vw, 45px);
    font-weight: 800;
    letter-spacing: -1.5px;
    margin: 5px 0 2px;
    color: #f2f7ff;
}
.hero-sub {
    font-size: 14px;
    color: #a8bdd8;
}
.section-card {
    border: 1px solid rgba(145, 181, 228, .17);
    border-radius: 17px;
    background: rgba(14, 30, 51, .82);
    padding: 17px 18px;
    margin: 8px 0 15px;
}
.metric-card {
    background: linear-gradient(145deg, #132943, #0d1d31);
    border: 1px solid rgba(127, 176, 242, .2);
    border-radius: 15px;
    padding: 17px;
    min-height: 105px;
}
.metric-label {
    font-size: 12px;
    color: #9bb3d1;
    margin-bottom: 9px;
}
.metric-value {
    font-size: 26px;
    font-weight: 750;
    color: #f2f7ff;
}
.status-card {
    border-radius: 16px;
    padding: 17px 19px;
    background: rgba(31, 58, 85, .7);
    border: 1px solid rgba(128, 174, 232, .22);
    margin: 10px 0;
}
.small-muted {
    color: #9bb1cc;
    font-size: 12px;
}
div[data-testid="stSelectbox"] label {
    font-size: 11px !important;
    color: #91a8c5 !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    border-radius: 11px;
}
div[data-testid="stTextInput"] input {
    border-radius: 12px;
}
.stButton > button {
    border-radius: 11px;
    border: 1px solid #376ba7;
    background: #183d68;
    color: white;
    font-weight: 650;
}
.stButton > button:hover {
    background: #24558b;
    border-color: #70b2ff;
    color: white;
}
div[data-testid="stAlert"] {
    border-radius: 12px;
}
hr {
    border-color: rgba(145, 181, 228, .15);
}
</style>
""", unsafe_allow_html=True)

# ---------------- LANGUAGE SELECTOR TOP RIGHT ----------------
header_left, header_right = st.columns([5, 1.25], vertical_alignment="center")

with header_right:
    language_labels = list(LANGUAGES.keys())
    current_label = next(
        (label for label, code in LANGUAGES.items()
         if code == st.session_state.language),
        "🇰🇷 한국어",
    )
    selected_label = st.selectbox(
        "Language",
        language_labels,
        index=language_labels.index(current_label),
        label_visibility="collapsed",
        key="language_selector",
    )
    st.session_state.language = LANGUAGES[selected_label]

lang = st.session_state.language
t = TEXT[lang]

with header_left:
    st.markdown(
        f"""
        <div style="padding:4px 0 14px">
            <div style="font-size:11px;letter-spacing:2px;color:#85baff;font-weight:700">
                AIR SAFE&nbsp; / &nbsp;FLIGHT WEATHER
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-kicker">✈ {t["tagline"]}</div>
        <div class="hero-title">AIR SAFE</div>
        <div class="hero-sub">
            Airport weather information · Wind · Visibility · Precipitation
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- AIRPORT DATA ----------------
AIRPORTS_URL = (
    "https://raw.githubusercontent.com/davidmegginson/"
    "ourairports-data/main/airports.csv"
)

@st.cache_data(ttl=86400, show_spinner=False)
def load_airports():
    response = requests.get(AIRPORTS_URL, timeout=35)
    response.raise_for_status()

    from io import BytesIO
    df = pd.read_csv(BytesIO(response.content), low_memory=False)

    required = [
        "name", "iso_country", "latitude_deg", "longitude_deg",
        "municipality", "iata_code", "gps_code", "ident", "type",
    ]
    for column in required:
        if column not in df.columns:
            df[column] = ""

    df = df[df["iso_country"].notna()].copy()
    df = df[df["latitude_deg"].notna() & df["longitude_deg"].notna()]
    df["iso_country"] = df["iso_country"].astype(str).str.upper()

    # Airport list excludes closed airports and focuses on airport types.
    allowed = ["large_airport", "medium_airport", "small_airport"]
    df = df[df["type"].isin(allowed)].copy()

    for column in [
        "name", "municipality", "iata_code", "gps_code", "ident", "type"
    ]:
        df[column] = df[column].fillna("").astype(str)

    return df.reset_index(drop=True)

@st.cache_data(show_spinner=False)
def get_country_names(language_code):
    locale = Locale.parse(language_code)
    names = {}
    for country_code in airports["iso_country"].unique():
        try:
            localized = locale.territories.get(country_code)
        except Exception:
            localized = None
        if not localized:
            localized = country_code
        names[country_code] = localized
    return names

try:
    with st.spinner(t["loading"]):
        airports = load_airports()
except Exception:
    st.error(t["airport_error"])
    st.stop()

country_names = get_country_names(lang)
country_codes = sorted(
    country_names.keys(),
    key=lambda code: country_names[code].casefold(),
)

# Default country: South Korea if available.
default_country = "KR" if "KR" in country_codes else country_codes[0]
if "selected_country" not in st.session_state:
    st.session_state.selected_country = default_country
if st.session_state.selected_country not in country_codes:
    st.session_state.selected_country = default_country

st.markdown(f"### 🌍 {t['country']}")

country_display = {
    f"{country_names[code]} ({code})": code for code in country_codes
}
display_options = list(country_display.keys())
current_country_label = next(
    (
        label for label, code in country_display.items()
        if code == st.session_state.selected_country
    ),
    display_options[0],
)

country_col, search_col = st.columns([1, 2.3], gap="large")

with country_col:
    chosen_country_label = st.selectbox(
        t["country"],
        display_options,
        index=display_options.index(current_country_label),
        label_visibility="collapsed",
        key="country_selector",
    )
    selected_country_code = country_display[chosen_country_label]
    st.session_state.selected_country = selected_country_code

country_airports = airports[
    airports["iso_country"] == selected_country_code
].copy()

# ---------------- AIRPORT SEARCH ----------------
def make_airport_label(row):
    name = str(row["name"])
    city = str(row["municipality"]).strip()
    iata = str(row["iata_code"]).strip()
    icao = str(row["gps_code"]).strip()
    ident = str(row["ident"]).strip()

    codes = []
    if iata:
        codes.append(iata)
    if icao and icao not in codes:
        codes.append(icao)
    if not codes and ident:
        codes.append(ident)

    code_text = " · ".join(codes)
    city_text = f" — {city}" if city else ""
    code_suffix = f"  [{code_text}]" if code_text else ""
    return f"{name}{city_text}{code_suffix}"

with search_col:
    search_text = st.text_input(
        t["search"],
        placeholder=t["placeholder"],
        help=t["search_help"],
        key="airport_search",
        label_visibility="collapsed",
    )

query = search_text.strip().casefold()
filtered = country_airports.copy()

if query:
    columns_to_search = [
        "name", "municipality", "iata_code", "gps_code", "ident"
    ]
    match_mask = pd.Series(False, index=filtered.index)
    for column in columns_to_search:
        match_mask |= filtered[column].str.casefold().str.contains(
            query, regex=False, na=False
        )
    filtered = filtered[match_mask]

priority = {
    "large_airport": 0,
    "medium_airport": 1,
    "small_airport": 2,
}
filtered["_priority"] = filtered["type"].map(priority).fillna(5)
filtered = filtered.sort_values(
    ["_priority", "name"]
).head(200)

st.caption(
    f"{t['airport_count']}: {len(filtered):,}  ·  "
    f"{country_names[selected_country_code]}"
)

if filtered.empty:
    st.info(t["no_match"] if query else t["empty_country"])
    st.stop()

airport_records = filtered.to_dict("records")

# Keep selection stable by airport ident, not the display string alone.
airport_options = {
    make_airport_label(row): row for row in airport_records
}

if "selected_airport_key" not in st.session_state:
    st.session_state.selected_airport_key = None

selected_airport_label = st.selectbox(
    t["choose_airport"],
    list(airport_options.keys()),
    index=None,
    placeholder=t["select_hint"],
    key="airport_selector",
)

if selected_airport_label is None:
    st.info(t["select_hint"])
    st.stop()

selected_airport = airport_options[selected_airport_label]

st.markdown("---")
st.markdown(f"### ✈️ {t['airport_info']}")

info1, info2, info3 = st.columns(3)
with info1:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="small-muted">{t["city"]}</div>
            <div style="font-size:18px;font-weight:700">
                {selected_airport["municipality"] or "—"}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with info2:
    code_value = (
        selected_airport["iata_code"]
        or selected_airport["gps_code"]
        or selected_airport["ident"]
        or "—"
    )
    st.markdown(
        f"""
        <div class="section-card">
            <div class="small-muted">{t["code"]}</div>
            <div style="font-size:18px;font-weight:700">{code_value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with info3:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="small-muted">{t["coordinates"]}</div>
            <div style="font-size:15px;font-weight:650">
                {selected_airport["latitude_deg"]:.3f},
                {selected_airport["longitude_deg"]:.3f}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------- WEATHER DATA ----------------
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    "ko": {
        0: "맑음", 1: "대체로 맑음", 2: "구름 조금", 3: "흐림",
        45: "안개", 48: "착빙성 안개", 51: "약한 이슬비",
        53: "이슬비", 55: "강한 이슬비", 56: "어는 이슬비",
        57: "강한 어는 이슬비", 61: "약한 비", 63: "비",
        65: "강한 비", 66: "어는 비", 67: "강한 어는 비",
        71: "약한 눈", 73: "눈", 75: "강한 눈", 77: "싸락눈",
        80: "소나기", 81: "강한 소나기", 82: "매우 강한 소나기",
        85: "눈 소나기", 86: "강한 눈 소나기", 95: "뇌우",
        96: "우박 동반 뇌우", 99: "강한 우박 동반 뇌우",
    },
    "en": {
        0: "Clear", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Rime fog", 51: "Light drizzle", 53: "Drizzle",
        55: "Heavy drizzle", 56: "Freezing drizzle", 57: "Heavy freezing drizzle",
        61: "Light rain", 63: "Rain", 65: "Heavy rain", 66: "Freezing rain",
        67: "Heavy freezing rain", 71: "Light snow", 73: "Snow", 75: "Heavy snow",
        77: "Snow grains", 80: "Rain showers", 81: "Heavy showers",
        82: "Violent showers", 85: "Snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe hailstorm",
    },
    "ja": {
        0: "晴れ", 1: "おおむね晴れ", 2: "晴れ時々曇り", 3: "曇り",
        45: "霧", 48: "着氷性の霧", 51: "弱い霧雨", 53: "霧雨",
        55: "強い霧雨", 61: "弱い雨", 63: "雨", 65: "強い雨",
        71: "弱い雪", 73: "雪", 75: "大雪", 80: "にわか雨",
        81: "強いにわか雨", 82: "非常に強いにわか雨",
        95: "雷雨", 96: "ひょうを伴う雷雨", 99: "強いひょうを伴う雷雨",
    },
    "zh": {
        0: "晴朗", 1: "大致晴朗", 2: "局部多云", 3: "阴天",
        45: "雾", 48: "冻雾", 51: "小毛毛雨", 53: "毛毛雨",
        55: "强毛毛雨", 61: "小雨", 63: "雨", 65: "大雨",
        71: "小雪", 73: "降雪", 75: "大雪", 80: "阵雨",
        81: "强阵雨", 82: "猛烈阵雨", 95: "雷暴",
        96: "伴有冰雹的雷暴", 99: "强冰雹雷暴",
    },
    "es": {
        0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado",
        3: "Nublado", 45: "Niebla", 48: "Niebla helada",
        51: "Llovizna ligera", 53: "Llovizna", 55: "Llovizna intensa",
        61: "Lluvia ligera", 63: "Lluvia", 65: "Lluvia intensa",
        71: "Nieve ligera", 73: "Nieve", 75: "Nieve intensa",
        80: "Chubascos", 81: "Chubascos fuertes", 82: "Chubascos violentos",
        95: "Tormenta", 96: "Tormenta con granizo", 99: "Granizada fuerte",
    },
    "fr": {
        0: "Dégagé", 1: "Plutôt dégagé", 2: "Partiellement nuageux",
        3: "Couvert", 45: "Brouillard", 48: "Brouillard givrant",
        51: "Bruine faible", 53: "Bruine", 55: "Bruine forte",
        61: "Pluie faible", 63: "Pluie", 65: "Pluie forte",
        71: "Neige faible", 73: "Neige", 75: "Neige forte",
        80: "Averses", 81: "Fortes averses", 82: "Averses violentes",
        95: "Orage", 96: "Orage avec grêle", 99: "Forte grêle",
    },
}

def weather_description(code, language):
    descriptions = WEATHER_CODES.get(language, WEATHER_CODES["en"])
    return descriptions.get(code, f"WMO {code}")

def fetch_weather(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "is_day,precipitation,rain,showers,snowfall,weather_code,"
            "cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,"
            "wind_direction_10m,wind_gusts_10m"
        ),
        "hourly": "visibility,precipitation_probability",
        "forecast_days": 1,
        "timezone": "auto",
    }
    response = requests.get(WEATHER_URL, params=params, timeout=25)
    response.raise_for_status()
    return response.json()

def assess_weather(current, visibility_m):
    wind = current.get("wind_speed_10m")
    gust = current.get("wind_gusts_10m")
    code = current.get("weather_code")
    rain = current.get("precipitation", 0) or 0

    # Illustrative thresholds only; not aviation operating limits.
    severe_codes = {95, 96, 99}
    reduced_visibility = visibility_m is not None and visibility_m < 3000
    strong_wind = wind is not None and wind >= 40
    strong_gust = gust is not None and gust >= 60
    active_precipitation = rain >= 5
    thunderstorm = code in severe_codes

    if thunderstorm or reduced_visibility or strong_wind or strong_gust or active_precipitation:
        return "poor"
    if (wind is not None and wind >= 25) or (visibility_m is not None and visibility_m < 8000):
        return "caution"
    if wind is None or visibility_m is None:
        return "unknown"
    return "good"

def display_metric(label, value, unit=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}{unit}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

weather_col, refresh_col = st.columns([4, 1], vertical_alignment="center")
with weather_col:
    st.markdown(f"### 🌦️ {t['weather']}")
with refresh_col:
    if st.button(t["refresh"], use_container_width=True):
        st.cache_data.clear()
        st.rerun()

try:
    with st.spinner(t["loading"]):
        weather_data = fetch_weather(
            float(selected_airport["latitude_deg"]),
            float(selected_airport["longitude_deg"]),
        )

    current = weather_data.get("current", {})
    current_units = weather_data.get("current_units", {})
    hourly = weather_data.get("hourly", {})
    hourly_units = weather_data.get("hourly_units", {})

    if not current:
        st.error(t["weather_error"])
        st.stop()

    # Find the hourly record nearest to the current local time.
    visibility_values = hourly.get("visibility", [])
    hourly_times = hourly.get("time", [])
    visibility_m = None

    if visibility_values and hourly_times:
        current_time = current.get("time", "")
        try:
            closest_index = min(
                range(len(hourly_times)),
                key=lambda i: abs(
                    pd.Timestamp(hourly_times[i])
                    - pd.Timestamp(current_time)
                ),
            )
            visibility_m = visibility_values[closest_index]
        except Exception:
            visibility_m = visibility_values[0]

    weather_code = current.get("weather_code")
    weather_name = weather_description(weather_code, lang)
    wind = current.get("wind_speed_10m")
    gust = current.get("wind_gusts_10m")
    humidity = current.get("relative_humidity_2m")
    cloud = current.get("cloud_cover")
    rain = current.get("precipitation")
    temp = current.get("temperature_2m")
    feels = current.get("apparent_temperature")
    pressure = current.get("pressure_msl")
    wind_direction = current.get("wind_direction_10m")

    visibility_km = (
        visibility_m / 1000 if visibility_m is not None else None
    )

    metric_cols = st.columns(4)
    metrics = [
        (t["temperature"], temp, "°C"),
        (t["wind"], wind, " km/h"),
        (t["gust"], gust, " km/h"),
        (t["visibility"], round(visibility_km, 1) if visibility_km is not None else "—", " km"),
    ]

    for col, (label, value, unit) in zip(metric_cols, metrics):
        with col:
            display_metric(
                label,
                value if value is not None else "—",
                unit if value is not None else "",
            )

    st.markdown("")

    secondary_cols = st.columns(4)
    secondary_metrics = [
        (t["humidity"], humidity, "%"),
        (t["cloud"], cloud, "%"),
        (t["rain"], rain, " mm"),
        (t["feels"], feels, "°C"),
    ]

    for col, (label, value, unit) in zip(secondary_cols, secondary_metrics):
        with col:
            display_metric(
                label,
                value if value is not None else "—",
                unit if value is not None else "",
            )

    st.markdown(
        f"""
        <div class="status-card">
            <div style="font-size:12px;color:#9bb3d1">{t["weather"]}</div>
            <div style="font-size:24px;font-weight:750;margin:6px 0">
                {weather_name}
            </div>
            <div style="font-size:13px;color:#bdd0e8">
                {t["wind_direction"]}: {wind_direction if wind_direction is not None else "—"}°
                &nbsp; · &nbsp;
                {t["pressure"]}: {pressure if pressure is not None else "—"} hPa
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    status = assess_weather(current, visibility_m)
    status_text = {
        "ko": {
            "good": "🟢 " + t["good"],
            "caution": "🟡 " + t["caution"],
            "poor": "🔴 " + t["poor"],
            "unknown": "⚪ " + t["unknown"],
        },
        "en": {
            "good": "🟢 " + t["good"],
            "caution": "🟡 " + t["caution"],
            "poor": "🔴 " + t["poor"],
            "unknown": "⚪ " + t["unknown"],
        },
        "ja": {
            "good": "🟢 " + t["good"],
            "caution": "🟡 " + t["caution"],
            "poor": "🔴 " + t["poor"],
            "unknown": "⚪ " + t["unknown"],
        },
        "zh": {
            "good": "🟢 " + t["good"],
            "caution": "🟡 " + t["caution"],
            "poor": "🔴 " + t["poor"],
            "unknown": "⚪ " + t["unknown"],
        },
        "es": {
            "good": "🟢 " + t["good"],
            "caution": "🟡 " + t["caution"],
            "poor": "🔴 " + t["poor"],
            "unknown": "⚪ " + t["unknown"],
        },
        "fr": {
            "good": "🟢 " + t["good"],
            "caution": "🟡 " + t["caution"],
            "poor": "🔴 " + t["poor"],
            "unknown": "⚪ " + t["unknown"],
        },
    }

    st.markdown(f"### 🛫 {t['flight']}")
    st.info(status_text.get(lang, status_text["en"])[status])

    if status == "poor":
        st.warning(t["bad_weather"])
    elif status == "good":
        st.caption(t["normal_weather"])

    st.caption(t["disclaimer"])
    st.caption(t["updated"])
    st.markdown(
        f'{t["source"]}: [Open-Meteo](https://open-meteo.com/) · '
        '[OurAirports](https://ourairports.com/data/)'
    )

except requests.RequestException:
    st.error(t["weather_error"])
except Exception as exc:
    st.error(t["weather_error"])
    with st.expander("Technical details"):
        st.code(str(exc))
