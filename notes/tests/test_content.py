from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestListPage(TestCase):
    """Тестирование страницы всех записей пользователя."""
    # Переменная для создания неограниченного количества заметок.
    TEST_NOTE_COUNT = 1

    @classmethod
    def setUpTestData(cls):
        """Добавление тестовых данных для последующих проверок."""
        cls.author = User.objects.create(username='Иванов Иван')
        all_notes = [Note(
            title=f'Заметка {idx}',
            text='Текст заметки',
            slug=f'zametka_{idx}',
            author=cls.author
        ) for idx in range(cls.TEST_NOTE_COUNT)]
        Note.objects.bulk_create(all_notes)

    def test_list_notes(self):
        """Созданы все заметки."""
        url = reverse('notes:list')
        self.client.force_login(self.author)
        response = self.client.get(url)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, self.TEST_NOTE_COUNT)

    def test_authorized_client_has_form(self):
        """Авторизованному пользователю показывается форма создания заметки."""
        url = reverse('notes:add')
        self.client.force_login(self.author)
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
