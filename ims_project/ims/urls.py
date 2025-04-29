from django.urls import path
from . import views

app_name = 'ims'  

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard view
    path('<str:model_name>/', views.model_list, name='model_list'),  # Model list view
    path('<str:model_name>/create/', views.model_create, name='model_create'),  # Model create view
    path('<str:model_name>/<str:item_id>/update/', views.model_update, name='model_update'),  # Model update view
    path('<str:model_name>/<str:item_id>/delete/', views.model_delete, name='model_delete'),  # Model delete view
]
