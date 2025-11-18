import os
import json
from io import BytesIO
from PIL import Image
import streamlit as st
import requests
from src.curator import explain_object  # OpenAI curator note

# -----------------------------
# Met API helpers
# -----------------------------
BASE = "https://collectionapi.metmuseum.org/public/collection/v1"

def search(q, max_results=12):
    resp = requests.get(f"{BASE}/search", params={"q": q, "hasImages": "true"})
    data = resp.json()
    object_ids = data.get("objectIDs", []) or []
    return object_ids[:max_results]

def get_object(object_id):
    resp = requests.get(f"{BASE}/objects/{object_id}")
    return resp.json() if resp.status_code == 200 else {}

# -----------------------------
# Streamlit App
# -----------------------------
st.set_page_config(layout="wide")
st.title("Gallery — The Met + Generated Works")

with st.sidebar:
    st.subheader("Search The Met")
    q = st.text_input("Keyword (The Met)", value="Monet")
    cols_num = st.selectbox("Columns", [2, 3, 4], index=1)
    max_results = st.slider("Max results", min_value=6, max_value=36, value=12, step=6)

# -----------------------------
# The Met Gallery
# -----------------------------
if q:
    ids = search(q, max_results=max_results)
    if not ids:
        st.warning("검색 결과가 없습니다.")
    else:
        metas = [get_object(i) for i in ids]
        cols = st.columns(cols_num)
        for i, meta in enumerate(metas):
            with cols[i % cols_num]:
                img = meta.get("primaryImageSmall") or meta.get("primaryImage")
                if img:
                    st.image(img, use_column_width=True)
                st.markdown(f"**{meta.get('title','Untitled')}**")
                artist = meta.get("artistDisplayName")
                if artist:
                    st.write(artist)
                st.caption(f"ObjectID: {meta.get('objectID')}")
                # Curator Note 버튼
                if st.button("Curator Note", key=f"note_{meta.get('objectID')}"):
                    with st.spinner("Generating curator note..."):
                        note = explain_object(meta)
                        st.markdown("---")
                        st.subheader("Curator Note")
                        st.write(note)

st.markdown("---")
st.write("아래는 업로드된(생성) 작품 섹션입니다.")

# -----------------------------
# Generated Works
# -----------------------------
gen_path = os.path.join("data", "generated_catalog.json")
if os.path.exists(gen_path):
    try:
        with open(gen_path, "r", encoding="utf-8") as f:
            gen = json.load(f)
    except Exception:
        gen = []
else:
    gen = []

if gen:
    cols = st.columns(3)
    for i, item in enumerate(gen):
        with cols[i % 3]:
            img_bytes = BytesIO(bytes(item.get("image_bytes"), "latin1")) if item.get("image_bytes") else None
            if img_bytes:
                try:
                    img = Image.open(img_bytes)
                    st.image(img, use_column_width=True, caption=item.get("title", "Generated"))
                except Exception:
                    st.write("(이미지 로드 실패)")
            st.markdown(f"**{item.get('title','(no title)')}**")
            st.write(item.get("description",""))
