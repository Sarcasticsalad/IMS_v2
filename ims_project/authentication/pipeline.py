from .models import UserProfile

def set_initial_password(backend, user, response, *args, **kwargs):
    if user and not user.has_usable_password():
        UserProfile.objects.get_or_create(user=user, defaults={'password_set': False})