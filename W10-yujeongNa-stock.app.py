import streamlit as st
import pandas as pd
import requests

# --- 기존 추천 종목 데이터 ---
stock_data = [
    {"종목명": "NAVER", "현재가": 280000, "점수": 9.0},
    {"종목명": "삼성전자", "현재가": 109900, "점수": 7.5},
    {"종목명": "카카오", "현재가": 64900, "점수": 7.5},
    {"종목명": "현대차", "현재가": 200000, "점수": 7.0},
    {"종목명": "삼성물산", "현재가": 125000, "점수": 6.5},
]
df = pd.DataFrame(stock_data)

st.title("코스피200 주식 추천 시스템")

cols = st.columns(len(df))
news_stock = st.session_state.get('news_stock', df.iloc[0]['종목명'])

# --- 좌측 추천 카드는 유지하고 ---
for idx, row in df.iterrows():
    with cols[idx]:
        st.markdown(f"**{idx+1}위. {row['종목명']}**")
        st.write(f"💵 현재가: {row['현재가']:,}원")
        st.write(f"⭐ 추천 점수: {row['점수']:.1f}점")
        # 뉴스 보기 버튼 추가 (클릭 시 세션 상태에 종목명 저장)
        if st.button(f"{row['종목명']} 뉴스 보기", key=row['종목명']):
            st.session_state['news_stock'] = row['종목명']

# --- 우측 또는 하단에 뉴스 창 추가 ---
st.markdown("---")
st.subheader(f"📢 {news_stock} 관련 최신 뉴스")

def get_news(query):
    # 네이버 뉴스 API 예시 (API키 발급 필요)
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=5&sort=date"
    headers = {
        "X-Naver-Client-Id": "YOUR_NAVER_CLIENT_ID",
        "X-Naver-Client-Secret": "YOUR_NAVER_CLIENT_SECRET"
    }
    try:
        res = requests.get(url, headers=headers)
        items = res.json().get('items', [])
        return [(item['title'], item['link']) for item in items]
    except:
        return []

news_list = get_news(news_stock)
if news_list:
    for title, link in news_list:
        # 뉴스 제목에 html 태그가 들어오는 경우도 있으니 st.markdown으로 처리
        st.markdown(f"- [{title}]({link})")
else:
    st.write("뉴스 결과가 없습니다. API 키 및 연결 상태를 확인해 주세요.")
