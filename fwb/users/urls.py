from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register, update_profile, add_child, add_contact, user_login, user_logout, profile, change_password

urlpatterns = [
    path('/', user_login, name='home'),
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('profile/update/', update_profile, name='update_profile'),
    path('contacts/add', add_contact, name='add_contact'),
    path('children/add/', add_child, name='add_child'),
    path("logout/", user_logout, name="logout"),
    path("profile/", profile, name="profile"),
    path("change-password/", change_password, name="change_password"),
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="users/password_reset.html"),
         name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="users/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="users/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="users/password_reset_complete.html"), name="password_reset_complete"),
]
