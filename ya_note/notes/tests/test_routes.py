from http import HTTPStatus

from notes.tests.conftest import BaseTestCase


class TestRoutes(BaseTestCase):
    def test_status_codes(self):
        test_cases = (
            (self.client, 'get', self.HOME_URL, HTTPStatus.OK),
            (self.client, 'get', self.LOGIN_URL, HTTPStatus.OK),
            (self.client, 'get', self.SIGNUP_URL, HTTPStatus.OK),
            (self.client, 'post', self.LOGOUT_URL, HTTPStatus.OK),
            (self.reader_client, 'get', self.LIST_URL, HTTPStatus.OK),
            (self.reader_client, 'get', self.ADD_URL, HTTPStatus.OK),
            (self.reader_client, 'get', self.SUCCESS_URL, HTTPStatus.OK),
            (self.author_client, 'get', self.DETAIL_URL, HTTPStatus.OK),
            (self.author_client, 'get', self.EDIT_URL, HTTPStatus.OK),
            (self.author_client, 'get', self.DELETE_URL, HTTPStatus.OK),
            (self.reader_client, 'get', self.DETAIL_URL, HTTPStatus.NOT_FOUND),
            (self.reader_client, 'get', self.EDIT_URL, HTTPStatus.NOT_FOUND),
            (self.reader_client, 'get', self.DELETE_URL, HTTPStatus.NOT_FOUND),
        )
        for client, method, url, expected_status in test_cases:
            with self.subTest(client=client, method=method, url=url):
                response = getattr(client, method)(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        for url, redirect_url in self.ANON_REDIRECT_CASES:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
