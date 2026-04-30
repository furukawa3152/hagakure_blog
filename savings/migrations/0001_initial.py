# Generated manually for the savings app.

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RewardSpend",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=80, verbose_name="満足度の高い使い道")),
                ("amount", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(9999999)], verbose_name="使った金額")),
                ("satisfaction", models.PositiveSmallIntegerField(default=5, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name="満足度")),
                ("spent_on", models.DateField(default=django.utils.timezone.localdate, verbose_name="使った日")),
                ("note", models.TextField(blank=True, verbose_name="メモ")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="作成日時")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新日時")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reward_spends", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "ごほうび支出",
                "verbose_name_plural": "ごほうび支出",
                "ordering": ["-spent_on", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="SavingEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=80, verbose_name="我慢したもの")),
                ("category", models.CharField(choices=[("drink", "飲み物"), ("snack", "おやつ・外食"), ("book", "本・教材"), ("subscription", "サブスク"), ("game", "ゲーム・娯楽"), ("clothes", "服・雑貨"), ("other", "その他")], max_length=24, verbose_name="カテゴリ")),
                ("amount", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(9999999)], verbose_name="浮いた金額")),
                ("avoided_on", models.DateField(default=django.utils.timezone.localdate, verbose_name="我慢した日")),
                ("note", models.TextField(blank=True, verbose_name="メモ")),
                ("roast_text", models.CharField(blank=True, max_length=160, verbose_name="辛口コメント")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="作成日時")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新日時")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="saving_entries", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "実質貯金記録",
                "verbose_name_plural": "実質貯金記録",
                "ordering": ["-avoided_on", "-created_at"],
            },
        ),
    ]
