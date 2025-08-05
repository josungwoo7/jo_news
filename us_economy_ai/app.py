import streamlit as st
from news_collector import get_news, extract_article_text
from summarizer import summarize_article
from data_fetcher import fetch_market_summary

st.set_page_config(layout="wide", page_title="미국 경제 분석 AI")
st.title("🇺🇸 미국 경제 분석 대시보드")

st.header("📉 증시 요약")
market_data = fetch_market_summary()
for index, data in market_data.items():
    st.metric(index, f"{data['close']:.2f}", f"{data['change']} ({data['pct']}%)")

st.header("📰 경제 뉴스 요약")
entries = get_news()
for i, entry in enumerate(entries, 1):
    with st.expander(f"{i}. {entry.title}"):
        article = extract_article_text(entry.link)
        if article:
            summary = summarize_article(article)
            st.markdown(summary)
        else:
            st.warning("본문을 불러올 수 없습니다.")
