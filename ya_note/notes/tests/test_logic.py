from http import HTTPStatus

from notes.models import Note
from .conftest import (
    ADD_URL, DELETE_URL, EDIT_URL, REDIRECT_URL, SUCCESS_URL, BaseTestCase
)


class TestLogic(BaseTestCase):

    def test_user_can_create_note(self):
        existing_ids = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), len(existing_ids) + 1)
        note = Note.objects.exclude(id__in=existing_ids).get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes_count = Note.objects.count()
        response = self.client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, REDIRECT_URL)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_empty_slug_is_filled_by_slugify(self):
        existing_ids = set(Note.objects.values_list('id', flat=True))
        self.form_data.pop('slug')
        self.author_client.post(ADD_URL, data=self.form_data)
        note = Note.objects.exclude(id__in=existing_ids).get()
        self.assertTrue(note.slug)

    def test_author_can_edit_note(self):
        expected_author = self.note.author
        response = self.author_client.post(EDIT_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, expected_author)

    def test_reader_cant_edit_note_of_another_user(self):
        old_title = self.note.title
        response = self.reader_client.post(EDIT_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, old_title)

    def test_author_can_delete_note(self):
        notes_count = Note.objects.count()
        response = self.author_client.post(DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count - 1)

    def test_reader_cant_delete_note_of_another_user(self):
        notes_count = Note.objects.count()
        expected_title = self.note.title
        expected_text = self.note.text
        expected_slug = self.note.slug
        expected_author = self.note.author
        response = self.reader_client.post(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, expected_title)
        self.assertEqual(self.note.text, expected_text)
        self.assertEqual(self.note.slug, expected_slug)
        self.assertEqual(self.note.author, expected_author)
