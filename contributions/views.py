from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Contribution
from .forms import ContributionForm
from .utils import allocate_contribution



@login_required
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
