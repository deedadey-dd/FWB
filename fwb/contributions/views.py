from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail, get_connection
from django.utils.timezone import now
from .models import Contribution, ContributionSetting, ContributionRecord, ExtraContribution
from .forms import ContributionForm
from .utils import allocate_contribution
from django.db.models.functions import ExtractYear, ExtractMonth
from django.db.models import Sum, Q
from datetime import datetime
from users.models import CustomUser
from collections import defaultdict
from decimal import Decimal
from django.conf import settings


def is_manager(user):
    return user.is_authenticated and user.is_staff  # Ensure `is_manager` exists in the user model


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
                    subject="FWB Contribution",
                    message=f"Dear {contribution.user.first_name},\n\nAn amount of {contribution.amount} has been "
                            f"recorded for you as {contribution.contribution_type} contribution.\n\nThank you!",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[contribution.user.email],
                    fail_silently=False,
                )

                messages.success(request, "Contribution recorded successfully.")
                return redirect("record_contribution")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")

    else:
        form = ContributionForm(user=request.user)

    return render(request, "contributions/record_contribution.html", {"form": form})


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

    # Identify **advance payments** (amount paid beyond required)
    total_paid_this_year = sum(contributions[current_year].values())  # Sum all contributions for current year
    expected_payment = current_month * monthly_amount  # Amount user should have paid by now

    advance_payment = max(0, total_paid_this_year - expected_payment)  # Extra amount paid

    # Convert advance payments into covered months
    months_covered_by_advance = advance_payment // monthly_amount

    # Remaining months in the year
    months_remaining = 12 - current_month

    # Adjust `total_due_year_end`
    months_due = max(0, months_remaining - months_covered_by_advance)
    total_due_year_end = months_due * monthly_amount

    # Determine health status
    if arrears_count == 0 and months_covered_by_advance == 0:
        health_status = "green"  # Fully up to date
    elif months_covered_by_advance > 0:
        health_status = "blue"  # Paid in advance
    elif arrears_count <= 2:
        health_status = "yellow"  # 1 or 2 months behind
    elif arrears_count >= 4:
        health_status = "red"  # More than 4 months behind
    else:
        health_status = "green"

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
        'last_two_years': last_two_years,
        'current_month': current_month,
        'first_name': user.first_name,
        'extra_contributions_dict': extra_contributions_dict,
        'month_range': range(1, 13),
        'total_due_year_end': total_due_year_end,
        'advance_payment': advance_payment,
    }

    return render(request, 'contributions/dashboard.html', context)


