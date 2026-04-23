import pytest
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, home_url):
    news_count = len(client.get(home_url).context['object_list'])
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, home_url):
    news_dates = [
        news.date for news in client.get(home_url).context['object_list']
    ]
    assert news_dates == sorted(news_dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(client, url_detail):
    news = client.get(url_detail).context['news']
    timestamps = [
        c.created for c in news.comment_set.all()
    ]
    assert timestamps == sorted(timestamps)


def test_anonymous_client_has_no_form(client, url_detail):
    assert 'form' not in client.get(url_detail).context


def test_authorized_client_has_form(author_client, url_detail):
    response = author_client.get(url_detail)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
