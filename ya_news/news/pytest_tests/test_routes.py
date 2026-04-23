from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status, method, expected_url',
    (
        (
            lazy_fixture('home_url'),
            lazy_fixture('client'),
            HTTPStatus.OK,
            'get',
            None
        ),
        (
            lazy_fixture('login_url'),
            lazy_fixture('client'),
            HTTPStatus.OK,
            'get',
            None
        ),
        (
            lazy_fixture('logout_url'),
            lazy_fixture('client'),
            HTTPStatus.OK,
            'post',
            None
        ),
        (
            lazy_fixture('signup_url'),
            lazy_fixture('client'),
            HTTPStatus.OK,
            'get',
            None
        ),
        (
            lazy_fixture('url_detail'),
            lazy_fixture('client'),
            HTTPStatus.OK,
            'get',
            None
        ),
        (
            lazy_fixture('url_edit'),
            lazy_fixture('author_client'),
            HTTPStatus.OK,
            'get',
            None
        ),
        (
            lazy_fixture('url_edit'),
            lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND,
            'get',
            None
        ),
        (
            lazy_fixture('url_delete'),
            lazy_fixture('author_client'),
            HTTPStatus.OK,
            'get',
            None
        ),
        (
            lazy_fixture('url_delete'),
            lazy_fixture('reader_client'),
            HTTPStatus.NOT_FOUND,
            'get',
            None
        ),
        (
            lazy_fixture('url_edit'),
            lazy_fixture('client'),
            HTTPStatus.FOUND,
            'get',
            lazy_fixture('expected_edit_redirect_url')
        ),
        (
            lazy_fixture('url_delete'),
            lazy_fixture('client'),
            HTTPStatus.FOUND,
            'get',
            lazy_fixture('expected_delete_redirect_url')
        ),
    ),
)
def test_pages_availability_and_redirects(
    url, parametrized_client, expected_status, method, expected_url
):
    response = getattr(parametrized_client, method)(url)
    assert response.status_code == expected_status
    if expected_url:
        assertRedirects(response, expected_url)
