from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestListPage(TestCase):
    """Тестирование страницы списка записей автора."""

    TEST_NOTES_COUNT = 15

    @classmethod
    def setUpTestData(cls):
        """Добавление авторов, их клиентов и их заметок."""
        cls.author = User.objects.create(username='Иванов Иван')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        # Создаем несколько заметок, чтобы убедиться, что нет пагинации.
        all_notes_author = [Note(
            title=f'Заметка {idx}',
            text='Текст заметки',
            slug=f'zametka_{idx}',
            author=cls.author
        ) for idx in range(cls.TEST_NOTES_COUNT)]
        Note.objects.bulk_create(all_notes_author)
        cls.other_user = User.objects.create(username='Другой пользователь')
        cls.auth_other_user = Client()
        cls.auth_other_user.force_login(cls.other_user)
        cls.note_other_user = Note.objects.create(
            title='Заметка другого пользователя',
            text='Текст',
            slug='slug_other_user',
            author=cls.other_user
        )

    def test_list_notes(self):
        """Тест вывода записей без пагинации."""
        url = reverse('notes:list')
        response = self.auth_client.get(url)
        notes_count = response.context['object_list'].count()
        self.assertEqual(notes_count, self.TEST_NOTES_COUNT)

    def test_user_can_see_only_own_notes(self):
        """Пользователь может видеть только свои заметки."""
        url = reverse('notes:list')
        response = self.auth_other_user.get(url)
        notes = response.context['object_list']
        # Ползователь получил только свою заметку.
        self.assertEqual(notes.count(), 1)
        note = notes[0]
        # Заголовок заметки соответствует созданной им заметки.
        self.assertEqual(note.title, self.note_other_user.title)
        count_all_notes_in_db = Note.objects.count()
        # В БД хранятся все заметки всех пользователей.
        self.assertEqual(count_all_notes_in_db, self.TEST_NOTES_COUNT + 1)


class TestAddNote(TestCase):
    """Тест создания и редактирования заметки."""

    @classmethod
    def setUpTestData(cls):
        """Добавление автора, создание клиента и добавление заметки."""
        cls.author = User.objects.create(username='Иванов Иван')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовое',
            text='Текст',
            slug='zagolovok',
            author=cls.author
        )

    def test_authorized_client_has_form(self):
        """Отображение формы создания и редактирования заметки."""
        note_kwargs = {'slug': self.note.slug}
        pages = (
            ('notes:add', None),
            ('notes:edit', note_kwargs),
        )
        for page, kwargs in pages:
            with self.subTest(page=page, kwargs=kwargs):
                url = reverse(page, kwargs=kwargs)
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
