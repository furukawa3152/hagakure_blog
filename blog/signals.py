# blog/signals.py
from wagtail.signals import page_published
from django.dispatch import receiver
from blog.models import BlogPage  # あなたのブログページモデル
from blog.utils.slack import send_slack_notification

@receiver(page_published)
def notify_slack_on_publish(sender, instance, **kwargs):
    if isinstance(instance, BlogPage):
        text = f"Scrollに新しい記事が公開されました！\nタイトル: {instance.title}\nURL: {instance.full_url}"
        send_slack_notification(text)