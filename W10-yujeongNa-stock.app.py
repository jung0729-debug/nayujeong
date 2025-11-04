import streamlit as st
import pandas as pd
import requests

st.sidebar.header("분석 설정")
num = st.sidebar.slider("추천받을 종목 개수", 1, 10, 5)
market_cap = st.sidebar.number_input("최소 거래 규모 (억원)", 0, 100000, 100)

if st.sidebar.button("분석 시작하기"):
    analyze = True
else:
    analyze = False

st.title("코스피200 주식 추천 시스템")
st.markdown("초보자도 쉽게 이해하는 주식 분석 도구")

stock_data = [
    {"종목명": "NAVER", "현재가": 280000, "점수": 9.0, "거래대금": 4935, "수익률": 11.6, "신호": ["상승추세", "강한지속", "적정가격"]},
    {"종목명": "삼성전자", "현재가": 109900, "점수": 7.5, "거래대금": 25052, "수익률": 7.7, "신호": ["상승추세", "강한지속", "조정가능"]},
    {"종목명": "카카오", "현재가": 64900, "점수": 7.5, "거래대금": 1996, "수익률": 6.6, "신호": ["상승추세", "강한지속", "적정가격"]},
    {"종목명": "현대차", "현재가": 200000, "점수": 7.0, "거래대금": 4300, "수익률": 9.3, "신호": ["상승추세", "강한지속"]},
    {"종목명": "삼성물산", "현재가": 125000, "점수": 6.5, "거래대금": 3900, "수익률": 5.1, "신호": ["상승추세"]},
]

df = pd.DataFrame(stock_data)

if analyze:
    df = df[df['거래대금'] >= market_cap].sort_values('점수', ascending=False).head(num)
    st.subheader(f"추천 종목 TOP {len(df)}")
    cols = st.columns(len(df))

    for idx, row in df.reset_index().iterrows():
        with cols[idx]:
            st.markdown(f"**{idx+1}위. {row['종목명']}**")
            st.write(f"💵 현재가: {row['현재가']:,}원")
            st.write(f"⭐ 추천 점수: {row['점수']:.1f}점")
            st.write(f"📈 최근5일 수익률: {row['수익률']}%")
            st.write(f"💸 평균 거래대금: {row['거래대금']:,}억원")
            st.write("✅ 매수 신호:")
            for signal in row['신호']:
                st.write("- " + signal)
            if st.button(f"{row['종목명']} 뉴스 보기", key=f"news_{idx}"):
                st.session_state.news_stock = row['종목명']
else:
    st.info("좌측에서 조건을 입력하고 '분석 시작하기'를 눌러주세요.")

news_stock = st.session_state.get('news_stock', df.iloc[0]['종목명'] if not df.empty else '')

st.markdown("---")
st.subheader(f"📢 {news_stock} 관련 최신 뉴스")

def get_news_newsapi(query):
    api_key = '6add4df125c64fdcb1ba47352dfcab55'  # 전달받은 키 활용
    url = f'https://newsapi.org/v2/everything?q={query}&pageSize=5&sortBy=publishedAt&apiKey={api_key}'
    try:
        response = requests.get(url)
        articles = response.json().get('articles', [])
        return [(article['title'], article['url']) for article in articles]
    except Exception as e:
        st.error(f'뉴스 API 호출 오류: {e}')
        return []

news_list = get_news_newsapi(news_stock)
if news_list:
    for title, link in news_list:
        st.markdown(f"- [{title}]({link})")
else:
    st.write("뉴스 결과가 없습니다. API 키 및 연결 상태를 확인해 주세요.")
