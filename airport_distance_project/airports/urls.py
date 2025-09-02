from django.urls import path
from . import views

app_name = 'airports'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('calculator/', views.airport_distance_view, name='airport_distance'),
    path('calculate/', views.calculate_distance, name='calculate_distance'),
]