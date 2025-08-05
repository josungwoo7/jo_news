import streamlit as st
import feedparser
from newspaper import Article
import openai
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

load_dotenv()
# 설정
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()


def summarize_by_url_only(url):
    prompt = f"""
이 뉴스 기사 URL을 참고해 미국 경제 요약을 해줘. 트럼프 정책과 주식시장 관련 내용이 있으면 중점 분석해줘:

URL: {url}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=800
    )
    return response.choices[0].message.content

def fallback_extract_article(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 기사 본문 추정: <p> 태그 다 모아서 연결
        paragraphs = soup.find_all('p')
        text = ' '.join(p.get_text() for p in paragraphs)
        if len(text.strip()) < 300:
            return ""
        return text
    except:
        return ""
    
def get_article_text(url):
    text = extract_article(url)
    if not text:
        text = fallback_extract_article(url)
    return text

def get_article_summary(url):
    text = extract_article(url)
    if text:
        return summarize_article(text)
    else:
        return summarize_by_url_only(url)
    
# --- 함수: 뉴스 RSS 가져오기 ---
def get_news_entries():
    url = "https://news.google.com/rss/search?q=US+economy+when:1d&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    return feed.entries[:5]

# --- 함수: 기사 내용 추출 ---
def extract_article(url):
    article = Article(url)
    try:
        article.download()
        article.parse()
        # print(article.html)
        return article.text
    except:
        return ""

# --- 함수: OpenAI로 요약 및 분석 ---
def summarize_article(text):
    prompt = f"""
다음은 미국 경제 기사입니다. 다음 항목을 중심으로 요약해줘:

1. 기사 핵심 요약 (3~4줄)
2. 트럼프의 경제 정책 관련 내용이 있다면 상세 분석
3. 미국 주식 시장 관련 내용이 있다면 분석 (S&P 500, 나스닥, 다우 포함)
4. 경제 흐름에 대한 시사점 정리

기사 원문:
{text}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=1000
    )
    return response.choices[0].message.content

# --- Streamlit 앱 시작 ---
st.set_page_config(page_title="미국 경제 뉴스 요약", layout="wide")
st.title("🇺🇸 미국 경제 뉴스 요약 및 분석")
st.markdown("최근 미국 경제 뉴스 중 **트럼프 경제 정책**과 **주식 시장 상황**에 초점을 맞춰 요약합니다.")

# 뉴스 가져오기
with st.spinner("뉴스를 수집하고 있습니다..."):
    news_entries = get_news_entries()

# 기사 선택
for idx, entry in enumerate(news_entries):
    with st.expander(f"{entry.title}"):
        st.write(f"[기사 링크]({entry.link})")
        with st.spinner("요약 중..."):
            # content = extract_article(entry.link)
            content = get_article_summary(entry.link)
            if content:
                summary = summarize_article(content)
                st.markdown(summary)
            else:
                st.warning("❌ 본문을 불러올 수 없습니다.")

