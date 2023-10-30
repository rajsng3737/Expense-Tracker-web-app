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
import json  # Import the json module

class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'User should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'User already exists, choose another one'}, status=409)
        return JsonResponse({'username_valid': True})

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        try:
            # Use Django's built-in email validation
            django_validate_email(email)
        except ValidationError:
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Sorry, email in use, choose another one'}, status=409)

        return JsonResponse({'email_valid': True})

class RegistrationView(SuccessMessageMixin, View):
    template_name = 'authentication/registration_form.html'
    success_url = reverse_lazy('login')
    success_message = "Account successfully created"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists() and not User.objects.filter(email=email).exists():
            if len(password) < 6:
                messages.error(request, 'Password too short')
                return render(request, self.template_name, context={'fieldValues': request.POST})
            
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect(self.success_url)

        return render(request, self.template_name, context={'fieldValues': request.POST})

class LoginView(View):
    template_name = 'authentication/login_form.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = authenticate(request, username=username, password=password)  # Use authenticate to check credentials

            if user:
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

class LogoutView(View):
    def post(self, request):
        logout(request)  # Use logout to log the user out
        messages.success(request, 'You have been logged out')
        return redirect('login')
