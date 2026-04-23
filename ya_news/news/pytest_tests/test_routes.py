import pytest
from pytest_django.asserts import assertRedirects

from .conftest import PAGES_AVAILABILITY_CASES, REDIRECT_CASES


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status, method',
    PAGES_AVAILABILITY_CASES,
)
def test_pages_availability(url, parametrized_client, expected_status, method):
    response = getattr(parametrized_client, method)(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url, expected_status, login_page_url',
    REDIRECT_CASES,
)
def test_redirect_for_anonymous_client(
    client, url, expected_status, login_page_url
):
    expected_url = f'{login_page_url}?next={url}'
    response = client.get(url)
    assert response.status_code == expected_status
    assertRedirects(response, expected_url)
