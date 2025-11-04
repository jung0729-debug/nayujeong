import streamlit as st
import pydeck as pdk
import pandas as pd
import requests

# ---- 기본 설정 ----
st.set_page_config(page_title="🌎 Creative Weather Dashboard by Nayujeong", layout="wide")
st.title("🌍 Creative Global Weather Dashboard by Nayujeong")

# ---- OpenWeather API ----
API_KEY = "YOUR_OPENWEATHER_API_KEY"  # 여기에 실제 API 키 넣기
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# ---- 지도 초기화 ----
INITIAL_VIEW = pdk.ViewState(latitude=20, longitude=0, zoom=1.5)
if "locations" not in st.session_state:
    st.session_state.locations = []

# ---- 애니메이션 함수 ----
def weather_animation(condition):
    if not condition:
        return
    if "snow" in condition.lower():
        snow_html = """
        <div class="snowflakes" aria-hidden="true">
          <div class="snowflake">❄️</div>
          <div class="snowflake">❅</div>
          <div class="snowflake">❆</div>
        </div>
        <style>
        .snowflake {
          position: fixed;
          top: -10px;
          color: white;
          font-size: 1.5em;
          user-select: none;
          animation: fall 10s linear infinite;
        }
        @keyframes fall {
          0% { transform: translateY(0); }
          100% { transform: translateY(100vh); }
        }
        </style>
        """
        st.markdown(snow_html, unsafe_allow_html=True)
    elif "rain" in condition.lower():
        rain_html = """
        <div class="rain">
          <div class="drop"></div><div class="drop"></div><div class="drop"></div>
        </div>
        <style>
        .drop {
          position: fixed;
          width: 2px;
          height: 20px;
          background: rgba(173,216,230,0.6);
          top: -20px;
          animation: rain 1s linear infinite;
        }
        @keyframes rain {
          to { transform: translateY(100vh); }
        }
        </style>
        """
        st.markdown(rain_html, unsafe_allow_html=True)

# ---- 위치 추가 ----
st.sidebar.header("📍 Select a Location")
lat = st.sidebar.number_input("Latitude", value=37.5665, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=126.9780, format="%.4f")

if st.sidebar.button("Add Location"):
    url = f"{BASE_URL}?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        
        # 실패 체크
        if response.status_code != 200 or "main" not in data:
            st.error(f"⚠️ Failed to fetch weather data: {data.get('message', 'Unknown error')}")
        else:
            name = data.get("name", "Unknown")
            temp = data["main"].get("temp", "N/A")
            hum = data["main"].get("humidity", "N/A")
            cond = data.get("weather", [{}])[0].get("description", "N/A")
            
            st.session_state.locations.append({
                "lat": lat,
                "lon": lon,
                "city": name,
                "temp": temp,
                "hum": hum,
                "cond": cond
            })
            st.rerun()
    except Exception as e:
        st.error(f"⚠️ Exception occurred: {e}")

# ---- 지도 표시 ----
if st.session_state.locations:
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

# ---- 날씨 카드 표시 ----
st.subheader("🌤️ Selected Locations")
for loc in st.session_state.locations:
    weather_animation(loc["cond"])
    with st.container():
        st.markdown(
            f"""
            <div style="padding:15px; border-radius:12px; background:#f5f5f5; margin-bottom:10px; box-shadow:2px 2px 8px rgba(0,0,0,0.1)">
                <h3>{loc['city']}</h3>
                <p><b>🌡️ Temperature:</b> {loc['temp']}°C</p>
                <p><b>💧 Humidity:</b> {loc['hum']}%</p>
                <p><b>☁️ Condition:</b> {loc['cond'].title()}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
