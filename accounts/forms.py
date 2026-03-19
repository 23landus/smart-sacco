from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# This identifies your custom User model defined in accounts/models.py
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        # These MUST match the names in your models.py exactly
        fields = ("phone_number", "full_name")