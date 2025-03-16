from django.contrib import admin
from .models import Contribution, MonthlyContribution, ExtraContribution

@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "date_contributed", "contribution_type", "recorded_by")
    search_fields = ("user__username", "user__email")
    list_filter = ("contribution_type", "date_contributed")

@admin.register(MonthlyContribution)
class MonthlyContributionAdmin(admin.ModelAdmin):
    list_display = ("user", "year", "month", "amount")
    search_fields = ("user__username", "user__email")

@admin.register(ExtraContribution)
class ExtraContributionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "date_contributed")
    search_fields = ("user__username", "user__email")
