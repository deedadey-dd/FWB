from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Contact, Child


# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'other_names', 'last_name', 'phone_number', 'date_of_birth',
                    'residence', 'hometown')
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


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    actions = ['make_manager', 'remove_manager']

    def make_manager(self, request, queryset):
        queryset.update(is_staff=True)
        self.message_user(request, "Selected users have been made managers.")
    make_manager.short_description = "Grant Manager Access (is_staff)"

    def remove_manager(self, request, queryset):
        queryset.update(is_staff=False)
        self.message_user(request, "Selected users have been removed from managers.")
    remove_manager.short_description = "Remove Manager Access (is_staff)"


# admin.site.register(CustomUser, CustomUserAdmin)
