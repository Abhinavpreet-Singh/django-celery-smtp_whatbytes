from django.contrib import admin
from django.urls import include, path

from emails import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('emails.urls')),
    path('', views.email_form, name='email-form'),
]
