from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from . forms import *
from django.contrib import messages
from django.views import generic
import requests
import wikipedia
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import random
import yt_dlp
import google.generativeai as genai
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Q
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache, cache_page
from django.core.mail import send_mail
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from wikipedia.exceptions import DisambiguationError, PageError
import sys
import json

# REST Framework imports
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import UserRateThrottle
from .serializers import *
# Helper function to create model instances using serializers
def create_from_serializer(serializer_class, data, user):
    """
    Helper function to create model instances using DRF serializers.
    Returns (instance, errors) tuple. If successful, instance is created and errors is None.
    If validation fails, instance is None and errors contains validation errors.
    """
    serializer = serializer_class(data=data)
    if serializer.is_valid():
        instance = serializer.save(user=user)
        return instance, None
    else:
        return None, serializer.errors

# Helper function to update model instances using DRF serializers
def update_from_serializer(serializer_class, instance, data):
    """
    Helper function to update model instances using DRF serializers.
    Returns (success, errors) tuple. If successful, success is True and errors is None.
    If validation fails, success is False and errors contains validation errors.
    """
    serializer = serializer_class(instance, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return True, None
    else:
        return False, serializer.errors



# Create your views here.

def home(request):
    return render(request, 'dashboard/home.html')


# Method to open notes feature and create new notes
@login_required
def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            data = {
                'title': request.POST['title'],
                'description': request.POST['description']
            }
            instance, errors = create_from_serializer(NotesSerializer, data, request.user)
            if instance:
                messages.success(request, f"Notes Added from {request.user.username} successfully!")
                return redirect("notes")
            else:
                for field, error_list in errors.items():
                    for error in error_list:
                        messages.error(request, f"{field}: {error}")
    else:
        form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context = {'notes': notes, 'form': form}
    return render(request, 'dashboard/notes.html', context)


# Method to delete an existing note
@login_required
def delete_note(request, pk=None):
    note = get_object_or_404(Notes, id=pk, user=request.user)
    note.delete()
    messages.success(request, "Note deleted successfully!")
    return redirect("notes")


# class to have detailed view of a individual note
class NotesDetailView(generic.DetailView):
    model = Notes


# Method to open Youtube feature and to provide the response according to the search text
def youtube(request):
    if request.method == "POST":
        form = DashboardFom(request.POST)
        text = request.POST.get('text')
        result_list = []

        if text:
            # Add educational keywords to filter results
            educational_keywords = [
                'tutorial', 'lecture', 'lesson', 'course', 'education',
                'learning', 'study', 'explained', 'guide', 'academic'
            ]
            # Enhance search query with educational filters
            enhanced_text = f"{text} tutorial OR lecture OR lesson"
            
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True,
                    'skip_download': True,
                    'no_color': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    search_results = ydl.extract_info(f"ytsearch15:{enhanced_text}", download=False)
                    
                    if search_results and 'entries' in search_results:
                        # Filter for educational content
                        for video in search_results['entries']:
                            if video and video.get('id'):
                                title = video.get('title', '').lower()
                                description = (video.get('description', '') or '').lower()
                                channel = (video.get('channel', '') or video.get('uploader', '')).lower()
                                
                                # Check if video seems educational
                                is_educational = any(keyword in title or keyword in description or keyword in channel 
                                                   for keyword in educational_keywords)
                                
                                # Skip entertainment/gaming/music videos
                                non_educational = ['music video', 'song', 'gameplay', 'gaming', 
                                                 'vlog', 'comedy', 'funny', 'prank']
                                is_non_educational = any(keyword in title for keyword in non_educational)
                                
                                if is_educational or not is_non_educational:
                                    # Format duration
                                    duration = video.get('duration', 0)
                                    if duration:
                                        duration = int(duration)
                                        mins = duration // 60
                                        secs = duration % 60
                                        duration_str = f"{mins}:{secs:02d}"
                                    else:
                                        duration_str = "N/A"
                                    
                                    # Format views
                                    views = video.get('view_count')
                                    if views:
                                        if views >= 1000000:
                                            views_str = f"{views/1000000:.1f}M"
                                        elif views >= 1000:
                                            views_str = f"{views/1000:.1f}K"
                                        else:
                                            views_str = str(views)
                                    else:
                                        views_str = "N/A"
                                    
                                    # Format published date
                                    upload_date = video.get('upload_date', '')
                                    if upload_date and len(upload_date) == 8:
                                        published = f"{upload_date[6:8]}/{upload_date[4:6]}/{upload_date[0:4]}"
                                    else:
                                        published = "N/A"
                                    
                                    # Get the best thumbnail
                                    video_id = video.get('id', '')
                                    thumbnail = video.get('thumbnail', '')
                                    
                                    if not thumbnail or 'googleusercontent.com' in thumbnail:
                                        thumbnail = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                                    
                                    result_dict = {
                                        'input': text,
                                        'title': video.get('title', 'No Title'),
                                        'duration': duration_str,
                                        'thumbnail': thumbnail,
                                        'channel': video.get('channel', '') or video.get('uploader', 'Unknown'),
                                        'link': f"https://www.youtube.com/watch?v={video_id}",
                                        'views': views_str,
                                        'published': published,
                                        'description': (video.get('description', '') or '')[:200]
                                    }
                                    result_list.append(result_dict)
                                    
                                    # Limit to 10 educational videos
                                    if len(result_list) >= 10:
                                        break
                        
            except Exception as e:
                print("Error while fetching videos:", e)
                import traceback
                traceback.print_exc()
                messages.error(request, "Error fetching videos. Please try again.")

        context = {
            'form': form,
            'results': result_list
        }
        return render(request, 'dashboard/youtube.html', context)

    else:
        form = DashboardFom()

    context = {'form': form}
    return render(request, 'dashboard/youtube.html', context)


# Method to open Homework feature and create a new homework along with assigning a date of completion to it
@login_required
def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST.get('is_finished', 'off')
                finished = True if finished == 'on' else False
            except:
                finished = False

            data = {
                'subject': request.POST['subject'],
                'title': request.POST['title'],
                'description': request.POST['description'],
                'due': request.POST['due'],
                'is_finished': finished
            }
            instance, errors = create_from_serializer(HomeworkSerializer, data, request.user)
            if instance:
                messages.success(request, f'Homework Added from {request.user.username}!!')
                return redirect("homework")
            else:
                for field, error_list in errors.items():
                    for error in error_list:
                        messages.error(request, f"{field}: {error}")
    else:
        form = HomeworkForm()

    homework = Homework.objects.filter(user=request.user).order_by("due")
    homework_done = len(homework) == 0

    context = {
        'homeworks': homework,
        'homeworks_done': homework_done,
        'form': form,
    }
    return render(request, 'dashboard/homework.html', context)


# Method to update the completion status of a homework
@login_required
def update_homework(request, pk=None):
    homework = get_object_or_404(Homework, id=pk, user=request.user)
    success, errors = update_from_serializer(HomeworkSerializer, homework, {'is_finished': not homework.is_finished})
    if success:
        messages.success(request, f"Homework status updated!")
    else:
        messages.error(request, "Error updating homework status")
    return redirect("homework")


# Method to delete an existing homework
@login_required
def delete_homework(request, pk=None):
    homework = get_object_or_404(Homework, id=pk, user=request.user)
    homework.delete()
    messages.success(request, "Homework deleted successfully!")
    return redirect("homework")


# Method to create a todo list using todo feature
@login_required
def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST.get("is_finished", 'off')
                finished = True if finished == 'on' else False
            except:
                finished = False

            data = {
                'title': request.POST['title'],
                'is_finished': finished
            }
            instance, errors = create_from_serializer(TodoSerializer, data, request.user)
            if instance:
                messages.success(request, f"Todo Added from {request.user.username}!!")
                return redirect("todo")
            else:
                for field, error_list in errors.items():
                    for error in error_list:
                        messages.error(request, f"{field}: {error}")
    else:
        form = TodoForm()

    todo = Todo.objects.filter(user=request.user)

    # Check if there are any todos and if all are finished
    if len(todo) == 0:
        todos_done = True  # No todos exist
    else:
        # Check if all existing todos are finished
        incomplete_todos = todo.filter(is_finished=False).count()
        todos_done = incomplete_todos == 0

    context = {
        'form': form,
        'todos': todo,
        'todos_done': todos_done
    }
    return render(request, "dashboard/todo.html", context)


# Method to update completion status of an existing todo
@login_required
def update_todo(request, pk=None):
    todo = get_object_or_404(Todo, id=pk, user=request.user)
    success, errors = update_from_serializer(TodoSerializer, todo, {'is_finished': not todo.is_finished})
    if success:
        messages.success(request, "Todo status updated!")
    else:
        messages.error(request, "Error updating todo status")
    return redirect("todo")


# Method to delete an existing todo
@login_required
def delete_todo(request, pk=None):
    todo = get_object_or_404(Todo, id=pk, user=request.user)
    todo.delete()
    messages.success(request, "Todo deleted successfully!")
    return redirect("todo")


# Method to find for the ebook stack based using the keyword searched
def books(request):
    if request.method == "POST":
        form = DashboardFom(request.POST)
        text = request.POST.get('text', '')
        
        if not text:
            messages.error(request, "Please enter a search term")
            return render(request, 'dashboard/books.html', {'form': form})
        
        url = "https://www.googleapis.com/books/v1/volumes?q=" + text
        
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            answer = r.json()
            result_list = []
            
            if 'items' in answer:
                # Get up to 10 results, or however many are available
                for i in range(min(10, len(answer['items']))):
                    try:
                        item = answer['items'][i]
                        volume_info = item.get('volumeInfo', {})
                        
                        # Safely get thumbnail
                        thumbnail = None
                        image_links = volume_info.get('imageLinks')
                        if image_links:
                            thumbnail = image_links.get('thumbnail') or image_links.get('smallThumbnail')
                        
                        result_dict = {
                            'title': volume_info.get('title', 'No Title'),
                            'subtitle': volume_info.get('subtitle'),
                            'description': volume_info.get('description'),
                            'count': volume_info.get('pageCount'),
                            'categories': volume_info.get('categories'),
                            'rating': volume_info.get('averageRating'),
                            'thumbnail': thumbnail,
                            'preview': volume_info.get('previewLink'),
                        }
                        result_list.append(result_dict)
                    except Exception as e:
                        print(f"Error processing book {i}: {e}")
                        continue
                
                if not result_list:
                    messages.warning(request, "No books found for your search")
            else:
                messages.warning(request, "No books found for your search")
            
            context = {
                'form': form,
                'results': result_list
            }
            return render(request, 'dashboard/books.html', context)
            
        except requests.RequestException as e:
            print(f"Books API Error: {e}")
            messages.error(request, "Error connecting to books API. Please try again.")
            context = {'form': form}
            return render(request, 'dashboard/books.html', context)
    else:
        form = DashboardFom()
    
    context = {'form': form}
    return render(request, 'dashboard/books.html', context)


# Method to perform the dictionary function
def dictionary(request):
    if request.method == "POST":
        form = DashboardFom(request.POST)
        text = request.POST.get('text', '').strip()
        
        if not text:
            messages.error(request, "Please enter a word")
            return render(request, 'dashboard/dictionary.html', {'form': form})
        
        # API used is dictionaryapi
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{text}"
        
        try:
            r = requests.get(url, timeout=10)
            
            if r.status_code == 200:
                answer = r.json()
                try:
                    phonetics = answer[0].get('phonetics', [{}])[0].get('text', 'N/A')
                    audio = answer[0].get('phonetics', [{}])[0].get('audio', '')
                    definition = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('definition', 'No definition found')
                    
                    context = {
                        'form': form,
                        'input': text,
                        'phonetics': phonetics,
                        'audio': audio,
                        'definition': definition,
                    }
                except (IndexError, KeyError, TypeError) as e:
                    print(f"Dictionary parsing error: {e}")
                    context = {
                        'form': form,
                        'input': text,
                        'error': 'Could not parse dictionary data'
                    }
            else:
                context = {
                    'form': form,
                    'input': text,
                    'error': f"Word '{text}' not found in dictionary"
                }
        except requests.RequestException as e:
            print(f"Dictionary API Error: {e}")
            context = {
                'form': form,
                'input': '',
                'error': 'Error connecting to dictionary API'
            }
        
        return render(request, 'dashboard/dictionary.html', context)
    else:
        form = DashboardFom()
        context = {'form': form}
    
    return render(request, 'dashboard/dictionary.html', context)


# Method to perform the WikiPedia search
def wiki(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        form = DashboardFom()
        
        if not text:
            messages.error(request, "Please enter a search term")
            return render(request, "dashboard/wiki.html", {'form': form})
        
        try:
            search = wikipedia.page(text)
            context = {
                'form': form,
                'title': search.title,
                'link': search.url,
                'details': search.summary
            }
            return render(request, "dashboard/wiki.html", context)
            
        except DisambiguationError as e:
            # Try a random option from disambiguation
            try:
                text = random.choice(e.options)
                search = wikipedia.page(text)
                context = {
                    'form': form,
                    'title': search.title,
                    'link': search.url,
                    'details': search.summary
                }
                return render(request, "dashboard/wiki.html", context)
            except:
                context = {
                    'form': form,
                    'error': f"Multiple results found. Try being more specific. Options: {', '.join(e.options[:5])}"
                }
                return render(request, "dashboard/wiki.html", context)
                
        except PageError:
            context = {
                'form': form,
                'error': f"No Wikipedia page found for '{text}'. Try another search."
            }
            return render(request, "dashboard/wiki.html", context)
        except Exception as e:
            print(f"Wikipedia error: {e}")
            context = {
                'form': form,
                'error': "An error occurred. Please try again."
            }
            return render(request, "dashboard/wiki.html", context)
    else:
        form = DashboardFom()
        context = {'form': form}
    
    return render(request, 'dashboard/wiki.html', context)


# Method to manage the expenses and to create and maintain an e-wallet
@login_required
def expense(request):
    # Get or create profile for the user
    profile, created = Profile.objects.get_or_create(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    if request.method == "POST":
        text = request.POST.get('text', '').strip()
        amount = request.POST.get('amount', '').strip()
        expense_type = request.POST.get('expense_type', '')

        if not text or not amount or not expense_type:
            messages.error(request, "Please fill all fields")
            return redirect("expense")

        try:
            amount_float = float(amount)
            if amount_float <= 0:
                messages.error(request, "Amount must be greater than 0")
                return redirect("expense")
        except ValueError:
            messages.error(request, "Invalid amount")
            return redirect("expense")

        data = {
            'name': text,
            'amount': amount_float,
            'expense_type': expense_type
        }
        instance, errors = create_from_serializer(ExpenseSerializer, data, request.user)
        if instance:
            # Updating the wallet status after receiving every transaction history
            if expense_type == 'Positive':
                profile.balance += amount_float
                profile.income += amount_float
            else:
                profile.expenses += amount_float
                profile.balance -= amount_float

            profile.save()
            messages.success(request, f"Expense added successfully!")
            return redirect("expense")
        else:
            for field, error_list in errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error}")

    context = {
        'profile': profile,
        'expenses': expenses
    }
    return render(request, 'dashboard/expense.html', context)


# Method to perform new user registration
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account Created for {username}!!")
            return redirect("login")
    else:
        form = UserRegistrationForm()
    
    context = {'form': form}
    return render(request, 'dashboard/register.html', context)


# Method for profile section (which keeps track of pending Homework and Todos)
@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)
    
    # If there are incomplete homeworks, homework_done should be False
    homework_done = len(homeworks) == 0
    
    # If there are incomplete todos, todos_done should be False
    todos_done = len(todos) == 0
    
    context = {
        'homeworks': homeworks,
        'todos': todos,
        'homework_done': homework_done,
        'todos_done': todos_done
    }
    return render(request, "dashboard/profile.html", context)


@login_required
def chatbot(request):
    chat_history = ChatHistory.objects.filter(user=request.user).order_by('-timestamp')[:10]
    
    if request.method == "POST":
        form = ChatbotForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data['message']
            
            if not user_message.strip():
                messages.error(request, "Please enter a message")
                return redirect('chatbot')
            
            try:
                # Configure Google Gemini
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                
                # Initialize the model with the updated model name
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                # Create the prompt with system instructions
                prompt = f"""You are a helpful study assistant for students. Provide clear, educational answers.

Student Question: {user_message}

Please provide a helpful and educational response:"""
                
                # Generate response
                response = model.generate_content(prompt)
                bot_response = response.text
                
                # Save to database
                ChatHistory.objects.create(
                    user=request.user,
                    message=user_message,
                    response=bot_response
                )
                
                messages.success(request, "Response received!")
                return redirect('chatbot')
                
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
                print(f"Chatbot Error: {e}")
                import traceback
                traceback.print_exc()
    else:
        form = ChatbotForm()
    
    context = {
        'form': form,
        'chat_history': chat_history
    }
    return render(request, 'dashboard/chatbot.html', context)


@login_required
def clear_chat_history(request):
    ChatHistory.objects.filter(user=request.user).delete()
    messages.success(request, "Chat history cleared!")
    return redirect('chatbot')


@login_required
def chatbot_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"error": "Message cannot be empty"}, status=400)

            try:
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')

                prompt = f"You are a helpful study assistant.\n\nStudent Question: {user_message}\n\nAnswer clearly:"
                response = model.generate_content(prompt)
                bot_response = response.text

                ChatHistory.objects.create(
                    user=request.user,
                    message=user_message,
                    response=bot_response
                )

                return JsonResponse({
                    "user": user_message,
                    "bot": bot_response
                })

            except Exception as e:
                print(f"Gemini API Error: {e}")
                return JsonResponse({"error": "AI service error"}, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)


