# final_project_app.py
import os
import io
import json
import streamlit as st
import requests
import numpy as np
import pandas as pd
import plotly.express as px
from PIL import Image
from src.met_api import search, get_object
from src.viz import plot_year_histogram

# --------------------
# Basic page + theme
# --------------------
st.set_page_config(page_title="AI Museum Curator", layout="wide", initial_sidebar_state="expanded")

# Minimal CSS for nicer museum look + masonry
st.markdown(
    """
    <style>
    /* Page background & hero */
    .hero {
        background: linear-gradient(90deg, rgba(14,14,14,1) 0%, rgba(26,18,12,1) 100%);
        color: #f5efe0;
        padding: 40px;
        border-radius: 10px;
        margin-bottom: 18px;
    }
    .hero h1 { font-size: 42px; margin: 0 0 6px 0; color: #F3C874; letter-spacing: 0.5px; }
    .hero p { color: #e6dfd0; margin: 0; font-size: 16px; }

    /* top nav */
    .topnav {
        display:flex;
        justify-content:space-between;
        align-items:center;
        margin-bottom:14px;
    }
    .nav-left {font-weight:700; color:#F3C874; font-size:20px;}
    .nav-right a {color:#ddd; margin-left:18px; text-decoration:none;}
    .nav-right a:hover {color:#F3C874;}

    /* Masonry gallery */
    .masonry { column-count: 3; column-gap: 16px; }
    @media (max-width: 1200px) { .masonry { column-count: 2; } }
    @media (max-width: 760px) { .masonry { column-count: 1; } }

    .card {
        display:inline-block;
        background:#111;
        color:#eee;
        margin:0 0 16px;
        width:100%;
        border-radius:8px;
        overflow:hidden;
        box-shadow: 0 6px 18px rgba(0,0,0,0.6);
        transition: transform .12s ease-in-out;
    }
    .card:hover { transform: translateY(-6px); }
    .card img { width:100%; display:block; }
    .card .meta { padding:10px 12px; font-size:14px; color:#ddd; }
    .card .meta .title { font-weight:700; color:#fff; }
    .badge { background:#2d2d2d; padding:4px 8px; border-radius:4px; font-size:12px; color:#cfc5b0; margin-right:6px; }

    /* small utility */
    .muted { color:#bfb8a7; font-size:13px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Top nav + hero
st.markdown(
    """
    <div class="topnav">
      <div class="nav-left">AI Museum Curator</div>
      <div class="nav-right">
        <a href="#gallery">Gallery</a>
        <a href="#dashboard">Dashboard</a>
        <a href="#about">About</a>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>🎨 AI Museum Curator</h1>
      <p>
        실존 미술관 데이터와 생성 AI 작품을 함께 전시하는 인터랙티브 포트폴리오입니다. 
        전문 큐레이터 해설, 색채 분석, 시계열·주제 대시보드로 예술성과 데이터 역량을 동시에 보여줍니다.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------
# Tabs
# --------------------
tab_gallery, tab_dashboard, tab_about = st.tabs(["🖼 Gallery", "📊 Dashboard", "ℹ️ About"])

# --------------------
# Helper: Curator note via Groq or OpenAI (fallback)
# --------------------
def get_curator_note_from_llm(meta, groq_key=None, openai_key=None):
    """
    Try Groq first if groq_key provided, else OpenAI if openai_key provided.
    Return text or helpful message.
    """
    title = meta.get("title", "Untitled")
    artist = meta.get("artistDisplayName", "Unknown")
    year = meta.get("objectDate", "")
    prompt = (
        f"You are a professional museum curator. Write a polished 150-220 word curator note for an intelligent lay audience.\n\n"
        f"Title: {title}\nArtist: {artist}\nYear: {year}\n\n"
        "Include: brief context, visual analysis (composition, color, technique), interpretive insight, and a viewing tip.\n"
        "Tone: authoritative, evocative, accessible."
    )
    # Groq branch
    if groq_key:
        try:
            # Minimal Groq REST-compatible call (if their SDK not installed)
            url = "https://api.groq.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
            payload = {
                "model": "llama3-70b",
                "messages": [
                    {"role": "system", "content": "You are a professional museum curator."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
            }
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            r.raise_for_status()
            jr = r.json()
            # structure may vary; try common fields
            if "choices" in jr and len(jr["choices"])>0:
                return jr["choices"][0].get("message", {}).get("content") or jr["choices"][0].get("text") or str(jr)
            # fallback stringified
            return str(jr)
        except Exception as e:
            return f"[Groq LLM error] {e}"

    # OpenAI branch
    if openai_key:
        try:
            # use OpenAI REST v1 chat completions
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini" if True else "gpt-4o",
                "messages": [
                    {"role":"system","content":"You are a professional museum curator."},
                    {"role":"user","content":prompt}
                ],
                "temperature":0.3,
                "max_tokens":400
            }
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            r.raise_for_status()
            jr = r.json()
            if "choices" in jr and len(jr["choices"])>0:
                return jr["choices"][0].get("message",{}).get("content") or jr["choices"][0].get("text") or str(jr)
            return str(jr)
        except Exception as e:
            return f"[OpenAI LLM error] {e}"

    # fallback
    return ("OpenAI/Groq API key not found. To enable curator notes, set GROQ_API_KEY or OPENAI_API_KEY "
            "in Streamlit Secrets or type your API key in the sidebar.")

# --------------------
# Helper: color analysis for an image URL
# --------------------
def analyze_image_colors_from_url(url, top_k=6, sample_pixels=4000):
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
    except Exception as e:
        return None, f"Failed to load image: {e}"

    arr = np.array(img).reshape(-1,3)
    if len(arr) > sample_pixels:
        idx = np.random.choice(len(arr), sample_pixels, replace=False)
        arr_s = arr[idx]
    else:
        arr_s = arr

    # simple quantization to find representative colors
    vals = (arr_s // 32).astype(int)  # 8-level quant
    keys, counts = np.unique(vals, axis=0, return_counts=True)
    order = np.argsort(-counts)[:top_k]
    rep = (keys[order] * 32 + 16).clip(0,255)
    palette_hex = [f"#{int(r):02x}{int(g):02x}{int(b):02x}" for r,g,b in rep]
    # stats: mean brightness, saturation proxy
    means = arr_s.mean(axis=0)
    brightness = float(np.mean(means))
    return {"palette": palette_hex, "brightness": brightness, "sample_count": len(arr_s)}, None

# --------------------
# Utility: show detail modal using st.modal
# --------------------
def show_artwork_modal(meta, groq_key=None, openai_key=None):
    title = meta.get("title","Untitled")
    artist = meta.get("artistDisplayName","Unknown")
    year = meta.get("objectDate","")
    img_url = meta.get("primaryImage") or meta.get("primaryImageSmall")
    with st.modal(f"{title} — {artist} ({year})"):
        col1, col2 = st.columns([2,1])
        with col1:
            if img_url:
                st.image(img_url, use_column_width=True)
            else:
                st.info("No high-resolution image available.")
            st.markdown("---")
            st.markdown("**Metadata**")
            md_items = [
                ("Title", meta.get("title")),
                ("Artist", meta.get("artistDisplayName")),
                ("Date", meta.get("objectDate")),
                ("Medium", meta.get("medium")),
                ("Dimensions", meta.get("dimensions")),
                ("Credit Line", meta.get("creditLine")),
                ("Repository", "The Met Museum (Public Domain)" if meta.get("isPublicDomain") else "Check rights")
            ]
            for k,v in md_items:
                if v:
                    st.write(f"**{k}:** {v}")
        with col2:
            st.markdown("### Curator Note")
            # prefer server secrets, allow local typed keys via sidebar
            groq_key_secret = st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") else None
            openai_key_secret = st.secrets.get("OPENAI_API_KEY") if hasattr(st, "secrets") else None
            # also allow user-entered key in session state
            typed_key = st.session_state.get("typed_llm_key", "")
            note = get_curator_note_from_llm(meta, groq_key=groq_key_secret or typed_key, openai_key=openai_key_secret or typed_key)
            st.write(note if note else "No curator note available.")
            st.markdown("---")
            st.markdown("### Color Analysis")
            if img_url:
                stats, err = analyze_image_colors_from_url(img_url)
                if err:
                    st.write(err)
                else:
                    palette = stats["palette"]
                    st.write("Representative palette:")
                    pal_cols = st.columns(len(palette))
                    for i, colhex in enumerate(palette):
                        with pal_cols[i]:
                            st.markdown(f"<div style='width:100%;height:60px;background:{colhex};border-radius:6px'></div>", unsafe_allow_html=True)
                            st.write(f"`{colhex}`")
                    st.write(f"Estimated brightness (0-255): {stats['brightness']:.1f}")
            else:
                st.info("No image to analyze for colors.")

# --------------------
# GALLERY TAB — Masonry gallery implemented via HTML blocks
# --------------------
with tab_gallery:
    st.markdown('<a id="gallery"></a>', unsafe_allow_html=True)
    st.markdown("## Gallery — Real works from The Met (mixed with generated uploads)")
    with st.expander("Search & Options", expanded=True):
        st.write("검색 후 썸네일을 클릭해 상세보기(모달)를 열어보세요.")
        q = st.text_input("Search The Met", value="Monet", key="search_q")
        cols_num = st.selectbox("Columns", [2,3,4], index=1)
        max_results = st.slider("Max results", 6, 30, 12)
        # allow typing a temporary LLM key for this session (not persisted to repo)
        typed_llm_key = st.text_input("Temporary LLM key (optional for curator notes)", type="password",
                                     help="If you don't use Streamlit Secrets, paste a Groq/OpenAI key here for this session.")
        st.session_state["typed_llm_key"] = typed_llm_key

    if q:
        ids = search(q, max_results=max_results)
        if not ids:
            st.warning("검색 결과가 없습니다.")
        else:
            objs = [get_object(i) for i in ids]
            # render masonry via HTML cards
            cards_html = "<div class='masonry'>"
            for meta in objs:
                img = meta.get("primaryImageSmall") or meta.get("primaryImage") or ""
                title = meta.get("title","Untitled")
                artist = meta.get("artistDisplayName","Unknown")
                year = meta.get("objectDate","")
                # card: clicking will create a st.button with unique key - we render image and then a button below via streamlit components
                # For simplicity, render visual card html and also place a Streamlit button underneath it to open modal.
                card = f"""
                  <div class="card">
                    <img src="{img}" alt="{title}">
                    <div class="meta">
                      <div class="title">{title}</div>
                      <div class="muted">{artist} — {year}</div>
                    </div>
                  </div>
                """
                cards_html += card
            cards_html += "</div>"
            st.components.v1.html(cards_html, height=800, scrolling=True)

            # After visual area, place grid of buttons aligned to objects for interactions
            st.markdown("**Actions**")
            grid_cols = st.columns(cols_num)
            for i, meta in enumerate(objs):
                with grid_cols[i % cols_num]:
                    if st.button(f"View • {meta.get('title','Untitled')[:28]}", key=f"view_{meta.get('objectID')}"):
                        show_artwork_modal(meta)

# --------------------
# DASHBOARD TAB
# --------------------
with tab_dashboard:
    st.markdown('<a id="dashboard"></a>', unsafe_allow_html=True)
    st.markdown("## Dashboard — Art analytics & trends")
    with st.expander("Dashboard Controls", expanded=True):
        dash_q = st.text_input("Keyword (for sampling)", value="Monet", key="dash_q_input")
        sample_n = st.slider("Sample size", 10, 80, 30, key="dash_sample")
        show_pca = st.checkbox("Compute color PCA clustering (may take time)", value=False)

    if dash_q:
        ids = search(dash_q, max_results=sample_n)
        metas = [get_object(i) for i in ids]
        fig, df = plot_year_histogram(metas)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            if st.checkbox("Show metadata table", key="show_meta_table"):
                st.dataframe(df)
        else:
            st.info("연도 데이터가 충분하지 않습니다.")

        # optional color PCA clustering
        if show_pca:
            st.markdown("### Color-feature PCA (2D) — sample images color centroids")
            # build simple color centroid per image (mean RGB of sampled pixels)
            rows = []
            for m in metas:
                img_url = m.get("primaryImageSmall") or m.get("primaryImage")
                if not img_url:
                    continue
                try:
                    r = requests.get(img_url, timeout=10)
                    img = Image.open(io.BytesIO(r.content)).convert("RGB")
                    arr = np.array(img).reshape(-1,3)
                    # sample
                    if len(arr) > 2000:
                        idx = np.random.choice(len(arr), 2000, replace=False)
                        arr_s = arr[idx]
                    else:
                        arr_s = arr
                    centroid = arr_s.mean(axis=0)
                    rows.append({"title": m.get("title"), "artist": m.get("artistDisplayName"), 
                                 "r": float(centroid[0]), "g": float(centroid[1]), "b": float(centroid[2])})
                except Exception:
                    continue
            if rows:
                df_c = pd.DataFrame(rows)
                # project rgb -> 2D via PCA (simple SVD)
                X = df_c[["r","g","b"]].to_numpy()
                Xc = X - X.mean(axis=0)
                u, s, vh = np.linalg.svd(Xc, full_matrices=False)
                coords = u[:, :2] * s[:2]
                df_c["x"] = coords[:,0]
                df_c["y"] = coords[:,1]
                fig2 = px.scatter(df_c, x="x", y="y", color="artist", hover_data=["title"])
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("색상 데이터를 얻을 수 있는 이미지가 적습니다.")

# --------------------
# ABOUT TAB
# --------------------
with tab_about:
    st.markdown('<a id="about"></a>', unsafe_allow_html=True)
    st.markdown("## About — Project & Credits")
    st.markdown("""
    **AI Museum Curator**은 The Met Museum Open Access API의 실제 작품 데이터와 사용자가 업로드하거나 생성한 예술 작품을 결합해
    고급스러운 전시 경험을 제공하는 포트폴리오 웹앱입니다.

    **주요 기능**
    - 실제 작품 갤러리(썸네일 → 모달 상세보기)
    - AI 기반 큐레이터 노트 (Groq 또는 OpenAI 사용 가능)
    - 작품 색상 분석 및 대표 팔레트 추출
    - 연도별/작가별 대시보드 및 색상 기반 클러스터링

    **데이터 출처**
    - The Met Museum Collection API (https://collectionapi.metmuseum.org)

    **Tech**
    - Streamlit · Plotly · Pillow · NumPy · Requests

    **개발자**
    - 당신의 이름 (원하면 이 부분 수정해서 넣어드릴게요)
    """)
    st.markdown("---")
    st.markdown("### Quick tips")
    st.write("- 큐레이터 노트를 활성화하려면 Streamlit Secrets에 `GROQ_API_KEY` 또는 `OPENAI_API_KEY` 를 넣어 주세요.")
    st.write("- 일시적으로 테스트하려면 왼쪽의 'Temporary LLM key' 입력란에 키를 붙여넣어도 됩니다 (세션 한정).")

# --------------------
# End
# --------------------
