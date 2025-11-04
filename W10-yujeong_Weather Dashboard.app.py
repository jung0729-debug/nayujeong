pip install streamlit folium streamlit-folium requests

import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# 🌏 페이지 기본 설정
st.set_page_config(page_title="Global Weather Dashboard - YuJeong", layout="wide")
st.title("☁️ Global Interactive Weather Dashboard 🌍")
st.write("Click anywhere on the map to view live weather data for that location!")

# 🗺️ 전세계 지도 표시
m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")

# Streamlit에서 Folium 지도 출력
st_data = st_folium(m, width=850, height=500)

# 🌦️ OpenWeatherMap API 키 설정 (★ 본인 키로 교체)
API_KEY = "YOUR_API_KEY"

# 📍 지도 클릭 감지
if st_data and st_data["last_clicked"]:
    lat = st_data["last_clicked"]["lat"]
    lon = st_data["last_clicked"]["lng"]

    # 지도 위 클릭 좌표 표시
    st.success(f"📍 Selected Coordinates: {lat:.4f}, {lon:.4f}")

    # 지도에 마커 추가
    folium.Marker(
        location=[lat, lon],
        popup=f"Selected: {lat:.2f}, {lon:.2f}",
        icon=folium.Icon(color="blue", icon="cloud"),
    ).add_to(m)

    # 🗺️ Reverse Geocoding으로 지역명 확인
    geo_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    geo_res = requests.get(geo_url).json()
    location_name = geo_res.get("display_name", "Unknown location")

    st.write(f"**Location:** {location_name}")

    # ☁️ 날씨 API 요청
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(weather_url)

    if response.status_code == 200:
        data = response.json()

        # 🌡️ 날씨 데이터 표시
        st.subheader(f"Weather near {location_name.split(',')[0]}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌡️ Temperature", f"{data['main']['temp']} °C")
        with col2:
            st.metric("💧 Humidity", f"{data['main']['humidity']} %")
        with col3:
            st.metric("🌬️ Wind Speed", f"{data['wind']['speed']} m/s")

        st.write("**Condition:**", data["weather"][0]["description"].title())
    else:
        st.error("Couldn't fetch weather data 😢")
else:
    st.info("🗺️ Click anywhere on the map to view weather information.")
