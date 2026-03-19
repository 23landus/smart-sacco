from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from .forms import CustomUserCreationForm

# 1. Registration View
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Use full_name since username is not in your model
            full_name = form.cleaned_data.get('full_name')
            messages.success(request, f'Account created for {full_name}!')
            return redirect('login') 
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# 2. Smart Login View (Handles Role Redirection)
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # ROLE REDIRECTION LOGIC
                if user.is_superuser:
                    messages.info(request, f"Welcome, Treasurer {username}.")
                    return redirect('treasurer_dashboard') # Send to Treasurer Portal
                elif user.is_staff:
                    messages.info(request, f"Staff Access: {username}")
                    return redirect('treasurer_dashboard') # Staff can see, but won't have 'power'
                else:
                    return redirect('dashboard') # Normal members go to main dashboard
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

# 3. Logout View
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')