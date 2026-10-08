
# Remove password field from admin user creation
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'role', 'phone_number', 'branch'),
        }),
    )

try:
    admin.site.unregister(User)
    admin.site.register(User, CustomUserAdmin)
except Exception:
    pass
