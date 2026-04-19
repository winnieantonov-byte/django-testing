import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, url_detail):
    form_data = {'text': 'Текст комментария'}
    client.post(url_detail, data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(
    author_client, author, news, url_detail, url_to_comments
):
    text = 'Текст комментария'
    form_data = {'text': text}
    response = author_client.post(url_detail, data=form_data)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == text
    assert new_comment.news == news
    assert new_comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, url_detail):
    bad_words_data = {'text': f'Текст с {BAD_WORDS[0]}'}
    response = author_client.post(url_detail, data=bad_words_data)
    assertFormError(
        response,
        'form',
        'text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, delete_url, url_to_comments):
    response = author_client.post(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client, delete_url):
    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, edit_url, url_to_comments, comment
):
    new_text = 'Обновлённый текст'
    form_data = {'text': new_text}
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == new_text


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    reader_client, edit_url, comment
):
    old_text = comment.text
    new_text = 'Обновлённый текст'
    form_data = {'text': new_text}
    response = reader_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_text
