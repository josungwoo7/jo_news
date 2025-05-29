import feedparser

def to_utf8(text):
    if not text:
        return ''
    if isinstance(text, bytes):
        return text.decode('utf-8', 'replace')
    return text.encode('utf-8', 'replace').decode('utf-8')

CNBC_RSS_URL = "https://www.cnbc.com/id/100003114/device/rss/rss.html"
BLOOMBERG_RSS_URL = "https://www.bloomberg.com/feed/podcast/etf-report.xml"
WSJ_RSS_URL = "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"
YAHOO_FINANCE_RSS_URL = "https://finance.yahoo.com/news/rssindex"
MARKETWATCH_RSS_URL = "https://feeds.marketwatch.com/marketwatch/topstories/"
FORBES_RSS_URL = "https://www.forbes.com/markets/feed/"

def fetch_cnbc_news(max_articles=10):
    feed = feedparser.parse(CNBC_RSS_URL)
    articles = []
    for entry in feed.entries[:max_articles]:
        summary = to_utf8(entry.summary)
        content = getattr(entry, 'content', None)
        if content and isinstance(content, list) and len(content) > 0:
            content_text = to_utf8(content[0].value)
        else:
            content_text = summary
        articles.append({
            "source": "CNBC",
            "title": to_utf8(entry.title),
            "link": entry.link,
            "summary": summary,
            "content": content_text
        })
    return articles

def fetch_bloomberg_news(max_articles=10):
    feed = feedparser.parse(BLOOMBERG_RSS_URL)
    articles = []
    for entry in feed.entries[:max_articles]:
        summary = to_utf8(entry.summary if hasattr(entry, 'summary') else entry.get('description', ''))
        content = getattr(entry, 'content', None)
        if content and isinstance(content, list) and len(content) > 0:
            content_text = to_utf8(content[0].value)
        else:
            content_text = summary
        articles.append({
            "source": "Bloomberg",
            "title": to_utf8(entry.title),
            "link": entry.link,
            "summary": summary,
            "content": content_text
        })
    return articles

def fetch_wsj_news(max_articles=10):
    feed = feedparser.parse(WSJ_RSS_URL)
    articles = []
    for entry in feed.entries[:max_articles]:
        summary = to_utf8(entry.summary if hasattr(entry, 'summary') else entry.get('description', ''))
        content = getattr(entry, 'content', None)
        if content and isinstance(content, list) and len(content) > 0:
            content_text = to_utf8(content[0].value)
        else:
            content_text = summary
        articles.append({
            "source": "WSJ",
            "title": to_utf8(entry.title),
            "link": entry.link,
            "summary": summary,
            "content": content_text
        })
    return articles

def fetch_yahoo_finance_news(max_articles=10):
    feed = feedparser.parse(YAHOO_FINANCE_RSS_URL)
    articles = []
    for entry in feed.entries[:max_articles]:
        summary = to_utf8(entry.summary if hasattr(entry, 'summary') else entry.get('description', ''))
        content = getattr(entry, 'content', None)
        if content and isinstance(content, list) and len(content) > 0:
            content_text = to_utf8(content[0].value)
        else:
            content_text = summary
        articles.append({
            "source": "Yahoo Finance",
            "title": to_utf8(entry.title),
            "link": entry.link,
            "summary": summary,
            "content": content_text
        })
    return articles

def fetch_marketwatch_news(max_articles=10):
    feed = feedparser.parse(MARKETWATCH_RSS_URL)
    articles = []
    for entry in feed.entries[:max_articles]:
        summary = to_utf8(getattr(entry, 'summary', None) or entry.get('description', None) or entry.title)
        content = getattr(entry, 'content', None)
        if content and isinstance(content, list) and len(content) > 0:
            content_text = to_utf8(content[0].value)
        else:
            description = to_utf8(entry.get('description', ''))
            content_text = f"{to_utf8(entry.title)}\n{description}" if description else summary
        articles.append({
            "source": "MarketWatch",
            "title": to_utf8(entry.title),
            "link": entry.link,
            "summary": summary,
            "content": content_text
        })
    return articles

def fetch_forbes_news(max_articles=10):
    feed = feedparser.parse(FORBES_RSS_URL)
    articles = []
    for entry in feed.entries[:max_articles]:
        summary = to_utf8(entry.summary if hasattr(entry, 'summary') else entry.get('description', ''))
        content = getattr(entry, 'content', None)
        if content and isinstance(content, list) and len(content) > 0:
            content_text = to_utf8(content[0].value)
        else:
            content_text = summary
        articles.append({
            "source": "Forbes",
            "title": to_utf8(entry.title),
            "link": entry.link,
            "summary": summary,
            "content": content_text
        })
    return articles

def fetch_all_news(max_articles=5):
    # 각 신문사별로 max_articles개씩 수집
    return (
        fetch_cnbc_news(max_articles)
        + fetch_bloomberg_news(max_articles)
        + fetch_wsj_news(max_articles)
        + fetch_yahoo_finance_news(max_articles)
        + fetch_marketwatch_news(max_articles)
        + fetch_forbes_news(max_articles)
    )

if __name__ == "__main__":
    for article in fetch_all_news():
        print(article) 