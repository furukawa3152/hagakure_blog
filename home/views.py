# CMS以外
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import requests

from django.http import HttpResponse
import traceback

from django.http import HttpResponse







# CMS以外
# hagakureTopページ
def index(request):
    return render(request, 'home/index.html')

# hagakure参加者の声ページ
def voice(request):
    return render(request, 'home/voice.html')

# hagakure利用規約のページ
def term_use(request):
    return render(request, 'home/term_use.html')

# transformersagaページ
def saga_bot(request):
    return render(request, 'home/saga_bot.html')

# API
@require_http_methods(["POST"])
def trans_sagaben(request):
    # 改行を取り除いて入力を処理
    user_message = request.POST.get('message', '').replace('\n', '').replace('\r', '')
    try:
        response = requests.post("https://9z6fdi7vqg.execute-api.ap-northeast-1.amazonaws.com/default/Transformer_saga",
                                json={"message": user_message})
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print(f"エラーばい。入力内容ば確認して試してくれん？: {err}")
        return render(request, "home/isaga_bot.html", {"messages": [{"sender": "bot", "text": "エラーばい。入力内容ば確認して試してくれん？"}]})
    else:
        return render(request, "home/saga_bot.html", {"messages": response.json()["messages"]})
# T5説明ページ
def indext5explain(request):
    return render(request, 'home/indext5explain.html')