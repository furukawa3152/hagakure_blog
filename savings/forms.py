from django import forms
from django.core.exceptions import ValidationError

from .models import RewardSpend, SavingEntry


class HalfWidthAmountMixin:
    def configure_amount_field(self, label):
        self.fields["amount"].label = label
        self.fields["amount"].required = True
        self.fields["amount"].widget = forms.TextInput(
            attrs={
                "inputmode": "none",
                "pattern": "[0-9]*",
                "autocomplete": "off",
                "placeholder": "例: 480",
                "required": "required",
                "readonly": "readonly",
            }
        )

    def clean_amount(self):
        value = self.cleaned_data["amount"]
        raw_value = str(self.data.get(self.add_prefix("amount"), value)).strip()
        if not raw_value.isascii() or not raw_value.isdecimal():
            raise ValidationError("金額は半角数字だけで入力してください。")

        amount = int(raw_value)
        if amount < 1:
            raise ValidationError("金額は1円以上で入力してください。")
        if amount > 9_999_999:
            raise ValidationError("金額は9,999,999円以下で入力してください。")
        return amount


class SavingEntryForm(HalfWidthAmountMixin, forms.ModelForm):
    class Meta:
        model = SavingEntry
        fields = ["title", "category", "amount"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].required = False
        self.fields["title"].widget.attrs.update({
            "placeholder": "例: コンビニのカフェラテ",
            "autocomplete": "off",
        })
        self.fields["category"].required = True
        category_choices = [
            (value, label)
            for value, label in self.fields["category"].choices
            if value
        ]
        self.fields["category"].choices = [("", "カテゴリを選択")] + category_choices
        self.fields["category"].widget.attrs.update({"required": "required"})
        self.configure_amount_field("浮いた金額")


class RewardSpendForm(HalfWidthAmountMixin, forms.ModelForm):
    class Meta:
        model = RewardSpend
        fields = ["title", "amount"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({
            "placeholder": "例: 週末のサウナ",
            "autocomplete": "off",
        })
        self.configure_amount_field("使った金額")
