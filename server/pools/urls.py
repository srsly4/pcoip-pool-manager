from django.urls import path
from . import views

app_name = 'pools'
urlpatterns = [
    path('reservations/', views.Reservations.as_view()),
    path('reservation/', views.SingleReservation.as_view()),
    path('auth/', views.Authentication.as_view()),
    path('pools/', views.PoolsList.as_view()),
]

