from django.conf import settings

from news.forms import CommentForm


def test_news_count(client, news_list, home_url):
    response = client.get(home_url)
    assert (
        len(response.context['object_list']) ==
        settings.NEWS_COUNT_ON_HOME_PAGE
    )


def test_news_order(client, news_list, home_url):
    news_dates = [
        news.date
        for news in client.get(home_url).context['object_list']
    ]
    assert news_dates == sorted(news_dates, reverse=True)


def test_comments_order(client, url_detail, comments_list):
    timestamps = [
        c.created
        for c in client.get(url_detail).context['news'].comment_set.all()
    ]
    assert timestamps == sorted(timestamps)


def test_anonymous_client_has_no_form(client, url_detail):
    assert 'form' not in client.get(url_detail).context


def test_authorized_client_has_form(author_client, url_detail):
    form = author_client.get(url_detail).context['form']
    assert isinstance(form, CommentForm)
