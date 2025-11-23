import os
from pathlib import Path

import openai
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Try multiple env locations (root/env, root/.env, mysite/settings/env) without overriding existing env vars
for candidate in [
    BASE_DIR / "env",
    BASE_DIR / ".env",
    BASE_DIR / "mysite" / "settings" / "env",
]:
    load_dotenv(candidate, override=False)

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    # 明示的にエラーを出すことでログが分かりやすくなる
    raise ValueError("OPENAI_API_KEY が設定されていません（env/.env または環境変数を確認してください）")

def review_blog_content(content):
    prompt = f"以下のブログ記事をレビューしてください（良い点・改善点・全体の印象など）。\n\n{content}"
    response = openai.chat.completions.create(
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
         """},  # system
            {"role": "user", "content": prompt}
        ],
        max_completion_tokens=1200,
        temperature=0.5,
    )
    return response.choices[0].message.content
