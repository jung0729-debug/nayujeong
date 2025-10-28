import streamlit as st
import random, math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb

# ---------- 팔레트 생성 ----------
def make_palette(k=6, mode="creative", base_h=0.6):
    cols = []
    if mode == "pastel":
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
    else:  # random
        for _ in range(k):
            h=random.random(); s=random.uniform(0.3,1.0); v=random.uniform(0.5,1.0)
            cols.append(tuple(hsv_to_rgb([h,s,v])))
    return cols

# ---------- 블롭 생성 ----------
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

# ---------- 포스터 그리기 ----------
def draw_poster(layers):
    fig, ax = plt.subplots(figsize=(6,8))
    ax.axis('off'); ax.set_facecolor((0.97,0.97,0.97))
    for layer in layers:
        x,y=blob(center=(layer["x"],layer["y"]),
                 r=layer["size"],
                 wobble=layer["wobble"],
                 irregularity=layer["irregularity"],
                 shape_type=layer["shape"])
        color=random.choice(layer["palette"])  # 선택한 모드에서 랜덤 색
        ax.fill(x,y,color=color,alpha=layer["alpha"],edgecolor=(0,0,0,0))
    ax.text(0.05,0.95,"Interactive Cinematic Poster", transform=ax.transAxes, fontsize=20,weight="bold")
    return fig

# ---------- Streamlit UI ----------
st.title("🎨final Poster Generator ")

n_layers=st.slider("Number of Layers",1,10,5)
color_modes=["pastel","vivid","mono","creative","cinematic","random"]

layers=[]
for i in range(n_layers):
    with st.expander(f"Layer {i+1} settings", expanded=(i<2)):
        x=st.slider(f"X (Layer {i+1})",0.0,1.0,0.5,key=f"x{i}")
        y=st.slider(f"Y (Layer {i+1})",0.0,1.0,0.5,key=f"y{i}")
        size=st.slider(f"Size",0.05,0.5,0.2,key=f"s{i}")
        wobble=st.slider(f"Wobble",0.0,1.0,0.2,key=f"w{i}")
        irregularity=st.slider(f"Irregularity",0.0,1.0,0.5,key=f"ir{i}")
        alpha=st.slider(f"Opacity",0.1,1.0,0.6,key=f"a{i}")
        shape=st.selectbox(f"Shape",["blob","ellipse","polygon","star"],key=f"sh{i}")
        palette_mode=st.selectbox(f"Color Mode",color_modes,key=f"mode{i}")
        palette=make_palette(6,mode=palette_mode)
        layers.append({"x":x,"y":y,"size":size,"wobble":wobble,"irregularity":irregularity,
                       "alpha":alpha,"shape":shape,"palette":palette})

fig=draw_poster(layers)
st.pyplot(fig)

# 다운로드
import io
buf=io.BytesIO()
fig.savefig(buf,format="png",dpi=300,bbox_inches="tight")
st.download_button("Download Poster",buf,file_name="poster.png",mime="image/png")