# @login_required
# @user_passes_test(lambda u: u.is_staff)  # Only managers can access
# def manager_dashboard(request):
#     # Get year from GET request or default to the current year
#     selected_year = request.GET.get("year")
#     current_year = datetime.now().year
#     year = int(selected_year) if selected_year else current_year
#     years = list(range(2020, current_year +1))
#     current_month = datetime.now().month
#
#     # Fetch contribution setting (amount per month)
#     try:
#         contribution_setting = ContributionSetting.objects.get(year=year)
#         monthly_amount = contribution_setting.amount
#     except ContributionSetting.DoesNotExist:
#         monthly_amount = 0  # Default if not set
#
#     # List of all users
#     users = CustomUser.objects.filter(is_staff=False)
#
#     # List of month names
#     month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
#
#     user_data = []
#     total_contributed = 0  # Track total contributions for the year
#
#     for user in users:
#         # Get the total contributions grouped by month
#         contributions = (
#             Contribution.objects.filter(user=user, date_contributed__year=year)
#             .values("date_contributed__month")
#             .annotate(total_paid=Sum("amount"))
#         )
#
#         # Create a dictionary for contributions per month
#         contributions_dict = {entry["date_contributed__month"]: entry["total_paid"] for entry in contributions}
#
#         # Calculate totals
#         total_paid = sum(contributions_dict.values())
#         due_up_to_date = (current_month * monthly_amount) - total_paid  # Can be negative
#         due_full_year = (12 * monthly_amount) - total_paid  # Always non-negative
#
#         # Prepare row data
#         row = {
#             "name": f"{user.first_name} {user.last_name}",
#             "monthly_contributions": [contributions_dict.get(month_index, 0) for month_index in range(1, 13)],
#             "total_paid": total_paid,
#             "due_up_to_date": due_up_to_date,
#             "due_full_year": max(0, due_full_year),
#         }
#
#         user_data.append(row)
#         total_contributed += total_paid  # Accumulate total contributions
#
#     # Calculate summary statistics
#     total_expected_up_to_now = current_month * monthly_amount * users.count()
#     total_expected_full_year = 12 * monthly_amount * users.count()
#     total_due_up_to_now = total_expected_up_to_now - total_contributed
#     total_due_full_year = total_expected_full_year - total_contributed
#
#     # Calculate expected contributions
#     total_expected_up_to_now = current_month * monthly_amount * users.count()
#     total_expected_full_year = 12 * monthly_amount * users.count()
#
#     # Calculate amount due
#     total_due_up_to_now = total_expected_up_to_now - total_contributed
#     total_due_full_year = total_expected_full_year - total_contributed
#
#     return render(request, "contributions/manager_dashboard.html", {
#         "user_data": user_data,
#         "month_names": month_names,
#         "year": year,
#         "years": years,
#         "total_contributed": total_contributed,
#         "total_expected_up_to_now": total_expected_up_to_now,
#         "total_expected_full_year": total_expected_full_year,
#         "total_due_up_to_now": total_due_up_to_now,
#         "total_due_full_year": total_due_full_year,
#     })
#

@login_required
@user_passes_test(is_manager)
def view_contributions(request):
    contributions = ContributionRecord.objects.select_related("user", "recorded_by").order_by("-recorded_at")

    return render(request, "contributions/contributions_list.html", {"contributions": contributions})


