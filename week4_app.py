# streamlit_abstract.py
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# -------------------------------
# 팔레트
# -------------------------------
def get_palette(style="Zen", n=8, seed=None):
    if seed is not None:
        np.random.seed(seed)
    if style == "Zen":
        return [(0.7, 0.6, 0.9), (0.9, 0.8, 0.95), (0.8, 0.7, 0.85)]
    elif style == "Party":
        return [tuple(np.random.rand(3)) for _ in range(n)]
    elif style == "Glitch":
        return [(np.random.rand(), np.random.rand()*0.5, np.random.rand()) for _ in range(n)]
    else:
        return [tuple(np.random.rand(3)) for _ in range(n)]

# -------------------------------
# 블롭 생성
# -------------------------------
def blob(n_points=200, radius=1.0, wobble=0.2):
    angles = np.linspace(0, 2*np.pi, n_points)
    radii = radius + np.random.uniform(-wobble, wobble, size=n_points)
    x = radii * np.cos(angles)
    y = radii * np.sin(angles)
    return x, y

# -------------------------------
# 포스터 그리기
# -------------------------------
def draw_poster(n_layers=8, wobble=0.2, radius=1.0, style="Zen", seed=None):
    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_facecolor("#fdfdf8")
    ax.axis("off")
    palette = get_palette(style, n_layers, seed)
    
    for i in range(n_layers):
        r = radius - i * 0.05
        x, y = blob(radius=r, wobble=wobble)
        color = palette[i % len(palette)]
        alpha = np.random.uniform(0.4, 0.8)
        ax.fill(x, y, color=color, alpha=alpha)
    
    st.pyplot(fig)
    plt.close(fig)

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("🎨 Generative Abstract Poster")

# 사이드바 슬라이더
n_layers = st.sidebar.slider("Layers", 3, 20, 8, 1)
wobble = st.sidebar.slider("Wobble", 0.01, 0.5, 0.2, 0.01)
radius = st.sidebar.slider("Radius", 0.5, 2.0, 1.0, 0.05)
style = st.sidebar.selectbox("Palette Style", ["Zen", "Party", "Glitch"])

# 새 포스터 생성 버튼
if st.button("Generate New Poster"):
    draw_poster(n_layers=n_layers, wobble=wobble, radius=radius, style=style, seed=None)
