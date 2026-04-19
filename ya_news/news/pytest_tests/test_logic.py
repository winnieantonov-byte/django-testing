import pytest
from http import HTTPStatus

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News


@pytest.fixture
def news(db):
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def author(db, django_user_model):
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def reader(db, django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def auth_client(reader, client):
    client.force_login(reader)
    return client


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.fixture
def url_detail(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def url_to_comments(url_detail):
    return url_detail + '#comments'


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, url_detail):
    form_data = {'text': 'Текст комментария'}
    client.post(url_detail, data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(auth_client, url_detail, url_to_comments, news, reader):
    text = 'Текст комментария'
    form_data = {'text': text}
    response = auth_client.post(url_detail, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == url_to_comments
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == text
    assert comment.news == news
    assert comment.author == reader


@pytest.mark.django_db
def test_user_cant_use_bad_words(auth_client, url_detail):
    bad_words_data = {'text': f'Текст с {BAD_WORDS[0]}'}
    response = auth_client.post(url_detail, data=bad_words_data)
    form = response.context['form']
    assert WARNING in form.errors['text']
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, delete_url, url_to_comments):
    response = author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == url_to_comments
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client, delete_url):
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, edit_url, url_to_comments, comment):
    new_text = 'Обновлённый комментарий'
    form_data = {'text': new_text}
    response = author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == url_to_comments
    comment.refresh_from_db()
    assert comment.text == new_text


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(reader_client, edit_url, comment):
    old_text = comment.text
    new_text = 'Обновлённый комментарий'
    form_data = {'text': new_text}
    response = reader_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_text
