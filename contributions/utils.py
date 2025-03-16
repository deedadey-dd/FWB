from datetime import datetime
from .models import MonthlyContribution

def allocate_contribution(user, amount, year=None):
    """Distribute a contribution amount into monthly slots until exhausted."""
    if year is None:
        year = datetime.now().year

    remaining_amount = amount
    for month in range(1, 13):
        if remaining_amount <= 0:
            break

        monthly_contrib, created = MonthlyContribution.objects.get_or_create(
            user=user,
            year=year,
            month=month,
            defaults={"amount": 0}
        )

        # Allocate money to this month
        monthly_contrib.amount += remaining_amount
        monthly_contrib.save()

        remaining_amount = 0  # Stop allocation after first month
