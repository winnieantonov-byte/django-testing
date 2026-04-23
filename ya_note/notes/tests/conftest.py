from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.NOTE_SLUG = 'note-slug'
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=cls.NOTE_SLUG,
            author=cls.author
        )

        cls.LOGIN_URL = reverse('users:login')
        cls.LIST_URL = reverse('notes:list')
        cls.ADD_URL = reverse('notes:add')
        cls.SUCCESS_URL = reverse('notes:success')
        cls.EDIT_URL = reverse('notes:edit', args=(cls.NOTE_SLUG,))
        cls.DELETE_URL = reverse('notes:delete', args=(cls.NOTE_SLUG,))
        cls.ANON_REDIRECT_CASES = (
            (cls.LIST_URL, f'{cls.LOGIN_URL}?next={cls.LIST_URL}'),
            (cls.ADD_URL, f'{cls.LOGIN_URL}?next={cls.ADD_URL}'),
            (cls.SUCCESS_URL, f'{cls.LOGIN_URL}?next={cls.SUCCESS_URL}'),
            (cls.EDIT_URL, f'{cls.LOGIN_URL}?next={cls.EDIT_URL}'),
            (cls.DELETE_URL, f'{cls.LOGIN_URL}?next={cls.DELETE_URL}'),
        )

        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
