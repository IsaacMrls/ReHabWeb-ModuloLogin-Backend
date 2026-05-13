from django.urls import path
from .views import send_code, verify_code, reset_password

urlpatterns = [
	path('send-code/', send_code),
	path('verify-code/', verify_code),
	path('reset-password/', reset_password),
]
