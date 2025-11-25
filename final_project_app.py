# final integrated streamlit app
# Single-file Streamlit application (integrated, improved UI)
# Features:
# - Sidebar with OpenAI API key input (session + Streamlit Secrets)
# - Gallery (Masonry layout) using The Met API, hover effects, View button opens modal detail
# - Artwork detail modal: large image, metadata, curator AI note (via OpenAI REST), color palette + basic analysis
# - Upload & Color Viz (user images): RGB 3D scatter + representative palette
# - Dashboard: Plotly year distribution, PCA color clustering, interactive filters
# - Theme / CSS for museum-like look

import os
import io
import json
import requests
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from PIL import Image
from src.met_api import search, get_object
from src.viz import plot_year_histogram

# Use uploaded screenshot file as logo if present
LOCAL_LOGO_PATH = "/mnt/data/Screenshot 2025-11-18 at 12.12.02 PM.png"
LOGO_URL = LOCAL_LOGO_PATH if os.path.exists(LOCAL_LOGO_PATH) else None

# --------- App config ---------
st.set_page_config(page_title="AI Museum Curator", layout="wide", initial_sidebar_state="expanded")

# --------- CSS / Theme ---------
st.markdown(
    """
    <style>
    :root{--gold:#CBB26A;--bg:#0D0D0D;--card:#111;--muted:#bfb8a7}
    body { background-color: var(--bg); color: #eee; }
    .topnav{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
    .nav-left {font-weight:700; color:var(--gold); font-size:20px}
    .nav-right a {color:#ddd; margin-left:16px; text-decoration:none}
    .hero{background:linear-gradient(90deg, rgba(14,14,14,1) 0%, rgba(26,18,12,1) 100%);padding:28px;border-radius:8px;margin-bottom:14px}
    .hero h1{font-size:36px;color:var(--gold);margin:0}
    .masonry{column-count:3;column-gap:16px}
    @media (max-width:1200px){.masonry{column-count:2}} @media (max-width:760px){.masonry{column-count:1}}
    .card{display:inline-block;background:var(--card);color:#eee;margin:0 0 16px;width:100%;border-radius:8px;overflow:hidden;box-shadow:0 6px 18px rgba(0,0,0,0.6);}
    .card img{width:100%;display:block}
    .card .meta{padding:10px 12px;font-size:14px;color:#ddd}
    .card .meta .title{font-weight:700;color:#fff}
    .muted{color:var(--muted);font-size:13px}
    .hover-overlay{position:relative}
    .hover-overlay .overlay{position:absolute;left:8px;bottom:8px;background:rgba(0,0,0,0.6);padding:6px 8px;border-radius:6px;color:#fff}
    .btn-small{background:#222;border:1px solid #333;color:#fff;padding:6px 8px;border-radius:6px}
    </style>
    """,
    unsafe_allow_html=True,
)

# --------- Sidebar ---------
st.sidebar.title("Controls & Settings")
st.sidebar.write("OpenAI key (optional) — paste here to enable curator notes for this session.")
# session persistent typed key
if "typed_llm_key" not in st.session_state:
    st.session_state["typed_llm_key"] = ""
st.session_state["typed_llm_key"] = st.sidebar.text_input("OpenAI API Key (session)", type="password", value=st.session_state["typed_llm_key"], help="This key is used only for the current session; or set OPENAI_API_KEY in Streamlit Secrets to keep private.")

# Navigation
nav = st.sidebar.radio("Navigate", ["Home","Gallery","Dashboard","Upload & Color Viz","About"]) 

# --------- Helper: LLM (OpenAI) call via REST ---------
def llm_curator_note(api_key, meta):
    """Call OpenAI chat completion (REST). Returns text or error message."""
    # prefer provided api_key, then session key, then env/secrets
    key = api_key or st.session_state.get("typed_llm_key") or os.getenv("OPENAI_API_KEY")
    if hasattr(st, "secrets") and not key:
        key = st.secrets.get("OPENAI_API_KEY")
    if not key:
        return None
    title = meta.get("title","Untitled")
    artist = meta.get("artistDisplayName","Unknown")
    year = meta.get("objectDate","")
    medium = meta.get("medium","")
    prompt = (
        f"You are a professional museum curator. Write a polished 150-220 word curator note for an intelligent lay audience."
        f"Title": {title}
Artist: {artist}
Year: {year}
Medium: {medium}


        "Include: brief context, visual analysis (composition, color, technique), interpretive insight, and a viewing tip. Tone: authoritative, evocative, accessible."
    )
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {"model":"gpt-4o-mini","messages":[{"role":"system","content":"You are a professional museum curator."},{"role":"user","content":prompt}],"temperature":0.3}
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        jr = r.json()
        if "choices" in jr and len(jr["choices"])>0:
            ch = jr["choices"][0]
            if isinstance(ch.get("message"), dict):
                return ch["message"].get("content")
            return ch.get("text")
        return str(jr)
    except Exception as e:
        return f"LLM request failed: {e}"

