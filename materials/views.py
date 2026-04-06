from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, viewsets

from users.tasks import send_course_update_email  # импортируем задачу Celery

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для курсов с отправкой уведомлений при обновлении
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_update(self, serializer):
        """
        При обновлении курса отправляем уведомления подписчикам
        """
        course = self.get_object()

        # Сохраняем обновление
        serializer.save()

        # Проверяем, прошло ли более 4 часов с последнего обновления
        # (чтобы не спамить уведомлениями)
        time_since_update = timezone.now() - course.updated_at
        if time_since_update > timedelta(hours=4):
            # Отправляем уведомления асинхронно через Celery
            send_course_update_email.delay(course.id)


# ---- Generic-классы для Lesson ----

class LessonListAPIView(generics.ListAPIView):
    """
    Получение списка уроков
    GET /lessons/
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonCreateAPIView(generics.CreateAPIView):
    """
    Создание урока
    POST /lessons/create/
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """
    Получение одного урока
    GET /lessons/{id}/
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonUpdateAPIView(generics.UpdateAPIView):
    """
    Обновление урока
    PUT /lessons/{id}/update/  (полное обновление)
    PATCH /lessons/{id}/update/ (частичное обновление)
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def perform_update(self, serializer):
        """
        При обновлении урока проверяем, нужно ли уведомить подписчиков курса
        """
        lesson = self.get_object()
        course = lesson.course

        # Сохраняем обновление урока
        serializer.save()

        # Проверяем, прошло ли более 4 часов с последнего обновления курса
        time_since_update = timezone.now() - course.updated_at
        if time_since_update > timedelta(hours=4):
            # Отправляем уведомления подписчикам курса
            send_course_update_email.delay(course.id)


class LessonDestroyAPIView(generics.DestroyAPIView):
    """
    Удаление урока
    DELETE /lessons/{id}/delete/
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
