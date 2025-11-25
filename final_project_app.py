import os, json, re
import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from io import BytesIO
import numpy as np

from src.met_api import search, get_object
from src.curator import explain_object

# ----------------------------------------------------
# 국가 추론 로직 (Met Museum 국가 데이터 부족 해결)
# ----------------------------------------------------
def derive_country(obj):
    if obj.get("country"):
        return obj["country"].strip()

    culture_map = {
        "American": "United States",
        "Korean": "Korea",
        "French": "France",
        "Egyptian": "Egypt",
        "Japanese": "Japan",
        "Chinese": "China",
        "Italian": "Italy",
        "German": "Germany",
        "Indian": "India",
        "Greek": "Greece",
        "British": "United Kingdom",
        "Spanish": "Spain",
    }

    # culture
    culture = obj.get("culture", "")
    if culture in culture_map:
        return culture_map[culture]

    # nationality
    nationality = obj.get("artistNationality", "")
    if nationality in culture_map:
        return culture_map[nationality]

    # bio 패턴
    bio = obj.get("artistDisplayBio", "")
    match = re.search(r"\(([^,]+),", bio)
    if match:
        nat = match.group(1).strip()
        if nat in culture_map:
            return culture_map[nat]

    # city 근사
    city = obj.get("city", "")
    city_map = {
        "New York": "United States",
        "Paris": "France",
        "Seoul": "Korea",
        "Tokyo": "Japan",
        "Cairo": "Egypt",
        "London": "United Kingdom",
        "Kyoto": "Japan",
        "Florence": "Italy",
        "Beijing": "China",
    }
    if city in city_map:
        return city_map[city]

    return "Unknown"


# ----------------------------------------------------
# Upload 이미지 색 추출 함수
# ----------------------------------------------------
def extract_color_palette(image, n_colors=6):
    img = image.resize((200, 200))
    arr = np.array(img)
    pixels = arr.reshape((-1, 3))

    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=n_colors, n_init="auto")
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)

    return ["rgb({},{},{})".format(*c) for c in colors]


# ----------------------------------------------------
# Streamlit UI
# ----------------------------------------------------
st.set_page_config(page_title="AI Museum Curator", layout="wide")
st.title("🖼️ AI Museum Curator – Upgraded Version")

tab1, tab2, tab3, tab4 = st.tabs(
    ["🔍 Search & Curator Note", "🖼 Gallery (확장)", "📊 Dashboard (국가·재료)", "🎨 Upload & Color Viz"]
)

# ----------------------------------------------------
# 1) 검색 + Curator Note
# ----------------------------------------------------
with tab1:
    st.subheader("🔍 작품 검색")
    q = st.text_input("검색어 입력 (예: van gogh, korea, sword 등)")

    if st.button("검색하기", key="search_btn"):
        if not q:
            st.warning("검색어를 입력하세요.")
        else:
            ids = search(q)
            st.success(f"{len(ids)}개 결과 발견됨.")
            if ids:
                obj_id = ids[0]
                obj = get_object(obj_id)

                if obj:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.image(obj.get("primaryImageSmall"), caption=obj.get("title", ""), width=350)

                    with col2:
                        st.markdown(f"### {obj.get('title', 'Unknown')}")
                        st.write(f"Artist: {obj.get('artistDisplayName')}")
                        st.write(f"Year: {obj.get('objectDate')}")

                    st.divider()
                    st.markdown("### 🎤 Curator Note")
                    note = explain_object(obj)
                    st.write(note)

# ----------------------------------------------------
# 2) Gallery 확장 – 2번 옵션 구현
# ----------------------------------------------------
with tab2:
    st.subheader("🖼 Gallery – 작품 2개 비교 확장")

    colA, colB = st.columns(2)

    with colA:
        q1 = st.text_input("왼쪽 작품 검색", key="g1")
        if st.button("검색 1", key="gbtn1"):
            ids1 = search(q1)
            if ids1:
                st.session_state["g1_obj"] = get_object(ids1[0])

        if "g1_obj" in st.session_state:
            obj1 = st.session_state["g1_obj"]
            st.image(obj1.get("primaryImageSmall"), width=300)
            st.write(obj1.get("title"))
            st.write(obj1.get("artistDisplayName"))
            st.write(obj1.get("objectDate"))

    with colB:
        q2 = st.text_input("오른쪽 작품 검색", key="g2")
        if st.button("검색 2", key="gbtn2"):
            ids2 = search(q2)
            if ids2:
                st.session_state["g2_obj"] = get_object(ids2[0])

        if "g2_obj" in st.session_state:
            obj2 = st.session_state["g2_obj"]
            st.image(obj2.get("primaryImageSmall"), width=300)
            st.write(obj2.get("title"))
            st.write(obj2.get("artistDisplayName"))
            st.write(obj2.get("objectDate"))

# ----------------------------------------------------
# 3) Dashboard 확장 – 국가·재료(Material) 트리맵
# ----------------------------------------------------
with tab3:
    st.subheader("📊 Dashboard – 국가별 / 재료별 분석")

    qdash = st.text_input("대시보드용 작품 검색", key="dash")
    if st.button("Search for Dashboard", key="dash_btn"):
        ids = search(qdash)[:80]
        data = []

        for oid in ids:
            obj = get_object(oid)
            if obj:
                country_clean = derive_country(obj)
                material = obj.get("medium", "Unknown")

                data.append({
                    "title": obj.get("title"),
                    "country": country_clean,
                    "material": material,
                })

        df = pd.DataFrame(data)
        st.write(df)

        st.markdown("### 🌍 국가별 Treemap")
        fig1 = px.treemap(df, path=["country"], values=None)
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("### 🧱 재료(Material)별 Treemap")
        fig2 = px.treemap(df, path=["material"], values=None, maxdepth=1)
        st.plotly_chart(fig2, use_container_width=True)

# ----------------------------------------------------
# 4) Upload 확장 – 색상 분석 예시 추가
# ----------------------------------------------------
with tab4:
    st.subheader("🎨 Upload Image + Color Visualization")

    file = st.file_uploader("이미지 업로드", type=["jpg", "png"])

    if file:
        img = Image.open(file).convert("RGB")
        st.image(img, caption="Uploaded Image", width=350)

        st.markdown("### 🎨 주요 색상 추출")
        palette = extract_color_palette(img, n_colors=6)

        cols = st.columns(6)
        for i, c in enumerate(palette):
            with cols[i]:
                st.markdown(
                    f"""
                    <div style='width:60px;height:60px;border-radius:8px;background:{c};border:1px solid #aaa'></div>
                    <p style='font-size:12px'>{c}</p>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("### 📘 예시: 색상 → 감정 분위기 분석 (샘플)")
        st.info("""
- 파랑 계열 → 평온, 안정감  
- 빨강 계열 → 에너지, 긴장감  
- 초록 계열 → 자연, 균형  
        """)

