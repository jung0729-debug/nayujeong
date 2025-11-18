import os, json
import streamlit as st
from src.met_api import search, get_object
from src.curator import explain_object
from src.viz import plot_year_histogram
from PIL import Image
from io import BytesIO
import numpy as np
import plotly.express as px

st.set_page_config(page_title="🎨 AI Museum Curator", layout="wide", initial_sidebar_state="expanded")
st.markdown("<h1 style='text-align:center; color:#FF8C00;'>🎨 AI Museum Curator — Portfolio & Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border:1px solid #bbb;'>", unsafe_allow_html=True)

# Tabs
tab_gallery, tab_dashboard, tab_upload = st.tabs(["🖼 Gallery", "📊 Dashboard", "⬆️ Upload & Color Viz"])

# ------------------ GALLERY TAB ------------------
with tab_gallery:
    st.markdown("### Gallery — The Met + Generated Works")
    with st.sidebar:
        st.markdown("### Search The Met")
        q = st.text_input("Keyword (The Met)", value="Monet")
        cols_num = st.selectbox("Columns", [2,3,4], index=1)
        max_results = st.slider("Max results", 6,36,12,6)

    if q:
        ids = search(q, max_results)
        if not ids:
            st.warning("검색 결과가 없습니다.")
        else:
            metas = [get_object(i) for i in ids[:max_results]]
            cols = st.columns(cols_num)
            for i, meta in enumerate(metas):
                with cols[i%cols_num]:
                    img = meta.get("primaryImageSmall") or meta.get("primaryImage")
                    if img:
                        st.image(img, use_column_width=True, caption=f"**{meta.get('title','Untitled')}** — {meta.get('artistDisplayName','Unknown')}")
                    if st.button("Curator Note", key=f"note_{meta.get('objectID')}"):
                        with st.spinner("Generating curator note..."):
                            note = explain_object(meta)
                            st.markdown("---")
                            st.subheader("Curator Note")
                            st.write(note)
    st.markdown("---")

    # Generated Works
    st.markdown("### Generated / Uploaded Artworks")
    gen_path = os.path.join("data","generated_catalog.json")
    gen = []
    if os.path.exists(gen_path):
        try:
            with open(gen_path,"r",encoding="utf-8") as f:
                gen = json.load(f)
        except:
            gen = []

    if gen:
        cols = st.columns(3)
        for i,item in enumerate(gen):
            with cols[i%3]:
                img_bytes = BytesIO(bytes(item.get("image_bytes"), "latin1")) if item.get("image_bytes") else None
                if img_bytes:
                    try:
                        img = Image.open(img_bytes)
                        st.image(img, use_column_width=True, caption=f"**{item.get('title','Generated')}**")
                    except:
                        st.write("(이미지 로드 실패)")
                st.write(item.get("description",""))

# ------------------ DASHBOARD TAB ------------------
with tab_dashboard:
    st.markdown("### Dashboard — Analytics")
    q_dash = st.text_input("Dashboard Keyword (The Met)", value="Monet", key="dash_q")
    n_dash = st.slider("Sample size", 10,100,30, key="dash_n")
    if q_dash:
        ids_dash = search(q_dash, n_dash)
        metas_dash = [get_object(i) for i in ids_dash]
        fig, df = plot_year_histogram(metas_dash)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            if st.checkbox("Show Sample Table"):
                st.dataframe(df.head(10))
        else:
            st.info("연도 데이터가 충분하지 않습니다.")

# ------------------ UPLOAD & COLOR VIZ TAB ------------------
with tab_upload:
    st.markdown("### Upload your AI-generated images")
    uploaded = st.file_uploader("Upload PNG/JPG (multiple allowed)", type=["png","jpg","jpeg"], accept_multiple_files=True)
    save_to_catalog = st.checkbox("Save to local catalog", value=False)

    if uploaded:
        for f in uploaded:
            st.markdown(f"#### {f.name}")
            try:
                img = Image.open(f).convert("RGB")
            except:
                st.error("이미지 로드 실패")
                continue
            st.image(img, use_column_width=True)

            arr = np.array(img).reshape(-1,3)
            sample_n = min(3000, len(arr))
            idx = np.random.choice(len(arr), sample_n, replace=False)
            sample = arr[idx]
            df_rgb = {"R": sample[:,0], "G": sample[:,1], "B": sample[:,2]}
            fig = px.scatter_3d(df_rgb, x="R", y="G", z="B", title="Color Distribution (RGB)", opacity=0.7)
            st.plotly_chart(fig, use_container_width=True)

            # Representative palette
            vals = (arr//32).astype(int)
            keys, counts = np.unique(vals, axis=0, return_counts=True)
            order = np.argsort(-counts)[:6]
            rep_colors = (keys[order]*32 +16).clip(0,255)
            palette_hex = [f"#{r:02x}{g:02x}{b:02x}" for r,g,b in rep_colors]
            st.write("Representative Palette:")
            cols = st.columns(len(palette_hex))
            for i,colhex in enumerate(palette_hex):
                with cols[i]:
                    st.markdown(f"<div style='width:100%;height:80px;background:{colhex};border-radius:6px'></div>", unsafe_allow_html=True)
                    st.write(f"`{colhex}`")

            # Save uploaded image
            if save_to_catalog:
                os.makedirs("data", exist_ok=True)
                path = os.path.join("data","generated_catalog.json")
                try:
                    with open(path,"r",encoding="utf-8") as g:
                        catalog = json.load(g)
                except:
                    catalog=[]
                bio = BytesIO()
                img.save(bio, format="PNG")
                b = bio.getvalue().decode("latin1")
                catalog.append({"title":f.name, "description":"","image_bytes":b})
                with open(path,"w",encoding="utf-8") as g:
                    json.dump(catalog,g,ensure_ascii=False, indent=2)
                st.success("Saved to generated_catalog.json")
    else:
        st.info("Upload images to visualize RGB color distribution and palette.")
