import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from PIL import Image
import io
import base64

from groq import Groq   # 🔥 OpenAI → Groq 로 변경

# -----------------------------
# Initialize Groq Client
# -----------------------------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generate_curator_note(title, artist, year):
    prompt = f"""
You are a professional art curator. Provide a sophisticated, elegant, museum-grade analysis of the artwork below.

Title: {title}
Artist: {artist}
Year: {year}

Write in 2–4 paragraphs, focusing on:
- historical context
- artistic techniques
- emotional tone and interpretation
- significance in art history
"""

    response = client.chat.completions.create(
        model="llama3-70b",
        messages=[
            {"role": "system", "content": "You are a professional art curator."},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message["content"]


def generate_ai_art_caption():
    prompt = """
You are an art curator specializing in contemporary AI-generated works.
Write a refined, elegant caption describing this artwork.
"""

    response = client.chat.completions.create(
        model="llama3-70b",
        messages=[
            {"role": "system", "content": "You write elegant museum-style captions."},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message["content"]


# -----------------------------
# MET API FETCH
# -----------------------------
def fetch_random_met_artwork():
    obj_url = "https://collectionapi.metmuseum.org/public/collection/v1/objects"

    all_ids = requests.get(obj_url).json()["objectIDs"]
    import random
    random_id = random.choice(all_ids)

    data = requests.get(f"{obj_url}/{random_id}").json()
    return data


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="AI Art Museum", page_icon="🎨", layout="wide")

st.title("🎨 AI Museum — Curator + AI Art + Analytics")

tab1, tab2, tab3 = st.tabs(["🖼 Explore Artwork", "✨ AI Gallery Upload", "📊 Art Data Visualization"])

# ----------------------------------------------------
# TAB 1 — Explore MET Museum Artwork
# ----------------------------------------------------
with tab1:
    st.header("🖼 Explore Real Museum Artworks (MET)")

    if st.button("Fetch Random Artwork"):
        data = fetch_random_met_artwork()

        title = data.get("title", "Unknown")
        artist = data.get("artistDisplayName", "Unknown Artist")
        year = data.get("objectDate", "Unknown Year")
        img_url = data.get("primaryImageSmall", None)

        st.subheader(f"{title} ({year}) — {artist}")

        if img_url:
            st.image(img_url, use_column_width=True)
        else:
            st.info("No image available.")

        if st.button("Generate Curator Note"):
            with st.spinner("Creating museum-grade analysis..."):
                note = generate_curator_note(title, artist, year)
            st.write(note)


# ----------------------------------------------------
# TAB 2 — AI Gallery Upload
# ----------------------------------------------------
with tab2:
    st.header("✨ Upload Your AI Artwork")

    uploaded_file = st.file_uploader("Upload an AI-generated image", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Artwork", use_column_width=True)

        if st.button("Generate Curator Caption"):
            with st.spinner("Creating caption..."):
                caption = generate_ai_art_caption()
            st.write("### 🖋 Curator Caption")
            st.write(caption)

        # Optional: Color histogram
        if st.button("Generate Color Analysis Chart"):
            img_arr = pd.DataFrame(img.getdata(), columns=["R", "G", "B"])
            fig = px.histogram(img_arr, x=["R", "G", "B"], barmode="group", title="Color Distribution")
            st.plotly_chart(fig)


# ----------------------------------------------------
# TAB 3 — Plotly Dashboard
# ----------------------------------------------------
with tab3:
    st.header("📊 Art Data Visualization")

    sample_data = pd.DataFrame({
        "Artist": ["Monet", "Monet", "Van Gogh", "Van Gogh", "Picasso", "Picasso"],
        "Year": [1880, 1890, 1888, 1890, 1905, 1910],
        "Works": [3, 5, 7, 8, 10, 4],
    })

    fig = px.line(sample_data, x="Year", y="Works", color="Artist", markers=True)
    st.plotly_chart(fig)
