from django.apps import AppConfig


class ImsAppConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "ims_app"
