from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .constants import ADD_URL, DELETE_URL, EDIT_URL, SUCCESS_URL


@pytest.mark.django_db
def test_user_can_create_note(author_client, author, form_data):
    notes_before = Note.objects.count()
    assertRedirects(author_client.post(ADD_URL, data=form_data), SUCCESS_URL)
    assert Note.objects.count() == notes_before + 1
    new_note = Note.objects.get(slug=form_data['slug'])
    assert new_note.title == form_data['title']
    assert new_note.text == form_data['text']
    assert new_note.author == author


@pytest.mark.django_db
def test_user_cant_create_note_with_non_unique_slug(
    author_client, note, form_data
):
    notes_before = list(Note.objects.all())
    form_data['slug'] = note.slug
    response = author_client.post(ADD_URL, data=form_data)
    assert response.status_code == HTTPStatus.OK
    assert WARNING in response.context['form'].errors['slug']
    assert notes_before == list(Note.objects.all())


@pytest.mark.django_db
def test_empty_slug_is_filled_by_slugify(author_client, author, form_data):
    notes_before = Note.objects.count()
    form_data.pop('slug')
    assertRedirects(author_client.post(ADD_URL, data=form_data), SUCCESS_URL)
    assert Note.objects.count() == notes_before + 1
    new_note = Note.objects.get(title=form_data['title'])
    assert new_note.slug == slugify(form_data['title'])
    assert new_note.author == author


@pytest.mark.django_db
def test_author_can_edit_note(author_client, author, note, form_data):
    assertRedirects(author_client.post(EDIT_URL, data=form_data), SUCCESS_URL)
    note_from_db = Note.objects.get(id=note.id)
    assert note_from_db.title == form_data['title']
    assert note_from_db.text == form_data['text']
    assert note_from_db.slug == form_data['slug']
    assert note_from_db.author == author


@pytest.mark.django_db
def test_reader_cant_edit_note_of_another_user(
    reader_client, author, note, form_data
):
    response = reader_client.post(EDIT_URL, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    note_from_db = Note.objects.get(id=note.id)
    assert note_from_db.author == author
    note_from_db = Note.objects.get(id=note.id)
    assert note_from_db.author == author


@pytest.mark.django_db
def test_author_can_delete_note(author_client, note):
    notes_before = Note.objects.count()
    assertRedirects(author_client.post(DELETE_URL), SUCCESS_URL)
    assert Note.objects.count() == notes_before - 1


@pytest.mark.django_db
def test_reader_cant_delete_note_of_another_user(reader_client, note):
    notes_before = list(Note.objects.all())
    assert reader_client.post(DELETE_URL).status_code == HTTPStatus.NOT_FOUND
    assert notes_before == list(Note.objects.all())
