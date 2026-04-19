import pytest
from http import HTTPStatus

from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def news(db):
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def author(db, django_user_model):
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def reader(db, django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args_fixture',
    (
        ('news:home', None),
        ('news:detail', 'news'),
        ('users:login', None),
        ('users:signup', None),
    )
)
def test_pages_availability(client, name, args_fixture, request):
    if args_fixture:
        obj = request.getfixturevalue(args_fixture)
        url = reverse(name, args=(obj.id,))
    else:
        url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_logout_availability(client):
    url = reverse('users:logout')
    response = client.post(url)
    assert response.status_code in (HTTPStatus.OK, HTTPStatus.FOUND)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user_client, expected_status',
    (
        ('author_client', HTTPStatus.OK),
        ('reader_client', HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_availability_for_comment_edit_and_delete(
    user_client, expected_status, name, comment, request
):
    client_instance = request.getfixturevalue(user_client)
    url = reverse(name, args=(comment.id,))
    response = client_instance.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_redirect_for_anonymous_client(client, name, comment):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url
