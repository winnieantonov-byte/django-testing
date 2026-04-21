from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture

from .constants import (
    ADD_URL, DELETE_URL, DETAIL_URL, EDIT_URL,
    HOME_URL, LIST_URL, LOGIN_URL, LOGOUT_URL,
    SIGNUP_URL, SUCCESS_URL
)


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (HOME_URL, lazy_fixture('client'), HTTPStatus.OK),
        (LOGIN_URL, lazy_fixture('client'), HTTPStatus.OK),
        (LOGOUT_URL, lazy_fixture('client'), HTTPStatus.OK),
        (SIGNUP_URL, lazy_fixture('client'), HTTPStatus.OK),
        (LIST_URL, lazy_fixture('author_client'), HTTPStatus.OK),
        (ADD_URL, lazy_fixture('author_client'), HTTPStatus.OK),
        (SUCCESS_URL, lazy_fixture('author_client'), HTTPStatus.OK),
        (DETAIL_URL, lazy_fixture('author_client'), HTTPStatus.OK),
        (EDIT_URL, lazy_fixture('author_client'), HTTPStatus.OK),
        (DELETE_URL, lazy_fixture('author_client'), HTTPStatus.OK),
        (DETAIL_URL, lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (EDIT_URL, lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (DELETE_URL, lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_availability_for_different_users(
    url, parametrized_client, expected_status
):
    assert parametrized_client.get(url).status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (LIST_URL, ADD_URL, SUCCESS_URL, DETAIL_URL, EDIT_URL, DELETE_URL),
)
def test_redirect_for_anonymous_client(client, url, expected_redirect_url):
    assertRedirects(client.get(url), expected_redirect_url(url))
