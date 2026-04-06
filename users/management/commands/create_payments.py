import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from materials.models import Course, Lesson
from users.models import Payment, User


class Command(BaseCommand):
    help = 'Создает тестовые платежи'

    def handle(self, *args, **options):
        # Получаем или создаем тестового пользователя
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.WARNING('Нет пользователей. Создаем тестового пользователя...'))
            user = User.objects.create_user(
                email='test@example.com',
                password='test123',
                first_name='Тест',
                last_name='Тестовый'
            )
            self.stdout.write(self.style.SUCCESS(f'Создан пользователь: {user.email}'))

        # Получаем все курсы и уроки
        courses = list(Course.objects.all())
        lessons = list(Lesson.objects.all())

        if not courses and not lessons:
            self.stdout.write(self.style.ERROR('Нет курсов и уроков. Сначала создай курсы и уроки.'))
            return

        # Очищаем старые платежи (опционально)
        Payment.objects.filter(user=user).delete()
        self.stdout.write('Старые платежи удалены')

        # Создаем 10 тестовых платежей
        payment_methods = [method[0] for method in Payment.PaymentMethod.choices]

        for i in range(10):
            # Случайная дата за последние 30 дней
            payment_date = timezone.now() - timedelta(days=random.randint(0, 30))

            # Случайный выбор: платим за курс или за урок
            if random.choice([True, False]) and courses:
                paid_course = random.choice(courses)
                paid_lesson = None
                payment_for = f'курс "{paid_course.title}"'
            elif lessons:
                paid_lesson = random.choice(lessons)
                paid_course = None
                payment_for = f'урок "{paid_lesson.title}"'
            else:
                continue

            # Случайная сумма
            amount = round(random.uniform(500, 15000), 2)

            # Случайный способ оплаты
            payment_method = random.choice(payment_methods)

            # Создаем платеж
            Payment.objects.create(
                user=user,
                payment_date=payment_date,
                amount=amount,
                payment_method=payment_method,
                paid_course=paid_course,
                paid_lesson=paid_lesson
            )

            self.stdout.write(f'Создан платеж: {payment_for} - {amount} руб. ({payment_method})')

        # Создаем несколько платежей за конкретные даты для тестирования сортировки
        if courses:
            # Платеж старой датой
            Payment.objects.create(
                user=user,
                payment_date=timezone.now() - timedelta(days=60),
                amount=999.99,
                payment_method='cash',
                paid_course=courses[0],
                paid_lesson=None
            )

            # Платеж большой суммой
            if len(courses) > 1:
                Payment.objects.create(
                    user=user,
                    payment_date=timezone.now() - timedelta(days=5),
                    amount=25000.00,
                    payment_method='transfer',
                    paid_course=courses[1],
                    paid_lesson=None
                )

        self.stdout.write(self.style.SUCCESS(f'Всего создано {Payment.objects.filter(user=user).count()} платежей'))
