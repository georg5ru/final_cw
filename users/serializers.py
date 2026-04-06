from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from materials.serializers import CourseSerializer, LessonSerializer
from users.models import Payment, User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации новых пользователей"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'phone', 'city', 'avatar')
        extra_kwargs = {
            'phone': {'required': False},
            'city': {'required': False},
            'avatar': {'required': False},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class PaymentSerializer(serializers.ModelSerializer):
    # ... (остается без изменений)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    paid_course_detail = CourseSerializer(source='paid_course', read_only=True)
    paid_lesson_detail = LessonSerializer(source='paid_lesson', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_email', 'payment_date', 'amount',
            'payment_method', 'paid_course', 'paid_course_detail',
            'paid_lesson', 'paid_lesson_detail',
        ]
        read_only_fields = ['payment_date']


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar', 'payments']
        read_only_fields = ['id', 'email']  # email нельзя менять через этот сериализатор
