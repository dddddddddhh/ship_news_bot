
import openai
import feedparser
import requests
from datetime import datetime
import urllib.parse
import os

# ✅ 환경변수에서 키 가져오기
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 🔍 검색 키워드
keywords = [
    "선박 친환경 연료",
    "선박 이산화탄소 저감",
    "선박 풍력 추진",
    "선박 에너지 효율 향상",
    "IMO 친환경 규제",
    "선박 탄소중립 기술",
    "메탄올 연료 추진 선박",
    "암모니아 연료",
    "수소 연료",
    "스마트십 자율운항",
    "배터리 하이브리드 선박",
    "EEDI EEXI CII 규제",
    "ESG 조선 기술"
]

# ⚔ 비교 대상 조선사
competitors = ["삼성중공업", "현대중공업", "한국조선해양", "현대미포조선", "현대삼호중공업", "중국 조선소", "CSSC"]

# 📚 뉴스 수집 및 요약
summaries = []
for kw in keywords:
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(kw)}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    if not feed.entries:
        continue
    article = feed.entries[0]
    title = article.title
    link = article.link

    prompt = f"""
    다음은 선박 관련 뉴스 기사입니다.
    제목: {title}
    링크: {link}

    1. 이 뉴스의 내용을 핵심 기술 중심으로 요약해줘.
    2. 이 기술이 어떤 조선사와 관련된 것인지 설명해줘.
    3. 그리고 경쟁사({', '.join(competitors)})들은 현재 유사한 기술을 개발 중인지 분석해줘.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        summary = response['choices'][0]['message']['content']
        summaries.append(f"📌 [{kw}]
{summary}")
    except Exception as e:
        summaries.append(f"[{kw}] 요약 실패: {str(e)}")

# 📬 텔레그램 전송
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})

full_text = f"📅 {datetime.now().strftime('%Y-%m-%d')} 선박 기술 뉴스 요약

" + "\n\n".join(summaries)

MAX_LENGTH = 4000
while len(full_text) > 0:
    send_telegram(full_text[:MAX_LENGTH])
    full_text = full_text[MAX_LENGTH:]
