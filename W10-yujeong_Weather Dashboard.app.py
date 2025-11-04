import streamlit as st
import pydeck as pdk
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="🌎 Global Weather Dashboard by Nayujeong", layout="wide")

st.title("🌍 Global Weather Dashboard by Nayujeong")
st.markdown("Click anywhere on the world map to explore weather by location!")

# 초기 지도 설정 (전세계)
INITIAL_VIEW_STATE = pdk.ViewState(
    latitude=20,
    longitude=0,
    zoom=1.5,
    pitch=0,
)

# 빈 데이터프레임 (클릭 포인트 저장용)
if "points" not in st.session_state:
    st.session_state.points = pd.DataFrame(columns=["lat", "lon"])

# 지도 클릭 이벤트 처리
clicked_point = st.session_state.get("clicked_point")

# pydeck 지도 구성
r = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=INITIAL_VIEW_STATE,
    tooltip={"text": "Click to select a location"},
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=st.session_state.points,
            get_position='[lon, lat]',
            get_color='[255, 0, 0, 200]',
            get_radius=30000,
        )
    ],
)

# 지도 표시
st.pydeck_chart(r)

st.write("🗺️ Clicked Locations:")
st.dataframe(st.session_state.points)

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
