from django.urls import path
from . import views

app_name = 'procedures'

urlpatterns = [
    path('create/', views.create_procedure, name='create'),  
    path('success/', views.procedure_success, name='procedure_success'),
    path('list/', views.procedure_list, name='list'),
    path('detail/<int:pk>/', views.procedure_detail, name='detail'),
    path('edit/<int:pk>/', views.procedure_edit, name='edit'),
    path('delete/<int:pk>/', views.procedure_delete, name='delete'),
    path('my-procedures/', views.my_procedures, name='my_procedures'),
    path('procedures/<int:pk>/mark-as-read/', views.mark_as_read, name='mark_as_read'),
    path('notifications/', views.notifications, name='notifications'),
    path('procedure/<int:pk>/tracking/', views.procedure_tracking, name='procedure_tracking'),
]
