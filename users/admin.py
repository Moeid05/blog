from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser 

class CustomUser_Admin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'total_vote', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions', 'followers')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('total_vote',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('total_vote',)}),
    )

admin.site.register(CustomUser , CustomUser_Admin)