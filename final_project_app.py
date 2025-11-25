import os
import json
import re       # <- 반드시 필요
import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from io import BytesIO
import numpy as np
from src.met_api import search, get_object
from src.curator import explain_object
from src.viz import plot_year_histogram


# -------------------------------------------
# 국가 데이터 자동 보완 함수
# -------------------------------------------
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
        "China":"China",
        "Thailand":"Thailand",
    }

    culture = obj.get("culture", "")
    if culture in culture_map:
        return culture_map[culture]

    nationality = obj.get("artistNationality", "")
    if nationality in culture_map:
        return culture_map[nationality]

    bio = obj.get("artistDisplayBio", "")
    match = re.search(r"\(([^,]+),", bio)
    if match:
        nat = match.group(1).strip()
        if nat in culture_map:
            return culture_map[nat]

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
        "India":"India",
    }
    if city in city_map:
        return city_map[city]

    return "Unknown"


st.set_page_config(page_title="🎨 AI Museum Curator", layout="wide", initial_sidebar_state="expanded")
st.markdown("<h1 style='text-align:center; color:#FF8C00;'>🎨 AI Museum Curator — Portfolio & Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border:1px solid #bbb;'>", unsafe_allow_html=True)

# Tabs
tab_gallery, tab_dashboard, tab_upload, tab_ai_gen = st.tabs(
    ["🖼 Gallery", "📊 Dashboard", "⬆️ Upload & Color Viz", "🤖 AI Generation"]
)


# ------------------ GALLERY TAB ------------------
# ------------------ GALLERY TAB ------------------
# ------------------ GALLERY TAB ------------------
with tab_gallery:
    st.markdown("### Gallery — The Met + Generated Works")

    with st.sidebar:
        st.markdown("### Search The Met")
        q = st.text_input("Keyword (The Met)", value="Monet")
        cols_num = st.selectbox("Columns", [2,3,4], index=1)
        max_results = st.slider("Max results", 6,36,12,6)
        api_key_input = st.text_input("Your OpenAI API Key (optional)", type="password")

    if q:
        ids = search(q, max_results)
        if not ids:
            st.warning("검색 결과가 없습니다.")
        else:
            metas = [get_object(i) for i in ids[:max_results]]
            cols = st.columns(cols_num)

            # ----------------------
            # Select to Compare
            # ----------------------
            select_options = [f"{m.get('title','Untitled')} — {m.get('artistDisplayName','Unknown')}" for m in metas]
            selected_compare = st.multiselect("Select artworks to compare", options=select_options)

            for i, meta in enumerate(metas):
                with cols[i%cols_num]:
                    img = meta.get("primaryImageSmall") or meta.get("primaryImage")
                    if img:
                        st.image(img, use_column_width=True, caption=f"**{meta.get('title','Untitled')}** — {meta.get('artistDisplayName','Unknown')}")

                    # Curator Note 버튼 (개별 작품)
                    if st.button("Curator Note", key=f"note_{meta.get('objectID')}"):
                        if not api_key_input:
                            st.warning("Please enter your OpenAI API key in the sidebar to generate a curator note.")
                        else:
                            with st.spinner("Generating curator note..."):
                                note = explain_object(meta, api_key=api_key_input)
                                st.markdown("---")
                                st.subheader("Curator Note")
                                st.write(note)

            # ----------------------
            # 선택 작품 비교 및 큐레이터 노트
            # ----------------------
            if selected_compare:
                st.markdown("### 🔍 Selected Artworks Comparison")
                for s in selected_compare:
                    idx = select_options.index(s)
                    m = metas[idx]
                    st.write(f"**{m.get('title','Untitled')} — {m.get('artistDisplayName','Unknown')}**")
                    st.write(f"Date: {m.get('objectDate','Unknown')}, Medium: {m.get('medium','Unknown')}, Country: {derive_country(m)}")
                    img = m.get("primaryImageSmall") or m.get("primaryImage")
                    if img:
                        st.image(img, width=300)

                    # 큐레이터 노트 API 호출
                    if api_key_input:
                        with st.spinner(f"Generating curator note for {m.get('title','Untitled')}..."):
                            note = explain_object(m, api_key=api_key_input, compare_with=selected_compare)
                            st.markdown("**Curator Note:**")
                            st.write(note)
                    else:
                        st.info("Enter OpenAI API key in sidebar to generate curator note.")


# ------------------ DASHBOARD TAB ------------------
with tab_dashboard:
    st.markdown("### Dashboard — Analytics")
    q_dash = st.text_input("Dashboard Keyword (The Met)", value="Monet", key="dash_q")
    n_dash = st.slider("Sample size", 10, 100, 30, key="dash_n")

    if q_dash:
        ids_dash = search(q_dash, n_dash)
        metas_dash = [get_object(i) for i in ids_dash]

        # Histogram
        fig, df = plot_year_histogram(metas_dash)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            if st.checkbox("Show Sample Table"):
                st.dataframe(df.head(10))
        else:
            st.info("연도 데이터가 충분하지 않습니다.")

        # ------------------ DASHBOARD TAB ------------------
# ------------------ AI GENERATION TAB ------------------
tab_ai_gen = st.tabs(["🖼 Gallery", "📊 Dashboard", "⬆️ Upload & Color Viz", "🤖 AI Generation"])[-1]

