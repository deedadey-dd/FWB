from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.utils.timezone import now
from .models import Contribution
from .forms import ContributionForm
from .utils import allocate_contribution
from django.db.models.functions import ExtractYear, ExtractMonth


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
                "admin@welfaresociety.com",
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
    total_due = total_arrears * 100

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
        'month_names': month_names,  # Pass the list to the template
    }

    return render(request, 'contributions/dashboard.html', context)


