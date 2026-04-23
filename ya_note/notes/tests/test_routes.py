from http import HTTPStatus
from .conftest import BaseTestCase


class TestRoutes(BaseTestCase):

    def test_status_codes(self):
        response = self.author_client.get(self.LIST_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        for url, expected_redirect in self.ANON_REDIRECT_CASES:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, expected_redirect)
