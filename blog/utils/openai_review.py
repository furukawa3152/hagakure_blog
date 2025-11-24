import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

logger = logging.getLogger(__name__)

# Try loading .env from project root and this utils directory (local dev use-case)
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(BASE_DIR / ".env")

_api_key = os.getenv("OPENAI_API_KEY")
_client = OpenAI(api_key=_api_key) if _api_key else None

def review_blog_content(content):
    if not _client:
        logger.error("OPENAI_API_KEYが設定されていません")
        raise RuntimeError("OPENAI_API_KEYが設定されていません")

    prompt = f"以下のブログ記事をレビューしてください（良い点・改善点・全体の印象など）。\n\n{content}"
    response = _client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": """ 
以下のような設定のキャラクターになりきって、「です」、「ます」や敬語は使わずにため口で、ブログ記事をレビューしてください。
長文の回答になっても、設定は必ず守ってください。
・名前は「HAGAKURE君」です。
・一人称は「拙者」です。
・語尾には「ござる」が付きます。
例文：
拙者は、Pythonを修行中の侍でござる。
拙者は、「HAGAKUREプログラミング塾」で学んでいるのでござる。
         これはPythonの構文についてのブログでござるな。
         コードの内容を、このように修正しても良いでござる。
         Pythonに出会ってから、多くのことを学び、コードを書くこと自体が楽しくなり申した。
         """},  # system
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.7,
    )
    return response.choices[0].message.content
