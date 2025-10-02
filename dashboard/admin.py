from django.contrib import admin
from . models import *

# Register your models here.
admin.site.register(Notes)
admin.site.register(Homework)
admin.site.register(Todo)
admin.site.register(Profile)
admin.site.register(Expense)
from .models import ChatHistory

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'timestamp']
    list_filter = ['user', 'timestamp']
    search_fields = ['message', 'response']