# Method to logout user
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('login')


# Study Timer View
@login_required
def study_timer(request):
    if request.method == "POST":
        form = StudySessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = request.user
            session.save()
            messages.success(request, "Study session started!")
            return redirect('study-timer')
    else:
        form = StudySessionForm()
    
    sessions = StudySession.objects.filter(user=request.user).order_by('-date', '-start_time')[:10]
    today = timezone.now().date()
    today_sessions = StudySession.objects.filter(
        user=request.user, 
        date=today,
        completed=True
    )
    total_today = today_sessions.aggregate(Sum('duration'))['duration__sum'] or 0
    
    context = {
        'form': form,
        'sessions': sessions,
        'total_today': total_today
    }
    return render(request, 'dashboard/study_timer.html', context)


@login_required
def complete_session(request, pk):
    session = get_object_or_404(StudySession, id=pk, user=request.user)
    session.completed = True
    session.end_time = timezone.now()
    session.save()
    messages.success(request, f"Great job! You studied {session.subject} for {session.duration} minutes!")
    return redirect('study-timer')


@login_required
def delete_session(request, pk):
    session = get_object_or_404(StudySession, id=pk, user=request.user)
    session.delete()
    messages.success(request, "Session deleted!")
    return redirect('study-timer')


@login_required
def progress_dashboard(request):
    user = request.user
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    total_study_time = StudySession.objects.filter(
        user=user, completed=True
    ).aggregate(Sum('duration'))['duration__sum'] or 0
    
    week_study_time = StudySession.objects.filter(
        user=user, completed=True, date__gte=week_ago
    ).aggregate(Sum('duration'))['duration__sum'] or 0
    
    total_homework = Homework.objects.filter(user=user).count()
    completed_homework = Homework.objects.filter(user=user, is_finished=True).count()
    pending_homework = total_homework - completed_homework
    
    total_todos = Todo.objects.filter(user=user).count()
    completed_todos = Todo.objects.filter(user=user, is_finished=True).count()
    pending_todos = total_todos - completed_todos
    
    total_notes = Notes.objects.filter(user=user).count()
    recent_sessions = StudySession.objects.filter(user=user).order_by('-date', '-start_time')[:5]
    recent_homeworks = Homework.objects.filter(user=user).order_by('-due')[:5]
    
    study_by_subject = StudySession.objects.filter(
        user=user, completed=True
    ).values('subject').annotate(
        total_time=Sum('duration')
    ).order_by('-total_time')[:5]
    
    homework_completion_rate = (completed_homework / total_homework * 100) if total_homework > 0 else 0
    todo_completion_rate = (completed_todos / total_todos * 100) if total_todos > 0 else 0
    
    context = {
        'total_study_time': total_study_time,
        'week_study_time': week_study_time,
        'total_homework': total_homework,
        'completed_homework': completed_homework,
        'pending_homework': pending_homework,
        'total_todos': total_todos,
        'completed_todos': completed_todos,
        'pending_todos': pending_todos,
        'total_notes': total_notes,
        'recent_sessions': recent_sessions,
        'recent_homeworks': recent_homeworks,
        'study_by_subject': study_by_subject,
        'homework_completion_rate': round(homework_completion_rate, 1),
        'todo_completion_rate': round(todo_completion_rate, 1),
    }
    return render(request, 'dashboard/progress_dashboard.html', context)


