
import requests
import pandas as pd
import streamlit as st
import pycountry

from babel import Locale
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(
    page_title="Air Safe | World Airport Weather",
    page_icon="✈️",
    layout="wide"
)

LANGUAGES = {
    "한국어": "ko",
    "English": "en",
    "日本語": "ja",
    "简体中文": "zh",
    "Español": "es",
    "Français": "fr",
}

TEXT = {
    "ko": {
        "title": "항공 기상 안전 시스템",
        "subtitle": "국가별 공항 날씨를 한눈에 확인하세요.",
        "language": "언어 선택",
        "country": "국가 선택",
        "airport_types": "조회할 공항 종류",
        "large": "대형 공항",
        "medium": "중형 공항",
        "small": "소형 공항",
        "limit": "조회할 공항 수",
        "search_button": "🌦️ 공항 날씨 조회",
        "loading": "세계 공항 정보를 불러오는 중...",
        "loading_weather": "공항 날씨를 조회하는 중...",
        "total_airports": "등록된 대상 공항",
        "results": "공항별 날씨 결과",
        "count": "조회된 공항",
        "warnings": "주의 조건 감지 공항",
        "average": "평균 기온",
        "warning_only": "주의 조건이 감지된 공항만 보기",
        "search": "공항명 또는 공항 코드 검색",
        "airport": "공항명",
        "city": "도시",
        "code": "공항 코드",
        "type": "공항 종류",
        "temp": "기온(°C)",
        "weather": "날씨",
        "wind": "풍속(km/h)",
        "gust": "돌풍(km/h)",
        "rain": "강수량(mm)",
        "visibility": "가시거리(km)",
        "advice": "기상 안내",
        "clear": "설정된 주의 조건 없음",
        "wind_warn": "강풍 주의",
        "gust_warn": "돌풍 주의",
        "rain_warn": "강수 확인",
        "vis_warn": "가시거리 주의",
        "fog_warn": "안개",
        "storm_warn": "뇌우",
        "snow_warn": "눈",
        "download": "📥 CSV 다운로드",
        "map": "🗺️ 공항 위치",
        "guide": "항공 안전 참고 사항",
        "guide1": "강풍과 돌풍은 항공기 지상 작업에 영향을 줄 수 있습니다.",
        "guide2": "비와 눈은 활주로 상태와 결빙 가능성 확인에 중요합니다.",
        "guide3": "안개와 낮은 가시거리는 공항의 지상 이동에 영향을 줄 수 있습니다.",
        "guide4": "실제 운항 및 정비 판단은 공식 자료와 관련 규정을 따라야 합니다.",
        "notice": "교육용 참고 프로그램입니다. 이 결과만으로 실제 항공기 운항 가능 여부를 판단할 수 없습니다.",
        "error_airports": "공항 데이터를 불러오지 못했습니다. 인터넷 연결을 확인하세요.",
        "error_weather": "날씨 정보를 가져오지 못했습니다. 잠시 후 다시 시도하세요.",
        "no_airports": "선택한 조건에 해당하는 공항이 없습니다.",
        "no_results": "조회 결과가 없습니다.",
        "kind_large": "대형",
        "kind_medium": "중형",
        "kind_small": "소형",
        "unknown": "정보 없음",
        "no_match": "검색 결과가 없습니다.",
        "limit_note": "공항이 많은 국가는 API 사용량과 응답 시간을 고려해 조회 수를 제한합니다.",
        "success": "날씨 조회 완료",
        "failed_batches": "개 묶음은 조회에 실패했습니다.",
        "country_note": "공항 데이터베이스에 등록된 공항 기준이며, 모든 공항이 포함되는 것은 아닙니다.",
        "weather_section": "현재 기상 정보",
        "project": "프로젝트",
        "source": "공항 데이터: OurAirports | 기상 데이터: Open-Meteo",
    },
    "en": {
        "title": "World Airport Weather System",
        "subtitle": "Explore weather conditions at airports around the world.",
        "language": "Language",
        "country": "Select a country",
        "airport_types": "Airport types",
        "large": "Large airports",
        "medium": "Medium airports",
        "small": "Small airports",
        "limit": "Number of airports to query",
        "search_button": "🌦️ Check Airport Weather",
        "loading": "Loading worldwide airport data...",
        "loading_weather": "Fetching airport weather...",
        "total_airports": "Available airports",
        "results": "Airport Weather Results",
        "count": "Airports queried",
        "warnings": "Airports with warnings",
        "average": "Average temperature",
        "warning_only": "Show airports with warnings only",
        "search": "Search airport name or code",
        "airport": "Airport",
        "city": "City",
        "code": "Airport code",
        "type": "Airport type",
        "temp": "Temp (°C)",
        "weather": "Weather",
        "wind": "Wind (km/h)",
        "gust": "Gust (km/h)",
        "rain": "Precipitation (mm)",
        "visibility": "Visibility (km)",
        "advice": "Weather advisory",
        "clear": "No configured warning conditions detected",
        "wind_warn": "Strong wind",
        "gust_warn": "Strong gusts",
        "rain_warn": "Precipitation",
        "vis_warn": "Low visibility",
        "fog_warn": "Fog",
        "storm_warn": "Thunderstorm",
        "snow_warn": "Snow",
        "download": "📥 Download CSV",
        "map": "🗺️ Airport Locations",
        "guide": "Aviation Safety Notes",
        "guide1": "Strong winds and gusts may affect ground operations.",
        "guide2": "Rain and snow require attention to runway conditions and icing.",
        "guide3": "Fog and low visibility may affect airport ground movement.",
        "guide4": "Actual flight and maintenance decisions must follow official data and regulations.",
        "notice": "Educational tool only. Do not use this result alone to determine flight safety.",
        "error_airports": "Could not load airport data. Check your internet connection.",
        "error_weather": "Could not retrieve weather. Please try again.",
        "no_airports": "No airports match the selected filters.",
        "no_results": "No results found.",
        "kind_large": "Large",
        "kind_medium": "Medium",
        "kind_small": "Small",
        "unknown": "Unavailable",
        "no_match": "No matching airports.",
        "limit_note": "Query limits help manage response time and API usage for countries with many airports.",
        "success": "Weather query complete",
        "failed_batches": " batches failed.",
        "country_note": "Based on airports in the database; not every airport is included.",
        "weather_section": "Current Weather",
        "project": "Project",
        "source": "Airport data: OurAirports | Weather data: Open-Meteo",
    },
    "ja": {
        "title": "世界の空港気象システム",
        "subtitle": "世界各国の空港の天気を確認できます。",
        "language": "言語選択",
        "country": "国を選択",
        "airport_types": "空港の種類",
        "large": "大規模空港",
        "medium": "中規模空港",
        "small": "小規模空港",
        "limit": "取得する空港数",
        "search_button": "🌦️ 空港の天気を確認",
        "loading": "世界の空港データを読み込み中...",
        "loading_weather": "空港の天気を取得中...",
        "total_airports": "対象空港数",
        "results": "空港別の天気",
        "count": "取得した空港",
        "warnings": "注意条件のある空港",
        "average": "平均気温",
        "warning_only": "注意条件のある空港のみ表示",
        "search": "空港名またはコードを検索",
        "airport": "空港名",
        "city": "都市",
        "code": "空港コード",
        "type": "空港の種類",
        "temp": "気温(°C)",
        "weather": "天気",
        "wind": "風速(km/h)",
        "gust": "突風(km/h)",
        "rain": "降水量(mm)",
        "visibility": "視程(km)",
        "advice": "気象注意",
        "clear": "設定された注意条件は検出されませんでした",
        "wind_warn": "強風注意",
        "gust_warn": "突風注意",
        "rain_warn": "降水あり",
        "vis_warn": "視程注意",
        "fog_warn": "霧",
        "storm_warn": "雷雨",
        "snow_warn": "雪",
        "download": "📥 CSVをダウンロード",
        "map": "🗺️ 空港の位置",
        "guide": "航空安全に関する注意",
        "guide1": "強風や突風は地上作業に影響する可能性があります。",
        "guide2": "雨や雪では滑走路の状態や着氷に注意が必要です。",
        "guide3": "霧や視程の低下は空港内の地上移動に影響します。",
        "guide4": "実際の運航・整備判断は公式情報と規則に従ってください。",
        "notice": "学習用ツールです。この結果だけで航空機の運航可否を判断しないでください。",
        "error_airports": "空港データを読み込めません。接続を確認してください。",
        "error_weather": "気象情報を取得できません。再試行してください。",
        "no_airports": "条件に一致する空港がありません。",
        "no_results": "結果がありません。",
        "kind_large": "大規模",
        "kind_medium": "中規模",
        "kind_small": "小規模",
        "unknown": "情報なし",
        "no_match": "一致する空港がありません。",
        "limit_note": "空港数の多い国では、応答時間とAPI利用量を考慮して件数を制限します。",
        "success": "天気の取得が完了しました",
        "failed_batches": "件のグループで取得に失敗しました。",
        "country_note": "データベースに登録された空港が対象です。すべての空港を網羅しているわけではありません。",
        "weather_section": "現在の気象情報",
        "project": "プロジェクト",
        "source": "空港データ: OurAirports | 気象データ: Open-Meteo",
    },
    "zh": {
        "title": "全球机场天气系统",
        "subtitle": "查看世界各地机场的天气情况。",
        "language": "选择语言",
        "country": "选择国家或地区",
        "airport_types": "机场类型",
        "large": "大型机场",
        "medium": "中型机场",
        "small": "小型机场",
        "limit": "查询机场数量",
        "search_button": "🌦️ 查询机场天气",
        "loading": "正在加载全球机场数据...",
        "loading_weather": "正在获取机场天气...",
        "total_airports": "可查询机场",
        "results": "机场天气结果",
        "count": "已查询机场",
        "warnings": "存在注意条件的机场",
        "average": "平均气温",
        "warning_only": "仅显示有注意提示的机场",
        "search": "搜索机场名称或代码",
        "airport": "机场名称",
        "city": "城市",
        "code": "机场代码",
        "type": "机场类型",
        "temp": "气温(°C)",
        "weather": "天气",
        "wind": "风速(km/h)",
        "gust": "阵风(km/h)",
        "rain": "降水量(mm)",
        "visibility": "能见度(km)",
        "advice": "天气提示",
        "clear": "未检测到已设置的注意条件",
        "wind_warn": "强风注意",
        "gust_warn": "阵风注意",
        "rain_warn": "有降水",
        "vis_warn": "能见度注意",
        "fog_warn": "雾",
        "storm_warn": "雷暴",
        "snow_warn": "降雪",
        "download": "📥 下载 CSV",
        "map": "🗺️ 机场位置",
        "guide": "航空安全提示",
        "guide1": "强风和阵风可能影响地面作业。",
        "guide2": "雨雪天气需要注意跑道状况和结冰风险。",
        "guide3": "雾和低能见度可能影响机场地面移动。",
        "guide4": "实际飞行和维修决策必须遵循官方信息和相关规定。",
        "notice": "本程序仅供学习参考。请勿仅凭此结果判断飞机是否可以运行。",
        "error_airports": "无法加载机场数据，请检查网络连接。",
        "error_weather": "无法获取天气信息，请稍后重试。",
        "no_airports": "没有符合条件的机场。",
        "no_results": "没有查询结果。",
        "kind_large": "大型",
        "kind_medium": "中型",
        "kind_small": "小型",
        "unknown": "暂无信息",
        "no_match": "没有匹配的机场。",
        "limit_note": "机场较多的国家会限制查询数量，以控制响应时间和 API 使用量。",
        "success": "天气查询完成",
        "failed_batches": "个数据组查询失败。",
        "country_note": "结果基于数据库中的机场，不保证包含所有机场。",
        "weather_section": "当前天气",
        "project": "项目",
        "source": "机场数据：OurAirports | 天气数据：Open-Meteo",
    },
    "es": {
        "title": "Sistema Meteorológico de Aeropuertos",
        "subtitle": "Consulta el tiempo en aeropuertos de todo el mundo.",
        "language": "Idioma",
        "country": "Seleccionar país",
        "airport_types": "Tipos de aeropuerto",
        "large": "Aeropuertos grandes",
        "medium": "Aeropuertos medianos",
        "small": "Aeropuertos pequeños",
        "limit": "Número de aeropuertos",
        "search_button": "🌦️ Consultar tiempo",
        "loading": "Cargando datos de aeropuertos...",
        "loading_weather": "Consultando el tiempo...",
        "total_airports": "Aeropuertos disponibles",
        "results": "Resultados meteorológicos",
        "count": "Aeropuertos consultados",
        "warnings": "Aeropuertos con alertas",
        "average": "Temperatura media",
        "warning_only": "Mostrar solo aeropuertos con alertas",
        "search": "Buscar nombre o código del aeropuerto",
        "airport": "Aeropuerto",
        "city": "Ciudad",
        "code": "Código",
        "type": "Tipo",
        "temp": "Temp. (°C)",
        "weather": "Tiempo",
        "wind": "Viento (km/h)",
        "gust": "Ráfagas (km/h)",
        "rain": "Precipitación (mm)",
        "visibility": "Visibilidad (km)",
        "advice": "Aviso meteorológico",
        "clear": "No se detectaron las condiciones de alerta configuradas",
        "wind_warn": "Viento fuerte",
        "gust_warn": "Ráfagas fuertes",
        "rain_warn": "Precipitación",
        "vis_warn": "Baja visibilidad",
        "fog_warn": "Niebla",
        "storm_warn": "Tormenta",
        "snow_warn": "Nieve",
        "download": "📥 Descargar CSV",
        "map": "🗺️ Ubicación de aeropuertos",
        "guide": "Notas de seguridad aérea",
        "guide1": "El viento fuerte puede afectar las operaciones en tierra.",
        "guide2": "La lluvia y la nieve requieren atención al estado de la pista y al hielo.",
        "guide3": "La niebla puede afectar los movimientos en tierra.",
        "guide4": "Las decisiones reales deben seguir los datos oficiales y la normativa.",
        "notice": "Herramienta educativa. No determina por sí sola si un vuelo puede operar.",
        "error_airports": "No se pudieron cargar los aeropuertos. Comprueba la conexión.",
        "error_weather": "No se pudo obtener el tiempo. Inténtalo de nuevo.",
        "no_airports": "No hay aeropuertos con estos filtros.",
        "no_results": "No hay resultados.",
        "kind_large": "Grande",
        "kind_medium": "Mediano",
        "kind_small": "Pequeño",
        "unknown": "No disponible",
        "no_match": "No se encontraron aeropuertos.",
        "limit_note": "Los países con muchos aeropuertos tienen límites para gestionar el tiempo y el uso de la API.",
        "success": "Consulta meteorológica completada",
        "failed_batches": " grupos no pudieron consultarse.",
        "country_note": "Se basa en los aeropuertos registrados; no se garantiza una lista completa.",
        "weather_section": "Tiempo actual",
        "project": "Proyecto",
        "source": "Datos de aeropuertos: OurAirports | Tiempo: Open-Meteo",
    },
    "fr": {
        "title": "Météo des aéroports du monde",
        "subtitle": "Consultez la météo des aéroports dans le monde entier.",
        "language": "Langue",
        "country": "Choisir un pays",
        "airport_types": "Types d'aéroports",
        "large": "Grands aéroports",
        "medium": "Aéroports moyens",
        "small": "Petits aéroports",
        "limit": "Nombre d'aéroports à consulter",
        "search_button": "🌦️ Consulter la météo",
        "loading": "Chargement des données aéroportuaires...",
        "loading_weather": "Récupération de la météo...",
        "total_airports": "Aéroports disponibles",
        "results": "Résultats météo des aéroports",
        "count": "Aéroports consultés",
        "warnings": "Aéroports avec alertes",
        "average": "Température moyenne",
        "warning_only": "Afficher uniquement les aéroports avec alertes",
        "search": "Rechercher un nom ou code d'aéroport",
        "airport": "Aéroport",
        "city": "Ville",
        "code": "Code",
        "type": "Type",
        "temp": "Temp. (°C)",
        "weather": "Météo",
        "wind": "Vent (km/h)",
        "gust": "Rafales (km/h)",
        "rain": "Précipitations (mm)",
        "visibility": "Visibilité (km)",
        "advice": "Alerte météo",
        "clear": "Aucune condition d'alerte configurée détectée",
        "wind_warn": "Vent fort",
        "gust_warn": "Fortes rafales",
        "rain_warn": "Précipitations",
        "vis_warn": "Faible visibilité",
        "fog_warn": "Brouillard",
        "storm_warn": "Orage",
        "snow_warn": "Neige",
        "download": "📥 Télécharger CSV",
        "map": "🗺️ Emplacement des aéroports",
        "guide": "Consignes de sécurité aérienne",
        "guide1": "Les vents forts peuvent affecter les opérations au sol.",
        "guide2": "La pluie et la neige nécessitent de vérifier la piste et le risque de givrage.",
        "guide3": "Le brouillard peut affecter les déplacements au sol.",
        "guide4": "Les décisions réelles doivent respecter les données officielles et les règlements.",
        "notice": "Outil éducatif. Ce résultat ne permet pas, à lui seul, de décider si un vol peut être effectué.",
        "error_airports": "Impossible de charger les aéroports. Vérifiez la connexion.",
        "error_weather": "Impossible de récupérer la météo. Réessayez.",
        "no_airports": "Aucun aéroport ne correspond aux filtres.",
        "no_results": "Aucun résultat.",
        "kind_large": "Grand",
        "kind_medium": "Moyen",
        "kind_small": "Petit",
        "unknown": "Indisponible",
        "no_match": "Aucun aéroport correspondant.",
        "limit_note": "Le nombre de requêtes est limité pour les pays ayant de nombreux aéroports.",
        "success": "Consultation météo terminée",
        "failed_batches": " groupes n'ont pas pu être consultés.",
        "country_note": "Basé sur les aéroports enregistrés dans la base de données, qui peut être incomplète.",
        "weather_section": "Météo actuelle",
        "project": "Projet",
        "source": "Données aéroportuaires : OurAirports | Météo : Open-Meteo",
    },
}

