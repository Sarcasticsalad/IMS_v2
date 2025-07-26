from django.urls import path
from . import views

app_name = 'authentication'  # Define the app namespace

urlpatterns = [
    path('', views.login_view, name='login'),  # Login view
    path('signup/', views.signup_view, name='signup'), # Signup View
    path('set-password/', views.set_password, name='set_password'),  # Set password view
    path('logout/', views.logout_view, name='logout'),  # Logout view
    path('redirect/', views.post_login_redirect, name='post_login_redirect'),  # Post-login redirect view

]
