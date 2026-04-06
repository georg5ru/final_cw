from rest_framework import serializers

from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для урока
    """
    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для курса с вложенными уроками
    """
    # Вложенные уроки (список) - Задание 3
    lessons = LessonSerializer(many=True, read_only=True)

    # Количество уроков (вычисляемое поле) - Задание 1
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'  # включает lessons и lessons_count

    def get_lessons_count(self, obj):
        """Возвращает количество уроков в курсе"""
        return obj.lessons.count()
