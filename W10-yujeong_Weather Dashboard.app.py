import streamlit as st
import requests
import pandas as pd

st.title("📡 간단 날씨 앱 (OpenWeatherMap API 사용)")

# API key 입력 받기
api_key = st.text_input("OpenWeatherMap API Key 입력", type="password")

# 도시명 입력 받기
city = st.text_input("조회할 도시 이름 (예: Seoul, London)")

if st.button("날씨 조회하기"):
    if not api_key:
        st.error("API Key를 입력하세요!")
    elif not city:
        st.error("도시 이름을 입력하세요!")
    else:
        # OpenWeatherMap 현재날씨 API 호출
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            st.subheader(f"{data['name']} ({data['sys']['country']}) 현재 날씨")
            weather = data['weather'][0]
            main = data['main']
            wind = data['wind']

            # 날씨 정보 출력
            st.write(f"🌡️ 온도: {main['temp']}°C")
            st.write(f"❄️ 체감 온도: {main['feels_like']}°C")
            st.write(f"☁️ 날씨: {weather['main']} - {weather['description']}")
            st.write(f"💧 습도: {main['humidity']}%")
            st.write(f"🍃 풍속: {wind['speed']} m/s")
        else:
            st.error("날씨 정보를 가져오는 데 실패했습니다. 도시명과 API 키를 확인하세요.")

