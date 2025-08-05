from news_trader.news_crawler import fetch_all_news
from news_trader.news_analyzer import analyze_news
from news_trader.stock_info import get_stock_info
from news_trader.telegram_alert import send_telegram_message
import re
import os
import json
import argparse
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from sib_api_v3_sdk import Configuration, ApiClient, TransactionalEmailsApi
from sib_api_v3_sdk.rest import ApiException

PROCESSED_FILE = "processed_articles.json"

def log(msg):
    now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{now} {msg}")

def load_processed_articles():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_processed_articles(processed):
    with open(PROCESSED_FILE, "w") as f:
        json.dump(list(processed), f)

def extract_ticker_or_company(analysis_text):
    # 종목명 또는 티커 추출 (간단한 정규식, 필요시 개선)
    match = re.search(r'(티커|종목명|회사명)[^\w\d]*([A-Z]{1,5})', analysis_text)
    if match:
        return match.group(2)
    # 대문자 1~5자리 추출 (예: AAPL, MSFT)
    match = re.search(r'\b[A-Z]{1,5}\b', analysis_text)
    if match:
        return match.group(0)
    return None

def is_positive_news(analysis_text):
    return '호재' in analysis_text or '긍정' in analysis_text

def summarize_for_telegram(analysis, max_lines=5):
    # 분석 결과를 5줄 이내로 요약해서 반환
    lines = [line.strip() for line in analysis.strip().split('\n') if line.strip()]
    
    return '\n'.join(lines[:max_lines])

def summary_mode():
    """트럼프 경제 정책과 미국 주식 시장 동향 분석 모드"""
    log("[경제 요약 모드] 시작")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # 오늘 날짜의 모든 경제 뉴스 수집
    articles = fetch_all_news(max_articles=10)
    all_news_content = []
    
    for article in articles:
        content = f"[{article['source']}] {article['title']}: {article['content'][:1000]}..."
        all_news_content.append(content)
    
    # 전체 뉴스를 하나의 텍스트로 합침
    combined_news = "\n\n".join(all_news_content)
    
    print("--------------------------------")
    print(combined_news)
    print("--------------------------------")

    # 트럼프 경제 정책과 주식 시장 분석 프롬프트
    analysis_prompt = PromptTemplate(
        input_variables=["news"],
        template="""
        다음은 오늘의 미국 경제 뉴스들입니다. 이를 바탕으로 다음 두 가지 관점에서 분석해주세요:

        1. 트럼프 대통령의 경제 정책 관련 뉴스 분석:
        - 관세, 세금, 규제완화, 인프라 등 트럼프 경제 정책과 관련된 내용
        - 정책이 경제에 미칠 영향 분석
        
        2. 미국 주식 시장의 전반적인 동향:
        - 주요 지수(S&P 500, 다우, 나스닥) 동향
        - 섹터별 주식 시장 흐름
        - 투자자 심리 및 시장 전망
        
        각 분석은 3-5줄로 간결하게 요약해주세요.

        뉴스: {news}
        """
    )
    
    try:
        llm = OpenAI(model_name="gpt-4o-mini", temperature=0.2)
        analysis_chain = analysis_prompt | llm
        analysis_result = analysis_chain.invoke({"news": combined_news})
        
        log("[경제 요약 분석 완료]")
        print(analysis_result)
        
        # 텔레그램으로 전송
        if chat_id:
            today = datetime.now().strftime('%Y-%m-%d')
            message = f"[미국 경제 동향 분석] {today}\n\n{analysis_result}"
            send_telegram_message(chat_id, message)
            log("[경제 요약] 텔레그램 전송 완료")
        
    except Exception as e:
        log(f"[오류] 경제 요약 분석 실패: {e}")

