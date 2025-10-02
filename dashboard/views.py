from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from . forms import *
from django.contrib import messages
from django.views import generic
import requests
import wikipedia
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseRedirect
import random
import yt_dlp
import google.generativeai as genai
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Q



# Create your views here.

def home(request):
    return render(request, 'dashboard/home.html')

# Method to open notes feature and create new notes
@login_required
def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(
                user=request.user, title=request.POST['title'], description=request.POST['description'])
            notes.save()
            messages.success(request, f"Notes Added from {request.user.username} successfully!")
            return redirect("notes")
    else:
        form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context = {'notes': notes, 'form': form}
    return render(request, 'dashboard/notes.html', context)

# Method to delete an existing note
@login_required
def delete_note(request, pk=None):
    Notes.objects.get(id=pk).delete()
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
                            if video:
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
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            homeworks = Homework(
                user=request.user,
                subject=request.POST['subject'],
                title=request.POST['title'],
                description=request.POST['description'],
                due=request.POST['due'],
                is_finished=finished
            )
            homeworks.save()
            messages.success(request, f'Homework Added from {request.user.username}!!')
            return redirect("homework")
    else:
        form = HomeworkForm()
    homework = Homework.objects.filter(user=request.user).order_by("due")
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    context = {
        'homeworks': homework,
        'homeworks_done': homework_done,
        'form': form,
    }
    return render(request, 'dashboard/homework.html', context)

# Method to update the completion status of a homework
@login_required
def update_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect("homework")

# Method to delete an existing homework
@login_required
def delete_homework(request, pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")

# Method to create a todo list using todo feature
@login_required
def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST["is_finished"]
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = Todo(
                user=request.user,
                title=request.POST['title'],
                is_finished=finished
            )
            todos.save()
            messages.success(request, f"Todo Added from {request.user.username}!!")
            return redirect("todo")
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user=request.user)
    # Check if there are any todos and if all are finished
    if len(todo) == 0:
        todos_done = True  # No todos exist
    else:
        # Check if all existing todos are finished
        incomplete_todos = todo.filter(is_finished=False).count()
        if incomplete_todos > 0:
            todos_done = False  # There are incomplete todos, show the table
        else:
            todos_done = True  # All todos are completed
    context = {
        'form': form,
        'todos': todo,
        'todos_done': todos_done
    }
    return render(request, "dashboard/todo.html", context)

# Method to update completion status of an existing todo
@login_required
def update_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect("todo")

# Method to delete an existing todo
@login_required
def delete_todo(request, pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect("todo")

# Method to find for the ebook stack based using the keyword searched
def books(request):
    if request.method == "POST":
        form = DashboardFom(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10):
            result_dict = {
                'title': answer['items'][i]['volumeInfo']['title'],
                'subtitle': answer['items'][i]['volumeInfo'].get('subtitle'),
                'description': answer['items'][i]['volumeInfo'].get('description'),
                'count': answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories': answer['items'][i]['volumeInfo'].get('categories'),
                'rating': answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail': answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview': answer['items'][i]['volumeInfo'].get('previewLink'),
            }
            result_list.append(result_dict)
            context = {
                'form': form,
                'results': result_list
            }
        return render(request, 'dashboard/books.html', context)
    else:
        form = DashboardFom()
    context = {'form': form}
    return render(request, 'dashboard/books.html', context)

# Method to perform the dictionary function
def dictionary(request):
    if request.method == "POST":
        form = DashboardFom(request.POST)
        text = request.POST['text']
        # API used is dictionaryapi
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
            }
        except:
            context = {
                'form': form,
                'input': ''
            }
        return render(request, 'dashboard/dictionary.html', context)
    else:
        form = DashboardFom()
        context = {'form': form}
    return render(request, 'dashboard/dictionary.html', context)

import random
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

