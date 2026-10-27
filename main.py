
import streamlit as st
import pandas as pd
import requests
import pycountry
from babel import Locale
from deep_translator import GoogleTranslator
from datetime import datetime
from functools import lru_cache

# -------------------------------
# 페이지 설정
# -------------------------------
st.set_page_config(
    page_title="Air Safe | 항공 안전 모니터",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
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

TRANSLATOR_LANGUAGES = {
    "ko": "ko",
    "en": "en",
    "ja": "ja",
    "zh": "zh-CN",
    "es": "es",
    "fr": "fr",
}

TEXT = {
    "ko": {
        "title": "AIR SAFE",
        "subtitle": "항공 안전 · 공항 기상 모니터링",
        "country": "국가 선택",
        "search": "공항 검색",
        "search_hint": "공항명, 도시명, IATA 또는 ICAO 코드 입력",
        "airport": "공항 선택",
        "weather": "현재 공항 기상",
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
        "assessment": "기상 참고 정보",
        "safe": "현재 표시된 기상 기준으로 특별한 주의 신호가 감지되지 않았습니다.",
        "caution": "기상 조건에 주의가 필요할 수 있습니다.",
        "danger": "기상 조건이 항공 운항에 영향을 줄 가능성이 있습니다.",
        "disclaimer": "이 정보는 참고용이며 실제 운항 가능 여부나 비행 허가를 판단하지 않습니다. 운항 결정은 항공사·조종사·관제기관의 공식 정보와 절차를 따라야 합니다.",
        "no_airports": "해당 국가의 공항 정보를 찾을 수 없습니다.",
        "no_match": "검색 결과가 없습니다. 다른 공항명이나 코드를 입력해 주세요.",
        "loading": "공항 정보를 불러오는 중입니다...",
        "weather_error": "기상 정보를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.",
        "select_airport": "공항을 선택하면 기상 정보가 표시됩니다.",
        "last_updated": "기상 정보 조회 시각",
        "airport_count": "검색 가능한 공항 수",
        "data_source": "데이터 출처",
        "weather_status": "운항 참고",
        "country_search": "국가 검색",
        "airport_info": "공항 정보",
        "latitude": "위도",
        "longitude": "경도",
        "elevation": "고도",
        "timezone": "시간대",
        "unknown": "정보 없음",
        "flight_note": "날씨만으로 실제 비행 가능 여부를 확정할 수 없습니다.",
    },
    "en": {
        "title": "AIR SAFE",
        "subtitle": "Aviation Safety · Airport Weather Monitoring",
        "country": "Select country",
        "search": "Search airports",
        "search_hint": "Airport, city, IATA or ICAO code",
        "airport": "Select airport",
        "weather": "Current Airport Weather",
        "temperature": "Temperature",
        "wind": "Wind speed",
        "gust": "Wind gust",
        "visibility": "Visibility",
        "humidity": "Humidity",
        "cloud": "Cloud cover",
        "rain": "Precipitation",
        "feels": "Feels like",
        "pressure": "Pressure",
        "direction": "Wind direction",
        "assessment": "Weather advisory",
        "safe": "No major caution signal detected in the displayed weather data.",
        "caution": "Weather conditions may require attention.",
        "danger": "Weather conditions may affect aviation operations.",
        "disclaimer": "This information is for reference only and does not determine flight clearance or operational suitability. Follow official airline, pilot, and air traffic control procedures.",
        "no_airports": "No airport data found for this country.",
        "no_match": "No results. Try another airport name or code.",
        "loading": "Loading airport data...",
        "weather_error": "Unable to load weather data. Please try again.",
        "select_airport": "Select an airport to view its weather.",
        "last_updated": "Weather retrieved at",
        "airport_count": "Airports available",
        "data_source": "Data sources",
        "weather_status": "Operational reference",
        "country_search": "Search countries",
        "airport_info": "Airport information",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "elevation": "Elevation",
        "timezone": "Time zone",
        "unknown": "Unavailable",
        "flight_note": "Weather alone cannot determine whether a flight can operate.",
    },
    "ja": {
        "title": "AIR SAFE",
        "subtitle": "航空安全・空港気象モニタリング",
        "country": "国を選択",
        "search": "空港を検索",
        "search_hint": "空港名、都市名、IATA・ICAOコード",
        "airport": "空港を選択",
        "weather": "現在の空港気象",
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
        "assessment": "気象参考情報",
        "safe": "表示された気象データでは、重大な注意信号は検出されていません。",
        "caution": "気象条件に注意が必要な場合があります。",
        "danger": "気象条件が航空運航に影響する可能性があります。",
        "disclaimer": "この情報は参考用です。実際の運航可否や飛行許可を判断するものではありません。公式情報と手順に従ってください。",
        "no_airports": "この国の空港情報が見つかりません。",
        "no_match": "検索結果がありません。別の空港名やコードを入力してください。",
        "loading": "空港情報を読み込んでいます...",
        "weather_error": "気象情報を取得できませんでした。再度お試しください。",
        "select_airport": "空港を選択すると気象情報が表示されます。",
        "last_updated": "気象情報取得時刻",
        "airport_count": "検索可能な空港数",
        "data_source": "データ提供元",
        "weather_status": "運航参考",
        "country_search": "国を検索",
        "airport_info": "空港情報",
        "latitude": "緯度",
        "longitude": "経度",
        "elevation": "標高",
        "timezone": "タイムゾーン",
        "unknown": "情報なし",
        "flight_note": "天候だけで実際の飛行可否を判断することはできません。",
    },
    "zh": {
        "title": "AIR SAFE",
        "subtitle": "航空安全 · 机场天气监测",
        "country": "选择国家",
        "search": "搜索机场",
        "search_hint": "机场名称、城市、IATA或ICAO代码",
        "airport": "选择机场",
        "weather": "当前机场天气",
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
        "assessment": "天气参考信息",
        "safe": "当前显示的天气数据中未发现明显的警示信号。",
        "caution": "天气状况可能需要特别注意。",
        "danger": "天气状况可能影响航空运行。",
        "disclaimer": "此信息仅供参考，不能用于确定航班是否可以运行或获得飞行许可。请遵循官方信息和操作程序。",
        "no_airports": "未找到该国家的机场信息。",
        "no_match": "没有搜索结果，请尝试其他机场名称或代码。",
        "loading": "正在加载机场数据...",
        "weather_error": "无法获取天气信息，请稍后重试。",
        "select_airport": "选择机场后即可查看天气信息。",
        "last_updated": "天气查询时间",
        "airport_count": "可查询机场数量",
        "data_source": "数据来源",
        "weather_status": "运行参考",
        "country_search": "搜索国家",
        "airport_info": "机场信息",
        "latitude": "纬度",
        "longitude": "经度",
        "elevation": "海拔",
        "timezone": "时区",
        "unknown": "暂无信息",
        "flight_note": "不能仅凭天气判断航班是否可以运行。",
    },
    "es": {
        "title": "AIR SAFE",
        "subtitle": "Seguridad aérea · Monitorización meteorológica",
        "country": "Seleccionar país",
        "search": "Buscar aeropuertos",
        "search_hint": "Aeropuerto, ciudad o código IATA/ICAO",
        "airport": "Seleccionar aeropuerto",
        "weather": "Meteorología actual",
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
        "assessment": "Aviso meteorológico",
        "safe": "No se detectan señales importantes de precaución en los datos mostrados.",
        "caution": "Las condiciones meteorológicas pueden requerir atención.",
        "danger": "El tiempo podría afectar a las operaciones aéreas.",
        "disclaimer": "Esta información es orientativa y no determina la autorización ni la viabilidad de un vuelo. Siga los procedimientos y fuentes oficiales.",
        "no_airports": "No se encontraron aeropuertos en este país.",
        "no_match": "Sin resultados. Pruebe con otro nombre o código.",
        "loading": "Cargando datos de aeropuertos...",
        "weather_error": "No se pudo cargar el tiempo. Inténtelo de nuevo.",
        "select_airport": "Seleccione un aeropuerto para ver el tiempo.",
        "last_updated": "Consulta meteorológica",
        "airport_count": "Aeropuertos disponibles",
        "data_source": "Fuentes de datos",
        "weather_status": "Referencia operativa",
        "country_search": "Buscar países",
        "airport_info": "Información del aeropuerto",
        "latitude": "Latitud",
        "longitude": "Longitud",
        "elevation": "Elevación",
        "timezone": "Zona horaria",
        "unknown": "No disponible",
        "flight_note": "El tiempo por sí solo no determina si un vuelo puede operar.",
    },
    "fr": {
        "title": "AIR SAFE",
        "subtitle": "Sécurité aérienne · Suivi météo des aéroports",
        "country": "Choisir un pays",
        "search": "Rechercher des aéroports",
        "search_hint": "Aéroport, ville ou code IATA/ICAO",
        "airport": "Choisir un aéroport",
        "weather": "Météo actuelle de l'aéroport",
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
        "assessment": "Avis météorologique",
        "safe": "Aucun signal majeur de vigilance détecté dans les données affichées.",
        "caution": "Les conditions météo peuvent nécessiter une attention particulière.",
        "danger": "Les conditions météo peuvent affecter les opérations aériennes.",
        "disclaimer": "Ces informations sont indicatives et ne déterminent pas l'autorisation ou la faisabilité d'un vol. Suivez les sources et procédures officielles.",
        "no_airports": "Aucun aéroport trouvé pour ce pays.",
        "no_match": "Aucun résultat. Essayez un autre nom ou code.",
        "loading": "Chargement des données des aéroports...",
        "weather_error": "Impossible de charger la météo. Veuillez réessayer.",
        "select_airport": "Choisissez un aéroport pour afficher la météo.",
        "last_updated": "Heure de consultation météo",
        "airport_count": "Aéroports disponibles",
        "data_source": "Sources des données",
        "weather_status": "Référence opérationnelle",
        "country_search": "Rechercher des pays",
        "airport_info": "Informations sur l'aéroport",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "elevation": "Altitude",
        "timezone": "Fuseau horaire",
        "unknown": "Indisponible",
        "flight_note": "La météo seule ne permet pas de déterminer si un vol peut être effectué.",
    },
}

# -------------------------------
# 언어 및 번역 함수
# -------------------------------
if "language" not in st.session_state:
    st.session_state.language = "ko"

def tr(key):
    return TEXT[st.session_state.language].get(
        key, TEXT["en"].get(key, key)
    )

@st.cache_data(ttl=86400, show_spinner=False)
def translate_airport_name(name, target_language):
    """공항 이름 번역. 실패하면 원문을 반환합니다."""
    if not isinstance(name, str) or not name.strip():
        return name

    if target_language == "en":
        return name

    target = TRANSLATOR_LANGUAGES.get(target_language, "en")

    try:
        translated = GoogleTranslator(
            source="auto",
            target=target,
        ).translate(name.strip())

        return translated if translated else name
    except Exception:
        return name

@st.cache_data(ttl=86400, show_spinner=False)
def get_country_name(country_code, language):
    try:
        locale = Locale.parse(language)
        name = locale.territories.get(country_code)
        if name:
            return str(name)
    except Exception:
        pass

    country = pycountry.countries.get(alpha_2=country_code)
    return country.name if country else country_code

# -------------------------------
# 공항 데이터
# -------------------------------
@st.cache_data(ttl=86400, show_spinner=False)
def load_airports():
    response = requests.get(AIRPORT_URL, timeout=30)
    response.raise_for_status()

    df = pd.read_csv(response.url if False else AIRPORT_URL)

    required_columns = [
        "name",
        "type",
        "iso_country",
        "municipality",
        "iata_code",
        "gps_code",
        "ident",
        "latitude_deg",
        "longitude_deg",
        "elevation_ft",
        "home_link",
        "scheduled_service",
    ]

    for column in required_columns:
        if column not in df.columns:
            df[column] = ""

    df = df[
        df["type"].isin(
            ["large_airport", "medium_airport", "small_airport"]
        )
    ].copy()

    df["iso_country"] = df["iso_country"].fillna("").astype(str)
    df["name"] = df["name"].fillna("").astype(str)
    df["municipality"] = df["municipality"].fillna("").astype(str)

    for column in ["iata_code", "gps_code", "ident"]:
        df[column] = df[column].fillna("").astype(str)

    df = df[df["iso_country"].str.len() == 2]

    return df

def airport_codes(row):
    codes = []

    iata = str(row.get("iata_code", "")).strip()
    icao = str(row.get("gps_code", "")).strip()
    ident = str(row.get("ident", "")).strip()

    if iata and iata.lower() != "nan":
        codes.append(iata)

    if icao and icao.lower() != "nan" and icao not in codes:
        codes.append(icao)

    if not codes and ident and ident.lower() != "nan":
        codes.append(ident)

    return " · ".join(codes)

def make_airport_label(row, language):
    original_name = str(row.get("name", "Unknown airport"))
    city = str(row.get("municipality", "") or "").strip()

    translated_name = translate_airport_name(original_name, language)

    translated_city = (
        translate_airport_name(city, language)
        if city and city.lower() != "nan"
        else ""
    )

    codes = airport_codes(row)
    city_part = f" — {translated_city}" if translated_city else ""
    code_part = f" [{codes}]" if codes else ""

    return f"{translated_name}{city_part}{code_part}"

# -------------------------------
# 날씨 API
# -------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def fetch_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": float(latitude),
        "longitude": float(longitude),
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "apparent_temperature,is_day,precipitation,"
            "rain,showers,weather_code,cloud_cover,"
            "pressure_msl,surface_pressure,wind_speed_10m,"
            "wind_direction_10m,wind_gusts_10m"
        ),
        "hourly": "visibility",
        "forecast_days": 1,
        "timezone": "auto",
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    current = data.get("current", {})

    hourly = data.get("hourly", {})
    hourly_times = hourly.get("time", [])
    hourly_visibility = hourly.get("visibility", [])

    current_time = current.get("time")
    visibility = None

    if current_time and hourly_times and hourly_visibility:
        try:
            nearest_index = min(
                range(len(hourly_times)),
                key=lambda i: abs(
                    datetime.fromisoformat(hourly_times[i])
                    - datetime.fromisoformat(current_time)
                ),
            )
            visibility = hourly_visibility[nearest_index]
        except Exception:
            visibility = None

    return {
        "current": current,
        "visibility": visibility,
        "timezone": data.get("timezone", ""),
    }

