from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User # Import your custom user model here

# This line tells Django to show "Users" in the admin panel
admin.site.register(User)