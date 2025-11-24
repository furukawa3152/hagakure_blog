import logging
import os
from pathlib import Path

from dotenv import load_dotenv
import requests

logger = logging.getLogger(__name__)

# プロジェクトのルートとutils直下の.envを順に読み込む
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(BASE_DIR / ".env")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_notification(text):
    if not SLACK_WEBHOOK_URL:
        logger.warning("SLACK_WEBHOOK_URLが設定されていないためSlack通知をスキップしました")
        return
    payload = {"text": text}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    response.raise_for_status()
