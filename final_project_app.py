# final integrated streamlit app
# ===============================
# Single-file version combining homepage, MET search, curator note, AI art upload,
# and Plotly visualization.

import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import base64
import io

# -------------------------
# MET API Functions
# -------------------------
MET_SEARCH_URL = "https://collectionapi.metmuseum.org/public/collection/v1/search"
MET_OBJECT_URL = "https://collectionapi.metmuseum.org/public/collection/v1/objects/{}"

def met_search(query):
    r = requests.get(MET_SEARCH_URL, params={"q": query})
    if r.status_code != 200:
        return []
    return r.json().get("objectIDs", [])[:20]

def met_object(object_id):
    r = requests.get(MET_OBJECT_URL.format(object_id))
    if r.status_code != 200:
        return None
    return r.json()

# -------------------------
# Curator Note (OpenAI API)
# -------------------------
import openai

def generate_curator_note(api_key, title, artist, period, medium, culture, description):
    if not api_key:
        return "⚠️ API Key not provided. Please enter your OpenAI API Key in the sidebar."

    openai.api_key = api_key

    prompt = f"""
    You are an art museum curator. Write a refined, elegant curator note.
    Title: {title}
    Artist: {artist}
    Period: {period}
    Medium: {medium}
    Culture: {culture}
    Description: {description}
    Style: sophisticated, educational, museum-quality writing.
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {e}"

# -------------------------
# Image → Plotly Histogram
# -------------------------
from PIL import Image

def make_image_histogram(uploaded_img):
    img = Image.open(uploaded_img).convert("RGB")
    df = pd.DataFrame({
        "Red": list(img.getdata(0)),
        "Green": list(img.getdata(1)),
        "Blue": list(img.getdata(2))
    })
    fig = px.histogram(df, x=["Red","Green","Blue"], barmode="overlay", opacity=0.7)
    fig.update_layout(title="Image Color Distribution", template="simple_white")
    return fig

# ===================================================
# STREAMLIT APP
# ===================================================
st.set_page_config(
    page_title="AI Museum Curator Exhibition",
    page_icon="🎨",
    layout="wide",
)

# -------------------------
# Sidebar
# -------------------------
st.sidebar.title("🔧 Controls & Settings")
openai_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

page = st.sidebar.radio(
    "Navigate",
    ["🏛 Home", "🖼 MET Museum Explorer", "🤖 AI Art Upload", "📊 Visualization Dashboard"]
)

# ===================================================
# HOME PAGE
# ===================================================
if page == "🏛 Home":
    st.markdown("""
    <h1 style='text-align:center; font-size:48px;'>AI Museum Curator Exhibition</h1>
    <p style='text-align:center; font-size:20px;'>Where real museum data meets AI-generated art and interactive visualizations.</p>
    <br>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])
    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Metropolitan_Museum_of_Art_%28The_Met%29_Logo.png/800px-Metropolitan_Museum_of_Art_%28The_Met%29_Logo.png", use_column_width=True)
    with col2:
        st.markdown("""
        ### 🌟 Features
        - Search MET Museum artworks
        - Generate museum-quality curator notes using AI
        - Upload & showcase your AI-generated artworks
        - Analyze artworks through Plotly dashboards

        ### 🧩 Tech Stack
        - **Streamlit** (UI / Web App)
        - **OpenAI GPT** (Curator Notes)
        - **Plotly** (Interactive Data Visualization)
        - **Python** (Backend Logic)
        """)

# ===================================================
# MET MUSEUM EXPLORER
# ===================================================
if page == "🖼 MET Museum Explorer":

    st.header("🖼 Explore MET Museum Collection")
    query = st.text_input("Search artworks", "van gogh")

    if st.button("Search MET"):
        ids = met_search(query)
        if not ids:
            st.warning("No artworks found.")
        else:
            for oid in ids:
                art = met_object(oid)
                if not art or not art.get("primaryImageSmall"):
                    continue

                st.image(art["primaryImageSmall"], width=350)
                st.subheader(art.get("title", "Untitled"))
                st.caption(f"Artist: {art.get('artistDisplayName','Unknown')} | Date: {art.get('objectDate','N/A')}")

                with st.expander("📜 Generate Curator Note"):
                    note = generate_curator_note(
                        openai_key,
                        art.get("title",""),
                        art.get("artistDisplayName",""),
                        art.get("period",""),
                        art.get("medium",""),
                        art.get("culture",""),
                        art.get("creditLine","")
                    )
                    st.write(note)

# ===================================================
# AI ART UPLOAD + PLOTLY
# ===================================================
if page == "🤖 AI Art Upload":
    st.header("🤖 Upload Your AI-Generated Artwork")
    uploaded = st.file_uploader("Upload image", type=["png","jpg","jpeg"])

    if uploaded:
        st.image(uploaded, caption="Uploaded Artwork", width=400)

        st.subheader("📊 Color Histogram Analysis")
        fig = make_image_histogram(uploaded)
        st.plotly_chart(fig, use_container_width=True)

# ===================================================
# DASHBOARD PAGE
# ===================================================
if page == "📊 Visualization Dashboard":
    st.header("📊 Artwork Data Visualization Dashboard")

    sample = pd.DataFrame({
        "Year": [1800,1850,1900,1950,2000,2020],
        "Works": [50,120,300,900,1600,2100]
    })

    fig = px.line(sample, x="Year", y="Works", title="Growth of Artworks Over Time", markers=True)
    st.plotly_chart(fig, use_container_width=True)
