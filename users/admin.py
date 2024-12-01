from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser 

class CustomUser Admin(UserAdmin):
    # Specify the fields to be displayed in the admin list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'total_vote', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions', 'followers')

    # Specify which fields are editable in the admin form
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('total_vote',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('total_vote',)}),
    )

# Register the CustomUser  model with the CustomUser Admin
admin.site.register(CustomUser , CustomUser Admin)