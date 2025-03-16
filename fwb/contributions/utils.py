from django.db.models import Sum
from datetime import datetime
from .models import Contribution, ContributionSetting
from .models import MonthlyContribution


def allocate_contribution(user, amount):
    """
    Allocate the given amount to the earliest unpaid months.
    """
    current_year = datetime.now().year
    try:
        contribution_setting = ContributionSetting.objects.get(year=current_year)
        monthly_amount = contribution_setting.amount  # The required monthly contribution
    except ContributionSetting.DoesNotExist:
        return  # If no setting exists, do nothing

    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # Get the user's existing contributions for the current year
    user_contributions = Contribution.objects.filter(
        user=user, date_contributed__year=current_year, contribution_type="monthly"
    ).values("date_contributed__month").annotate(total=Sum("amount"))

    # Create a dictionary to track paid months
    paid_months = {entry["date_contributed__month"]: entry["total"] for entry in user_contributions}

    remaining_amount = amount

    for month_index, month_name in enumerate(months, start=1):
        if remaining_amount <= 0:
            break  # Stop if no amount is left to allocate

        # Get how much has been paid for this month
        paid_so_far = paid_months.get(month_index, 0)
        due = max(monthly_amount - paid_so_far, 0)  # Amount still due for this month

        if due > 0:
            allocation = min(due, remaining_amount)  # Allocate what we can
            Contribution.objects.create(
                user=user,
                amount=allocation,
                date_contributed=datetime(current_year, month_index, 1),
                contribution_type="monthly",
                recorded_by=user  # Assuming the recorded_by is the same user, adjust if needed
            )
            remaining_amount -= allocation  # Deduct the allocated amount


