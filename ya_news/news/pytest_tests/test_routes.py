from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (reverse('news:home'), lazy_fixture('client'), HTTPStatus.OK),
        (reverse('users:login'), lazy_fixture('client'), HTTPStatus.OK),
        (reverse('users:logout'), lazy_fixture('client'), HTTPStatus.OK),
        (reverse('users:signup'), lazy_fixture('client'), HTTPStatus.OK),
        (
            lazy_fixture('url_detail'),
            lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            lazy_fixture('url_edit'),
            lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            lazy_fixture('url_edit'),
            lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            lazy_fixture('url_delete'),
            lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            lazy_fixture('url_delete'),
            lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND
        ),
    ),
)
def test_pages_availability_for_different_users(
    url, parametrized_client, expected_status
):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (lazy_fixture('url_edit'), lazy_fixture('url_delete')),
)
def test_redirect_for_anonymous_client(client, url_login, url):
    expected_url = f'{url_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
