import pandas as pd
import matplotlib.pyplot as plt

def plot_year_histogram(metas_dash):
    """
    metas_dash: list of dict (Met metadata)
    - year 컬럼이 없으면 objectDate를 이용해 생성
    - NaN 제거 후 히스토그램 생성
    """
    # DataFrame 변환
    df = pd.DataFrame(metas_dash)

    # 1️⃣ year 컬럼 확인/생성
    if "year" not in df.columns:
        if "objectDate" in df.columns:
            # objectDate 문자열 → 숫자로 변환 (실패하면 NaN)
            df["year"] = pd.to_numeric(df["objectDate"], errors="coerce")
        else:
            print("year 컬럼도 objectDate 컬럼도 없음")
            return None, df

    # 2️⃣ NaN 제거
    df = df.dropna(subset=["year"])

    # 3️⃣ int로 변환 (히스토그램용)
    df["year"] = df["year"].astype(int)

    # 4️⃣ 히스토그램 생성
    fig, ax = plt.subplots(figsize=(8, 4))
    df["year"].hist(bins=30, ax=ax)
    ax.set_title("Artworks by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")

    return fig, df
