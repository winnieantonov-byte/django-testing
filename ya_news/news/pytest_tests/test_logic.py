from http import HTTPStatus

import pytest
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, url_detail):
    client.post(url_detail, data={'text': 'Текст комментария'})
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(
    author_client, author, news, url_detail
):
    author_client.post(url_detail, data={'text': 'Текст'})
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == 'Текст'
    assert new_comment.news == news
    assert new_comment.author == author


@pytest.mark.parametrize('word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, url_detail, word):
    bad_words_data = {'text': f'Текст с {word}'}
    response = author_client.post(url_detail, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert WARNING in response.context['form'].errors
    assert Comment.objects.count() == 0

def test_author_can_delete_comment(author_client, url_delete):
    author_client.post(url_delete)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(reader_client, comment):
    response = reader_client.post(reverse('news:delete', args=(comment.id,)))
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, url_edit, comment):
    author_client.post(url_edit, data={'text': 'Новый текст'})
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == 'Новый текст'


def test_user_cant_edit_comment_of_another_user(reader_client, comment):
    response = reader_client.post(
        reverse('news:edit', args=(comment.id,)),
        data={'text': 'Новый текст'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text
