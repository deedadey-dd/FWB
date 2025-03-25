# import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.utils.timezone import now
from .models import Contribution, ContributionSetting, ContributionRecord, ExtraContribution
from .forms import ContributionForm
from .utils import allocate_contribution
from django.db.models.functions import ExtractYear, ExtractMonth
from django.db.models import Sum
from datetime import datetime
from users.models import CustomUser
from django.contrib import messages
from collections import defaultdict


def is_manager(user):
    return user.is_authenticated and user.is_staff  # Ensure `is_manager` exists in the user model


# @login_required
# @user_passes_test(is_manager)
# def record_contribution(request):
#     if not request.user.is_staff:  # Only managers can enter contributions
#         messages.error(request, "You do not have permission to record contributions.")
#         return redirect("home")
#
#     if request.method == "POST":
#         form = ContributionForm(request.POST)
#         if form.is_valid():
#             contribution = form.save(commit=False)
#             contribution.recorded_by = request.user
#
#             try:
#                 # Save a bulk record before allocating it to unpaid months
#                 contribution_record = ContributionRecord.objects.create(
#                     user=contribution.user,
#                     amount=contribution.amount,
#                     contribution_type=contribution.contribution_type,
#                     recorded_by=request.user
#                 )
#
#                 # Allocate the contribution if it's a monthly one
#                 if contribution.contribution_type == "Monthly":
#                     allocate_contribution(contribution.user, contribution.amount, contribution.date_contributed)
#                 # If it is an extra contribution, save it as such.
#                 else:
#                     reason = form.cleaned_data["new_reason"] or form.cleaned_data["previous_reason"]
#                     extra_contribution = ExtraContribution.objects.create(
#                         user=request.user,
#                         amount=contribution.amount,
#                         reason=reason
#                     )
#                     extra_contribution.save()
#
#                 # Send Email Notification
#                 send_mail(
#                     "Contribution Recorded",
#                     f"Dear {contribution.user.first_name},\n\nAn amount of {contribution.amount} has been recorded for you as {contribution.contribution_type} contribution.\n\nThank you!",
#                     "deedadey@vivaldi.net",
#                     [contribution.user.email],
#                     fail_silently=True,
#                 )
#
#                 messages.success(request, "Contribution recorded successfully.")
#                 return redirect("record_contribution")
#             except Exception as e:
#                 messages.error(request, f"An error occurred: {e}")
#
#     else:
#         form = ContributionForm()
#
#     return render(request, "contributions/record_contribution.html", {"form": form})


