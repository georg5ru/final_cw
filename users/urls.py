from django.urls import path

from users.views import PaymentListAPIView, UserProfileAPIView, UserRegistrationView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
    path('users/<int:pk>/', UserProfileAPIView.as_view(), name='user-profile'),
]
