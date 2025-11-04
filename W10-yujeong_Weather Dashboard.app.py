import streamlit as st
import pydeck as pdk
import pandas as pd
import requests

# ---------------- 기본 설정 ----------------
st.set_page_config(page_title="🌎 Creative Weather Dashboard by Nayujeong", layout="wide")
st.title("🌍 Creative Global Weather Dashboard by Nayujeong")

API_KEY = "YOUR_OPENWEATHER_API_KEY"  # 👉 OpenWeather 키 입력 필요
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# 사용자가 지도 좌표 입력 (클릭 대신 수동 입력)
st.sidebar.header("📍 Select a Location")
lat = st.sidebar.number_input("Latitude", value=37.5665, format="%.4f")  # 기본 서울
lon = st.sidebar.number_input("Longitude", value=126.9780, format="%.4f")

if st.sidebar.button("Add Location"):
    new_point = pd.DataFrame([[lat, lon]], columns=["lat", "lon"])
    st.session_state.points = pd.concat([st.session_state.points, new_point], ignore_index=True)
    st.experimental_rerun()

# 현재 선택된 위치 표시
if not st.session_state.points.empty:
    st.success(f"✅ Last selected location: ({lat}, {lon})")

# ---------------- 주요 도시 목록 ----------------
major_cities = {
    "Seoul": [37.5665, 126.9780],
    "Tokyo": [35.6895, 139.6917],
    "New York": [40.7128, -74.0060],
    "Paris": [48.8566, 2.3522],
    "London": [51.5074, -0.1278],
    "Sydney": [-33.8688, 151.2093],
    "Toronto": [43.6532, -79.3832],
    "Berlin": [52.5200, 13.4050],
    "Rome": [41.9028, 12.4964],
    "Mexico City": [19.4326, -99.1332],
}

# ---------------- 세션 초기화 ----------------
if "locations" not in st.session_state:
    st.session_state.locations = []

# ---------------- 애니메이션 함수 ----------------
def weather_animation(condition):
    if "snow" in condition.lower():
        snow_html = """
        <div class="snowflakes" aria-hidden="true">
          <div class="snowflake">❄️</div><div class="snowflake">❅</div><div class="snowflake">❆</div>
        </div>
        <style>
        .snowflake {
          position: fixed; top: -10px; color: white; font-size: 1.5em;
          user-select: none; animation: fall 10s linear infinite;
        }
        @keyframes fall { 0% { transform: translateY(0); } 100% { transform: translateY(100vh); } }
        </style>
        """
        st.markdown(snow_html, unsafe_allow_html=True)
    elif "rain" in condition.lower():
        rain_html = """
        <div class="rain"><div class="drop"></div><div class="drop"></div><div class="drop"></div></div>
        <style>
        .drop {
          position: fixed; width: 2px; height: 20px; background: rgba(173,216,230,0.6);
          top: -20px; animation: rain 1s linear infinite;
        }
        @keyframes rain { to { transform: translateY(100vh); } }
        </style>
        """
        st.markdown(rain_html, unsafe_allow_html=True)

# ---------------- 날씨 요청 함수 ----------------
def fetch_weather(lat, lon):
    url = f"{BASE_URL}?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()
    city = data.get("name", "Unknown")
    temp = data["main"]["temp"]
    hum = data["main"]["humidity"]
    cond = data["weather"][0]["description"]
    return {"city": city, "temp": temp, "hum": hum, "cond": cond}

# ---------------- 사이드바: 주요 도시 ----------------
st.sidebar.header("🏙️ Major Cities")
selected_city = st.sidebar.radio("Choose a city:", list(major_cities.keys()))

if st.sidebar.button("Show Weather"):
    lat, lon = major_cities[selected_city]
    info = fetch_weather(lat, lon)
    info["lat"], info["lon"] = lat, lon
    st.session_state.locations.append(info)
    st.rerun()

# ---------------- 지도 표시 ----------------
INITIAL_VIEW = pdk.ViewState(latitude=20, longitude=0, zoom=1.5)
r = pdk.Deck(
    map_style=None,
    initial_view_state=INITIAL_VIEW,
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=pd.DataFrame(st.session_state.locations),
            get_position='[lon, lat]',
            get_color='[255, 0, 0, 200]',
            get_radius=40000,
        )
    ],
)
st.pydeck_chart(r)

# ---------------- 날씨 카드 출력 ----------------
st.subheader("🌤️ Selected Locations")
for loc in st.session_state.locations:
    weather_animation(loc["cond"])
    with st.container():
        st.markdown(
            f"""
            <div style="padding:15px; border-radius:12px; background:#f5f5f5; margin-bottom:10px;
                        box-shadow:2px 2px 8px rgba(0,0,0,0.1)">
                <h3>{loc['city']}</h3>
                <p><b>🌡️ Temperature:</b> {loc['temp']}°C</p>
                <p><b>💧 Humidity:</b> {loc['hum']}%</p>
                <p><b>☁️ Condition:</b> {loc['cond'].title()}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
