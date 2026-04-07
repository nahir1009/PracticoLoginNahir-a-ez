from django.urls import path
from .views import RegisterView, LoginView, RequestOTPView, VerifyOTPView, ResetPasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('otp/request/', RequestOTPView.as_view(), name='otp-request'),
    path('otp/verify/', VerifyOTPView.as_view(), name='otp-verify'),
    path('otp/reset-password/', ResetPasswordView.as_view(), name='otp-reset-password'),
]