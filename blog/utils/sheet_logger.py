import gspread
import os
import openai
from google.oauth2.service_account import Credentials
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_hagakure_summary(content):
    """HAGAKURE君の口調で超簡潔に一言でブログ内容を説明"""
    prompt = f"以下のブログ記事の内容を、超簡潔に一言（30文字以内）で説明してください。\n\n{content[:1000]}"  # 最初の1000文字のみ使用
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """ 
あなたは「HAGAKURE君」という侍キャラクターです。
・一人称は「拙者」
・語尾には「ござる」が付く
・「です」「ます」は使わない
・超簡潔に一言（30文字以内）でブログの内容を説明する

例：
「Pythonの基礎を学ぶブログでござる」
「Reactフックの使い方を解説しているでござる」
「データベース設計の極意が書かれているでござる」
         """},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def log_to_sheet(author_name, post_title, content, post_url):
    """
    log_for_xシートにブログ投稿をログ記録
    
    Args:
        author_name: 投稿者名
        post_title: 投稿タイトル
        content: ブログ本文
        post_url: ブログのURL
    
    Returns:
        bool: 記録に成功したか（重複の場合はFalse）
    """
    try:
        # 認証情報を取得
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'mysite', 'settings', 'hagakurewagtailauth-fbf65e104bc8.json')
        
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        
        client = gspread.authorize(creds)
        SPREADSHEET_ID = "1qW3HmauHOlqnAhaG-bsNx9I8Ank6Lan4h6uCU9tV0VQ"
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        
        # log_for_xシートを取得
        worksheet = spreadsheet.worksheet("log_for_x")
        
        # 既存データを取得（A列とB列）
        all_records = worksheet.get_all_values()
        
        # 重複チェック：同じ投稿者名 + タイトルの組み合わせがあるか
        for row in all_records:
            if len(row) >= 2:
                if row[0] == author_name and row[1] == post_title:
                    print(f"重複：{author_name} - {post_title} はすでに記録されています")
                    return False
        
        # 重複がない場合、HAGAKURE君の一言を生成
        summary = generate_hagakure_summary(content)
        
        # 現在日時を取得
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 新しい行を追加（A:投稿者, B:タイトル, C:一言, D:URL, E:日時）
        new_row = [author_name, post_title, summary, post_url, timestamp]
        worksheet.append_row(new_row)
        
        print(f"ログ記録成功：{author_name} - {post_title}")
        return True
        
    except Exception as e:
        print(f"シートへのログ記録エラー: {e}")
        return False


if __name__ == '__main__':
    # テスト用
    test_content = "Pythonの基礎について学びます。変数、関数、クラスなどの概念を解説します。"
    log_to_sheet("テスト太郎", "Pythonの基礎", test_content, "https://example.com/blog/1")