# @login_required
# @user_passes_test(lambda u: u.is_staff)  # Only managers can access
# def manager_dashboard(request):
#     # Get year from GET request or default to the current year
#     selected_year = request.GET.get("year")
#     current_year = datetime.now().year
#     year = int(selected_year) if selected_year else current_year
#     years = list(range(2020, current_year + 1))
#     current_month = datetime.now().month
#
#     # Fetch contribution setting (amount per month)
#     try:
#         contribution_setting = ContributionSetting.objects.get(year=year)
#         monthly_amount = contribution_setting.amount
#     except ContributionSetting.DoesNotExist:
#         monthly_amount = 0  # Default if not set
#
#     # Get search query and filter option
#     search_query = request.GET.get("search", "").strip()
#     filter_option = request.GET.get("filter", "")
#
#     # Fetch all non-staff users
#     users = CustomUser.objects.filter(is_staff=False)
#
#     # Apply search filter (Partial name search)
#     if search_query:
#         users = users.filter(
#             Q(first_name__icontains=search_query) |
#             Q(other_names__icontains=search_query) |  # If you have an 'other_names' field
#             Q(last_name__icontains=search_query)
#         )
#
#     # Prepare data
#     month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
#     user_data = []
#     total_contributed = 0  # Track total contributions for the year
#
#     for user in users:
#         # Get total contributions per month
#         contributions = (
#             Contribution.objects.filter(user=user, date_contributed__year=year)
#             .values("date_contributed__month")
#             .annotate(total_paid=Sum("amount"))
#         )
#
#         # Create dictionary for contributions per month
#         contributions_dict = {entry["date_contributed__month"]: entry["total_paid"] for entry in contributions}
#
#         # Calculate totals
#         total_paid = sum(contributions_dict.values())
#         due_up_to_date = (current_month * monthly_amount) - total_paid  # Can be negative (advanced payments)
#         due_full_year = (12 * monthly_amount) - total_paid  # Always non-negative
#
#         # Prepare user data row
#         row = {
#             "id": user.id,
#             "name": f"{user.first_name} {user.last_name}",
#             "monthly_contributions": [contributions_dict.get(month_index, 0) for month_index in range(1, 13)],
#             "total_paid": total_paid,
#             "due_up_to_date": due_up_to_date,
#             "due_full_year": max(0, due_full_year),
#             "months_defaulted": max(0, due_up_to_date // monthly_amount),
#         }
#
#         user_data.append(row)
#         total_contributed += total_paid
#
#     # Filtering logic
#     if filter_option == "defaulted_2_or_less":
#         user_data = [u for u in user_data if 1 <= u["months_defaulted"] <= 2]
#     elif filter_option == "defaulted_up_to_4":
#         user_data = [u for u in user_data if 3 <= u["months_defaulted"] <= 4]
#     elif filter_option == "defaulted_more_than_4":
#         user_data = [u for u in user_data if u["months_defaulted"] > 4]
#     elif filter_option == "up_to_date":
#         user_data = [u for u in user_data if u["due_up_to_date"] == 0]
#     elif filter_option == "advanced":
#         user_data = [u for u in user_data if u["due_up_to_date"] < 0]
#
#     # Sorting users alphabetically by first_name
#     user_data = sorted(user_data, key=lambda x: x["name"].split()[0])
#
#     # Calculate summary statistics
#     total_expected_up_to_now = current_month * monthly_amount * users.count()
#     total_expected_full_year = 12 * monthly_amount * users.count()
#     total_due_up_to_now = total_expected_up_to_now - total_contributed
#     total_due_full_year = total_expected_full_year - total_contributed
#
#     return render(request, "contributions/manager_dashboard.html", {
#         "user_data": user_data,
#         "month_names": month_names,
#         "year": year,
#         "years": years,
#         "total_contributed": total_contributed,
#         "total_expected_up_to_now": total_expected_up_to_now,
#         "total_expected_full_year": total_expected_full_year,
#         "total_due_up_to_now": total_due_up_to_now,
#         "total_due_full_year": total_due_full_year,
#         "search_query": search_query,
#         "filter_option": filter_option,
#     })


