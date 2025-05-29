from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

prompt = PromptTemplate(
    input_variables=["news"],
    template="""
    다음은 미국 경제 뉴스 기사입니다.

    1. 기사 내용을 5줄 이내로 요약하세요.
    2. 투자 관점에서 호재인지 악재인지 판단해 주세요. 호재라면 호재 이유를 알려주세요. 악재라면 악재 이유를 알려주세요. 없다면 무시해주세요.
    3. 기사에 언급된 종목명(티커 또는 회사명)이 있다면 알려주세요. 없다면 무시해주세요.
    4. 기사에 직접적으로 언급되지 않았더라도, 기사 내용을 기반으로 유망하다고 유추할 수 있는 산업군(예: 원자력, AI, 반도체 등)을 추천해 주세요. 없다면 무시해주세요.
    5. 위에서 추천한 산업군과 관련된 미국 주식 또는 ETF(티커와 이름)를 2~3개 추천해 주세요. 없다면 무시해주세요.

    기사제목: {title}
    기사내용: {content}
    """
)

llm = OpenAI(model_name="gpt-4o-mini", temperature=0.2)
chain = prompt | llm

def analyze_news(news_title, news_text):
    """
    뉴스 요약, 호재/악재, 종목명, 유망 산업군, 관련 주식/ETF 추천 결과를 반환합니다.
    """
    return chain.invoke({"title": news_title, "content": news_text})

if __name__ == "__main__":
    sample = "Trump administration pushes for new nuclear energy policy."
    print(analyze_news(sample)) 