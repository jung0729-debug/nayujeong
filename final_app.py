import streamlit as st
import numpy as np
import random
import math
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb

st.set_page_config(
    page_title="Generative Poster Art Studio", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 컬러 팔레트 CSV 업로드 기능
def read_palette(uploaded_csv):
    df = pd.read_csv(uploaded_csv)
    return [(row.r/255, row.g/255, row.b/255) for row in df.itertuples()]

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

def blob(center=(0.5, 0.5), r=0.3, points=300, wobble=0.25, irregularity=0.6, rotation=0, symmetry=False):
    angles = np.linspace(0, 2*math.pi, points, endpoint=False)
    radii = r * (1 + wobble*(np.random.rand(points)-0.5))
    if symmetry:
        radii = np.abs(np.sin(angles*random.uniform(2,6) + random.random()*2*math.pi)) * r * 1.2
    else:
        radii *= 1 + irregularity * np.sin(angles*random.uniform(2,6) + random.random()*2*math.pi)
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    # rotation (degree)
    if rotation != 0:
        theta = np.radians(rotation)
        x_c, y_c = center
        x_rot = np.cos(theta) * (x - x_c) - np.sin(theta) * (y - y_c) + x_c
        y_rot = np.sin(theta) * (x - x_c) + np.cos(theta) * (y - y_c) + y_c
        x, y = x_rot, y_rot
    return x, y

def show_palette(palette):
    st.write("### Color Palette Preview")
    fig, ax = plt.subplots(figsize=(6,1))
    for i, c in enumerate(palette):
        ax.fill_between([i, i+1], 0, 1, color=c)
    ax.axis("off")
    st.pyplot(fig)
    plt.close()

def draw_poster(
    n_layers, wobble, palette_mode, seed, uploaded_csv_palette,
    bg_color, font_color, n_points, irregularity, radius_min,
    radius_max, palette_len, alpha_min, alpha_max, rotation, symmetry, shape_type):

    random.seed(seed); np.random.seed(seed)
    fig, ax = plt.subplots(figsize=(6,8))
    ax.axis('off')
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    palette = make_palette(palette_len, mode=palette_mode, uploaded_csv=uploaded_csv_palette)
    for _ in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(radius_min, radius_max)
        color = random.choice(palette)
        alpha = random.uniform(alpha_min, alpha_max)
        deg = rotation if rotation else random.uniform(0, 360)
        # shape type 선택
        if shape_type == "blob":
            x, y = blob((cx,cy), r=rr, points=n_points, wobble=wobble, irregularity=irregularity, rotation=deg, symmetry=symmetry)
        elif shape_type == "circle":
            angles = np.linspace(0, 2*np.pi, n_points, endpoint=False)
            x = cx + rr * np.cos(angles)
            y = cy + rr * np.sin(angles)
        elif shape_type == "polygon":
            nsides = random.randint(3,12)
            angles = np.linspace(0, 2*np.pi, nsides, endpoint=False)
            x = cx + rr * np.cos(angles)
            y = cy + rr * np.sin(angles)
        ax.fill(x, y, color=color, alpha=alpha, edgecolor=(0,0,0,0))
    ax.text(0.08, 0.96, "🎨 Gorgeous Interactive Poster", transform=ax.transAxes,
        fontsize=22, weight="bold", color=font_color, fontfamily="monospace")
    ax.text(0.1, 0.91, f"Full Custom Controls", transform=ax.transAxes, fontsize=12, color=font_color)
    st.pyplot(fig)
    plt.close()

# --- 사이드바 전체 컨트롤 ---
st.sidebar.title("🎛️ Poster Controls")

palette_mode = st.sidebar.selectbox("Palette mode", ["pastel","vivid","mono","random","csv"])
uploaded_csv = None
if palette_mode == "csv":
    uploaded = st.sidebar.file_uploader("Upload palette CSV (r,g,b)", type=["csv"])
    uploaded_csv = uploaded if uploaded is not None else None

n_layers = st.sidebar.slider("Layers", 3, 20, 8)
palette_len = st.sidebar.slider("Palette Colors", 3, 12, 6)
n_points = st.sidebar.slider("Blob Points", 30, 600, 220)
wobble = st.sidebar.slider("Wobble", 0.01, 8.0, 1.1, 0.01)
irregularity = st.sidebar.slider("Irregularity", 0.0, 1.5, 0.6, 0.01)
radius_min = st.sidebar.slider("Min Radius", 0.05, 0.4, 0.15, 0.01)
radius_max = st.sidebar.slider("Max Radius", 0.25, 0.9, 0.45, 0.01)
alpha_min = st.sidebar.slider("Min Alpha", 0.1, 0.8, 0.3, 0.01)
alpha_max = st.sidebar.slider("Max Alpha", 0.1, 0.8, 0.6, 0.01)
rotation = st.sidebar.slider("Rotation deg", 0, 360, 0, 5)
symmetry = st.sidebar.checkbox("Enable Symmetry", value=False)
shape_type = st.sidebar.selectbox("Shape Type", ["blob", "circle", "polygon"])
seed = st.sidebar.slider("Seed", 0, 9999, 1234)
bg_color = st.sidebar.color_picker("Background Color", "#181024")
font_color = st.sidebar.color_picker("Font Color", "#FFCCAA")

if uploaded_csv:
    palette = make_palette(palette_len, mode="csv", uploaded_csv=uploaded_csv)
else:
    palette = make_palette(palette_len, mode=palette_mode)

show_palette(palette)

draw_poster(
    n_layers, wobble, palette_mode, seed, uploaded_csv, bg_color, font_color,
    n_points, irregularity, radius_min, radius_max, palette_len,
    alpha_min, alpha_max, rotation, symmetry, shape_type
)
