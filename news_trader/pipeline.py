from news_trader.news_crawler import fetch_all_news
from news_trader.news_analyzer import analyze_news
from news_trader.stock_info import get_stock_info
from news_trader.telegram_alert import send_telegram_message
import re
import os
import json
from datetime import datetime

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

def main():
    # chat_id는 환경변수 또는 직접 입력
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
        analysis = analyze_news(article['title'], article['content'])
        log(f"[분석 결과]\n{analysis}")
        # 기사 요약 5줄 이내로 텔레그램 전송 및 종합 리포트에 저장
        summary = summarize_for_telegram(analysis, max_lines=5)
        daily_summaries.append(f"[{article['source']}] {article['title']}\n{summary}\n")
        if chat_id:
            message = f"[경제 뉴스 요약]\n신문사: {article['source']}\n제목: {article['title']}\n링크: {article['link']}\n\n{summary}"
            send_telegram_message(chat_id, message)
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
                # 텔레그램 알림 전송
                if chat_id:
                    message = f"[매수 조건 충족]\n종목: {ticker} ({company_name})\n현재가: ${stock['price']}\nPER: {stock['pe_ratio']}\n시가총액: ${stock['market_cap']:,.0f}\n기사 제목: {article['title']}\n기사 링크: {article['link']}"
                    send_telegram_message(chat_id, message)
            else:
                log(f"[매수 조건 미충족] {ticker}")
        else:
            log("[매수 대상 아님]")
        processed.add(article_id)
    save_processed_articles(processed)
    # 오늘의 경제 리포트 종합 및 전송
    if chat_id and daily_summaries:
        today = datetime.now().strftime('%Y-%m-%d')
        report = f"[오늘의 경제 리포트] {today}\n\n" + "\n".join(daily_summaries)
        send_telegram_message(chat_id, report)
        log("[오늘의 경제 리포트] 텔레그램 전송 완료")

if __name__ == "__main__":
    main() 