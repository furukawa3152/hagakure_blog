from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class SavingEntry(models.Model):
    CATEGORY_DRINK = "drink"
    CATEGORY_SNACK = "snack"
    CATEGORY_BOOK = "book"
    CATEGORY_SUBSCRIPTION = "subscription"
    CATEGORY_GAME = "game"
    CATEGORY_CLOTHES = "clothes"
    CATEGORY_OTHER = "other"

    CATEGORY_CHOICES = [
        (CATEGORY_DRINK, "飲み物"),
        (CATEGORY_SNACK, "おやつ・外食"),
        (CATEGORY_BOOK, "本・教材"),
        (CATEGORY_SUBSCRIPTION, "サブスク"),
        (CATEGORY_GAME, "ゲーム・娯楽"),
        (CATEGORY_CLOTHES, "服・雑貨"),
        (CATEGORY_OTHER, "その他"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saving_entries",
    )
    title = models.CharField("我慢したもの", max_length=80)
    category = models.CharField("カテゴリ", max_length=24, choices=CATEGORY_CHOICES)
    amount = models.PositiveIntegerField(
        "浮いた金額",
        validators=[MinValueValidator(1), MaxValueValidator(9_999_999)],
    )
    avoided_on = models.DateField("我慢した日", default=timezone.localdate)
    note = models.TextField("メモ", blank=True)
    roast_text = models.CharField("辛口コメント", max_length=160, blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        ordering = ["-avoided_on", "-created_at"]
        verbose_name = "実質貯金記録"
        verbose_name_plural = "実質貯金記録"

    def __str__(self):
        return f"{self.title} ({self.amount}円)"


class RewardSpend(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reward_spends",
    )
    title = models.CharField("満足度の高い使い道", max_length=80)
    amount = models.PositiveIntegerField(
        "使った金額",
        validators=[MinValueValidator(1), MaxValueValidator(9_999_999)],
    )
    satisfaction = models.PositiveSmallIntegerField(
        "満足度",
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    spent_on = models.DateField("使った日", default=timezone.localdate)
    note = models.TextField("メモ", blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        ordering = ["-spent_on", "-created_at"]
        verbose_name = "ごほうび支出"
        verbose_name_plural = "ごほうび支出"

    def __str__(self):
        return f"{self.title} ({self.amount}円)"
