"""studentstudyportal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.urls.conf import include
from dashboard import views as dash_views
from django.contrib.auth import views as auth_views
from dashboard.health_check import health_check
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

# API Router
router = DefaultRouter()
router.register(r'notes', dash_views.NotesViewSet)
router.register(r'homework', dash_views.HomeworkViewSet)
router.register(r'todos', dash_views.TodoViewSet)
router.register(r'profile', dash_views.ProfileViewSet)
router.register(r'expenses', dash_views.ExpenseViewSet)
router.register(r'chat-history', dash_views.ChatHistoryViewSet)
router.register(r'study-sessions', dash_views.StudySessionViewSet)
router.register(r'shared-notes', dash_views.SharedNoteViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('register/',dash_views.register,name='register'),
    path('login/',auth_views.LoginView.as_view(template_name="dashboard/login.html"),name='login'),
    path('profile/',dash_views.profile,name='profile'),
    path('logout/',auth_views.LogoutView.as_view(template_name="dashboard/logout.html"),name='logout'),
    path('health/', health_check, name='health_check'),

    # API URLs
    path('api/', include(router.urls)),
    path('api/login/', dash_views.api_login, name='api_login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/chatbot/', dash_views.api_chatbot, name='api_chatbot'),
    path('api/progress/', dash_views.api_progress_dashboard, name='api_progress'),

]
