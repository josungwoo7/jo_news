import feedparser
from newspaper import Article

def get_news():
    feed = feedparser.parse("https://news.google.com/rss/search?q=US+economy+when:1d&hl=en-US&gl=US&ceid=US:en")
    return feed.entries[:5]

def extract_article_text(url):
    article = Article(url)
    try:
        article.download()
        article.parse()
        return article.text if len(article.text.strip()) > 100 else ""
    except:
        return ""
