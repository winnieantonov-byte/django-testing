from notes.tests.conftest import BaseTestCase
from notes.forms import NoteForm


class TestContent(BaseTestCase):
    def test_notes_list_for_different_users(self):
        users_params = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for client, note_in_list in users_params:
            with self.subTest(client=client):
                response = client.get(self.LIST_URL)
                all_notes = response.context['object_list']
                self.assertEqual((self.note in all_notes), note_in_list)
                if note_in_list:
                    self.assertEqual(all_notes.count(), 1)
                    note = all_notes[0]
                    self.assertEqual(note.title, self.note.title)
                    self.assertEqual(note.text, self.note.text)
                    self.assertEqual(note.slug, self.note.slug)

    def test_pages_contains_form(self):
        for url in self.PAGES_WITH_FORM_URLS:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
