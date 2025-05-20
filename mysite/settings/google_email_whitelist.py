import logging
from django.core.cache import cache
from mysite.settings import read_account_sheet                     # 既存モジュール

#CACHE_KEY = "allowed_google_emails"
#CACHE_TTL = 60 * 60  # 1 時間

def get_allowed_emails():
    emails = read_account_sheet.read_acount_list()
    #if emails is None:
       # try:
            #emails = read_account_sheet.read_acount_list()
            #cache.set(CACHE_KEY, emails, CACHE_TTL)
        #except Exception as e:
           # logging.warning(f"Sheets 読み込み失敗: {e}")
            #emails = []
    return emails

if __name__ == '__main__':
    print(get_allowed_emails())