from datetime import datetime, timedelta
from http import HTTPStatus

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from pytest_lazyfixture import lazy_fixture
from news.forms import BAD_WORDS
from news.models import Comment, News

# --- Константы для параметризации ---

CREATE_COMMENT_CASES = [
    ('client', 0),
    ('author_client', 1),
]

BAD_WORDS_CASES = [
    {'text': f'Текст с {word}'} for word in BAD_WORDS
]

# Общие lazy_fixture для исключения дублирования в test_routes
CLIENT = lazy_fixture('client')
AUTHOR_CLIENT = lazy_fixture('author_client')
READER_CLIENT = lazy_fixture('reader_client')

HOME_URL = lazy_fixture('home_url')
LOGIN_URL = lazy_fixture('login_url')
LOGOUT_URL = lazy_fixture('logout_url')
SIGNUP_URL = lazy_fixture('signup_url')
DETAIL_URL = lazy_fixture('url_detail')
EDIT_URL = lazy_fixture('url_edit')
DELETE_URL = lazy_fixture('url_delete')

PAGES_AVAILABILITY_CASES = (
    (HOME_URL, CLIENT, HTTPStatus.OK, 'get'),
    (LOGIN_URL, CLIENT, HTTPStatus.OK, 'get'),
    (LOGOUT_URL, CLIENT, HTTPStatus.OK, 'post'),
    (SIGNUP_URL, CLIENT, HTTPStatus.OK, 'get'),
    (DETAIL_URL, CLIENT, HTTPStatus.OK, 'get'),
    (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK, 'get'),
    (EDIT_URL, READER_CLIENT, HTTPStatus.NOT_FOUND, 'get'),
    (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK, 'get'),
    (DELETE_URL, READER_CLIENT, HTTPStatus.NOT_FOUND, 'get'),
)

REDIRECT_CASES = (
    (EDIT_URL, HTTPStatus.FOUND, LOGIN_URL),
    (DELETE_URL, HTTPStatus.FOUND, LOGIN_URL),
)

# --- Фикстуры для создания данных ---


@pytest.fixture
def news_list(db):
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comments_list(news, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()

# --- Фикстуры пользователей и клиентов ---


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

# --- Фикстуры объектов ---


@pytest.fixture
def news(db):
    return News.objects.create(title='Тестовая новость', text='Текст.')


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )

# --- Фикстуры URL-адресов ---


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def url_detail(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def url_edit(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def url_delete(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def form_data():
    return {'text': 'Текст комментария'}
