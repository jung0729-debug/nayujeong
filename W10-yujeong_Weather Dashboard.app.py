import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Na Yujeong's Global Weather Dashboard", page_icon="🌎")

st.title("🌎 Na Yujeong's Global Weather Dashboard")
st.caption("Explore real-time temperature data from anywhere in the world using the Open-Meteo API.")

# 🌍 나라별 주요 도시 좌표 데이터
countries = {
    "South Korea": {
        "Seoul": [37.5665, 126.9780],
        "Busan": [35.1796, 129.0756],
        "Jeju": [33.4996, 126.5312],
        "Incheon": [37.4563, 126.7052],
    },
    "Japan": {
        "Tokyo": [35.6895, 139.6917],
        "Osaka": [34.6937, 135.5023],
        "Sapporo": [43.0618, 141.3545],
        "Fukuoka": [33.5904, 130.4017],
    },
    "United States": {
        "New York": [40.7128, -74.0060],
        "Los Angeles": [34.0522, -118.2437],
        "Chicago": [41.8781, -87.6298],
        "Houston": [29.7604, -95.3698],
    },
    "France": {
        "Paris": [48.8566, 2.3522],
        "Lyon": [45.7640, 4.8357],
        "Marseille": [43.2965, 5.3698],
        "Nice": [43.7102, 7.2620],
    },
    "Australia": {
        "Sydney": [-33.8688, 151.2093],
        "Melbourne": [-37.8136, 144.9631],
        "Brisbane": [-27.4698, 153.0251],
        "Perth": [-31.9505, 115.8605],
    }
}

# 1️⃣ 나라 선택
country = st.selectbox("🌍 Select a Country", list(countries.keys()))

# 2️⃣ 도시 선택
city = st.selectbox("🏙️ Select a City", list(countries[country].keys()))
lat, lon = countries[country][city]

# 지도 표시
st.map(pd.DataFrame([[lat, lon]], columns=["lat", "lon"]))

# 3️⃣ Open-Meteo API 요청
url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m"
data = requests.get(url).json()

temps = data["hourly"]["temperature_2m"]
times = data["hourly"]["time"]

df = pd.DataFrame({
    "Time": times,
    "Temperature (°C)": temps
})

# 4️⃣ 시각화
st.subheader(f"🌡 Hourly Temperature in {city}, {country}")
st.line_chart(df.set_index("Time"))

st.success(f"✅ Successfully loaded weather data for {city}, {country}!")