# @login_required
# @user_passes_test(lambda u: u.is_staff)  # Only managers can access
# def manager_dashboard(request):
#     selected_year = request.GET.get("year")
#     current_year = datetime.now().year
#     year = int(selected_year) if selected_year else current_year
#     years = list(range(2020, current_year + 1))
#     current_month = datetime.now().month
#
#     # Get contribution settings (monthly amount)
#     try:
#         contribution_setting = ContributionSetting.objects.get(year=year)
#         monthly_amount = contribution_setting.amount
#     except ContributionSetting.DoesNotExist:
#         monthly_amount = 0
#
#     search_query = request.GET.get("search", "").strip()
#     filter_option = request.GET.get("filter", "").strip()  # Get filter option
#
#     users = CustomUser.objects.filter(is_staff=False)
#
#     # Apply search filter (Partial name search)
#     if search_query:
#         users = users.filter(
#             Q(first_name__icontains=search_query) |
#             Q(other_names__icontains=search_query) |
#             Q(last_name__icontains=search_query)
#         )
#
#     month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
#     user_data = []
#     total_contributed = 0
#
#     for user in users:
#         # Get total contributions per month
#         contributions = (
#             Contribution.objects.filter(user=user, date_contributed__year=year)
#             .values("date_contributed__month")
#             .annotate(total_paid=Sum("amount"))
#         )
#
#         contributions_dict = {entry["date_contributed__month"]: entry["total_paid"] for entry in contributions}
#
#         # Calculate totals
#         total_paid = sum(contributions_dict.values())
#         due_up_to_date = (current_month * monthly_amount) - total_paid
#         due_full_year = (12 * monthly_amount) - total_paid
#         months_defaulted = max(0, due_up_to_date // monthly_amount)  # Convert to int in case it's Decimal
#
#         # Store data for filtering
#         user_entry = {
#             "id": user.id,
#             "name": f"{user.first_name} {user.last_name}",
#             "monthly_contributions": [contributions_dict.get(month, 0) for month in range(1, 13)],
#             "total_paid": total_paid,
#             "due_up_to_date": due_up_to_date,
#             "due_full_year": max(0, due_full_year),
#             "months_defaulted": int(months_defaulted),  # Ensure it’s an integer
#         }
#
#         user_data.append(user_entry)
#         total_contributed += total_paid
#
#     # **Filtering Logic**
#     print("Selected Filter:", filter_option)  # Debugging
#
#     if filter_option == "up_to_date":
#         user_data = [user for user in user_data if user["months_defaulted"] == 0]
#     elif filter_option == "defaulting_2":
#         user_data = [user for user in user_data if 1 <= user["months_defaulted"] <= 2]
#     elif filter_option == "defaulting_4":
#         user_data = [user for user in user_data if 3 <= user["months_defaulted"] <= 4]
#     elif filter_option == "defaulting_more":
#         user_data = [user for user in user_data if user["months_defaulted"] > 4]
#     elif filter_option == "paid_in_advance":
#         user_data = [user for user in user_data if user["due_up_to_date"] < Decimal(0)]  # Ensure Decimal comparison
#
#     print("Filtered User Data:", user_data)  # Debugging output to verify filtering
#
#     # Sorting users alphabetically
#     user_data = sorted(user_data, key=lambda x: x["name"].split()[0])
#
#     # Summary statistics
#     total_expected_up_to_now = current_month * monthly_amount * users.count()
#     total_expected_full_year = 12 * monthly_amount * users.count()
#     total_due_up_to_now = total_expected_up_to_now - total_contributed
#     total_due_full_year = total_expected_full_year - total_contributed
#
#     return render(request, "contributions/manager_dashboard.html", {
#         "user_data": user_data,
#         "month_names": month_names,
#         "year": year,
#         "years": years,
#         "total_contributed": total_contributed,
#         "total_expected_up_to_now": total_expected_up_to_now,
#         "total_expected_full_year": total_expected_full_year,
#         "total_due_up_to_now": total_due_up_to_now,
#         "total_due_full_year": total_due_full_year,
#         "search_query": search_query,
#         "filter_option": filter_option,
#     })


#############
@login_required
@user_passes_test(lambda u: u.is_staff)  # Only managers can access
def manager_dashboard(request):
    # Get year from GET request or default to the current year
    selected_year = request.GET.get("year")
    current_year = datetime.now().year
    year = int(selected_year) if selected_year else current_year
    years = list(range(2020, current_year + 1))
    current_month = datetime.now().month

    # Handle message sending if POST request
    if request.method == 'POST' and 'send_messages' in request.POST:
        recipient_type = request.POST.get('recipient_type')
        users_to_message = get_users_by_status(recipient_type, year, current_month)

        for user in users_to_message:
            status_message = get_status_message(user, year, current_month)
            subject = "FWB Status Reminder"
            message = f"Dear {user.first_name},\n\nThis is an automated message on your status.\n{status_message}\n\nThank you."
            connect()
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

        messages.success(request, f"Messages sent to {len(users_to_message)} members")
        return redirect('manager_dashboard')

    # Fetch contribution setting (amount per month)
    try:
        contribution_setting = ContributionSetting.objects.get(year=year)
        monthly_amount = contribution_setting.amount
    except ContributionSetting.DoesNotExist:
        monthly_amount = 0  # Default if not set

    # Get search query
    search_query = request.GET.get('search', '')

    # Get status filter
    status_filter = request.GET.get('status_filter', '')

    # Base queryset
    users = CustomUser.objects.filter(is_staff=False).order_by('first_name')

    # Apply search filter
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(other_names__icontains=search_query)
        )

    # List of month names
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

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

        # Calculate months defaulting (positive means behind, negative means ahead)
        months_defaulting = current_month - (total_paid / monthly_amount) if monthly_amount else 0

        # Prepare row data
        row = {
            "user": user,
            "name": f"{user.first_name} {user.last_name}",
            "monthly_contributions": [contributions_dict.get(month_index, 0) for month_index in range(1, 13)],
            "total_paid": total_paid,
            "due_up_to_date": due_up_to_date,
            "due_full_year": max(0, due_full_year),
            "months_defaulting": months_defaulting,
            "status": get_contribution_status(months_defaulting),
        }

        # Apply status filter if specified
        if not status_filter or row['status'] == status_filter:
            user_data.append(row)
            total_contributed += total_paid  # Accumulate total contributions

    # Calculate summary statistics
    total_expected_up_to_now = current_month * monthly_amount * users.count()
    total_expected_full_year = 12 * monthly_amount * users.count()
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
        "search_query": search_query,
        "status_filter": status_filter,
        "status_options": [
            ('', 'All Members'),
            ('up_to_date', 'Up to Date'),
            ('default_2', 'Defaulting by 2 months or less'),
            ('default_4', 'Defaulting by 2-4 months'),
            ('default_over_4', 'Defaulting by more than 4 months'),
            ('ahead', 'Paid in Advance'),
        ],
    })


