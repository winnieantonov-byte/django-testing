from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = 'Новый текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый текст комментария'
FORM_DATA = {'text': COMMENT_TEXT}
NEW_FORM_DATA = {'text': NEW_COMMENT_TEXT}


def test_anonymous_user_cant_create_comment(client, url_detail):
    client.post(url_detail, data=FORM_DATA)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client, author, news, url_detail, url_to_comments
):
    response = author_client.post(url_detail, data=FORM_DATA)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == COMMENT_TEXT
    assert new_comment.news == news
    assert new_comment.author == author


@pytest.mark.parametrize('word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, url_detail, word):
    bad_words_data = {'text': f'Текст с {word}'}
    response = author_client.post(url_detail, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert WARNING in response.context['form'].errors['text']
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, url_delete, url_to_comments):
    response = author_client.post(url_delete)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
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
    author_client, url_edit, url_to_comments, comment
):
    response = author_client.post(url_edit, data=NEW_FORM_DATA)
    assertRedirects(response, url_to_comments)
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == NEW_COMMENT_TEXT
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news


def test_user_cant_edit_comment_of_another_user(
    reader_client, url_edit, comment
):
    response = reader_client.post(url_edit, data=NEW_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text
    assert comment_from_db.author == comment.author
    assert comment_from_db.news == comment.news
