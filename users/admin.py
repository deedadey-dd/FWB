from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser, Contact, Child


# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'other_names', 'last_name', 'phone_number', 'date_of_birth', 'residence', 'hometown')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name', 'other_names')
    ordering = ('first_name',)
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('other_names', 'phone_number', 'date_of_birth', 'residence', 'hometown',)}),
    )

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'relationship', 'phone_number')
    search_fields = ('name', 'relationship', 'phone_number')


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'date_of_birth', 'phone_number')
    search_fields = ('name', 'date_of_birth', 'phone_number')


admin.site.register(CustomUser, CustomUserAdmin)
