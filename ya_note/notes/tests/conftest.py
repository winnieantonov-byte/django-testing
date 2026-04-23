from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    NOTE_SLUG = 'note-slug'

    @classmethod
    def setUpTestData(cls):
        # Пользователи
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        # Клиенты
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # Данные
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=cls.NOTE_SLUG,
            author=cls.author
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        # URL-адреса (атрибуты, которые используются в логике и роутах)
        cls.HOME_URL = reverse('notes:home')
        cls.LOGIN_URL = reverse('users:login')
        cls.LOGOUT_URL = reverse('users:logout')
        cls.SIGNUP_URL = reverse('users:signup')
        cls.LIST_URL = reverse('notes:list')
        cls.ADD_URL = reverse('notes:add')
        cls.SUCCESS_URL = reverse('notes:success')
        cls.DETAIL_URL = reverse('notes:detail', args=(cls.NOTE_SLUG,))
        cls.EDIT_URL = reverse('notes:edit', args=(cls.NOTE_SLUG,))
        cls.DELETE_URL = reverse('notes:delete', args=(cls.NOTE_SLUG,))
