from django.urls import path

from . import views

app_name = 'pools'
urlpatterns = [
    path('login', views.login, name='login'),
]
