from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

BAD_WORDS_CASES = [
    {'text': f'Текст с {word}'} for word in BAD_WORDS
]


def test_anonymous_user_cant_create_comment(client, url_detail, form_data):
    Comment.objects.all().delete()
    client.post(url_detail, data=form_data)
    assert Comment.objects.count() == 0


def test_auth_user_can_create_comment(
    author_client, author, news, url_detail, form_data
):
    Comment.objects.all().delete()
    author_client.post(url_detail, data=form_data)
    assert Comment.objects.count() == 1
    assert Comment.objects.get().text == form_data['text']
    assert Comment.objects.get().news == news
    assert Comment.objects.get().author == author


@pytest.mark.parametrize('form_data_bad', BAD_WORDS_CASES)
def test_user_cant_use_bad_words(author_client, url_detail, form_data_bad):
    Comment.objects.all().delete()
    response = author_client.post(url_detail, data=form_data_bad)
    assert 'form' in response.context
    assert WARNING in response.context['form'].errors['text']


def test_author_can_delete_comment(author_client, url_delete):
    assert author_client.post(url_delete).status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_reader_cant_delete_comment_of_author(
    reader_client, url_delete, comment, author, news
):
    assert reader_client.post(url_delete).status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert Comment.objects.get().text == comment.text
    assert Comment.objects.get().author == author
    assert Comment.objects.get().news == news


def test_author_can_edit_comment(author_client, url_edit, comment, form_data):
    response = author_client.post(url_edit, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_reader_cant_edit_comment_of_author(
    reader_client, url_edit, comment, form_data, author, news
):
    response = reader_client.post(url_edit, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.get().text == comment.text
    assert Comment.objects.get().author == author
    assert Comment.objects.get().news == news
