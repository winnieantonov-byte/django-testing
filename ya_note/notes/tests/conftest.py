from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

# --- Константы URL ---
LOGIN_URL = reverse('users:login')
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')

NOTE_SLUG = 'note-slug'
EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))
DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG,))

LIST_REDIRECT = f'{LOGIN_URL}?next={LIST_URL}'
ADD_REDIRECT = f'{LOGIN_URL}?next={ADD_URL}'
SUCCESS_REDIRECT = f'{LOGIN_URL}?next={SUCCESS_URL}'
EDIT_REDIRECT = f'{LOGIN_URL}?next={EDIT_URL}'
DELETE_REDIRECT = f'{LOGIN_URL}?next={DELETE_URL}'
DETAIL_REDIRECT = f'{LOGIN_URL}?next={DETAIL_URL}'


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=NOTE_SLUG,
            author=cls.author
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
