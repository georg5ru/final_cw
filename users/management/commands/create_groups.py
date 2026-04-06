from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from materials.models import Course, Lesson


class Command(BaseCommand):
    help = 'Создание групп пользователей и назначение прав'

    def handle(self, *args, **options):
        # Создаем группу модераторов
        moderator_group, created = Group.objects.get_or_create(name='Модераторы')

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Модераторы" создана'))
        else:
            self.stdout.write('Группа "Модераторы" уже существует')

        # Получаем права для курсов и уроков
        course_ct = ContentType.objects.get_for_model(Course)
        lesson_ct = ContentType.objects.get_for_model(Lesson)

        # Права для курсов (без создания и удаления)
        course_permissions = Permission.objects.filter(
            content_type=course_ct,
            codename__in=['view_course', 'change_course']
        )

        # Права для уроков (без создания и удаления)
        lesson_permissions = Permission.objects.filter(
            content_type=lesson_ct,
            codename__in=['view_lesson', 'change_lesson']
        )

        # Назначаем права группе
        for perm in course_permissions:
            moderator_group.permissions.add(perm)
            self.stdout.write(f'Добавлено право: {perm.codename}')

        for perm in lesson_permissions:
            moderator_group.permissions.add(perm)
            self.stdout.write(f'Добавлено право: {perm.codename}')

        self.stdout.write(self.style.SUCCESS('Права успешно назначены группе "Модераторы"'))
