import logging

from wagtail.signals import page_published
from django.dispatch import receiver
from blog.models import BlogPage
from blog.utils.slack import send_slack_notification
from blog.utils.openai_review import review_blog_content

logger = logging.getLogger(__name__)

@receiver(page_published)
def notify_slack_on_publish(sender, instance, **kwargs):
    if isinstance(instance, BlogPage):
        # 本文を取得（例：page.bodyがStreamFieldの場合はstrで変換）
        content = str(instance.body)
        review = "AIレビューの生成に失敗しました。"
        try:
            review = review_blog_content(content)
        except Exception:
            logger.exception("AI review failed during publish for page %s", instance.id)

        text = (
            f"Scrollに新しい記事が公開されたでござる！\n"
            f"タイトル: {instance.title}\n"
            f"URL: {instance.full_url}\n\n"
            f"拙者がレビューした内容でござる。\n{review}"
        )
        try:
            send_slack_notification(text)
        except Exception:
            logger.exception("Slack notification failed for page %s", instance.id)
