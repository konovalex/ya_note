from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestListPage(TestCase):
    """Тестирование страницы списка записей пользователя."""

    TEST_NOTES_COUNT = 15

    @classmethod
    def setUpTestData(cls):
        """Добавление тестовых данных для последующих проверок."""
        cls.author = User.objects.create(username='Иванов Иван')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        all_notes = [Note(
            title=f'Заметка {idx}',
            text='Текст заметки',
            slug=f'zametka_{idx}',
            author=cls.author
        ) for idx in range(cls.TEST_NOTES_COUNT)]
        Note.objects.bulk_create(all_notes)

    def test_list_notes(self):
        """Тест вывода записей без пагинации."""
        url = reverse('notes:list')
        response = self.auth_client.get(url)
        notes_count = response.context['object_list'].count()
        self.assertEqual(notes_count, self.TEST_NOTES_COUNT)


class TestAddNote(TestCase):
    """Тест создания новой заметки."""

    @classmethod
    def setUpTestData(cls):
        """Добавление тестовых данных для последующих проверок."""
        cls.author = User.objects.create(username='Иванов Иван')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

    def test_authorized_client_has_form(self):
        """Авторизованному пользователю показывается форма создания заметки."""
        url = reverse('notes:add')
        response = self.auth_client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
