from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


NOTE_TITLE = 'Заметка'
NOTE_TEXT = 'Текст заметки'
NOTE_SLUG = 'zametka'

User = get_user_model()


class TestNoteDetail(TestCase):
    """Тестирование отдельной страницы с записью и дубликатов slug."""

    @classmethod
    def setUpTestData(cls):
        """Добавление тестовых данных для последующих проверок."""
        cls.author = User.objects.create(username='Иванов Иван')
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.author)
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=NOTE_SLUG,
            author=cls.author
        )
        cls.reader = User.objects.create(username='Читатель')
        cls.auth_reader = Client()
        cls.auth_reader.force_login(cls.reader)
        cls.note_url = reverse('notes:detail', kwargs={'slug': cls.note.slug})

    def test_authorized_client_can_view_own_note(self):
        """Авторизованный пользователь может видеть свою запись."""
        response = self.auth_user.get(self.note_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_client_cant_view_ahother_note(self):
        """Автризованный пользователь не может видеть чужую запись."""
        response = self.auth_reader.get(self.note_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestDuplicateSlug(TestCase):
    """Тестирование создания записей с одинаковыми slug."""

    @classmethod
    def setUpTestData(cls):
        """Добавление тестовых данных для последующих проверок."""
        cls.author = User.objects.create(username='Иванов Иван')
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=NOTE_SLUG,
            author=cls.author
        )
        cls.user = User.objects.create(username='Другой участник')
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
        cls.url_create_note = reverse('notes:add')
        cls.error_text = NOTE_SLUG + WARNING

    def test_create_note_with_same_slug(self):
        """Создание заметки с тем же самым slug."""
        form_with_same_slug = {
            'title': NOTE_TITLE,
            'text': NOTE_TEXT,
            'slug': NOTE_SLUG
        }
        response = self.auth_user.post(
            self.url_create_note,
            data=form_with_same_slug
        )
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.error_text
        )

    def test_create_note_without_slug(self):
        """Создание заметки без слага."""
        form_with_same_slug = {'title': NOTE_TITLE, 'text': NOTE_TEXT}
        response = self.auth_user.post(
            self.url_create_note,
            data=form_with_same_slug
        )
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.error_text
        )


class TestNoteEditDelete(TestCase):
    """Тестирование редактирования и удаления заметки."""

    NEW_NOTE_TEXT = 'Новый текст заметки'

    @classmethod
    def setUpTestData(cls):
        """Добавление тестовых данных для последующих проверок."""
        cls.author = User.objects.create(username='Автор заметки')
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=NOTE_SLUG,
            author=cls.author
        )
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)

        cls.another_user = User.objects.create(username='Другой пользователь')
        cls.auth_another_user = Client()
        cls.auth_another_user.force_login(cls.another_user)

        cls.kwargs = {'slug': cls.note.slug}
        cls.url_edit_note = reverse('notes:edit', kwargs=cls.kwargs)
        cls.url_delete_note = reverse('notes:delete', kwargs=cls.kwargs)
        cls.url_redirect = reverse('notes:success')
        cls.edit_form_data = {
            'title': NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': NOTE_SLUG
        }

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        response = self.auth_author.delete(self.url_delete_note)
        self.assertRedirects(response, self.url_redirect)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить чужую заявку."""
        response = self.auth_another_user.delete(self.url_delete_note)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_own_note(self):
        """Автор может редактировать свою заметку."""
        response = self.auth_author.post(
            self.url_edit_note,
            data=self.edit_form_data
        )
        self.assertRedirects(response, self.url_redirect)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_author_cant_edit_another_note(self):
        """Пользователь не может редактировать чужую заметку."""
        response = self.auth_another_user.post(
            self.url_edit_note,
            data=self.edit_form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, NOTE_TEXT)
