from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


CREATE_COMMENT_CASES = [
    ("client", 0),
    ("author_client", 1),
]

BAD_WORDS_CASES = [
    (f'Текст с {BAD_WORDS[0]}', True),
    (f'Текст с {BAD_WORDS[1]}', True),
    ('Чистый текст', False),
]

DELETE_COMMENT_CASES = [
    ("author_client", 0, HTTPStatus.FOUND),
    ("reader_client", 1, HTTPStatus.NOT_FOUND),
]

EDIT_COMMENT_CASES = [
    ("author_client", True, HTTPStatus.FOUND),
    ("reader_client", False, HTTPStatus.NOT_FOUND),
]


@pytest.mark.django_db
@pytest.mark.parametrize("client_fixture,expected_count", CREATE_COMMENT_CASES)
def test_create_comment(
    request, client_fixture, expected_count, url_detail, author, news
):
    client = request.getfixturevalue(client_fixture)
    client.post(url_detail, data={'text': 'Текст'})
    assert Comment.objects.count() == expected_count
    if expected_count == 1:
        new_comment = Comment.objects.get()
        assert new_comment.text == 'Текст'
        assert new_comment.news == news
        assert new_comment.author == author


@pytest.mark.django_db
@pytest.mark.parametrize("text,has_bad_words", BAD_WORDS_CASES)
def test_comment_validation(author_client, url_detail, text, has_bad_words):
    response = author_client.post(url_detail, data={'text': text})
    if has_bad_words:
        assert WARNING in response.context['form'].errors['text']
        assert Comment.objects.count() == 0
    else:
        assert Comment.objects.count() == 1


@pytest.mark.parametrize(
    "client_fixture,expected_count,expected_code",
    DELETE_COMMENT_CASES
)
def test_delete_comment(
    request, client_fixture, expected_count, expected_code, url_delete
):
    client = request.getfixturevalue(client_fixture)
    response = client.post(url_delete)
    assert response.status_code == expected_code
    assert Comment.objects.count() == expected_count


@pytest.mark.parametrize(
    "client_fixture,text_changed,expected_code",
    EDIT_COMMENT_CASES
)
def test_edit_comment(
    request, client_fixture, text_changed, expected_code, url_edit, comment
):
    client = request.getfixturevalue(client_fixture)
    new_text = 'Новый текст'
    response = client.post(url_edit, data={'text': new_text})
    assert response.status_code == expected_code
    comment_from_db = Comment.objects.get(id=comment.id)
    if text_changed:
        assert comment_from_db.text == new_text
        assert comment_from_db.news == comment.news
        assert comment_from_db.author == comment.author
    else:
        assert comment_from_db.text == comment.text
        assert comment_from_db.news == comment.news
        assert comment_from_db.author == comment.author
