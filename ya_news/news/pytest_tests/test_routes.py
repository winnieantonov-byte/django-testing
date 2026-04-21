from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture

from .constants import (
    HOME_URL, LOGIN_URL, LOGOUT_URL, SIGNUP_URL
)


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status, method',
    (
        (HOME_URL, lazy_fixture('client'), HTTPStatus.OK, 'get'),
        (LOGIN_URL, lazy_fixture('client'), HTTPStatus.OK, 'get'),
        (LOGOUT_URL, lazy_fixture('client'), HTTPStatus.OK, 'post'),
        (SIGNUP_URL, lazy_fixture('client'), HTTPStatus.OK, 'get'),
        (
            lazy_fixture('url_detail'),
            lazy_fixture('client'),
            HTTPStatus.OK,
            'get'
        ),
        (
            lazy_fixture('url_edit'),
            lazy_fixture('author_client'),
            HTTPStatus.OK,
            'get'
        ),
        (
            lazy_fixture('url_edit'),
            lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND,
            'get'
        ),
        (
            lazy_fixture('url_delete'),
            lazy_fixture('author_client'),
            HTTPStatus.OK,
            'get'
        ),
        (
            lazy_fixture('url_delete'),
            lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND,
            'get'
        ),
    ),
)
def test_pages_availability_for_different_users(
    url, parametrized_client, expected_status, method
):
    if method == 'get':
        response = parametrized_client.get(url)
    else:
        response = parametrized_client.post(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (lazy_fixture('url_edit'), lazy_fixture('url_delete')),
)
def test_redirect_for_anonymous_client(client, url_login, url):
    expected_url = f'{url_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
