from notes.forms import NoteForm

from .conftest import ADD_URL, EDIT_URL, LIST_URL, BaseTestCase


class TestContent(BaseTestCase):

    def test_note_in_list_for_author(self):
        notes = self.author_client.get(LIST_URL).context['object_list']
        self.assertIn(self.note, notes)
        note = notes.get(pk=self.note.pk)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_note_not_in_list_for_reader(self):
        self.assertNotIn(
            self.note,
            self.reader_client.get(LIST_URL).context['object_list']
        )

    def test_pages_contain_form(self):
        for url in (ADD_URL, EDIT_URL):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
