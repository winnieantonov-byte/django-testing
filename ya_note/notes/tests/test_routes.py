from http import HTTPStatus

from .conftest import (
    ADD_URL, ANON_REDIRECT_CASES, DELETE_URL, DETAIL_URL,
    EDIT_URL, LIST_URL, LOGIN_URL, SUCCESS_URL, BaseTestCase
)


class TestRoutes(BaseTestCase):

    def test_pages_availability(self):
        urls = (
            (LIST_URL, self.author_client, HTTPStatus.OK),
            (ADD_URL, self.author_client, HTTPStatus.OK),
            (SUCCESS_URL, self.author_client, HTTPStatus.OK),
            (EDIT_URL, self.author_client, HTTPStatus.OK),
            (DELETE_URL, self.author_client, HTTPStatus.OK),
            (DETAIL_URL, self.author_client, HTTPStatus.OK),
            (EDIT_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (DELETE_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (DETAIL_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (LOGIN_URL, self.client, HTTPStatus.OK),
        )
        for url, client, status in urls:
            with self.subTest(url=url, client=client):
                self.assertEqual(client.get(url).status_code, status)

    def test_redirect_for_anonymous_client(self):
        for url, expected_redirect in ANON_REDIRECT_CASES:
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), expected_redirect)
