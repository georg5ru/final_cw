from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from materials.models import Course, Lesson
from users.models import User


class LessonApiTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email='user@test.com',
            password='test123',
        )
        self.client.force_authenticate(user=self.user)
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user,
        )
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Lesson Description',
            video_link='https://www.youtube.com/watch?v=test',
            course=self.course,
            owner=self.user,
        )

    def test_lesson_list_returns_array(self):
        url = reverse('lesson-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)

    def test_lesson_retrieve(self):
        url = reverse('lesson-detail', args=[self.lesson.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.lesson.id)
        self.assertEqual(response.data['title'], self.lesson.title)

    def test_lesson_create(self):
        url = reverse('lesson-create')
        data = {
            'title': 'New Lesson',
            'description': 'New Description',
            'video_link': 'https://www.youtube.com/watch?v=new',
            'course': self.course.id,
            'owner': self.user.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.last().owner_id, self.user.id)

    def test_lesson_update(self):
        url = reverse('lesson-update', args=[self.lesson.id])
        data = {
            'title': 'Updated Lesson',
            'description': 'Updated Description',
            'video_link': 'https://www.youtube.com/watch?v=updated',
            'course': self.course.id,
            'owner': self.user.id,
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Lesson')

    def test_lesson_delete(self):
        url = reverse('lesson-delete', args=[self.lesson.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())


class CourseApiTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email='user@test.com',
            password='test123',
        )
        self.client.force_authenticate(user=self.user)
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            owner=self.user,
        )
        Lesson.objects.create(
            title='Lesson 1',
            description='Lesson 1 Description',
            video_link='https://www.youtube.com/watch?v=lesson1',
            course=self.course,
            owner=self.user,
        )

    def test_course_list_has_computed_fields(self):
        url = reverse('course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)

        course = response.data[0]
        self.assertIn('lessons', course)
        self.assertIn('lessons_count', course)
        self.assertEqual(course['lessons_count'], 1)
