# CMS以外
from django.shortcuts import render

# loginページ
def blog_login(request):
    return render(request, 'blog_login.html')

# ガイドラインページ
def blog_guidelines(request):
    return render(request, 'guidelines.html')


# 404ページテスト用
#from django.shortcuts import render
#def test_404(request):
#    return render(request, '404.html', status=404)

#Debug=Falseの時にエラーをHTMLで表示させるロジック
#import traceback
#from django.http import HttpResponseServerError


#def custom_500_view(request):
#    import sys
#    exc_type, exc_value, tb = sys.exc_info()
#    trace = ''.join(traceback.format_exception(exc_type, exc_value, tb))
#    return HttpResponseServerError(f"<pre>{trace}</pre>")