from django.urls import path
from . import views


urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('verify-email/<str:uuidToken>/<str:uniqueId>', views.activate, name='verify-email'),
    path('forgot-password', views.forgot_password, name='forgot-password'),
]
