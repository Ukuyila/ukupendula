from django.urls import path
from . import views


urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('verify-email/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/(?P<uniqueId>[0-9A-Za-z_\-]+)/', views.activate, name='verify-email'),
    path('forgot-password', views.forgot_password, name='forgot-password'),
]
