from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = {'text': 'Текст комментария'}
BAD_WORDS_DATA = [{'text': word} for word in BAD_WORDS]


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, url_detail):
    response = client.post(url_detail, data=COMMENT_TEXT)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_auth_user_can_create_comment(
    author_client, author, news, url_detail, url_detail_to_comments
):
    response = author_client.post(url_detail, data=COMMENT_TEXT)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, url_detail_to_comments)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize('bad_words_data', BAD_WORDS_DATA)
def test_user_cant_use_bad_words(author_client, url_detail, bad_words_data):
    response = author_client.post(url_detail, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert WARNING in response.context['form'].errors['text']
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
    author_client, url_delete, url_detail_to_comments
):
    response = author_client.post(url_delete)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, url_detail_to_comments)
    assert Comment.objects.count() == 0


def test_reader_cant_delete_comment_of_author(
    reader_client, url_delete, comment
):
    response = reader_client.post(url_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news


def test_author_can_edit_comment(
    author_client, comment, url_edit, url_detail_to_comments
):
    response = author_client.post(url_edit, data=BAD_WORDS_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, url_detail_to_comments)
    comment.refresh_from_db()
    assert comment.text == BAD_WORDS_DATA


def test_reader_cant_edit_comment_of_author(
    reader_client, comment, url_edit
):
    response = reader_client.post(url_edit, data=COMMENT_TEXT)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news
