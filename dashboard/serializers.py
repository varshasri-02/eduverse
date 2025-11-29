from rest_framework import serializers
from .models import Notes, Homework, Todo, Profile, Expense, ChatHistory, StudySession, SharedNote
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class NotesSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Notes
        fields = ['id', 'user', 'title', 'description']
        read_only_fields = ['user']


class HomeworkSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Homework
        fields = ['id', 'user', 'subject', 'title', 'description', 'due', 'is_finished']
        read_only_fields = ['user']


class TodoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Todo
        fields = ['id', 'user', 'title', 'is_finished']
        read_only_fields = ['user']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'income', 'expenses', 'amount', 'balance']
        read_only_fields = ['user']


class ExpenseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'user', 'name', 'amount', 'expense_type']
        read_only_fields = ['user']


class ChatHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ChatHistory
        fields = ['id', 'user', 'message', 'response', 'timestamp']
        read_only_fields = ['user', 'timestamp']


class StudySessionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = StudySession
        fields = ['id', 'user', 'subject', 'duration', 'date', 'start_time', 'end_time', 'completed']
        read_only_fields = ['user', 'date', 'start_time']


class SharedNoteSerializer(serializers.ModelSerializer):
    note = NotesSerializer(read_only=True)
    shared_by = UserSerializer(read_only=True)
    shared_with = UserSerializer(many=True, read_only=True)

    class Meta:
        model = SharedNote
        fields = ['id', 'note', 'shared_by', 'shared_with', 'is_public', 'created_at']
        read_only_fields = ['shared_by', 'created_at']