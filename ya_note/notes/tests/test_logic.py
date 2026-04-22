from http import HTTPStatus

from notes.forms import WARNING
from notes.models import Note
from notes.tests.conftest import BaseTestCase
from pytils.translit import slugify


class TestLogic(BaseTestCase):

    def test_user_can_create_note(self):
        notes_before = Note.objects.count()
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_before + 1)
        new_note = Note.objects.exclude(id__in=note_ids_before).get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes_before = Note.objects.count()
        self.client.post(self.ADD_URL, data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_before)

    def test_not_unique_slug(self):
        notes_before = set(
            Note.objects.values_list(
                'id', 'title', 'text', 'slug', 'author_id'
            )
        )
        form_data = self.form_data.copy()
        form_data['slug'] = self.note.slug
        response = self.author_client.post(self.ADD_URL, data=form_data)
        form = response.context['form']
        self.assertIn(self.note.slug + WARNING, form.errors['slug'])
        notes_after = set(
            Note.objects.values_list(
                'id', 'title', 'text', 'slug', 'author_id'
            )
        )
        self.assertSetEqual(notes_after, notes_before)

    def test_empty_slug_is_filled_by_slugify(self):
        form_data = self.form_data.copy()
        form_data.pop('slug')
        notes_before = Note.objects.count()
        note_ids_before = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(self.ADD_URL, data=form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_before + 1)
        new_note = Note.objects.exclude(id__in=note_ids_before).get()
        self.assertEqual(new_note.title, form_data['title'])
        self.assertEqual(new_note.text, form_data['text'])
        self.assertEqual(new_note.slug, slugify(form_data['title']))
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_note(self):
        original_author = self.note.author
        self.author_client.post(self.EDIT_URL, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, original_author)

    def test_reader_cant_edit_note_of_another_user(self):
        original_title = self.note.title
        original_text = self.note.text
        original_slug = self.note.slug
        original_author = self.note.author
        response = self.reader_client.post(self.EDIT_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, original_title)
        self.assertEqual(self.note.text, original_text)
        self.assertEqual(self.note.slug, original_slug)
        self.assertEqual(self.note.author, original_author)

    def test_author_can_delete_note(self):
        self.author_client.post(self.DELETE_URL)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_reader_cant_delete_note_of_another_user(self):
        notes_before = set(
            Note.objects.values_list(
                'id', 'title', 'text', 'slug', 'author_id'
            )
        )
        response = self.reader_client.post(self.DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_after = set(
            Note.objects.values_list(
                'id', 'title', 'text', 'slug', 'author_id'
            )
        )
        self.assertSetEqual(notes_after, notes_before)
