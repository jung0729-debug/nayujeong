import streamlit as st
import requests

# 🌸 페이지 기본 설정
st.set_page_config(page_title="Na Yujeong's MET Art Explorer", page_icon="🎨", layout="wide")

# 🌈 스타일 커스터마이징 (CSS)
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
            font-family: 'Helvetica Neue', sans-serif;
        }
        h1 {
            text-align: center;
            color: #3b3b3b;
            font-weight: 700;
            margin-bottom: 0.2em;
        }
        .subtitle {
            text-align: center;
            color: #6c757d;
            font-size: 1.1em;
            margin-bottom: 2em;
        }
        .art-card {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .footer {
            text-align: center;
            margin-top: 3em;
            color: #8a8a8a;
            font-size: 0.9em;
        }
    </style>
""", unsafe_allow_html=True)

# 🎨 제목 영역
st.markdown("<h1>🎨 Na Yujeong's MET Art Explorer</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Explore beautiful artworks from The Metropolitan Museum of Art API</p>", unsafe_allow_html=True)

# 🔍 검색 입력
query = st.text_input("Search for Artworks:", "flower")

if query:
    search_url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={query}"
    search_response = requests.get(search_url).json()

    if search_response.get("total", 0) > 0:
        # 최대 4개 결과만 보여주기
        ids = search_response["objectIDs"][:4]

        cols = st.columns(2)
        for idx, object_id in enumerate(ids):
            object_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
            object_data = requests.get(object_url).json()

            with cols[idx % 2]:
                st.markdown("<div class='art-card'>", unsafe_allow_html=True)
                st.subheader(object_data.get("title", "Untitled"))

                if object_data.get("primaryImageSmall"):
                    st.image(object_data["primaryImageSmall"], use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x300?text=No+Image", use_container_width=True)

                st.write(f"**Artist:** {object_data.get('artistDisplayName', 'Unknown')}")
                st.write(f"**Year:** {object_data.get('objectDate', 'N/A')}")
                st.write(f"**Culture:** {object_data.get('culture', 'N/A')}")
                st.write(f"**Department:** {object_data.get('department', 'N/A')}")
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("No artworks found for that keyword.")

# ❤️ 푸터
st.markdown("<p class='footer'>Made with ❤️ by Na Yujeong</p>", unsafe_allow_html=True)