WEATHER_NAMES = {
    "ko": {
        0: "맑음", 1: "대체로 맑음", 2: "구름 조금", 3: "흐림",
        45: "안개", 48: "짙은 안개", 51: "약한 이슬비",
        53: "이슬비", 55: "강한 이슬비", 61: "약한 비",
        63: "비", 65: "강한 비", 71: "약한 눈", 73: "눈",
        75: "강한 눈", 80: "소나기", 81: "강한 소나기",
        82: "매우 강한 소나기", 95: "뇌우", 96: "우박 동반 뇌우",
        99: "강한 뇌우",
    },
    "en": {
        0: "Clear", 1: "Mostly clear", 2: "Partly cloudy",
        3: "Overcast", 45: "Fog", 48: "Dense fog",
        51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
        61: "Light rain", 63: "Rain", 65: "Heavy rain",
        71: "Light snow", 73: "Snow", 75: "Heavy snow",
        80: "Rain showers", 81: "Heavy showers", 82: "Violent showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail",
        99: "Severe thunderstorm",
    },
    "ja": {
        0: "晴れ", 1: "おおむね晴れ", 2: "晴れ時々曇り",
        3: "曇り", 45: "霧", 48: "濃霧",
        51: "弱い霧雨", 53: "霧雨", 55: "強い霧雨",
        61: "弱い雨", 63: "雨", 65: "強い雨",
        71: "弱い雪", 73: "雪", 75: "強い雪",
        80: "にわか雨", 81: "強いにわか雨", 82: "激しいにわか雨",
        95: "雷雨", 96: "ひょうを伴う雷雨", 99: "激しい雷雨",
    },
    "zh": {
        0: "晴朗", 1: "大致晴朗", 2: "局部多云", 3: "阴天",
        45: "雾", 48: "浓雾", 51: "小毛毛雨", 53: "毛毛雨",
        55: "强毛毛雨", 61: "小雨", 63: "雨", 65: "大雨",
        71: "小雪", 73: "雪", 75: "大雪", 80: "阵雨",
        81: "强阵雨", 82: "猛烈阵雨", 95: "雷暴",
        96: "伴有冰雹的雷暴", 99: "强雷暴",
    },
    "es": {
        0: "Despejado", 1: "Mayormente despejado",
        2: "Parcialmente nublado", 3: "Nublado",
        45: "Niebla", 48: "Niebla densa", 51: "Llovizna ligera",
        53: "Llovizna", 55: "Llovizna intensa", 61: "Lluvia ligera",
        63: "Lluvia", 65: "Lluvia intensa", 71: "Nieve ligera",
        73: "Nieve", 75: "Nieve intensa", 80: "Chubascos",
        81: "Chubascos fuertes", 82: "Chubascos violentos",
        95: "Tormenta", 96: "Tormenta con granizo",
        99: "Tormenta intensa",
    },
    "fr": {
        0: "Dégagé", 1: "Généralement dégagé",
        2: "Partiellement nuageux", 3: "Couvert",
        45: "Brouillard", 48: "Brouillard dense",
        51: "Bruine légère", 53: "Bruine", 55: "Forte bruine",
        61: "Pluie légère", 63: "Pluie", 65: "Forte pluie",
        71: "Neige légère", 73: "Neige", 75: "Forte neige",
        80: "Averses", 81: "Fortes averses", 82: "Averses violentes",
        95: "Orage", 96: "Orage avec grêle", 99: "Orage violent",
    },
}

