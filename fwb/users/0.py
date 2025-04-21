@login_required
def profile(request):
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = ProfileCompletionForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                request.user.check_profile_completion()
                messages.success(request, "Profile updated successfully!")
                return redirect('profile')

        elif 'add_contact' in request.POST:
            contact_form = ContactForm(request.POST)
            if contact_form.is_valid():
                name = contact_form.cleaned_data.get("name")
                phone = contact_form.cleaned_data.get("phone")

                # Prevent duplicate contacts
                existing = request.user.contacts.filter(name=name, phone_number=phone).exists()
                if existing:
                    messages.warning(request, "This contact already exists.")
                else:
                    contact = contact_form.cleaned_data
                    # Manually create contact object without double saving
                    request.user.contacts.create(name=contact["name"], phone_number=contact["phone"])
                    request.user.check_profile_completion()
                    messages.success(request, "Contact added successfully!")

                return redirect('profile')

    user_form = ProfileCompletionForm(instance=request.user)
    contact_form = ContactForm()

    context = {
        'user_form': user_form,
        'contact_form': contact_form,
        'profile_complete': request.user.profile_complete,
        'contacts': request.user.contacts.all()
    }
    return render(request, 'users/profile.html', context)
