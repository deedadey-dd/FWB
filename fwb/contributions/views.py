# import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.utils.timezone import now
from .models import Contribution, ContributionSetting
from .forms import ContributionForm
from .utils import allocate_contribution
from django.db.models.functions import ExtractYear, ExtractMonth
from django.db.models import Sum
from datetime import datetime
from users.models import CustomUser


def is_manager(user):
    return user.is_authenticated and user.is_staff  # Ensure `is_manager` exists in the user model


@login_required
@user_passes_test(is_manager)
def record_contribution(request):
    if not request.user.is_staff:  # Only managers can enter contributions
        messages.error(request, "You do not have permission to record contributions.")
        return redirect("home")

    if request.method == "POST":
        form = ContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.recorded_by = request.user
            contribution.save()

            # Allocate to months if it's a monthly contribution
            if contribution.contribution_type == "monthly":
                allocate_contribution(contribution.user, contribution.amount)

            # Send Email Notification
            send_mail(
                "Contribution Recorded",
                f"Dear {contribution.user.first_name},\n\nA contribution of {contribution.amount} has been recorded for you.\n\nThank you!",
                "deedadey@vivaldi.net",
                [contribution.user.email],
                fail_silently=True,
            )

            messages.success(request, "Contribution recorded successfully.")
            return redirect("record_contribution")
    else:
        form = ContributionForm()

    return render(request, "contributions/record_contribution.html", {"form": form})


def dashboard(request):
    user = request.user
    current_date = now()
    current_year = datetime.now().year
    contribution_setting = ContributionSetting.objects.filter(year=current_year).first()
    monthly_amount = contribution_setting.amount if contribution_setting else 0

    # Extract year and month dynamically
    past_contributions = (
        Contribution.objects.filter(user=user)
        .annotate(year=ExtractYear('date_contributed'), month=ExtractMonth('date_contributed'))
        .order_by('-year', '-month')
    )

    # Organizing data into a dictionary format
    contributions = {}
    for contrib in past_contributions:
        year = contrib.year
        month = contrib.month
        if year not in contributions:
            contributions[year] = {}
        contributions[year][month] = True  # Mark as paid

    # Arrears calculation (unpaid months)
    total_arrears = 0
    for year, months in contributions.items():
        for month in range(1, 13):  # Loop through all months
            if month not in months:  # If a month is missing, it means unpaid
                months[month] = False
                total_arrears += 1

    # Required amount to close the year (assuming each month = $100)
    total_due = total_arrears * monthly_amount

    # Determine health status
    if total_arrears == 0:
        health_status = "green"
    elif total_arrears <= 2:
        health_status = "yellow"
    elif total_arrears >= 4:
        health_status = "red"
    else:
        health_status = "blue"  # Paid in advance

    # List of month names
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    context = {
        'current_date': current_date,
        'contributions': contributions,
        'total_arrears': total_arrears,
        'total_due': total_due,
        'health_status': health_status,
        'month_names': month_names,
        'monthly_amount': monthly_amount,
        'current_year': current_year,
        'first_name': user.first_name
    }

    return render(request, 'contributions/dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)  # Only managers can access
def manager_dashboard(request):
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Fetch contribution setting (amount per month)
    try:
        contribution_setting = ContributionSetting.objects.get(year=current_year)
        monthly_amount = contribution_setting.amount
    except ContributionSetting.DoesNotExist:
        monthly_amount = 0  # Default if not set

    # List of all users
    users = CustomUser.objects.all()

    # Months mapping
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    user_data = []

    for user in users:
        # Get the total contributions grouped by month
        contributions = (
            Contribution.objects.filter(user=user, date_contributed__year=current_year)
            .values("date_contributed__month")
            .annotate(total_paid=Sum("amount"))
        )

        # Create a dictionary for contributions per month
        contributions_dict = {entry["date_contributed__month"]: entry["total_paid"] for entry in contributions}

        # Prepare row data
        row = {
            "name": f"{user.first_name} {user.last_name}",
            "monthly_contributions": [],
            "total_paid": sum(contributions_dict.values()),
            "due_up_to_date": max(0, (current_month * monthly_amount) - sum(contributions_dict.values())),
            "due_full_year": max(0, (12 * monthly_amount) - sum(contributions_dict.values())),
        }

        # Populate monthly contributions
        for month_index in range(1, 13):  # 1 to 12
            row["monthly_contributions"].append(contributions_dict.get(month_index, 0))

        user_data.append(row)

    return render(request, "contributions/manager_dashboard.html", {
        "user_data": user_data,
        "month_names": month_names,
    })

