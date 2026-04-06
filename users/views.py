import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import Payment, User
from users.serializers import PaymentSerializer, UserRegistrationSerializer, UserSerializer


class PaymentFilter(django_filters.FilterSet):
    """Кастомный фильтр для платежей"""

    class Meta:
        model = Payment
        fields = {
            'paid_course': ['exact', 'isnull'],
            'paid_lesson': ['exact', 'isnull'],
            'payment_method': ['exact'],
            'amount': ['exact', 'gte', 'lte'],
        }


class PaymentListAPIView(generics.ListAPIView):
    """Список платежей - только для авторизованных"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']


class UserProfileAPIView(generics.RetrieveAPIView):
    """Просмотр профиля пользователя - только авторизованные"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserRegistrationView(generics.CreateAPIView):
    """Регистрация нового пользователя - доступно всем"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
