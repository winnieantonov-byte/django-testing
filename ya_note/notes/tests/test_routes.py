from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    HOME_URL = reverse('notes:home')
    LIST_URL = reverse('notes:list')
    ADD_URL = reverse('notes:add')
    SUCCESS_URL = reverse('notes:success')
    LOGIN_URL = reverse('users:login')
    LOGOUT_URL = reverse('users:logout')
    SIGNUP_URL = reverse('users:signup')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug',
            author=cls.author
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_pages_availability(self):
        urls = (self.HOME_URL, self.LOGIN_URL, self.SIGNUP_URL)
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_availability(self):
        response = self.client.post(self.LOGOUT_URL)
        self.assertIn(response.status_code, (HTTPStatus.OK, HTTPStatus.FOUND))

    def test_availability_for_authenticated_user(self):
        self.client.force_login(self.reader)
        urls = (self.LIST_URL, self.ADD_URL, self.SUCCESS_URL)
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_author_and_reader(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (self.detail_url, self.edit_url, self.delete_url)
        for user, status in users_statuses:
            self.client.force_login(user)
            for url in urls:
                with self.subTest(user=user, url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            self.LIST_URL, self.ADD_URL, self.SUCCESS_URL,
            self.detail_url, self.edit_url, self.delete_url
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
