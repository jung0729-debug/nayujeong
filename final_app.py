import streamlit as st
import numpy as np
import random
import math
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
from io import BytesIO

st.set_page_config(
    page_title="Generative Poster Art Studio", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #210046 0%, #231447 100%);
            color: #fff !important;
        }
        .stApp {
            background: linear-gradient(135deg, #210046 0%, #231447 100%) !important;
        }
    </style>
""", unsafe_allow_html=True)

# 컬러 팔레트 CSV 업로더/로더
def read_palette(uploaded_csv):
    df = pd.read_csv(uploaded_csv)
    return [(row.r/255, row.g/255, row.b/255) for row in df.itertuples()]

@st.cache_data
def make_palette(k=6, mode="pastel", base_h=0.60, uploaded_csv=None):
    cols = []
    if mode == "csv" and uploaded_csv:
        return read_palette(uploaded_csv)
    for _ in range(k):
        if mode == "pastel":
            h = random.random(); s = random.uniform(0.15,0.35); v = random.uniform(0.9,1.0)
        elif mode == "vivid":
            h = random.random(); s = random.uniform(0.8,1.0);  v = random.uniform(0.8,1.0)
        elif mode == "mono":
            h = base_h;         s = random.uniform(0.2,0.6);   v = random.uniform(0.5,1.0)
        else: # random
            h = random.random(); s = random.uniform(0.3,1.0); v = random.uniform(0.5,1.0)
        cols.append(tuple(hsv_to_rgb([h,s,v])))
    return cols

def blob(center=(0.5, 0.5), r=0.3, points=300, wobble=0.25, irregularity=0.6):
    angles = np.linspace(0, 2*math.pi, points, endpoint=False)
    radii = r * (1 + wobble*(np.random.rand(points)-0.5))
    radii *= 1 + irregularity * np.sin(angles*random.uniform(2,6) + random.random()*2*math.pi)
    scale_x = random.uniform(0.7, 1.3)
    scale_y = random.uniform(0.7, 1.3)
    x = center[0] + scale_x * radii * np.cos(angles)
    y = center[1] + scale_y * radii * np.sin(angles)
    return x, y

def show_palette(palette):
    st.write("### Color Palette Preview")
    fig, ax = plt.subplots(figsize=(6,1))
    for i, c in enumerate(palette):
        ax.fill_between([i, i+1], 0, 1, color=c)
    ax.axis("off")
    st.pyplot(fig)
    plt.close()

def draw_poster(n_layers, wobble, palette_mode, seed, uploaded_csv_palette=None, bg_color='#181024', font_color='#FFCCAA'):
    random.seed(seed); np.random.seed(seed)
    fig, ax = plt.subplots(figsize=(6,8))
    ax.axis('off')

    # 배경설정
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    palette = make_palette(6, mode=palette_mode, uploaded_csv=uploaded_csv_palette)
    for _ in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.15, 0.45)
        x, y = blob((cx,cy), r=rr, wobble=wobble)
        color = random.choice(palette)
        alpha = random.uniform(0.35, 0.57)
        ax.fill(x, y, color=color, alpha=alpha, edgecolor=(0,0,0,0))
    ax.text(0.08, 0.96, "🎨 Gorgeous Interactive Poster", transform=ax.transAxes,
        fontsize=22, weight="bold", color=font_color, fontfamily="monospace")
    ax.text(0.1, 0.91, f"Palette: {palette_mode.title()}, Layers: {n_layers}", 
        transform=ax.transAxes, fontsize=12, color=font_color)
    st.pyplot(fig)
    plt.close()

# 사이드바 위젯 – 팔레트 업로드, 옵션 등
st.sidebar.title("Poster Controls")
palette_mode = st.sidebar.selectbox("Palette mode", ["pastel","vivid","mono","random","csv"])
uploaded_csv = None
if palette_mode == "csv":
    uploaded = st.sidebar.file_uploader("Upload palette CSV (r,g,b)", type=["csv"])
    uploaded_csv = uploaded if uploaded is not None else None
else:
    uploaded_csv = None

n_layers = st.sidebar.slider("Layers", 3, 20, 8)
wobble = st.sidebar.slider("Wobble", 0.01, 8.0, 1.1, 0.01)
seed = st.sidebar.slider("Seed", 0, 9999, 1234)
bg_color = st.sidebar.color_picker("Background Color", "#181024")
font_color = st.sidebar.color_picker("Font Color", "#FFCCAA")

with st.sidebar:
    st.write("---")
    st.caption("Upload a palette CSV with 'r,g,b' columns for custom color sets.")

if uploaded_csv:
    palette = make_palette(6, mode="csv", uploaded_csv=uploaded_csv)
else:
    palette = make_palette(6, mode=palette_mode)

show_palette(palette)
draw_poster(n_layers, wobble, palette_mode, seed, uploaded_csv, bg_color, font_color)