def main():
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not chat_id:
        log("[안내] 텔레그램 chat_id를 환경변수 TELEGRAM_CHAT_ID로 지정하거나, 코드에 직접 입력하세요.")
    processed = load_processed_articles()
    articles = fetch_all_news(max_articles=5)
    daily_summaries = []
    for article in articles:
        article_id = article['link']
        if article_id in processed:
            log(f"[패스] 이미 처리한 기사: {article['title']}")
            continue
        log(f"[신문사] {article['source']} | [기사 제목] {article['title']}")
        analysis = analyze_news(article['content'])
        log(f"[분석 결과]\n{analysis}")
        summary = summarize_for_telegram(analysis, max_lines=5)
        daily_summaries.append(f"[{article['source']}] {article['title']}\n{summary}\n")
        if chat_id:
            message = f"[경제 뉴스 요약]\n신문사: {article['source']}\n제목: {article['title']}\n링크: {article['link']}\n\n{summary}"
        ticker = extract_ticker_or_company(analysis)
        if ticker and is_positive_news(analysis):
            stock = get_stock_info(ticker)
            company_name = stock['info'].get('shortName') if stock['info'] else None
            if not stock['price']:
                log(f"[주가 정보] {ticker}: 정보 없음 (유효하지 않은 티커일 수 있음)")
                processed.add(article_id)
                continue
            log(f"[주가 정보] {ticker} ({company_name}): {stock['price']} / PER: {stock['pe_ratio']}")
            if stock['pe_ratio'] and stock['pe_ratio'] < 25 and stock['market_cap'] and stock['market_cap'] > 1e9:
                log(f"[매수 조건 충족] {ticker} (자동매수는 비활성화)")
                if chat_id:
                    message = f"[매수 조건 충족]\n종목: {ticker} ({company_name})\n현재가: ${stock['price']}\nPER: {stock['pe_ratio']}\n시가총액: ${stock['market_cap']:,.0f}\n기사 제목: {article['title']}\n기사 링크: {article['link']}"
                    send_telegram_message(chat_id, message)
            else:
                log(f"[매수 조건 미충족] {ticker}")
        else:
            log("[매수 대상 아님]")
        processed.add(article_id)
    save_processed_articles(processed)
    if chat_id and daily_summaries:
        today = datetime.now().strftime('%Y-%m-%d')
        report = f"[오늘의 경제 리포트] {today}\n\n" + "\n".join(daily_summaries)
        def send_brevo_email(subject, content, sender_email, receiver_emails_str):
            configuration = Configuration()
            configuration.api_key['api-key'] = os.getenv('BREVO_API_KEY')
            api_instance = TransactionalEmailsApi(ApiClient(configuration))
            email_params = {
                "sender": {"email": sender_email, "name": "News Trader"},
                "to": [{"email": email.strip()} for email in receiver_emails_str.split(',')],
                "subject": subject,
                "htmlContent": content.replace('\n', '<br>')
            }
            try:
                api_instance.send_transac_email(email_params)
                log("[오늘의 경제 리포트] 이메일 전송 완료")
            except ApiException as e:
                log(f"[오류] 이메일 전송 실패: {e}")
        receiver_emails = os.getenv("RECEIVER_EMAILS")
        if receiver_emails:
            send_brevo_email(
                subject=f"[오늘의 경제 리포트] {today}",
                content=report,
                sender_email="dalmooria@gmail.com",
                receiver_emails_str=receiver_emails
            )
        summary_prompt = PromptTemplate(
            input_variables=["report"],
            template="""
            다음은 오늘의 경제 뉴스 리포트입니다. 500자 이내로 가장 중요한 경제 관련 내용만 간단히 요약해주세요.
            
            {report}
            """
        )
        try:
            summary_chain = summary_prompt | OpenAI(model_name="gpt-4o-mini", temperature=0.2)
            summary = summary_chain.invoke({"report": report})
            summary_message = f"[오늘의 경제 뉴스 핵심 요약]\n\n{summary}"
            send_telegram_message(chat_id, summary_message)
            log("[오늘의 경제 뉴스 요약] 텔레그램 전송 완료")
        except Exception as e:
            log(f"[오류] 뉴스 요약 생성 실패: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="경제 뉴스 자동 분석 시스템")
    parser.add_argument("-summary", action="store_true", help="트럼프 경제 정책과 미국 주식 시장 동향 분석 모드")
    args = parser.parse_args()
    
    if args.summary:
        summary_mode()
    else:
        main()