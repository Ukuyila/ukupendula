from django.urls import path
from . import views

from django.contrib.auth.views import (
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)


urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    # path('forgot-password', views.forgot_password, name='forgot-password'),

    path('password-reset/', PasswordResetView.as_view(template_name='authorisation/forgot-password.html'),name='password-reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='authorisation/password-reset-done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='authorisation/password-reset-confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',PasswordResetCompleteView.as_view(template_name='authorisation/password-reset-complete.html'),name='password_reset_complete'),
]
