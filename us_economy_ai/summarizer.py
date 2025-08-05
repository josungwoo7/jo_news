import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_article(text):
    prompt = f"""
[미국 경제 뉴스 요약]

1. 주요 내용 요약
2. 트럼프의 경제 정책 관련 내용
3. 주식 시장 (S&P 500, 나스닥, 다우) 관련 분석
4. 경제 흐름에 대한 시사점

기사 본문:
{text}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message.content
