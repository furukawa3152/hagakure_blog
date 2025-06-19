import os
import openai
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'env'))

openai.api_key = os.getenv("OPENAI_API_KEY")

def review_blog_content(content):
    prompt = f"以下のブログ記事をレビューしてください（良い点・改善点・全体の印象など）。\n\n{content}"
    response = openai.chat.completions.create(
        model="gpt-4o",
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