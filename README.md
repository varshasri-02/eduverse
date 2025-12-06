# Eduverse   

<h3>Build a functional prototype of a platform that gives students an array of digital academic and social tools to stay engaged with their studies, peers and broader university community.</h3>

<h3> StudentStudyPortal is a portal with following features in its dashboard to make student's life easy and more manageable.</h3> 
    <ol>
        <li>Notes : Users can create text notes and refer them later, they are stored permanently until deleted.</li>
        <li>Shared Notes : Users can share notes with other students, view shared notes, and download them.</li>
        <li>Homework: Users can add homeworks and assign them deadlines, they will be displayed prioritised by deadlines.</li>
        <li>Youtube Search: Users can perform Youtube search and select desired video to play it on youtube.</li>
        <li>To Do: Users can add to-do lists for their day and remove them as the work is finished.</li>
        <li>Books: Users can browse books from a list of neatly organised book menu.</li>
        <li>Dictionary: Users can enter a word, and the meaning will be displayed along with its phonetic description instantaneously.</li>
        <li>Wikipedia: Users can search wikipedia to get fast results.</li>
        <li>Expense Tracker: A virtual wallet is implemented to help the users to manage their expenses and keep track of it.</li>
        <li>AI Study Assistant: An AI-powered chatbot to clarify doubts, answer academic questions, and guide students.</li>
        <li>Study Timer: A timer to help students manage study sessions and breaks effectively.</li>
        <li>Progress Monitoring: A dashboard view of study progress and academic productivity.</li>
        <li>Profile : This will display all the pending todos and homeworks to the users.</li>
    </ol>
    
<h2>Technologies Used:</h2>
<ul>
    <li>Python</li>
    <li>Django</li>
    <li>Bootstrap</li>
    <li>JavaScript</li>
</ul>
    
<h2>Additional Python Modules Required:</h2>
<ul>
    <li>Django</li>
    <li>django-crispy-forms</li>
    <li>youtubesearchpython</li>
    <li>wikipedia</li>
</ul>

<h2>APIs Required:</h2>
<ul>
    <li>Dictionary API </li>
    <li>Google e-books API</li>
    <li>Google Gemini AI API (for chatbot)</li>
</ul>

<h2>API Endpoints:</h2>
<p>The application provides REST API endpoints for all core features. Authentication is handled via JWT tokens.</p>

<h3>Authentication:</h3>
<ul>
    <li><code>POST /api/login/</code> - Login with username/password to get JWT tokens</li>
    <li><code>POST /api/token/refresh/</code> - Refresh JWT access token</li>
</ul>

<h3>Notes API:</h3>
<ul>
    <li><code>GET /api/notes/</code> - List user's notes</li>
    <li><code>POST /api/notes/</code> - Create a new note</li>
    <li><code>GET /api/notes/{id}/</code> - Retrieve a specific note</li>
    <li><code>PUT /api/notes/{id}/</code> - Update a note</li>
    <li><code>DELETE /api/notes/{id}/</code> - Delete a note</li>
</ul>

<h3>Homework API:</h3>
<ul>
    <li><code>GET /api/homework/</code> - List user's homework</li>
    <li><code>POST /api/homework/</code> - Create homework</li>
    <li><code>GET /api/homework/{id}/</code> - Retrieve homework</li>
    <li><code>PUT /api/homework/{id}/</code> - Update homework</li>
    <li><code>DELETE /api/homework/{id}/</code> - Delete homework</li>
    <li><code>POST /api/homework/{id}/toggle_finished/</code> - Toggle completion status</li>
</ul>

<h3>Todo API:</h3>
<ul>
    <li><code>GET /api/todos/</code> - List user's todos</li>
    <li><code>POST /api/todos/</code> - Create todo</li>
    <li><code>GET /api/todos/{id}/</code> - Retrieve todo</li>
    <li><code>PUT /api/todos/{id}/</code> - Update todo</li>
    <li><code>DELETE /api/todos/{id}/</code> - Delete todo</li>
    <li><code>POST /api/todos/{id}/toggle_finished/</code> - Toggle completion status</li>
</ul>

<h3>Expenses API:</h3>
<ul>
    <li><code>GET /api/expenses/</code> - List user's expenses</li>
    <li><code>POST /api/expenses/</code> - Create expense</li>
    <li><code>GET /api/expenses/{id}/</code> - Retrieve expense</li>
    <li><code>PUT /api/expenses/{id}/</code> - Update expense</li>
    <li><code>DELETE /api/expenses/{id}/</code> - Delete expense</li>
</ul>

<h3>Other APIs:</h3>
<ul>
    <li><code>GET /api/profile/</code> - User profile</li>
    <li><code>GET /api/chat-history/</code> - Chat history</li>
    <li><code>GET /api/study-sessions/</code> - Study sessions</li>
    <li><code>GET /api/shared-notes/</code> - Shared notes</li>
    <li><code>POST /api/chatbot/</code> - AI chatbot query</li>
    <li><code>GET /api/progress/</code> - Progress dashboard data</li>
</ul>

<h3>Postman Collection:</h3>
<p>A Postman collection file <code>eduverse_api.postman_collection.json</code> is included in the repository for easy API testing.</p>
  
<h2>Note :</h2>

<b>The Secret_Key required for the execution and debugging of project is not removed from the project code.</b>
  
<h2>Usage :</h2>

    python django_web_app/manage.py makemigrations

    python django_web_app/manage.py migrate

    python django_web_app/manage.py runserver
    
   In your web browser enter the address : http://localhost:8000 or http://127.0.0.1:8000/
