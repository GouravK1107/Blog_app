from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login , logout # Rename to avoid conflict

# Home page view
def home(request):
    return HttpResponse("<h1>Hello, this is the new project's app!</h1>")

def custom_logout_view(request):
    logout(request)  # Ends the session
    return redirect('login')

# Login view
def login_view(request):  # Renamed to avoid conflict with auth_login
    if request.method == "POST":
        email = request.POST.get('login')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Both fields are required.")
            return render(request, 'account/login.html')

        try:
            # Fetch the username associated with this email
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, 'account/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('home')  # Change to your desired page after login
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, 'account/login.html')

    return render(request, 'account/login.html')

# Signup view
def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required.")
            return render(request, 'account/signup.html')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'account/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'account/signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'account/signup.html')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        # Authenticate and login
        user = authenticate(request, username=username, password=password1)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Account created and logged in successfully!")
            return redirect('create_profile')

    return render(request, 'account/signup.html')