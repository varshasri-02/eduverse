from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "notes"
        verbose_name_plural = "notes"
class Homework(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    subject = models.CharField(max_length=50, db_index=True)
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField()
    due = models.DateTimeField(db_index=True)
    is_finished=models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Todo(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, db_index=True)
    title = models.CharField(max_length=100, db_index=True)
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return self.title

TYPE = (
    ('Positive', 'Positive'),
    ('Negative', 'Negative')
    )

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    income = models.FloatField(default=0)
    expenses = models.FloatField(default=0)
    amount = models.FloatField(default=0)
    balance = models.FloatField(default=0)

    def __str__(self):
        return str(self.user)


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    amount = models.FloatField(default=0)
    expense_type = models.CharField(max_length=100,choices=TYPE)

    def __str__(self):
        return self.name
    
    
class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"
class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    subject = models.CharField(max_length=100, db_index=True)
    duration = models.IntegerField(help_text="Duration in minutes")
    date = models.DateField(auto_now_add=True, db_index=True)
    start_time = models.DateTimeField(auto_now_add=True, db_index=True)
    end_time = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.subject} - {self.duration}min"


class SharedNote(models.Model):
    note = models.ForeignKey(Notes, on_delete=models.CASCADE, db_index=True)
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_notes', db_index=True)
    shared_with = models.ManyToManyField(User, related_name='received_notes', blank=True)
    is_public = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    def __str__(self):
        return f"{self.note.title} shared by {self.shared_by.username}"
