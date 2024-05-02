import pytest

from django.test.client import Client

from notes.models import Note


@pytest.fixture
def author(django_user_model):
    """Автор заметки."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Читатель заметки."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Клиент автора заметки."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Клиент читателя заметки."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def note(author):
    """Заметка."""
    note = Note.objects.create(
        title='Заголовок',
        text='Текст заметки',
        slug='note-slug',
        author=author
    )
    return note


@pytest.fixture
def slug_for_args(note):
    """Возвращает слаг заметки в виде кортежа."""
    return (note.slug,)


@pytest.fixture
def form_data():
    """Данные для формы изменения заметки."""
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
        'slug': 'new-slug'
    } 
