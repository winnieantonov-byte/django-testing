from http import HTTPStatus

from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .conftest import BaseTestCase


class TestLogic(BaseTestCase):

    def test_user_can_create_note(self):
        notes_before = Note.objects.count()
        response = self.author_client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_before + 1)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes_before = set(Note.objects.all())
        response = self.client.post(self.ADD_URL, data=self.form_data)
        expected_url = f'{reverse("users:login")}?next={self.ADD_URL}'
        self.assertRedirects(response, expected_url)
        self.assertSetEqual(notes_before, set(Note.objects.all()))

    def test_not_unique_slug(self):
        notes_before = set(Note.objects.all())
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.ADD_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form = response.context['form']
        self.assertIn('slug', form.errors)
        self.assertEqual(form.errors['slug'][0], self.note.slug + WARNING)
        self.assertSetEqual(notes_before, set(Note.objects.all()))

    def test_empty_slug_is_filled_by_slugify(self):
        self.form_data.pop('slug')
        notes_before = Note.objects.count()
        response = self.author_client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_before + 1)
        new_note = Note.objects.get(title=self.form_data['title'])
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.EDIT_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        updated_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])
        self.assertEqual(updated_note.author, self.author)

    def test_reader_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.EDIT_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, note_from_db.author)

    def test_author_can_delete_note(self):
        notes_before = Note.objects.count()
        response = self.author_client.post(self.DELETE_URL)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_before - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_reader_cant_delete_note_of_another_user(self):
        notes_before = set(Note.objects.all())
        response = self.reader_client.post(self.DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertSetEqual(notes_before, set(Note.objects.all()))