def weather_description(code, language):
    descriptions = {
        "ko": {
            0: "맑음",
            1: "대체로 맑음",
            2: "부분적으로 흐림",
            3: "흐림",
            45: "안개",
            48: "착빙성 안개",
            51: "약한 이슬비",
            53: "이슬비",
            55: "강한 이슬비",
            61: "약한 비",
            63: "비",
            65: "강한 비",
            71: "약한 눈",
            73: "눈",
            75: "강한 눈",
            80: "소나기",
            81: "강한 소나기",
            82: "매우 강한 소나기",
            95: "뇌우",
            96: "우박을 동반한 뇌우",
            99: "강한 우박을 동반한 뇌우",
        },
        "en": {
            0: "Clear",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Drizzle",
            55: "Heavy drizzle",
            61: "Light rain",
            63: "Rain",
            65: "Heavy rain",
            71: "Light snow",
            73: "Snow",
            75: "Heavy snow",
            80: "Rain showers",
            81: "Heavy showers",
            82: "Violent showers",
            95: "Thunderstorm",
            96: "Thunderstorm with hail",
            99: "Heavy hail thunderstorm",
        },
        "ja": {
            0: "晴れ", 1: "おおむね晴れ", 2: "一部曇り",
            3: "曇り", 45: "霧", 48: "着氷性の霧",
            51: "弱い霧雨", 53: "霧雨", 55: "強い霧雨",
            61: "弱い雨", 63: "雨", 65: "強い雨",
            71: "弱い雪", 73: "雪", 75: "強い雪",
            80: "にわか雨", 81: "強いにわか雨",
            82: "非常に強いにわか雨", 95: "雷雨",
            96: "ひょうを伴う雷雨", 99: "強いひょうを伴う雷雨",
        },
        "zh": {
            0: "晴朗", 1: "大致晴朗", 2: "局部多云",
            3: "阴天", 45: "雾", 48: "冻雾",
            51: "小毛毛雨", 53: "毛毛雨", 55: "强毛毛雨",
            61: "小雨", 63: "雨", 65: "大雨",
            71: "小雪", 73: "降雪", 75: "大雪",
            80: "阵雨", 81: "强阵雨", 82: "猛烈阵雨",
            95: "雷暴", 96: "伴有冰雹的雷暴",
            99: "强冰雹雷暴",
        },
        "es": {
            0: "Despejado", 1: "Mayormente despejado",
            2: "Parcialmente nublado", 3: "Nublado",
            45: "Niebla", 48: "Niebla con escarcha",
            51: "Llovizna ligera", 53: "Llovizna",
            55: "Llovizna intensa", 61: "Lluvia ligera",
            63: "Lluvia", 65: "Lluvia intensa",
            71: "Nieve ligera", 73: "Nieve", 75: "Nieve intensa",
            80: "Chubascos", 81: "Chubascos fuertes",
            82: "Chubascos muy fuertes", 95: "Tormenta",
            96: "Tormenta con granizo",
            99: "Tormenta fuerte con granizo",
        },
        "fr": {
            0: "Dégagé", 1: "Généralement dégagé",
            2: "Partiellement nuageux", 3: "Couvert",
            45: "Brouillard", 48: "Brouillard givrant",
            51: "Bruine légère", 53: "Bruine",
            55: "Bruine forte", 61: "Pluie faible",
            63: "Pluie", 65: "Pluie forte",
            71: "Neige faible", 73: "Neige", 75: "Neige forte",
            80: "Averses", 81: "Fortes averses",
            82: "Averses très fortes", 95: "Orage",
            96: "Orage avec grêle",
            99: "Fort orage avec grêle",
        },
    }

    try:
        return descriptions.get(language, descriptions["en"]).get(
            int(code), tr("unknown")
        )
    except (TypeError, ValueError):
        return tr("unknown")

