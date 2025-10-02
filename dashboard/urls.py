from django.urls import path
from . import views
urlpatterns = [
    path('', views.home,name="home"),

    path('notes', views.notes,name="notes"),
    path('delete_note/<int:pk>', views.delete_note, name="delete-note"),
    path('notes_detail/<int:pk>', views.NotesDetailView.as_view(), name="notes-detail"),

    path('homework', views.homework,name="homework"),
    path('update_homework/<int:pk>', views.update_homework, name="update-homework"),
    path('delete_homework/<int:pk>', views.delete_homework, name="delete-homework"),

    path('youtube', views.youtube,name="youtube"),

    path('todo', views.todo,name="todo"),
    path('update_todo/<int:pk>', views.update_todo, name="update-todo"),
    path('delete_todo/<int:pk>', views.delete_todo, name="delete-todo"),

    path('books', views.books,name="books"),

    path('dictionary', views.dictionary,name="dictionary"),

    path('wiki', views.wiki,name="wiki"),

    path('expense', views.expense,name="expense"),
  
    path('chatbot/', views.chatbot, name='chatbot'),
    path('chatbot/clear/', views.clear_chat_history, name='clear_chat_history'),
    path('logout/', views.logout_view, name='logout'),
    path('study-timer/', views.study_timer, name='study-timer'),
    path('complete-session/<int:pk>/', views.complete_session, name='complete-session'),
    path('delete-session/<int:pk>/', views.delete_session, name='delete-session'),
    
    # Progress Dashboard
    path('progress/', views.progress_dashboard, name='progress-dashboard'),
    
    # Share Notes URLs
    path('share-note/<int:pk>/', views.share_note, name='share-note'),
    path('shared-notes/', views.shared_notes, name='shared-notes'),
    path("chatbot/api/", views.chatbot_api, name="chatbot_api"), 
    path('note/<int:pk>/download/', views.download_note_pdf, name='download_note_pdf'),


]
