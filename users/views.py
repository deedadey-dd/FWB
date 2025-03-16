from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from users.forms import CustomUserCreationForm, CustomUserUpdateForm, ContactForm, ChildForm, LoginForm,UserProfileForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {form: form})


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
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid Login Credentials. Please Try Again')

        else:
            form = LoginForm()

        return render(request, 'users/login.html', {'form':form})

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
