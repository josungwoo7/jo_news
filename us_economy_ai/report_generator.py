from jinja2 import Template
from weasyprint import HTML

def generate_report(date, news_summaries, market_summary, filename="report.pdf"):
    template_html = """
    <h1>미국 경제 리포트 - {{ date }}</h1>
    <h2>증시 요약</h2>
    <ul>
        {% for k, v in market_summary.items() %}
        <li><b>{{ k }}</b>: {{ v.close }} ({{ v.change }} / {{ v.pct }}%)</li>
        {% endfor %}
    </ul>
    <h2>뉴스 요약</h2>
    {% for news in news_summaries %}
        <h3>{{ loop.index }}. {{ news.title }}</h3>
        <p>{{ news.summary }}</p>
    {% endfor %}
    """
    template = Template(template_html)
    rendered = template.render(date=date, news_summaries=news_summaries, market_summary=market_summary)
    HTML(string=rendered).write_pdf(filename)
