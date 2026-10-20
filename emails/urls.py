from django.urls import path

from . import views

urlpatterns = [
    path('send-email/', views.send_email, name='send-email'),
    path('email-status/<str:task_id>/', views.email_status, name='email-status'),
]
