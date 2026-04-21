from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug',
            author=cls.author
        )

    def test_notes_list_for_different_users(self):
        users_params = (
            (self.author, True),
            (self.reader, False),
        )
        for user, note_in_list in users_params:
            with self.subTest(user=user):
                self.client.force_login(user)
                response = self.client.get(self.LIST_URL)
                all_notes = response.context['object_list']
                self.assertEqual((self.note in all_notes), note_in_list)
                if note_in_list:
                    note_obj = all_notes.get(slug=self.note.slug)
                    self.assertEqual(note_obj.title, self.note.title)
                    self.assertEqual(note_obj.text, self.note.text)
                    self.assertEqual(note_obj.slug, self.note.slug)

    def test_pages_contains_form(self):
        urls = (
            reverse('notes:add'),
            reverse('notes:edit', args=(self.note.slug,)),
        )
        self.client.force_login(self.author)
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