@login_required
def share_note(request, pk):
    note = get_object_or_404(Notes, id=pk, user=request.user)
    
    if request.method == "POST":
        form = ShareNoteForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username', '').strip()
            make_public = form.cleaned_data.get('make_public', False)
            
            shared_note, created = SharedNote.objects.get_or_create(
                note=note,
                shared_by=request.user
            )
            
            if make_public:
                shared_note.is_public = True
                shared_note.save()
                messages.success(request, "Note made public for all users!")
            elif username:
                try:
                    share_with_user = User.objects.get(username=username)
                    if share_with_user == request.user:
                        messages.warning(request, "You cannot share a note with yourself!")
                    else:
                        shared_note.shared_with.add(share_with_user)
                        messages.success(request, f"Note shared with {username}!")
                except User.DoesNotExist:
                    messages.error(request, f"User {username} not found!")
            else:
                messages.warning(request, "Please enter a username or check 'Make Public'")
            
            return redirect('notes')
    else:
        form = ShareNoteForm()
    
    context = {'form': form, 'note': note}
    return render(request, 'dashboard/share_note.html', context)


@login_required
def shared_notes(request):
    # Notes shared with me or public (excluding my own notes)
    shared_with_me = SharedNote.objects.filter(
        Q(shared_with=request.user) | Q(is_public=True)
    ).exclude(
        shared_by=request.user
    ).select_related('note', 'shared_by').filter(
        note__isnull=False
    )

    # Notes I've shared with others
    my_shared_notes = SharedNote.objects.filter(
        shared_by=request.user
    ).select_related('note').filter(
        note__isnull=False
    )

    context = {
        'shared_with_me': shared_with_me,
        'my_shared_notes': my_shared_notes
    }
    return render(request, 'dashboard/shared_notes.html', context)


