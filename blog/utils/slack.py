import os
from dotenv import load_dotenv
import requests

# プロジェクトのルートに.envまたはenvファイルがある場合
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'env'))

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_notification(text):
    if not SLACK_WEBHOOK_URL:
        raise ValueError("SLACK_WEBHOOK_URLが設定されていません")
    payload = {"text": text}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    response.raise_for_status()