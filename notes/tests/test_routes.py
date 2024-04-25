from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    """Тестирование маршрутов."""

    @classmethod
    def setUpTestData(cls):
        """Добавление тестовых данных для последующих проверок."""
        cls.author = User.objects.create(username='Иванов Иван')
        cls.reader = User.objects.create(username='Простой читатель')
        cls.note = Note.objects.create(
            title='Заголовок заметки',
            text='Текст заметки',
            slug='zametka',
            author=cls.author
        )

    def test_availability_for_pages_home_and_auth(self):
        """Доступность общих страниц для неавторизованных пользователей."""
        pages = ['notes:home', 'users:login', 'users:logout', 'users:signup']

        for page in pages:
            with self.subTest(page=page):
                url = reverse(page)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_pages_add_success_and_list(self):
        """Доступность страниц создания и просмотра списка всех заметок."""
        pages = ['notes:add', 'notes:success', 'notes:list']
        self.client.force_login(self.author)
        for page in pages:
            with self.subTest(page=page):
                url = reverse(page)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_detail_edit_and_delete(self):
        """Доступность страниц просмотра, редактирования и удаления заметки."""
        note_kwargs = {'slug': self.note.slug}
        pages = (
            ('notes:detail', note_kwargs),
            ('notes:edit', note_kwargs),
            ('notes:delete', note_kwargs),
        )
        users = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )

        for user, status in users:
            self.client.force_login(user)
            for page, kwargs in pages:
                with self.subTest(user=user, page=page):
                    url = reverse(page, kwargs=kwargs)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Редирект анонимных пользователей.

        Анонимные пользователи при просмотре любых страниц,
        связанных с заметками, должны перенаправляться
        на страницу авторизации.
        """
        note_kwargs = {'slug': self.note.slug}
        pages = (
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
            ('notes:detail', note_kwargs),
            ('notes:edit', note_kwargs),
            ('notes:delete', note_kwargs),
        )

        login_url = reverse('users:login')

        for page, kwargs in pages:
            with self.subTest(page=page):
                url = reverse(page, kwargs=kwargs)
                reditect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, reditect_url)
