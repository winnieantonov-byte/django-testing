from http import HTTPStatus

from pytils.translit import slugify

from notes.models import Note
from .conftest import (
    ADD_REDIRECT, ADD_URL, DELETE_URL, EDIT_URL, SUCCESS_URL, BaseTestCase
)


class TestLogic(BaseTestCase):

    def test_user_can_create_note(self):
        existing_pks = set(Note.objects.values_list('pk', flat=True))
        response = self.author_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        new_notes = Note.objects.exclude(pk__in=existing_pks)
        self.assertEqual(new_notes.count(), 1)
        note = new_notes.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes_count_before = Note.objects.count()
        response = self.client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, ADD_REDIRECT)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count_after)

    def test_empty_slug_is_filled_by_slugify(self):
        existing_pks = set(Note.objects.values_list('pk', flat=True))
        self.form_data.pop('slug')
        self.author_client.post(ADD_URL, data=self.form_data)
        new_notes = Note.objects.exclude(pk__in=existing_pks)
        self.assertEqual(new_notes.count(), 1)
        note = new_notes.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, slugify(self.form_data['title']))
        self.assertEqual(note.author, self.author)

    def test_author_can_edit_note(self):
        response = self.author_client.post(EDIT_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.note.refresh_from_db()
        note = self.note
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_reader_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(EDIT_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_author_can_delete_note(self):
        notes_count_before = Note.objects.count()
        self.assertRedirects(self.author_client.post(DELETE_URL), SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count_before - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_reader_cant_delete_note_of_another_user(self):
        self.assertEqual(
            self.reader_client.post(DELETE_URL).status_code,
            HTTPStatus.NOT_FOUND
        )
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)
