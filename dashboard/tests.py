from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Notes, Homework, Todo, Expense, Profile
from datetime import datetime, timedelta
import json

# Create your tests here.

class WebViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_notes_create_view(self):
        response = self.client.post(reverse('notes'), {
            'title': 'Test Note',
            'description': 'Test Description'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Notes.objects.filter(user=self.user, title='Test Note').exists())

    def test_homework_create_view(self):
        response = self.client.post(reverse('homework'), {
            'subject': 'Math',
            'title': 'Test Homework',
            'description': 'Test Description',
            'due': (datetime.now() + timedelta(days=1)).date()
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Homework.objects.filter(user=self.user, title='Test Homework').exists())

    def test_todo_create_view(self):
        response = self.client.post(reverse('todo'), {
            'title': 'Test Todo'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Todo.objects.filter(user=self.user, title='Test Todo').exists())

    def test_expense_create_view(self):
        response = self.client.post(reverse('expense'), {
            'text': 'Test Expense',
            'amount': '100.00',
            'expense_type': 'Negative'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Expense.objects.filter(user=self.user, name='Test Expense').exists())

    def test_update_homework_view(self):
        homework = Homework.objects.create(
            user=self.user,
            subject='Math',
            title='Test Homework',
            description='Test',
            due=datetime.now() + timedelta(days=1),
            is_finished=False
        )
        response = self.client.get(reverse('update-homework', kwargs={'pk': homework.id}))
        self.assertEqual(response.status_code, 302)
        homework.refresh_from_db()
        self.assertTrue(homework.is_finished)

    def test_update_todo_view(self):
        todo = Todo.objects.create(
            user=self.user,
            title='Test Todo',
            is_finished=False
        )
        response = self.client.get(reverse('update-todo', kwargs={'pk': todo.id}))
        self.assertEqual(response.status_code, 302)
        todo.refresh_from_db()
        self.assertTrue(todo.is_finished)

    def test_delete_note_view(self):
        note = Notes.objects.create(
            user=self.user,
            title='Test Note',
            description='Test'
        )
        response = self.client.get(reverse('delete-note', kwargs={'pk': note.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Notes.objects.filter(id=note.id).exists())


class APITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_notes_api_create(self):
        data = {'title': 'API Note', 'description': 'API Description'}
        response = self.client.post('/api/notes/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Notes.objects.filter(user=self.user, title='API Note').exists())

    def test_notes_api_list(self):
        Notes.objects.create(user=self.user, title='Note 1', description='Desc 1')
        Notes.objects.create(user=self.user, title='Note 2', description='Desc 2')
        response = self.client.get('/api/notes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_notes_api_update(self):
        note = Notes.objects.create(user=self.user, title='Old Title', description='Old Desc')
        data = {'title': 'New Title', 'description': 'New Desc'}
        response = self.client.put(f'/api/notes/{note.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        self.assertEqual(note.title, 'New Title')

    def test_homework_api_create(self):
        data = {
            'subject': 'Math',
            'title': 'API Homework',
            'description': 'API Desc',
            'due': (datetime.now() + timedelta(days=1)).isoformat(),
            'is_finished': False
        }
        response = self.client.post('/api/homeworks/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Homework.objects.filter(user=self.user, title='API Homework').exists())

    def test_homework_api_toggle_finished(self):
        homework = Homework.objects.create(
            user=self.user,
            subject='Math',
            title='Test',
            description='Test',
            due=datetime.now() + timedelta(days=1),
            is_finished=False
        )
        response = self.client.post(f'/api/homeworks/{homework.id}/toggle_finished/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        homework.refresh_from_db()
        self.assertTrue(homework.is_finished)

    def test_todo_api_create(self):
        data = {'title': 'API Todo', 'is_finished': False}
        response = self.client.post('/api/todos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Todo.objects.filter(user=self.user, title='API Todo').exists())

    def test_todo_api_toggle_finished(self):
        todo = Todo.objects.create(user=self.user, title='Test Todo', is_finished=False)
        response = self.client.post(f'/api/todos/{todo.id}/toggle_finished/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        todo.refresh_from_db()
        self.assertTrue(todo.is_finished)

    def test_expense_api_create(self):
        data = {'name': 'API Expense', 'amount': 50.0, 'expense_type': 'Negative'}
        response = self.client.post('/api/expenses/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Expense.objects.filter(user=self.user, name='API Expense').exists())