AIRPORTS_URL = (
    "https://raw.githubusercontent.com/"
    "davidmegginson/ourairports-data/main/airports.csv"
)
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def tr(key):
    return TEXT[st.session_state.lang][key]


def localized_country(code, lang):
    try:
        loc = Locale.parse(lang)
        name = loc.territories.get(code)
        if name:
            return name
    except Exception:
        pass

    try:
        country = pycountry.countries.get(alpha_2=code)
        return country.name if country else code
    except Exception:
        return code


def country_sort_key(item):
    return item[1].casefold()


@st.cache_data(ttl=86400)
def load_airports():
    response = requests.get(AIRPORTS_URL, timeout=60)
    response.raise_for_status()

    from io import BytesIO

    df = pd.read_csv(BytesIO(response.content), low_memory=False)

    required = [
        "name", "type", "latitude_deg", "longitude_deg",
        "iso_country", "municipality", "ident"
    ]
    df = df[required].copy()

    df = df[
        df["type"].isin([
            "large_airport",
            "medium_airport",
            "small_airport"
        ])
    ]

    df["latitude_deg"] = pd.to_numeric(
        df["latitude_deg"], errors="coerce"
    )
    df["longitude_deg"] = pd.to_numeric(
        df["longitude_deg"], errors="coerce"
    )

    df = df.dropna(
        subset=["latitude_deg", "longitude_deg", "iso_country"]
    )

    return df


