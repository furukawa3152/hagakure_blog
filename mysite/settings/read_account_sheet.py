import gspread
import os
from google.oauth2.service_account import Credentials
from pathlib import Path

def read_acount_list():
    # サービスアカウントのJSONキーのパス
    BASE_DIR = Path(__file__).resolve().parent

    SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'hagakurewagtailauth-fbf65e104bc8.json')


    # 認証情報を作成
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    # スプレッドシートに接続
    client = gspread.authorize(creds)

    # スプレッドシートを開く（スプレッドシートのIDを指定）
    SPREADSHEET_ID = "1qW3HmauHOlqnAhaG-bsNx9I8Ank6Lan4h6uCU9tV0VQ"
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    # シートを開く
    worksheet = spreadsheet.sheet1  # 最初のシートを取得

    # B列の全データを取得（リスト形式）
    column_b_values = worksheet.col_values(2)  # B列を取得（1列目はA列、2列目はB列）

    # 2行目以降を取得（1行目を削除）
    return column_b_values[1:]

if __name__ == '__main__':
    print(read_acount_list())