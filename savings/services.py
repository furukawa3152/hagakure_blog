import json
from pathlib import Path

from .models import SavingEntry


DEFAULT_ROASTS_BY_CATEGORY = {
    SavingEntry.CATEGORY_DRINK: [
        "その一杯、買わなくても人類は存続しました。",
        "水分補給と気分転換を混同しなかったのは偉いです。",
    ],
    SavingEntry.CATEGORY_SNACK: [
        "胃袋の一瞬の拍手より、残高の沈黙を選びました。",
        "未来の自分が、糖分より現金を歓迎しています。",
    ],
    SavingEntry.CATEGORY_BOOK: [
        "積ん読タワーの増築許可は却下されました。",
        "読了予定のない知識欲に、今日は予算が下りませんでした。",
    ],
    SavingEntry.CATEGORY_SUBSCRIPTION: [
        "見ていない月額課金に、また家賃を払わずに済みました。",
        "使っていない便利さほど高いものはありません。",
    ],
    SavingEntry.CATEGORY_GAME: [
        "ログインボーナスより現実のボーナスを取りました。",
        "今日のクエスト報酬は、使わなかった現金です。",
    ],
    SavingEntry.CATEGORY_CLOTHES: [
        "クローゼットの空き容量にも限界という概念があります。",
        "似た服を買う儀式を一回スキップしました。",
    ],
    SavingEntry.CATEGORY_OTHER: [
        "買わない判断にも、たまには価値があります。",
        "曖昧な欲望に領収書を発行せずに済みました。",
    ],
}


def load_roasts_by_category():
    roasts_path = Path(__file__).resolve().parent / "data" / "roasts.json"
    try:
        with roasts_path.open(encoding="utf-8") as roasts_file:
            data = json.load(roasts_file)
    except (OSError, json.JSONDecodeError):
        return DEFAULT_ROASTS_BY_CATEGORY

    if not isinstance(data, dict):
        return DEFAULT_ROASTS_BY_CATEGORY

    cleaned = {}
    for category, roasts in data.items():
        if isinstance(category, str) and isinstance(roasts, list):
            cleaned[category] = [text for text in roasts if isinstance(text, str) and text.strip()]

    return cleaned or DEFAULT_ROASTS_BY_CATEGORY


def build_roast_text(category, title):
    roasts_by_category = load_roasts_by_category()
    choices = (
        roasts_by_category.get(category)
        or roasts_by_category.get(SavingEntry.CATEGORY_OTHER)
        or DEFAULT_ROASTS_BY_CATEGORY[SavingEntry.CATEGORY_OTHER]
    )
    index = sum(ord(char) for char in title) % len(choices)
    return choices[index]