@login_required
@user_passes_test(is_manager)
def record_contribution(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to record contributions.")
        return redirect("home")

    if request.method == "POST":
        form = ContributionForm(request.POST, user=request.user)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.recorded_by = request.user

            try:
                # Save the contribution record
                ContributionRecord.objects.create(
                    user=contribution.user,
                    amount=contribution.amount,
                    contribution_type=contribution.contribution_type,
                    recorded_by=request.user
                )

                # Allocate if it's a monthly contribution
                if contribution.contribution_type == "monthly":
                    allocate_contribution(contribution.user, contribution.amount, contribution.date_contributed)

                else:  # Extra Contribution
                    reason = form.cleaned_data["new_reason"] or form.cleaned_data["previous_reason"]
                    if reason:
                        ExtraContribution.objects.create(
                            user=contribution.user,
                            amount=contribution.amount,
                            reason=reason
                        )

                # Send notification email
                send_mail(
                    "Contribution Recorded",
                    f"Dear {contribution.user.first_name},\n\nAn amount of {contribution.amount} has been recorded for you as {contribution.contribution_type} contribution.\n\nThank you!",
                    "deedadey@vivaldi.net",
                    [contribution.user.email],
                    fail_silently=True,
                )

                messages.success(request, "Contribution recorded successfully.")
                return redirect("record_contribution")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")

    else:
        form = ContributionForm(user=request.user)

    return render(request, "contributions/record_contribution.html", {"form": form})


# def dashboard(request):
#     user = request.user
#     current_date = now()
#     current_year = datetime.now().year
#     contribution_setting = ContributionSetting.objects.filter(year=current_year).first()
#     monthly_amount = contribution_setting.amount if contribution_setting else 0
#
#     # Fetching standard contributions
#     past_contributions = (
#         Contribution.objects.filter(user=user)
#         .annotate(year=ExtractYear('date_contributed'), month=ExtractMonth('date_contributed'))
#         .order_by('-year', '-month')
#     )
#
#     # Fetching extra contributions
#     extra_contributions = ExtraContribution.objects.filter(user=user).order_by('-date_contributed')
#
#     # Organizing data into a dictionary format
#     contributions = {}
#     for contrib in past_contributions:
#         year = contrib.year
#         month = contrib.month
#         if year not in contributions:
#             contributions[year] = {}
#         contributions[year][month] = True  # Mark as paid
#
#     # Arrears calculation (unpaid months)
#     total_arrears = 0
#     for year, months in contributions.items():
#         for month in range(1, 13):  # Loop through all months
#             if month not in months:  # If a month is missing, it means unpaid
#                 months[month] = False
#                 total_arrears += 1
#
#     # Required amount to close the year
#     total_due = total_arrears * monthly_amount
#
#     # Determine health status
#     if total_arrears == 0:
#         health_status = "green"
#     elif total_arrears <= 2:
#         health_status = "yellow"
#     elif total_arrears >= 4:
#         health_status = "red"
#     else:
#         health_status = "blue"  # Paid in advance
#
#     # List of month names
#     month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
#
#     # Fetch extra contributions and group by reason
#     extra_contributions = (
#         ExtraContribution.objects.filter(user=user)
#         .values("reason")
#         .annotate(total_amount=Sum("amount"))
#     )
#
#     # Extract first word of each reason
#     extra_contributions_dict = {reason.split()[0]: total_amount for reason, total_amount in
#                                 extra_contributions.values_list("reason", "total_amount") if reason is not None}
#
#     context = {
#         'current_date': current_date,
#         'contributions': contributions,
#         'total_arrears': total_arrears,
#         'total_due': total_due,
#         'health_status': health_status,
#         'month_names': month_names,
#         'monthly_amount': monthly_amount,
#         'current_year': current_year,
#         'first_name': user.first_name,
#         'extra_contributions_dict': extra_contributions_dict,  # Include extra contributions
#     }
#
#     return render(request, 'contributions/dashboard.html', context)


def dashboard(request):
    user = request.user
    current_date = now()
    current_year = current_date.year
    current_month = current_date.month  # Get current month
    last_two_years = [current_year - 1, current_year]  # Last year and this year only

    contribution_setting = ContributionSetting.objects.filter(year=current_year).first()
    monthly_amount = contribution_setting.amount if contribution_setting else 0

    # Fetching standard contributions for the last two years
    past_contributions = (
        Contribution.objects.filter(user=user, date_contributed__year__in=last_two_years)
        .annotate(year=ExtractYear('date_contributed'), month=ExtractMonth('date_contributed'))
        .values("year", "month")
        .annotate(total_amount=Sum("amount"))  # Sum contributions per month
        .order_by('-year', '-month')
    )

    # Organizing data into a dictionary format
    contributions = {year: {month: 0 for month in range(1, 13)} for year in last_two_years}
    for contrib in past_contributions:
        contributions[contrib["year"]][contrib["month"]] = contrib["total_amount"]  # Store summed contributions

    # Arrears calculation (only for the current year and up to the current month)
    arrears_count = sum(1 for month in range(1, current_month + 1) if contributions[current_year][month] < monthly_amount)

    # Required amount to close arrears
    total_due = sum(max(monthly_amount - contributions[current_year][month], 0) for month in range(1, current_month + 1))

    # Determine health status based on months missed (arrears_count)
    if arrears_count == 0:
        health_status = "green"  # Fully up to date
    elif arrears_count <= 2:
        health_status = "yellow"  # 1 or 2 months behind
    elif arrears_count >= 4:
        health_status = "red"  # More than 4 months behind
    else:
        health_status = "blue"  # Paid in advance

    # Calculate total_due_year_end (amount needed to complete the year)
    total_due_year_end = total_due  # Start with the total needed to catch up

    for month in range(current_month + 1, 13):  # Loop from next month to December
        total_due_year_end += monthly_amount  # Add the monthly amount for each remaining month

    # List of month names
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Fetch extra contributions and group by reason
    extra_contributions = (
        ExtraContribution.objects.filter(user=user)
        .values("reason")
        .annotate(total_amount=Sum("amount"))
    )

    extra_contributions_dict = {
        reason.split()[0]: total_amount for reason, total_amount in extra_contributions.values_list("reason", "total_amount") if reason is not None
    }

    context = {
        'current_date': current_date,
        'contributions': contributions,
        'total_arrears': arrears_count,
        'total_due': total_due,
        'health_status': health_status,
        'month_names': month_names,
        'monthly_amount': monthly_amount,
        'current_year': current_year,
        'last_two_years': last_two_years,  # Send last two years to template
        'current_month': current_month,  # Pass the current month to the template
        'first_name': user.first_name,
        'extra_contributions_dict': extra_contributions_dict,
        'month_range': range(1, 13),
        'total_due_year_end': total_due_year_end,

    }

    return render(request, 'contributions/dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)  # Only managers can access
def manager_dashboard(request):
    # Get year from GET request or default to the current year
    selected_year = request.GET.get("year")
    current_year = datetime.now().year
    year = int(selected_year) if selected_year else current_year
    years = list(range(2020, current_year +1))
    current_month = datetime.now().month

    # Fetch contribution setting (amount per month)
    try:
        contribution_setting = ContributionSetting.objects.get(year=year)
        monthly_amount = contribution_setting.amount
    except ContributionSetting.DoesNotExist:
        monthly_amount = 0  # Default if not set

    # List of all users
    users = CustomUser.objects.filter(is_staff=False)

    # Months mapping
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    user_data = []
    total_contributed = 0  # Track total contributions for the year

    for user in users:
        # Get the total contributions grouped by month
        contributions = (
            Contribution.objects.filter(user=user, date_contributed__year=year)
            .values("date_contributed__month")
            .annotate(total_paid=Sum("amount"))
        )

        # Create a dictionary for contributions per month
        contributions_dict = {entry["date_contributed__month"]: entry["total_paid"] for entry in contributions}

        # Calculate totals
        total_paid = sum(contributions_dict.values())
        due_up_to_date = (current_month * monthly_amount) - total_paid  # Can be negative
        due_full_year = (12 * monthly_amount) - total_paid  # Always non-negative

        # Prepare row data
        row = {
            "name": f"{user.first_name} {user.last_name}",
            "monthly_contributions": [contributions_dict.get(month_index, 0) for month_index in range(1, 13)],
            "total_paid": total_paid,
            "due_up_to_date": due_up_to_date,
            "due_full_year": max(0, due_full_year),
        }

        user_data.append(row)
        total_contributed += total_paid  # Accumulate total contributions

    # Calculate summary statistics
    total_expected_up_to_now = current_month * monthly_amount * users.count()
    total_expected_full_year = 12 * monthly_amount * users.count()
    total_due_up_to_now = total_expected_up_to_now - total_contributed
    total_due_full_year = total_expected_full_year - total_contributed

    # Calculate expected contributions
    total_expected_up_to_now = current_month * monthly_amount * users.count()
    total_expected_full_year = 12 * monthly_amount * users.count()

    # Calculate amount due
    total_due_up_to_now = total_expected_up_to_now - total_contributed
    total_due_full_year = total_expected_full_year - total_contributed

    return render(request, "contributions/manager_dashboard.html", {
        "user_data": user_data,
        "month_names": month_names,
        "year": year,
        "years": years,
        "total_contributed": total_contributed,
        "total_expected_up_to_now": total_expected_up_to_now,
        "total_expected_full_year": total_expected_full_year,
        "total_due_up_to_now": total_due_up_to_now,
        "total_due_full_year": total_due_full_year,
    })


@login_required
@user_passes_test(is_manager)
def view_contributions(request):
    contributions = ContributionRecord.objects.select_related("user", "recorded_by").order_by("-recorded_at")

    return render(request, "contributions/contributions_list.html", {"contributions": contributions})


@login_required
@user_passes_test(lambda u: u.is_staff)
def extra_contributions_view(request):
    selected_year = request.GET.get("year")
    current_year = datetime.now().year
    year = int(selected_year) if selected_year else current_year
    years = list(range(2020, current_year + 1))

    # Fetch extra contributions (excluding 'Regular')
    extra_contributions = ExtraContribution.objects.filter(date_contributed__year=year)

    # Calculate Total Extra Contributions
    total_extra_contributions = extra_contributions.aggregate(total=Sum("amount"))["total"] or 0

    # Group by reason and calculate totals
    reason_contributions = (
        extra_contributions.values("reason")
        .annotate(total=Sum("amount"))
        .order_by("reason")
    )

    # Expected total per reason
    expected_per_reason = {
        "Building Fund": 50000,
        "Missions": 20000,
        "Special Offering": 10000,
    }

    # Prepare data for table
    user_contributions = defaultdict(lambda: defaultdict(int))
    for contribution in extra_contributions:
        user_contributions[contribution.user][contribution.reason] += contribution.amount  # ✅ Fix field name

    user_data = [
        {
            "name": f"{user.first_name} {user.last_name}",
            "extra_contributions": contributions,
            "total_paid": sum(contributions.values()),
        }
        for user, contributions in user_contributions.items()
    ]

    # Get unique reasons
    extra_reasons = list(extra_contributions.values_list("reason", flat=True).distinct())  # ✅ Fix field name

    # Calculate actual vs expected per reason
    reason_summary = []
    for reason in extra_reasons:
        actual_total = next((r["total"] for r in reason_contributions if r["reason"] == reason), 0)
        expected_total = expected_per_reason.get(reason, 0)
        percentage = (actual_total / expected_total * 100) if expected_total > 0 else 0
        reason_summary.append({"reason": reason, "actual": actual_total, "expected": expected_total, "percentage": round(percentage, 2)})

    print(extra_reasons)

    return render(request, "contributions/extra_contributions.html", {
        "user_data": user_data,
        "year": year,
        "years": years,
        "extra_reasons": extra_reasons,
        "total_extra_contributions": total_extra_contributions,
        "reason_summary": reason_summary,
    })
