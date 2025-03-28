from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_backends
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.context_processors import request

from .forms import CustomUserCreationForm, CustomUserUpdateForm, ContactForm, ChildForm, LoginForm, UserProfileForm
from django.contrib.auth.forms import PasswordChangeForm


def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('record_contribution')
        return redirect('dashboard')
    return redirect('login')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            backend = get_backends()[0]
            user.backend = f'{backend.__module__}.{backend.__class__.__name__}'

            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CustomUserUpdateForm(instance=request.user)
    return render(request, 'users/update_profile.html', {'form': form})


@login_required
def add_contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            return redirect("dashboard")
    else:
        form = ContactForm()
    return render(request, "users/add_contact.html", {"form": form})


@login_required
def add_child(request):
    if request.method == "POST":
        form = ChildForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.user = request.user
            child.save()
            return redirect("dashboard")
    else:
        form = ChildForm()
    return render(request, "users/add_child.html", {"form": form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']
            user = authenticate(request, username=identifier, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful')
                if user.is_staff:
                    return redirect('record_contribution')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid login credentials. Please try again.')
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")  # Redirect to the login page


@login_required
def dashboard(request):
    return render(request, "users/dashboard.html")


@login_required
def profile(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "users/profile.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)  # Prevents logout after password change
            messages.success(request, "Password changed successfully!")
            return redirect("profile")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "users/change_password.html", {"form": form})


def dashboard(request):
    user = request.user
    current_date = now()

    # Get past years contributions
    past_contributions = Contribution.objects.filter(user=user).order_by('-year')

    # Calculate contribution status
    contributions = {year: {} for year in past_contributions.values_list('year', flat=True)}

    for contrib in past_contributions:
        contributions[contrib.year][contrib.month] = contrib.paid

    # Arrears calculation (unpaid months)
    total_arrears = sum(1 for year, months in contributions.items() for month, paid in months.items() if not paid)

    # Required amount to close the year (ignoring extras)
    total_due = total_arrears * 100  # Assuming each month is $100

    # Determine health status
    defaults = total_arrears
    if defaults == 0:
        health_status = "green"
    elif defaults <= 2:
        health_status = "yellow"
    elif defaults >= 4:
        health_status = "red"
    else:
        health_status = "blue"  # Paid in advance

    context = {
        'current_date': current_date,
        'contributions': contributions,
        'total_arrears': total_arrears,
        'total_due': total_due,
        'health_status': health_status,
    }

    return render(request, 'contributions/dashboard.html', context)
