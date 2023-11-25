from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth.views import LogoutView as AuthLogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError
import json  

# View to validate a username 
class UsernameValidationView(View):
    def post(self, request):
        # Load the JSON data from the request body
        data = json.loads(request.body)
        username = data['username']

        # Check if the username contains only alphanumeric characters
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'User should only contain alphanumeric characters'}, status=400)

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'User already exists, choose another one'}, status=409)

        return JsonResponse({'username_valid': True})

# View to validate an email through an AJAX request
class EmailValidationView(View):
    def post(self, request):
        # Load the JSON data from the request body
        data = json.loads(request.body)
        email = data['email']

        try:
            # Use Django's built-in email validation
            django_validate_email(email)
        except ValidationError:
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Sorry, email in use, choose another one'}, status=409)

        return JsonResponse({'email_valid': True})

# View for user registration
class RegistrationView(SuccessMessageMixin, View):
    template_name = 'authentication/registration_form.html'
    success_url = reverse_lazy('login')
    success_message = "Account successfully created"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        # Retrieve user registration form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if the username and email do not already exist
        if not User.objects.filter(username=username).exists() and not User.objects.filter(email=email).exists():
            # Check if the password meets the minimum length requirement
            if len(password) < 6:
                messages.error(request, 'Password too short')
                return render(request, self.template_name, context={'fieldValues': request.POST})

            # Create a new user and log them in
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect(self.success_url)

        return render(request, self.template_name, context={'fieldValues': request.POST})

# View for user login
class LoginView(View):
    template_name = 'authentication/login_form.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        # Retrieve user login form data
        username = request.POST['username']
        password = request.POST['password']

        # Check if both username and password are provided
        if username and password:
            # Use authenticate to check credentials
            user = authenticate(request, username=username, password=password)

            if user:
                # Check if the user account is active
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome, {user.username}. You are now logged in.')
                    return redirect('expenses')
                messages.error(request, 'Account is not active, please check your email.')
            else:
                messages.error(request, 'Invalid credentials, please try again.')
        else:
            messages.error(request, 'Please fill in all fields.')

        return render(request, self.template_name)

# View for user logout
class LogoutView(View):
    def post(self, request):
        # Use logout to log the user out
        logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')
