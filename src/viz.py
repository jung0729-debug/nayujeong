# src/viz.py
import pandas as pd
import plotly.express as px

def parse_year(v):
    try:
        s = str(v).strip()
        # take first 4-digit number if possible
        if len(s) >= 4 and s[:4].isdigit():
            return int(s[:4])
        # fallback: find digits
        import re
        m = re.search(r"\d{4}", s)
        if m:
            return int(m.group(0))
    except:
        pass
    return None

def plot_year_histogram(metas):
    """
    metas: list of MET metadata dicts
    returns: (fig, dataframe)
    """
    rows = []
    for m in metas:
        year = parse_year(m.get("objectDate",""))
        rows.append({"title": m.get("title"), "artist": m.get("artistDisplayName"), "year": year})
    df = pd.DataFrame(rows)
    df = df.dropna(subset=["year"])
    if df.empty:
        return (None, df)
    fig = px.histogram(df, x="year", nbins=30, title="Artwork Year Distribution")
    return (fig, df)