def get_contribution_status(months_defaulting):
    """Determine the contribution status based on months defaulting"""
    if months_defaulting < 0:
        return 'ahead'
    elif months_defaulting == 0:
        return 'up_to_date'
    elif 0 < months_defaulting <= 2:
        return 'default_2'
    elif 2 <= months_defaulting < 4:
        return 'default_4'
    else:
        return 'default_over_4'


def get_users_by_status(status, year, current_month):
    """Get users filtered by their contribution status"""
    users = CustomUser.objects.filter(is_staff=False)
    result = []

    for user in users:
        try:
            monthly_amount = ContributionSetting.objects.get(year=year).amount
        except ContributionSetting.DoesNotExist:
            monthly_amount = 0

        total_paid = Contribution.objects.filter(
            user=user, date_contributed__year=year
        ).aggregate(total_paid=Sum('amount'))['total_paid'] or 0

        months_defaulting = (total_paid / monthly_amount) - current_month if monthly_amount else 0
        user_status = get_contribution_status(months_defaulting)

        if user_status == status:
            result.append(user)

    return result


def get_status_message(user, year, current_month):
    """Generate appropriate status message for a user"""
    try:
        monthly_amount = ContributionSetting.objects.get(year=year).amount
    except ContributionSetting.DoesNotExist:
        monthly_amount = 0

    total_paid = Contribution.objects.filter(
        user=user, date_contributed__year=year
    ).aggregate(total_paid=Sum('amount'))['total_paid'] or 0

    months_defaulting = current_month - (total_paid / monthly_amount) if monthly_amount else 0

    if months_defaulting < 0:
        return f"You have paid in advance by {-months_defaulting:.1f} months. Thank you for your prompt contributions."
    elif months_defaulting == 0:
        return "Your contributions are up to date. Thank you for your prompt payments."
    else:
        return f"You are defaulting by {months_defaulting:.1f} months. Kindly make your contributions to come up to date."
##############


@login_required
@user_passes_test(lambda u: u.is_staff)
def send_reminder_message(request):
    if request.method == "POST":
        user_ids = request.POST.getlist("user_ids")
        users = CustomUser.objects.filter(id__in=user_ids)

        for user in users:
            months_defaulted = int(request.POST.get(f"months_defaulted_{user.id}", 0))
            message_text = f"Dear {user.first_name}, This is an automated message on your status. You are defaulting by {months_defaulted} months; Kindly make your contributions to come up to date. Thank you."
            # Send message (e.g., email or SMS logic here)
            print(f"Sending to {user.email}: {message_text}")  # Replace with actual sending logic

        messages.success(request, "Reminder messages sent successfully!")
        return redirect("manager_dashboard")



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
