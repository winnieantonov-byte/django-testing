import pytest
from django.test import Client

from notes.models import Note
from .constants import LOGIN_URL, NOTE_SLUG


@pytest.fixture(autouse=True)
def enable_db_access(db):
    pass


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def note(author):
    return Note.objects.create(
        title='Заголовок',
        text='Текст',
        slug=NOTE_SLUG,
        author=author
    )


@pytest.fixture
def form_data():
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
        'slug': 'new-slug'
    }


@pytest.fixture
def expected_redirect_url():
    def _create_url(url):
        return f'{LOGIN_URL}?next={url}'
    return _create_url
