from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from authentication.views import post_login_redirect

urlpatterns = [
    path("admin/", admin.site.urls),  # Admin panel URL
    path('', include('authentication.urls')),  # Authentication URLs
    path('ims/', include('ims.urls')),  # IMS URLs (for dashboard, models, etc.)
    path('instagram/', include('instagram_automation.urls')),  # Add the new app URLs
    path('oauth/', include('social_django.urls', namespace='social')),  # OAuth URLs (if needed)
    path('redirect/', post_login_redirect, name='post_login_redirect'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