@login_required
def download_note_pdf(request, pk):
    # Fetch note owned by user OR shared with user OR public
    note = get_object_or_404(
        Notes.objects.filter(
            Q(user=request.user) | 
            Q(sharednote__shared_with=request.user) | 
            Q(sharednote__is_public=True)
        ).distinct(), 
        id=pk
    )

    # Create PDF using ReportLab
    buffer = BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Add title
    title_style = styles['Heading1']
    story.append(Paragraph(note.title, title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Add description/content
    body_style = styles['BodyText']
    # Split description into paragraphs
    paragraphs = note.description.split('\n')
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para, body_style))
            story.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF value
    buffer.seek(0)
    
    # Create response
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{note.title}.pdf"'
    return response


# ==================== REST API VIEWS ====================

@api_view(['POST'])
def api_login(request):
    """API endpoint for user login with JWT tokens"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

    from django.contrib.auth import authenticate
    user = authenticate(username=username, password=password)

    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class NotesViewSet(viewsets.ModelViewSet):
    serializer_class = NotesSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    queryset = Notes.objects.all()

    def get_queryset(self):
        return Notes.objects.filter(user=self.request.user).select_related('user')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HomeworkViewSet(viewsets.ModelViewSet):
    serializer_class = HomeworkSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    queryset = Homework.objects.all()

    def get_queryset(self):
        return Homework.objects.filter(user=self.request.user).select_related('user').order_by('due')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_finished(self, request, pk=None):
        homework = self.get_object()
        homework.is_finished = not homework.is_finished
        homework.save()
        return Response({'status': 'updated', 'is_finished': homework.is_finished})


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    queryset = Todo.objects.all()

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user).select_related('user')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_finished(self, request, pk=None):
        todo = self.get_object()
        todo.is_finished = not todo.is_finished
        todo.save()
        return Response({'status': 'updated', 'is_finished': todo.is_finished})


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    queryset = Profile.objects.all()

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user).select_related('user')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    queryset = Expense.objects.all()

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user).select_related('user')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChatHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = ChatHistorySerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    queryset = ChatHistory.objects.all()

    def get_queryset(self):
        return ChatHistory.objects.filter(user=self.request.user).select_related('user').order_by('-timestamp')[:50]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudySessionViewSet(viewsets.ModelViewSet):
    serializer_class = StudySessionSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    queryset = StudySession.objects.all()

    def get_queryset(self):
        return StudySession.objects.filter(user=self.request.user).select_related('user').order_by('-start_time')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        session = self.get_object()
        session.completed = True
        session.end_time = timezone.now()
        session.save()
        return Response({'status': 'completed'})


class SharedNoteViewSet(viewsets.ModelViewSet):
    serializer_class = SharedNoteSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    queryset = SharedNote.objects.all()

    def get_queryset(self):
        return SharedNote.objects.filter(
            Q(shared_with=self.request.user) | Q(is_public=True)
        ).exclude(shared_by=self.request.user).select_related('note', 'shared_by')

    def perform_create(self, serializer):
        serializer.save(shared_by=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_chatbot(request):
    """Optimized chatbot API with per-user caching"""
    from django.core.cache import cache

    user_message = request.data.get('message', '').strip()

    if not user_message:
        return Response({'error': 'Message required'}, status=status.HTTP_400_BAD_REQUEST)

    # Create per-user cache key
    cache_key = f"chatbot_response_{request.user.id}_{hash(user_message)}"

    # Check cache first
    cached_response = cache.get(cache_key)
    if cached_response:
        return Response(cached_response)

    try:
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        prompt = f"You are a helpful study assistant.\n\nStudent Question: {user_message}\n\nAnswer clearly:"
        response_obj = model.generate_content(prompt)
        bot_response = response_obj.text

        # Save to database
        ChatHistory.objects.create(
            user=request.user,
            message=user_message,
            response=bot_response
        )

        response_data = {
            'user_message': user_message,
            'bot_response': bot_response
        }

        # Cache the response for 5 minutes per user
        cache.set(cache_key, response_data, 300)

        return Response(response_data)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_progress_dashboard(request):
    """Optimized progress dashboard API with per-user caching"""
    from django.core.cache import cache

    user = request.user
    cache_key = f"progress_dashboard_{user.id}"

    # Check cache first
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    # Use aggregation for better performance
    study_stats = StudySession.objects.filter(user=user, completed=True).aggregate(
        total_time=Sum('duration'),
        week_time=Sum('duration', filter=Q(date__gte=week_ago))
    )

    homework_stats = Homework.objects.filter(user=user).aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(is_finished=True))
    )

    todo_stats = Todo.objects.filter(user=user).aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(is_finished=True))
    )

    notes_count = Notes.objects.filter(user=user).count()

    response_data = {
        'study_sessions': {
            'total_time': study_stats['total_time'] or 0,
            'week_time': study_stats['week_time'] or 0,
        },
        'homework': {
            'total': homework_stats['total'],
            'completed': homework_stats['completed'],
            'pending': homework_stats['total'] - homework_stats['completed'],
            'completion_rate': round((homework_stats['completed'] / homework_stats['total'] * 100) if homework_stats['total'] > 0 else 0, 1)
        },
        'todos': {
            'total': todo_stats['total'],
            'completed': todo_stats['completed'],
            'pending': todo_stats['total'] - todo_stats['completed'],
            'completion_rate': round((todo_stats['completed'] / todo_stats['total'] * 100) if todo_stats['total'] > 0 else 0, 1)
        },
        'notes': {
            'total': notes_count
        }
    }

    # Cache for 10 minutes per user
    cache.set(cache_key, response_data, 600)

    return Response(response_data)



