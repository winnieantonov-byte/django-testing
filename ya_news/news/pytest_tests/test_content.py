from django.conf import settings
from news.forms import CommentForm


def test_news_count(client, url_home, all_news):
    response = client.get(url_home)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, url_home, all_news):
    response = client.get(url_home)
    news_dates = [news.date for news in response.context['object_list']]
    assert news_dates == sorted(news_dates, reverse=True)


def test_comments_order(client, url_detail, comment):
    response = client.get(url_detail)
    assert 'news' in response.context
    timestamps = [
        c.created for c in response.context['news'].comment_set.all()
    ]
    assert timestamps == sorted(timestamps)


def test_anonymous_client_has_no_form(client, url_detail):
    response = client.get(url_detail)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, url_detail):
    response = author_client.get(url_detail)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
