from notes.forms import NoteForm
from .conftest import BaseTestCase


class TestContent(BaseTestCase):

    def test_note_in_list_for_author(self):
        response = self.author_client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        note_obj = object_list.get(pk=self.note.pk)
        self.assertEqual(note_obj.title, self.note.title)
        self.assertEqual(note_obj.text, self.note.text)
        self.assertEqual(note_obj.slug, self.note.slug)
        self.assertEqual(note_obj.author, self.author)

    def test_note_not_in_list_for_reader(self):
        response = self.reader_client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_add_page_contains_form(self):
        response = self.author_client.get(self.ADD_URL)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_page_contains_form(self):
        response = self.author_client.get(self.EDIT_URL)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
