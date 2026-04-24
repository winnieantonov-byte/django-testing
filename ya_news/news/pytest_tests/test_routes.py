from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture

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

EDIT_REDIRECT = lazy_fixture('expected_edit_redirect_url')
DELETE_REDIRECT = lazy_fixture('expected_delete_redirect_url')


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status, method',
    (
        (HOME_URL, CLIENT, HTTPStatus.OK, 'get'),
        (LOGIN_URL, CLIENT, HTTPStatus.OK, 'get'),
        (LOGOUT_URL, CLIENT, HTTPStatus.OK, 'post'),
        (SIGNUP_URL, CLIENT, HTTPStatus.OK, 'get'),
        (DETAIL_URL, CLIENT, HTTPStatus.OK, 'get'),
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK, 'get'),
        (EDIT_URL, READER_CLIENT, HTTPStatus.NOT_FOUND, 'get'),
        (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK, 'get'),
        (DELETE_URL, READER_CLIENT, HTTPStatus.NOT_FOUND, 'get'),
        (EDIT_URL, CLIENT, HTTPStatus.FOUND, 'get'),
        (DELETE_URL, CLIENT, HTTPStatus.FOUND, 'get'),
    ),
)
def test_pages_availability(
    url, parametrized_client, expected_status, method
):
    response = getattr(parametrized_client, method)(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url, expected_url',
    (
        (EDIT_URL, EDIT_REDIRECT),
        (DELETE_URL, DELETE_REDIRECT),
    ),
)
def test_redirect_for_anonymous_client(client, url, expected_url):
    assertRedirects(client.get(url), expected_url)