# --------- Helper: Color analysis ---------
def analyze_image_from_url(url, top_k=6, sample_pixels=4000):
    try:
        resp = requests.get(url, timeout=20)
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
    vals = (arr_s // 32).astype(int)
    keys, counts = np.unique(vals, axis=0, return_counts=True)
    order = np.argsort(-counts)[:top_k]
    rep = (keys[order]*32 + 16).clip(0,255)
    palette = [f"#{int(r):02x}{int(g):02x}{int(b):02x}" for r,g,b in rep]
    brightness = float(arr_s.mean())
    return {"palette":palette, "brightness":brightness, "sample_count":len(arr_s)}, None

# --------- Helper: Show modal ---------
def show_artwork_modal(meta):
    title = meta.get("title","Untitled")
    artist = meta.get("artistDisplayName","Unknown")
    year = meta.get("objectDate","")
    img_url = meta.get("primaryImage") or meta.get("primaryImageSmall")
    with st.modal(f"{title} — {artist}"):
        c1, c2 = st.columns([2,1])
        with c1:
            if img_url:
                st.image(img_url, use_column_width=True)
            else:
                st.info("No image available for this object.")
            st.markdown("---")
            st.markdown("**Metadata**")
            md = [("Title", meta.get("title")), ("Artist", meta.get("artistDisplayName")), ("Date", meta.get("objectDate")), ("Medium", meta.get("medium")), ("Dimensions", meta.get("dimensions"))]
            for k,v in md:
                if v:
                    st.write(f"**{k}:** {v}")
        with c2:
            st.markdown("### Curator Note")
            # LLM key: prefer typed session key, but sidebar input used system-wide
            note = llm_curator_note(st.session_state.get("typed_llm_key"), meta)
            if note is None:
                st.info("Curator note unavailable. Please provide an OpenAI API key in the sidebar or Streamlit Secrets.")
            else:
                st.write(note)
            st.markdown("---")
            st.markdown("### Color Analysis")
            if img_url:
                stats, err = analyze_image_from_url(img_url)
                if err:
                    st.write(err)
                else:
                    pal = stats["palette"]
                    cols = st.columns(len(pal))
                    for i,colhex in enumerate(pal):
                        with cols[i]:
                            st.markdown(f"<div style='width:100%;height:60px;background:{colhex};border-radius:6px'></div>", unsafe_allow_html=True)
                            st.write(f"`{colhex}`")
                    st.write(f"Estimated brightness: {stats['brightness']:.1f}")
            else:
                st.info("No image to analyze for colors.")

# --------- HOME ---------
if nav == "Home":
    st.markdown("<div class='hero'><h1>🎨 AI Museum Curator</h1><p>Real museum data + AI-generated art — museum-grade curator notes, color analysis, and visual analytics.</p></div>", unsafe_allow_html=True)
    if LOGO_URL:
        try:
            st.image(LOGO_URL, width=220)
        except:
            pass

# --------- GALLERY ---------
if nav == "Gallery":
    st.markdown("## Gallery — The Met Collection")
    with st.expander("Search & options", expanded=True):
        q = st.text_input("Keyword (The Met)", value="Monet", key="search_q")
        cols_num = st.selectbox("Columns", [2,3,4], index=1)
        max_results = st.slider("Max results", 6, 30, 12, key="max_results")
        # allow typing a session LLM key
        st.session_state["typed_llm_key"] = st.text_input("Temporary OpenAI key for this session (optional)", type="password")
    if q:
        ids = search(q, max_results=max_results)
        if not ids:
            st.warning("검색 결과가 없습니다.")
        else:
            metas = [get_object(i) for i in ids]
            # build masonry html
            html = "<div class='masonry'>"
            for m in metas:
                img = m.get("primaryImageSmall") or m.get("primaryImage") or ""
                title = m.get("title","Untitled")
                artist = m.get("artistDisplayName","Unknown")
                year = m.get("objectDate")
                card = f"""
                <div class='card hover-overlay'>
                  <img src='{img}' alt='{title}'>
                  <div class='meta'>
                    <div class='title'>{title}</div>
                    <div class='muted'>{artist} — {year}</div>
                  </div>
                </div>
                """
                html += card
            html += "</div>"
            st.components.v1.html(html, height=800, scrolling=True)
            st.markdown("---")
            st.markdown("**Actions**")
            # buttons for each
            cols = st.columns(cols_num)
            for i,m in enumerate(metas):
                with cols[i%cols_num]:
                    if st.button(f"View • {m.get('title','Untitled')[:28]}", key=f"view_{m.get('objectID')}"):
                        show_artwork_modal(m)

# --------- DASHBOARD ---------
if nav == "Dashboard":
    st.markdown("## Dashboard — Art analytics & trends")
    with st.expander("Controls", expanded=True):
        dash_q = st.text_input("Keyword (sample)", value="Monet", key="dash_q")
        sample_n = st.slider("Sample size", 10, 80, 30, key="dash_n")
        show_pca = st.checkbox("Compute color PCA clustering (may take time)")
    if dash_q:
        ids = search(dash_q, max_results=sample_n)
        metas = [get_object(i) for i in ids]
        fig, df = plot_year_histogram(metas)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            if st.checkbox("Show metadata table", key="meta_table"):
                st.dataframe(df)
        else:
            st.info("연도 데이터가 충분하지 않습니다.")
        if show_pca:
            st.markdown("### Color PCA (2D)")
            rows = []
            for m in metas:
                img_url = m.get("primaryImageSmall") or m.get("primaryImage")
                if not img_url:
                    continue
                try:
                    r = requests.get(img_url, timeout=10)
                    img = Image.open(io.BytesIO(r.content)).convert("RGB")
                    arr = np.array(img).reshape(-1,3)
                    if len(arr) > 2000:
                        idx = np.random.choice(len(arr), 2000, replace=False)
                        arr_s = arr[idx]
                    else:
                        arr_s = arr
                    centroid = arr_s.mean(axis=0)
                    rows.append({"title":m.get('title'), 'artist':m.get('artistDisplayName'), 'r':float(centroid[0]), 'g':float(centroid[1]), 'b':float(centroid[2])})
                except:
                    continue
            if rows:
                dfc = pd.DataFrame(rows)
                X = dfc[["r","g","b"]].to_numpy()
                Xc = X - X.mean(axis=0)
                u,s,vh = np.linalg.svd(Xc, full_matrices=False)
                coords = u[:,:2] * s[:2]
                dfc['x'] = coords[:,0]; dfc['y'] = coords[:,1]
                fig2 = px.scatter(dfc, x='x', y='y', color='artist', hover_data=['title'])
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info('색상 데이터를 얻을 수 있는 이미지가 충분하지 않습니다.')

# --------- UPLOAD & COLOR VIZ ---------
if nav == "Upload & Color Viz":
    st.markdown("## Upload AI-generated images & analyze colors")
    uploaded = st.file_uploader("Upload PNG/JPG", type=["png","jpg","jpeg"], accept_multiple_files=True)
    save_local = st.checkbox("Save uploaded images to local catalog (data/generated_catalog.json)")
    if uploaded:
        for f in uploaded:
            st.markdown(f"### {f.name}")
            try:
                img = Image.open(f).convert('RGB')
            except Exception as e:
                st.error(f"이미지 로드 실패: {e}")
                continue
            st.image(img, use_column_width=True)
            arr = np.array(img).reshape(-1,3)
            sample_n = min(3000, len(arr))
            idx = np.random.choice(len(arr), sample_n, replace=False)
            sample = arr[idx]
            df_rgb = pd.DataFrame({'R':sample[:,0],'G':sample[:,1],'B':sample[:,2]})
            fig = px.scatter_3d(df_rgb, x='R', y='G', z='B', title='Color Distribution (RGB)', opacity=0.7)
            st.plotly_chart(fig, use_container_width=True)
            # representative palette
            vals = (arr//32).astype(int)
            keys, counts = np.unique(vals, axis=0, return_counts=True)
            order = np.argsort(-counts)[:6]
            rep_colors = (keys[order]*32 + 16).clip(0,255)
            palette_hex = [f"#{int(r):02x}{int(g):02x}{int(b):02x}" for r,g,b in rep_colors]
            cols = st.columns(len(palette_hex))
            for i,colhex in enumerate(palette_hex):
                with cols[i]:
                    st.markdown(f"<div style='width:100%;height:80px;background:{colhex};border-radius:6px'></div>", unsafe_allow_html=True)
                    st.write(f"`{colhex}`")
            if save_local:
                os.makedirs('data', exist_ok=True)
                path = os.path.join('data','generated_catalog.json')
                try:
                    with open(path,'r',encoding='utf-8') as g:
                        catalog = json.load(g)
                except:
                    catalog = []
                bio = io.BytesIO(); img.save(bio, format='PNG'); b = bio.getvalue().decode('latin1')
                catalog.append({'title':f.name,'description':'','image_bytes':b})
                with open(path,'w',encoding='utf-8') as g:
                    json.dump(catalog,g, ensure_ascii=False, indent=2)
                st.success('Saved to generated_catalog.json')
    else:
        st.info('Upload images to see color analysis')

# --------- ABOUT ---------
if nav == "About":
    st.markdown("## About this project")
    st.markdown("AI Museum Curator: integration of The Met API, AI curator notes, and visual analytics.

Set your OpenAI key in the sidebar to enable curator notes.")
    st.markdown('
**Credits & Tech**: Streamlit · Plotly · Pillow · NumPy · Requests')

# END
