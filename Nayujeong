import streamlit as st
import random, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb

PALETTE_FILE = "palette.csv"

# ---------- 팔레트 관련 함수 ----------
def read_palette():
    return pd.read_csv(PALETTE_FILE)

def load_csv_palette():
    df = read_palette()
    return [(row.r, row.g, row.b) for row in df.itertuples()]

def make_palette(k=6, mode="pastel", base_h=0.60):
    cols = []
    if mode == "csv":
        return load_csv_palette()

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


# ---------- 블롭 생성 ----------
def blob(center=(0.5, 0.5), r=0.3, points=300, wobble=0.25, irregularity=0.6):
    angles = np.linspace(0, 2*math.pi, points, endpoint=False)
    radii = r * (1 + wobble*(np.random.rand(points)-0.5))
    radii *= 1 + irregularity * np.sin(angles*random.uniform(2,6) + random.random()*2*math.pi)
    scale_x = random.uniform(0.7, 1.3)
    scale_y = random.uniform(0.7, 1.3)
    x = center[0] + scale_x * radii * np.cos(angles)
    y = center[1] + scale_y * radii * np.sin(angles)
    return x, y


# ---------- 포스터 그리기 ----------
def draw_poster(n_layers=20, wobble=4.0, palette_mode="pastel", seed=0):
    random.seed(seed); np.random.seed(seed)
    fig, ax = plt.subplots(figsize=(6,8))
    ax.axis('off')
    ax.set_facecolor((0.97,0.97,0.97))

    palette = make_palette(6, mode=palette_mode)
    for _ in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.15, 0.45)
        x, y = blob((cx,cy), r=rr, wobble=wobble)
        color = random.choice(palette)
        alpha = random.uniform(0.3, 0.6)
        ax.fill(x, y, color=color, alpha=alpha, edgecolor=(0,0,0,0))

    ax.text(0.05, 0.95, f"Interactive Poster • {palette_mode}",
            transform=ax.transAxes, fontsize=20, weight="bold")
    return fig


# ---------- Streamlit UI ----------
st.title("🎨 Interactive Poster Generator")

n_layers = st.slider("Layers", 3, 20, 8)
wobble = st.slider("Wobble", 0.01, 9.0, 0.15)
palette_mode = st.selectbox("Palette Mode", ["pastel","vivid","mono","random","csv"])
seed = st.slider("Seed", 0, 9999, 0)

fig = draw_poster(n_layers, wobble, palette_mode, seed)
st.pyplot(fig)
