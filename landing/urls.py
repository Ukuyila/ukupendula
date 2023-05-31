from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('ukupendula-pricing', views.pricing, name='pricing'),
]
