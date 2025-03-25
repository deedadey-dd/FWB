from django.db.models import Sum
from datetime import datetime
from .models import Contribution, ContributionSetting


def allocate_contribution(user, amount, contribution_date):
    """
    Allocate the given amount to the earliest unpaid months in order.
    """
    current_year = contribution_date.year  # Use the actual year of the contribution

    try:
        contribution_setting = ContributionSetting.objects.get(year=current_year)
        monthly_amount = contribution_setting.amount  # The required monthly contribution
    except ContributionSetting.DoesNotExist:
        return  # If no setting exists, do nothing

    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # Get user's contributions for the current year, grouped by month
    user_contributions = Contribution.objects.filter(
        user=user,
        date_contributed__year=current_year,
        contribution_type="monthly"
    ).values("date_contributed__month").annotate(total=Sum("amount"))

    # Create a dictionary to track paid months
    paid_months = {entry["date_contributed__month"]: entry["total"] for entry in user_contributions}

    remaining_amount = amount

    # **Start from the earliest unpaid month, not from January always**
    for month_index in range(1, 13):  # Months are indexed from 1 (Jan) to 12 (Dec)
        if remaining_amount <= 0:
            break  # Stop if no amount is left to allocate

        paid_so_far = paid_months.get(month_index, 0)
        due = max(monthly_amount - paid_so_far, 0)  # Amount still due for this month

        if due > 0:
            allocation = min(due, remaining_amount)  # Allocate what we can
            Contribution.objects.create(
                user=user,
                amount=allocation,
                date_contributed=datetime(current_year, month_index, 1),  # Assign correct month
                contribution_type="monthly",
                recorded_by=user  # Ensure the correct manager records it
            )
            remaining_amount -= allocation  # Deduct the allocated amount
