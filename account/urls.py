from django.urls import path

from . import views

urlpatterns = [
    path('auth/', views.PhoneNumberInputAPIView.as_view(), name='auth'),
    path('auth_code_input/', views.AuthCodeInputAPIView.as_view(), name='auth-code-input'),
    path('profile/', views.InputInviteCode.as_view(), name='profile'),
]
