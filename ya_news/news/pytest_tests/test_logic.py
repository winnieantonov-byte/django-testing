from http import HTTPStatus

import pytest
from news.models import Comment

from .conftest import BAD_WORDS_CASES, CREATE_COMMENT_CASES


@pytest.mark.parametrize(
    'client_fixture, expected_count', CREATE_COMMENT_CASES
)
def test_create_comment_count(
    request, client_fixture, expected_count, url_detail, form_data
):
    client = request.getfixturevalue(client_fixture)
    client.post(url_detail, data=form_data)
    assert Comment.objects.count() == expected_count


def test_author_comment_fields(
    author_client, url_detail, author, news, form_data
):
    author_client.post(url_detail, data=form_data)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == author


@pytest.mark.parametrize('form_data_bad', BAD_WORDS_CASES)
def test_comment_validation(author_client, url_detail, form_data_bad):
    response = author_client.post(url_detail, data=form_data_bad)
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, url_delete):
    response = author_client.post(url_delete)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_reader_cant_delete_comment_of_author(reader_client, url_delete):
    response = reader_client.post(url_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, url_edit, comment, form_data):
    new_text = 'Обновленный текст'
    form_data['text'] = new_text
    response = author_client.post(url_edit, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == new_text


def test_reader_cant_edit_comment_of_author(
    reader_client, url_edit, comment, form_data
):
    old_text = comment.text
    new_text = 'Обновленный текст'
    form_data['text'] = new_text
    response = reader_client.post(url_edit, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_text
