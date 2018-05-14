from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = 'pools'
urlpatterns = [
    path('reservations/', views.Reservations.as_view()),
    path('auth/', views.Authentication.as_view()),
    path('pools/', views.PoolsList.as_view())
]

