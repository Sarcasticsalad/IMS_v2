from django.urls import path
from . import views
from .views import FlaskMessageLogListView

app_name = 'instagram_automation'

urlpatterns = [
    path('setup/', views.InstagramSetupView.as_view(), name='setup'),
    path('webhook/', views.InstagramWebhookView.as_view(), name='webhook'),
    path('logs/', views.MessageLogListView.as_view(), name='message_logs'),
    path('rules/', views.AutoResponseRuleListView.as_view(), name='rule_list'),
    path('rules/create/', views.AutoResponseRuleCreateView.as_view(), name='rule_create'),
    path('rules/<str:rule_id>/update/', views.AutoResponseRuleUpdateView.as_view(), name='rule_update'),
    path('rules/<str:rule_id>/delete/', views.AutoResponseRuleDeleteView.as_view(), name='rule_delete'),
    path("flask-message-logs/", FlaskMessageLogListView.as_view(), name="flask_message_log_list"),
] 