def assess_weather(current, visibility):
    """간단한 참고용 표시이며 공식 항공 운항 판단이 아닙니다."""
    code = current.get("weather_code")
    wind = current.get("wind_speed_10m")
    gust = current.get("wind_gusts_10m")
    rain = current.get("precipitation")
    cloud = current.get("cloud_cover")

    severe = False
    caution = False

    try:
        if int(code) in [45, 48, 65, 75, 82, 95, 96, 99]:
            severe = True
        if wind is not None and float(wind) >= 40:
            severe = True
        if gust is not None and float(gust) >= 55:
            severe = True
        if visibility is not None and float(visibility) < 1000:
            severe = True
    except (TypeError, ValueError):
        pass

    try:
        if int(code) in [2, 3, 51, 53, 55, 61, 63, 71, 73, 80, 81]:
            caution = True
        if wind is not None and float(wind) >= 25:
            caution = True
        if gust is not None and float(gust) >= 35:
            caution = True
        if visibility is not None and float(visibility) < 5000:
            caution = True
        if rain is not None and float(rain) > 0:
            caution = True
        if cloud is not None and float(cloud) >= 90:
            caution = True
    except (TypeError, ValueError):
        pass

    if severe:
        return "danger", "🔴"
    if caution:
        return "caution", "🟡"
    return "safe", "🟢"

