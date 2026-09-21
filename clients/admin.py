from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django import forms
from .models import UserProfile  # Assuming UserProfile handles role, phone, branch


# 1. Custom User Creation Form for Step 1
class CustomUserCreationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    # UserProfile fields
    phone_number = forms.CharField(max_length=10, required=False)
    role = forms.ChoiceField(
        choices=[('ADMIN', 'Admin'), ('STAFF', 'Staff')],
        initial='STAFF'
    )
    branch = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            # Save or create associated UserProfile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data.get('role')
            profile.phone_number = self.cleaned_data.get('phone_number')
            profile.branch = self.cleaned_data.get('branch')
            profile.save()
        return user


# 2. Inline editor for UserProfile details when editing an existing user
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Details'
    fk_name = 'user'


# 3. Unregister default UserAdmin and register Custom UserAdmin
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    inlines = (UserProfileInline,)
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'first_name',
                'last_name',
                'email',
                'password',
                'role',
                'phone_number',
                'branch',
            ),
        }),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')