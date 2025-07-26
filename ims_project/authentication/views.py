from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm, AuthenticationForm
from django.urls import reverse
from .models import UserProfile
from social_django.models import UserSocialAuth
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

# View to handle signup
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Creates and saves the new user to the database
            user = form.save()

            # Creates the associated UserProfile
            UserProfile.objects.create(user=user, password_set=True)

            # This logs the new user immediately after sign up
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            logger.info(f"User {user.username} created and logged in.")

            # Redirect the user to main dashboard
            return redirect('ims:dashboard')
        
        else:
            logger.error("Form is not valid.")
            logger.error(form.errors.as_json())

    else:
        form = UserCreationForm()
    return render(request, 'authentication/signup.html', {'form':form})    


# View to handle user login
def login_view(request):
    if request.method == 'POST':
        # Use Django's built-in AuthenticationForm
        logger.info("Login view received a POST request.")
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            logger.info("Login form is valid.")
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Autheticate the user
            user = authenticate(username=username, password=password)

            if user is not None:
                logger.info(f"User '{username}' authenticated successfully.")
                login(request, user)
                return redirect('ims:dashboard')
            
            else: 
                logger.error("Login form is not valid.")
                logger.error(f"Form errors: {form.errors.as_json()}")
        else:
            logger.info("Login view received a GET request.")
            form = AuthenticationForm()
                
    if request.user.is_authenticated:
        return redirect(reverse('ims:dashboard'))  # Redirect to dashboard if user is logged in
    
    return render(request, 'authentication/login.html')  # Render the login page if not authenticated

# View for setting a password
@login_required
def set_password(request):
    user = request.user
    
    # Check if user already has a password set
    if user.userprofile.password_set:
        return redirect(reverse('ims:dashboard'))  # Redirect to dashboard if password is already set
    
    # Handle password setting through POST request
    if request.method == 'POST':
        form = SetPasswordForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()  # Save the new password
            
            # Mark password as set in the UserProfile model
            user_profile = user.userprofile
            user_profile.password_set = True
            user_profile.save()
            
            # Logout the user after setting the password
            logout(request)

            # Authenticate and log the user back in
            user = authenticate(username=user.username, password=request.POST['new_password1'])
            if user is not None:
                login(request, user)
            
            # Redirect the user to the login page after logging out
            return redirect('authentication:login')
    else:
        form = SetPasswordForm(user=user)

    # Render the set password form
    return render(request, 'authentication/set_password.html', {'form': form})

# Logout view
def logout_view(request):
    # Log out the user and redirect to the login page
    logout(request)
    return redirect('authentication:login')  # Redirect to the login page after logging out

# Post login redirect to handle users without a set password
@login_required
def post_login_redirect(request):
    if not request.user.has_usable_password():
        return redirect('authentication:login')  # Redirect to set password if no usable password
    return redirect('ims:dashboard')  # Redirect to the dashboard if the password is set

# Google login complete (handle auto username generation)
def google_login_complete(request):
    # Get the user from social authentication
    social_user = UserSocialAuth.objects.get(provider='google', user=request.user)
    google_name = social_user.extra_data.get('name', 'user')

    # Set a unique username (e.g., use the Google account name or email)
    username = google_name if google_name else social_user.user.email.split('@')[0]
    username = make_unique_username(username)  # Ensure the username is unique

    # Assign the username to the user
    user = request.user
    user.username = username
    user.save()

    # Ensure the user profile is created and associate it
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    user_profile.password_set = False  # Set this flag if the password is not set yet
    user_profile.save()

    login(request, user)
    return redirect('authentication:set_password')  # Redirect to password set page after login

# Helper function to ensure the username is unique
def make_unique_username(username):
    if not User.objects.filter(username=username).exists():
        return username
    else:
        i = 1
        new_username = f"{username}{i}"
        while User.objects.filter(username=new_username).exists():
            i += 1
            new_username = f"{username}{i}"
        return new_username
