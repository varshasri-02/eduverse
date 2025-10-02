
from django import forms
from . models import *
from django.contrib.auth.forms import UserCreationForm


class NotesForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ['title', 'description']

class DateInput(forms.DateInput):
    input_type = 'date'

class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        widgets = {'due':DateInput()}
        fields = ['subject','title','description','due','is_finished']

class DashboardFom(forms.Form):
    text = forms.CharField(max_length=100, label="Enter your Search : ")

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title','is_finished']

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','password1','password2']
class ChatbotForm(forms.Form):
    message = forms.CharField(
        max_length=500,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ask me anything...',
                'autocomplete': 'off'
            }
        ),
        label=''
    )
class StudySessionForm(forms.ModelForm):
    class Meta:
        model = StudySession
        fields = ['subject', 'duration']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Enter subject name'}),
            'duration': forms.NumberInput(attrs={'placeholder': 'Duration in minutes', 'min': 1})
        }

class ShareNoteForm(forms.Form):
    username = forms.CharField(
        max_length=150, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter username to share with'})
    )
    make_public = forms.BooleanField(required=False, label='Make public for all users')