@st.cache_data(ttl=600)
def get_weather_batch(rows, lang):
    if not rows:
        return []

    latitudes = [row[2] for row in rows]
    longitudes = [row[3] for row in rows]

    params = {
        "latitude": ",".join(map(str, latitudes)),
        "longitude": ",".join(map(str, longitudes)),
        "current": (
            "temperature_2m,relative_humidity_2m,precipitation,"
            "weather_code,wind_speed_10m,wind_gusts_10m,visibility"
        ),
        "timezone": "UTC"
    }

    response = requests.get(
        WEATHER_URL,
        params=params,
        timeout=45
    )
    response.raise_for_status()

    payload = response.json()
    weather_data = payload if isinstance(payload, list) else [payload]

    results = []

    for row, item in zip(rows, weather_data):
        current = item.get("current", {})
        code = current.get("weather_code")
        wind = current.get("wind_speed_10m")
        gust = current.get("wind_gusts_10m")
        rain = current.get("precipitation")
        visibility = current.get("visibility")

        warnings = []

        if wind is not None and wind >= 30:
            warnings.append(TEXT[lang]["wind_warn"])
        if gust is not None and gust >= 50:
            warnings.append(TEXT[lang]["gust_warn"])
        if rain is not None and rain > 0:
            warnings.append(TEXT[lang]["rain_warn"])
        if visibility is not None and visibility < 5000:
            warnings.append(TEXT[lang]["vis_warn"])
        if code in (45, 48):
            warnings.append(TEXT[lang]["fog_warn"])
        if code in (95, 96, 99):
            warnings.append(TEXT[lang]["storm_warn"])
        if code in (71, 73, 75):
            warnings.append(TEXT[lang]["snow_warn"])

        names = {
            "large_airport": TEXT[lang]["kind_large"],
            "medium_airport": TEXT[lang]["kind_medium"],
            "small_airport": TEXT[lang]["kind_small"],
        }

        results.append({
            "country_code": row[0],
            "country": localized_country(row[0], lang),
            "airport": row[1],
            "city": row[4] or "",
            "code": row[5] or "",
            "type": names.get(row[6], row[6]),
            "temp": current.get("temperature_2m"),
            "weather": WEATHER_NAMES[lang].get(code, TEXT[lang]["unknown"]),
            "wind": wind,
            "gust": gust,
            "rain": rain,
            "visibility": (
                round(visibility / 1000, 1)
                if visibility is not None else None
            ),
            "advice": ", ".join(warnings) if warnings else TEXT[lang]["clear"],
            "latitude": row[2],
            "longitude": row[3],
            "has_warning": bool(warnings),
        })

    return results


