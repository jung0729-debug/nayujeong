#step1

# Generative Abstract Poster
# Concepts: randomness, lists, loops, functions, matplotlib

import random
import math
import numpy as np
import matplotlib.pyplot as plt

def random_palette(k=5):
    # k개의 랜덤 색상(파스텔 톤 느낌)을 생성해서 리스트로 반환
    return [(random.random(), random.random(), random.random()) for _ in range(k)]

def blob(center=(0.5, 0.5), r=0.3, points=200, wobble=0.15):
    # 일정 반경(r)을 기준으로 약간씩 흔들리는(wobble) 곡선을 만들어 폐곡선 형태를 반환
    angles = np.linspace(0, 2*math.pi, points)  # 0~360도를 points 개수만큼 나눈 각도 배열
    radii = r * (1 + wobble*(np.random.rand(points)-0.5))  # 반지름에 랜덤 흔들림 추가
    x = center[0] + radii * np.cos(angles)  # 중심 x 좌표 기준으로 각도에 맞게 좌표 계산
    y = center[1] + radii * np.sin(angles)  # 중심 y 좌표 기준으로 각도에 맞게 좌표 계산
    return x, y  # (x,y) 좌표 배열 반환

random.seed()  # 실행할 때마다 다른 랜덤 시드 사용 → 매번 다른 아트워크 생성
plt.figure(figsize=(7,10))  # 그림 크기 설정 (7인치 × 10인치)
plt.axis('off')  # 축 눈금/테두리 제거 (깨끗한 캔버스 느낌)

# 배경색 설정 (아주 밝은 크림색 톤)
plt.gca().set_facecolor((0.98,0.98,0.97))

palette = random_palette(6)  # 랜덤 색상 6개를 만들어 팔레트로 저장
n_layers = 8  # 블롭(도형) 레이어 개수
for i in range(n_layers):
    cx, cy = random.random(), random.random()  # 도형 중심을 랜덤 위치로 지정
    rr = random.uniform(0.15, 0.45)  # 도형의 기본 반지름 크기를 랜덤으로 선택
    x, y = blob(center=(cx, cy), r=rr, wobble=random.uniform(0.05,0.25))  # 랜덤 블롭 도형 생성
    color = random.choice(palette)  # 팔레트에서 색 하나 랜덤 선택
    alpha = random.uniform(0.25, 0.6)  # 반투명 정도(투명도) 랜덤 설정
    plt.fill(x, y, color=color, alpha=alpha, edgecolor=(0,0,0,0))  # 도형을 색 채워서 그림 위에 올림

# 포스터 제목 텍스트 추가
plt.text(0.05, 0.95, "Generative Poster", fontsize=18, weight='bold', transform=plt.gca().transAxes)
# 부제 텍스트 추가
plt.text(0.05, 0.91, "Week 2 • Arts & Advanced Big Data", fontsize=11, transform=plt.gca().transAxes)

# x, y 범위 [0,1]으로 고정 (전체 캔버스를 0~1 좌표계로 사용)
plt.xlim(0,1); plt.ylim(0,1)
plt.show()  # 최종 이미지 출력
