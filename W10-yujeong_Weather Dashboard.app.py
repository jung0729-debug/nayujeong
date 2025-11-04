import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Na Yujeong's Weather Dashboard", page_icon="🌤")

st.title("🌤 Na Yujeong's Interactive Weather Dashboard")
st.caption("Select a location to view real-time weather data from Open-Meteo API")

# 기본 위치 데이터 (한국 주요 도시)
locations = {
    "Seoul": [37.5665, 126.9780],
    "Busan": [35.1796, 129.0756],
    "Jeju": [33.4996, 126.5312],
    "Daegu": [35.8714, 128.6014],
    "Incheon": [37.4563, 126.7052],
    "Daejeon": [36.3504, 127.3845]
}

city = st.selectbox("Choose a city:", list(locations.keys()))
lat, lon = locations[city]

# 지도 표시 (streamlit 기본 지도)
st.map(pd.DataFrame([[lat, lon]], columns=["lat", "lon"]))

# Open-Meteo API 호출
url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m"
data = requests.get(url).json()

# 기온 데이터 가져오기
temps = data["hourly"]["temperature_2m"]
times = data["hourly"]["time"]

df = pd.DataFrame({
    "Time": times,
    "Temperature (°C)": temps
})

st.subheader(f"🌡 Hourly Temperature in {city}")
st.line_chart(df.set_index("Time"))

st.success(f"✅ Weather data successfully loaded for {city}!")