# Language selector
if "lang" not in st.session_state:
    st.session_state.lang = "ko"

language_name = st.selectbox(
    "🌐 " + TEXT[st.session_state.lang]["language"],
    list(LANGUAGES.keys()),
    index=list(LANGUAGES.values()).index(st.session_state.lang)
)

new_lang = LANGUAGES[language_name]
if new_lang != st.session_state.lang:
    st.session_state.lang = new_lang
    st.rerun()

lang = st.session_state.lang

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #071426, #102b49, #163c5b);
    color: #f4f8ff;
}
.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
}
h1, h2, h3, p, label {
    color: #f4f8ff !important;
}
.hero {
    background: linear-gradient(120deg, #163e65, #087eaa);
    padding: 28px;
    border-radius: 20px;
    border: 1px solid #397ba7;
    margin-bottom: 22px;
}
.hero h1 {
    font-size: 34px;
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
.info-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(180,220,255,0.2);
    padding: 18px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="hero">
        <h1>✈️ AIR SAFE</h1>
        <h2>{tr("title")}</h2>
        <p>{tr("subtitle")}</p>
    </div>
    """,
    unsafe_allow_html=True
)

try:
    with st.spinner(tr("loading")):
        airports_df = load_airports()
except Exception:
    st.error(tr("error_airports"))
    st.stop()

# Localized country names
country_codes = sorted(
    airports_df["iso_country"].dropna().unique().tolist()
)

country_options = [
    (localized_country(code, lang), code)
    for code in country_codes
]
country_options.sort(key=country_sort_key)

localized_names = [name for name, code in country_options]
country_code_by_name = {
    name: code for name, code in country_options
}

preferred_code = "KR"
default_country_name = next(
    (
        name for name, code in country_options
        if code == preferred_code
    ),
    localized_names[0] if localized_names else ""
)

st.markdown("## 🌍 " + tr("country"))

selected_country_name = st.selectbox(
    tr("country"),
    localized_names,
    index=(
        localized_names.index(default_country_name)
        if default_country_name in localized_names else 0
    ),
    label_visibility="collapsed"
)

selected_country_code = country_code_by_name[selected_country_name]

country_df = airports_df[
    airports_df["iso_country"] == selected_country_code
].copy()

st.markdown("### 🛫 " + tr("airport_types"))

type_labels = {
    tr("large"): "large_airport",
    tr("medium"): "medium_airport",
    tr("small"): "small_airport",
}

selected_type_labels = st.multiselect(
    tr("airport_types"),
    list(type_labels.keys()),
    default=list(type_labels.keys())
)

selected_types = [
    type_labels[label] for label in selected_type_labels
]

country_df = country_df[
    country_df["type"].isin(selected_types)
].copy()

st.info(
    f"{tr('total_airports')}: **{len(country_df):,}**. "
    f"{tr('country_note')}"
)

if country_df.empty:
    st.warning(tr("no_airports"))
    st.stop()

max_limit = min(len(country_df), 2000)

airport_limit = st.slider(
    tr("limit"),
    min_value=1,
    max_value=max_limit,
    value=min(max_limit, 300)
)

st.caption(tr("limit_note"))

if st.button(tr("search_button"), type="primary"):
    target = country_df.head(airport_limit).copy()

    rows = [
        (
            str(row["iso_country"]),
            str(row["name"]),
            float(row["latitude_deg"]),
            float(row["longitude_deg"]),
            str(row["municipality"]) if pd.notna(row["municipality"]) else "",
            str(row["ident"]) if pd.notna(row["ident"]) else "",
            str(row["type"]),
        )
        for _, row in target.iterrows()
    ]

    batches = [
        rows[i:i + 50]
        for i in range(0, len(rows), 50)
    ]

    all_results = []
    failures = 0
    progress = st.progress(0)
    status = st.empty()

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_map = {
            executor.submit(get_weather_batch, tuple(batch), lang): i
            for i, batch in enumerate(batches)
        }

        done = 0

        for future in as_completed(future_map):
            try:
                all_results.extend(future.result())
            except Exception:
                failures += 1

            done += 1
            progress.progress(done / len(batches))
            status.write(f"{done}/{len(batches)}")

    progress.empty()
    status.empty()

    if all_results:
        result_df = pd.DataFrame(all_results)
        result_df = result_df.sort_values(
            "has_warning", ascending=False
        )

        st.session_state.weather_results = result_df
        st.session_state.weather_country_code = selected_country_code
        st.session_state.weather_language = lang

        st.success(
            f"{tr('success')}: {len(result_df):,}"
        )

        if failures:
            st.warning(
                f"{failures}{tr('failed_batches')}"
            )
    else:
        st.error(tr("error_weather"))

if "weather_results" in st.session_state:
    result_df = st.session_state.weather_results.copy()

    # Translate cached result fields again if the user changes language.
    if st.session_state.weather_language != lang:
        st.info(tr("no_results"))
    else:
        st.markdown("---")
        st.markdown("## 📊 " + tr("results"))

        total = len(result_df)
        warning_count = int(result_df["has_warning"].sum())
        average_temp = result_df["temp"].mean()

        c1, c2, c3 = st.columns(3)
        c1.metric(tr("count"), f"{total:,}")
        c2.metric(tr("warnings"), f"{warning_count:,}")
        c3.metric(
            tr("average"),
            f"{average_temp:.1f} °C"
            if pd.notna(average_temp) else tr("unknown")
        )

        show_warnings = st.checkbox(tr("warning_only"))

        display_df = result_df.copy()

        if show_warnings:
            display_df = display_df[
                display_df["has_warning"]
            ]

        search = st.text_input("🔎 " + tr("search"))

        if search:
            mask = (
                display_df["airport"].astype(str).str.contains(
                    search, case=False, na=False
                )
                | display_df["code"].astype(str).str.contains(
                    search, case=False, na=False
                )
                | display_df["city"].astype(str).str.contains(
                    search, case=False, na=False
                )
            )
            display_df = display_df[mask]

        columns = {
            "airport": tr("airport"),
            "city": tr("city"),
            "code": tr("code"),
            "type": tr("type"),
            "temp": tr("temp"),
            "weather": tr("weather"),
            "wind": tr("wind"),
            "gust": tr("gust"),
            "rain": tr("rain"),
            "visibility": tr("visibility"),
            "advice": tr("advice"),
        }

        st.dataframe(
            display_df[list(columns.keys())].rename(columns=columns),
            use_container_width=True,
            hide_index=True
        )

        csv = display_df.rename(columns=columns).to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            tr("download"),
            data=csv,
            file_name="air_safe_weather.csv",
            mime="text/csv"
        )

        st.markdown("### " + tr("map"))

        if not display_df.empty:
            st.map(
                display_df[["latitude", "longitude"]].rename(
                    columns={
                        "latitude": "latitude",
                        "longitude": "longitude"
                    }
                )
            )
        else:
            st.info(tr("no_match"))

st.markdown("---")
st.markdown("### 🔧 " + tr("guide"))

st.markdown(
    f"""
    <div class="info-card">
        <p>• {tr("guide1")}</p>
        <p>• {tr("guide2")}</p>
        <p>• {tr("guide3")}</p>
        <p>• {tr("guide4")}</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(tr("notice"))
st.caption(tr("source"))
st.caption("AIR SAFE | " + tr("project"))