with tab_ai_gen:
    st.markdown("### Generate AI Images Based on Your Favorite Artwork")
    
    # Step 1: Keyword / Object selection
    fav_keyword = st.text_input("Enter a keyword or artwork title", value="Monet")
    fav_max_results = st.slider("Number of artworks to fetch for preference", 3, 12, 3)
    api_key_ai = st.text_input("Your OpenAI API Key", type="password")
    
    if fav_keyword and api_key_ai:
        # Fetch artworks
        ids_fav = search(fav_keyword, fav_max_results)
        metas_fav = [get_object(i) for i in ids_fav]
        
        st.markdown("#### Select your favorite artwork")
        fav_options = [f"{m.get('title','Untitled')} — {m.get('artistDisplayName','Unknown')}" for m in metas_fav]
        selected_fav = st.selectbox("Choose one", options=fav_options)
        
        if selected_fav:
            idx = fav_options.index(selected_fav)
            fav_art = metas_fav[idx]
            img_url = fav_art.get("primaryImageSmall") or fav_art.get("primaryImage")
            
            if img_url:
                st.image(img_url, width=300, caption=f"**{fav_art.get('title','Untitled')}**")
            
            # Step 2: Generate AI image
            if st.button("Generate Similar AI Image"):
                import openai
                openai.api_key = api_key_ai
                
                with st.spinner("Generating AI image..."):
                    prompt = f"Create an AI-generated image similar in style and content to '{fav_art.get('title','Untitled')}' by {fav_art.get('artistDisplayName','Unknown')}. Focus on the artistic style and composition."
                    
                    response = openai.images.generate(
                        model="gpt-image-1",
                        prompt=prompt,
                        size="1024x1024"
                    )
                    
                    ai_img_url = response.data[0].url
                    st.image(ai_img_url, caption="🎨 AI Generated Image", use_column_width=True)

# ------------------ DASHBOARD TAB ------------------
with tab_dashboard:
    st.markdown("### 📊 Dashboard — Analytics (Country & Medium)")

    # key를 고유하게 변경
    q_dash = st.text_input("Dashboard Keyword (The Met)", value="Monet", key="dashboard_keyword")
    n_dash = st.slider("Sample size", 10,100,30, key="dashboard_sample_size")
    
    if q_dash:
        ids_dash = search(q_dash, n_dash)
        metas_dash = [get_object(i) for i in ids_dash]

        if not metas_dash:
            st.warning("검색 결과가 없습니다.")
        else:
            # 국가 및 재료 정보 보완
            countries = [derive_country(m) for m in metas_dash]
            mediums = [m.get("medium", "Unknown") for m in metas_dash]

            df_meta = pd.DataFrame({
                "country": countries,
                "medium": mediums,
                "title": [m.get("title","Unknown") for m in metas_dash]
            })

            # Country Treemap
            st.markdown("### 🌍 Country Distribution Treemap")
            if df_meta["country"].nunique() > 1:
                fig_country = px.treemap(df_meta, path=['country'], title="Country Treemap")
                st.plotly_chart(fig_country, use_container_width=True)
            else:
                st.info("국가 데이터가 부족합니다.")

            # Medium / Material Treemap
            st.markdown("### 🧵 Medium / Material Treemap")
            if df_meta["medium"].nunique() > 1:
                fig_medium = px.treemap(df_meta, path=['medium'], title="Medium / Material Treemap")
                st.plotly_chart(fig_medium, use_container_width=True)
            else:
                st.info("재료 데이터가 부족합니다.")

            # Optional: Sample Table
            if st.checkbox("Show Sample Table", key="dashboard_sample_table"):
                st.dataframe(df_meta.head(10))



# ------------------ UPLOAD & COLOR VIZ TAB ------------------
with tab_upload:
    st.markdown("### Upload your AI-generated images")
    uploaded = st.file_uploader("Upload PNG/JPG (multiple allowed)", type=["png","jpg","jpeg"], accept_multiple_files=True)
    save_to_catalog = st.checkbox("Save to local catalog", value=False)

    if uploaded:
        api_key_style = st.text_input("OpenAI API Key for AI Style Explanation", type="password")

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

            # ---- (NEW) Basic Image Style Metrics ----
            stat = ImageStat.Stat(img)
            brightness = sum(stat.mean) / 3
            contrast = np.std(np.array(img))
            saturation = np.mean(np.abs(np.array(img) - np.mean(arr)))

            st.markdown("### 📐 Image Style Metrics")
            st.write(f"**Brightness:** {brightness:.2f}")
            st.write(f"**Contrast:** {contrast:.2f}")
            st.write(f"**Saturation:** {saturation:.2f}")

            # ---- (NEW) AI Style Description ----
            if api_key_style and st.button(f"AI Style Description — {f.name}", key=f"ai_desc_{f.name}"):
                import openai
                openai.api_key = api_key_style

                with st.spinner("Analyzing style..."):
                    prompt = f"""
                    You are an art expert. Analyze this image based on brightness {brightness:.2f}, 
                    contrast {contrast:.2f}, and saturation {saturation:.2f}. 
                    Describe its artistic style in 150 words.
                    """

                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    img_bytes = buf.getvalue()

                    response = openai.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are an art curator."},
                            {"role": "user", "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": "data:image/png;base64," + base64.b64encode(img_bytes).decode()}
                            ]}
                        ]
                    )
                    st.write(response.choices[0].message.content)

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
