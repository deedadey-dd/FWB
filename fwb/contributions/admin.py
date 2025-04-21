from django.contrib import admin
from django.core.exceptions import PermissionDenied
from .models import Contribution, MonthlyContribution, ExtraContribution, ContributionSetting, Expense


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


@admin.register(ContributionSetting)
class ContributionSettingAdmin(admin.ModelAdmin):
    list_display = ('year', 'amount', 'set_by')
    search_fields = ('year',)


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("description", "amount", "category", "date", "recorded_by")

    def save_model(self, request, obj, form, change):
        if not request.user.is_staff:
            raise PermissionDenied("Only staff members can add expenses.")
        obj.recorded_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Expense, ExpenseAdmin)
