from wagtail.signals import page_published
from django.dispatch import receiver
from blog.models import BlogPage
from blog.utils.slack import send_slack_notification
from blog.utils.openai_review import review_blog_content
from blog.utils.sheet_logger import log_to_sheet

@receiver(page_published)
def notify_slack_on_publish(sender, instance, **kwargs):
    if isinstance(instance, BlogPage):
        # 本文を取得（例：page.bodyがStreamFieldの場合はstrで変換）
        content = str(instance.body)
        
        # 投稿者名を取得（owner または revision.user から）
        author_name = "管理者"  # デフォルト値
        if hasattr(instance, 'owner') and instance.owner:
            author_name = instance.owner.get_full_name() or instance.owner.username
        
        # スプレッドシートにログ記録（重複チェックあり）
        log_to_sheet(author_name, instance.title, content, instance.full_url)
        
        # Slackレビュー通知
        review = review_blog_content(content)
        text = (
            f"Scrollに新しい記事が公開されたでござる！\n"
            f"タイトル: {instance.title}\n"
            f"URL: {instance.full_url}\n\n"
            f"拙者がレビューした内容でござる。\n{review}"
        )
        send_slack_notification(text)