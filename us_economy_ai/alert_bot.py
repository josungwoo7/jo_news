import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def send_telegram_message(chat_id, message):
    data = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        response = requests.post(TELEGRAM_API_URL, data=data)
        if response.status_code == 200:
            print("[텔레그램] 메시지 전송 완료")
        else:
            print(f"[텔레그램] 메시지 전송 실패: {response.text}")
    except Exception as e:
        print(f"[텔레그램] 메시지 전송 중 오류 발생: {e}")
