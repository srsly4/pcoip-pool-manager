from django.urls import path

from . import views

app_name = 'pools'
urlpatterns = [
    path('auth/', views.Authentication.as_view()),
    path('pools/', views.PoolsList.as_view())
]