# -------------------------------
# 디자인
# -------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, #17375e 0, transparent 32%),
            linear-gradient(135deg, #07111f 0%, #0b1729 48%, #101e33 100%);
        color: #edf4ff;
    }

    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    [data-testid="stSidebar"] {
        background-color: #0b1729;
    }

    h1, h2, h3, p, label, span {
        color: #edf4ff;
    }

    .hero {
        padding: 26px 28px;
        border: 1px solid rgba(133, 184, 255, 0.25);
        border-radius: 22px;
        background: linear-gradient(
            120deg,
            rgba(21, 53, 91, 0.92),
            rgba(12, 28, 48, 0.96)
        );
        box-shadow: 0 12px 35px rgba(0,0,0,0.18);
        margin-bottom: 20px;
    }

    .hero-title {
        font-size: 35px;
        font-weight: 800;
        letter-spacing: 3px;
        margin-bottom: 5px;
        color: #ffffff;
    }

    .hero-subtitle {
        color: #a8c8ee;
        font-size: 14px;
    }

    .section-title {
        font-size: 19px;
        font-weight: 700;
        margin: 16px 0 12px 0;
        color: #f3f7ff;
    }

    .metric-card {
        background: rgba(17, 37, 61, 0.88);
        border: 1px solid rgba(119, 171, 231, 0.22);
        border-radius: 16px;
        padding: 17px 18px;
        min-height: 108px;
        margin-bottom: 10px;
    }

    .metric-label {
        color: #9eb8d9;
        font-size: 13px;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #ffffff;
        font-size: 25px;
        font-weight: 750;
        line-height: 1.3;
    }

    .metric-sub {
        color: #92b4db;
        font-size: 12px;
        margin-top: 5px;
    }

    .info-card {
        background: rgba(13, 30, 50, 0.9);
        border: 1px solid rgba(119, 171, 231, 0.18);
        border-radius: 16px;
        padding: 18px;
        margin: 10px 0;
    }

    .disclaimer {
        background: rgba(111, 81, 26, 0.18);
        border: 1px solid rgba(237, 184, 76, 0.35);
        color: #f4d99b;
        border-radius: 12px;
        padding: 13px 15px;
        font-size: 12px;
        line-height: 1.6;
        margin-top: 15px;
    }

    .source-line {
        color: #829ab9;
        font-size: 11px;
        margin-top: 18px;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background-color: #101f33;
        border-color: #2a4668;
        border-radius: 10px;
    }

    div[data-baseweb="select"] span,
    div[data-baseweb="input"] input {
        color: #f1f6ff;
    }

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    .stButton button {
        border-radius: 10px;
        border: 1px solid #416b9c;
        background: #173b63;
        color: white;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------
# 상단 헤더와 언어 선택
# -------------------------------
header_col, language_col = st.columns([5, 1.25], vertical_alignment="center")

with language_col:
    st.selectbox(
        "Language / 언어",
        options=list(LANGUAGES.keys()),
        format_func=lambda code: LANGUAGES[code],
        key="language",
        label_visibility="collapsed",
    )

with header_col:
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-title">✈️ {tr("title")}</div>
            <div class="hero-subtitle">{tr("subtitle")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

lang = st.session_state.language

# -------------------------------
# 공항 데이터 불러오기
# -------------------------------
try:
    with st.spinner(tr("loading")):
        airports = load_airports()
except Exception as error:
    st.error(f"{tr('loading')} ({error})")
    st.stop()

# -------------------------------
# 국가 선택
# -------------------------------
country_codes = sorted(
    airports["iso_country"].dropna().unique().tolist()
)

country_options = {}
for code in country_codes:
    country_options[get_country_name(code, lang)] = code

sorted_country_names = sorted(country_options.keys(), key=str.casefold)

st.markdown(
    f'<div class="section-title">🌍 {tr("country")}</div>',
    unsafe_allow_html=True,
)

selected_country_name = st.selectbox(
    tr("country_search"),
    options=sorted_country_names,
    index=(
        sorted_country_names.index("대한민국")
        if lang == "ko" and "대한민국" in sorted_country_names
        else (
            sorted_country_names.index("South Korea")
            if lang == "en" and "South Korea" in sorted_country_names
            else 0
        )
    ),
)

selected_country_code = country_options[selected_country_name]

country_airports = airports[
    airports["iso_country"] == selected_country_code
].copy()

if country_airports.empty:
    st.warning(tr("no_airports"))
    st.stop()

st.caption(
    f"{tr('airport_count')}: {len(country_airports):,}"
)

# -------------------------------
# 공항 검색
# -------------------------------
st.markdown(
    f'<div class="section-title">🔎 {tr("search")}</div>',
    unsafe_allow_html=True,
)

search_text = st.text_input(
    tr("search"),
    placeholder=tr("search_hint"),
    key="airport_search",
)

filtered = country_airports.copy()
query = search_text.strip().casefold()

if query:
    search_columns = [
        "name",
        "municipality",
        "iata_code",
        "gps_code",
        "ident",
    ]

    mask = pd.Series(False, index=filtered.index)

    for column in search_columns:
        mask |= (
            filtered[column]
            .astype(str)
            .str.casefold()
            .str.contains(query, regex=False, na=False)
        )

    filtered = filtered[mask]

    # 원래 이름이나 코드로 검색되지 않았을 때만
    # 일부 공항 이름을 번역해 추가 검색합니다.
    if filtered.empty and lang != "en":
        localized_matches = []

        # 모든 공항을 번역하지 않고 최대 150개까지만 확인합니다.
        for idx, row in country_airports.head(150).iterrows():
            translated_name = translate_airport_name(
                str(row["name"]), lang
            )
            translated_city = translate_airport_name(
                str(row["municipality"]), lang
            )

            if (
                query in translated_name.casefold()
                or query in translated_city.casefold()
            ):
                localized_matches.append(idx)

        if localized_matches:
            filtered = country_airports.loc[localized_matches].copy()

if filtered.empty:
    st.info(tr("no_match"))
    st.stop()

# 검색 결과가 너무 많으면 우선 최대 100개를 선택 목록에 표시합니다.
filtered = filtered.head(100).copy()

# 선택 목록에 표시할 이름을 현재 언어로 번역합니다.
labels = {}
for idx, row in filtered.iterrows():
    label = make_airport_label(row, lang)

    # 이름이 같더라도 서로 다른 공항을 구분합니다.
    if label in labels:
        label = f"{label} · {row.get('ident', '')}"

    labels[label] = idx

airport_labels = list(labels.keys())

st.markdown(
    f'<div class="section-title">📍 {tr("airport")}</div>',
    unsafe_allow_html=True,
)

selected_label = st.selectbox(
    tr("airport"),
    options=airport_labels,
    key="selected_airport",
)

selected_index = labels[selected_label]
selected_airport = filtered.loc[selected_index]

# -------------------------------
# 공항 기본 정보
# -------------------------------
st.markdown(
    f'<div class="section-title">🛫 {tr("airport_info")}</div>',
    unsafe_allow_html=True,
)

info_cols = st.columns(4)

iata = str(selected_airport.get("iata_code", "") or "").strip()
icao = str(selected_airport.get("gps_code", "") or "").strip()

if not iata or iata.lower() == "nan":
    iata = "—"

if not icao or icao.lower() == "nan":
    icao = "—"

elevation = selected_airport.get("elevation_ft")
try:
    elevation_text = f"{float(elevation):,.0f} ft"
except (TypeError, ValueError):
    elevation_text = tr("unknown")

latitude = selected_airport.get("latitude_deg")
longitude = selected_airport.get("longitude_deg")

info_items = [
    ("IATA", iata),
    ("ICAO", icao),
    (tr("elevation"), elevation_text),
    (
        tr("latitude"),
        f"{float(latitude):.4f}°"
        if pd.notna(latitude)
        else tr("unknown"),
    ),
]

for col, (label, value) in zip(info_cols, info_items):
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="font-size:21px">
                    {value}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -------------------------------
# 현재 날씨
# -------------------------------
st.markdown(
    f'<div class="section-title">🌦️ {tr("weather")}</div>',
    unsafe_allow_html=True,
)

if pd.isna(latitude) or pd.isna(longitude):
    st.warning(tr("weather_error"))
    st.stop()

try:
    with st.spinner(tr("weather")):
        weather = fetch_weather(latitude, longitude)

    current = weather["current"]
    visibility = weather["visibility"]

    status_key, status_icon = assess_weather(current, visibility)

    if status_key == "danger":
        st.error(f"{status_icon} {tr('danger')}")
    elif status_key == "caution":
        st.warning(f"{status_icon} {tr('caution')}")
    else:
        st.success(f"{status_icon} {tr('safe')}")

    code = current.get("weather_code")
    description = weather_description(code, lang)

    st.markdown(
        f"""
        <div class="info-card">
            <div style="font-size:14px;color:#9eb8d9">
                {tr("weather_status")}
            </div>
            <div style="font-size:26px;font-weight:750;margin-top:5px">
                {description}
            </div>
            <div style="color:#9eb8d9;font-size:12px;margin-top:5px">
                {tr("last_updated")}: {current.get("time", tr("unknown"))}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    def display_value(value, unit="", decimals=0):
        try:
            if value is None or pd.isna(value):
                return tr("unknown")
            return f"{float(value):,.{decimals}f}{unit}"
        except (TypeError, ValueError):
            return tr("unknown")

    metric_items = [
        (
            "🌡️",
            tr("temperature"),
            display_value(current.get("temperature_2m"), " °C", 1),
        ),
        (
            "💨",
            tr("wind"),
            display_value(current.get("wind_speed_10m"), " km/h", 1),
        ),
        (
            "🌬️",
            tr("gust"),
            display_value(current.get("wind_gusts_10m"), " km/h", 1),
        ),
        (
            "👁️",
            tr("visibility"),
            display_value(
                float(visibility) / 1000 if visibility is not None else None,
                " km",
                1,
            ),
        ),
        (
            "💧",
            tr("humidity"),
            display_value(current.get("relative_humidity_2m"), "%"),
        ),
        (
            "☁️",
            tr("cloud"),
            display_value(current.get("cloud_cover"), "%"),
        ),
        (
            "🌧️",
            tr("rain"),
            display_value(current.get("precipitation"), " mm", 1),
        ),
        (
            "🌡️",
            tr("feels"),
            display_value(current.get("apparent_temperature"), " °C", 1),
        ),
        (
            "🧭",
            tr("direction"),
            display_value(current.get("wind_direction_10m"), "°"),
        ),
        (
            "📈",
            tr("pressure"),
            display_value(current.get("pressure_msl"), " hPa", 1),
        ),
    ]

    metric_cols = st.columns(4)

    for i, (emoji, label, value) in enumerate(metric_items):
        with metric_cols[i % 4]:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{emoji} {label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        f"""
        <div class="disclaimer">
            ⚠️ <b>{tr("assessment")}</b><br>
            {tr("disclaimer")}<br><br>
            {tr("flight_note")}
        </div>
        """,
        unsafe_allow_html=True,
    )

except Exception:
    st.error(tr("weather_error"))

# -------------------------------
# 지도
# -------------------------------
st.markdown(
    f'<div class="section-title">🗺️ {tr("airport_info")}</div>',
    unsafe_allow_html=True,
)

try:
    map_data = pd.DataFrame(
        {
            "lat": [float(latitude)],
            "lon": [float(longitude)],
        }
    )
    st.map(map_data, zoom=8)
except Exception:
    st.caption(tr("unknown"))

# -------------------------------
# 데이터 출처
# -------------------------------
st.markdown(
    f"""
    <div class="source-line">
        {tr("data_source")}:
        OurAirports · Open-Meteo
    </div>
    """,
    unsafe_allow_html=True,
)
