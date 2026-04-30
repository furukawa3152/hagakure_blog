from django.contrib import admin

from .models import RewardSpend, SavingEntry


@admin.register(SavingEntry)
class SavingEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "amount", "avoided_on", "created_at")
    list_filter = ("category", "avoided_on", "created_at")
    search_fields = ("title", "note", "user__username", "user__email")


@admin.register(RewardSpend)
class RewardSpendAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "amount", "satisfaction", "spent_on", "created_at")
    list_filter = ("satisfaction", "spent_on", "created_at")
    search_fields = ("title", "note", "user__username", "user__email")
