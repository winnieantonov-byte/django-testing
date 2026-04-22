from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


PAGES_AVAILABILITY_CASES = (
    (
        lazy_fixture('home_url'),
        lazy_fixture('client'),
        HTTPStatus.OK, 'get'),
    (
        lazy_fixture('login_url'),
        lazy_fixture('client'),
        HTTPStatus.OK, 'get'),
    (
        lazy_fixture('logout_url'),
        lazy_fixture('client'),
        HTTPStatus.OK, 'post'),
    (
        lazy_fixture('signup_url'),
        lazy_fixture('client'),
        HTTPStatus.OK, 'get'),
    (
        lazy_fixture('url_detail'),
        lazy_fixture('client'),
        HTTPStatus.OK, 'get'),
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
)

REDIRECT_CASES = (
    (lazy_fixture('url_edit'), HTTPStatus.FOUND, lazy_fixture('login_url')),
    (lazy_fixture('url_delete'), HTTPStatus.FOUND, lazy_fixture('login_url')),
)


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status, method',
    PAGES_AVAILABILITY_CASES,
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
    'url, expected_status, login_url',
    REDIRECT_CASES,
)
def test_redirect_for_anonymous_client(
    client, url, expected_status, login_url
):
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == expected_status
    assertRedirects(response, expected_url)
