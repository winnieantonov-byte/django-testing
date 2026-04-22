from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    NOTE_SLUG = 'note-slug'
    HOME_URL = reverse('notes:home')
    LOGIN_URL = reverse('users:login')
    LOGOUT_URL = reverse('users:logout')
    SIGNUP_URL = reverse('users:signup')
    LIST_URL = reverse('notes:list')
    ADD_URL = reverse('notes:add')
    SUCCESS_URL = reverse('notes:success')
    DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG,))
    EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
    DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))
    PAGES_WITH_FORM_URLS = (ADD_URL, EDIT_URL)
    ANON_ONLY_URLS = (
        LIST_URL,
        ADD_URL,
        SUCCESS_URL,
        DETAIL_URL,
        EDIT_URL,
        DELETE_URL,
    )
    ANON_REDIRECT_CASES = (
        (LIST_URL, f'{LOGIN_URL}?next={LIST_URL}'),
        (ADD_URL, f'{LOGIN_URL}?next={ADD_URL}'),
        (SUCCESS_URL, f'{LOGIN_URL}?next={SUCCESS_URL}'),
        (DETAIL_URL, f'{LOGIN_URL}?next={DETAIL_URL}'),
        (EDIT_URL, f'{LOGIN_URL}?next={EDIT_URL}'),
        (DELETE_URL, f'{LOGIN_URL}?next={DELETE_URL}'),
    )

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
            slug=cls.NOTE_SLUG,
            author=cls.author
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def get_expected_redirect_url(self, url):
        return f'{self.LOGIN_URL}?next={url}'
