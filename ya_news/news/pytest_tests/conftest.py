from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture(autouse=True)
def enable_db_access(db):
    pass


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
def news(db):
    return News.objects.create(title='Тестовая новость', text='Просто текст.')


@pytest.fixture
def news_list(db):
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def comments_list(news, author):
    now = timezone.now()
    comments = [
        Comment(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        for index in range(10)
    ]
    Comment.objects.bulk_create(comments)
    created_comments = (
        Comment.objects.filter(news=news, author=author)
        .order_by('id')[:10]
    )
    for index, comment in enumerate(created_comments):
        comment.created = now + timedelta(days=index)
    Comment.objects.bulk_update(created_comments, ['created'])


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
def url_login():
    return reverse('users:login')
