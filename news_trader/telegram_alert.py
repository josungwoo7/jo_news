import requests

TELEGRAM_TOKEN = "8052139129:AAFAVnV9Xf2wvs3nS3e4zvBUr6WvugNx_58"
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

if __name__ == "__main__":
    # 테스트용 chat_id를 입력하세요 (예: 123456789 또는 -1001234567890)
    chat_id = "8082360458"
    message = "텔레그램 메시지 전송 테스트입니다."
    send_telegram_message(chat_id, message) 