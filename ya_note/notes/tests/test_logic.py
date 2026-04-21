from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):
    ADD_URL = reverse('notes:add')
    SUCCESS_URL = reverse('notes:success')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'note-slug'
        }

    def test_user_can_create_note(self):
        self.client.force_login(self.author)
        notes_before = Note.objects.count()
        response = self.client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_before + 1)
        # Ищем по слагу из формы
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data)
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes_before = Note.objects.count()
        self.client.post(self.ADD_URL, data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_before)

    def test_not_unique_slug(self):
        note = Note.objects.create(
            title='Оригинал', text='Текст', slug='unique', author=self.author
        )
        self.form_data['slug'] = note.slug
        notes_before = Note.objects.count()
        self.client.force_login(self.author)
        response = self.client.post(self.ADD_URL, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), notes_before)

    def test_empty_slug_is_filled_by_slugify(self):
        self.client.force_login(self.author)
        self.form_data.pop('slug')
        notes_before = Note.objects.count()
        response = self.client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_before + 1)
        # Ищем по заголовку
        new_note = Note.objects.get(title=self.form_data['title'])
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))

    def test_author_can_edit_note(self):
        note = Note.objects.create(
            title='Старый', text='Текст', slug='slug', author=self.author
        )
        url = reverse('notes:edit', args=(note.slug,))
        self.client.force_login(self.author)
        self.client.post(url, data=self.form_data)
        # Получаем обновленный объект по тому же слагу
        note_from_db = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(note_from_db.title, self.form_data['title'])
        self.assertEqual(note_from_db.text, self.form_data)
        self.assertEqual(note_from_db.author, self.author)

    def test_reader_cant_edit_note_of_another_user(self):
        note = Note.objects.create(
            title='Заголовок', text='Текст', slug='slug', author=self.author
        )
        url = reverse('notes:edit', args=(note.slug,))
        self.client.force_login(self.reader)
        response = self.client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Проверяем, что в базе все осталось по-прежнему
        note_from_db = Note.objects.get(slug=note.slug)
        self.assertEqual(note.title, note_from_db.title)
        self.assertEqual(note.author, self.author)

    def test_author_can_delete_note(self):
        note = Note.objects.create(
            title='Удалить', text='Текст', slug='del', author=self.author
        )
        url = reverse('notes:delete', args=(note.slug,))
        notes_before = Note.objects.count()
        self.client.force_login(self.author)
        self.client.post(url)
        self.assertEqual(Note.objects.count(), notes_before - 1)

    def test_reader_cant_delete_note_of_another_user(self):
        note = Note.objects.create(
            title='Заголовок', text='Текст', slug='slug', author=self.author
        )
        url = reverse('notes:delete', args=(note.slug,))
        notes_before = Note.objects.count()
        self.client.force_login(self.reader)
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_before)
