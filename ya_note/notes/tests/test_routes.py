from http import HTTPStatus

from .conftest import (
    ADD_REDIRECT, ADD_URL, DELETE_REDIRECT, DELETE_URL,
    DETAIL_REDIRECT, DETAIL_URL, EDIT_REDIRECT, EDIT_URL,
    LIST_REDIRECT, LIST_URL, LOGIN_URL, SUCCESS_REDIRECT,
    SUCCESS_URL, BaseTestCase
)


class TestRoutes(BaseTestCase):

    def test_pages_availability(self):
        ok = HTTPStatus.OK
        not_found = HTTPStatus.NOT_FOUND
        found = HTTPStatus.FOUND

        urls = (
            (LIST_URL, self.author_client, ok),
            (ADD_URL, self.author_client, ok),
            (SUCCESS_URL, self.author_client, ok),
            (EDIT_URL, self.author_client, ok),
            (DELETE_URL, self.author_client, ok),
            (DETAIL_URL, self.author_client, ok),
            (EDIT_URL, self.reader_client, not_found),
            (DELETE_URL, self.reader_client, not_found),
            (DETAIL_URL, self.reader_client, not_found),
            (LOGIN_URL, self.client, ok),
            (LIST_URL, self.client, found),
            (ADD_URL, self.client, found),
            (SUCCESS_URL, self.client, found),
            (EDIT_URL, self.client, found),
            (DELETE_URL, self.client, found),
            (DETAIL_URL, self.client, found),
        )
        for url, client, status in urls:
            with self.subTest(url=url, client=client):
                self.assertEqual(client.get(url).status_code, status)

    def test_redirect_for_anonymous_client(self):
        redirect_cases = (
            (LIST_URL, LIST_REDIRECT),
            (ADD_URL, ADD_REDIRECT),
            (SUCCESS_URL, SUCCESS_REDIRECT),
            (EDIT_URL, EDIT_REDIRECT),
            (DELETE_URL, DELETE_REDIRECT),
            (DETAIL_URL, DETAIL_REDIRECT),
        )
        for url, expected_redirect in redirect_cases:
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), expected_redirect)