# Method to perform the WikiPedia search
def wiki(request):
    if request.method == 'POST':
        text = request.POST['text']
        form = DashboardFom()
        try:
            search = wikipedia.page(text)
        except DisambiguationError as e:
            text = random.choice(e.options)
            search = wikipedia.page(text)
        except PageError:
            context = {
                'form': form,
                'error': f"No Wikipedia page found for '{text}'. Try another search."
            }
            return render(request, "dashboard/wiki.html", context)

        context = {
            'form': form,
            'title': search.title,
            'link': search.url,
            'details': search.summary
        }
        return render(request, "dashboard/wiki.html", context)

    else:
        form = DashboardFom()
        context = {
            'form': form
        }
    return render(request, 'dashboard/wiki.html', context)


# Method to manage the expenses and to create and maintain an e-wallet(Profile class is referring to that!)
@login_required
def expense(request):
    profiles = Profile.objects.filter(user=request.user).first()
    expenses = Expense.objects.filter(user=request.user)
    profile = Profile(user=request.user)
    profile.save()

    if request.method == "POST":
        text = request.POST.get('text')
        amount = request.POST.get('amount')
        expense_type = request.POST.get('expense_type')
        expense = Expense(name=text, amount=amount, expense_type=expense_type, user=request.user)
        expense.save()

        # Updating the wallet status after recieving every transaction history
        if expense_type == 'Positive':
            profiles.balance += float(amount)
            profiles.income += float(amount)
        else:
            profiles.expenses += float(amount)
            profiles.balance -= float(amount)
        profiles.save()
        return redirect("expense")
    context = {
        'profiles': profiles,
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
    context = {
        'form': form
    }
    return render(request, 'dashboard/register.html', context)

# Method for profile section (which keeps track of pending Homework and Todos)
@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)
    # If there are incomplete homeworks, homework_done should be False
    if len(homeworks) == 0:
        homework_done = True  # No incomplete homeworks
    else:
        homework_done = False  # There are incomplete homeworks
    # If there are incomplete todos, todos_done should be False
    if len(todos) == 0:
        todos_done = True  # No incomplete todos
    else:
        todos_done = False  # There are incomplete todos
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
from django.http import JsonResponse

@login_required
def chatbot_api(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        user_message = data.get("message", "")

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
            return JsonResponse({"error": str(e)}, status=500)


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
    
    sessions = StudySession.objects.filter(user=request.user)[:10]
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
    session = StudySession.objects.get(id=pk, user=request.user)
    session.completed = True
    session.end_time = timezone.now()
    session.save()
    messages.success(request, f"Great job! You studied {session.subject} for {session.duration} minutes!")
    return redirect('study-timer')

@login_required
def delete_session(request, pk):
    StudySession.objects.get(id=pk, user=request.user).delete()
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
    recent_sessions = StudySession.objects.filter(user=user)[:5]
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
    note = Notes.objects.get(id=pk, user=request.user)
    
    if request.method == "POST":
        form = ShareNoteForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            make_public = form.cleaned_data['make_public']
            
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
                    shared_note.shared_with.add(share_with_user)
                    messages.success(request, f"Note shared with {username}!")
                except User.DoesNotExist:
                    messages.error(request, f"User {username} not found!")
            
            return redirect('notes')
    else:
        form = ShareNoteForm()
    
    context = {'form': form, 'note': note}
    return render(request, 'dashboard/share_note.html', context)

@login_required
def shared_notes(request):
    # Only notes that exist
    shared_with_me = SharedNote.objects.filter(
        Q(shared_with=request.user) | Q(is_public=True)
    ).exclude(shared_by=request.user).exclude(note__isnull=True)

    my_shared_notes = SharedNote.objects.filter(shared_by=request.user).exclude(note__isnull=True)

    context = {
        'shared_with_me': shared_with_me,
        'my_shared_notes': my_shared_notes
    }
    return render(request, 'dashboard/shared_notes.html', context)

from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from django.shortcuts import get_object_or_404

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

    # PDF generation logic here
    from io import BytesIO
    from django.http import HttpResponse
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, note.title)
    p.drawString(100, 780, note.description)
    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
