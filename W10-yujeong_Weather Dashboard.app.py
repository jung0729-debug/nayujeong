import streamlit as st
from streamlit_folium import st_folium
import folium
import requests

st.title("🌤️ yujeongNa's Open-Meteo 인터랙티브 날씨 대시보드")
st.markdown("지도를 클릭하거나 주요 도시 버튼을 누르면 해당 위치의 날씨 정보를 불러옵니다.")

# 주요 도시 리스트 (추가 가능)
major_cities = {
    "서울": (37.5665, 126.9780),
    "부산": (35.1796, 129.0756),
    "도쿄": (35.6895, 139.6917),
    "베이징": (39.9042, 116.4074),
    "상하이": (31.2304, 121.4737),
    "뉴욕": (40.7128, -74.0060),
    "런던": (51.5074, -0.1278),
    "파리": (48.8566, 2.3522)
}

# 주요 도시 버튼 UI (좌측 세로 영역)
with st.sidebar:
    st.markdown("### 🌍 주요 도시 바로가기")
    selected_city = None
    for name, (lat, lon) in major_cities.items():
        if st.button(name):
            selected_city = (lat, lon, name)

# 지도 생성
if selected_city:
    m = folium.Map(location=[selected_city[0], selected_city[1]], zoom_start=8)
    folium.Marker([selected_city[0], selected_city[1]], popup=selected_city[2]).add_to(m)
else:
    m = folium.Map(location=[37.57, 126.98], zoom_start=5)
m.add_child(folium.LatLngPopup())  # 클릭한 위치 위도경도 팝업

st_map = st_folium(m, width=700, height=500)

# (1) 주요 도시 버튼 클릭 시
if selected_city:
    lat, lon, name = selected_city
    st.write(f"선택 지역: {name} (위도 {lat:.3f}, 경도 {lon:.3f})")
elif st_map['last_clicked']:
    # (2) 지도에서 직접 위치 클릭 시
    lat = st_map['last_clicked']['lat']
    lon = st_map['last_clicked']['lng']
    st.write(f"선택 지역: 위도 {lat:.3f}, 경도 {lon:.3f}")
else:
    lat, lon = None, None

# 날씨 정보 출력 (위도/경도 존재시)
if lat is not None and lon is not None:
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true"
    )
    resp = requests.get(url).json()
    if "current_weather" in resp:
        cur = resp['current_weather']
        st.metric("기온(°C)", cur['temperature'])
        st.metric("풍속(m/s)", cur['windspeed'])
        st.metric("풍향(°)", cur['winddirection'])
        st.metric("날씨코드", cur['weathercode'])
    else:
        st.write("날씨 데이터를 불러올 수 없습니다.")
else:
    st.info("지도를 클릭하거나 좌측 도시 버튼 중 하나를 클릭하세요.")

