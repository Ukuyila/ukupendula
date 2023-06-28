from django.urls import path
from . import views


urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('forgot-password', views.forgot_password, name='forgot-password'),
]
