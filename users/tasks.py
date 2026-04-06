from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from materials.models import Course, Subscription
from users.models import User


@shared_task
def send_course_update_email(course_id):
    """
    Отправка уведомлений подписчикам об обновлении курса
    """
    try:
        course = Course.objects.get(id=course_id)
        subscriptions = Subscription.objects.filter(course=course).select_related('user')

        # Собираем email всех подписчиков
        recipients = [sub.user.email for sub in subscriptions if sub.user.email]

        if not recipients:
            return f"Нет подписчиков у курса '{course.title}'"

        # Отправляем письмо
        send_mail(
            subject=f'Курс "{course.title}" обновлен',
            message=f'Курс "{course.title}" был обновлен. Зайдите на платформу, чтобы посмотреть новые материалы.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )

        return f"Отправлено писем: {len(recipients)} для курса '{course.title}'"

    except Course.DoesNotExist:
        return f"Курс с id {course_id} не существует"
    except Exception as e:
        return f"Ошибка отправки писем: {str(e)}"


@shared_task
def block_inactive_users():
    """
    Блокировка пользователей, которые не заходили более месяца
    Запускается по расписанию каждый день в полночь
    """
    try:
        # Вычисляем дату месяц назад
        month_ago = timezone.now() - timedelta(days=30)

        # Находим пользователей, которые не заходили более месяца
        # и при этом не являются суперпользователями и активны
        inactive_users = User.objects.filter(
            last_login__lt=month_ago,
            is_active=True,
            is_superuser=False,
            is_staff=False
        )

        count = inactive_users.count()

        if count > 0:
            # Блокируем найденных пользователей
            inactive_users.update(is_active=False)

            # Отправляем уведомление администратору
            if settings.DEFAULT_FROM_EMAIL:
                send_mail(
                    subject='Блокировка неактивных пользователей',
                    message=f'Заблокировано {count} пользователей, которые не заходили более месяца.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )

            return f"Заблокировано {count} неактивных пользователей"
        else:
            return "Нет пользователей для блокировки"

    except Exception as e:
        return f"Ошибка при блокировке пользователей: {str(e)}"


@shared_task
def test_task():
    """
    Тестовая задача для проверки работы Celery
    """
    print("Celery работает!")
    return "OK"
