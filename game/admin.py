from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    
    # Which fields to display when editing an existing User:
    fieldsets = (
        (None, {'fields': ('username', 'password', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Which fields to display when adding a new User:
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'role', 'password1', 'password2'),
        }),
    )

    list_display = ('username', 'role', 'is_staff')
    search_fields = ('username', 'role')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)
