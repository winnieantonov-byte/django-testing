import pytest
from pytest_lazyfixture import lazy_fixture

from notes.forms import NoteForm
from .constants import ADD_URL, EDIT_URL, LIST_URL


@pytest.mark.parametrize(
    'parametrized_client, expected_count',
    (
        (lazy_fixture('author_client'), 1),
        (lazy_fixture('reader_client'), 0),
    ),
)
def test_notes_list_for_different_users(
    parametrized_client, expected_count, note
):
    all_notes = parametrized_client.get(LIST_URL).context['object_list']
    assert all_notes.count() == expected_count
    if expected_count > 0:
        note_from_list = all_notes.get()
        assert note_from_list.title == note.title
        assert note_from_list.text == note.text
        assert note_from_list.slug == note.slug


@pytest.mark.parametrize('url', (ADD_URL, EDIT_URL))
def test_pages_contains_form(author_client, url):
    assert isinstance(author_client.get(url).context['form'], NoteForm)
