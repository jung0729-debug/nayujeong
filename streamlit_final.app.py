import streamlit as st
import random, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb

PALETTE_FILE = "palette.csv"

# ---------- 팔레트 관련 ----------
def read_palette():
    try:
        df = pd.read_csv(PALETTE_FILE)
        if not all(col in df.columns for col in ["r","g","b"]):
            st.warning("CSV에 r,g,b 컬럼이 없습니다. 기본 팔레트를 사용합니다.")
            return None
        return df
    except Exception as e:
        st.warning(f"CSV를 불러오는 중 오류 발생: {e}")
        return None

def load_csv_palette():
    df = read_palette()
    if df is None:
        return [(1,0,0),(0,1,0),(0,0,1)]
    return [(row.r, row.g, row.b) for row in df.itertuples()]

def make_palette(k=6, mode="pastel", base_h=0.60):
    if mode == "csv":
        return load_csv_palette()
    cols = []
    for _ in range(k):
        if mode == "pastel":
            h = random.random(); s = random.uniform(0.15,0.35); v = random.uniform(0.9,1.0)
        elif mode == "vivid":
            h = random.random(); s = random.uniform(0.8,1.0); v = random.uniform(0.8,1.0)
        elif mode == "mono":
            h = base_h; s = random.uniform(0.2,0.6); v = random.uniform(0.5,1.0)
        else:
            h = random.random(); s = random.uniform(0.3,1.0); v = random.uniform(0.5,1.0)
        cols.append(tuple(hsv_to_rgb([h,s,v])))
    return cols

def show_palette(palette):
    st.markdown("**Palette Preview:**")
    cols_html = "".join([f"<div style='width:30px;height:30px;background-color:rgb({int(c[0]*255)},{int(c[1]*255)},{int(c[2]*255)});display:inline-block;margin:2px;border-radius:4px;'></div>" for c in palette])
    st.markdown(cols_html, unsafe_allow_html=True)

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
def draw_poster(n_layers=20, wobble=0.3, irregularity=0.6, palette_mode="pastel", seed=0):
    random.seed(seed); np.random.seed(seed)
    fig, ax = plt.subplots(figsize=(6,8))
    ax.axis('off')
    ax.set_facecolor((0.97,0.97,0.97))
    palette = make_palette(6, mode=palette_mode)
    
    for _ in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.15, 0.45)
        x, y = blob((cx,cy), r=rr, wobble=wobble, irregularity=irregularity)
        color = random.choice(palette)
        alpha = random.uniform(0.3, 0.7)
        ax.fill(x, y, color=color, alpha=alpha, edgecolor=(0,0,0,0))
    
    ax.text(0.05, 0.95, f"Interactive Poster • {palette_mode} Palette",
            transform=ax.transAxes, fontsize=20, weight="bold")
    return fig

# ---------- Streamlit UI ----------
st.title("🎨 Interactive Poster Generator (A+ Version)")

# 팔레트 설정
palette_mode = st.selectbox("Palette Mode", ["pastel","vivid","mono","random","csv"])
palette = make_palette(6, palette_mode)
show_palette(palette)

# 블롭 설정
n_layers = st.slider("Number of Layers", 3, 30, 10)
wobble = st.slider("Wobble (shape distortion)", 0.01, 1.0, 0.2)
irregularity = st.slider("Irregularity (edges)", 0.0, 1.0, 0.5)
seed = st.slider("Random Seed", 0, 9999, 0)

# 포스터 생성
fig = draw_poster(n_layers, wobble, irregularity, palette_mode, seed)
st.pyplot(fig)

# 다운로드 버튼
import io
buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
st.download_button("Download Poster as PNG", buf, file_name=f"poster_{seed}.png", mime="image/png")
