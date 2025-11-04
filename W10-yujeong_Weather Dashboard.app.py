import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Global Weather Map", layout="wide")

st.title("🌎 Global Interactive Weather Map")
st.markdown("Click anywhere on the map or choose a major city from the sidebar!")

# ---- 주요 도시 데이터 ----
major_cities = {
    "Seoul": [37.5665, 126.9780],
    "Tokyo": [35.6895, 139.6917],
    "Beijing": [39.9042, 116.4074],
    "New York": [40.7128, -74.0060],
    "Los Angeles": [34.0522, -118.2437],
    "Paris": [48.8566, 2.3522],
    "London": [51.5074, -0.1278],
    "Berlin": [52.5200, 13.4050],
    "Moscow": [55.7558, 37.6176],
    "Sydney": [-33.8688, 151.2093],
    "Cairo": [30.0444, 31.2357],
    "Mexico City": [19.4326, -99.1332]
}

# ---- 세션 상태 초기화 ----
if "locations" not in st.session_state:
    st.session_state.locations = []

# ---- 사이드바 ----
st.sidebar.header("📍 Major Cities")
selected_city = st.sidebar.selectbox("Choose a city", ["-- Select --"] + list(major_cities.keys()))
if selected_city != "-- Select --":
    lat, lon = major_cities[selected_city]
    st.session_state.locations.append({"name": selected_city, "lat": lat, "lon": lon})
    st.sidebar.success(f"Added {selected_city} to the map!")

# ---- 지도 기본 설정 ----
m = folium.Map(location=[20, 0], zoom_start=2)

# ---- 클릭 이벤트 ----
st.markdown("### 🗺️ Click on the map to add a new location.")
map_data = st_folium(m, width=1200, height=600)

if map_data and map_data["last_clicked"]:
    click = map_data["last_clicked"]
    st.session_state.locations.append({
        "name": f"Custom ({click['lat']:.2f}, {click['lng']:.2f})",
        "lat": click["lat"],
        "lon": click["lng"]
    })
    st.experimental_rerun()

# ---- 저장된 마커 표시 ----
for loc in st.session_state.locations:
    folium.Marker(
        [loc["lat"], loc["lon"]],
        popup=loc["name"],
        tooltip=loc["name"],
        icon=folium.Icon(color="blue", icon="cloud")
    ).add_to(m)

# ---- 업데이트된 지도 렌더 ----
st_data = st_folium(m, width=1200, height=600)

# ---- 현재 저장된 도시 목록 표시 ----
if st.session_state.locations:
    st.sidebar.markdown("### 📍 Added Locations")
    for loc in st.session_state.locations:
        st.sidebar.write(f"- {loc['name']} ({loc['lat']:.2f}, {loc['lon']:.2f})")
