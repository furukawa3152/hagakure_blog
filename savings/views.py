from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import RewardSpendForm, SavingEntryForm
from .models import RewardSpend, SavingEntry
from .services import build_roast_text


def _money_or_zero(value):
    return value or 0


@require_POST
def dev_login(request):
    if not settings.DEBUG:
        raise Http404()

    user_model = get_user_model()
    user, _ = user_model.objects.get_or_create(
        username="savings-dev-user",
        defaults={
            "email": "savings-dev@example.com",
            "is_staff": True,
        },
    )
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")

    next_url = request.POST.get("next") or request.GET.get("next") or "/savings/"
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = "/savings/"
    return redirect(next_url)


@login_required
def dashboard(request):
    saving_form = SavingEntryForm()
    reward_form = RewardSpendForm()

    savings = SavingEntry.objects.filter(user=request.user)
    rewards = RewardSpend.objects.filter(user=request.user)

    total_saved = _money_or_zero(savings.aggregate(total=Sum("amount"))["total"])
    total_spent = _money_or_zero(rewards.aggregate(total=Sum("amount"))["total"])
    reward_count = rewards.count()

    context = {
        "saving_form": saving_form,
        "reward_form": reward_form,
        "total_saved": total_saved,
        "total_spent": total_spent,
        "balance": total_saved - total_spent,
        "saving_count": savings.count(),
        "reward_count": reward_count,
        "recent_savings": savings[:3],
        "recent_rewards": rewards[:3],
    }
    return render(request, "savings/dashboard.html", context)


@login_required
@require_POST
def create_saving(request):
    form = SavingEntryForm(request.POST)
    if form.is_valid():
        saving = form.save(commit=False)
        saving.user = request.user
        saving.roast_text = build_roast_text(saving.category, saving.title)
        saving.save()
        messages.success(request, saving.roast_text)
    else:
        messages.error(request, "入力内容を確認してください。金額は1円以上で登録できます。")
    return redirect("savings:dashboard")


@login_required
@require_POST
def create_reward(request):
    form = RewardSpendForm(request.POST)
    if form.is_valid():
        reward = form.save(commit=False)
        reward.user = request.user
        reward.save()
        messages.success(request, "いい浪費です。満足度の低い出費より、だいぶ筋が通っています。")
    else:
        messages.error(request, "入力内容を確認してください。満足度は1から5で登録できます。")
    return redirect("savings:dashboard")


@login_required
@require_POST
def delete_saving(request, pk):
    saving = get_object_or_404(SavingEntry, pk=pk, user=request.user)
    saving.delete()
    messages.success(request, "実質貯金の記録を削除しました。")
    return redirect("savings:dashboard")


@login_required
@require_POST
def delete_reward(request, pk):
    reward = get_object_or_404(RewardSpend, pk=pk, user=request.user)
    reward.delete()
    messages.success(request, "使い道の記録を削除しました。")
    return redirect("savings:dashboard")
