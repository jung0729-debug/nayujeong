import streamlit as st
import random, math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import io

# ---------- 팔레트 ----------
def make_palette(k=6, mode="creative", base_h=0.6):
    cols = []
    if mode=="pastel":
        for _ in range(k):
            h=random.random(); s=random.uniform(0.2,0.4); v=random.uniform(0.9,1.0)
            cols.append(tuple(hsv_to_rgb([h,s,v])))
    elif mode=="vivid":
        for _ in range(k):
            h=random.random(); s=random.uniform(0.8,1.0); v=random.uniform(0.8,1.0)
            cols.append(tuple(hsv_to_rgb([h,s,v])))
    elif mode=="mono":
        for _ in range(k):
            h=base_h; s=random.uniform(0.3,0.6); v=random.uniform(0.5,1.0)
            cols.append(tuple(hsv_to_rgb([h,s,v])))
    elif mode=="creative":
        base_h=random.random()
        for i in range(k):
            if i%2==0: h=(base_h + i*0.1)%1.0
            else: h=(base_h + 0.5 + i*0.05)%1.0
            s=random.uniform(0.5,0.9); v=random.uniform(0.7,1.0)
            cols.append(tuple(hsv_to_rgb([h,s,v])))
    elif mode=="cinematic":
        for i in range(k):
            if i%2==0: h=random.uniform(0.05,0.12); s=random.uniform(0.7,0.9); v=random.uniform(0.7,1.0)
            else: h=random.uniform(0.5,0.65); s=random.uniform(0.4,0.7); v=random.uniform(0.5,0.9)
            cols.append(tuple(hsv_to_rgb([h,s,v])))
    else:
        for _ in range(k):
            h=random.random(); s=random.uniform(0.3,1.0); v=random.uniform(0.5,1.0)
            cols.append(tuple(hsv_to_rgb([h,s,v])))
    return cols

# ---------- 블롭/모양 ----------
def blob(center=(0.5,0.5), r=0.3, points=300, wobble=0.25, irregularity=0.6, shape_type="blob"):
    angles = np.linspace(0, 2*math.pi, points, endpoint=False)
    radii = r * (1 + wobble*(np.random.rand(points)-0.5))
    radii *= 1 + irregularity * np.sin(angles*random.uniform(2,6) + random.random()*2*math.pi)
    scale_x, scale_y = random.uniform(0.7,1.3), random.uniform(0.7,1.3)
    x = center[0] + scale_x * radii * np.cos(angles)
    y = center[1] + scale_y * radii * np.sin(angles)
    if shape_type=="ellipse":
        x=center[0]+scale_x*r*np.cos(angles)
        y=center[1]+scale_y*r*np.sin(angles)
    elif shape_type=="polygon":
        n=random.randint(3,8)
        poly_angles=np.linspace(0,2*math.pi,n,endpoint=False)
        x=center[0]+scale_x*r*np.cos(poly_angles)
        y=center[1]+scale_y*r*np.sin(poly_angles)
    elif shape_type=="star":
        n=random.randint(5,8)
        x_arr,y_arr=[],[]
        for i in range(2*n):
            angle=i*np.pi/n
            rad=r*(1.0 if i%2==0 else 0.5)
            x_arr.append(center[0]+scale_x*rad*math.cos(angle))
            y_arr.append(center[1]+scale_y*rad*math.sin(angle))
        x,y=np.array(x_arr), np.array(y_arr)
    return x,y

# ---------- 포스터 그리기 (입체 느낌) ----------
def draw_poster_3d(n_layers, size_range, wobble, irregularity, alpha, shape_types, palette):
    fig, ax = plt.subplots(figsize=(6,8))
    ax.axis('off'); ax.set_facecolor((0.97,0.97,0.97))
    
    # z-depth 값 (깊이감)
    z_values = np.linspace(0.5, 1.0, n_layers)
    np.random.shuffle(z_values)
    
    for i in range(n_layers):
        cx, cy = random.random(), random.random()
        z = z_values[i]
        r = random.uniform(size_range[0], size_range[1]) * z
        shape = random.choice(shape_types)
        x,y = blob(center=(cx,cy), r=r, wobble=wobble, irregularity=irregularity, shape_type=shape)
        
        # 입체 느낌: 중심 밝기 + z값 반영
        base_color = np.array(random.choice(palette))
        color = np.clip(base_color * (0.7 + 0.3*z),0,1)
        layer_alpha = alpha * (0.5 + 0.5*z)
        ax.fill(x,y,color=color,alpha=layer_alpha,edgecolor=(0,0,0,0))
    
    ax.text(0.05,0.95,"🎨 3D-ish Random Poster", transform=ax.transAxes, fontsize=20,weight="bold")
    return fig

# ---------- Streamlit UI ----------
st.title("🎨 3D-ish Random Poster Generator")

# 전체 옵션
n_layers = st.slider("Number of Layers", 1, 20, 8)
size_range = st.slider("Blob Size Range", 0.05, 0.5, (0.1,0.3))
wobble = st.slider("Wobble", 0.0, 1.0, 0.2)
irregularity = st.slider("Irregularity", 0.0, 1.0, 0.5)
alpha = st.slider("Opacity", 0.1, 1.0, 0.6)
shape_types = st.multiselect("Shapes", ["blob","ellipse","polygon","star"], default=["blob","ellipse"])
color_mode = st.selectbox("Color Mode", ["pastel","vivid","mono","creative","cinematic","random"])
palette = make_palette(6, mode=color_mode)

# 포스터 그리기
fig = draw_poster_3d(n_layers, size_range, wobble, irregularity, alpha, shape_types, palette)
st.pyplot(fig)

# 다운로드
buf = io.BytesIO()
fig.savefig(buf,format="png",dpi=300,bbox_inches="tight")
st.download_button("Download Poster",buf,file_name="poster.png",mime="image/png")
