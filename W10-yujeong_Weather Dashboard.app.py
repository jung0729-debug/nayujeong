import streamlit as st
import requests
from streamlit_folium import st_folium
import folium
import pandas as pd
from datetime import date

# 페이지 설정
st.set_page_config(page_title="Na Yujeong’s Weather Dashboard", page_icon="🌦️", layout="wide")

# 스타일
st.markdown("""
    <style>
        .main { background-color: #f8fafc; font-family: 'Helvetica Neue', sans-serif; }
        h1 { text-align: center; color: #334155; font-weight: 700; }
        .subtitle { text-align: center; color: #64748b; font-size: 1.1em; margin-bottom: 2em; }
    </style>
""", unsafe_allow_html=True)

# 제목
st.markdown("<h1>🌦️ Na Yujeong’s Interactive Weather Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Click on the map and select a date to explore temperature, humidity, wind, and precipitation data.</p>", unsafe_allow_html=True)

# 날짜 선택
st.markdown("### 📅 Select Date")
selected_date = st.date_input("Choose a date:", value=date.today())

# 지도
map_center = [36.5, 127.8]
m = folium.Map(location=map_center, zoom_start=6)
map_data = st_folium(m, width=800, height=500)

# 클릭 시 처리
if map_data and map_data["last_clicked"]:
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    # 지도에 마커 표시
    folium.Marker([lat, lon], popup="Selected Location").add_to(m)

    st.success(f"📍 Location: {lat:.2f}, {lon:.2f}")

    # Open-Meteo API 요청
    api_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
        f"&start_date={selected_date}&end_date={selected_date}"
    )
    res = requests.get(api_url)
    data = res.json()

    if "hourly" in data:
        df = pd.DataFrame({
            "Time": data["hourly"]["time"],
            "Temperature (°C)": data["hourly"]["temperature_2m"],
            "Humidity (%)": data["hourly"]["relative_humidity_2m"],
            "Precipitation (mm)": data["hourly"]["precipitation"],
            "Wind Speed (m/s)": data["hourly"]["wind_speed_10m"]
        })
        df["Time"] = pd.to_datetime(df["Time"])

        # 차트 출력
        st.markdown("### 🌡️ Hourly Weather Data")
        st.line_chart(df.set_index("Time")[["Temperature (°C)", "Humidity (%)", "Wind Speed (m/s)", "Precipitation (mm)"]])

        # 데이터 테이블
        with st.expander("Show Data Table"):
            st.dataframe(df)

        # 주소 표시 (Reverse Geocoding)
        geo_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        geo_res = requests.get(geo_url, headers={"User-Agent": "StreamlitApp"})
        if geo_res.status_code == 200:
            geo_data = geo_res.json()
            address = geo_data.get("display_name", "Address not found")
            st.info(f"📫 **Address:** {address}")
    else:
        st.warning("No data available for this date or location.")
else:
    st.info("Click on the map to load weather data.")
